"""Parsers package with format dispatcher."""

from pathlib import Path
from typing import Tuple
from app.core.exceptions import UnsupportedFileError
from .text_parser import TextParser
from .pdf_parser import PDFParser
from .docx_parser import DocxParser
from .csv_parser import CSVParser
from .xlsx_parser import XLSXParser

PARSER_MAP = {
    ".txt": TextParser(),
    ".md": TextParser(),
    ".json": TextParser(),
    ".log": TextParser(),
    ".pdf": PDFParser(),
    ".docx": DocxParser(),
    ".csv": CSVParser(),
    ".xlsx": XLSXParser(),
}


def parse_evidence_file(content_bytes: bytes, filename: str) -> Tuple[str, dict]:
    """Selects the parser corresponding to filename extension and extracts content."""
    ext = Path(filename).suffix.lower()
    parser = PARSER_MAP.get(ext)
    if not parser:
        raise UnsupportedFileError(filename)
    return parser.parse(content_bytes, filename)


__all__ = [
    "TextParser",
    "PDFParser",
    "DocxParser",
    "CSVParser",
    "XLSXParser",
    "parse_evidence_file",
]
