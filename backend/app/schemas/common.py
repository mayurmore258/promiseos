"""Common Pydantic Schemas for API responses and errors."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Machine-readable error code", examples=["COMMITMENT_NOT_FOUND"])
    message: str = Field(..., description="Human-readable error explanation", examples=["Commitment was not found."])
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional context or validation details")


class ErrorResponse(BaseModel):
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: str = Field(default="ok", examples=["ok"])
    app: str = Field(default="PromiseOS Backend")
    version: str = Field(default="1.0.0")


class ReadyResponse(BaseModel):
    status: str = Field(default="ready", examples=["ready"])
    database: str = Field(..., examples=["connected"])
    storage: str = Field(..., examples=["ready"])
    llm_mode: str = Field(..., examples=["mock"])
    active_providers: List[str] = Field(default_factory=list, examples=[["mock"]])
