import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app


@pytest.mark.asyncio
async def test_ingest_and_retrieve():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Reading logs is gated, so retrieve an owner token first.
        registered = await client.post(
            "/api/v1/auth/register",
            json={"email": "pipeline@example.com", "password": "correct-horse-battery"},
        )
        assert registered.status_code == 201, registered.text
        headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}

        # Ingest a log
        response = await client.post("/api/v1/ingest", json={
            "service_name": "test-service",
            "timestamp": "2024-01-01T00:00:00Z",
            "level": "ERROR",
            "message": "Test error",
        })
        assert response.status_code == 200

        # Retrieve logs
        response = await client.get("/api/v1/logs", headers=headers)
        assert response.status_code == 200
