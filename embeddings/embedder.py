from langchain_ollama import OllamaEmbeddings


def get_embedding_model():
    """Return embedding model for RAG."""
    return OllamaEmbeddings(model="mxbai-embed-large")  # 🔒 FIXED
