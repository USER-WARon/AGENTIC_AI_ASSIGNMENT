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


def create_llm():
    """Create the single shared API model used by all agents."""
    from langchain_openai import ChatOpenAI

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Add OPENAI_API_KEY to your .env file to use PaperPilot.")
    options = {"model": MODEL_NAME, "temperature": 0.2, "api_key": api_key}
    if OPENAI_BASE_URL:
        options["base_url"] = OPENAI_BASE_URL
    return ChatOpenAI(**options)
