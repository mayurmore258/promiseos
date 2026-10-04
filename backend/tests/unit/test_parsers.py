"""Unit tests for document parsers (TXT, CSV, PDF, DOCX, XLSX)."""

import io
import pytest
from app.core.exceptions import UnsupportedFileError
from app.evidence.parsers import parse_evidence_file
from app.evidence.parsers.csv_parser import CSVParser
from app.evidence.parsers.text_parser import TextParser


def test_text_parser():
    content = b"Rahul: I will send the quotation tonight.\nMayur: Thanks."
    text, meta = parse_evidence_file(content, "chat.txt")
    assert "quotation" in text
    assert meta["format"] == "text"
    assert meta["line_count"] == 2


def test_csv_parser():
    content = b"Item,Price,Status\nWidget A,$50,Available\nWidget B,$100,Updated\n"
    text, meta = parse_evidence_file(content, "pricing.csv")
    assert "Widget A" in text
    assert "Item: Widget A | Price: $50 | Status: Available" in text
    assert meta["format"] == "csv"
    assert meta["row_count"] == 3


def test_docx_parser():
    import docx
    doc = docx.Document()
    doc.add_paragraph("Official Deliverable Document")
    doc.add_paragraph("Quotation confirmed for Mayur.")
    bio = io.BytesIO()
    doc.save(bio)
    docx_bytes = bio.getvalue()

    text, meta = parse_evidence_file(docx_bytes, "deliverable.docx")
    assert "Official Deliverable Document" in text
    assert "Quotation confirmed" in text
    assert meta["format"] == "docx"


def test_xlsx_parser():
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Catalog"
    ws.append(["Product", "Cost", "Delivery"])
    ws.append(["Module 1", 500, "Free"])
    bio = io.BytesIO()
    wb.save(bio)
    xlsx_bytes = bio.getvalue()

    text, meta = parse_evidence_file(xlsx_bytes, "catalog.xlsx")
    assert "Module 1" in text
    assert "Cost: 500" in text
    assert meta["format"] == "xlsx"


def test_unsupported_parser():
    with pytest.raises(UnsupportedFileError):
        parse_evidence_file(b"data", "script.py")
