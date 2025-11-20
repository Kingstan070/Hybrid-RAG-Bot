# rag/metadata_matcher.py

import numpy as np
from langchain_ollama import OllamaEmbeddings

embedder = OllamaEmbeddings(model="mxbai-embed-large")
CHAPTER_VECS = {}   # CACHED!


def cosine(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))


def init_embeddings(chapters: list):
    """Embed chapters ONCE & cache vectors"""
    global CHAPTER_VECS
    CHAPTER_VECS = {}  # RESET & REBUILD!
    for c in chapters:
        CHAPTER_VECS[c] = embedder.embed_query(c)


def detect_relevant_chapter(query: str, threshold: float = 0.45) -> str:
    """Safely return best matching chapter or Unknown"""

    # Prevent crash
    if not CHAPTER_VECS:
        return "Unknown"

    query_vec = embedder.embed_query(query)

    scores = [
        (chap, cosine(query_vec, vec))
        for chap, vec in CHAPTER_VECS.items()
    ]

    if not scores:
        return "Unknown"

    best, score = sorted(scores, key=lambda x: x[1], reverse=True)[0]
    return best if score >= threshold else "Unknown"
