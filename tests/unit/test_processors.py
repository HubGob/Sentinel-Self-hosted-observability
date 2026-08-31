from datetime import datetime
from sentinel.worker.processors import normalize_log


def test_normalize_log():
    raw = {
        "service_name": "my-app",
        "timestamp": "2024-01-01T00:00:00Z",
        "level": "error",
        "message": "Connection refused",
    }
    result = normalize_log(raw)
    assert result["service_name"] == "my-app"
    assert result["level"] == "ERROR"
    assert isinstance(result["timestamp"], datetime)


def test_normalize_log_defaults():
    raw = {"message": "hello"}
    result = normalize_log(raw)
    assert result["level"] == "INFO"
    assert result["service_name"] == "unknown"
