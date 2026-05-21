import pytest


@pytest.fixture
def sample_text():
    return "Retrieval-Augmented Generation combines search with language models."


@pytest.fixture
def sample_chunks():
    return [
        "RAG is a technique that combines information retrieval with text generation.",
        "Vector databases store embeddings for semantic search.",
        "BM25 is a bag-of-words retrieval function that ranks documents.",
        "PostgreSQL supports full-text search through tsvector and GIN indexes.",
        "Hybrid search combines vector similarity with keyword matching.",
    ]
