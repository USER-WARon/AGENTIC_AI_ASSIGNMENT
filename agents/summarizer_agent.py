from agents.base import PaperAgent

class SummarizerAgent(PaperAgent):
    name = "Summarizer Agent"
    task = "Write a faithful structured paper summary in plain Markdown, not JSON. Use headings: Paper and research question, Objectives, Methodology, Main results, Contributions, Limitations, and Conclusion. Use concise prose and bullets where helpful. Cite page numbers. Do not return slides or a slides array. If the evidence is missing, say it is not stated."
    k = 8
