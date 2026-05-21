import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from app.main import app


@pytest.mark.asyncio
async def test_upload_endpoint_rejects_invalid_type():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/documents/upload",
            files={"file": ("test.exe", b"not allowed", "application/octet-stream")},
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_document_status_not_found():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        with patch('app.api.documents.DocumentService') as MockService:
            mock_instance = MockService.return_value
            mock_instance.get_status = AsyncMock(side_effect=ValueError("Document not found"))

            response = await client.get("/api/documents/nonexistent/status")
            assert response.status_code == 404
