import os
import sys

# Add the project root to sys.path
sys.path.append(os.getcwd())

from infrastructure.adapters.langchain_adapter import LangChainAdapter


def test_adapter():
    print("Testing LangChainAdapter...")
    adapter = LangChainAdapter()

    print("1. Testing generate_response...")
    response = adapter.generate_response("Hello, are you working?")
    print(f"Response: {response[:50]}...")
    assert len(response) > 0

    print("2. Testing get_embedding...")
    embedding = adapter.get_embedding("Test embedding")
    print(f"Embedding length: {len(embedding)}")
    assert len(embedding) > 0

    print("LangChainAdapter verification SUCCESSFUL!")


if __name__ == "__main__":
    try:
        test_adapter()
    except Exception as e:
        print(f"Verification FAILED: {e}")
        sys.exit(1)
