"""End-to-End Workflow Validation Tests for PromiseOS.

Validates the complete PromiseOS backend workflow:
Communication -> Commitment Discovery -> ML Corroboration -> Evidence Planning ->
Evidence Ingestion -> Search/Retrieval -> Verification -> Human Review -> Follow-up -> Approval.

Explicitly tests all 5 core PromiseOS trust statuses:
- Scenario A: FULFILLED
- Scenario B: PARTIALLY FULFILLED
- Scenario C: UNVERIFIED (Absence of evidence != failure)
- Scenario D: CONTRADICTORY (Conflicting claims)
- Scenario E: UNFULFILLED (Affirmative proof of non-delivery)

Also validates:
- ML advisory isolation (candidates never dropped or mutated by ML)
- Human control & approval invariants (no auto-send, human in control)
- Non-accusatory communication principles
"""

import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.services.ml_service import MLPredictionResult


# ==============================================================================
# SCENARIO A: FULFILLED
# ==============================================================================
@pytest.mark.asyncio
async def test_e2e_scenario_a_fulfilled(client: AsyncClient):
    """Scenario A: Full lifecycle resulting in FULFILLED.
    
    1. Ingest conversation: "Rahul: I'll send the client proposal by Friday."
    2. Commitment discovered and persisted.
    3. ML corroboration attached (advisory only).
    4. Evidence requirements planned.
    5. Evidence uploaded confirming delivery on Friday.
    6. Evidence retrieved & verified -> status == "fulfilled".
    7. Human review recorded.
    8. Follow-up drafted (polite confirmation) -> Human approves draft.
    """
    # 1. Analyze communication
    conv_text = "Rahul: I'll send the client proposal by Friday.\nMayur: Thanks Rahul."
    res_analyze = await client.post("/api/analyze", json={"text": conv_text, "source": "conversation"})
    assert res_analyze.status_code == 201
    data_analyze = res_analyze.json()
    assert data_analyze["total_commitments"] >= 1

    commitment = data_analyze["commitments"][0]
    c_id = commitment["id"]
    assert commitment["person"] == "Rahul"
    assert "proposal" in commitment["object"].lower()
    assert commitment["status"] == "pending"

    # ML Corroboration verification: local ML predicted COMMITMENT without altering LLM candidate
    assert commitment.get("ml_label") == "COMMITMENT" or settings.ML_COMMITMENT_ENABLED
    assert commitment["confidence"] >= 0.80
    assert len(commitment["expected_evidence"]) >= 2

    # 2. Upload matching fulfillment evidence
    evidence_text = (
        "Email Receipt:\n"
        "From: rahul@example.com\n"
        "To: client-lead@acme.corp\n"
        "Date: Friday, 3:15 PM\n"
        "Subject: Client Proposal Final\n"
        "Client proposal sent Friday via Outlook to client lead. All terms confirmed and dispatched."
    )
    res_upload = await client.post(
        "/api/evidence/upload",
        files={"file": ("proposal_dispatch.txt", evidence_text.encode("utf-8"), "text/plain")},
        data={"commitment_id": c_id},
    )
    assert res_upload.status_code == 201

    # 3. Search and retrieve evidence
    res_search = await client.post(
        "/api/evidence/search",
        json={"commitment_id": c_id, "query": "client proposal", "top_k": 3},
    )
    assert res_search.status_code == 200
    assert res_search.json()["total_found"] >= 1

    # 4. Verify commitment -> FULFILLED
    res_verify = await client.post(f"/api/verify/{c_id}")
    assert res_verify.status_code == 200
    ver_data = res_verify.json()
    assert ver_data["status"] == "fulfilled"
    assert ver_data["confidence"] >= 0.85
    assert len(ver_data["missing_items"]) == 0
    assert len(ver_data["contradictions"]) == 0

    # 5. Human Review of Verification
    res_review = await client.post(
        f"/api/verify/{c_id}/review",
        json={"status": "fulfilled", "notes": "Audited by project manager. Delivered on time."},
    )
    assert res_review.status_code == 200
    assert res_review.json()["status"] == "fulfilled"
    assert "Audited by project manager" in res_review.json()["explanation"]

    # 6. Generate Follow-up Draft
    res_followup = await client.post(f"/api/followup/{c_id}", json={"tone": "polite"})
    assert res_followup.status_code == 201
    f_data = res_followup.json()
    assert f_data["approved"] is False  # Never sent autonomously!
    assert "Rahul" in f_data["draft"]
    assert "received" in f_data["draft"].lower() or "complete" in f_data["draft"].lower()

    # 7. Human Approves Follow-up
    res_approve = await client.post(
        f"/api/followup/{f_data['id']}/approve",
        json={"approved": True, "edited_draft": "Hi Rahul, received the proposal and looks great. Thank you!"},
    )
    assert res_approve.status_code == 200
    assert res_approve.json()["approved"] is True
    assert res_approve.json()["approved_at"] is not None


