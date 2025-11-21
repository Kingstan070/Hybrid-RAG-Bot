# api/app.py

import os
from fastapi import FastAPI, HTTPException
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from rag.pipeline import rag_query
from rag.metadata_matcher import init_embeddings
import config.settings as settings

app = FastAPI(title="RAG Chat API")

# Load DB at startup
db = Chroma(
    collection_name=settings.CHROMA_COLLECTION,
    persist_directory=settings.CHROMA_PERSIST_DIR,
    embedding_function=OllamaEmbeddings(model=settings.EMBEDDING_MODEL,
                                        base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
)

# Load & cache chapters embeddings
collection = db.get()
chapters = sorted({m["chapter"] for m in collection["metadatas"]})
if chapters:
    init_embeddings(chapters)
    print(f"[INFO] Cached {len(chapters)} chapter embeddings.")
else:
    print("[WARN] No chapters found in DB.")


@app.get("/")
def home():
    return {"message": "RAG API is running 🚀"}


@app.post("/ask")
def ask_question(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        response = rag_query(db, query)
        return {"query": query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
