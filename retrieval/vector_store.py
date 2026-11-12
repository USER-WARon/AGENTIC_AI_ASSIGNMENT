"""Chroma-backed retrieval using a tiny deterministic feature-hash embedder."""
import hashlib
import re
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from config import CHROMA_DIR
from retrieval.pdf_loader import PaperChunk


class HashEmbeddings(Embeddings):
    """Small local embedding suitable for an assignment MVP; no model download."""
    dimensions = 384

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        features = tokens + [f"{a}_{b}" for a, b in zip(tokens, tokens[1:])]
        for token in features:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "little")
            vector[value % self.dimensions] += 1.0 if value & 1 else -1.0
        norm = sum(x * x for x in vector) ** 0.5 or 1.0
        return [x / norm for x in vector]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def create_store(chunks: list[PaperChunk], collection_id: str,
                 persist_directory: str = CHROMA_DIR) -> Chroma:
    if not chunks:
        raise ValueError("No text chunks to index.")
    return Chroma.from_texts(
        texts=[chunk.text for chunk in chunks],
        metadatas=[{"page": chunk.page, "chunk": chunk.chunk} for chunk in chunks],
        ids=[f"{collection_id}-{chunk.chunk}" for chunk in chunks],
        embedding=HashEmbeddings(), collection_name=f"paper_{collection_id[:24]}",
        persist_directory=persist_directory,
    )


def retrieve(store: Chroma, query: str, k: int = 5) -> list[tuple[str, int]]:
    docs = store.similarity_search(query, k=k)
    return [(doc.page_content, int(doc.metadata.get("page", 0))) for doc in docs]
