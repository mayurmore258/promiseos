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

        # 1. Normalize typographic/smart punctuation (curly quotes, smart apostrophes, en/em dashes)
        normalized_text = (
            text.replace("\u2019", "'")
            .replace("\u2018", "'")
            .replace("\u201c", '"')
            .replace("\u201d", '"')
            .replace("\u2013", "-")
            .replace("\u2014", "-")
        )

        raw_lines = []
        for line in normalized_text.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            speaker_prefix = ""
            content = line_str
            if ":" in line_str:
                parts = line_str.split(":", 1)
                # Find the speaker immediately preceding the colon
                speaker_match = re.search(r"([A-Za-z0-9_\s]{1,30})$", parts[0].strip())
                if speaker_match and not any(kw in parts[0].lower() for kw in ["http", "https"]):
                    cand = speaker_match.group(1).strip()
                    # If cand has sentence punctuation, take the final segment
                    cand_clean = re.split(r"[.!?]\s*", cand)[-1].strip()
                    if cand_clean and len(cand_clean.split()) <= 3:
                        speaker_prefix = cand_clean + ": "
                        content = parts[1].strip()

            # Split sentences within this turn
            sentences = re.split(
                r"(?<=[.!?])\s+(?=(?:i'll|i\s+will|we'll|we\s+will|then\s+i'll|then\s+i\s+will|[A-Za-z]+:)\b)",
                content,
                flags=re.IGNORECASE,
            )
            for s in sentences:
                s_str = s.strip()
                if not s_str:
                    continue
                # Split compound clauses on " and I'll " etc.
                sub_clauses = re.split(r"\s+and\s+(?=(?:i'll|i\s+will|we'll|we\s+will)\b)", s_str, flags=re.IGNORECASE)
                for sc in sub_clauses:
                    sc_str = sc.strip()
                    if sc_str:
                        if speaker_prefix and not sc_str.startswith(speaker_prefix) and ":" not in sc_str:
                            raw_lines.append(f"{speaker_prefix}{sc_str}")
                        else:
                            raw_lines.append(sc_str)

        for line in raw_lines:
            line_lower = line.lower()
            speaker = "Unknown"
            msg = line
            if ":" in line:
                parts = line.split(":", 1)
                speaker = parts[0].strip()
                msg = parts[1].strip()
            msg_lower = msg.lower()

            # Skip questions (e.g. "Have you completed the DBMS assignment?")
            if msg_lower.endswith("?") or msg_lower.startswith(("have you ", "did you ", "can you ", "could you ", "will you ")):
                continue

            # Strip leading conversational fillers / acknowledgments from message for cleaner extraction
            clean_msg = re.sub(
                r"^(?:okay|ok|perfect|sure|thanks|got it|fine|great|not yet|yes)[,.]?\s*",
                "",
                msg,
                flags=re.IGNORECASE,
            ).strip()
            clean_lower = clean_msg.lower()

            # Skip pure acknowledgments and non-commitment filler
            if clean_lower in ("", "okay.", "ok", "sure", "thanks", "got it", "fine.", "perfect.", "not yet.", "not yet", "yes.", "yes"):
                continue

            # Check for commitment markers
            commitment_markers = [
                "i'll", "i will", "promise to", "promise i'll", "promise i will",
                "we will", "we'll", "will send", "will update",
                "will complete", "will submit", "will deliver", "then i'll", "then i will",
                "i completed", "completed the payment", "i have completed", "completed payment"
            ]
            if not any(pat in clean_lower or pat in msg_lower for pat in commitment_markers):
                continue

            # Identify committer person or target entity
            person = speaker if speaker != "Unknown" else "Rahul"
            if speaker == "Unknown":
                if "rahul" in msg_lower:
                    person = "Rahul"
                elif "mayur" in msg_lower:
                    person = "Mayur"
                elif "priya" in msg_lower:
                    person = "Priya"
                elif "neha" in msg_lower:
                    person = "Neha"

            # Extract deadline text if present (match longer specific terms first)
            dl = None
            deadline_terms = [
                "by friday at 5 pm", "friday at 5 pm", "by friday at 5pm", "friday at 5pm",
                "by 5 pm", "by 5pm", "at 5 pm", "at 5pm",
                "tomorrow morning", "tomorrow afternoon", "tomorrow evening", "tomorrow night",
                "this morning", "this afternoon", "this evening",
                "next friday", "next monday", "next week", "this week",
                "tonight", "tomorrow", "today",
                "by friday", "friday", "monday", "thursday",
                "soon", "later"
            ]
            for term in deadline_terms:
                if term in clean_lower or term in msg_lower:
                    dl = term
                    break

            # Extract action and object
            # Case 1: Send quotation / proposal
            if "quotation" in clean_lower or "quote" in clean_lower or "proposal" in clean_lower:
                obj = "quotation" if ("quotation" in clean_lower or "quote" in clean_lower) else ("revised proposal" if "revised" in clean_lower else "proposal")
                action = "Send"
                commitments.append({
                    "person": person,
                    "action": action,
                    "object": obj,
                    "description": clean_msg if "if " in clean_lower else f"{action} the {obj}",
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
            elif "pricing" in clean_lower or ("sheet" in clean_lower and "pricing" in clean_lower):
                obj = "pricing sheet" if "sheet" in clean_lower else ("pricing thing" if "thing" in clean_lower else "pricing updates")
                action = "Take care" if "take care" in clean_lower else "Update"
                commitments.append({
                    "person": person,
                    "action": action,
                    "object": obj,
                    "description": clean_msg if "if " in clean_lower else f"{action} the {obj}",
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
            # Case 3: Questions / Assignment / General deliverables
            else:
                action = "Complete"
                obj = "deliverable"
                for act in ["combine", "submit", "prepare", "deliver", "review", "call", "schedule", "share", "upload", "complete", "send"]:
                    if act in clean_lower:
                        action = act.capitalize()
                        break

                if "question" in clean_lower:
                    m = re.search(r"questions?\s*[\d\w–-]+", clean_lower)
                    obj = m.group(0) if m else "questions"
                elif "assignment" in clean_lower:
                    obj = "assignment"
                elif "final files" in clean_lower or "files" in clean_lower:
                    obj = "final files"
                elif "report" in clean_lower:
                    obj = "report"
                elif "investor deck" in clean_lower or "deck" in clean_lower:
                    obj = "investor deck"
                elif "meeting" in clean_lower:
                    obj = "meeting"
                elif "document" in clean_lower:
                    obj = "document"
                elif "payment" in clean_lower:
                    obj = "payment"
                elif "database migration" in clean_lower or "migration" in clean_lower:
                    obj = "database migration & deployment"

                # Clean description of leading "then " if present
                desc_text = re.sub(r"^then\s+", "", clean_msg, flags=re.IGNORECASE)

                commitments.append({
                    "person": person,
                    "action": action,
                    "object": obj,
                    "description": desc_text,
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
