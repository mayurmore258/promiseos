"""Demo Readiness and Backend Integration Validation Test Suite for PromiseOS.

Comprehensive test coverage for:
- Phase 2: API Contract Validation
- Phase 3: Scenarios A through F (Fulfilled, Partial, Unverified, Contradictory, Unfulfilled, Multi)
- Phase 4: Database Persistence across requests/sessions
- Phase 5: Complete E2E Workflow
- Phase 6: ML V2 Calibrated Model Verification
- Phase 7: Human Control and Trust Safety Invariants (1 through 10)
- Phase 9: Error Handling and Boundary Conditions
- Phase 11: Health and Readiness Endpoints
"""

import os
import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.services.ml_service import ml_commitment_service, MLPredictionResult


# ==============================================================================
# PHASE 3: REALISTIC PROMISEOS DEMO SCENARIOS (A - F)
# ==============================================================================

@pytest.mark.asyncio
async def test_scenario_a_fulfilled_investor_deck(client: AsyncClient):
    """SCENARIO A — FULFILLED.
    
    Conversation: "Rahul: I'll send the finalized investor deck by Friday at 5 PM."
    Evidence: Document showing finalized investor deck was sent before deadline.
    Expected: FULFILLED.
    """
    # 1. Analyze
    conv = "Rahul: I'll send the finalized investor deck by Friday at 5 PM."
    res = await client.post("/api/analyze", json={"text": conv, "source": "conversation"})
    assert res.status_code == 201
    c = res.json()["commitments"][0]
    c_id = c["id"]
    assert c["person"] == "Rahul"
    assert "deck" in c["object"].lower() or "deliverable" in c["object"].lower()
    assert c["status"] == "pending"

    # 2. Upload fulfillment evidence
    ev_content = (
        "Email Transmission Receipt:\n"
        "From: rahul@acmecorp.com\n"
        "To: investors@capital.vc\n"
        "Date: Friday 4:30 PM (before 5:00 PM deadline)\n"
        "Subject: Finalized Investor Deck Q4\n"
        "The finalized investor deck was sent before the 5 PM deadline via Outlook."
    )
    up = await client.post(
        "/api/evidence/upload",
        files={"file": ("investor_deck_receipt.txt", ev_content.encode("utf-8"), "text/plain")},
        data={"commitment_id": c_id},
    )
    assert up.status_code == 201

    # 3. Verify
    ver = await client.post(f"/api/verify/{c_id}")
    assert ver.status_code == 200
    ver_data = ver.json()
    assert ver_data["status"] == "fulfilled"
    assert ver_data["confidence"] >= 0.85
    assert len(ver_data["missing_items"]) == 0
    assert len(ver_data["contradictions"]) == 0

    # 4. Generate follow-up & approve
    fol = await client.post(f"/api/followup/{c_id}")
    assert fol.status_code == 201
    assert fol.json()["approved"] is False

    app = await client.post(f"/api/followup/{fol.json()['id']}/approve", json={"approved": True})
    assert app.status_code == 200
    assert app.json()["approved"] is True


@pytest.mark.asyncio
async def test_scenario_b_partially_fulfilled_migration(client: AsyncClient):
    """SCENARIO B — PARTIALLY FULFILLED.
    
    Conversation: "Rahul: I'll complete the database migration and deploy the backend by Monday."
    Evidence: Database migration completed. Deployment not completed.
    Expected: PARTIALLY_FULFILLED.
    """
    conv = "Rahul: I'll complete the database migration and deploy the backend by Monday."
    res = await client.post("/api/analyze", json={"text": conv, "source": "conversation"})
    assert res.status_code == 201
    c_id = res.json()["commitments"][0]["id"]

    ev_content = (
        "DevOps Status Log - Monday:\n"
        "Database migration completed successfully.\n"
        "Deployment not completed; staging cluster rollout pending approval."
    )
    up = await client.post(
        "/api/evidence/upload",
        files={"file": ("devops_status.txt", ev_content.encode("utf-8"), "text/plain")},
        data={"commitment_id": c_id},
    )
    assert up.status_code == 201

    ver = await client.post(f"/api/verify/{c_id}")
    assert ver.status_code == 200
    ver_data = ver.json()
    assert ver_data["status"] == "partial"
    assert len(ver_data["missing_items"]) >= 1

    fol = await client.post(f"/api/followup/{c_id}")
    assert fol.status_code == 201
    assert "pending" in fol.json()["draft"].lower() or "progress" in fol.json()["draft"].lower()


