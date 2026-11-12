# Development status

## Implemented

- Streamlit PDF upload and five task areas.
- Page-aware PDF extraction, overlap chunking, local feature-hash embeddings, persistent ChromaDB, and similarity retrieval.
- Four identifiable agents plus grounded paper Q&A, sharing one OpenAI chat model.
- LangChain chat prompt templates, LCEL runnable chains, deterministic intent routing, output checks, Markdown downloads, and PPTX export.
- README, environment template, requirements, and focused unit tests.

## Verification still required

The current desktop environment has no callable `python`, `python3`, or `py` executable, and no `pytest` command. No `OPENAI_API_KEY` was available. I could not install dependencies, run the test suite, launch Streamlit, or complete the requested PDF → summary → concepts → PPTX → viva → Q&A workflow here.

After Python 3.10+ and dependencies are available, run:

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
Copy-Item .env.example .env
# Add OPENAI_API_KEY to .env, then:
streamlit run app.py
```

Upload a text-based research PDF and generate each result in the app. OCR is required before upload for scanned-only PDFs.
