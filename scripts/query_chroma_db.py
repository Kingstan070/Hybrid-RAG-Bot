# scripts/query_chroma_db.py

import numpy as np
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from rag.metadata_matcher import detect_relevant_chapter, init_embeddings, cosine

SIM_THRESHOLD = 0.60  # tune later


def main():
    db = Chroma(
        collection_name="manual_chunks",
        persist_directory="data/chroma_db",
        embedding_function=OllamaEmbeddings(model="mxbai-embed-large")
    )

    # ----- Load chapters from metadata -----
    collection = db.get()
    chapters = sorted(list({m["chapter"] for m in collection["metadatas"]}))

    init_embeddings(chapters)
    print(f"[INFO] Cached {len(chapters)} chapter embeddings.\n")

    # ================= QUERY LOOP =================
    while True:
        query = input("\nAsk something (or 'exit'): ")
        if query.lower() == "exit":
            break

        chapter = detect_relevant_chapter(query, threshold=SIM_THRESHOLD)
        print(f"\n[MATCH] Best Chapter = {chapter}")

        filters = {"chapter": chapter} if chapter != "Unknown" else {}

        # ---- FIRST TRY: FILTER BY CHAPTER ----
        try:
            docs = db.similarity_search(query, k=5, filter=filters)
        except:
            docs = []

        # ---- FALLBACK: PURE SIMILARITY ----
        if not docs:
            print("[INFO] Fallback → Pure similarity search")
            docs = db.similarity_search(query, k=5)

        query_vec = db._embedding_function.embed_query(query)
        valid_docs = []
        for d in docs:
            doc_vec = db._embedding_function.embed_query(d.page_content)
            sim = cosine(query_vec, doc_vec)
            if sim >= SIM_THRESHOLD:
                valid_docs.append((d, sim))

        if not valid_docs:
            print("\n[I DON'T KNOW] → Not covered in the manual.\n")
            continue

        # ---- Display Top 3 Results ----
        valid_docs.sort(key=lambda x: x[1], reverse=True)
        for doc, sim in valid_docs[:3]:
            print("\n---")
            print(f"[SIM SCORE] {sim:.4f}")
            print(
                f"[CHAPTER] {doc.metadata.get('chapter')} | Page: {doc.metadata.get('page')}")
            print(doc.page_content[:350], "\n")


if __name__ == "__main__":
    main()
