"""Unit tests for date and deadline parsing."""

from datetime import datetime, timedelta, time
import pytest
from app.utils.dates import parse_deadline, normalize_date_str


def test_parse_deadline_tonight():
    ref = datetime(2026, 10, 4, 14, 0, 0)
    raw, parsed = parse_deadline("tonight", reference_dt=ref)
    assert raw == "tonight"
    assert parsed is not None
    assert parsed.date() == ref.date()
    assert parsed.time() == time(23, 59, 59)


def test_parse_deadline_tomorrow():
    ref = datetime(2026, 10, 4, 10, 30, 0)
    raw, parsed = parse_deadline("I'll send it tomorrow", reference_dt=ref)
    assert "tomorrow" in raw
    assert parsed is not None
    assert parsed.date() == (ref + timedelta(days=1)).date()
    assert parsed.time() == time(23, 59, 59)


def test_parse_deadline_next_friday():
    ref = datetime(2026, 10, 4, 12, 0, 0)  # Sunday
    raw, parsed = parse_deadline("next Friday", reference_dt=ref)
    assert raw == "next Friday"
    assert parsed is not None
    assert parsed.weekday() == 4  # Friday
    assert parsed > ref


def test_parse_deadline_this_week():
    ref = datetime(2026, 10, 5, 9, 0, 0)  # Monday
    raw, parsed = parse_deadline("by end of this week", reference_dt=ref)
    assert parsed is not None
    assert parsed.weekday() == 6  # Sunday


def test_parse_deadline_ambiguous_keywords():
    for kw in ["soon", "later", "sometime", "asap", "whenever"]:
        raw, parsed = parse_deadline(kw)
        assert raw == kw
        # Crucial principle: ambiguous terms must NOT invent a date!
        assert parsed is None


def test_parse_deadline_explicit_date():
    ref = datetime(2026, 10, 4, 10, 0, 0)
    raw, parsed = parse_deadline("2026-10-15", reference_dt=ref)
    assert parsed is not None
    assert parsed.year == 2026
    assert parsed.month == 10
    assert parsed.day == 15


def test_parse_deadline_empty():
    assert parse_deadline("") == (None, None)
    assert parse_deadline("   ") == (None, None)
    assert parse_deadline(None) == (None, None)


def test_normalize_date_str():
    dt = datetime(2026, 10, 4, 23, 59, 59)
    assert normalize_date_str(dt) == "2026-10-04T23:59:59"
    assert normalize_date_str(None) is None
