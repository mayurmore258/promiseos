"""End-to-End Test for the complete PromiseOS workflow."""

from pathlib import Path
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_promiseos_e2e_flow(client: AsyncClient):
    """Executes the entire PromiseOS end-to-end lifecycle locally without external API keys.

    Workflow:
    1. Load sample conversation
    2. POST /api/analyze
    3. Verify extracted & persisted commitments (Quotation & Pricing Sheet)
    4. Verify planned evidence requirements
    5. Upload sample evidence files (quotation.txt and pricing.csv)
    6. Search and retrieve candidate evidence
    7. Verify Commitment 1 (Quotation -> Fulfilled)
    8. Verify Commitment 2 (Pricing Sheet -> Partial)
    9. Retrieve updated commitment details
    10. Generate follow-up draft for partial commitment
    11. Human approves follow-up draft
    12. Verify final database state
    """
    # 1. Load sample conversation
    samples_dir = Path(__file__).parent.parent / "data" / "samples"
    conv_file = samples_dir / "sample_conversation.txt"
    assert conv_file.exists(), f"Sample conversation file missing: {conv_file}"
    conversation_text = conv_file.read_text(encoding="utf-8")

    # 2. POST /api/analyze
    analyze_res = await client.post("/api/analyze", json={"text": conversation_text, "source": "conversation"})
    assert analyze_res.status_code == 201
    analyze_data = analyze_res.json()

    # 3. Verify extracted commitments
    assert analyze_data["total_commitments"] == 2
    commitments = analyze_data["commitments"]

    c1_quotation = next(c for c in commitments if "quotation" in c["object"].lower())
    c2_pricing = next(c for c in commitments if "pricing" in c["object"].lower())

    assert c1_quotation["person"] == "Rahul"
    assert c1_quotation["action"] == "Send"
    assert c1_quotation["deadline_raw"] == "tonight"
    assert len(c1_quotation["expected_evidence"]) > 0

    assert c2_pricing["person"] == "Rahul"
    assert c2_pricing["action"] == "Update"
    assert c2_pricing["deadline_raw"] == "tomorrow"
    assert len(c2_pricing["expected_evidence"]) > 0

    # 4. Upload sample evidence for Commitment 1 (quotation.txt)
    test_ev_dir = Path(__file__).parent.parent / "data" / "test_evidence"
    quote_bytes = (test_ev_dir / "quotation.txt").read_bytes()

    up1_res = await client.post(
        "/api/evidence/upload",
        files={"file": ("quotation.txt", quote_bytes, "text/plain")},
        data={"commitment_id": c1_quotation["id"]},
    )
    assert up1_res.status_code == 201
    assert up1_res.json()["file_name"] == "quotation.txt"

    # 5. Upload sample evidence for Commitment 2 (pricing.csv)
    pricing_bytes = (test_ev_dir / "pricing.csv").read_bytes()
    up2_res = await client.post(
        "/api/evidence/upload",
        files={"file": ("pricing.csv", pricing_bytes, "text/csv")},
        data={"commitment_id": c2_pricing["id"]},
    )
    assert up2_res.status_code == 201
    assert up2_res.json()["file_name"] == "pricing.csv"

    # 6. Search evidence for Commitment 1
    search_res = await client.post(
        "/api/evidence/search",
        json={"commitment_id": c1_quotation["id"], "top_k": 5},
    )
    assert search_res.status_code == 200
    assert search_res.json()["total_found"] >= 1

    # 7. Run Verification on Commitment 1 (Expect FULFILLED)
    v1_res = await client.post(f"/api/verify/{c1_quotation['id']}")
    assert v1_res.status_code == 200
    v1_data = v1_res.json()
    assert v1_data["status"] == "fulfilled"
    assert v1_data["confidence"] >= 0.85
    assert len(v1_data["evidence"]) >= 1

    # 8. Run Verification on Commitment 2 (Expect PARTIAL)
    v2_res = await client.post(f"/api/verify/{c2_pricing['id']}")
    assert v2_res.status_code == 200
    v2_data = v2_res.json()
    assert v2_data["status"] == "partial"
    assert len(v2_data["missing_items"]) >= 1

    # 9. Retrieve Commitment 1 details to verify final state
    detail1 = await client.get(f"/api/commitments/{c1_quotation['id']}")
    assert detail1.status_code == 200
    assert detail1.json()["status"] == "fulfilled"
    assert len(detail1.json()["evidence"]) >= 1
    assert detail1.json()["verification"]["status"] == "fulfilled"

    # 10. Generate Follow-up Draft for Commitment 2
    followup_res = await client.post(f"/api/followup/{c2_pricing['id']}", json={"tone": "polite"})
    assert followup_res.status_code == 201
    followup_data = followup_res.json()
    f_id = followup_data["id"]
    assert followup_data["approved"] is False
    assert "Rahul" in followup_data["draft"]

    # 11. Human Approves Follow-up Draft
    approve_res = await client.post(
        f"/api/followup/{f_id}/approve",
        json={
            "approved": True,
            "edited_draft": "Hi Rahul, thank you for updating base prices. Could you let us know when the delivery charges will be ready?",
        },
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["approved"] is True
    assert approve_res.json()["approved_at"] is not None

    # 12. Retrieve Commitment 2 details to verify full final state
    detail2 = await client.get(f"/api/commitments/{c2_pricing['id']}")
    assert detail2.status_code == 200
    assert detail2.json()["status"] == "partial"
    assert detail2.json()["verification"]["status"] == "partial"
    assert detail2.json()["followup"]["approved"] is True
