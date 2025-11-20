# scripts/query_chroma_db.py

import numpy as np
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from rag.metadata_matcher import detect_relevant_chapter, detect_relevant_keyword, init_embeddings, cosine

SIM_THRESHOLD = 0.40  # will tune later


def main():
    db = Chroma(
        collection_name="manual_chunks",
        persist_directory="data/chroma_db",
        embedding_function=OllamaEmbeddings(model="mxbai-embed-large")
    )

    # Load metadata
    collection = db.get()
    all_metadata = collection["metadatas"]
    chapters = sorted(list({m["chapter"] for m in all_metadata}))
    raw_keywords = [m.get("keywords")
                    for m in all_metadata if m.get("keywords")]

    keywords = sorted(list({
        k.strip() for k in raw_keywords
        if isinstance(k, str) and 1 < len(k.split()) < 4
    }))[:80]

    init_embeddings(chapters, keywords)
    print(
        f"[INFO] Embedded {len(chapters)} chapters & {len(keywords)} keywords for caching.")

    # ============ MAIN LOOP ============ #
    while True:
        query = input("\nAsk something (or 'exit'): ")
        if query.lower() == "exit":
            break

        # Metadata detection
        chapter = detect_relevant_chapter(query, threshold=SIM_THRESHOLD)
        keyword = detect_relevant_keyword(query, threshold=SIM_THRESHOLD)
        print(f"\n[MATCH] Chapter = {chapter} | Keyword = {keyword}")

        # Try chapter filter first
        filters = {}
        if chapter != "Unknown":
            filters = {"chapter": chapter}

        try:
            docs = db.similarity_search(query, k=5, filter=filters)
        except:
            docs = []

        if not docs and keyword:
            print("[INFO] Trying keyword-based filtering...")
            try:
                docs = db.similarity_search(
                    query, k=5, filter={"keywords": {"$contains": keyword}})
            except:
                docs = []

        if not docs:
            print("[INFO] Falling back to pure similarity search...")
            docs = db.similarity_search(query, k=5)

        # === REAL SIMILARITY CHECK (using cosine) ===
        query_vec = db._embedding_function.embed_query(query)

        valid_docs = []
        for d in docs:
            doc_vec = db._embedding_function.embed_query(d.page_content)
            sim = cosine(query_vec, doc_vec)
            if sim >= SIM_THRESHOLD:
                valid_docs.append((d, sim))

        # No strong result → I don't know
        if not valid_docs:
            print("\n[I DON'T KNOW] → Not covered in manual.\n")
            continue

        # Sort final answers & display
        valid_docs.sort(key=lambda x: x[1], reverse=True)
        for doc, sim in valid_docs[:3]:
            print("\n---")
            print(f"[SIM SCORE] {sim:.4f}")
            print(
                f"[CHAPTER] {doc.metadata.get('chapter', 'Unknown')} | Page: {doc.metadata.get('page', 'N/A')}")
            print(doc.page_content[:350], "\n")


if __name__ == "__main__":
    main()
