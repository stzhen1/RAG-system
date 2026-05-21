from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None
    history: List[Dict[str, str]] = Field(default_factory=list)
    filters: Optional[Dict[str, str]] = None


class Citation(BaseModel):
    document_name: str
    page: Optional[int] = None
    content_snippet: str
    score: float


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    citations: List[Citation] = Field(default_factory=list)
    created_at: str
