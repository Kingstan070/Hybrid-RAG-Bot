# ---- Base image ----
FROM python:3.11-slim

# ---- System dependencies ----
RUN apt-get update && apt-get install -y \
    curl wget gnupg build-essential \
    libgl1 libgl1-mesa-dev libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# ---- Install Ollama ----
RUN curl https://ollama.ai/install.sh | sh

# ---- Create working directory ----
WORKDIR /app
COPY . /app

# ---- Install Python dependencies ----
RUN pip install --no-cache-dir -r requirements.txt

# ---- ENV variables (can be overridden in HF Spaces UI) ----
ENV CHROMA_DIR=/app/data/chroma_db
ENV PDF_PATH=/app/data/input.pdf
ENV OLLAMA_HOST=http://localhost:11434
ENV APP_HOST=0.0.0.0
ENV APP_PORT=8000

# ---- Ensure entry script is executable ----
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000 11434

ENTRYPOINT ["./docker-entrypoint.sh"]
