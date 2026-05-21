import pytest
from unittest.mock import AsyncMock, patch
from app.services.retrieval_service import RetrievalService


@pytest.mark.asyncio
async def test_hybrid_search_returns_combined_results():
    service = RetrievalService()

    with patch.object(service, '_vector_search', new_callable=AsyncMock) as mock_vector, \
         patch.object(service, '_bm25_search', new_callable=AsyncMock) as mock_bm25, \
         patch.object(service, '_rerank', new_callable=AsyncMock) as mock_rerank:

        mock_vector.return_value = [
            {"chunk_id": "a", "content": "Vector result 1", "score": 0.9},
            {"chunk_id": "b", "content": "Vector result 2", "score": 0.7},
        ]
        mock_bm25.return_value = [
            {"chunk_id": "b", "content": "BM25 result 1", "score": 0.8},
            {"chunk_id": "c", "content": "BM25 result 2", "score": 0.6},
        ]
        mock_rerank.return_value = [
            {"chunk_id": "b", "content": "BM25 result 1", "score": 0.85},
            {"chunk_id": "a", "content": "Vector result 1", "score": 0.82},
            {"chunk_id": "c", "content": "BM25 result 2", "score": 0.55},
        ]

        result = await service.search("What is RAG?")

        assert len(result) == 3
        assert result[0]["chunk_id"] == "b"
        mock_vector.assert_called_once()
        mock_bm25.assert_called_once()
        mock_rerank.assert_called_once()


@pytest.mark.asyncio
async def test_metadata_filter_injected():
    service = RetrievalService()
    with patch.object(service, '_vector_search', new_callable=AsyncMock) as mock_vector, \
         patch.object(service, '_bm25_search', new_callable=AsyncMock) as mock_bm25, \
         patch.object(service, '_rerank', new_callable=AsyncMock) as mock_rerank:

        mock_vector.return_value = []
        mock_bm25.return_value = []
        mock_rerank.return_value = []

        await service.search("query", filters={"tenant_id": "t1", "kb_id": "kb1"})

        call_kwargs = mock_vector.call_args[1]
        assert "filter" in call_kwargs
        assert call_kwargs["filter"]["tenant_id"] == "t1"
