import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app


@pytest.mark.asyncio
async def test_full_chat_flow_mocked():
    """Integration test: upload -> status -> chat with mocked dependencies."""
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

        # 2. Upload document (mocked)
        with patch('app.api.documents.DocumentService') as MockDocService:
            mock_instance = MockDocService.return_value
            mock_instance.upload = AsyncMock(return_value={
                "document_id": "test-doc-id",
                "filename": "test.pdf",
                "status": "uploaded",
                "file_size_bytes": 1024,
            })

            resp = await client.post(
                "/api/documents/upload",
                files={"file": ("test.pdf", b"%PDF-1.4 fake pdf content", "application/pdf")},
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["document_id"] == "test-doc-id"
            assert data["status"] == "uploaded"

        # 3. Get document status (mocked)
        with patch('app.api.documents.DocumentService') as MockDocService:
            mock_instance = MockDocService.return_value
            mock_instance.get_status = AsyncMock(return_value={
                "id": "test-doc-id",
                "filename": "test.pdf",
                "file_type": "pdf",
                "status": "ready",
                "page_count": 5,
                "file_size_bytes": 1024,
                "error_message": None,
                "created_at": "2026-05-20T00:00:00",
                "updated_at": "2026-05-20T00:01:00",
            })

            resp = await client.get("/api/documents/test-doc-id/status")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ready"

        # 4. Chat query (mocked)
        with patch('app.api.chat.ChatService') as MockChatService:
            mock_instance = MockChatService.return_value
            mock_instance.chat = AsyncMock(return_value=iter(["RAG ", "combines ", "retrieval ", "with ", "generation."]))

            resp = await client.post("/api/chat", json={
                "query": "What is RAG?",
                "history": [],
            })

            assert resp.status_code == 200
            assert "text/event-stream" in resp.headers["content-type"]

            body = resp.text
            assert "data:" in body
            assert "RAG" in body
            assert "[DONE]" in body