@pytest.mark.asyncio
async def test_scenario_c_unverified_absence_of_evidence(client: AsyncClient):
    """SCENARIO C — UNVERIFIED.
    
    Conversation: "Rahul: I'll send the client proposal tomorrow."
    No evidence available.
    Expected: UNVERIFIED.
    IMPORTANT: Must NOT mark this UNFULFILLED merely because evidence is missing.
    """
    conv = "Rahul: I'll send the client proposal tomorrow."
    res = await client.post("/api/analyze", json={"text": conv, "source": "conversation"})
    assert res.status_code == 201
    c_id = res.json()["commitments"][0]["id"]

    # No evidence uploaded!
    ver = await client.post(f"/api/verify/{c_id}")
    assert ver.status_code == 200
    ver_data = ver.json()

    # TRUST INVARIANT ASSERTION
    assert ver_data["status"] == "unverified"
    assert ver_data["status"] != "unfulfilled"
    assert "absence of evidence is not proof of failure" in ver_data["explanation"].lower()
    assert ver_data["confidence"] == 0.5


@pytest.mark.asyncio
async def test_scenario_d_contradictory_payment(client: AsyncClient):
    """SCENARIO D — CONTRADICTORY.
    
    Conversation: "Rahul: I completed the payment."
    Evidence indicates: Payment failed/rejected.
    Expected: CONTRADICTORY.
    """
    conv = "Rahul: I completed the payment."
    res = await client.post("/api/analyze", json={"text": conv, "source": "conversation"})
    assert res.status_code == 201
    c_id = res.json()["commitments"][0]["id"]

    ev_content = (
        "Stripe Gateway Audit Report:\n"
        "Transaction ID: tx_98726354\n"
        "Payment status: failed/rejected. Card declined due to authentication timeout."
    )
    up = await client.post(
        "/api/evidence/upload",
        files={"file": ("payment_log.txt", ev_content.encode("utf-8"), "text/plain")},
        data={"commitment_id": c_id},
    )
    assert up.status_code == 201

    ver = await client.post(f"/api/verify/{c_id}")
    assert ver.status_code == 200
    ver_data = ver.json()
    assert ver_data["status"] == "contradictory"
    assert len(ver_data["contradictions"]) >= 1

    fol = await client.post(f"/api/followup/{c_id}")
    assert fol.status_code == 201
    assert "clarify" in fol.json()["draft"].lower() or "differing updates" in fol.json()["draft"].lower()


@pytest.mark.asyncio
async def test_scenario_e_unfulfilled_missed_assignment(client: AsyncClient):
    """SCENARIO E — UNFULFILLED.
    
    Conversation: "Rahul: I'll submit the assignment by Friday."
    Evidence/status clearly indicates it was not submitted by the deadline.
    Expected: UNFULFILLED.
    """
    conv = "Rahul: I'll submit the assignment by Friday."
    res = await client.post("/api/analyze", json={"text": conv, "source": "conversation"})
    assert res.status_code == 201
    c_id = res.json()["commitments"][0]["id"]

    ev_content = (
        "LMS Course Audit Log:\n"
        "Course: CS501\n"
        "Student: Rahul\n"
        "Portal Record: Assignment was not submitted by the deadline on Friday. Submission window closed."
    )
    up = await client.post(
        "/api/evidence/upload",
        files={"file": ("lms_audit.txt", ev_content.encode("utf-8"), "text/plain")},
        data={"commitment_id": c_id},
    )
    assert up.status_code == 201

    ver = await client.post(f"/api/verify/{c_id}")
    assert ver.status_code == 200
    ver_data = ver.json()
    assert ver_data["status"] == "unfulfilled"
    assert "not completed" in ver_data["explanation"].lower() or "non-delivery" in ver_data["explanation"].lower()

    fol = await client.post(f"/api/followup/{c_id}")
    assert fol.status_code == 201
    assert "assistance" in fol.json()["draft"].lower() or "checking in" in fol.json()["draft"].lower()