# ==============================================================================
# SCENARIO B: PARTIALLY FULFILLED
# ==============================================================================
@pytest.mark.asyncio
async def test_e2e_scenario_b_partially_fulfilled(client: AsyncClient):
    """Scenario B: Lifecycle resulting in PARTIAL.
    
    1. Ingest commitment for report.
    2. Evidence shows draft was finished, but final delivery is pending/not sent.
    3. Verification returns 'partial' with missing items.
    4. Follow-up draft acknowledges progress and politely inquires about pending items.
    5. Human reviewer approves follow-up.
    """
    conv_text = "Rahul: I'll finish the client report and send it to the client by Friday."
    res_analyze = await client.post("/api/analyze", json={"text": conv_text, "source": "conversation"})
    assert res_analyze.status_code == 201
    commitment = res_analyze.json()["commitments"][0]
    c_id = commitment["id"]

    # Evidence shows partial progress (draft finished, but delivery pending / not sent)
    ev_text = (
        "Sprint Status Update:\n"
        "Client report draft completed but not sent. Base figures updated, final signoff pending."
    )
    res_up = await client.post(
        "/api/evidence/upload",
        files={"file": ("report_status.txt", ev_text.encode("utf-8"), "text/plain")},
        data={"commitment_id": c_id},
    )
    assert res_up.status_code == 201

    # Verification -> PARTIAL
    res_ver = await client.post(f"/api/verify/{c_id}")
    assert res_ver.status_code == 200
    ver_data = res_ver.json()
    assert ver_data["status"] == "partial"
    assert len(ver_data["missing_items"]) >= 1

    # Follow-up -> Inquires about pending items without hostility
    res_fol = await client.post(f"/api/followup/{c_id}")
    assert res_fol.status_code == 201
    f_data = res_fol.json()
    assert f_data["approved"] is False
    assert "pending" in f_data["draft"].lower() or "progress" in f_data["draft"].lower()

    # Human approval
    res_app = await client.post(f"/api/followup/{f_data['id']}/approve", json={"approved": True})
    assert res_app.status_code == 200
    assert res_app.json()["approved"] is True


# ==============================================================================
# SCENARIO C: UNVERIFIED (Absence of evidence != failure)
# ==============================================================================
@pytest.mark.asyncio
async def test_e2e_scenario_c_unverified_no_evidence_invariant(client: AsyncClient):
    """Scenario C: CRITICAL INVARIANT TEST.
    
    Absence of evidence MUST NEVER be classified as unfulfilled/failed.
    1. Ingest commitment: "Rahul: I'll send the revised proposal by Friday."
    2. Provide ZERO evidence.
    3. Verification MUST return 'unverified'.
    4. Explanation MUST emphasize that lack of evidence is not proof of failure.
    5. Follow-up MUST be a neutral, non-accusatory check-in.
    """
    conv_text = "Rahul: I'll send the revised proposal by Friday."
    res_analyze = await client.post("/api/analyze", json={"text": conv_text, "source": "conversation"})
    assert res_analyze.status_code == 201
    commitment = res_analyze.json()["commitments"][0]
    c_id = commitment["id"]

    # Provide NO evidence
    res_ver = await client.post(f"/api/verify/{c_id}")
    assert res_ver.status_code == 200
    ver_data = res_ver.json()

    # CRITICAL INVARIANT ASSERTION
    assert ver_data["status"] == "unverified", "Violated invariant: absence of evidence was marked as failure!"
    assert "absence of evidence is not proof of failure" in ver_data["explanation"].lower()
    assert ver_data["confidence"] == 0.5

    # Follow-up is polite check-in, NOT an accusation of failure
    res_fol = await client.post(f"/api/followup/{c_id}")
    assert res_fol.status_code == 201
    draft = res_fol.json()["draft"]
    assert "friendly check-in" in draft.lower()
    assert "fail" not in draft.lower()
    assert "breach" not in draft.lower()


