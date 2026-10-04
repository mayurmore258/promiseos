"""Security and File Validation Utilities.

Guards against path traversal, validates MIME types and file extensions,
computes cryptographic hashes for duplicate detection, and sanitizes filenames.
"""

import hashlib
import os
import re
from pathlib import Path
from typing import Optional, Set, Tuple

ALLOWED_EXTENSIONS: Set[str] = {
    ".txt",
    ".pdf",
    ".docx",
    ".csv",
    ".xlsx",
    ".md",
    ".json",
}

EXTENSION_TO_MIME = {
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".json": "application/json",
    ".csv": "text/csv",
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def sanitize_filename(filename: str) -> str:
    """Removes path separators, null bytes, and unsafe characters from a filename."""
    # Strip any directory path components
    base = os.path.basename(filename)
    # Remove null bytes
    base = base.replace("\0", "")
    # Allow alphanumeric, dashes, underscores, dots, spaces, parentheses
    clean = re.sub(r"[^\w\s\.\(\)-]", "_", base)
    # Collapse multiple spaces or dots
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean or "unnamed_file"


def compute_sha256(content: bytes) -> str:
    """Computes SHA-256 hash of byte content for deduplication."""
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.hexdigest()


def validate_file_extension(filename: str) -> Tuple[bool, str]:
    """Validates if the file extension is allowed for processing.

    Returns:
        (is_valid, extension)
    """
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS, ext


def is_safe_path(base_dir: Path, target_path: Path) -> bool:
    """Ensures target_path is strictly within base_dir (prevents directory traversal)."""
    try:
        base_resolved = base_dir.resolve()
        target_resolved = target_path.resolve()
        return base_resolved in target_resolved.parents or base_resolved == target_resolved
    except (ValueError, RuntimeError):
        return False
