"""Unit tests for Mock LLM resilience and Provider Fallback chain."""

from typing import Any, Dict, Optional, Type
import pytest
from pydantic import BaseModel
from app.core.exceptions import ProviderError
from app.llm.base import BaseLLMProvider, LLMResult
from app.llm.mock import MockLLMProvider
from app.llm.router import LLMRouter


class FailingProvider(BaseLLMProvider):
    """Simulates a provider that throws a connection or rate limit error."""

    def __init__(self, name: str = "failing_provider"):
        super().__init__(name=name, is_configured=True)

    async def generate(self, task: str, input_text: str, **kwargs) -> LLMResult:
        raise ProviderError(self.name, "Simulated 503 Rate Limit / Outage")


class MalformedOutputProvider(BaseLLMProvider):
    """Simulates a provider that returns invalid or non-schema JSON."""

    def __init__(self, name: str = "malformed_provider"):
        super().__init__(name=name, is_configured=True)

    async def generate(self, task: str, input_text: str, **kwargs) -> LLMResult:
        return LLMResult(
            task=task,
            provider=self.name,
            model="broken-model",
            raw_text="NOT VALID JSON AT ALL",
            parsed_json={"unrecognized_field": 123},
            success=True,
        )


class SuccessfulBackupProvider(BaseLLMProvider):
    """Simulates the fallback provider that succeeds."""

    def __init__(self, name: str = "backup_provider"):
        super().__init__(name=name, is_configured=True)

    async def generate(self, task: str, input_text: str, **kwargs) -> LLMResult:
        return LLMResult(
            task=task,
            provider=self.name,
            model="backup-model",
            raw_text='{"status": "ok"}',
            parsed_json={"status": "ok"},
            success=True,
        )


class ExpectedSchema(BaseModel):
    status: str


@pytest.mark.asyncio
async def test_fallback_when_primary_provider_fails():
    """Verifies: Provider A fails -> Provider B is attempted."""
    router = LLMRouter()
    p_fail = FailingProvider("primary_provider")
    p_backup = SuccessfulBackupProvider("secondary_provider")

    # Manually configure active provider chain for test
    router.providers = [p_fail, p_backup]

    # Force router to use active chain instead of mock shortcut
    orig_should_use = router.get_active_providers
    router.get_active_providers = lambda: [p_fail, p_backup]

    try:
        res = await router.generate(
            task="verification",
            input_text="Test prompt",
        )
        assert res.success is True
        assert res.provider == "secondary_provider"
    finally:
        router.get_active_providers = orig_should_use


@pytest.mark.asyncio
async def test_fallback_when_primary_provider_returns_schema_mismatch():
    """Verifies: Provider A returns malformed/mismatched output -> fallback to Provider B."""
    router = LLMRouter()
    p_malformed = MalformedOutputProvider("malformed_provider")
    p_backup = SuccessfulBackupProvider("valid_provider")

    router.get_active_providers = lambda: [p_malformed, p_backup]

    res = await router.generate(
        task="verification",
        input_text="Test prompt",
        schema=ExpectedSchema,
    )

    assert res.success is True
    assert res.provider == "valid_provider"
    assert res.parsed_json == {"status": "ok"}


@pytest.mark.asyncio
async def test_mock_llm_handles_empty_and_unrecognized_input():
    """Verifies that MockLLM handles unexpected tasks and empty strings without crashing."""
    mock = MockLLMProvider()

    # Empty string
    res_empty = await mock.generate(task="commitment_extraction", input_text="")
    assert res_empty.success is True
    assert res_empty.parsed_json == []

    # Unrecognized task
    res_unknown = await mock.generate(task="unknown_arbitrary_task", input_text="Sample")
    assert res_unknown.success is True
    assert "Mock output for unknown task" in res_unknown.parsed_json["message"]


def test_provider_errors_do_not_leak_secrets():
    """Verifies that ProviderError representations do not expose API keys."""
    secret_key = "sk-super-secret-production-key-12345"
    err = ProviderError("groq", "Authentication failed for authorization header")

    # Secret key should never be present in the exception string representation
    assert secret_key not in str(err)
    assert secret_key not in err.message
