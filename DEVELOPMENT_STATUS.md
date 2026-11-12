# Development status

## Implemented

- Streamlit PDF upload and five task areas.
- Page-aware PDF extraction, overlap chunking, local feature-hash embeddings, persistent ChromaDB, and similarity retrieval.
- Four identifiable agents plus grounded paper Q&A, sharing one OpenAI chat model.
- LangChain chat prompt templates, LCEL runnable chains, deterministic intent routing, output checks, Markdown downloads, and PPTX export.
- README, environment template, requirements, and focused unit tests.

## Verification

- Ran the test suite in the project's Python 3.12 virtual environment: **5 passed**.
- Confirmed `.env`, `.venv`, `.venv312`, and `.paperpilot_chroma` are Git-ignored.
- Added focused checks for invalid PDF signatures and upload size limits.
- The full OpenRouter-backed PDF-to-output workflow still requires a valid local key and a user-selected paper, so it was not exercised during this review.

For a local smoke test, run:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
Copy-Item .env.example .env
# Add OPENAI_API_KEY to .env, then:
python -m streamlit run app.py
```

Upload a text-based research PDF and generate each result in the app. OCR is required before upload for scanned-only PDFs.
