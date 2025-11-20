# embeddings/embedder.py

import json
import time
from tqdm import tqdm
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


def build_chroma_db(input_file: str, persist_dir: str, limit: int = None):
    data = json.load(open(input_file, "r", encoding="utf-8"))

    if limit:
        data = data[:limit]
        print(f"[INFO] Using ONLY first {limit} chunks (out of {len(data)})")

    texts = [d["text"] for d in data]
    metadatas = [
        {
            "chapter": d["chapter"],
            "page": d["page"],
            "keywords": ", ".join(d.get("keywords", []))
            if isinstance(d.get("keywords"), list) else ""
        }
        for d in data
    ]

    embeddings = OllamaEmbeddings(model="mxbai-embed-large")

    vectordb = Chroma(
        collection_name="manual_chunks",
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    print(f"[INFO] Starting embedding of {len(texts)} chunks...")
    start = time.time()

    for i in tqdm(range(len(texts)), desc="Embedding chunks", unit="chunk"):
        vectordb.add_texts(
            texts=[texts[i]],
            metadatas=[metadatas[i]]
        )

    total_time = time.time() - start
    print(f"\n[OK] Stored {len(texts)} chunks → {persist_dir}")
    print(f"[TIME] Total elapsed: {total_time:.2f} sec")
    print(f"[SPEED] Avg per chunk: {total_time/len(texts):.3f} sec")

    return len(texts)
