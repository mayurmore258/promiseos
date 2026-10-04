"""Evidence API Routes."""

from typing import Optional
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.evidence import (
    EvidenceSearchRequest,
    EvidenceSearchResult,
    EvidenceUploadResponse,
)
from app.services.evidence_service import EvidenceService

router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.post(
    "/upload",
    response_model=EvidenceUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Evidence File",
    description="Uploads and indexes an evidence document (TXT, PDF, DOCX, CSV, XLSX) linked to an optional commitment.",
)
async def upload_evidence(
    file: UploadFile = File(..., description="Evidence file (TXT, PDF, DOCX, CSV, XLSX)"),
    commitment_id: Optional[str] = Form(None, description="Optional commitment UUID to associate with this evidence"),
    session: AsyncSession = Depends(get_db),
):
    content_bytes = await file.read()
    service = EvidenceService(session)
    return await service.upload_evidence_file(
        file_bytes=content_bytes,
        original_filename=file.filename or "evidence.txt",
        content_type=file.content_type,
        commitment_id=commitment_id,
    )


@router.post(
    "/search",
    response_model=EvidenceSearchResult,
    status_code=status.HTTP_200_OK,
    summary="Search Evidence for Commitment",
    description="Finds and ranks candidate evidence chunks matching a commitment using multi-factor scoring.",
)
async def search_evidence(
    request: EvidenceSearchRequest,
    session: AsyncSession = Depends(get_db),
):
    service = EvidenceService(session)
    return await service.search_evidence(
        commitment_id=request.commitment_id,
        query=request.query,
        top_k=request.top_k,
    )
