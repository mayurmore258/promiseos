"""Parser for PDF evidence files."""

import io
from typing import Tuple
from app.core.exceptions import MalformedFileError
from app.utils.text import clean_text


class PDFParser:
    """Extracts text and page structure from PDF documents."""

    def parse(self, content_bytes: bytes, filename: str) -> Tuple[str, dict]:
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content_bytes))
            pages_text = []
            num_pages = len(reader.pages)

            for i, page in enumerate(reader.pages):
                txt = page.extract_text() or ""
                pages_text.append(txt)

            full_text = clean_text("\n\n".join(pages_text))
            metadata = {
                "format": "pdf",
                "page_count": num_pages,
                "character_count": len(full_text),
            }
            return full_text, metadata
        except Exception as e:
            raise MalformedFileError(filename, f"Failed to extract PDF content: {str(e)}")
