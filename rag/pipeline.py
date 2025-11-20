import time
from rag.metadata_matcher import detect_relevant_chapter
from langchain_ollama import ChatOllama

from app_logging.query_logger import query_logger
from app_logging.llm_logger import llm_logger


def rag_query(db, query: str, sim_threshold=0.40):

    total_start = time.time()
    query_logger.info(f"Query received - {query}")

    # CHAPTER MATCH
    t0 = time.time()
    chapter = detect_relevant_chapter(query, threshold=sim_threshold)
    query_logger.info(f"Relevant chapter detected - {chapter}")
    query_logger.info(f"Chapter detection = {time.time() - t0:.4f}s")

    # METADATA FILTER
    filters = {}
    if chapter != "Unknown":
        filters = {"chapter": chapter}
        query_logger.info(f"Applied filters - {filters}")

    # RETRIEVAL
    t1 = time.time()
    try:
        docs = db.similarity_search(query, k=3, filter=filters)
    except:
        docs = db.similarity_search(query, k=3)

    query_logger.info(f"Retrieved {len(docs)} docs in {time.time()-t1:.4f}s")

    if not docs:
        query_logger.warning("NO RELEVANT DOCS - RETURN 'I DON'T KNOW'")
        return "I DON'T KNOW"

    # LLM CALL
    context = "\n\n".join([d.page_content for d in docs[:2]])
    prompt = f"""
You are a VMware expert. Answer STRICTLY based on this document.
If answer is outside scope → ONLY reply 'I DON'T KNOW'

CONTEXT:
{context}

USER:
{query}
"""

    t2 = time.time()
    llm = ChatOllama(model="llama3.2:3b")
    response = llm.invoke(prompt)
    llm_logger.info(f"PROMPT SENT → {prompt[:500]}")
    llm_logger.info(f"LLM REPLY - {response}")
    llm_logger.info(f"LLM Gen Time = {time.time() - t2:.4f}s")

    query_logger.info(
        f"TOTAL PIPELINE LATENCY = {time.time() - total_start:.4f}s")

    return response
