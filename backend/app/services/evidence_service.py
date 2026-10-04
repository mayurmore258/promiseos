"""Evidence Ingestion and Search Service."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.evidence_agent import evidence_agent
from app.core.exceptions import NotFoundError
from app.core.logging import logger
from app.db.repositories.commitments import CommitmentRepository
from app.db.repositories.evidence import EvidenceRepository
from app.models.evidence import Evidence, EvidenceChunk
from app.schemas.evidence import (
    EvidenceItemResponse,
    EvidenceSearchResult,
    EvidenceUploadResponse,
)
from app.services.file_service import file_service
from app.utils.ids import generate_uuid


class EvidenceService:
    """Manages evidence file uploading, duplicate detection, and candidate retrieval."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.evidence_repo = EvidenceRepository(session)
        self.commitment_repo = CommitmentRepository(session)

    async def upload_evidence_file(
        self,
        file_bytes: bytes,
        original_filename: str,
        content_type: str = None,
        commitment_id: Optional[str] = None,
    ) -> EvidenceUploadResponse:
        # Validate commitment if provided
        commitment = None
        if commitment_id:
            commitment = await self.commitment_repo.get_by_id(commitment_id)
            if not commitment:
                raise NotFoundError("commitment", commitment_id)

        # Process file through file service
        (
            clean_name,
            storage_path,
            mime,
            size,
            content_hash,
            metadata,
            chunks,
            raw_text,
        ) = file_service.process_file_content(file_bytes, original_filename, content_type)

        # Check for duplicate file for this commitment
        existing = await self.evidence_repo.find_by_hash(content_hash, commitment_id=commitment_id)
        if existing:
            logger.info(
                f"Duplicate evidence detected for hash {content_hash[:8]} and commitment {commitment_id}",
                extra={"operation": "upload_evidence", "is_duplicate": True},
            )
            return EvidenceUploadResponse(
                id=existing.id,
                commitment_id=existing.commitment_id,
                file_name=existing.file_name,
                mime_type=existing.mime_type,
                file_size=existing.file_size,
                content_hash=existing.content_hash,
                chunk_count=len(chunks),
                is_duplicate=True,
                created_at=existing.created_at,
            )

        # Create Evidence record
        evidence_id = generate_uuid()
        evidence_model = Evidence(
            id=evidence_id,
            commitment_id=commitment_id,
            file_name=clean_name,
            content_reference=storage_path,
            evidence_type="document" if "pdf" in clean_name or "doc" in clean_name else ("sheet" if "csv" in clean_name or "xls" in clean_name else "text"),
            mime_type=mime,
            file_size=size,
            content_hash=content_hash,
            relevance_score=0.0,
            source_type="uploaded_file",
            raw_text=raw_text,
            metadata_json=metadata,
        )
        saved_evidence = await self.evidence_repo.create(evidence_model)

        # Create chunk records
        chunk_models = [
            EvidenceChunk(
                id=generate_uuid(),
                evidence_id=evidence_id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                metadata_json=c.get("metadata_json", {}),
            )
            for c in chunks
        ]
        if chunk_models:
            await self.evidence_repo.create_chunks(chunk_models)

        logger.info(
            f"Uploaded and indexed evidence '{clean_name}' for commitment {commitment_id}",
            extra={"operation": "upload_evidence", "evidence_id": evidence_id},
        )

        return EvidenceUploadResponse(
            id=saved_evidence.id,
            commitment_id=saved_evidence.commitment_id,
            file_name=saved_evidence.file_name,
            mime_type=saved_evidence.mime_type,
            file_size=saved_evidence.file_size,
            content_hash=saved_evidence.content_hash,
            chunk_count=len(chunk_models),
            is_duplicate=False,
            created_at=saved_evidence.created_at,
        )

    async def search_evidence(
        self,
        commitment_id: str,
        query: Optional[str] = None,
        top_k: int = 5,
    ) -> EvidenceSearchResult:
        commitment = await self.commitment_repo.get_by_id(commitment_id)
        if not commitment:
            raise NotFoundError("commitment", commitment_id)

        evidence_items = await self.evidence_repo.list_by_commitment(commitment_id)
        return await evidence_agent.search_evidence(
            commitment=commitment,
            evidence_items=evidence_items,
            top_k=top_k,
            custom_query=query,
        )
