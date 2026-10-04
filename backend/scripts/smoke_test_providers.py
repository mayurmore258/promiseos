"""Smoke test utility for PromiseOS LLM providers.

Tests each configured real provider independently:
1. Groq
2. NVIDIA
3. SambaNova
4. OpenRouter

Requirements:
- Exactly one minimal test request per provider.
- Tiny harmless prompt.
- Short timeout (15s).
- Zero workflow / db / commitment overhead.
- No secrets / keys printed or logged.
- Compact formatted output.
"""

import asyncio
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.exceptions import ProviderError
from app.llm.base import BaseLLMProvider, LLMResult
from app.llm.groq_provider import GroqProvider
from app.llm.nvidia_provider import NvidiaProvider
from app.llm.sambanova_provider import SambaNovaProvider
from app.llm.openrouter_provider import OpenRouterProvider


def sanitize_text(text: Optional[str]) -> str:
    """Sanitize error messages and text to ensure no API keys or secrets leak."""
    if not text:
        return ""

    sanitized = str(text)

    # Collect all configured API keys/secrets from settings
    secret_keys = [
        getattr(settings, "GROQ_API_KEY", None),
        getattr(settings, "NVIDIA_API_KEY", None),
        getattr(settings, "SAMBANOVA_API_KEY", None),
        getattr(settings, "OPENROUTER_API_KEY", None),
        getattr(settings, "GEMINI_API_KEY", None),
        getattr(settings, "SUPABASE_KEY", None),
    ]

    for secret in secret_keys:
        if secret and len(secret.strip()) >= 4:
            clean_secret = secret.strip()
            if clean_secret in sanitized:
                sanitized = sanitized.replace(clean_secret, "[REDACTED]")

    # Redact Authorization / Bearer tokens and generic key query params
    sanitized = re.sub(r"Bearer\s+[A-Za-z0-9_\-\.]+", "Bearer [REDACTED]", sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(
        r'("?(?:api[_-]?key|authorization|token)"?\s*[:=]\s*"?[a-zA-Z0-9_\-\.]+)',
        r'"api_key": "[REDACTED]"',
        sanitized,
        flags=re.IGNORECASE,
    )

    return sanitized


def classify_error(err: Exception) -> str:
    """Classify provider failure into a concise, human-readable reason."""
    err_str = sanitize_text(str(err))
    err_lower = err_str.lower()

    if isinstance(err, asyncio.TimeoutError) or "timed out" in err_lower or "timeout" in err_lower:
        return "Request timed out"
    if "not configured" in err_lower or "missing key" in err_lower:
        return "Missing API key"
    if "401" in err_str or "unauthorized" in err_lower or "invalid_api_key" in err_lower or "authentication" in err_lower:
        return "Authentication failure"
    if "402" in err_str or "payment" in err_lower or "billing" in err_lower or "balance" in err_lower:
        return "Quota exhausted / payment required (HTTP 402)"
    if "403" in err_str or "forbidden" in err_lower:
        return "Access forbidden"
    if "410" in err_str or "gone" in err_lower or "end of life" in err_lower:
        return "Invalid model (model reached end-of-life)"
    if "404" in err_str or "model_not_found" in err_lower or "does not exist" in err_lower or "invalid model" in err_lower:
        return "Invalid model (model not found on provider)"
    if "429" in err_str or "rate limit" in err_lower or "quota" in err_lower or "too many requests" in err_lower:
        return "Rate limit exceeded"
    if "503" in err_str or "502" in err_str or "504" in err_str or "service unavailable" in err_lower or "bad gateway" in err_lower:
        return "Provider unavailable"
    if "500" in err_str:
        return "Provider internal server error"
    if "jsondecodeerror" in err_lower or "malformed" in err_lower or ("json" in err_lower and "extract" in err_lower):
        return "Malformed response"
    if "connection" in err_lower or "network" in err_lower or "dns" in err_lower:
        return "Provider unavailable (connection failed)"

    first_line = err_str.split("\n")[0].strip()
    return first_line[:30] if first_line else "Unknown error"


async def test_single_provider(
    provider: BaseLLMProvider,
    display_name: str,
    timeout_seconds: float = 15.0,
) -> Tuple[str, str, Optional[float]]:
    """Test a single provider independently with a tiny minimal request.
    
    Returns (display_name, status_str, latency_ms).
    """
    if not provider.is_configured:
        return (display_name, "FAIL - Missing API key", None)

    task = "smoke_test"
    input_text = 'Return JSON: {"status": "OK"}'
    system_prompt = 'You are a health-check responder. Reply strictly in JSON: {"status": "OK"}.'

    start_time = time.time()
    try:
        result: LLMResult = await asyncio.wait_for(
            provider.generate(
                task=task,
                input_text=input_text,
                system_prompt=system_prompt,
            ),
            timeout=timeout_seconds,
        )

        latency_ms = (time.time() - start_time) * 1000

        # Validate that the response is successful and contains valid data
        if result.success and (result.parsed_json is not None or result.raw_text):
            return (display_name, "PASS", latency_ms)
        else:
            return (display_name, "FAIL - Malformed response", latency_ms)

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        reason = classify_error(e)
        return (display_name, f"FAIL - {reason}", latency_ms)


async def run_smoke_tests() -> List[Tuple[str, str, Optional[float]]]:
    """Execute smoke test for all 4 providers independently."""
    providers_to_test = [
        ("Groq", GroqProvider()),
        ("NVIDIA", NvidiaProvider()),
        ("SambaNova", SambaNovaProvider()),
        ("OpenRouter", OpenRouterProvider()),
    ]

    results = []
    for display_name, provider_instance in providers_to_test:
        result = await test_single_provider(provider_instance, display_name, timeout_seconds=15.0)
        results.append(result)

    return results


def print_results(results: List[Tuple[str, str, Optional[float]]]) -> None:
    """Print results in the requested compact format."""
    print()
    for name, status, _ in results:
        print(f"{name:<10} {status}")
    print()


if __name__ == "__main__":
    test_results = asyncio.run(run_smoke_tests())
    print_results(test_results)
