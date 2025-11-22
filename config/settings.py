# config/settings.py

import os
from pydantic import BaseModel


class Settings(BaseModel):
    # ====== DATABASE ======
    CHROMA_COLLECTION: str = "manual_chunks"
    CHROMA_PERSIST_DIR: str = os.path.join("data", "chroma_db")
    PROCESSED_RAW_BLOCKS_PATH: str = os.path.join(
        "data", "processed_csv", "raw_blocks.json")

    # ====== LOGGING ======
    LOG_DIR: str = os.path.join("logs")

    # ====== EMBEDDINGS ======
    OLLAMA_EMBEDDING_MODEL: str = "mxbai-embed-large"

    # ====== LLM MODEL ======
    LLM_MODEL: str = "llama3.2:3b"    # or "llama3" or anything you use

    # ====== RAG PARAMETERS ======
    SIM_THRESHOLD: float = 0.50       # if similarity < threshold, ignore
    CONTEXT_THRESHOLD: float = 0.35   # if context similarity < threshold, ignore


# create a settings object you can import everywhere
settings = Settings()
