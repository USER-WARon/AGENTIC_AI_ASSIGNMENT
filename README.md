# PaperPilot AI

PaperPilot turns a text-based research PDF into a grounded study guide: a structured summary, concepts and methods, a detailed PowerPoint, viva questions, and answers to questions about the paper.

## What you need

- Windows 10 or 11
- Python **3.12** (recommended; Python 3.14 caused a native dependency import issue on the original setup)
- Internet access for installing packages and calling OpenRouter
- An OpenRouter account and API key
- A text-based research paper PDF. Scanned/image-only PDFs need OCR before upload.

## 1. Install Python 3.12

Open PowerShell and check whether the Python launcher sees 3.12:

```powershell
py -0p
```

If Python 3.12 is not listed, install Python 3.12 from [python.org](https://www.python.org/downloads/) or the approved app source for your computer. Close and reopen PowerShell, then check:

```powershell
py -3.12 --version
```

It should print `Python 3.12.x`. Use Python 3.12 for this project instead of 3.14.

## 2. Open the project folder

In PowerShell, change to the folder where `app.py` and `requirements.txt` are located. For this workspace:

```powershell
Set-Location "$HOME\Documents\Codex\2026-11-12\referenced-chatgpt-conversation-this-is-an"
```

Confirm the project files are there:

```powershell
Get-ChildItem app.py, requirements.txt, .env.example
```

## 3. Create and activate the virtual environment

Run these commands from the project folder:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
```

The version should be Python 3.12.x and the prompt should show `(.venv)`. If PowerShell says script execution is disabled, use the current PowerShell window only to activate the environment:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This changes the policy only for that PowerShell process. Alternatively, skip activation and use `.\.venv\Scripts\python.exe` in place of `python` in the remaining commands.

## 4. Install project packages

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Wait for pip to finish and return to the prompt. The requirements include Streamlit, LangChain, ChromaDB, PDF reading/export, PowerPoint export, and tests. If you change `requirements.txt` later, repeat `python -m pip install -r requirements.txt` with this environment active.

## 5. Create an OpenRouter API key

1. Sign in or create an account at [OpenRouter](https://openrouter.ai/).
2. Open the [API Keys page](https://openrouter.ai/settings/keys).
3. Choose **Create Key**, give it a name such as `PaperPilot`, and optionally set a spending limit.
4. Copy the key when it is shown. OpenRouter displays the secret key at creation; store it privately. Check your OpenRouter account for model availability, usage limits, and any credit/payment requirements.
5. Choose a model ID that is currently available in your account. Model IDs use a `provider/model` format. The example below uses `openai/gpt-4o-mini`; choose a different available model if needed.

OpenRouter provides an OpenAI-compatible API. This project points the LangChain OpenAI client to `https://openrouter.ai/api/v1` and uses the OpenRouter key as its bearer credential. See the [OpenRouter developer docs](https://openrouter.ai/developers) and [API key docs](https://openrouter.ai/docs/api/api-reference/api-keys/create-keys).

## 6. Put the key in `.env`

Make a private configuration file from the example:

```powershell
Copy-Item .env.example .env
notepad .env
```

In Notepad, replace the values with your own key and chosen model. Keep the setting names and base URL as shown:

```text
OPENAI_API_KEY=sk-or-paste-your-key-here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=openai/gpt-4o-mini
CHROMA_DIR=./.paperpilot_chroma
```

Save and close Notepad. Do not add spaces around `=`. Keep the key in `.env`; do not paste it into chat, screenshots, source files, or README. `.env` is excluded by `.gitignore`. The checked-in `.env.example` contains placeholders only.

## 7. Start PaperPilot

From the project folder with `(.venv)` active:

```powershell
python -m streamlit run app.py
```

Streamlit prints a local address, usually `http://localhost:8501`, and may open it in your browser. Leave the PowerShell window running while you use the app. Stop the app with **Ctrl+C** in that window.

## 8. Use the app

1. Upload a selectable-text research PDF.
2. Wait for the page text and ChromaDB index to finish processing.
3. In **Summary**, **Concepts**, and **Viva prep**, choose the generation button. Download those outputs as PDF.
4. In **Presentation**, generate the detailed 8–10 slide deck. Review the text preview, then download the styled PowerPoint (`.pptx`).
5. In **Ask your paper**, enter a question and choose **Ask**. Download the response as PDF.

The model uses retrieved excerpts from the uploaded paper. Check important claims against the original paper; model responses can still contain mistakes.

## 9. Run the tests (optional)

From the project folder with `(.venv)` active:

```powershell
python -m pytest -q
```

## Troubleshooting

### `streamlit` command is not recognized

Use the module form from the activated virtual environment:

```powershell
python -m streamlit run app.py
```

### `No module named reportlab` (or another missing package)

The environment may have been created before the package was added. Activate `.venv`, then install the full current requirements:

```powershell
python -m pip install -r requirements.txt
```

### LangChain or `_uuid_utils` import is blocked

Use Python 3.12 and reinstall packages in a fresh project virtual environment. If Windows Smart App Control blocks a native package, review the block and Windows Security setting on your personal device before deciding whether to change it. Do not rename DLL or `.pyd` files to get around the block.

### `parse_slides` cannot be imported or code changes do not appear

Stop Streamlit with **Ctrl+C**, confirm the terminal is in the project folder, and restart it with `python -m streamlit run app.py`. Verify the helper exists in the project file:

```powershell
Select-String -Path .\export\pptx_exporter.py -Pattern "def parse_slides"
```

### OpenRouter says unauthorized, model not found, or request failed

- `401` / unauthorized: check that `.env` contains the current OpenRouter key, without quotes or spaces, and restart Streamlit after saving it.
- Model error: use the exact model ID displayed by OpenRouter, including the provider prefix.
- Credit, limit, or rate error: check the OpenRouter account’s model availability, key limits, usage, and funding settings.
- Check that `OPENAI_BASE_URL` is exactly `https://openrouter.ai/api/v1`.

### Scanned PDF or no text detected

PaperPilot extracts embedded/selectable text. OCR the PDF first, save a searchable copy, and upload that copy.

## Security and privacy

The uploader is limited to 30 MB, 300 pages, and 1.5 million extracted characters. Paper text chunks are stored locally in `.paperpilot_chroma/`. For generation, retrieved excerpts and your question are sent to OpenRouter and the selected model provider. Keep the app on localhost and do not upload confidential documents unless you accept that data flow. Keep your API key in `.env`, never in source or screenshots. Review [SECURITY_REVIEW.md](SECURITY_REVIEW.md) for the code-review findings and remaining limits.

## Project architecture

```mermaid
flowchart LR
  PDF[PDF upload] --> EXTRACT[pypdf page extraction]
  EXTRACT --> CHUNK[Overlapping page-aware chunks]
  CHUNK --> EMBED[Local feature-hash embeddings]
  EMBED --> CHROMA[(ChromaDB)]
  CHROMA --> RETRIEVE[Per-task retrieval]
  RETRIEVE --> PROMPT[Grounded LangChain PromptTemplate]
  PROMPT --> LCEL[LCEL: shared OpenRouter model and parser]
  LCEL --> AGENTS[Summary · Concepts · Slides · Viva · Q&A]
  AGENTS --> EXPORT[PDF and PowerPoint downloads]
```

## Four agents and supported routing

| Agent | Output |
| --- | --- |
| Summarizer Agent | Objectives, methodology, results, contributions, limitations, conclusion |
| Concept Extractor Agent | Concepts, methods, technologies, contributions, results |
| Slide Generator Agent | Detailed, cited presentation content and styled PPTX |
| Viva Agent | 15–20 paper-specific questions and answers |

Rule-based intent routing supports `SUMMARY`, `CONCEPT_EXTRACTION`, `SLIDE_GENERATION`, `VIVA_PREPARATION`, and `CONCEPT_EXPLANATION`. All four agents share one OpenRouter-backed chat model through LangChain.

## Assignment acceptance criteria

- [x] LLM integration through one API model
- [x] Interactive Streamlit interface
- [x] Grounded zero-shot prompt design and output checks
- [x] LangChain Prompt Templates and LCEL
- [x] Retrieval-grounded agents and paper Q&A
- [x] Rule-based intent detection and routing
- [x] ChromaDB vector storage with page metadata and retrieval

## Limitations

- OpenRouter network access is required for generated responses; model availability, rate limits, and any usage costs depend on the selected model and account.
- Local feature-hash embeddings are lightweight lexical vectors and may retrieve paraphrases less accurately than a trained semantic embedding model.
- OCR, multiple-paper comparison, authentication, and cloud deployment are not included.
