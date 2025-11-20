# Hybrid RAG Support Bot (Advanced PDF-Aware RAG)

This project implements a **Retrieval-Augmented Generation (RAG)** system with **document structure awareness**.
Instead of blindly searching embeddings, the system extracts **chapter-level metadata**, handles **TOC edge cases**, and uses **keyword extraction** to improve retrieval accuracy.

The project is built using:

* Python (modular pipeline)
* PyMuPDF (PDF parsing)
* Ollama (local LLM + embeddings)
* RAKE (lightweight keyword extraction)
* ChromaDB (vector storage – coming next)

The goal is to create a **hybrid retrieval system** with:
✔ Metadata filtering
✔ Low hallucination
✔ Latency logging (retrieval vs generation)
✔ Flask API + Streamlit UI (planned)

---

## 🚧 Current Progress

**Completed:**

* Environment setup (Conda + Ollama models)
* PDF ingestion pipeline
* TOC edge-case detection (Level-1 / Level-2 / No TOC)
* Fallback parser using heuristics
* Chunking (paragraph-based)
* Keyword extraction using RAKE
* JSON output with structured metadata

---

## 🧠 Next Steps (To Do)

* [ ] Embed chunks using `mxbai-embed-large` via Ollama
* [ ] Create ChromaDB vector store with metadata
* [ ] Implement hybrid retriever:
  - Metadata filter → similarity search
  - “I don’t know” handling
* [ ] Build Flask API for inference
* [ ] Add latency logging (retrieval vs generation)
* [ ] Streamlit UI for:
  - Upload PDF / Use existing DB
  - Query interface
  - Show logs + latency
* [ ] Final documentation and screenshots

