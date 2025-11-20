# ingestion/keyword_extractor.py

from rake_nltk import Rake
import nltk
from typing import List, Dict


def ensure_nltk():
    # MUST HAVE THESE NOW
    for resource in ["punkt", "punkt_tab", "stopwords"]:
        try:
            nltk.data.find(f"tokenizers/{resource}")
        except LookupError:
            print(f"[INFO] Downloading NLTK resource: {resource} ...")
            nltk.download(resource)


def extract_keywords(chunks: List[Dict], top_k=5) -> List[Dict]:
    ensure_nltk()  # ensure resources exist before extracting

    rake = Rake()  # uses NLTK internally

    for chunk in chunks:
        rake.extract_keywords_from_text(chunk["text"])
        keywords = rake.get_ranked_phrases()[:top_k]  # top N phrases
        chunk["keywords"] = keywords

    return chunks
