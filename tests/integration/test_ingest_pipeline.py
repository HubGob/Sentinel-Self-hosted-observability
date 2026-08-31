import pytest
from httpx import AsyncClient, ASGITransport
from apps.api.main import app


@pytest.mark.asyncio
async def test_ingest_and_retrieve():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Ingest a log
        response = await client.post("/api/v1/ingest", json={
            "service_name": "test-service",
            "timestamp": "2024-01-01T00:00:00Z",
            "level": "ERROR",
            "message": "Test error",
        })
        assert response.status_code == 200

        # Retrieve logs
        response = await client.get("/api/v1/logs")
        assert response.status_code == 200
