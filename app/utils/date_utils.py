from datetime import datetime
from typing import Optional


def now_iso() -> str:
    """Get current time in ISO format"""
    return datetime.utcnow().isoformat()


def parse_iso(iso_string: str) -> Optional[datetime]:
    """Parse ISO format string to datetime"""
    try:
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    except:
        return None
