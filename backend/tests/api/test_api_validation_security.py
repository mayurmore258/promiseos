"""Comprehensive API Validation, Security, and Concurrency/Repeatability Tests."""

import io
import pytest
from httpx import AsyncClient
from app.core.config import settings


# ---------------------------------------------------------------------------
# API Validation Tests (Section 19)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api_validation_wrong_data_types(client: AsyncClient):
    """Wrong data types passed to analyze endpoint."""
    res = await client.post("/api/analyze", json={"text": 12345})
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_api_validation_invalid_status_enum(client: AsyncClient):
    """Invalid status enum value passed to commitment update."""
    res = await client.patch(
        "/api/commitments/11111111-1111-1111-1111-111111111111",
        json={"status": "not_a_valid_status"},
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_api_validation_invalid_query_parameters(client: AsyncClient):
    """Limit parameter violating ge/le constraints."""
    res = await client.get("/api/commitments?limit=-10")
    assert res.status_code == 422

    res_too_large = await client.get("/api/commitments?limit=1000")
    assert res_too_large.status_code == 422


@pytest.mark.asyncio
async def test_api_validation_malformed_json_body(client: AsyncClient):
    """Invalid JSON payload."""
    res = await client.post(
        "/api/analyze",
        content="This is not valid json{",
        headers={"Content-Type": "application/json"},
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_api_validation_missing_required_fields(client: AsyncClient):
    """Search evidence missing commitment_id field."""
    res = await client.post("/api/evidence/search", json={})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# Security Tests (Section 10 & 20)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_security_path_traversal_in_filename(client: AsyncClient):
    """Malicious filename attempting path traversal (e.g., ../../evil.txt)."""
    # Create commitment first
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the quotation tonight."})
    com_id = res.json()["commitments"][0]["id"]

    malicious_filename = "../../evil.txt"
    files = {"file": (malicious_filename, b"malicious content trying to escape directory", "text/plain")}
    data = {"commitment_id": com_id}

    up_res = await client.post("/api/evidence/upload", files=files, data=data)
    # The file service must sanitize the filename to "evil.txt" and safely persist strictly inside upload_dir
    assert up_res.status_code == 201
    assert up_res.json()["file_name"] == "evil.txt"
    assert ".." not in up_res.json()["file_name"]
    assert "/" not in up_res.json()["file_name"]


@pytest.mark.asyncio
async def test_security_oversized_file_upload(client: AsyncClient):
    """File exceeding MAX_UPLOAD_SIZE_MB."""
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the quotation tonight."})
    com_id = res.json()["commitments"][0]["id"]

    # Temporarily set max upload size to 1KB for test
    orig_mb = settings.MAX_UPLOAD_SIZE_MB
    settings.MAX_UPLOAD_SIZE_MB = 1  # 1MB
    try:
        # Create bytes larger than 1MB
        oversized_bytes = b"0" * (1024 * 1024 + 500)
        files = {"file": ("oversized.txt", oversized_bytes, "text/plain")}
        up_res = await client.post("/api/evidence/upload", files=files, data={"commitment_id": com_id})
        assert up_res.status_code == 413
        assert up_res.json()["error"]["code"] == "FILE_SIZE_EXCEEDED"
    finally:
        settings.MAX_UPLOAD_SIZE_MB = orig_mb


@pytest.mark.asyncio
async def test_security_unsupported_mime_types(client: AsyncClient):
    """Disallowed executable or script extensions."""
    for bad_name in ["hack.sh", "virus.exe", "macro.bin", "exploit.bat"]:
        files = {"file": (bad_name, b"echo exploit", "application/octet-stream")}
        up_res = await client.post("/api/evidence/upload", files=files)
        assert up_res.status_code == 400
        assert up_res.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


@pytest.mark.asyncio
async def test_security_exception_leakage_masking(client: AsyncClient):
    """Verifies that 404/500 responses do not leak database passwords, file paths, or stack traces."""
    res = await client.get("/api/commitments/00000000-0000-0000-0000-000000009999")
    assert res.status_code == 404
    data = res.json()

    # Response should have clean error schema
    assert "error" in data
    assert "code" in data["error"]
    assert "Traceback" not in str(data)
    assert "password" not in str(data).lower()
    assert "aiosqlite" not in str(data).lower()


# ---------------------------------------------------------------------------
# Concurrency / Repeatability Tests (Section 21)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_repeatability_repeated_analysis(client: AsyncClient):
    """Running analyze multiple times on the same input must be stable and consistent."""
    text = "Rahul: I'll send the quotation tonight."
    for _ in range(3):
        res = await client.post("/api/analyze", json={"text": text})
        assert res.status_code == 201
        assert res.json()["total_commitments"] == 1


@pytest.mark.asyncio
async def test_repeatability_repeated_verification(client: AsyncClient):
    """Verifying the same commitment multiple times does not corrupt state."""
    res = await client.post("/api/analyze", json={"text": "Rahul: I'll send the quotation tonight."})
    com_id = res.json()["commitments"][0]["id"]

    for _ in range(3):
        v_res = await client.post(f"/api/verify/{com_id}")
        assert v_res.status_code == 200
        assert v_res.json()["status"] == "unverified"
