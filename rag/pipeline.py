# rag/pipeline.py

import time
from rag.metadata_matcher import detect_top_chapters, cosine
from langchain_ollama import ChatOllama

from app_logging.query_logger import query_logger
from app_logging.llm_logger import llm_logger


# ---------------- SAFE LOGGING ----------------
def safe_log(msg: str):
    return msg.encode("ascii", errors="ignore").decode("ascii")


# ---------------- SMART HALLUCINATION CHECK ----------------
def context_is_relevant(query, context, embed_fn, min_sim=0.45):
    """Semantic similarity check (better than overlap)."""
    q_vec = embed_fn(query)
    ctx_vec = embed_fn(context)
    sim = cosine(q_vec, ctx_vec)
    return sim >= min_sim, sim


# ---------------- RAG PIPELINE ----------------
def rag_query(db, query: str, prev_answer=None, sim_threshold=0.55):
    total_start = time.time()
    query_logger.info(safe_log(f"Query received → {query}"))

    # 🧠 INCLUDE CONTEXT FROM PREVIOUS ANSWERS (FOLLOW-UP QUESTIONS SUPPORT)
    prev_context = f"PREVIOUS ANSWER:\n{prev_answer}\n\n" if prev_answer else ""

    # ---------------------------------------------------------
    # 1️⃣ SMART CHAPTER MATCHING → KEEP CHAPTERS CLOSE TO BEST
    # ---------------------------------------------------------
    t0 = time.time()
    chapters_scores = detect_top_chapters(query, top_k=5, return_scores=True)
    query_logger.info(safe_log(f"Raw chapter scores → {chapters_scores}"))

    if not chapters_scores:
        return "I couldn't analyze any relevant sections. Please rephrase."

    max_score = max(s for _, s in chapters_scores)
    threshold_ratio = 0.85  # keep chapters >= 85% of best score

    valid_chapters = [
        chap for chap, s in chapters_scores
        if s >= max_score * threshold_ratio and s >= sim_threshold
    ]

    query_logger.info(safe_log(f"max_score = {max_score:.3f}"))
    query_logger.info(safe_log(f"Chapters kept → {valid_chapters}"))
    query_logger.info(f"Chapter match time = {time.time() - t0:.4f}s")

    if not valid_chapters:
        return "I need more specific details to search relevant sections."

    # ---------------------------------------------------------
    # 2️⃣ RETRIEVE DOCS (ONLY FROM VALID CHAPTERS, NO GLOBAL)
    # ---------------------------------------------------------
    docs = []

    for chap in valid_chapters:
        try:
            result = db.similarity_search(query, k=2, filter={"chapter": chap})
            docs.extend(result)
            query_logger.info(safe_log(f"Docs from '{chap}' → {len(result)}"))
        except Exception as e:
            query_logger.warning(
                safe_log(f"Failed chapter search → {chap} | {e}"))

    # ---- REMOVE DUPLICATES ----
    unique_docs = list({d.page_content: d for d in docs}.values())
    query_logger.info(safe_log(f"Total unique docs → {len(unique_docs)}"))

    if not unique_docs:
        return "I found some sections, but nothing useful. Try rephrasing."

    # ---------------------------------------------------------
    # 3️⃣ CONTEXT PREPARATION
    # ---------------------------------------------------------
    context = prev_context + \
        "\n\n".join(d.page_content for d in unique_docs[:3])

    # 🔍 SEMANTIC HALLUCINATION CHECK
    ok, sim = context_is_relevant(
        query,
        context,
        db._embedding_function.embed_query,
        min_sim=0.35
    )

    query_logger.info(safe_log(f"Context similarity score = {sim:.3f}"))
    if not ok:
        return (
            "I found some related parts, but the relevance seems weak.\n"
            "Could you please clarify or provide more details?"
        )

    # ---------------------------------------------------------
    # 4️⃣ FINAL PROMPT FOR LLM
    # ---------------------------------------------------------
    prompt = f"""
You are a customer support technical expert.
Answer STRICTLY using only the provided context.
If the information is incomplete → ask a follow-up question.
Do NOT hallucinate. Do NOT use outside knowledge.

-------------------------
CONTEXT:
{context}
-------------------------

USER QUESTION:
{query}

ANSWER:
"""

    # ---------------------------------------------------------
    # 5️⃣ CALL LLM
    # ---------------------------------------------------------
    t2 = time.time()
    llm = ChatOllama(model="llama3.2:3b")
    response = llm.invoke(prompt)
    response_text = response.content

    llm_logger.info(safe_log(f"PROMPT SENT → {prompt[:400]}"))
    llm_logger.info(safe_log(f"LLM REPLY → {response_text}"))
    llm_logger.info(safe_log(f"Response Time = {time.time() - t2:.4f}s"))

    query_logger.info(
        safe_log(f"TOTAL LATENCY = {time.time() - total_start:.4f}s"))

    return response_text
