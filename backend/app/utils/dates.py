"""Date parsing and normalization utilities.

Preserves the original raw deadline string (e.g. "tonight", "tomorrow", "next Friday")
while calculating a normalized ISO datetime where feasible, without inventing dates for ambiguous terms.
"""

from datetime import datetime, timedelta, time
from typing import Optional, Tuple
from dateutil import parser as dateutil_parser

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

AMBIGUOUS_KEYWORDS = {
    "soon",
    "later",
    "sometime",
    "asap",
    "whenever",
    "eventually",
    "in future",
    "when possible",
    "tbd",
}


def parse_deadline(
    raw_text: Optional[str],
    reference_dt: Optional[datetime] = None,
) -> Tuple[Optional[str], Optional[datetime]]:
    """Parses raw deadline text into (raw_text, normalized_datetime).

    If raw_text is ambiguous or empty, normalized_datetime is None.
    Never invents a timestamp for ambiguous input.
    """
    if not raw_text or not raw_text.strip():
        return None, None

    raw_clean = raw_text.strip()
    lowered = raw_clean.lower()
    ref = reference_dt or datetime.now()

    # Check for explicitly ambiguous terms
    if any(kw in lowered for kw in AMBIGUOUS_KEYWORDS):
        return raw_clean, None

    # Handle relative keywords
    if "tonight" in lowered:
        normalized = datetime.combine(ref.date(), time(23, 59, 59))
        return raw_clean, normalized

    if "today" in lowered:
        normalized = datetime.combine(ref.date(), time(23, 59, 59))
        return raw_clean, normalized

    if "day after tomorrow" in lowered:
        normalized = datetime.combine(ref.date() + timedelta(days=2), time(23, 59, 59))
        return raw_clean, normalized

    if "tomorrow" in lowered:
        normalized = datetime.combine(ref.date() + timedelta(days=1), time(23, 59, 59))
        return raw_clean, normalized

    if "end of this week" in lowered or "this week" in lowered:
        # End of current week (Sunday)
        days_ahead = 6 - ref.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        normalized = datetime.combine(ref.date() + timedelta(days=days_ahead), time(23, 59, 59))
        return raw_clean, normalized

    # Check weekday patterns like "next friday", "by monday"
    for day_name, day_num in WEEKDAYS.items():
        if day_name in lowered:
            days_ahead = (day_num - ref.weekday()) % 7
            if "next" in lowered or days_ahead == 0:
                days_ahead += 7
            normalized = datetime.combine(ref.date() + timedelta(days=days_ahead), time(23, 59, 59))
            return raw_clean, normalized

    # Try standard dateutil parsing for explicit dates (e.g., "2026-10-04", "Oct 15", "October 4th 5pm")
    try:
        parsed = dateutil_parser.parse(raw_clean, fuzzy=True, default=ref)
        # If no time was specified, default to end of day
        if parsed.time() == time(0, 0):
            parsed = datetime.combine(parsed.date(), time(23, 59, 59))
        return raw_clean, parsed
    except (ValueError, TypeError, OverflowError):
        # Ambiguous or non-parseable format
        return raw_clean, None


def normalize_date_str(dt: Optional[datetime]) -> Optional[str]:
    """Formats datetime as ISO-8601 string."""
    if dt is None:
        return None
    return dt.isoformat()
