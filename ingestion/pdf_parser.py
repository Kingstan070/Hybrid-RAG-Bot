# ingestion/pdf_parser.py

import fitz  # PyMuPDF
from typing import List, Dict

# NEW — logging
from app_logging.parse_logger import parse_logger


def _build_page_to_chapter(doc) -> Dict[int, str]:
    """
    Dynamically detect correct TOC level for chapters.
    1. If Level 1 has many entries - use it.
    2. If Level 1 only has 1-2 entries - switch to Level 2.
    """
    toc = doc.get_toc()
    total_pages = len(doc)

    parse_logger.info(f"TOC entries detected = {len(toc)}")

    # Default mapping
    page_to_chapter = {p: "Unknown" for p in range(total_pages)}

    if not toc:
        parse_logger.warning("No TOC found — returning default mapping.")
        return page_to_chapter

    # Count entries by level
    level_counts = {}
    for level, title, _ in toc:
        level_counts[level] = level_counts.get(level, 0) + 1

    parse_logger.info(f"TOC level counts: {level_counts}")

    # Decide best TOC level
    if 1 in level_counts and level_counts[1] >= 3:
        chapter_level = 1
        parse_logger.info("Using TOC level 1 as chapter level")
    else:
        chapter_level = 2
        parse_logger.info("Using TOC level 2 as fallback")

    # Collect chapters
    chapters = []
    for level, title, page_num in toc:
        if level != chapter_level:
            continue
        idx = max(0, min(total_pages - 1, page_num - 1))
        chapters.append((idx, title))

    if not chapters:
        parse_logger.warning(
            "No matching chapters found for selected TOC level.")
        return page_to_chapter

    chapters.sort(key=lambda x: x[0])
    parse_logger.info(f"Total chapters detected = {len(chapters)}")

    # Map chapters to pages
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

    parse_logger.warning("TOC not found — using heuristic-based parsing")

    parsed_blocks = []
    current_chapter = "General"

    for p in range(total_pages):
        page = doc[p]
        text = page.get_text("text").strip()

        if len(text) < 30:
            continue

        lines = text.split("\n")[:5]
        for line in lines:
            line_clean = line.strip()
            if line_clean.isupper() and 2 <= len(line_clean.split()) <= 6:
                current_chapter = line_clean
                parse_logger.info(
                    f"Detected new chapter: {current_chapter} (Page {p})")
                break

        parsed_blocks.append({
            "page": p,
            "chapter": current_chapter,
            "text": text,
        })

    parse_logger.info(
        f"Parsed {len(parsed_blocks)} pages using fallback parser")
    return parsed_blocks


def parse_pdf(pdf_path: str) -> List[Dict]:
    """
    Main PDF parser:
    - Uses TOC detection
    - Falls back to heuristic parsing
    """
    parse_logger.info(f"Opening PDF: {pdf_path}")

    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    parse_logger.info(f"Total pages detected: {total_pages}")

    toc = doc.get_toc()

    if toc:
        parse_logger.info("TOC detected — structured parsing enabled")
        page_to_chapter = _build_page_to_chapter(doc)
        use_toc = True
    else:
        parse_logger.warning(
            "No TOC detected — using fallback heuristic parser")
        use_toc = False

    parsed_blocks = []

    if use_toc:
        for p in range(total_pages):
            text = doc[p].get_text("text").strip()
            if len(text) < 20:
                continue
            parsed_blocks.append({
                "page": p,
                "chapter": page_to_chapter.get(p, "Unknown"),
                "text": text,
            })
        parse_logger.info(
            f"Structured parsing complete — parsed {len(parsed_blocks)} pages")
    else:
        parsed_blocks = _parse_without_toc(doc, total_pages)

    return parsed_blocks


# Debug CLI
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    parser.add_argument("--pages", type=int, default=40)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()

    parse_logger.info(f"CLI started for {args.pdf}")

    doc = fitz.open(args.pdf)
    mapping = _build_page_to_chapter(doc)

    print("=== PAGE - CHAPTER MAP (preview) ===")
    for p in range(min(args.pages, len(doc))):
        print(f"Page {p:3d} -> {mapping[p]}")

    if args.out:
        blocks = parse_pdf(args.pdf)
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(blocks, f, indent=2, ensure_ascii=False)
        parse_logger.info(f"Parsed blocks saved to {args.out}")
        print(f"\nSaved parsed blocks to {args.out}")
