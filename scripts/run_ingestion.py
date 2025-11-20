# scripts/run_ingestion.py

import json
import argparse
from ingestion.pdf_parser import parse_pdf
from ingestion.chunker import chunk_blocks

# Optional: import keyword extractor only when required
try:
    from ingestion.keyword_extractor import extract_keywords
    KEYWORD_SUPPORT = True
except ImportError:
    KEYWORD_SUPPORT = False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PDF Ingestion Pipeline")
    parser.add_argument("--pdf", required=True, help="Path to PDF file")
    parser.add_argument("--out", default="data/processed_csv/raw_blocks.json",
                        help="Output path for raw data")
    parser.add_argument("--chunk", action="store_true",
                        help="Chunk the parsed data")
    parser.add_argument("--keywords", action="store_true",
                        help="Extract keywords from chunks")
    args = parser.parse_args()

    # ---- 1) Parse PDF into structured blocks ----
    blocks = parse_pdf(args.pdf)
    print(f"[OK] Parsed {len(blocks)} blocks.")

    # ---- 2) Save RAW blocks ----
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(blocks, f, indent=2, ensure_ascii=False)
    print(f"[OK] Raw blocks saved to {args.out}")

    # ---- 3) Optional: Chunking ----
    if args.chunk:
        print("[INFO] Chunking enabled...")

        # 🔥 NEW: pass PDF path to ensure 'source' metadata + unique IDs
        chunks = chunk_blocks(blocks, args.pdf)

        chunk_path = args.out.replace(".json", "_chunked.json")
        with open(chunk_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)

        print(f"[OK] Created {len(chunks)} chunks → {chunk_path}")
    else:
        chunks = None
        chunk_path = None

    # ---- 4) Optional: Keyword Extraction ----
    if args.keywords:
        if chunks is None:
            print("[WARN] Chunking is required before keyword extraction.")
        elif not KEYWORD_SUPPORT:
            print("[ERROR] Keyword extractor module not found.")
        else:
            print("[INFO] Keyword extraction enabled...")
            chunks = extract_keywords(chunks)

            key_path = chunk_path.replace(".json", "_keywords.json")
            with open(key_path, "w", encoding="utf-8") as f:
                json.dump(chunks, f, indent=2, ensure_ascii=False)

            print(f"[OK] Keywords added → {key_path}")

    print("\n[FINISHED] Ingestion pipeline complete.")
