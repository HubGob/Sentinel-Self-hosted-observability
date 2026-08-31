import pytest
from sentinel.apps.collector.collector import parse_docker_log


def test_parse_docker_log():
    line = "2024-01-01T00:00:00Z ERROR Connection refused"
    result = parse_docker_log(line, "my-container", "abc123")
    assert result["service_name"] == "my-container"
    assert result["level"] == "ERROR"
    assert result["message"] == "Connection refused"


def test_parse_docker_log_no_level():
    line = "2024-01-01T00:00:00Z Hello world"
    result = parse_docker_log(line, "my-container", "abc123")
    assert result["level"] == "INFO"
    assert result["message"] == "Hello world"
