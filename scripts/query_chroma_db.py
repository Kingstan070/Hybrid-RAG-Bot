# scripts/query_chroma_db.py

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


def main():
    db = Chroma(
        collection_name="manual_chunks",
        persist_directory="data/chroma_db",
        embedding_function=OllamaEmbeddings(model="mxbai-embed-large")
    )

    while True:
        query = input("\nAsk something (or 'exit'): ")
        if query.lower() == "exit":
            break

        results = db.similarity_search(query, k=3)

        for r in results:
            print("\n---")
            print(
                f"[CHAPTER] {r.metadata['chapter']} (Page: {r.metadata['page']})")
            print(r.page_content[:350])


if __name__ == "__main__":
    main()
