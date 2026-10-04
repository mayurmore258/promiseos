"""File persistence and processing service.

Handles validation, hashing, safe disk storage, format parsing, and chunking.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
from app.core.config import settings
from app.core.exceptions import (
    FileSizeExceededError,
    MalformedFileError,
    SecurityError,
    UnsupportedFileError,
)
from app.core.logging import logger
from app.core.security import (
    compute_sha256,
    is_safe_path,
    sanitize_filename,
    validate_file_extension,
    EXTENSION_TO_MIME,
)
from app.evidence.chunker import DocumentChunker
from app.evidence.parsers import parse_evidence_file
from app.utils.ids import generate_uuid


class FileService:
    """Safely ingests, parses, and chunks uploaded evidence files."""

    def __init__(self):
        self.chunker = DocumentChunker(chunk_size=500, chunk_overlap=80)

    def process_file_content(
        self,
        file_bytes: bytes,
        original_filename: str,
        content_type: str = None,
    ) -> Tuple[str, str, str, int, str, dict, List[Dict[str, Any]]]:
        """Validates, stores, parses, and chunks uploaded file content.

        Returns:
            (safe_filename, storage_path, mime_type, file_size, content_hash, metadata, chunks)
        """
        # 1. Size validation
        size = len(file_bytes)
        if size == 0:
            raise MalformedFileError(original_filename, "Uploaded file is empty (0 bytes).")
        if size > settings.max_upload_size_bytes:
            raise FileSizeExceededError(original_filename, size, settings.MAX_UPLOAD_SIZE_MB)

        # 2. Extension & MIME validation
        clean_name = sanitize_filename(original_filename)
        is_valid, ext = validate_file_extension(clean_name)
        if not is_valid:
            raise UnsupportedFileError(clean_name, content_type)

        mime = content_type or EXTENSION_TO_MIME.get(ext, "application/octet-stream")

        # 3. Content hash
        content_hash = compute_sha256(file_bytes)

        # 4. Save file safely with unique prefix to prevent overwrite or path traversal
        unique_name = f"{generate_uuid()}_{clean_name}"
        target_path = settings.upload_path / unique_name

        if not is_safe_path(settings.upload_path, target_path):
            raise SecurityError("Detected unauthorized path traversal attempt.")

        try:
            target_path.write_bytes(file_bytes)
        except Exception as e:
            raise MalformedFileError(clean_name, f"Failed to persist file: {str(e)}")

        # 5. Extract text and metadata
        raw_text, meta = parse_evidence_file(file_bytes, clean_name)

        # 6. Chunk text
        chunks = self.chunker.chunk_text(
            raw_text,
            base_metadata={"file_name": clean_name, "content_hash": content_hash},
        )

        logger.info(
            f"Processed file '{clean_name}' ({size} bytes, {len(chunks)} chunks, hash={content_hash[:8]})",
            extra={"operation": "process_file", "file_name": clean_name},
        )

        return (
            clean_name,
            str(target_path),
            mime,
            size,
            content_hash,
            meta,
            chunks,
            raw_text,
        )


file_service = FileService()