@pytest.mark.asyncio
async def test_scenario_f_multiple_commitments_isolation(client: AsyncClient):
    """SCENARIO F — MULTIPLE COMMITMENTS.
    
    One conversation containing multiple commitments:
    - send proposal
    - schedule meeting
    - upload document
    - complete payment
    Verify that commitments remain separate and correctly linked to evidence.
    """
    conv = (
        "Rahul: I'll send the proposal tomorrow.\n"
        "Rahul: I'll schedule the meeting for Thursday.\n"
        "Rahul: I'll upload the document by Friday.\n"
        "Rahul: I'll complete the payment today."
    )
    res = await client.post("/api/analyze", json={"text": conv, "source": "conversation"})
    assert res.status_code == 201
    data = res.json()
    assert data["total_commitments"] == 4
    commitments = data["commitments"]

    # Verify each commitment is distinct
    c_ids = [c["id"] for c in commitments]
    assert len(set(c_ids)) == 4, "Commitments must have unique IDs"

    # Verify independent objects
    objects = [c["object"].lower() for c in commitments]
    assert any("proposal" in o for o in objects)
    assert any("meeting" in o for o in objects)
    assert any("document" in o for o in objects)
    assert any("payment" in o for o in objects)

    # Attach evidence only to the 'proposal' commitment
    prop_com = [c for c in commitments if "proposal" in c["object"].lower()][0]
    ev_proposal = "Sent client proposal to partner via email."
    up = await client.post(
        "/api/evidence/upload",
        files={"file": ("proposal_dispatch.txt", ev_proposal.encode("utf-8"), "text/plain")},
        data={"commitment_id": prop_com["id"]},
    )
    assert up.status_code == 201

    # Verify that searching for 'meeting' does not return proposal evidence
    meet_com = [c for c in commitments if "meeting" in c["object"].lower()][0]
    ver_meet = await client.post(f"/api/verify/{meet_com['id']}")
    assert ver_meet.status_code == 200
    assert ver_meet.json()["status"] == "unverified", "Evidence must not bleed into unrelated commitments!"


# ==============================================================================
# PHASE 4: DATABASE PERSISTENCE VALIDATION
# ==============================================================================

