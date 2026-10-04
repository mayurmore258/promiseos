"""Orchestration Service for managing end-to-end PromiseOS workflows."""

from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import logger
from app.schemas.analysis import AnalyzeResponse
from app.schemas.followup import FollowupResponse
from app.schemas.verification import VerificationResponse
from app.services.analysis_service import AnalysisService
from app.services.commitment_service import CommitmentService
from app.services.evidence_service import EvidenceService
from app.services.followup_service import FollowupService
from app.services.verification_service import VerificationService


class OrchestrationService:
    """Provides high-level coordinator methods for the full commitment lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.analysis_svc = AnalysisService(session)
        self.commitment_svc = CommitmentService(session)
        self.evidence_svc = EvidenceService(session)
        self.verification_svc = VerificationService(session)
        self.followup_svc = FollowupService(session)

    async def run_full_pipeline_for_text(
        self,
        text: str,
        source: str = "conversation",
        user_id: Optional[str] = None,
    ) -> AnalyzeResponse:
        """Discovers commitments and generates initial evidence plans."""
        return await self.analysis_svc.analyze_text(text=text, source=source, user_id=user_id)

    async def verify_and_draft_followup(
        self,
        commitment_id: str,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Runs verification, and if unverified, partial, or contradictory, generates a follow-up draft."""
        ver_result = await self.verification_svc.verify_commitment(commitment_id, notes=notes)
        followup_result = None

        if ver_result.status in ("partial", "unverified", "unfulfilled", "contradictory"):
            followup_result = await self.followup_svc.generate_followup(commitment_id)

        return {
            "commitment_id": commitment_id,
            "verification": ver_result,
            "followup": followup_result,
        }