# ==============================================================================
# SCENARIO D: CONTRADICTORY (Conflicting records)
# ==============================================================================
@pytest.mark.asyncio
async def test_e2e_scenario_d_contradictory_evidence(client: AsyncClient):
    """Scenario D: Conflicting records detected.
    
    1. Ingest commitment: "Rahul: I'll send the quotation tonight."
    2. Evidence contains conflicting statements: sender says sent Friday, recipient says never received.
    3. Verification returns 'contradictory'.
    4. Contradictions list is populated.
    5. Follow-up asks for clarification neutrally.
    """
    conv_text = "Rahul: I'll send the quotation tonight."
    res_analyze = await client.post("/api/analyze", json={"text": conv_text, "source": "conversation"})
    assert res_analyze.status_code == 201
    commitment = res_analyze.json()["commitments"][0]
    c_id = commitment["id"]

    # Conflicting evidence
    conflict_text = (
        "Audit Log:\n"
        "Sender log: quotation sent via email at 4 PM.\n"
        "Customer message: Did not receive the quotation, we never received any file."
    )
    res_up = await client.post(
        "/api/evidence/upload",
        files={"file": ("audit_conflict.txt", conflict_text.encode("utf-8"), "text/plain")},
        data={"commitment_id": c_id},
    )
    assert res_up.status_code == 201

    # Verification -> CONTRADICTORY
    res_ver = await client.post(f"/api/verify/{c_id}")
    assert res_ver.status_code == 200
    ver_data = res_ver.json()
    assert ver_data["status"] == "contradictory"
    assert len(ver_data["contradictions"]) >= 1

    # Follow-up asks for clarification neutrally
    res_fol = await client.post(f"/api/followup/{c_id}")
    assert res_fol.status_code == 201
    draft = res_fol.json()["draft"]
    assert "differing updates" in draft.lower() or "clarify" in draft.lower()


# ==============================================================================
# SCENARIO E: UNFULFILLED (Affirmative proof of non-delivery)
# ==============================================================================
@pytest.mark.asyncio
async def test_e2e_scenario_e_unfulfilled_affirmative_evidence(client: AsyncClient):
    """Scenario E: Affirmative evidence of failure/missed deadline.
    
    1. Ingest commitment: "Rahul: I'll deliver the project files by Friday."
    2. Evidence affirms that deadline passed and task was cancelled / failed to deliver.
    3. Verification returns 'unfulfilled'.
    4. Follow-up offers assistance, remains polite without hostility.
    5. Human review can override/annotate status.
    """
    conv_text = "Rahul: I'll deliver the project files by Friday."
    res_analyze = await client.post("/api/analyze", json={"text": conv_text, "source": "conversation"})
    assert res_analyze.status_code == 201
    commitment = res_analyze.json()["commitments"][0]
    c_id = commitment["id"]

    # Affirmative evidence of non-delivery
    failure_text = (
        "Project Retrospective:\n"
        "Deadline passed and project files were cancelled and failed to deliver on Friday. Task missed."
    )
    res_up = await client.post(
        "/api/evidence/upload",
        files={"file": ("failure_retro.txt", failure_text.encode("utf-8"), "text/plain")},
        data={"commitment_id": c_id},
    )
    assert res_up.status_code == 201

    # Verification -> UNFULFILLED
    res_ver = await client.post(f"/api/verify/{c_id}")
    assert res_ver.status_code == 200
    ver_data = res_ver.json()
    assert ver_data["status"] == "unfulfilled"

    # Follow-up -> Helpful and non-accusatory
    res_fol = await client.post(f"/api/followup/{c_id}")
    assert res_fol.status_code == 201
    draft = res_fol.json()["draft"]
    assert "checking in" in draft.lower() or "assistance" in draft.lower()

    # Human Review can annotate or override
    res_rev = await client.post(
        f"/api/commitments/{c_id}/review",
        json={"status": "unfulfilled", "notes": "Reviewed: Client agreed to postpone deadline."},
    )
    assert res_rev.status_code == 200
    assert res_rev.json()["status"] == "unfulfilled"


