from httpx import AsyncClient, ASGITransport
import pytest
from apps.api.main import app


@pytest.mark.asyncio
async def test_ingest_log():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/ingest", json={
            "service_name": "test-service",
            "timestamp": "2024-01-01T00:00:00Z",
            "level": "ERROR",
            "message": "Something broke",
        })
    assert response.status_code == 200
    assert response.json()["accepted"] == 1
