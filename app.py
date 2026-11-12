"""PaperPilot AI: an academic paper assistant powered by grounded retrieval."""
import hashlib
import json
import re
import streamlit as st
from config import APP_NAME, create_llm
from retrieval.pdf_loader import load_pdf
from retrieval.vector_store import create_store
from orchestration.workflow import build_agents
from orchestration.router import route_intent, SUMMARY, CONCEPT_EXTRACTION, SLIDE_GENERATION, VIVA_PREPARATION
from export.pptx_exporter import create_pptx
from export.pptx_exporter import parse_slides
from export.pdf_exporter import create_text_pdf

st.set_page_config(page_title=APP_NAME, page_icon="📄", layout="wide")
st.title("📄 PaperPilot AI")
st.caption("Upload a research paper to explore its ideas, prepare for a viva, and build a presentation.")

def readable_output(value):
    """Render accidental JSON agent responses as readable Markdown."""
    text = value.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.I)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return text

    def render(item, depth=2):
        if isinstance(item, dict):
            # Common slide-shaped response: display titles and bullets as text.
            if "title" in item and any(key in item for key in ("bullets", "points", "content")):
                title = str(item.get("title", "Key points"))
                points = item.get("bullets", item.get("points", item.get("content", [])))
                if isinstance(points, str): points = [points]
                body = "\n".join(f"- {point}" for point in points) if isinstance(points, list) else str(points)
                citation = f"\n\n_Source: {item['citation']}_" if item.get("citation") else ""
                return f"{'#' * min(depth, 4)} {title}\n\n{body}{citation}"
            parts = []
            for key, child in item.items():
                heading = str(key).replace("_", " ").title()
                if isinstance(child, (dict, list)):
                    parts.append(f"{'#' * min(depth, 4)} {heading}\n\n{render(child, depth + 1)}")
                else:
                    parts.append(f"**{heading}:** {child}")
            return "\n\n".join(parts)
        if isinstance(item, list):
            return "\n\n".join((render(child, depth + 1) if isinstance(child, (dict, list)) else f"- {child}") for child in item)
        return str(item)

    return render(data)

uploaded = st.file_uploader("Choose a research paper PDF", type=["pdf"])
if uploaded:
    pdf_bytes = uploaded.getvalue()
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    if st.session_state.get("paper_digest") != digest:
        with st.spinner("Reading pages and indexing paper text…"):
            try:
                pages, chunks = load_pdf(pdf_bytes)
                store = create_store(chunks, digest[:24])
                st.session_state.update(paper_digest=digest, paper_name=uploaded.name, pages=pages,
                                        store=store, agents=None, outputs={})
                st.success(f"Indexed {len(chunks)} text chunks across {len(pages)} pages.")
            except ValueError as exc:
                st.error(str(exc))
                st.stop()
            except Exception as exc:
                st.error(f"Paper indexing failed: {exc}")
                st.stop()
    if st.session_state.get("agents") is None:
        try:
            st.session_state.agents = build_agents(create_llm(), st.session_state.store)
        except Exception as exc:
            st.error(str(exc))
            st.stop()
    agents = st.session_state.agents
    st.caption(f"Current paper: **{st.session_state.paper_name}** · {len(st.session_state.pages)} pages")
    summary_tab, concepts_tab, slides_tab, viva_tab, qa_tab = st.tabs(["Summary", "Concepts", "Presentation", "Viva prep", "Ask your paper"])

    def run_agent(intent, prompt, output_key):
        with st.spinner(f"{agents[intent].name} is working…"):
            result = agents[intent].run(prompt)
        st.session_state.outputs[output_key] = result
        return result

    with summary_tab:
        if st.button("Generate structured summary", key="summary_btn"):
            run_agent(SUMMARY, "Summarize this paper.", "summary")
        if "summary" in st.session_state.outputs:
            summary_md = readable_output(st.session_state.outputs["summary"])
            st.markdown(summary_md)
            st.download_button("Download summary (PDF)", create_text_pdf("Research Paper Summary", summary_md, st.session_state.paper_name), "paper_summary.pdf", "application/pdf")
    with concepts_tab:
        if st.button("Extract concepts and contributions", key="concept_btn"):
            run_agent(CONCEPT_EXTRACTION, "Extract the key concepts, methods, contributions and results.", "concepts")
        if "concepts" in st.session_state.outputs:
            concepts_md = readable_output(st.session_state.outputs["concepts"])
            st.markdown(concepts_md)
            st.download_button("Download concepts (PDF)", create_text_pdf("Key Concepts and Contributions", concepts_md, st.session_state.paper_name), "paper_concepts.pdf", "application/pdf")
    with slides_tab:
        if st.button("Generate presentation slides", key="slides_btn"):
            slides = run_agent(SLIDE_GENERATION, "Create the slide deck for this paper.", "slides")
            try:
                parsed_slides = parse_slides(slides)
                st.session_state.outputs["slide_data"] = parsed_slides
                st.session_state.outputs["pptx"] = create_pptx(slides, st.session_state.paper_name)
                st.session_state.outputs["slide_error"] = None
            except ValueError as exc:
                st.session_state.outputs["slide_error"] = str(exc)
        if "slides" in st.session_state.outputs:
            if st.session_state.outputs.get("slide_error"):
                st.error(st.session_state.outputs["slide_error"])
            elif st.session_state.outputs.get("slide_data"):
                st.success(f"Created a {len(st.session_state.outputs['slide_data'])}-slide presentation.")
                for number, slide in enumerate(st.session_state.outputs["slide_data"], 1):
                    with st.expander(f"Slide {number}: {slide['title']}", expanded=number == 1):
                        for bullet in slide["bullets"]:
                            st.markdown(f"- {bullet}")
                        if slide.get("citation"):
                            st.caption(f"Source: {slide['citation']}")
                st.download_button("Download designed PowerPoint (.pptx)", st.session_state.outputs["pptx"], "paperpilot_presentation.pptx", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
    with viva_tab:
        if st.button("Prepare 15–20 viva questions", key="viva_btn"):
            run_agent(VIVA_PREPARATION, "Prepare viva questions and answers.", "viva")
        if "viva" in st.session_state.outputs:
            viva_md = readable_output(st.session_state.outputs["viva"])
            st.markdown(viva_md)
            st.download_button("Download viva guide (PDF)", create_text_pdf("Viva Preparation Guide", viva_md, st.session_state.paper_name), "viva_guide.pdf", "application/pdf")
    with qa_tab:
        with st.form("paper_question"):
            question = st.text_input("Ask a question about this paper")
            ask = st.form_submit_button("Ask")
        if ask and question.strip():
            intent = route_intent(question)
            st.caption(f"Routed to {agents[intent].name}")
            answer = run_agent(intent, question.strip(), "last_answer")
            answer_md = readable_output(answer)
            st.markdown(answer_md)
            st.download_button("Download answer (PDF)", create_text_pdf("Answer to Your Paper Question", f"## Question\n\n{question.strip()}\n\n## Answer\n\n{answer_md}", st.session_state.paper_name), "paper_answer.pdf", "application/pdf", key="answer_pdf")
        elif ask:
            st.info("Enter a question first.")
else:
    st.info("Upload a text-based research PDF to get started. Scanned PDFs need OCR before upload.")
