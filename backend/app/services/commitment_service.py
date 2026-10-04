"""Commitment management and human review service."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundError
from app.core.logging import logger
from app.db.repositories.commitments import CommitmentRepository
from app.models.commitment import Commitment
from app.schemas.commitment import (
    CommitmentDetailResponse,
    CommitmentResponse,
    CommitmentReviewRequest,
    CommitmentUpdate,
)
from app.utils.dates import parse_deadline


class CommitmentService:
    """Provides business logic for querying, editing, and reviewing commitments."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CommitmentRepository(session)

    async def get_commitment_detail(self, commitment_id: str) -> CommitmentDetailResponse:
        commitment = await self.repo.get_by_id(commitment_id, load_relations=True)
        if not commitment:
            raise NotFoundError("commitment", commitment_id)

        evidence_items = [
            {
                "id": e.id,
                "file_name": e.file_name,
                "evidence_type": e.evidence_type,
                "mime_type": e.mime_type,
                "file_size": e.file_size,
                "content_hash": e.content_hash,
                "relevance_score": e.relevance_score,
                "created_at": e.created_at.isoformat(),
            }
            for e in commitment.evidence_items
        ]

        latest_ver = (
            max(commitment.verification_results, key=lambda v: getattr(v, "created_at", None) or getattr(v, "verified_at", None) or datetime.min)
            if commitment.verification_results
            else None
        )
        ver_dict = None
        if latest_ver:
            ver_dict = {
                "id": latest_ver.id,
                "status": latest_ver.status,
                "explanation": latest_ver.explanation,
                "evidence_summary": latest_ver.evidence_summary,
                "missing_items": latest_ver.missing_items,
                "contradictions": latest_ver.contradictions,
                "confidence": latest_ver.confidence,
                "verified_at": latest_ver.verified_at.isoformat() if latest_ver.verified_at else None,
            }

        latest_followup = (
            max(commitment.followups, key=lambda f: getattr(f, "created_at", None) or datetime.min)
            if commitment.followups
            else None
        )
        followup_dict = None
        if latest_followup:
            followup_dict = {
                "id": latest_followup.id,
                "draft": latest_followup.draft,
                "approved": latest_followup.approved,
                "approved_at": latest_followup.approved_at.isoformat() if latest_followup.approved_at else None,
                "created_at": latest_followup.created_at.isoformat(),
            }

        resp = CommitmentDetailResponse(
            id=commitment.id,
            user_id=commitment.user_id,
            person=commitment.person,
            action=commitment.action,
            object=commitment.object,
            description=commitment.description,
            deadline=commitment.deadline,
            deadline_raw=commitment.deadline_raw,
            source=commitment.source,
            source_excerpt=commitment.source_excerpt,
            expected_evidence=commitment.expected_evidence or [],
            status=commitment.status,
            confidence=commitment.confidence,
            created_at=commitment.created_at,
            updated_at=commitment.updated_at,
            evidence=evidence_items,
            verification=ver_dict,
            followup=followup_dict,
        )
        return resp

    async def list_commitments(
        self,
        status: Optional[str] = None,
        person: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CommitmentResponse]:
        items = await self.repo.list(status=status, person=person, limit=limit, offset=offset)
        return [CommitmentResponse.model_validate(c) for c in items]

    async def update_commitment(
        self,
        commitment_id: str,
        update_dto: CommitmentUpdate,
    ) -> CommitmentResponse:
        commitment = await self.repo.get_by_id(commitment_id)
        if not commitment:
            raise NotFoundError("commitment", commitment_id)

        update_dict = update_dto.model_dump(exclude_unset=True)

        # If raw deadline is being updated, re-normalize
        if "deadline_raw" in update_dict and update_dict["deadline_raw"]:
            raw_dl, norm_dl = parse_deadline(update_dict["deadline_raw"])
            update_dict["deadline_raw"] = raw_dl
            if "deadline" not in update_dict or update_dict["deadline"] is None:
                update_dict["deadline"] = norm_dl

        updated = await self.repo.update(commitment, update_dict)
        logger.info(
            f"Updated commitment {commitment_id}",
            extra={"operation": "update_commitment", "commitment_id": commitment_id},
        )
        return CommitmentResponse.model_validate(updated)

    async def review_commitment(
        self,
        commitment_id: str,
        review: CommitmentReviewRequest,
    ) -> CommitmentResponse:
        """Human review action to confirm or correct commitment status."""
        commitment = await self.repo.get_by_id(commitment_id)
        if not commitment:
            raise NotFoundError("commitment", commitment_id)

        updated = await self.repo.update(commitment, {"status": review.status})
        logger.info(
            f"Human reviewed commitment {commitment_id}: new status='{review.status}'",
            extra={"operation": "review_commitment", "commitment_id": commitment_id},
        )
        return CommitmentResponse.model_validate(updated)
