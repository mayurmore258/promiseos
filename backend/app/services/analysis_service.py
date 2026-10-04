"""Analysis Service for coordinating commitment extraction and initial evidence planning."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.commitment_agent import commitment_agent
from app.agents.evidence_planner import evidence_planner
from app.core.exceptions import ValidationError
from app.core.logging import logger
from app.db.repositories.commitments import CommitmentRepository
from app.models.commitment import Commitment
from app.models.followup import AnalysisRun
from app.schemas.analysis import AnalyzeResponse
from app.schemas.commitment import CommitmentResponse
from app.utils.ids import generate_uuid


class AnalysisService:
    """Orchestrates communication parsing, commitment discovery, and evidence planning."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CommitmentRepository(session)

    async def analyze_text(
        self,
        text: str,
        source: str = "conversation",
        user_id: Optional[str] = None,
    ) -> AnalyzeResponse:
        if not text or not text.strip():
            raise ValidationError("Input text cannot be empty or whitespace only.")

        logger.info(
            f"Analyzing communication text ({len(text)} chars) from source '{source}'",
            extra={"operation": "analyze_text", "source": source},
        )

        # 1. Discover commitments
        extracted_creates = await commitment_agent.extract_commitments(
            text=text,
            source=source,
            user_id=user_id,
        )

        created_commitments: List[Commitment] = []

        # 2. Plan evidence requirements & persist
        for c_create in extracted_creates:
            # Plan evidence requirements if not already present
            if not c_create.expected_evidence:
                c_dict = c_create.model_dump()
                planned_ev = await evidence_planner.plan_evidence(c_dict)
                c_create.expected_evidence = planned_ev

            model = Commitment(
                id=generate_uuid(),
                user_id=c_create.user_id,
                person=c_create.person,
                action=c_create.action,
                object=c_create.object,
                description=c_create.description,
                deadline=c_create.deadline,
                deadline_raw=c_create.deadline_raw,
                source=c_create.source,
                source_excerpt=c_create.source_excerpt,
                expected_evidence=c_create.expected_evidence,
                status=c_create.status,
                confidence=c_create.confidence,
            )
            persisted = await self.repo.create(model)
            created_commitments.append(persisted)

        # 3. Audit analysis run
        run = AnalysisRun(
            id=generate_uuid(),
            user_id=user_id,
            raw_input=text,
            extracted_count=len(created_commitments),
        )
        self.session.add(run)
        await self.session.flush()

        logger.info(
            f"Analysis complete. Discovered and persisted {len(created_commitments)} commitments.",
            extra={"operation": "analyze_text", "extracted_count": len(created_commitments)},
        )

        commitment_responses = [
            CommitmentResponse.model_validate(c) for c in created_commitments
        ]

        return AnalyzeResponse(
            analysis_id=run.id,
            total_commitments=len(commitment_responses),
            commitments=commitment_responses,
        )
