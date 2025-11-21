import re


def smart_clean(text: str) -> str:
    """
    Smart noise removal while preserving technical & semantic structure.

    - Removes PDF garbage and control chars.
    - Cleans TOC filler dot patterns like '..... 520'.
    - Fixes glued section numbers like '17.2.100Davor' -> '17.2.100 Davor'.
    - Drops standalone page-number / roman-number lines (xii, 526, etc.).
    - Normalizes whitespace and escape characters.
    """
    if not text:
        return ""

    # 1) Strip unreadable unicode / control noise but keep normal ASCII
    text = text.encode("ascii", errors="ignore").decode("ascii")

    # 2) Remove standalone page-number lines and roman numeral page markers
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()

        # pure page number: "526"
        if re.fullmatch(r"\d{1,4}", stripped):
            continue

        # pure roman numeral: "xii", "XIII", etc. (front-matter pages)
        if re.fullmatch(r"[ivxlcdmIVXLCDM]{1,7}", stripped):
            continue

        cleaned_lines.append(line)

    text = "\n".join(cleaned_lines)

    # 3) Remove TOC tail patterns like ". . . . . . 520"
    #    First: kill ".... 520" style dot+page-number tails
    text = re.sub(r"\.{2,}\s*\d{1,4}", "", text)

    # 4) Collapse repeated dots ". . . . ." into a single space
    #    (we only target 2+ consecutive dots to avoid touching "v4.0.1")
    text = re.sub(r"\.{2,}", " ", text)

    # 5) Fix glued section numbers: "17.2.100Davor" -> "17.2.100 Davor"
    text = re.sub(r"(\d)([A-Za-z])", r"\1 \2", text)

    # 6) Normalize escape characters and whitespace:
    #    - turn tabs/newlines into spaces
    #    - collapse multiple spaces into one
    text = text.replace("\r", " ").replace("\t", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()

    return text
