"""Followup Service for drafting and human approval."""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.followup_agent import followup_agent
from app.core.exceptions import NotFoundError
from app.core.logging import logger
from app.db.repositories.commitments import CommitmentRepository
from app.db.repositories.followups import FollowupRepository
from app.db.repositories.verification import VerificationRepository
from app.models.followup import Followup
from app.schemas.followup import FollowupApproveRequest, FollowupResponse
from app.schemas.verification import VerificationResponse
from app.utils.ids import generate_uuid


class FollowupService:
    """Manages generation of follow-up drafts and human approval."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.commitment_repo = CommitmentRepository(session)
        self.verification_repo = VerificationRepository(session)
        self.followup_repo = FollowupRepository(session)

    async def generate_followup(
        self,
        commitment_id: str,
        tone: str = "polite",
        custom_instruction: Optional[str] = None,
    ) -> FollowupResponse:
        commitment = await self.commitment_repo.get_by_id(commitment_id)
        if not commitment:
            raise NotFoundError("commitment", commitment_id)

        latest_ver = await self.verification_repo.get_latest_by_commitment(commitment_id)
        ver_resp = None
        if latest_ver:
            ver_resp = VerificationResponse(
                id=latest_ver.id,
                commitment_id=latest_ver.commitment_id,
                status=latest_ver.status,
                evidence=[],
                explanation=latest_ver.explanation,
                evidence_summary=latest_ver.evidence_summary,
                missing_items=latest_ver.missing_items,
                contradictions=latest_ver.contradictions,
                confidence=latest_ver.confidence,
            )

        draft_text = await followup_agent.draft_followup(
            commitment=commitment,
            verification=ver_resp,
            tone=tone,
            custom_instruction=custom_instruction,
        )

        followup_id = generate_uuid()
        followup_model = Followup(
            id=followup_id,
            commitment_id=commitment.id,
            draft=draft_text,
            approved=False,
            created_at=datetime.utcnow(),
        )
        saved = await self.followup_repo.create(followup_model)

        logger.info(
            f"Generated follow-up draft {followup_id} for commitment {commitment_id}",
            extra={"operation": "generate_followup", "followup_id": followup_id},
        )

        return FollowupResponse.model_validate(saved)

    async def approve_followup(
        self,
        followup_id: str,
        approval: FollowupApproveRequest,
    ) -> FollowupResponse:
        followup = await self.followup_repo.get_by_id(followup_id)
        if not followup:
            raise NotFoundError("followup", followup_id)

        update_dict = {}
        if approval.edited_draft is not None:
            update_dict["draft"] = approval.edited_draft.strip()

        if approval.approved:
            followup.approved = True
            followup.approved_at = datetime.utcnow()
            update_dict["approved"] = True
            update_dict["approved_at"] = datetime.utcnow()
        else:
            update_dict["approved"] = False
            update_dict["approved_at"] = None

        updated = await self.followup_repo.update(followup, update_dict)

        logger.info(
            f"Follow-up {followup_id} approval recorded: approved={updated.approved}",
            extra={"operation": "approve_followup", "followup_id": followup_id},
        )

        return FollowupResponse.model_validate(updated)
