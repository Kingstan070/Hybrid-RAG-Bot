# scripts/query_chroma_db.py

from langchain_chroma import Chroma
from rag.pipeline import rag_query
from rag.metadata_matcher import init_embeddings  # IMPORTANT
from langchain_ollama import OllamaEmbeddings


def main():
    db = Chroma(collection_name="manual_chunks",
                persist_directory="data/chroma_db",
                embedding_function=OllamaEmbeddings(model="mxbai-embed-large"))

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
