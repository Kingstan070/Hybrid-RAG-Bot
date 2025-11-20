from langchain_ollama import ChatOllama


def get_llm():
    """Return the LLM used for answering."""
    return ChatOllama(model="llama3.2:3b")  # 🔒 FIXED
