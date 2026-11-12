"""Common retrieval-grounded LCEL agent behavior."""
from langchain_core.runnables import RunnableLambda
from prompts.templates import make_chain, verify_output
from retrieval.vector_store import retrieve


class PaperAgent:
    name = "Paper Agent"
    task = "Answer using the paper."
    k = 5

    def __init__(self, llm, store):
        self.llm, self.store = llm, store
        self.chain = make_chain(llm, self.task)
        self.workflow = RunnableLambda(self._prepare) | self.chain | RunnableLambda(self._verify)

    def _prepare(self, inputs):
        question = inputs["question"]
        excerpts = retrieve(self.store, f"{self.task}\n{question}", k=self.k)
        context = "\n\n".join(f"[Page {page}] {text}" for text, page in excerpts)
        self._last_context = context
        return {"question": question, "context": context}

    def _verify(self, answer):
        return verify_output(answer, getattr(self, "_last_context", " "))

    def run(self, question: str) -> str:
        return self.workflow.invoke({"question": question})
