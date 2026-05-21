from pydantic import BaseModel
from typing import Optional


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    file_size_bytes: int


class DocumentStatusResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str
    page_count: Optional[int] = None
    file_size_bytes: int
    error_message: Optional[str] = None
    created_at: str
    updated_at: str
