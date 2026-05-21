from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.document import DocumentUploadResponse, DocumentStatusResponse
from app.services.document_service import DocumentService
from app.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("pdf", "txt", "md"):
        raise HTTPException(status_code=400, detail=f"Unsupported file type: .{ext}")

    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {settings.max_upload_size_mb}MB limit")

    service = DocumentService()
    result = await service.upload(content, file.filename)
    return DocumentUploadResponse(**result)


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(document_id: str):
    service = DocumentService()
    try:
        result = await service.get_status(document_id)
        return DocumentStatusResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
