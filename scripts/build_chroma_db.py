# scripts/build_chroma_db.py

import argparse
from embeddings.embedder import build_chroma_db
from app_logging.embed_logger import embed_logger  # <-- NEW
from config.settings import settings

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build ChromaDB")
    parser.add_argument("--input", required=True)
    parser.add_argument("--persist", default=settings.CHROMA_PERSIST_DIR)
    parser.add_argument("--limit", type=int, help="Use only N chunks")
    args = parser.parse_args()

    embed_logger.info(
        f"Starting ChromaDB build | input={args.input} | persist={args.persist} | limit={args.limit}"
    )

    count = build_chroma_db(args.input, args.persist, limit=args.limit)

    embed_logger.info(f"Stored {count} chunks into {args.persist}")
    print(f"[OK] Stored {count} chunks into {args.persist}")
