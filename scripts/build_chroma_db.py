# scripts/build_chroma_db.py

import argparse
from embeddings.embedder import build_chroma_db

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build ChromaDB")
    parser.add_argument("--input", required=True)
    parser.add_argument("--persist", default="data/chroma_db")
    parser.add_argument("--limit", type=int, help="Use only N chunks")
    args = parser.parse_args()

    count = build_chroma_db(args.input, args.persist,
                            limit=args.limit)
    print(f"[OK] Stored {count} chunks into {args.persist}")
