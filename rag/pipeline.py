# rag/pipeline.py

import time
from rag.metadata_matcher import detect_relevant_chapter
from langchain_ollama import ChatOllama

from app_logging.query_logger import query_logger
from app_logging.llm_logger import llm_logger


# -------- SAFE LOGGER --------
def safe_log(msg: str):
    return msg.encode("ascii", errors="ignore").decode("ascii")


# -------- RAG PIPELINE --------
def rag_query(db, query: str, sim_threshold=0.40):
    total_start = time.time()
    query_logger.info(safe_log(f"Query received → {query}"))

    # --- CHAPTER MATCH ---
    t0 = time.time()
    chapter = detect_relevant_chapter(query, threshold=sim_threshold)
    query_logger.info(safe_log(f"Relevant chapter detected → {chapter}"))
    query_logger.info(f"Chapter match time = {time.time() - t0:.4f}s")

    filters = {"chapter": chapter} if chapter != "Unknown" else {}
    if filters:
        query_logger.info(safe_log(f"Applied filters → {filters}"))

    # --- RETRIEVE DOCS ---
    t1 = time.time()
    try:
        docs = db.similarity_search(query, k=3, filter=filters)
    except:
        docs = db.similarity_search(query, k=3)

    query_logger.info(f"Retrieved {len(docs)} docs in {time.time() - t1:.4f}s")

    if not docs:
        msg = "I DON'T KNOW"
        query_logger.warning(safe_log(f"No relevant docs → {msg}"))
        return msg

    # --- PREPARE PROMPT ---
    context = "\n\n".join([d.page_content for d in docs[:2]])
    prompt = f"""
You are a VMware expert. Answer STRICTLY based on this document.
If answer is outside scope → ONLY reply 'I DON'T KNOW' tone.

CONTEXT:
{context}

USER:
{query}
"""

    # --- CALL LLM ---
    t2 = time.time()
    llm = ChatOllama(model="llama3.2:3b")
    response = llm.invoke(prompt)

    response_text = response.content  # FIX!

    llm_logger.info(safe_log(f"PROMPT SENT → {prompt[:400]}"))
    llm_logger.info(safe_log(f"LLM REPLY → {response_text}"))
    llm_logger.info(safe_log(f"LLM Response Time = {time.time() - t2:.4f}s"))

    query_logger.info(f"TOTAL LATENCY = {time.time() - total_start:.4f}s")

    return response_text
