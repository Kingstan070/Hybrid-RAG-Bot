"""
CLI TEST - CHECK IF OLLAMA EMBEDDINGS WORK
Run: python scripts/test_ollama_embed.py --model mxbai-embed-large
"""

import argparse
from langchain_ollama import OllamaEmbeddings


def test_embeddings(model_name: str):
    embedder = OllamaEmbeddings(model=model_name)
    vec = embedder.embed_query("test embeddings")
    print("\nEmbedding vector size:", len(vec))
    print("First few values:", vec[:10])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="mxbai-embed-large",
                        help="Name of Ollama embedding model")

    args = parser.parse_args()

    test_embeddings(args.model)
