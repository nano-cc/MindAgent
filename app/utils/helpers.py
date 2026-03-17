import json
from typing import Any


def parse_json_field(value: str) -> Any:
    """Parse JSON field from database"""
    if not value:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return None


def to_json_field(value: Any) -> str:
    """Convert value to JSON field for database"""
    if value is None:
        return None
    return json.dumps(value)


def sanitize_string(value: str, max_length: int = None) -> str:
    """Sanitize string input"""
    if not value:
        return ""
    result = value.strip()
    if max_length and len(result) > max_length:
        result = result[:max_length]
    return result
