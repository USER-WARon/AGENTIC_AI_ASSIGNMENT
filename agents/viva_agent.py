from agents.base import PaperAgent

class VivaAgent(PaperAgent):
    name = "Viva Agent"
    task = "Create 15 to 20 likely viva questions with concise, paper-grounded answers. Number the questions. Cite source page numbers when useful."
    k = 10
