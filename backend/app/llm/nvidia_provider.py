"""NVIDIA NIM LLM Provider implementation (OpenAI-compatible API)."""

import json
import re
import time
from typing import Any, Dict, Optional, Type
import httpx
from pydantic import BaseModel
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.llm.base import BaseLLMProvider, LLMResult


class NvidiaProvider(BaseLLMProvider):
    """NVIDIA NIM API provider."""

    BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
    DEFAULT_MODEL = "meta/llama-3.1-70b-instruct"

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.NVIDIA_API_KEY
        super().__init__(name="nvidia", is_configured=bool(key and key.strip()))
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
            raise ProviderError("nvidia", "NVIDIA_API_KEY is not configured", is_retryable=False)

        start = time.time()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        sys_msg = system_prompt or (
            "You are PromiseOS AI, an agent specializing in discovering commitments, "
            "planning verification evidence, and performing unbiased factual verification. "
            "Always respond in valid JSON format."
        )

        prompt = f"Task: {task}\n\nContext: {json.dumps(context or {})}\n\nInput:\n{input_text}"

        payload = {
            "model": self.DEFAULT_MODEL,
            "messages": [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        try:
            async with httpx.AsyncClient(timeout=25.0) as client:
                res = await client.post(self.BASE_URL, headers=headers, json=payload)
                if res.status_code != 200:
                    raise ProviderError("nvidia", f"HTTP {res.status_code}: {res.text}", is_retryable=True)

                data = res.json()
                raw_text = data["choices"][0]["message"]["content"]
                parsed_json = self._extract_json(raw_text)
                latency = (time.time() - start) * 1000

                return LLMResult(
                    task=task,
                    provider="nvidia",
                    model=self.DEFAULT_MODEL,
                    raw_text=raw_text,
                    parsed_json=parsed_json,
                    latency_ms=round(latency, 2),
                    success=True,
                )
        except httpx.TimeoutException:
            raise ProviderError("nvidia", "Request timed out after 25s", is_retryable=True)
        except httpx.RequestError as e:
            raise ProviderError("nvidia", f"Network request error: {str(e)}", is_retryable=True)

    def _extract_json(self, text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if match:
                return json.loads(match.group(1))
            raise
