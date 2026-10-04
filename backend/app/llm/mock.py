"""Mock LLM Provider for local development, tests, and offline execution.

Produces deterministic structured outputs conforming to Pydantic schemas.
Clearly marked as mock development mode.
"""

import json
import re
import time
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel
from app.llm.base import BaseLLMProvider, LLMResult


class MockLLMProvider(BaseLLMProvider):
    """Deterministic local mock provider requiring no external API keys."""

    def __init__(self):
        super().__init__(name="mock", is_configured=True)

    async def generate(
        self,
        task: str,
        input_text: str,
        schema: Optional[Type[BaseModel]] = None,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> LLMResult:
        start_time = time.time()
        ctx = context or {}

        if task == "commitment_extraction":
            parsed = self._extract_commitments(input_text)
        elif task == "evidence_planning":
            parsed = self._plan_evidence(input_text, ctx)
        elif task == "verification":
            parsed = self._verify_commitment(input_text, ctx)
        elif task == "followup_generation":
            parsed = self._generate_followup(input_text, ctx)
        else:
            parsed = {"status": "ok", "message": f"Mock output for unknown task {task}"}

        raw_json = json.dumps(parsed, indent=2)
        latency = (time.time() - start_time) * 1000

        return LLMResult(
            task=task,
            provider="mock (development/test mode)",
            model="promiseos-mock-engine-v1",
            raw_text=raw_json,
            parsed_json=parsed,
            latency_ms=round(latency, 2),
            success=True,
        )

    def _extract_commitments(self, text: str) -> List[Dict[str, Any]]:
        """Extracts commitments deterministically from conversation text."""
        commitments = []
        raw_lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Split compound clauses if " and I'll " or " and I will " or " and we'll " exists
        raw_lines = []
        for line in text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            # If line has multiple sentences with commitment markers, split them
            sentences = re.split(r"(?<=[.!?])\s+(?=(?:i'll|i\s+will|we'll|we\s+will|rahul:|mayur:|[A-Z][a-z]+:)\b)", line_str, flags=re.IGNORECASE)
            raw_lines.extend([s.strip() for s in sentences if s.strip()])

        lines = []
        for line in raw_lines:
            # Check for speaker prefix e.g. "Rahul: ..."
            speaker_prefix = ""
            content = line
            if ":" in line:
                parts = line.split(":", 1)
                speaker_prefix = parts[0].strip() + ": "
                content = parts[1].strip()

            sub_clauses = re.split(r"\s+and\s+(?=(?:i'll|i\s+will|we'll|we\s+will)\b)", content, flags=re.IGNORECASE)
            for sc in sub_clauses:
                lines.append(f"{speaker_prefix}{sc.strip()}".strip())

        for line in lines:
            line_lower = line.lower()
            # Extract speaker if "Speaker: message"
            speaker = "Unknown"
            msg = line
            if ":" in line:
                parts = line.split(":", 1)
                speaker = parts[0].strip()
                msg = parts[1].strip()
            msg_lower = msg.lower()

            # Skip acknowledgments and purely past discussions (non-commitments)
            if msg_lower in ("okay.", "ok", "sure", "thanks", "got it", "fine."):
                continue
            if not any(pat in msg_lower for pat in ["i'll", "i will", "promise to", "we will", "we'll", "will send", "will update", "i completed", "completed the payment", "i have completed", "completed payment"]):
                continue

            # Identify committer person or target entity
            person = speaker if speaker != "Unknown" else "Rahul"
            if speaker == "Unknown":
                if "rahul" in msg_lower:
                    person = "Rahul"
                elif "mayur" in msg_lower:
                    person = "Mayur"

            # Extract deadline text if present
            dl = None
            for term in ["tonight", "tomorrow", "next friday", "next monday", "this week", "by friday at 5 pm", "by friday", "friday at 5 pm", "friday", "monday", "by 5pm", "soon", "later", "today", "thursday"]:
                if term in msg_lower:
                    dl = term
                    break

            # Case 1: Send quotation / proposal
            if "quotation" in msg_lower or "quote" in msg_lower or "proposal" in msg_lower:
                obj = "quotation" if ("quotation" in msg_lower or "quote" in msg_lower) else ("revised proposal" if "revised" in msg_lower else "proposal")
                action = "Send"
                commitments.append({
                    "person": person,
                    "action": action,
                    "object": obj,
                    "description": msg if "if " in msg_lower else f"{action} the {obj}",
                    "deadline_raw": dl or "tonight",
                    "source": "conversation",
                    "source_excerpt": line,
                    "expected_evidence": [
                        f"{obj} document",
                        "sent message/email",
                        "timestamp",
                    ],
                    "confidence": 0.94,
                    "status": "pending",
                })
            # Case 2: Update pricing sheet / thing
            elif "pricing" in msg_lower or "sheet" in msg_lower:
                obj = "pricing sheet" if "sheet" in msg_lower else ("pricing thing" if "thing" in msg_lower else "pricing updates")
                action = "Take care" if "take care" in msg_lower else "Update"
                commitments.append({
                    "person": person,
                    "action": action,
                    "object": obj,
                    "description": msg if "if " in msg_lower else f"{action} the {obj}",
                    "deadline_raw": dl or "tomorrow",
                    "source": "conversation",
                    "source_excerpt": line,
                    "expected_evidence": [
                        "updated pricing sheet / CSV",
                        "delivery cost updates",
                        "version change log",
                    ],
                    "confidence": 0.92,
                    "status": "pending",
                })
            # Case 3: Conditional or generic commitment
            else:
                action = "Complete"
                obj = "deliverable"
                for act in ["send", "submit", "prepare", "deliver", "review", "call", "schedule", "share", "upload", "complete"]:
                    if act in msg_lower:
                        action = act.capitalize()
                        break

                if "final files" in msg_lower or "files" in msg_lower:
                    obj = "final files"
                elif "report" in msg_lower:
                    obj = "report"
                elif "investor deck" in msg_lower or "deck" in msg_lower:
                    obj = "investor deck"
                elif "meeting" in msg_lower:
                    obj = "meeting"
                elif "document" in msg_lower:
                    obj = "document"
                elif "payment" in msg_lower:
                    obj = "payment"
                elif "assignment" in msg_lower:
                    obj = "assignment"
                elif "database migration" in msg_lower or "migration" in msg_lower:
                    obj = "database migration & deployment"

                commitments.append({
                    "person": person,
                    "action": action,
                    "object": obj,
                    "description": msg,
                    "deadline_raw": dl,
                    "source": "conversation",
                    "source_excerpt": line,
                    "expected_evidence": [
                        f"{action} confirmation",
                        "deliverable artifact",
                        "completion timestamp",
                    ],
                    "confidence": 0.85,
                    "status": "pending",
                })

        return commitments

    def _plan_evidence(self, commitment_desc: str, context: Dict[str, Any]) -> List[str]:
        """Plans observable verification requirements for a commitment."""
        obj = context.get("object", "").lower()
        act = context.get("action", "").lower()

        if "quotation" in obj or "quote" in obj:
            return ["quotation document", "sent message/email", "delivery timestamp"]
        elif "proposal" in obj:
            return ["uploaded proposal / document", "sent message/email", "document shared with recipient", "delivery timestamp"]
        elif "pricing" in obj or "sheet" in obj:
            return ["updated pricing sheet / CSV", "delivery cost updates", "version change log"]
        elif "report" in obj:
            return ["report document (PDF/Word)", "dispatch receipt", "submission timestamp"]
        elif "deck" in obj or "investor" in obj:
            return ["finalized investor deck", "sent email/receipt", "dispatch timestamp"]
        elif "migration" in obj or "deploy" in obj:
            return ["database migration log", "deployment status report", "release pipeline confirmation"]
        elif "payment" in obj:
            return ["payment receipt", "transaction confirmation", "gateway audit log"]
        elif "assignment" in obj:
            return ["assignment submission record", "portal receipt", "submission timestamp"]
        elif "meeting" in obj:
            return ["calendar invite", "meeting link", "participant confirmations"]
        elif "document" in obj:
            return ["uploaded document", "document link", "upload timestamp"]
        elif "code" in obj or "pr" in obj:
            return ["pull request link", "git commit hash", "review approval"]
        else:
            return [
                f"{act.capitalize()} deliverable or document",
                "confirmation of receipt or timestamp",
                "audit log or team communication",
            ]

    def _verify_commitment(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates retrieved evidence against commitment requirements."""
        commitment = context.get("commitment", {})
        evidence_items = context.get("evidence", [])
        obj = commitment.get("object", "").lower()
        desc = commitment.get("description", "").lower()
        person = commitment.get("person", "The committer")

        # Combine text of all retrieved evidence
        all_text = " ".join([e.get("content", "") + " " + e.get("file_name", "") for e in evidence_items]).lower()

        # Rule: Absence of evidence is UNVERIFIED, never failure
        if not evidence_items or not all_text.strip():
            return {
                "status": "unverified",
                "explanation": (
                    f"No evidence has been provided yet for {person}'s commitment: '{commitment.get('description')}'. "
                    "In accordance with PromiseOS verification principles, absence of evidence is not proof of failure."
                ),
                "evidence_summary": "No supporting or contradicting evidence uploaded.",
                "missing_items": commitment.get("expected_evidence", ["Deliverable artifact", "Timestamp"]),
                "contradictions": [],
                "confidence": 0.5,
            }

        # Check for contradictions: when BOTH positive delivery/sent AND negative/unreceived statements exist, or payment claims contradict failed/declined evidence
        has_positive_sent = (
            "sent friday" in all_text
            or "sent via" in all_text
            or "dispatched" in all_text
            or "delivered" in all_text
            or "report sent" in all_text
            or "proposal sent" in all_text
            or "deck was sent" in all_text
            or "sent before" in all_text
        )
        has_negative_claim = (
            "never received" in all_text
            or "didn't receive" in all_text
            or "did not receive" in all_text
            or "still waiting" in all_text
            or "not sent" in all_text
            or "failed/rejected" in all_text
        )
        has_payment_conflict = (
            ("payment" in obj or "payment" in desc)
            and ("failed" in all_text or "rejected" in all_text)
            and ("completed" in desc or "completed" in all_text or "paid" in desc)
        )
        has_conflict = (
            "contradiction" in all_text
            or "conflict" in all_text
            or (has_positive_sent and has_negative_claim and "completed but not sent" not in all_text and "not completed" not in all_text)
            or has_payment_conflict
        )
        if has_conflict:
            return {
                "status": "contradictory",
                "explanation": (
                    f"Conflicting evidence was detected regarding {person}'s commitment '{commitment.get('description')}'. "
                    "One record suggests completion while another record indicates failure, rejection, or non-delivery."
                ),
                "evidence_summary": "Available evidence sources present conflicting states of completion.",
                "missing_items": [],
                "contradictions": ["Conflicting delivery/status reported between records."],
                "confidence": 0.85,
            }

        # Check for unfulfilled indicator: affirmative evidence showing non-delivery or failure WITHOUT contradictory sent claims
        has_non_delivery = (
            ("still waiting" in all_text and not has_positive_sent)
            or ("not sent" in all_text and not ("completed but not sent" in all_text))
            or "missed" in all_text
            or "cancelled" in all_text
            or "failed to deliver" in all_text
            or "not submitted" in all_text
            or "was not submitted" in all_text
        )
        if has_non_delivery:
            return {
                "status": "unfulfilled",
                "explanation": (
                    f"Evidence indicates that {person}'s commitment '{commitment.get('description')}' was not completed "
                    "and the designated timeframe passed with affirmative confirmation of non-delivery."
                ),
                "evidence_summary": "Confirmation of non-delivery found in records.",
                "missing_items": ["Completed deliverable"],
                "contradictions": [],
                "confidence": 0.90,
            }

        # Check for partial fulfillment
        is_partial = (
            "not sent" in all_text
            or "tbd" in all_text
            or "pending" in all_text
            or "partial" in all_text
            or "draft" in all_text
            or "not completed" in all_text
            or "partially" in all_text
        )
        if is_partial:
            return {
                "status": "partial",
                "explanation": (
                    f"Commitment: '{commitment.get('description')}'. "
                    "Evidence demonstrates that initial steps or base requirements were completed, "
                    "but final dispatch or delivery terms remain pending/unresolved."
                ),
                "evidence_summary": "Deliverable prepared/updated, but final completion or delivery is pending.",
                "missing_items": ["Final dispatch / delivery confirmation"],
                "contradictions": [],
                "confidence": 0.88,
            }

        # Check for fulfilled
        return {
            "status": "fulfilled",
            "explanation": (
                f"Commitment: '{commitment.get('description')}'. "
                "Retrieved evidence confirms deliverable was produced and dispatched within promised timeframe. "
                "All observable fulfillment criteria have been verified."
            ),
            "evidence_summary": "Deliverable reference, terms, and delivery confirmation verified in evidence.",
            "missing_items": [],
            "contradictions": [],
            "confidence": 0.95,
        }

    def _generate_followup(self, input_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generates polite, non-accusatory follow-up message draft."""
        commitment = context.get("commitment", {})
        verification = context.get("verification", {})
        person = commitment.get("person", "Team")
        obj = commitment.get("object", "item")
        status = verification.get("status", "unverified")
        missing = verification.get("missing_items", [])

        if status == "fulfilled":
            draft = (
                f"Hi {person}, just confirming that we received the {obj} and everything looks complete. "
                "Thank you for following up on this!"
            )
        elif status == "partial":
            missing_str = ", ".join(missing) if missing else "the remaining items"
            draft = (
                f"Hi {person}, thanks for making progress on the {obj}. "
                f"It looks like {missing_str} might still be pending. "
                "Could you let us know when you might be able to share the updated details? Thanks!"
            )
        elif status == "contradictory":
            draft = (
                f"Hi {person}, we noticed differing updates regarding the {obj}. "
                "Could you help clarify the current status so we're aligned on next steps?"
            )
        elif status == "unfulfilled":
            draft = (
                f"Hi {person}, checking in regarding the {obj} from earlier. "
                "Let us know if you need any assistance or if we should adjust the timeline."
            )
        else:  # unverified / pending
            draft = (
                f"Hi {person}, friendly check-in on the {obj} that was discussed. "
                "Please share the deliverable or let us know if there are any updates when you have a moment."
            )

        return {
            "draft": draft,
            "tone": context.get("tone", "polite"),
            "approved": False,
        }
