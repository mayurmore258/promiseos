"""LLM Provider Base Classes and Interfaces."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel, Field


class LLMResult(BaseModel):
    """Standardized response container from any LLM provider."""
    task: str
    provider: str
    model: str
    raw_text: str
    parsed_json: Optional[Any] = None
    latency_ms: float = 0.0
    success: bool = True
    error_message: Optional[str] = None


class BaseLLMProvider(ABC):
    """Abstract interface that all AI providers must implement."""

    def __init__(self, name: str, is_configured: bool = False):
        self.name = name
        self.is_configured = is_configured

    @abstractmethod
    async def generate(
        self,
        task: str,
        input_text: str,
        schema: Optional[Type[BaseModel]] = None,
        context: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None,
    ) -> LLMResult:
        """Executes LLM completion for the given task and returns a structured LLMResult."""
        pass
