"""Read routers are gated; these tests now authenticate first.

The gate itself is covered in test_auth.py. What matters here is that the
endpoints still return the right shapes once you are allowed in.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app

EMAIL = "reader@example.com"
PASSWORD = "correct-horse-battery"


async def _authorized_client(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/auth/register", json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 201, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_list_logs_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _authorized_client(client)
        response = await client.get("/api/v1/logs", headers=headers)
    assert response.status_code == 200
    assert response.json()["logs"] == []


async def test_list_services_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _authorized_client(client)
        response = await client.get("/api/v1/services", headers=headers)
    assert response.status_code == 200
    assert response.json()["services"] == []


async def test_list_alerts_empty() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = await _authorized_client(client)
        response = await client.get("/api/v1/alerts", headers=headers)
    assert response.status_code == 200
    assert response.json()["alerts"] == []


@pytest.mark.parametrize("path", ["/api/v1/logs", "/api/v1/services", "/api/v1/alerts"])
async def test_gated_routers_are_unreachable_without_a_token(path: str) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(path)
    assert response.status_code == 401
