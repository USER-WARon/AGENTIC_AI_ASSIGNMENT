"""Extract page-aware text and create overlapping, page-aware chunks."""
from dataclasses import dataclass
from io import BytesIO
from pypdf import PdfReader
from config import CHUNK_OVERLAP, CHUNK_SIZE, MAX_PDF_BYTES, MAX_PDF_PAGES, MAX_PDF_TEXT_CHARS


@dataclass
class PaperChunk:
    text: str
    page: int
    chunk: int


def extract_pages(pdf_bytes: bytes) -> list[tuple[int, str]]:
    if len(pdf_bytes) > MAX_PDF_BYTES:
        raise ValueError(f"PDF is too large. The maximum upload size is {MAX_PDF_BYTES // (1024 * 1024)} MB.")
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("This file does not appear to be a valid PDF.")
    try:
        reader = PdfReader(BytesIO(pdf_bytes), strict=False)
        if len(reader.pages) > MAX_PDF_PAGES:
            raise ValueError(f"PDF has too many pages. The limit is {MAX_PDF_PAGES} pages.")
        pages = []
        total_chars = 0
        for i, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            total_chars += len(text)
            if total_chars > MAX_PDF_TEXT_CHARS:
                raise ValueError("Extracted text is too large to process safely (maximum 1.5 million characters).")
            pages.append((i + 1, text))
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Could not read this PDF. It may be damaged, encrypted, or unsupported.") from exc
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
