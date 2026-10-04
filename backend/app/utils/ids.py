"""UUID utilities for database models and tracking."""

import uuid


def generate_uuid() -> str:
    """Generates a standard UUIDv4 string."""
    return str(uuid.uuid4())


def is_valid_uuid(val: str) -> bool:
    """Validates whether a string is a valid UUID."""
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, AttributeError, TypeError):
        return False
