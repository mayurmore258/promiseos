"""Unit tests for security, path traversal protection, and file sanitization."""

from pathlib import Path
import pytest
from app.core.security import (
    compute_sha256,
    is_safe_path,
    sanitize_filename,
    validate_file_extension,
)


def test_sanitize_filename():
    assert sanitize_filename("../../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\windows\\system32\\calc.exe") == "calc.exe"
    assert sanitize_filename("my\0secret\0file.txt") == "mysecretfile.txt"
    assert sanitize_filename("quotation revised (v2).txt") == "quotation revised (v2).txt"
    assert sanitize_filename("") == "unnamed_file"


def test_compute_sha256():
    data1 = b"Hello PromiseOS"
    data2 = b"Hello PromiseOS"
    data3 = b"Different Content"
    assert compute_sha256(data1) == compute_sha256(data2)
    assert compute_sha256(data1) != compute_sha256(data3)


def test_validate_file_extension():
    for valid in ["doc.txt", "report.pdf", "sheet.xlsx", "table.csv", "memo.docx", "note.md"]:
        is_val, ext = validate_file_extension(valid)
        assert is_val is True

    for invalid in ["script.py", "program.exe", "run.bat", "exploit.sh", "archive.zip"]:
        is_val, ext = validate_file_extension(invalid)
        assert is_val is False


def test_is_safe_path(tmp_path):
    base_dir = tmp_path / "uploads"
    base_dir.mkdir()

    safe_target = base_dir / "safe_file.txt"
    unsafe_target = base_dir / ".." / "escaped.txt"
    root_traversal = Path("C:/Windows/System32/drivers/etc/hosts")

    assert is_safe_path(base_dir, safe_target) is True
    assert is_safe_path(base_dir, unsafe_target) is False
    assert is_safe_path(base_dir, root_traversal) is False
