from agents.base import PaperAgent

class ConceptExtractorAgent(PaperAgent):
    name = "Concept Extractor Agent"
    task = "Extract key concepts, methods, algorithms or technologies, contributions, and reported results as concise labeled bullets."
    k = 7
