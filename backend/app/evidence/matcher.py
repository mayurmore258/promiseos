"""Semantic and Multi-factor Matcher for Evidence Evaluation."""

import re
from typing import Any, Dict, List, Tuple
from app.utils.text import compute_jaccard_similarity, tokenize


class EvidenceMatcher:
    """Evaluates relevance between a commitment and an evidence text segment.

    Scores across:
    - Entity & Name matching (e.g., person name)
    - Action and Object semantic alignment
    - Expected evidence criteria matching
    - Lexical token overlap
    """

    def score(
        self,
        chunk_text: str,
        commitment: Dict[str, Any],
        file_name: str = "",
    ) -> Tuple[float, List[str]]:
        reasons: List[str] = []
        score = 0.0
        text_lower = (chunk_text + " " + file_name).lower()
        chunk_tokens = set(tokenize(text_lower))

        # 1. Action & Object matching (Weight: 0.35)
        obj = str(commitment.get("object", "")).lower()
        act = str(commitment.get("action", "")).lower()
        desc = str(commitment.get("description", "")).lower()

        obj_tokens = set(tokenize(obj))
        act_tokens = set(tokenize(act))

        if obj and (obj in text_lower or any(t in text_lower for t in obj_tokens)):
            score += 0.25
            reasons.append(f"Matched commitment deliverable/object '{obj}'")
        elif any(t in chunk_tokens for t in obj_tokens):
            score += 0.15
            reasons.append(f"Partial match for object tokens in '{obj}'")

        if act and (act in text_lower or any(t in text_lower for t in act_tokens)):
            score += 0.10
            reasons.append(f"Matched commitment action '{act}'")

        # 2. Entity / Person matching (Weight: 0.15)
        person = str(commitment.get("person", "")).lower()
        if person and person in text_lower:
            score += 0.15
            reasons.append(f"Matched committer entity '{person}'")

        # 3. Expected evidence items (Weight: 0.25)
        expected = commitment.get("expected_evidence", [])
        matched_expected = 0
        for exp in expected:
            exp_clean = str(exp).lower()
            exp_tokens = set(tokenize(exp_clean))
            if exp_clean in text_lower or len(exp_tokens.intersection(chunk_tokens)) >= 1:
                matched_expected += 1

        if expected and matched_expected > 0:
            exp_ratio = matched_expected / len(expected)
            score += 0.25 * exp_ratio
            reasons.append(f"Matched {matched_expected}/{len(expected)} planned evidence criteria")

        # 4. Token Overlap & Semantic Lexical (Weight: 0.20)
        jaccard = compute_jaccard_similarity(desc, chunk_text)
        score += min(0.20, jaccard * 0.4)

        # 5. Temporal / Deadline cues (Weight: 0.05)
        dl_raw = str(commitment.get("deadline_raw", "")).lower()
        if dl_raw and dl_raw in text_lower:
            score += 0.05
            reasons.append(f"Matched temporal cue '{dl_raw}'")

        # Clamp between 0.0 and 1.0
        final_score = min(1.0, max(0.0, score))
        return round(final_score, 3), reasons
