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
st.markdown("""
<style>
  .pp-hero { padding: 1.35rem 1.6rem 1.25rem; border-radius: 18px;
    background: linear-gradient(120deg, #13233e 0%, #1e3c68 68%, #236d7a 100%);
    color: #fff; margin: .2rem 0 1rem; }
  .pp-kicker { color: #70d4c6; text-transform: uppercase; letter-spacing: .12em;
    font-size: .75rem; font-weight: 700; margin-bottom: .35rem; }
  .pp-hero h1 { color: white; font-size: 2.15rem; margin: 0 0 .35rem; }
  .pp-hero p { color: #e0e9f5; margin: 0; font-size: 1.02rem; }
  .pp-card { background: rgba(43,103,194,.08); border: 1px solid rgba(43,103,194,.18);
    border-radius: 14px; padding: 1rem 1.05rem; min-height: 112px; }
  .pp-card strong { color: #2b67c2; font-size: 1rem; }
  .pp-card span { display: block; margin-top: .35rem; font-size: .9rem; opacity: .85; }
</style>
<div class="pp-hero">
  <div class="pp-kicker">Your research, ready to present</div>
  <h1>PaperPilot AI</h1>
  <p>Turn a research paper into clear study notes, viva preparation, and a presentation you can explain.</p>
</div>
""", unsafe_allow_html=True)

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
    if uploaded.size > 30 * 1024 * 1024:
        st.error("PDF is too large. The maximum upload size is 30 MB.")
        st.stop()
    pdf_bytes = uploaded.getvalue()
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    if st.session_state.get("paper_digest") != digest:
        with st.status("Preparing your paper…", expanded=True) as progress:
            try:
                progress.write("Extracting page text and checking the PDF…")
                pages, chunks = load_pdf(pdf_bytes)
                progress.write(f"Split {len(chunks)} text sections across {len(pages)} pages.")
                progress.write("Building the local search index…")
                store = create_store(chunks, digest[:24])
                st.session_state.update(paper_digest=digest, paper_name=uploaded.name, pages=pages,
                                        store=store, agents=None, outputs={})
                progress.update(label=f"Paper ready · {len(pages)} pages indexed", state="complete", expanded=False)
            except ValueError as exc:
                progress.update(label="Could not prepare this PDF", state="error", expanded=False)
                st.error(str(exc))
                st.stop()
            except Exception as exc:
                progress.update(label="Indexing failed", state="error", expanded=False)
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
    st.info("For AI-generated results, retrieved excerpts from this paper and your question are sent to OpenRouter and the model provider you selected. Avoid uploading confidential or sensitive documents unless you are comfortable with their data policies.")
    section = st.radio("Paper tools", ["Summary", "Concepts", "Presentation", "Viva prep", "Ask your paper"], horizontal=True, label_visibility="collapsed", key="paper_tools_nav")

    def run_agent(intent, prompt, output_key):
        try:
            with st.spinner(f"{agents[intent].name} is working…"):
                result = agents[intent].run(prompt)
        except Exception:
            st.error("The model request failed. Check the API key, model ID, account limits, and network connection, then try again.")
            return None
        st.session_state.outputs[output_key] = result
        return result

    if section == "Summary":
        if st.button("Generate structured summary", key="summary_btn"):
            run_agent(SUMMARY, "Summarize this paper.", "summary")
        if "summary" in st.session_state.outputs:
            summary_md = readable_output(st.session_state.outputs["summary"])
            st.markdown(summary_md)
            st.download_button("Download summary (PDF)", create_text_pdf("Research Paper Summary", summary_md, st.session_state.paper_name), "paper_summary.pdf", "application/pdf")
    elif section == "Concepts":
        if st.button("Extract concepts and contributions", key="concept_btn"):
            run_agent(CONCEPT_EXTRACTION, "Extract the key concepts, methods, contributions and results.", "concepts")
        if "concepts" in st.session_state.outputs:
            concepts_md = readable_output(st.session_state.outputs["concepts"])
            st.markdown(concepts_md)
            st.download_button("Download concepts (PDF)", create_text_pdf("Key Concepts and Contributions", concepts_md, st.session_state.paper_name), "paper_concepts.pdf", "application/pdf")
    elif section == "Presentation":
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
    elif section == "Viva prep":
        if st.button("Prepare 15–20 viva questions", key="viva_btn"):
            run_agent(VIVA_PREPARATION, "Prepare viva questions and answers.", "viva")
        if "viva" in st.session_state.outputs:
            viva_md = readable_output(st.session_state.outputs["viva"])
            st.markdown(viva_md)
            st.download_button("Download viva guide (PDF)", create_text_pdf("Viva Preparation Guide", viva_md, st.session_state.paper_name), "viva_guide.pdf", "application/pdf")
    elif section == "Ask your paper":
        with st.form("paper_question"):
            question = st.text_input("Ask a question about this paper", max_chars=2000)
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
    st.markdown("### Start with your paper")
    st.caption("Upload a text-based PDF above. PaperPilot will index it locally, then you can choose what to create.")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="pp-card"><strong>Understand</strong><span>Get a structured summary and key concepts with page references.</span></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="pp-card"><strong>Prepare</strong><span>Build a detailed slide deck and practice with viva questions.</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="pp-card"><strong>Ask</strong><span>Get answers grounded in passages from your paper.</span></div>', unsafe_allow_html=True)
    st.caption("Scanned PDFs need OCR before upload. Retrieved excerpts are sent to OpenRouter when you request AI-generated results.")
