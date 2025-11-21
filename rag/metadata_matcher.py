# rag/metadata_matcher.py

import numpy as np
from langchain_ollama import OllamaEmbeddings

embedder = OllamaEmbeddings(model="mxbai-embed-large")
CHAPTER_VECS = {}  # cached once


def cosine(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))


def init_embeddings(chapters: list):
    """Embed all chapter names ONCE"""
    global CHAPTER_VECS
    CHAPTER_VECS = {}
    for c in chapters:
        CHAPTER_VECS[c] = embedder.embed_query(c)


def detect_top_chapters(query: str, top_k=3, return_scores=False):
    """Return top-k chapters ranked by similarity"""
    if not CHAPTER_VECS:
        return []

    query_vec = embedder.embed_query(query)
    scores = [(chap, cosine(query_vec, vec))
              for chap, vec in CHAPTER_VECS.items()]
    scores.sort(key=lambda x: x[1], reverse=True)
    if return_scores:
        return [(c, s) for c, s in scores[:top_k]]
    return [c for c, s in scores[:top_k]]  # only the chapter names
