"""LLM Router with Priority Order, Graceful Fallbacks, and JSON Validation.

Order: Groq -> NVIDIA NIM -> SambaNova -> Gemini -> OpenRouter -> MockLLM
Falls back immediately to MockLLM if in MOCK_LLM mode or if no external keys are configured.
"""

from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, ValidationError as PydanticValidationError
from app.core.config import settings
from app.core.exceptions import ProviderError
from app.core.logging import logger
from app.llm.base import BaseLLMProvider, LLMResult
from app.llm.groq_provider import GroqProvider
from app.llm.nvidia_provider import NvidiaProvider
from app.llm.sambanova_provider import SambaNovaProvider
from app.llm.gemini_provider import GeminiProvider
from app.llm.openrouter_provider import OpenRouterProvider
from app.llm.mock import MockLLMProvider


class LLMRouter:
    """Manages provider fallback chain and schema enforcement."""

    def __init__(self):
        self.mock_provider = MockLLMProvider()
        # Instantiate provider candidates
        self.providers: List[BaseLLMProvider] = [
            GroqProvider(),
            NvidiaProvider(),
            SambaNovaProvider(),
            GeminiProvider(),
            OpenRouterProvider(),
        ]

    def get_active_providers(self) -> List[BaseLLMProvider]:
        """Returns list of configured providers according to priority order."""
        if settings.should_use_mock_llm():
            return [self.mock_provider]

        configured = [p for p in self.providers if p.is_configured]
        # Always attach mock provider at the end as ultimate offline resilience
        configured.append(self.mock_provider)
        return configured

    async def generate(
        self,
        task: str,
        input_text: str,
        schema: Optional[Type[BaseModel]] = None,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> LLMResult:
        """Executes task through provider chain with automatic fallback on failure."""
        active_chain = self.get_active_providers()
        last_error = None

        for provider in active_chain:
            try:
                logger.info(
                    f"Executing LLM task '{task}' with provider '{provider.name}'",
                    extra={"operation": "llm_generate", "provider": provider.name},
                )
                result = await provider.generate(
                    task=task,
                    input_text=input_text,
                    schema=schema,
                    context=context,
                    system_prompt=system_prompt,
                )

                # Validate against Pydantic schema if provided
                if schema and result.parsed_json is not None:
                    try:
                        if isinstance(result.parsed_json, list):
                            # Validate each item if schema is a single item
                            [schema.model_validate(item) for item in result.parsed_json]
                        elif isinstance(result.parsed_json, dict):
                            schema.model_validate(result.parsed_json)
                    except PydanticValidationError as ve:
                        logger.warning(
                            f"Provider '{provider.name}' output failed schema validation: {ve}. Falling back.",
                            extra={"operation": "llm_schema_mismatch", "provider": provider.name},
                        )
                        last_error = ve
                        continue

                return result

            except Exception as e:
                logger.warning(
                    f"Provider '{provider.name}' failed during task '{task}': {e}. Trying next provider...",
                    extra={"operation": "llm_fallback", "provider": provider.name},
                )
                last_error = e

        # If all real providers failed and mock was not reached, invoke mock directly
        logger.info("All configured providers failed; falling back to MockLLMProvider.")
        return await self.mock_provider.generate(
            task=task,
            input_text=input_text,
            schema=schema,
            context=context,
            system_prompt=system_prompt,
        )


llm_router = LLMRouter()
