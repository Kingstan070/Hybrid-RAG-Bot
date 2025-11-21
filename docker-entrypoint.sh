#!/usr/bin/env bash
set -e

echo "🚀 Starting Ollama..."
ollama serve &

# Wait for Ollama to start
sleep 5

echo "📥 Pulling required models (only if not already downloaded)..."
ollama pull mxbai-embed-large || true
ollama pull llama3.2:3b || true

echo "🔍 Checking for existing ChromaDB at: $CHROMA_DIR"
if [ -d "$CHROMA_DIR" ] && [ "$(ls -A "$CHROMA_DIR")" ]; then
  echo "🟢 Existing ChromaDB found. Skipping ingestion and embedding."
else
  echo "🟠 No DB found. Running ingestion and embedding pipeline..."

  if [ ! -f "$PDF_PATH" ]; then
    echo "❌ PDF not found at: $PDF_PATH"
    echo "   Please upload one or set PDF_PATH correctly in Hugging Face Space."
    exit 1
  fi

  echo "📄 Ingesting PDF: $PDF_PATH ..."
  python scripts/ingest_pdf.py --pdf_path "$PDF_PATH" --chunk

  echo "🧠 Building ChromaDB embeddings..."
  python scripts/build_chroma.py

  echo "✨ Ingestion + Embedding complete."
fi

echo "🚀 Starting API server"
uvicorn api.app:app --host "$APP_HOST" --port "$APP_PORT"
