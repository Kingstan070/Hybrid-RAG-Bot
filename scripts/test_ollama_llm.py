"""
CLI TEST – CHECK IF OLLAMA LLM WORKS
Run: python scripts/test_ollama_llm.py --model llama3.2:3b
"""

import argparse
from langchain_ollama import ChatOllama


def test_llm(model_name: str):
    llm = ChatOllama(model=model_name)
    response = llm.invoke(
        "Hello, are you working correctly? my name is allwin")
    print("\nResponse from LLM:")
    print(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="llama3.2:3b",
                        help="Name of Ollama model to test")

    args = parser.parse_args()

    test_llm(args.model)
