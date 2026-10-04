"""Verification Service coordinating evidence evaluation and status persistence."""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.verification_agent import verification_agent
from app.core.exceptions import NotFoundError
from app.core.logging import logger
from app.db.repositories.commitments import CommitmentRepository
from app.db.repositories.evidence import EvidenceRepository
from app.db.repositories.verification import VerificationRepository
from app.evidence.retrieval import evidence_retriever
from app.models.verification import VerificationResult
from app.schemas.verification import VerificationResponse, VerificationReviewRequest
from app.utils.ids import generate_uuid


class VerificationService:
    """Manages the verification pipeline execution and human review overrides."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.commitment_repo = CommitmentRepository(session)
        self.evidence_repo = EvidenceRepository(session)
        self.verification_repo = VerificationRepository(session)

    async def verify_commitment(
        self,
        commitment_id: str,
        notes: Optional[str] = None,
    ) -> VerificationResponse:
        commitment = await self.commitment_repo.get_by_id(commitment_id)
        if not commitment:
            raise NotFoundError("commitment", commitment_id)

        # 1. Fetch all evidence linked to this commitment or unassigned in workspace
        evidence_items = await self.evidence_repo.list_by_commitment(commitment_id, include_unassigned=True)

        # 2. Retrieve ranked candidate chunks
        candidate_chunks = evidence_retriever.retrieve(
            commitment=commitment,
            evidence_items=evidence_items,
            top_k=8,
        )

        # 3. Associate any unassigned evidence files whose chunks matched this commitment
        for ev in evidence_items:
            if ev.commitment_id is None:
                matching_chunks = [c for c in candidate_chunks if c.evidence_id == ev.id and c.relevance_score >= 0.20]
                if matching_chunks:
                    ev.commitment_id = commitment.id
                    ev.relevance_score = max(c.relevance_score for c in matching_chunks)
                    self.session.add(ev)

        # 4. Execute Verification Agent
        ver_response = await verification_agent.verify(
            commitment=commitment,
            candidate_evidence=candidate_chunks,
            notes=notes,
        )

        # 5. Persist VerificationResult
        now_dt = datetime.utcnow()
        ver_id = generate_uuid()
        result_model = VerificationResult(
            id=ver_id,
            commitment_id=commitment.id,
            status=ver_response.status,
            explanation=ver_response.explanation,
            evidence_summary=ver_response.evidence_summary,
            missing_items=ver_response.missing_items,
            contradictions=ver_response.contradictions,
            confidence=ver_response.confidence,
            verified_at=now_dt,
            created_at=now_dt,
        )
        await self.verification_repo.create(result_model)

        # 6. Update Commitment status to match verification
        await self.commitment_repo.update(commitment, {"status": ver_response.status})
        await self.session.commit()

        ver_response.id = ver_id
        logger.info(
            f"Verification completed for commitment {commitment_id}: status='{ver_response.status}', confidence={ver_response.confidence}",
            extra={"operation": "verify_commitment", "status": ver_response.status},
        )

        return ver_response

    async def review_verification(
        self,
        commitment_id: str,
        review: VerificationReviewRequest,
    ) -> VerificationResponse:
        """Human approval or override of verification result."""
        latest = await self.verification_repo.get_latest_by_commitment(commitment_id)
        if not latest:
            raise NotFoundError("verification_result", commitment_id)

        update_dict = {"status": review.status}
        if review.notes:
            update_dict["explanation"] = f"{latest.explanation}\n[Human Review]: {review.notes}"

        updated = await self.verification_repo.update(latest, update_dict)

        # Also update commitment status
        commitment = await self.commitment_repo.get_by_id(commitment_id)
        if commitment:
            await self.commitment_repo.update(commitment, {"status": review.status})

        return VerificationResponse(
            id=updated.id,
            commitment_id=updated.commitment_id,
            status=updated.status,
            evidence=[],
            explanation=updated.explanation,
            evidence_summary=updated.evidence_summary,
            missing_items=updated.missing_items,
            contradictions=updated.contradictions,
            confidence=updated.confidence,
            verified_at=updated.verified_at,
        )