@pytest.mark.asyncio
async def test_database_persistence_across_requests(client: AsyncClient):
    """Verify that records persist across separate API calls, queries, and updates."""
    # 1. Create commitment via analyze
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the investor deck by Friday."})
    assert res.status_code == 201
    c_id = res.json()["commitments"][0]["id"]

    # 2. Re-fetch via GET /api/commitments/{id}
    get1 = await client.get(f"/api/commitments/{c_id}")
    assert get1.status_code == 200
    assert get1.json()["id"] == c_id

    # 3. Patch commitment
    patch_res = await client.patch(
        f"/api/commitments/{c_id}",
        json={"object": "updated investor deck", "deadline_raw": "Monday 10 AM"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["object"] == "updated investor deck"

    # 4. Verify patch persisted in subsequent GET
    get2 = await client.get(f"/api/commitments/{c_id}")
    assert get2.status_code == 200
    assert get2.json()["object"] == "updated investor deck"
    assert get2.json()["deadline_raw"] == "Monday 10 AM"

    # 5. Upload evidence
    ev_up = await client.post(
        "/api/evidence/upload",
        files={"file": ("deck.txt", b"Final deck sent.", "text/plain")},
        data={"commitment_id": c_id},
    )
    assert ev_up.status_code == 201
    ev_id = ev_up.json()["id"]

    # 6. Verify evidence is linked in commitment detail
    get3 = await client.get(f"/api/commitments/{c_id}")
    assert get3.status_code == 200
    assert len(get3.json()["evidence"]) >= 1
    assert any(e["id"] == ev_id for e in get3.json()["evidence"])

    # 7. Human review persists
    rev_res = await client.post(
        f"/api/commitments/{c_id}/review",
        json={"status": "partial", "notes": "Waiting on legal review."},
    )
    assert rev_res.status_code == 200
    assert rev_res.json()["status"] == "partial"

    get4 = await client.get(f"/api/commitments/{c_id}")
    assert get4.json()["status"] == "partial"


# ==============================================================================
# PHASE 6: ML V2 CALIBRATED MODEL VALIDATION
# ==============================================================================

def test_ml_v2_model_loading_and_advisory_contract():
    """Verify that the production ML service correctly uses the calibrated V2 model."""
    assert os.path.exists(settings.ML_MODEL_PATH), f"Model path does not exist: {settings.ML_MODEL_PATH}"
    assert "v2_calibrated" in settings.ML_MODEL_PATH.lower()

    # Load model
    model = ml_commitment_service.get_model()
    assert model is not None

    # Test COMMITMENT prediction
    p_com = ml_commitment_service.predict("I will deliver the quarterly financial report by next Friday at 5pm.")
    assert isinstance(p_com, MLPredictionResult)
    assert p_com.label == "COMMITMENT"
    assert p_com.probability is not None
    assert 0.0 <= p_com.probability <= 1.0
    assert p_com.is_available is True

    # Test NON_COMMITMENT prediction
    p_non = ml_commitment_service.predict("The weather in San Francisco was lovely yesterday afternoon.")
    assert isinstance(p_non, MLPredictionResult)
    assert p_non.label == "NON_COMMITMENT"
    assert p_non.probability is not None
    assert p_non.is_available is True

    # Test edge cases: empty string and None
    p_empty = ml_commitment_service.predict("")
    assert p_empty.label == "NON_COMMITMENT"
    assert p_empty.probability == 0.0

    p_none = ml_commitment_service.predict(None)
    assert p_none.label == "NON_COMMITMENT"
    assert p_none.probability == 0.0


# ==============================================================================
# PHASE 7: TRUST AND HUMAN SAFETY INVARIANTS
# ==============================================================================

@pytest.mark.asyncio
async def test_trust_invariants_human_approval_gate(client: AsyncClient):
    """Verify that follow-up drafts CANNOT be approved without explicit human action."""
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the finalized deck tomorrow."})
    c_id = res.json()["commitments"][0]["id"]

    # Generate follow-up
    fol = await client.post(f"/api/followup/{c_id}")
    assert fol.status_code == 201
    f_data = fol.json()
    f_id = f_data["id"]

    # Invariant: Must start unapproved
    assert f_data["approved"] is False

    # Check detail endpoint reflects unapproved state
    detail = await client.get(f"/api/commitments/{c_id}")
    assert detail.json()["followup"]["approved"] is False

    # Explicit human approval
    app = await client.post(
        f"/api/followup/{f_id}/approve",
        json={"approved": True, "edited_draft": "Custom human-approved message."},
    )
    assert app.status_code == 200
    assert app.json()["approved"] is True
    assert app.json()["draft"] == "Custom human-approved message."


def test_trust_invariants_ml_scope_and_isolation():
    """Verify Invariants 8 & 9: ML cannot determine fulfillment or accuse anyone of lying."""
    # Invariant 8: ML label scope is strictly linguistic commitment classification
    allowed_labels = {"COMMITMENT", "NON_COMMITMENT", "UNKNOWN", "DISABLED"}
    res1 = ml_commitment_service.predict("I promise to deliver the report tomorrow.")
    assert res1.label in allowed_labels
    assert res1.label not in {"FULFILLED", "UNFULFILLED", "PARTIAL", "LIAR", "DISHONEST"}

    res2 = ml_commitment_service.predict("I failed to deliver the file yesterday.")
    assert res2.label in allowed_labels
    assert res2.label not in {"FULFILLED", "UNFULFILLED", "LIAR"}

    # Invariant 9: ML outputs probability only; it cannot assign trustworthiness or lie score
    assert hasattr(res1, "probability")
    assert not hasattr(res1, "trustworthiness")
    assert not hasattr(res1, "lie_score")


@pytest.mark.asyncio
async def test_trust_invariant_missing_evidence_never_failure(client: AsyncClient):
    """Verify Invariant 10: Absence of evidence MUST NEVER become failure/unfulfilled."""
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll complete the audit report by Friday."})
    c_id = res.json()["commitments"][0]["id"]

    # Verify without evidence
    ver = await client.post(f"/api/verify/{c_id}")
    assert ver.status_code == 200
    data = ver.json()
    assert data["status"] == "unverified"
    assert data["status"] != "unfulfilled"
    assert "absence of evidence is not proof of failure" in data["explanation"].lower()


# ==============================================================================
# PHASE 9: ERROR HANDLING AND BOUNDARY CONDITIONS
# ==============================================================================

@pytest.mark.asyncio
async def test_error_handling_invalid_uuid(client: AsyncClient):
    """Invalid UUID format returns 422 or 404 rather than 500 stack trace."""
    res = await client.get("/api/commitments/invalid-uuid-format")
    assert res.status_code in (404, 422)


@pytest.mark.asyncio
async def test_error_handling_nonexistent_commitment(client: AsyncClient):
    """Nonexistent UUID returns 404 with structured error response."""
    res = await client.get("/api/commitments/11111111-1111-1111-1111-111111111111")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "COMMITMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_error_handling_missing_required_analyze_fields(client: AsyncClient):
    """Missing required 'text' field in analyze payload returns 422."""
    res = await client.post("/api/analyze", json={})
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_error_handling_empty_upload(client: AsyncClient):
    """Empty file upload returns 400 with MALFORMED_FILE code."""
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the proposal."})
    c_id = res.json()["commitments"][0]["id"]

    up = await client.post(
        "/api/evidence/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
        data={"commitment_id": c_id},
    )
    assert up.status_code == 400
    assert up.json()["error"]["code"] == "MALFORMED_FILE"


# ==============================================================================
# PHASE 11: HEALTH AND READINESS CHECKS
# ==============================================================================

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    res = await client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_readiness_endpoint(client: AsyncClient):
    res = await client.get("/api/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["storage"] == "ready"
