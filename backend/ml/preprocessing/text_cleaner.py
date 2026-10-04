"""Reproducible local text preprocessing for Commitment Classification."""

import re
from typing import Optional


def clean_text(text: Optional[str]) -> str:
    """Preprocess and clean input text for TF-IDF feature extraction.
    
    Preserves:
    - Crucial commitment indicator contractions (i'll, we'll, won't, can't, i'm).
    - Basic punctuation cues while stripping irregular whitespace and control characters.
    - Speaker delimiters (e.g., 'Rahul: ') are standardized to space.
    """
    if not text or not isinstance(text, str):
        return ""

    # Convert to lowercase
    s = text.lower()

    # Standardize speaker turn indicators in multi-message chats (e.g. "rahul: " -> "rahul ")
    s = re.sub(r"^[a-z0-9_\-\s]+:\s*", " ", s, flags=re.MULTILINE)

    # Standardize common contractions
    s = s.replace("’", "'").replace("`", "'")

    # Replace newlines with spaces
    s = re.sub(r"[\r\n\t]+", " ", s)

    # Remove non-word characters except apostrophes and hyphens
    s = re.sub(r"[^\w\s'-]", " ", s)

    # Normalize multiple spaces
    s = re.sub(r"\s+", " ", s).strip()

    return s
