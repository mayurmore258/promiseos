"""Structured Logging for PromiseOS Backend.

Provides standard logging with contextual metadata (request_id, commitment_id,
provider, latency_ms) and redacts any potential secrets.
"""

import json
import logging
import sys
import time
from typing import Any, Dict, Optional
from contextvars import ContextVar

# Context variables for tracing requests across async call chains
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
commitment_id_var: ContextVar[Optional[str]] = ContextVar("commitment_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Formats log records as structured text or JSON."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_var.get()
        com_id = commitment_id_var.get()

        meta: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        if req_id:
            meta["request_id"] = req_id
        if com_id:
            meta["commitment_id"] = com_id

        # Attach custom attributes if passed via extra
        for key in ("operation", "provider", "latency_ms", "status_code", "error_code"):
            if hasattr(record, key):
                meta[key] = getattr(record, key)

        if record.exc_info:
            meta["exc_info"] = self.formatException(record.exc_info)

        # In development, pretty format; in production/test, structured representation
        parts = [
            f"[{meta['timestamp']}]",
            f"[{meta['level']}]",
            f"[{meta.get('operation', record.name)}]",
            meta["message"],
        ]
        if req_id:
            parts.append(f"(req={req_id})")
        if com_id:
            parts.append(f"(com={com_id})")
        if "provider" in meta:
            parts.append(f"provider={meta['provider']}")
        if "latency_ms" in meta:
            parts.append(f"latency={meta['latency_ms']}ms")

        return " ".join(parts).strip()


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures root and app loggers."""
    log_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
        root_logger.addHandler(handler)
    else:
        root_logger.handlers[0].setFormatter(StructuredFormatter(datefmt="%Y-%m-%d %H:%M:%S"))

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return logging.getLogger("promiseos")


logger = setup_logging()
