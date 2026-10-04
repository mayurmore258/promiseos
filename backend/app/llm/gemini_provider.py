"""Google Gemini Provider implementation."""

import json
import re
import time
from typing import Any, Dict, Optional, Type
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.llm.base import BaseLLMProvider, LLMResult


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider."""

    DEFAULT_MODEL = "gemini-1.5-flash"
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.GEMINI_API_KEY
        super().__init__(name="gemini", is_configured=bool(key and key.strip()))
        self.api_key = key

    async def generate(
        self,
        task: str,
        input_text: str,
        schema: Optional[Type[BaseModel]] = None,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> LLMResult:
        if not self.is_configured:
            raise ProviderError("gemini", "GEMINI_API_KEY is not configured", is_retryable=False)

        start = time.time()
        url = f"{self.BASE_URL}/{self.DEFAULT_MODEL}:generateContent?key={self.api_key}"

        sys_msg = system_prompt or (
            "You are PromiseOS AI, an agent specializing in discovering commitments, "
            "planning verification evidence, and performing unbiased factual verification. "
            "Always respond in valid JSON format."
        )

        prompt = f"{sys_msg}\n\nTask: {task}\n\nContext: {json.dumps(context or {})}\n\nInput:\n{input_text}"

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    raise ProviderError("gemini", f"HTTP {res.status_code}: {res.text}", is_retryable=True)

                data = res.json()
                raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed_json = self._extract_json(raw_text)
                latency = (time.time() - start) * 1000

                return LLMResult(
                    task=task,
                    provider="gemini",
                    model=self.DEFAULT_MODEL,
                    raw_text=raw_text,
                    parsed_json=parsed_json,
                    latency_ms=round(latency, 2),
                    success=True,
                )
        except httpx.TimeoutException:
            raise ProviderError("gemini", "Request timed out after 25s", is_retryable=True)
        except httpx.RequestError as e:
            raise ProviderError("gemini", f"Network request error: {str(e)}", is_retryable=True)

    def _extract_json(self, text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if match:
                return json.loads(match.group(1))
            raise
