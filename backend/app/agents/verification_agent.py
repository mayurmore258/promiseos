"""Verification Agent for assessing commitment fulfillment against evidence.

Core Philosophy:
- Evidence over assumption.
- Verification over accusation.
- Never treat absence of evidence as automatic proof of failure.
- Safe uncertainty state: UNVERIFIED.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.llm.router import llm_router
from app.models.commitment import Commitment
from app.schemas.evidence import EvidenceMatchChunk
from app.schemas.verification import VerificationEvidenceItem, VerificationResponse, VerificationStatus


class VerificationAgent:
    """Evaluates candidate evidence against commitment requirements and outputs structured verdict."""

    SYSTEM_PROMPT = """You are the PromiseOS Verification Agent.
You compare WHAT WAS PROMISED against WHAT THE EVIDENCE SHOWS.

Core Principles:
1. Evidence over assumption. Verification over accusation.
2. Use ONLY supplied evidence. Distinguish evidence from inference.
3. NEVER treat absence of evidence as automatic proof of failure! If evidence is absent or insufficient, return UNVERIFIED.
4. If available evidence conflicts, return CONTRADICTORY.
5. If some parts are verified but others missing, return PARTIAL.
6. If all key requirements are confirmed by evidence, return FULFILLED.
7. Return UNFULFILLED ONLY when there is affirmative evidence confirming non-fulfillment or failure.

Every verification explanation MUST clearly detail:
1. What was promised
2. What evidence was found
3. What evidence proves
4. What remains uncertain
5. Why this status was assigned

Return JSON:
{
  "status": "fulfilled|partial|unfulfilled|unverified|contradictory",
  "explanation": "Structured explanation covering the 5 points",
  "evidence_summary": "Brief summary of evidence used",
  "missing_items": ["item 1", "item 2"],
  "contradictions": [],
  "confidence": 0.95
}
"""

    async def verify(
        self,
        commitment: Commitment,
        candidate_evidence: List[EvidenceMatchChunk],
        notes: Optional[str] = None,
    ) -> VerificationResponse:
        logger.info(
            f"Verifying commitment {commitment.id} ('{commitment.description}') with {len(candidate_evidence)} candidate chunks",
            extra={"operation": "verify_commitment", "commitment_id": commitment.id},
        )

        # Build context
        com_dict = {
            "id": commitment.id,
            "person": commitment.person,
            "action": commitment.action,
            "object": commitment.object,
            "description": commitment.description,
            "deadline_raw": commitment.deadline_raw,
            "deadline": commitment.deadline.isoformat() if commitment.deadline else None,
            "expected_evidence": commitment.expected_evidence or [],
            "source_excerpt": commitment.source_excerpt,
        }

        ev_list = [
            {
                "file_name": c.file_name,
                "content": c.content,
                "relevance_score": c.relevance_score,
                "match_reasons": c.match_reasons,
            }
            for c in candidate_evidence
        ]

        prompt_input = (
            f"COMMITMENT:\n"
            f"- Person: {commitment.person}\n"
            f"- Action: {commitment.action}\n"
            f"- Object: {commitment.object}\n"
            f"- Description: {commitment.description}\n"
            f"- Deadline: {commitment.deadline_raw}\n"
            f"- Expected Evidence: {', '.join(commitment.expected_evidence or [])}\n\n"
            f"AVAILABLE EVIDENCE ({len(candidate_evidence)} items):\n"
        )

        if not candidate_evidence:
            prompt_input += "No evidence uploaded or retrieved for this commitment."
        else:
            for idx, c in enumerate(candidate_evidence):
                prompt_input += f"\n[Evidence {idx+1}] File: {c.file_name} (Score: {c.relevance_score})\nContent: {c.content}\n"

        if notes:
            prompt_input += f"\nReviewer Notes: {notes}\n"

        result = await llm_router.generate(
            task="verification",
            input_text=prompt_input,
            context={"commitment": com_dict, "evidence": ev_list, "notes": notes},
            system_prompt=self.SYSTEM_PROMPT,
        )

        parsed = result.parsed_json or {}
        raw_status = str(parsed.get("status", "unverified")).lower()

        valid_statuses = {"fulfilled", "partial", "unfulfilled", "unverified", "contradictory"}
        status: VerificationStatus = raw_status if raw_status in valid_statuses else "unverified"

        # Safe guard: if there is truly no evidence, status MUST be unverified
        if not candidate_evidence and status in ("unfulfilled", "fulfilled", "partial"):
            status = "unverified"
            explanation = (
                f"No evidence has been provided yet for {commitment.person}'s commitment '{commitment.description}'. "
                "Under PromiseOS safety rules, absence of evidence is not proof of failure; therefore status is UNVERIFIED."
            )
        else:
            explanation = parsed.get(
                "explanation",
                f"Commitment '{commitment.description}' evaluated against {len(candidate_evidence)} evidence segments.",
            )

        evidence_items_out: List[VerificationEvidenceItem] = [
            VerificationEvidenceItem(
                file_name=c.file_name,
                excerpt=c.content[:200] + ("..." if len(c.content) > 200 else ""),
                relevance_score=c.relevance_score,
                source_type="uploaded_file",
            )
            for c in candidate_evidence
        ]

        return VerificationResponse(
            commitment_id=commitment.id,
            status=status,
            evidence=evidence_items_out,
            explanation=explanation,
            evidence_summary=parsed.get("evidence_summary", f"{len(candidate_evidence)} evidence excerpts evaluated."),
            missing_items=parsed.get("missing_items", []),
            contradictions=parsed.get("contradictions", []),
            confidence=float(parsed.get("confidence", 0.85 if candidate_evidence else 0.5)),
            verified_at=datetime.utcnow(),
        )


verification_agent = VerificationAgent()
