"""Commitment Extraction Agent.

Discovers commitments from messy human communication.
Preserves verbatim wording, relative deadlines, and uncertainty.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger
from app.llm.router import llm_router
from app.schemas.commitment import CommitmentCreate
from app.services.ml_service import MLCommitmentService, ml_commitment_service
from app.utils.dates import parse_deadline


class CommitmentAgent:
    """Extracts structured commitments (who, what, when, source excerpt) from communication."""

    def __init__(self, ml_service: Optional[MLCommitmentService] = None):
        self.ml_service = ml_service or ml_commitment_service

    SYSTEM_PROMPT = """You are the PromiseOS Commitment Extraction Agent.
Your job is to discover commitments from messy human communication (e.g., chat logs, emails, notes).

For each promise or commitment, extract:
- person: Name of the person who made the promise (e.g. Rahul).
- action: Verb of commitment (e.g. Send, Update, Deliver, Review).
- object: The deliverable or subject (e.g. quotation, pricing sheet).
- description: Human-readable summary of the commitment.
- deadline_raw: Original verbatim deadline phrasing (e.g., "tonight", "tomorrow", "next Friday", "in 2 hours"). Do not invent!
- source_excerpt: The verbatim sentence or message from the input text containing this commitment.
- confidence: Float between 0.0 and 1.0.

RULES:
1. Do not fabricate commitments.
2. If communication is merely acknowledgment ("ok", "sure", "thanks"), do NOT extract it as a commitment.
3. If deadline is ambiguous or unspecified, preserve deadline_raw as null or the verbatim word ("soon", "later").
4. Output a JSON array of objects conforming to the schema.
"""

    async def extract_commitments(
        self,
        text: str,
        source: str = "conversation",
        user_id: Optional[str] = None,
        reference_dt: Optional[datetime] = None,
    ) -> List[CommitmentCreate]:
        """Extracts candidate commitments and resolves dates without destroying raw text."""
        logger.info("Executing commitment extraction agent", extra={"operation": "extract_commitments"})

        result = await llm_router.generate(
            task="commitment_extraction",
            input_text=text,
            context={"source": source},
            system_prompt=self.SYSTEM_PROMPT,
        )

        commitments_raw = result.parsed_json or []
        if isinstance(commitments_raw, dict) and "commitments" in commitments_raw:
            commitments_raw = commitments_raw["commitments"]

        commitments: List[CommitmentCreate] = []

        for item in commitments_raw:
            if not isinstance(item, dict):
                continue

            person = item.get("person") or "Unknown"
            if isinstance(person, str) and person.strip().lower() in ("none", "null", ""):
                person = "Unknown"
            action = item.get("action") or "Complete"
            obj = item.get("object") or "task"
            description = item.get("description") or f"{action} {obj}"
            raw_dl = item.get("deadline_raw")
            source_excerpt = item.get("source_excerpt", text[:120])
            expected_evidence = item.get("expected_evidence", [])
            confidence = float(item.get("confidence", 0.9))

            # Normalize date while strictly preserving raw text
            deadline_text, normalized_dt = parse_deadline(raw_dl, reference_dt=reference_dt)

            # Local ML classification on candidate source excerpt if feature flag enabled
            ml_label = None
            ml_confidence = None

            if settings.ML_COMMITMENT_ENABLED:
                target_excerpt = source_excerpt or description or text[:120]
                ml_pred = self.ml_service.predict(target_excerpt)
                ml_label = ml_pred.label
                ml_confidence = ml_pred.probability

            commitments.append(
                CommitmentCreate(
                    user_id=user_id,
                    person=person,
                    action=action,
                    object=obj,
                    description=description,
                    deadline=normalized_dt,
                    deadline_raw=deadline_text,
                    source=source,
                    source_excerpt=source_excerpt,
                    expected_evidence=expected_evidence,
                    status="pending",
                    confidence=confidence,
                    ml_label=ml_label,
                    ml_confidence=ml_confidence,
                )
            )

        logger.info(
            f"Extracted {len(commitments)} commitments from text",
            extra={"operation": "extract_commitments", "count": len(commitments)},
        )
        return commitments


commitment_agent = CommitmentAgent()
