# PaperPilot security review

## Scope

Static review of local PDF ingestion, retrieval, prompts, model calls, Streamlit rendering, and generated downloads. No external targets or live API-key tests were used.

## Findings fixed

- **Unbounded PDF workload:** uploads, page counts, and extracted text could consume excessive memory/CPU. Added 30 MB upload, 300 page, and 1.5 million extracted-character caps, plus a PDF signature check and actionable errors.
- **Unbounded user request/output size:** bounded Q&A input to 2,000 characters and model output to 3,000 tokens to reduce accidental prompt/cost abuse.
- **Third-party data flow was unclear:** the app now tells users that retrieved document excerpts and questions are sent to OpenRouter and the chosen model provider.
- **Raw provider exception display:** agent request failures now show a generic message instead of rendering provider exception detail in the UI.
- **Credential template hygiene:** `.env.example` uses a placeholder and `.env` is ignored by Git. A real-looking key was previously present in the example file; revoke it if it was active, and remove it from any history or copies where it was shared.
- **Virtual environments:** `.venv*/` ignores both `.venv` and `.venv312`.

## Remaining risks and safe use

- Keep the app bound to localhost. Streamlit has no authentication configured; do not expose it to a LAN or the public internet.
- Uploaded text is persisted in the local Chroma directory and selected excerpts are sent to the configured model provider. Do not use confidential papers unless their handling is acceptable to you.
- PDF parsing and model/provider libraries can contain vulnerabilities. Keep dependencies updated from trusted sources. This review did not run a dependency vulnerability database scan.
- Prompt-injection text inside a paper is treated as untrusted context in the system prompt, but this is not a formal guarantee. Review generated claims against the original paper.
- Smart App Control may block native package files on Windows. Do not rename or patch blocked binaries to evade the policy.

## Verification status

Input validation and generic provider-error handling were added. Automated tests and a live model workflow still need to be run in the user's Python environment because this workspace's system Python launcher is unavailable. No API requests were sent during this review.