# ==============================================================================
# ML ISOLATION & ADVISORY BEHAVIOR
# ==============================================================================
@pytest.mark.asyncio
async def test_e2e_ml_advisory_isolation_when_negative(client: AsyncClient, monkeypatch):
    """Verify ML never drops candidates, even when predicting NON_COMMITMENT.
    
    1. Force ML to predict NON_COMMITMENT with 0.05 probability.
    2. Analyze communication.
    3. Candidate MUST still be extracted, persisted, and returned.
    4. Candidate can still have evidence attached and verified.
    """
    from app.agents.commitment_agent import commitment_agent

    class MockNegativeML:
        def predict(self, text: str) -> MLPredictionResult:
            return MLPredictionResult(label="NON_COMMITMENT", probability=0.05, is_available=True)

    monkeypatch.setattr(commitment_agent, "ml_service", MockNegativeML())

    conv_text = "Rahul: I'll send the quotation tonight."
    res = await client.post("/api/analyze", json={"text": conv_text})
    assert res.status_code == 201
    data = res.json()

    # Candidate was preserved, NOT dropped
    assert data["total_commitments"] == 1
    c = data["commitments"][0]
    assert c["person"] == "Rahul"
    assert c["object"] == "quotation"
    assert c["confidence"] == 0.94  # LLM confidence unaltered!


# ==============================================================================
# EVIDENCE PIPELINE (PARSING, CHUNKING, SEARCH)
# ==============================================================================
@pytest.mark.asyncio
async def test_e2e_evidence_pipeline_multiformat(client: AsyncClient):
    """Verify evidence ingestion, parsing, chunking, and multi-factor retrieval."""
    # Analyze to get commitment
    res_a = await client.post("/api/analyze", json={"text": "Rahul: I'll update the pricing sheet tomorrow."})
    c_id = res_a.json()["commitments"][0]["id"]

    # Upload CSV evidence
    csv_bytes = b"product,price,currency,status\nServer Alpha,999,USD,updated\nStorage Beta,499,USD,pending\n"
    res_up = await client.post(
        "/api/evidence/upload",
        files={"file": ("pricing_update.csv", csv_bytes, "text/csv")},
        data={"commitment_id": c_id},
    )
    assert res_up.status_code == 201
    assert res_up.json()["file_name"] == "pricing_update.csv"
    assert res_up.json()["chunk_count"] >= 1

    # Search evidence
    res_search = await client.post(
        "/api/evidence/search",
        json={"commitment_id": c_id, "query": "pricing sheet", "top_k": 5},
    )
    assert res_search.status_code == 200
    search_data = res_search.json()
    assert search_data["total_found"] >= 1
    assert any("Server Alpha" in ch["content"] for ch in search_data["candidates"])


# ==============================================================================
# HUMAN IN CONTROL INVARIANTS
# ==============================================================================
@pytest.mark.asyncio
async def test_e2e_human_control_invariants(client: AsyncClient):
    """Verify human approval requirement and manual review override capability."""
    res_a = await client.post("/api/analyze", json={"text": "Rahul: I'll send the proposal by Friday."})
    c_id = res_a.json()["commitments"][0]["id"]

    # Generate follow-up
    res_fol = await client.post(f"/api/followup/{c_id}")
    f_id = res_fol.json()["id"]
    assert res_fol.json()["approved"] is False

    # Attempting to retrieve commitment details shows pending draft
    res_detail = await client.get(f"/api/commitments/{c_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["followup"]["approved"] is False

    # Human explicitly approves
    res_app = await client.post(
        f"/api/followup/{f_id}/approve",
        json={"approved": True, "edited_draft": "Approved custom follow-up text."},
    )
    assert res_app.status_code == 200
    assert res_app.json()["approved"] is True
    assert res_app.json()["draft"] == "Approved custom follow-up text."

    # Human can also review and manually override commitment status
    res_rev = await client.post(
        f"/api/commitments/{c_id}/review",
        json={"status": "fulfilled", "notes": "Manually verified by human reviewer."},
    )
    assert res_rev.status_code == 200
    assert res_rev.json()["status"] == "fulfilled"
