import httpx
import pytest

from sentinel import notify
from sentinel.config import settings


class FakeResponse:
    def __init__(self, status_code: int = 204) -> None:
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("boom", request=None, response=None)  # type: ignore[arg-type]


class FakeAsyncClient:
    posted: list[tuple[str, dict]] = []

    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, *args) -> bool:
        return False

    async def post(self, url: str, json: dict | None = None) -> FakeResponse:
        FakeAsyncClient.posted.append((url, json or {}))
        return FakeResponse()


def test_payload_marks_down_red_and_up_green():
    down = notify.build_payload("svc", opened=True, url="https://svc.example.com")
    up = notify.build_payload("svc", opened=False)

    assert "DOWN" in down["embeds"][0]["title"]
    assert down["embeds"][0]["color"] == notify.RED
    assert down["embeds"][0]["description"] == "https://svc.example.com"
    assert "UP" in up["embeds"][0]["title"]
    assert up["embeds"][0]["color"] == notify.GREEN


@pytest.mark.asyncio
async def test_notify_is_a_noop_without_a_webhook(monkeypatch):
    monkeypatch.setattr(settings, "discord_webhook_url", None)
    assert await notify.notify_incident("svc", opened=True) is False


@pytest.mark.asyncio
async def test_notify_posts_the_payload_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "discord_webhook_url", "https://discord.test/hook")
    monkeypatch.setattr(notify.httpx, "AsyncClient", FakeAsyncClient)
    FakeAsyncClient.posted = []

    assert await notify.notify_incident("svc", opened=True, url="https://svc.example.com") is True
    url, body = FakeAsyncClient.posted[0]
    assert url == "https://discord.test/hook"
    assert "DOWN" in body["embeds"][0]["title"]


@pytest.mark.asyncio
async def test_notify_swallows_failures(monkeypatch):
    monkeypatch.setattr(settings, "discord_webhook_url", "https://discord.test/hook")

    class ExplodingClient(FakeAsyncClient):
        async def post(self, url: str, json: dict | None = None) -> FakeResponse:
            raise ConnectionError("no route to host")

    monkeypatch.setattr(notify.httpx, "AsyncClient", ExplodingClient)
    assert await notify.notify_incident("svc", opened=True) is False
