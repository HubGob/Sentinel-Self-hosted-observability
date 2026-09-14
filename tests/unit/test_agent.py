from typing import Any

import pytest

from apps.agent.agent import check_target, classify, load_targets


class FakeResponse:
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code


class FakeClient:
    """Minimal httpx.AsyncClient stand-in: returns a canned response or raises."""

    def __init__(self, status_code: int = 200, exc: Exception | None = None) -> None:
        self.status_code = status_code
        self.exc = exc
        self.posted: list[tuple[str, dict[str, Any]]] = []

    async def get(self, url: str) -> FakeResponse:
        if self.exc is not None:
            raise self.exc
        return FakeResponse(self.status_code)

    async def post(self, url: str, json: dict[str, Any]) -> FakeResponse:
        self.posted.append((url, json))
        return FakeResponse(204)


def test_classify_treats_client_errors_as_up():
    assert classify(200) == "up"
    assert classify(404) == "up"


def test_classify_treats_server_errors_as_down():
    assert classify(500) == "down"
    assert classify(503) == "down"


def test_load_targets_parses_a_json_array():
    assert load_targets('[{"name": "weather-app", "url": "https://example.com"}]') == [
        {"name": "weather-app", "url": "https://example.com"}
    ]


def test_load_targets_empty_is_an_empty_list():
    assert load_targets("") == []
    assert load_targets("   ") == []


def test_load_targets_rejects_non_array_json():
    with pytest.raises(ValueError):
        load_targets('{"name": "not-a-list"}')


@pytest.mark.asyncio
async def test_check_target_reports_up_with_latency():
    target = {"name": "svc", "url": "https://example.com"}
    result = await check_target(target, client=FakeClient(status_code=200))  # type: ignore[arg-type]
    assert result["service_name"] == "svc"
    assert result["url"] == "https://example.com"
    assert result["status"] == "up"
    assert isinstance(result["latency_ms"], int)


@pytest.mark.asyncio
async def test_check_target_reports_down_when_the_request_raises():
    target = {"name": "svc", "url": "https://example.com"}
    client = FakeClient(exc=ConnectionError("refused"))
    result = await check_target(target, client=client)  # type: ignore[arg-type]
    assert result["status"] == "down"
    assert result["latency_ms"] is None
