from io import BytesIO
from pypdf import PdfWriter
from retrieval.pdf_loader import extract_pages, chunk_pages, PaperChunk
from retrieval.vector_store import HashEmbeddings
from orchestration.router import route_intent
from export.pptx_exporter import create_pptx, parse_slides, slides_to_markdown
from export.pdf_exporter import create_text_pdf


def test_pdf_page_and_chunk_metadata():
    pages = [(1, "PaperPilot test paper: method and results.")]
    chunks = chunk_pages(pages, size=20, overlap=2)
    assert chunks and chunks[0].page == 1


def test_scanned_or_empty_pdf_has_actionable_error():
    from pypdf import PdfWriter
    output = BytesIO()
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)
    writer.write(output)
    try:
        extract_pages(output.getvalue())
    except ValueError as exc:
        assert "scanned PDF" in str(exc)
    else:
        raise AssertionError("Expected an empty-text PDF error")


def test_pdf_input_guards(monkeypatch):
    import retrieval.pdf_loader as loader
    try:
        loader.extract_pages(b"not a pdf")
    except ValueError as exc:
        assert "valid PDF" in str(exc)
    else:
        raise AssertionError("Expected a PDF signature error")
    monkeypatch.setattr(loader, "MAX_PDF_BYTES", 8)
    try:
        loader.extract_pages(b"%PDF-1.7 payload")
    except ValueError as exc:
        assert "too large" in str(exc)
    else:
        raise AssertionError("Expected an upload size error")


def test_embeddings_router_and_pptx():
    vectors = HashEmbeddings().embed_documents(["research method", "research method"])
    assert len(vectors[0]) == 384 and vectors[0] == vectors[1]
    assert route_intent("prepare viva questions") == "VIVA_PREPARATION"
    assert route_intent("make slides") == "SLIDE_GENERATION"
    assert route_intent("explain the loss function") == "CONCEPT_EXPLANATION"
    assert create_pptx('[{"title":"Method","bullets":["Step one"]}]').startswith(b"PK")


def test_slide_json_parsing_and_readable_outline():
    slides = parse_slides('```json\n{"slides":[{"title":"Findings","bullets":["Accuracy improved"],"citation":"p. 4"}]}\n```')
    assert slides[0]["title"] == "Findings"
    assert "Accuracy improved" in slides_to_markdown(slides)
    assert create_text_pdf("Summary", "## Findings\n\n- Test result", "Sample paper").startswith(b"%PDF")
