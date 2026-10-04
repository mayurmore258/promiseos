"""Unit tests for LLM Router, Mock Provider, and Provider Fallbacks."""

import pytest
from app.core.config import settings
from app.llm.groq_provider import GroqProvider
from app.llm.nvidia_provider import NvidiaProvider
from app.llm.sambanova_provider import SambaNovaProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.openrouter_provider import OpenRouterProvider
from app.llm.mock import MockLLMProvider
from app.llm.router import LLMRouter


@pytest.mark.asyncio
async def test_mock_llm_commitment_extraction():
    mock = MockLLMProvider()
    input_text = "Rahul: I'll send the quotation tonight.\nRahul: I'll also update the pricing sheet tomorrow.\nMayur: Okay."
    res = await mock.generate(task="commitment_extraction", input_text=input_text)
    assert res.success is True
    assert isinstance(res.parsed_json, list)
    assert len(res.parsed_json) == 2
    assert res.parsed_json[0]["person"] == "Rahul"
    assert res.parsed_json[0]["object"] == "quotation"


@pytest.mark.asyncio
async def test_mock_llm_evidence_planning():
    mock = MockLLMProvider()
    res = await mock.generate(
        task="evidence_planning",
        input_text="Send quotation tonight",
        context={"object": "quotation", "action": "Send"},
    )
    assert res.success is True
    assert isinstance(res.parsed_json, list)
    assert any("quotation" in item for item in res.parsed_json)


@pytest.mark.asyncio
async def test_mock_llm_verification_fulfilled():
    mock = MockLLMProvider()
    res = await mock.generate(
        task="verification",
        input_text="Check quotation",
        context={
            "commitment": {"person": "Rahul", "object": "quotation", "description": "Send quotation"},
            "evidence": [{"content": "Quotation Ref #Q-2026-901 sent via email at 20:45", "file_name": "quotation.txt"}],
        },
    )
    assert res.parsed_json["status"] == "fulfilled"
    assert res.parsed_json["confidence"] >= 0.9


@pytest.mark.asyncio
async def test_mock_llm_verification_partial():
    mock = MockLLMProvider()
    res = await mock.generate(
        task="verification",
        input_text="Check pricing sheet",
        context={
            "commitment": {"person": "Rahul", "object": "pricing sheet", "description": "Update pricing sheet"},
            "evidence": [{"content": "Product A updated, delivery cost TBD", "file_name": "pricing.csv"}],
        },
    )
    assert res.parsed_json["status"] == "partial"
    assert len(res.parsed_json["missing_items"]) > 0


@pytest.mark.asyncio
async def test_mock_llm_verification_unverified_on_empty():
    mock = MockLLMProvider()
    res = await mock.generate(
        task="verification",
        input_text="No evidence provided",
        context={
            "commitment": {"person": "Rahul", "object": "report", "description": "Send weekly report"},
            "evidence": [],
        },
    )
    # Safety invariant: empty evidence must NEVER equal failure
    assert res.parsed_json["status"] == "unverified"


@pytest.mark.asyncio
async def test_mock_llm_verification_contradictory():
    mock = MockLLMProvider()
    res = await mock.generate(
        task="verification",
        input_text="Conflicting records",
        context={
            "commitment": {"person": "Rahul", "object": "report", "description": "Send weekly report"},
            "evidence": [{"content": "Report sent Friday. However recipient is still waiting and report was not sent.", "file_name": "chat.txt"}],
        },
    )
    assert res.parsed_json["status"] == "contradictory"


@pytest.mark.asyncio
async def test_mock_llm_followup_generation():
    mock = MockLLMProvider()
    res = await mock.generate(
        task="followup_generation",
        input_text="Draft follow-up",
        context={
            "commitment": {"person": "Rahul", "object": "pricing sheet"},
            "verification": {"status": "partial", "missing_items": ["delivery cost"]},
        },
    )
    assert "draft" in res.parsed_json
    assert res.parsed_json["approved"] is False
    assert "Rahul" in res.parsed_json["draft"]


@pytest.mark.asyncio
async def test_router_fallback():
    router = LLMRouter()
    # In MOCK_LLM mode, router directly uses mock provider
    res = await router.generate(
        task="commitment_extraction",
        input_text="Rahul: I'll send the quotation tonight.",
    )
    assert res.success is True
    assert "mock" in res.provider


# ---------------------------------------------------------------------------
# External Provider Isolation Tests (Skipped when keys are absent)
# ---------------------------------------------------------------------------
def test_groq_provider_configuration():
    provider = GroqProvider()
    if not provider.is_configured:
        pytest.skip("GROQ_API_KEY is not configured in .env (expected during offline dev).")


def test_nvidia_provider_configuration():
    provider = NvidiaProvider()
    if not provider.is_configured:
        pytest.skip("NVIDIA_API_KEY is not configured in .env (expected during offline dev).")


def test_sambanova_provider_configuration():
    provider = SambaNovaProvider()
    if not provider.is_configured:
        pytest.skip("SAMBANOVA_API_KEY is not configured in .env (expected during offline dev).")


def test_gemini_provider_configuration():
    provider = GeminiProvider()
    if not provider.is_configured:
        pytest.skip("GEMINI_API_KEY is not configured in .env (expected during offline dev).")


def test_openrouter_provider_configuration():
    provider = OpenRouterProvider()
    if not provider.is_configured:
        pytest.skip("OPENROUTER_API_KEY is not configured in .env (expected during offline dev).")
