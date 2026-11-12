"""Extract page-aware text and create overlapping, page-aware chunks."""
from dataclasses import dataclass
from io import BytesIO
from pypdf import PdfReader
from config import CHUNK_OVERLAP, CHUNK_SIZE


@dataclass
class PaperChunk:
    text: str
    page: int
    chunk: int


def extract_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    try:
        reader = PdfReader(BytesIO(pdf_bytes), strict=False)
        pages = [(i + 1, (page.extract_text() or "").strip()) for i, page in enumerate(reader.pages)]
    except Exception as exc:
        raise ValueError(f"Could not read this PDF: {exc}") from exc
    if not pages or not any(text for _, text in pages):
        raise ValueError("No selectable text was found. This may be a scanned PDF; run OCR first and upload it again.")
    return pages


def chunk_pages(pages: list[tuple[int, str]], size: int = CHUNK_SIZE,
                overlap: int = CHUNK_OVERLAP) -> list[PaperChunk]:
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("Chunk size must be positive and overlap must be smaller than chunk size.")
    chunks: list[PaperChunk] = []
    for page_no, text in pages:
        start = 0
        while start < len(text):
            end = min(len(text), start + size)
            part = text[start:end].strip()
            if part:
                chunks.append(PaperChunk(part, page_no, len(chunks)))
            if end == len(text):
                break
            start = end - overlap
    return chunks


def load_pdf(pdf_bytes: bytes) -> tuple[list[tuple[int, str]], list[PaperChunk]]:
    pages = extract_pages(pdf_bytes)
    return pages, chunk_pages(pages)
