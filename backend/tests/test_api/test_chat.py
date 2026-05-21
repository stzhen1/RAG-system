import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app


@pytest.mark.asyncio
async def test_chat_endpoint_returns_sse():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch('app.api.chat.ChatService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.chat = AsyncMock(return_value=iter(["Test response"]))

            response = await client.post("/api/chat", json={
                "query": "What is RAG?",
                "history": [],
            })

            assert response.status_code == 200
            assert "text/event-stream" in response.headers["content-type"]
