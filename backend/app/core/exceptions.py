"""PromiseOS Custom Exceptions and Error Handlers.

Provides standard exception classes and error responses conforming to:
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human-readable description",
        "details": {}
    }
}
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class PromiseOSError(Exception):
    """Base exception for all PromiseOS domain errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }

    def to_response(self) -> JSONResponse:
        return JSONResponse(status_code=self.status_code, content=self.to_dict())


class NotFoundError(PromiseOSError):
    """Resource not found (commitment, evidence, followup)."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource.capitalize()} '{identifier}' was not found.",
            code=f"{resource.upper()}_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "id": identifier},
        )


class ValidationError(PromiseOSError):
    """Client request input validation error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class UnsupportedFileError(PromiseOSError):
    """File extension or MIME type not supported."""

    def __init__(self, file_name: str, mime_type: Optional[str] = None):
        super().__init__(
            message=f"File '{file_name}' format is not supported. Supported: TXT, PDF, DOCX, CSV, XLSX.",
            code="UNSUPPORTED_FILE_TYPE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"file_name": file_name, "mime_type": mime_type},
        )


class FileSizeExceededError(PromiseOSError):
    """Uploaded file exceeds max allowed size."""

    def __init__(self, file_name: str, size_bytes: int, max_mb: int):
        super().__init__(
            message=f"File '{file_name}' ({size_bytes / (1024*1024):.1f}MB) exceeds limit of {max_mb}MB.",
            code="FILE_SIZE_EXCEEDED",
            status_code=413,
            details={"file_name": file_name, "size_bytes": size_bytes, "max_mb": max_mb},
        )


class MalformedFileError(PromiseOSError):
    """File could not be parsed or contains malformed data."""

    def __init__(self, file_name: str, reason: str):
        super().__init__(
            message=f"Failed to process '{file_name}': {reason}",
            code="MALFORMED_FILE",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"file_name": file_name, "reason": reason},
        )


class SecurityError(PromiseOSError):
    """Path traversal or security violation detected."""

    def __init__(self, message: str = "Invalid file path or security violation"):
        super().__init__(
            message=message,
            code="SECURITY_VIOLATION",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class ProviderError(PromiseOSError):
    """AI / LLM Provider error (timeout, rate limit, parse error)."""

    def __init__(self, provider: str, message: str, is_retryable: bool = True):
        super().__init__(
            message=f"AI Provider '{provider}' failed: {message}",
            code="AI_PROVIDER_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
            details={"provider": provider, "retryable": is_retryable},
        )


class StorageError(PromiseOSError):
    """Storage or file persistence error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="STORAGE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )


class VerificationError(PromiseOSError):
    """Error during verification pipeline execution."""

    def __init__(self, commitment_id: str, reason: str):
        super().__init__(
            message=f"Verification failed for commitment '{commitment_id}': {reason}",
            code="VERIFICATION_FAILED",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"commitment_id": commitment_id, "reason": reason},
        )
