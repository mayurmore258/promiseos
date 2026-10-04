"""Comprehensive API Endpoint Tests for PromiseOS."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_and_ready_endpoints(client: AsyncClient):
    # GET /api/health
    res_health = await client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    # GET /api/ready
    res_ready = await client.get("/api/ready")
    assert res_ready.status_code == 200
    data = res_ready.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["storage"] == "ready"


@pytest.mark.asyncio
async def test_analyze_empty_input(client: AsyncClient):
    res = await client.post("/api/analyze", json={"text": "   "})
    assert res.status_code == 422
    err = res.json()
    assert "error" in err
    assert err["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_analyze_valid_conversation_multiple_commitments(client: AsyncClient):
    payload = {
        "text": "Rahul: I'll send the quotation tonight.\nRahul: I'll also update the pricing sheet tomorrow.\nMayur: Okay.",
        "source": "conversation",
    }
    res = await client.post("/api/analyze", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["total_commitments"] == 2
    assert len(data["commitments"]) == 2

    # Check first commitment
    c1 = data["commitments"][0]
    assert c1["person"] == "Rahul"
    assert c1["action"] == "Send"
    assert c1["object"] == "quotation"
    assert c1["deadline_raw"] == "tonight"
    assert c1["status"] == "pending"
    assert len(c1["expected_evidence"]) > 0

    # Check second commitment
    c2 = data["commitments"][1]
    assert c2["person"] == "Rahul"
    assert c2["action"] == "Update"
    assert c2["object"] == "pricing sheet"
    assert c2["deadline_raw"] == "tomorrow"


@pytest.mark.asyncio
async def test_commitments_crud_and_human_review(client: AsyncClient):
    # 1. Analyze to create commitment
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the quotation tonight."})
    assert res.status_code == 201
    com_id = res.json()["commitments"][0]["id"]

    # 2. GET /api/commitments
    list_res = await client.get("/api/commitments?person=Rahul")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # 3. GET /api/commitments/{id}
    detail_res = await client.get(f"/api/commitments/{com_id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == com_id

    # 4. PATCH /api/commitments/{id}
    patch_res = await client.patch(
        f"/api/commitments/{com_id}",
        json={"object": "revised proposal", "deadline_raw": "next Friday"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["object"] == "revised proposal"
    assert patch_res.json()["deadline_raw"] == "next Friday"

    # 5. POST /api/commitments/{id}/review (Human Review)
    review_res = await client.post(
        f"/api/commitments/{com_id}/review",
        json={"status": "fulfilled", "notes": "Confirmed directly with client."},
    )
    assert review_res.status_code == 200
    assert review_res.json()["status"] == "fulfilled"


@pytest.mark.asyncio
async def test_commitment_not_found(client: AsyncClient):
    res = await client.get("/api/commitments/00000000-0000-0000-0000-000000009999")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "COMMITMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_evidence_upload_valid_empty_and_duplicate(client: AsyncClient):
    # Create commitment
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the quotation tonight."})
    com_id = res.json()["commitments"][0]["id"]

    # 1. Valid upload
    file_content = b"Official Quotation Document #Q-2026-901 for Mayur."
    files = {"file": ("quotation.txt", file_content, "text/plain")}
    data = {"commitment_id": com_id}

    up_res = await client.post("/api/evidence/upload", files=files, data=data)
    assert up_res.status_code == 201
    up_data = up_res.json()
    assert up_data["file_name"] == "quotation.txt"
    assert up_data["is_duplicate"] is False
    assert up_data["chunk_count"] >= 1

    # 2. Duplicate upload
    files_dup = {"file": ("quotation.txt", file_content, "text/plain")}
    dup_res = await client.post("/api/evidence/upload", files=files_dup, data=data)
    assert dup_res.status_code == 201
    assert dup_res.json()["is_duplicate"] is True
    assert dup_res.json()["id"] == up_data["id"]

    # 3. Empty file upload
    empty_files = {"file": ("empty.txt", b"", "text/plain")}
    empty_res = await client.post("/api/evidence/upload", files=empty_files, data=data)
    assert empty_res.status_code == 400
    assert empty_res.json()["error"]["code"] == "MALFORMED_FILE"

    # 4. Unsupported file type
    unsupp_files = {"file": ("hack.py", b"print('hack')", "text/x-python")}
    unsupp_res = await client.post("/api/evidence/upload", files=unsupp_files, data=data)
    assert unsupp_res.status_code == 400
    assert unsupp_res.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


@pytest.mark.asyncio
async def test_evidence_search(client: AsyncClient):
    # Create commitment & upload evidence
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the quotation tonight."})
    com_id = res.json()["commitments"][0]["id"]

    file_content = b"Quotation #Q-2026-901 sent to Mayur via email at 20:45 IST."
    await client.post(
        "/api/evidence/upload",
        files={"file": ("quotation.txt", file_content, "text/plain")},
        data={"commitment_id": com_id},
    )

    # Search evidence
    search_res = await client.post(
        "/api/evidence/search",
        json={"commitment_id": com_id, "top_k": 3},
    )
    assert search_res.status_code == 200
    s_data = search_res.json()
    assert s_data["commitment_id"] == com_id
    assert s_data["total_found"] >= 1
    assert s_data["candidates"][0]["relevance_score"] > 0.0


@pytest.mark.asyncio
async def test_verify_commitment_and_human_review(client: AsyncClient):
    # Create commitment & upload quotation evidence
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the quotation tonight."})
    com_id = res.json()["commitments"][0]["id"]

    file_content = b"Official Quotation Ref #Q-2026-901 sent via email tonight by Rahul."
    await client.post(
        "/api/evidence/upload",
        files={"file": ("quotation.txt", file_content, "text/plain")},
        data={"commitment_id": com_id},
    )

    # Run verification
    verify_res = await client.post(f"/api/verify/{com_id}")
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["status"] == "fulfilled"
    assert "quotation" in v_data["explanation"].lower()
    assert v_data["confidence"] >= 0.8

    # Verify commitment status updated in DB
    com_detail = await client.get(f"/api/commitments/{com_id}")
    assert com_detail.json()["status"] == "fulfilled"

    # Human review / override verification
    review_ver_res = await client.post(
        f"/api/verify/{com_id}/review",
        json={"status": "partial", "notes": "Requires client sign-off before marking fulfilled."},
    )
    assert review_ver_res.status_code == 200
    assert review_ver_res.json()["status"] == "partial"


@pytest.mark.asyncio
async def test_verify_no_evidence_safely_unverified(client: AsyncClient):
    # Absence of evidence must NEVER mark commitment as failure
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll prepare the marketing deck."})
    com_id = res.json()["commitments"][0]["id"]

    verify_res = await client.post(f"/api/verify/{com_id}")
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "unverified"


@pytest.mark.asyncio
async def test_followup_generate_and_approve(client: AsyncClient):
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll also update the pricing sheet tomorrow."})
    com_id = res.json()["commitments"][0]["id"]

    # 1. Generate follow-up
    f_res = await client.post(f"/api/followup/{com_id}", json={"tone": "polite"})
    assert f_res.status_code == 201
    f_data = f_res.json()
    followup_id = f_data["id"]
    assert f_data["approved"] is False
    assert len(f_data["draft"]) > 10

    # 2. Human approve follow-up
    app_res = await client.post(
        f"/api/followup/{followup_id}/approve",
        json={"approved": True, "edited_draft": "Hi Rahul, checking in on the pricing sheet."},
    )
    assert app_res.status_code == 200
    assert app_res.json()["approved"] is True
    assert app_res.json()["draft"] == "Hi Rahul, checking in on the pricing sheet."
