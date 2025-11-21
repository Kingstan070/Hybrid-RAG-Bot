# ingestion/pdf_parser.py

import fitz  # PyMuPDF
from typing import List, Dict

# logging
from app_logging.parse_logger import parse_logger


# =============================
#  HIERARCHICAL TOC PARSER
# =============================
def _parse_hierarchical_toc(doc) -> Dict[int, str]:
    """
    Build hierarchical TOC using levels 1,2,3,4...
    Output: flat page_to_chapter mapping.
    (✔️ Same output structure — no change in JSON format)
    """
    toc = doc.get_toc()
    total_pages = len(doc)

    if not toc:
        parse_logger.warning("Hierarchical TOC parsing failed — no TOC found.")
        return {p: "Unknown" for p in range(total_pages)}

    stack = {1: None, 2: None, 3: None, 4: None, 5: None}
    formatted_chapters = []  # [(page_idx, "Ch1 > Sec1 > Subsec"), ...]

    for level, title, page in toc:
        page_idx = max(0, min(total_pages - 1, page - 1))

        # Clear lower levels
        for l in range(level, 6):
            stack[l] = None

        stack[level] = title  # update current level

        # Build hierarchical title (ignore empty values)
        full_title = " > ".join([v for v in stack.values() if v])
        formatted_chapters.append((page_idx, full_title))

    page_to_chapter = {p: "Unknown" for p in range(total_pages)}
    formatted_chapters.sort(key=lambda x: x[0])

    for i, (start_page, title) in enumerate(formatted_chapters):
        end_page = (
            formatted_chapters[i + 1][0]
            if i + 1 < len(formatted_chapters) else total_pages
        )
        for p in range(start_page, end_page):
            page_to_chapter[p] = title

    parse_logger.info(
        f"Hierarchical TOC parsing complete — {len(formatted_chapters)} detected")
    return page_to_chapter


# =============================
#  FALLBACK PARSER
# =============================
def _parse_without_toc(doc, total_pages):
    parse_logger.warning("TOC NOT FOUND — using heuristic parsing")
    parsed_blocks = []
    current_chapter = "General"

    for p in range(total_pages):
        page = doc[p]
        text = page.get_text("text").strip()

        if len(text) < 30:
            continue

        lines = text.split("\n")[:5]
        for line in lines:
            if line.strip().isupper() and 2 <= len(line.split()) <= 6:
                current_chapter = line.strip()
                parse_logger.info(
                    f"Detected heading {current_chapter} on page {p}")
                break

        parsed_blocks.append({
            "page": p,
            "chapter": current_chapter,  # <-- SAME STRUCTURE AS BEFORE
            "text": text,  # <-- SAME STRUCTURE AS BEFORE
        })

    return parsed_blocks


# =============================
#  MAIN PDF PARSER
# =============================
def parse_pdf(pdf_path: str) -> List[Dict]:
    parse_logger.info(f"Opening PDF — {pdf_path}")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)

    parse_logger.info(f"Total pages detected: {total_pages}")

    toc = doc.get_toc()

    if toc:
        parse_logger.info("TOC found — using HIERARCHICAL handler")
        page_to_chapter = _parse_hierarchical_toc(doc)
        use_toc = True
    else:
        use_toc = False
        parse_logger.warning("No TOC detected — using fallback parser")

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
            f"Structured parsing complete — {len(parsed_blocks)} blocks created")
    else:
        parsed_blocks = _parse_without_toc(doc, total_pages)

    return parsed_blocks
