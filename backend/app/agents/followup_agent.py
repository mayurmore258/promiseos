"""Followup Agent for drafting polite, non-accusatory communications.

Never autonomously sends messages. Drafts require human review and approval.
"""

from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.llm.router import llm_router
from app.models.commitment import Commitment
from app.schemas.verification import VerificationResponse


class FollowupAgent:
    """Generates polite, action-oriented follow-up message drafts."""

    SYSTEM_PROMPT = """You are the PromiseOS Followup Drafting Agent.
Your job is to draft a polite, constructive, professional, and non-accusatory follow-up message.

Guidelines:
1. Never accuse or blame anyone.
2. Acknowledge what appears complete or what progress has been made.
3. Gently point out remaining missing items or needed clarifications.
4. Ask what the next step should be or when an update might be expected.
5. Keep it concise (2-4 sentences).
6. Note: This message is a draft for human review. It will NEVER be sent automatically.

Return JSON:
{
  "draft": "The message text",
  "tone": "polite"
}
"""

    async def draft_followup(
        self,
        commitment: Commitment,
        verification: Optional[VerificationResponse] = None,
        tone: str = "polite",
        custom_instruction: Optional[str] = None,
    ) -> str:
        logger.info(
            f"Drafting follow-up for commitment {commitment.id}",
            extra={"operation": "draft_followup", "commitment_id": commitment.id},
        )

        ver_dict = {}
        if verification:
            ver_dict = {
                "status": verification.status,
                "explanation": verification.explanation,
                "missing_items": verification.missing_items,
                "contradictions": verification.contradictions,
            }

        input_text = (
            f"Committer: {commitment.person}\n"
            f"Commitment: {commitment.description}\n"
            f"Deadline: {commitment.deadline_raw}\n"
            f"Status: {ver_dict.get('status', commitment.status)}\n"
            f"Missing Items: {ver_dict.get('missing_items', [])}\n"
            f"Tone: {tone}\n"
        )
        if custom_instruction:
            input_text += f"Custom Instruction: {custom_instruction}\n"

        result = await llm_router.generate(
            task="followup_generation",
            input_text=input_text,
            context={
                "commitment": {
                    "person": commitment.person,
                    "action": commitment.action,
                    "object": commitment.object,
                    "description": commitment.description,
                    "deadline_raw": commitment.deadline_raw,
                },
                "verification": ver_dict,
                "tone": tone,
            },
            system_prompt=self.SYSTEM_PROMPT,
        )

        parsed = result.parsed_json or {}
        draft = parsed.get("draft")
        if draft and draft.strip():
            return draft.strip()

        # Fallback polite draft
        return (
            f"Hi {commitment.person}, friendly check-in on the {commitment.object}. "
            "Could you please share an update when you have a moment? Thanks!"
        )


followup_agent = FollowupAgent()
