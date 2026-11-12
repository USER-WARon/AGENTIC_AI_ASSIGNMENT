"""Shared PaperPilot configuration and LLM setup."""
import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "PaperPilot AI"
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "").strip()
CHROMA_DIR = os.getenv("CHROMA_DIR", ".paperpilot_chroma")
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 180
MAX_PDF_BYTES = 30 * 1024 * 1024
MAX_PDF_PAGES = 300
MAX_PDF_TEXT_CHARS = 1_500_000
MAX_QUESTION_CHARS = 2_000


def create_llm():
    """Create the single shared API model used by all agents."""
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Add OPENAI_API_KEY to your .env file to use PaperPilot.")
    options = {"model": MODEL_NAME, "temperature": 0.2, "api_key": api_key, "max_tokens": 3000}
    if OPENAI_BASE_URL:
        options["base_url"] = OPENAI_BASE_URL
    return ChatOpenAI(**options)
