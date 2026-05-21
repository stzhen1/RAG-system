import pytest
from app.adapters.reranker_adapter import get_reranker


@pytest.mark.asyncio
async def test_reranker_interface():
    reranker = get_reranker()
    query = "What is RAG?"
    documents = [
        "RAG combines retrieval with generation.",
        "The sky is blue today.",
        "Vector databases are used for semantic search in RAG systems.",
    ]
    results = await reranker.rerank(query, documents)

    assert len(results) > 0
    assert "index" in results[0]
    assert "score" in results[0]
    assert "document" in results[0]
    scores = {r["index"]: r["score"] for r in results}
    assert scores[0] > scores[1] or scores[2] > scores[1]
