"""Unit tests for commitment discovery, extraction, ambiguous dates, and conditional context."""

import pytest
from app.agents.commitment_agent import commitment_agent
from app.agents.evidence_planner import evidence_planner
from app.utils.dates import parse_deadline


@pytest.mark.asyncio
async def test_single_commitment_extraction():
    """Scenario: 'I'll send Rahul the revised proposal by Friday.'"""
    text = "I'll send Rahul the revised proposal by Friday."
    commitments = await commitment_agent.extract_commitments(text)

    assert len(commitments) == 1
    c = commitments[0]
    assert c.person == "Rahul"
    assert c.action.lower() == "send"
    assert "proposal" in c.object.lower()
    assert c.deadline_raw is not None
    assert "friday" in c.deadline_raw.lower()


@pytest.mark.asyncio
async def test_multiple_commitments_not_collapsed():
    """Scenario: 'I'll send the proposal to Rahul tomorrow and I'll update the pricing sheet by Friday.'

    Must extract 2 distinct commitments without collapsing them.
    """
    text = "I'll send the proposal to Rahul tomorrow and I'll update the pricing sheet by Friday."
    commitments = await commitment_agent.extract_commitments(text)

    assert len(commitments) == 2, f"Expected 2 commitments, got {len(commitments)}"

    c1 = commitments[0]
    c2 = commitments[1]

    assert "proposal" in c1.object.lower()
    assert c1.deadline_raw == "tomorrow"

    assert "pricing" in c2.object.lower()
    assert "friday" in c2.deadline_raw.lower()


@pytest.mark.asyncio
async def test_non_commitment_text_not_extracted():
    """Scenario: 'We discussed the proposal yesterday.'

    Must NOT produce any commitment.
    """
    text = "We discussed the proposal yesterday."
    commitments = await commitment_agent.extract_commitments(text)

    assert len(commitments) == 0, f"Expected 0 commitments from non-promissory text, got {len(commitments)}"


@pytest.mark.asyncio
async def test_ambiguous_commitment_does_not_fabricate_dates():
    """Scenario: 'I'll take care of the pricing thing soon.'

    Action extracted, object preserved, deadline_raw='soon', normalized deadline=None.
    """
    text = "I'll take care of the pricing thing soon."
    commitments = await commitment_agent.extract_commitments(text)

    assert len(commitments) == 1
    c = commitments[0]
    assert c.action in ("Take care", "Update", "Complete")
    assert "pricing" in c.object.lower()
    assert c.deadline_raw == "soon"
    # Mandatory rule: Do NOT invent a normalized date for ambiguous input
    assert c.deadline is None


@pytest.mark.asyncio
async def test_conditional_commitment_preserves_condition():
    """Scenario: 'If the client approves the design, I'll send the final files.'"""
    text = "If the client approves the design, I'll send the final files."
    commitments = await commitment_agent.extract_commitments(text)

    assert len(commitments) == 1
    c = commitments[0]
    assert "send" in c.action.lower()
    assert "files" in c.object.lower()
    # Verify that conditional context is preserved
    assert "if the client approves" in c.description.lower() or "if the client approves" in c.source_excerpt.lower()


@pytest.mark.asyncio
async def test_evidence_planning_is_specific_and_observable():
    """Verifies that evidence requirements are observable facts rather than generic phrases."""
    c_dict = {
        "id": "111",
        "person": "Rahul",
        "action": "Send",
        "object": "proposal",
        "description": "Send Rahul the proposal",
        "deadline_raw": "Friday",
    }
    requirements = await evidence_planner.plan_evidence(c_dict)

    assert len(requirements) >= 2
    for req in requirements:
        assert len(req.strip()) > 3
        # Must not simply say generic "check if promise was fulfilled"
        assert "check if promise was fulfilled" not in req.lower()
        # Should refer to concrete artifacts or actions
        assert any(term in req.lower() for term in ["proposal", "document", "message", "email", "timestamp", "receipt"])


def test_changed_deadline_handling():
    """Scenario: Send Friday -> Actually Monday."""
    raw1, dt1 = parse_deadline("Friday")
    raw2, dt2 = parse_deadline("Monday")

    assert raw1 == "Friday"
    assert raw2 == "Monday"
    assert dt1 is not None and dt2 is not None
    # Both resolve distinctly without collision
    assert dt1 != dt2
