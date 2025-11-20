# ingestion/keyword_extractor.py

from rake_nltk import Rake
import nltk
from typing import List, Dict

from app_logging.parse_logger import parse_logger  # <-- NEW


def ensure_nltk():
    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab/english", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
    ]

    for path, name in resources:
        try:
            nltk.data.find(path)
        except LookupError:
            parse_logger.info(f"Downloading NLTK resource: {name}")
            nltk.download(name)


def extract_keywords(chunks: List[Dict], top_k: int = 5) -> List[Dict]:
    parse_logger.info(
        f"Starting keyword extraction for {len(chunks)} chunks | top_k={top_k}"
    )

    ensure_nltk()
    rake = Rake()

    for idx, chunk in enumerate(chunks):
        text = chunk.get("text", "")
        rake.extract_keywords_from_text(text)
        keywords = rake.get_ranked_phrases()[:top_k]
        chunk["keywords"] = keywords

        if idx % 50 == 0:
            parse_logger.info(
                f"Keyword extraction progress: {idx + 1}/{len(chunks)}"
            )

    parse_logger.info("Keyword extraction complete.")
    return chunks
