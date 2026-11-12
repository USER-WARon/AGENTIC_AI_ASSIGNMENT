"""Minimal shared-model agent registry and dispatcher."""
from agents.summarizer_agent import SummarizerAgent
from agents.concept_agent import ConceptExtractorAgent
from agents.slide_agent import SlideGeneratorAgent
from agents.viva_agent import VivaAgent
from orchestration.router import *

def build_agents(llm, store):
    return {
        SUMMARY: SummarizerAgent(llm, store),
        CONCEPT_EXTRACTION: ConceptExtractorAgent(llm, store),
        SLIDE_GENERATION: SlideGeneratorAgent(llm, store),
        VIVA_PREPARATION: VivaAgent(llm, store),
        CONCEPT_EXPLANATION: PaperQnAAgent(llm, store),
    }

class PaperQnAAgent(SummarizerAgent):
    name = "Paper Q&A Agent"
    task = "Answer the user's question using only the retrieved paper excerpts. Explain uncertainty if not stated."
    k = 5
