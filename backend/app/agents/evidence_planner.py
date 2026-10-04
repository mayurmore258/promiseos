"""Evidence Planning Agent.

Determines what observable facts or artifacts would prove a commitment was fulfilled.
"""

from typing import Any, Dict, List
from app.core.logging import logger
from app.llm.router import llm_router


class EvidencePlanner:
    """Plans concrete evidence requirements for a given commitment."""

    SYSTEM_PROMPT = """You are the PromiseOS Evidence Planning Agent.
For any given commitment, identify 2-4 observable, concrete facts or artifacts that would prove fulfillment.

Ask yourself: "What observable facts would prove this commitment was fulfilled?"
Examples:
- Commitment: Send quotation tonight.
  Observable facts: ["quotation document (PDF/text)", "sent email or chat message", "timestamp before deadline"]
- Commitment: Update pricing sheet tomorrow.
  Observable facts: ["updated pricing sheet / CSV", "delivery cost updates", "version change log"]

Return a JSON array of concise string requirements.
"""

    async def plan_evidence(self, commitment_dict: Dict[str, Any]) -> List[str]:
        """Generates evidence requirements for the commitment."""
        logger.info(
            f"Planning evidence for commitment '{commitment_dict.get('description')}'",
            extra={"operation": "plan_evidence", "commitment_id": commitment_dict.get("id")},
        )

        input_text = (
            f"Person: {commitment_dict.get('person')}\n"
            f"Action: {commitment_dict.get('action')}\n"
            f"Deliverable/Object: {commitment_dict.get('object')}\n"
            f"Description: {commitment_dict.get('description')}\n"
            f"Deadline: {commitment_dict.get('deadline_raw')}"
        )

        result = await llm_router.generate(
            task="evidence_planning",
            input_text=input_text,
            context=commitment_dict,
            system_prompt=self.SYSTEM_PROMPT,
        )

        planned = result.parsed_json or []
        if isinstance(planned, dict) and "expected_evidence" in planned:
            planned = planned["expected_evidence"]

        if isinstance(planned, list) and planned:
            return [str(item) for item in planned]

        # Default fallback if empty
        obj = commitment_dict.get("object", "deliverable")
        return [
            f"{obj} document or file",
            "proof of dispatch / timestamp",
            "acknowledgment or delivery confirmation",
        ]


evidence_planner = EvidencePlanner()
