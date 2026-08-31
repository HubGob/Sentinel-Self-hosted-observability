from httpx import AsyncClient, ASGITransport
import pytest
from apps.api.main import app


@pytest.mark.asyncio
async def test_list_logs_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/logs")
    assert response.status_code == 200
    assert response.json()["logs"] == []


@pytest.mark.asyncio
async def test_list_services_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/services")
    assert response.status_code == 200
    assert response.json()["services"] == []


@pytest.mark.asyncio
async def test_list_alerts_empty():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/alerts")
    assert response.status_code == 200
    assert response.json()["alerts"] == []
