# scripts/check_extraction_coverage.py

import fitz      # PyMuPDF
import json
import argparse


def get_raw_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = []
    for page in doc:
        text = page.get_text("text")
        all_text.append(text)
    return "\n".join(all_text)


def get_parsed_text(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [item["text"] for item in data if "text" in item]
    return "\n".join(texts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to original PDF")
    parser.add_argument("--parsed", required=True,
                        help="Path to parsed_blocks.json")
    args = parser.parse_args()

    print("\n[INFO] Extracting raw text from PDF...")
    raw_text = get_raw_text_from_pdf(args.pdf)
    raw_len = len(raw_text.split())

    print("[INFO] Extracting text from parsed JSON...")
    parsed_text = get_parsed_text(args.parsed)
    parsed_len = len(parsed_text.split())

    coverage = (parsed_len / raw_len) * 100 if raw_len > 0 else 0

    print("\n===== TEXT COVERAGE REPORT =====")
    print(f"Total words in PDF:     {raw_len}")
    print(f"Words captured in RAG:  {parsed_len}")
    print(f"Coverage:               {coverage:.2f}%")
    print("================================")
