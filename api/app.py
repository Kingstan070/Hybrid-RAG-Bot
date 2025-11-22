# api/app.py

import os
from fastapi import FastAPI, HTTPException
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from rag.pipeline import rag_query
from rag.metadata_matcher import init_embeddings
from config.settings import settings

app = FastAPI(title="RAG Chat API")

LOG_DIR = settings.LOG_DIR

# Load DB at startup
db = Chroma(
    collection_name=settings.CHROMA_COLLECTION,
    persist_directory=settings.CHROMA_PERSIST_DIR,
    embedding_function=OllamaEmbeddings(model=settings.OLLAMA_EMBEDDING_MODEL,
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


@app.get("/healthz")
def health_check():
    return {"status": "ok"}


@app.post("/ask")
def ask_question(query: str):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        response = rag_query(db, query)
        return {"query": query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs")
def list_logs():
    if not os.path.exists(LOG_DIR):
        raise HTTPException(status_code=404, detail="Log directory not found")

    files = [f for f in os.listdir(LOG_DIR) if f.endswith(".log")]
    return {"files": files}


@app.get("/logs/{filename}")
def read_log_file(filename: str):
    filepath = os.path.join(LOG_DIR, filename)

    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Log file not found")

    try:
        with open(filepath, "r") as file:
            content = file.read()
        return {"filename": filename, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
