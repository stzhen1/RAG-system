import pytest
from unittest.mock import AsyncMock, patch
from app.services.document_service import DocumentService


@pytest.mark.asyncio
async def test_upload_triggers_pipeline():
    service = DocumentService()

    with patch.object(service, '_store_file', new_callable=AsyncMock) as mock_store, \
         patch.object(service, '_create_document_record', new_callable=AsyncMock) as mock_create, \
         patch('app.services.document_service.run_ingestion_pipeline') as mock_pipeline:

        mock_store.return_value = "minio://bucket/doc.pdf"
        mock_create.return_value = None

        result = await service.upload(b"file content", "test.pdf")

        assert result["document_id"] is not None
        assert result["status"] == "uploaded"
        mock_pipeline.assert_called_once()


@pytest.mark.asyncio
async def test_upload_rejects_oversized_file():
    service = DocumentService()
    huge_file = b"x" * (101 * 1024 * 1024)
    with pytest.raises(ValueError, match="exceeds"):
        await service.upload(huge_file, "large.pdf")


@pytest.mark.asyncio
async def test_get_status_returns_document_state():
    service = DocumentService()

    with patch.object(service, '_get_document', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            "id": "doc-1",
            "filename": "test.pdf",
            "status": "ready",
            "page_count": 10,
        }

        result = await service.get_status("doc-1")
        assert result["status"] == "ready"
        assert result["filename"] == "test.pdf"


@pytest.mark.asyncio
async def test_get_status_not_found():
    service = DocumentService()

    with patch.object(service, '_get_document', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        with pytest.raises(ValueError, match="not found"):
            await service.get_status("nonexistent")
