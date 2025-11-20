from langchain_chroma import Chroma
from rag.pipeline import rag_query


def main():
    db = Chroma(collection_name="manual_chunks",
                persist_directory="data/chroma_db")
    while True:
        q = input("\nAsk something: ")
        print(rag_query(db, q))


if __name__ == "__main__":
    main()
