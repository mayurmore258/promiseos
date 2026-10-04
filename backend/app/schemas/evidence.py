"""Evidence Pydantic Schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceUploadResponse(BaseModel):
    id: str = Field(..., description="UUID of created evidence record")
    commitment_id: Optional[str] = Field(None, description="Linked commitment ID if specified")
    file_name: str = Field(..., description="Sanitized file name")
    mime_type: str = Field(..., description="Detected MIME type")
    file_size: int = Field(..., description="File size in bytes")
    content_hash: str = Field(..., description="SHA-256 hash of content")
    chunk_count: int = Field(default=0, description="Number of text chunks created")
    is_duplicate: bool = Field(default=False, description="Whether this exact file hash already existed")
    created_at: datetime


class EvidenceSearchRequest(BaseModel):
    commitment_id: str = Field(..., description="Target commitment UUID to search evidence for")
    query: Optional[str] = Field(None, description="Optional custom query string (defaults to commitment description)")
    top_k: int = Field(default=5, ge=1, le=50, description="Max candidate chunks to return")


class EvidenceMatchChunk(BaseModel):
    chunk_id: str
    evidence_id: str
    file_name: str
    chunk_index: int
    content: str
    relevance_score: float = Field(..., ge=0.0, le=1.0)
    match_reasons: List[str] = Field(default_factory=list)


class EvidenceSearchResult(BaseModel):
    commitment_id: str
    total_found: int
    candidates: List[EvidenceMatchChunk]


class EvidenceItemResponse(BaseModel):
    id: str
    commitment_id: Optional[str]
    file_name: str
    evidence_type: str
    mime_type: str
    file_size: int
    content_hash: str
    relevance_score: float
    source_type: str
    metadata_json: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}
