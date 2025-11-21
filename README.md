# 🚀 Hybrid RAG Support Bot

### **Structure-Aware Retrieval-Augmented Generation for PDFs**

_A Local, Privacy-Preserving RAG System Designed for Real-World Documents_

---

## 📌 Introduction

This project aims to overcome a major limitation in most Retrieval-Augmented Generation (RAG) systems:

> **RAG systems do not understand document structure — they only process flat text.**

PDFs in the real world contain:
- Different formatting styles
- Missing/irregular table of contents
- Long paragraphs without headings
- Page-level context where meaning depends on structure

**Our goal** was to build a robust **structure-aware RAG pipeline** that understands PDFs using:  
✔ TOC detection (Level-1 / Level-2 / No TOC)  
✔ Chapter + section metadata extraction  
✔ Paragraph-based chunking  
✔ Keyword extraction using RAKE  
✔ Local embeddings using Ollama  
✔ Hybrid retrieval — metadata + similarity search  
✔ Latency measurement for each stage

**What is achieved now:**  
✔ PDF parsing with structural awareness  
✔ Metadata + keyword-rich embeddings stored in ChromaDB  
✔ Working CLI retrieval  
✔ A functional API (`api/app.py`) for querying via FastAPI  
✔ Fully local execution — **no cloud APIs used**

**This is a working prototype, tested on CPU, built within a limited time.**  
More testing and improvements are planned in future updates.

---

## 🧠 Core Modules Used (and WHY)

|Module|Purpose|
|---|---|
|**PyMuPDF (`fitz`)**|PDF parsing, page extraction, TOC reading|
|**RAKE-NLTK**|Keyword extraction for boosting retrieval relevance|
|**LangChain**|Framework to connect vector DB + LLM + retriever|
|**ChromaDB**|Local vector database to store embeddings & metadata|
|**Ollama**|Local LLM inference — no API key, fully offline|
|**FastAPI**|API layer to interact with the RAG system|
|**Pydantic**|Configuration management (`config/settings.py`)|
|**Custom Loggers**|Tracks parsing, embeddings, query latency|
|**NumPy / Pandas**|/Data handling for chunks & processed CSVs|

---

## ⚙️ Setup Instructions

### 🧪 1️⃣ Create Conda Environment

```bash
conda env create -f environment.yml
conda activate hybrid_bot
```

### 📦 2️⃣ Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### 🤖 3️⃣ Install Ollama (Required)

Download & install from:  
🔗 [https://ollama.ai/download](https://ollama.ai/download)

### 📥 4️⃣ Pull Models (Embedding + LLM)

```bash
ollama pull mxbai-embed-large     # Embedding model
ollama pull llama3.2:3b           # LLM for generation
```

---

## ▶ Usage — How the System Works

### 📌 Why Do We Ingest the PDF?

Before retrieval is possible, we must:  
✔ Parse PDF + detect structure  
✔ Split into meaningful chunks  
✔ Extract metadata & keywords  
✔ Store in CSV & JSON formats

### 📌 Why Do We Build ChromaDB?

Once chunks are extracted, we:  
✔ Embed them using `mxbai-embed-large`  
✔ Store them inside ChromaDB  
✔ Enable retrieval using LangChain Retriever

---

### 🚀 **Run These Scripts (In Correct Order)**

| Step | Command                                                       | Purpose                       |
| ---- | ------------------------------------------------------------- | ----------------------------- |
| 1️⃣  | `python scripts/ingest_pdf.py --pdf_path input.pdf --chunk`   | Parse PDF & generate metadata |
| 2️⃣  | `python scripts/build_chroma.py`                              | Build embeddings + local DB   |

⚠ **Note:** `query_chroma.py` is only for testing.  

---

## 📁 Project Structure

```
Hybrid-RAG-Bot/
│
├── ingestion/              ← PDF parsing + TOC detection + chunking
├── embeddings/             ← Embedding + ChromaDB builder
├── rag/                    ← Retrieval + LLM pipeline
├── api/                    ← FastAPI interface (basic)
├── scripts/                ← RUN THESE FIRST (pipeline scripts)
├── app_logging/            ← Modular logging system
├── config/settings.py      ← Central configuration
├── data/                   ← Output CSVs + vector DB
└── README.md
```

(Verified via `project_snapshot.txt`)

---

## ⚠ Known Issues / Limitations

| Issue                         | Reason                                        |
| ----------------------------- | --------------------------------------------- |
| Limited testing               | Developed only on CPU (time-limited)          |
| Threshold values              | Tuned manually ("eyeballing") → needs testing |
| Only one API endpoint exists  | Due to project deadline                       |
| CLI retrieval logs incomplete | API-based logging recommended                 |

---

## 🔧 Future Fixes & Improvements

🚀 Planned features:

- Add more API endpoints (upload PDF, rebuild DB, test queries)
- Automate ingestion & embedding — **no CLI required**
- Improve PDF generalization across formats
- Add Streamlit UI for user-friendly front-end
- Confidence scoring + metadata filtering
- Load balancing for large PDFs

---

## 📬 Contact

**Author:** Allwin Kingstan  
📧 **[tallwinkingstan@gmail.com](mailto:tallwinkingstan@gmail.com)**  

🔗 GitHub: `https://github.com/Kingstan070`
