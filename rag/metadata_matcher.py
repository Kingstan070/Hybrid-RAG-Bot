# rag/metadata_matcher.py

import numpy as np
from langchain_ollama import OllamaEmbeddings

embedder = OllamaEmbeddings(model="mxbai-embed-large")

# ---------- PRECOMPUTED STORAGE ----------
CHAPTER_VECS = {}   # {"Introduction": [0.23, ...]}


def cosine(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))


def init_embeddings(chapters: list):
    """Embed chapters ONCE and store vectors."""
    global CHAPTER_VECS
    for c in chapters:
        CHAPTER_VECS[c] = embedder.embed_query(c)


def detect_relevant_chapter(query: str, threshold: float = 0.45) -> str:
    """Return best matching chapter or Unknown."""
    query_vec = embedder.embed_query(query)

    scores = [
        (chap, cosine(query_vec, vec))
        for chap, vec in CHAPTER_VECS.items()
    ]

    best, score = sorted(scores, key=lambda x: x[1], reverse=True)[0]
    return best if score >= threshold else "Unknown"
