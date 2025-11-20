# ingestion/pdf_parser.py

import fitz  # PyMuPDF
from typing import List, Dict


def _build_page_to_chapter(doc) -> Dict[int, str]:
    """
    Dynamically detect correct TOC level for chapters.
    1. If Level 1 has many entries → use it.
    2. If Level 1 only has 1-2 entries → switch to Level 2.
    """
    toc = doc.get_toc()
    total_pages = len(doc)

    # Default mapping
    page_to_chapter = {p: "Unknown" for p in range(total_pages)}

    if not toc:
        return page_to_chapter

    # Count entries by level
    level_counts = {}
    for level, title, _ in toc:
        level_counts[level] = level_counts.get(level, 0) + 1

    # Decide best TOC level
    if 1 in level_counts and level_counts[1] >= 3:
        chapter_level = 1
    else:
        chapter_level = 2   # ⚠ fallback when level-1 is generic

    # Collect chapters
    chapters = []
    for level, title, page_num in toc:
        if level != chapter_level:
            continue

        idx = max(0, min(total_pages - 1, page_num - 1))
        chapters.append((idx, title))

    if not chapters:
        return page_to_chapter  # nothing matched

    chapters.sort(key=lambda x: x[0])  # sort by page index

    # Map page ranges → chapters
    for i, (start_page, title) in enumerate(chapters):
        end_page = chapters[i + 1][0] if i + 1 < len(chapters) else total_pages
        for p in range(start_page, end_page):
            page_to_chapter[p] = title

    return page_to_chapter


def _parse_without_toc(doc, total_pages):
    """
    Fallback parsing when no TOC exists.
    Try to detect chapter headings via heuristics:
      - uppercase lines
      - lines with < 7 words
    If no heading is detected, assign 'General'.
    """

    parsed_blocks = []
    current_chapter = "General"

    for p in range(total_pages):
        page = doc[p]
        text = page.get_text("text").strip()

        if len(text) < 30:
            # Skip blank or useless pages
            continue

        # Heuristic: detect headings in FIRST 5 LINES
        lines = text.split("\n")[:5]
        for line in lines:
            line_clean = line.strip()
            if (
                line_clean.isupper()                               # ALL CAPS → likely heading
                # Short phrase
                and 2 <= len(line_clean.split()) <= 6
            ):
                current_chapter = line_clean                       # Update chapter
                break

        parsed_blocks.append({
            "page": p,
            "chapter": current_chapter,
            "text": text,
        })

    return parsed_blocks


def parse_pdf(pdf_path: str) -> List[Dict]:
    """
    Very simple parser:
    - Uses TOC level-1 entries as 'chapter'
    - Extracts raw text per page
    - Returns list[ {page, chapter, text} ]
    """
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    toc = doc.get_toc()

    if toc and len(toc) > 0:
        print("[INFO] TOC found → structured parsing.")
        page_to_chapter = _build_page_to_chapter(doc)
        use_toc = True
    else:
        print("[WARN] NO TOC found → using fallback parser.")
        use_toc = False

    parsed_blocks: List[Dict] = []

    if use_toc:
        for p in range(total_pages):
            page = doc[p]
            text = page.get_text("text").strip()
            if len(text) < 20:
                continue

            parsed_blocks.append({
                "page": p,
                "chapter": page_to_chapter[p],
                "text": text,
            })
    else:
        parsed_blocks = _parse_without_toc(doc, total_pages)

    return parsed_blocks


if __name__ == "__main__":
    # Small debug CLI: show first N pages and their chapters
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--pages", type=int, default=40)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    doc = fitz.open(args.pdf)
    mapping = _build_page_to_chapter(doc)

    print("=== PAGE → CHAPTER MAP (preview) ===")
    for p in range(min(args.pages, len(doc))):
        print(f"Page {p:3d} -> {mapping[p]}")

    if args.out:
        blocks = parse_pdf(args.pdf)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(blocks, f, indent=2, ensure_ascii=False)
        print(f"\nSaved parsed blocks to {args.out}")
