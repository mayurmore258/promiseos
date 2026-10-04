"""Parser for plain text, markdown, and json evidence files."""

from typing import Tuple
from app.core.exceptions import MalformedFileError
from app.utils.text import clean_text


class TextParser:
    """Parses plain text formats (.txt, .md, .log, .json)."""

    def parse(self, content_bytes: bytes, filename: str) -> Tuple[str, dict]:
        """Extracts text content and metadata from raw bytes."""
        try:
            # Try utf-8 first, fallback to latin-1
            try:
                raw_str = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raw_str = content_bytes.decode("latin-1")

            cleaned = clean_text(raw_str)
            line_count = len(raw_str.splitlines())
            metadata = {
                "format": "text",
                "character_count": len(cleaned),
                "line_count": line_count,
            }
            return cleaned, metadata
        except Exception as e:
            raise MalformedFileError(filename, f"Error decoding text: {str(e)}")
