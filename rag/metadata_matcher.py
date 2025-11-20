# rag/metadata_matcher.py

import numpy as np
from langchain_ollama import OllamaEmbeddings

embedder = OllamaEmbeddings(model="mxbai-embed-large")


# ---------- PRECOMPUTED STORAGE ----------
CHAPTER_VECS = {}   # {"Introduction": [0.23, ...], ...}
KEYWORD_VECS = {}   # {"installation": [...], ...}


def cosine(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))


# ---------- PRECOMPUTE ONCE ----------
def init_embeddings(chapters: list, keywords: list):
    """
    Embed chapters & keywords ONCE (store in dictionaries).
    Should be called only once at startup of query script.
    """
    global CHAPTER_VECS, KEYWORD_VECS

    # Chapters
    for c in chapters:
        CHAPTER_VECS[c] = embedder.embed_query(c)

    # Clean keywords: short phrases only
    keywords = [k for k in keywords if isinstance(
        k, str) and 1 < len(k.split()) < 4]
    for k in keywords[:80]:   # limit for speed
        KEYWORD_VECS[k] = embedder.embed_query(k)  # store embedding


# ---------- QUERY HANDLERS ----------
def detect_relevant_chapter(query: str, threshold: float = 0.45) -> str:
    """Return best matching chapter or Unknown."""
    query_vec = embedder.embed_query(query)
    scores = [
        (chap, cosine(query_vec, vec))
        for chap, vec in CHAPTER_VECS.items()
    ]
    best, score = sorted(scores, key=lambda x: x[1], reverse=True)[0]
    return best if score >= threshold else "Unknown"


def detect_relevant_keyword(query: str, threshold: float = 0.45) -> str:
    """Return best matching keyword or None."""
    query_vec = embedder.embed_query(query)
    scores = [
        (kw, cosine(query_vec, vec))
        for kw, vec in KEYWORD_VECS.items()
    ]
    if not scores:
        return None
    best, score = sorted(scores, key=lambda x: x[1], reverse=True)[0]
    return best if score >= threshold else None
