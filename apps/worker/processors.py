from datetime import datetime
from typing import Any


def normalize_log(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw log entry into a structured format."""
    level = raw.get("level", "INFO").upper()
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if level not in valid_levels:
        level = "INFO"

    timestamp = raw.get("timestamp")
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    elif not isinstance(timestamp, datetime):
        timestamp = datetime.utcnow()

    return {
        "service_name": raw.get("service_name", "unknown"),
        "timestamp": timestamp,
        "level": level,
        "message": raw.get("message", ""),
        "source": raw.get("source"),
        "container_id": raw.get("container_id"),
        "container_name": raw.get("container_name"),
        "raw": raw.get("raw"),
    }
