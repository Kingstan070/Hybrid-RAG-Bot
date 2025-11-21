# scripts/query_chroma_db.py

import os
from langchain_chroma import Chroma
from rag.pipeline import rag_query
from rag.metadata_matcher import init_embeddings  # IMPORTANT
from langchain_ollama import OllamaEmbeddings
from config.settings import settings


def main():
    db = Chroma(collection_name=settings.CHROMA_COLLECTION,
                persist_directory=settings.CHROMA_PERSIST_DIR,
                embedding_function=OllamaEmbeddings(model=settings.OLLAMA_EMBEDDING_MODEL,
                                                    base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434")))

    # ---------- LOAD CHAPTERS FIRST ----------
    collection = db.get()
    chapters = sorted(list({m["chapter"] for m in collection["metadatas"]}))

    if chapters:
        init_embeddings(chapters)
        print(f"\n[INFO] Cached {len(chapters)} chapter embeddings.")
    else:
        print("\n[WARN] No chapters found in DB.")

    # ---------- QUERY LOOP ----------
    while True:
        q = input("\nAsk something: ")
        if q.lower() == "exit":
            print("Exiting...")
            break
        print(rag_query(db, q))


if __name__ == "__main__":
    main()
