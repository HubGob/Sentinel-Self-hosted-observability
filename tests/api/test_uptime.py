import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_report_accepts_an_up_check():
    async with _client() as client:
        response = await client.post(
            "/api/v1/report",
            json={
                "service_name": "weather-app",
                "url": "https://weather.example.com",
                "status": "up",
                "latency_ms": 42,
            },
        )
    assert response.status_code == 200
    assert response.json() == {
        "accepted": 1,
        "incident_opened": False,
        "incident_closed": False,
    }


@pytest.mark.asyncio
async def test_incident_opens_only_after_three_consecutive_failures():
    async with _client() as client:
        first = await client.post("/api/v1/report", json={"service_name": "svc", "status": "down"})
        second = await client.post("/api/v1/report", json={"service_name": "svc", "status": "down"})
        third = await client.post("/api/v1/report", json={"service_name": "svc", "status": "down"})
    assert first.json()["incident_opened"] is False
    assert second.json()["incident_opened"] is False
    assert third.json()["incident_opened"] is True


@pytest.mark.asyncio
async def test_recovery_closes_the_incident_and_records_a_duration():
    async with _client() as client:
        for _ in range(3):
            await client.post("/api/v1/report", json={"service_name": "svc", "status": "down"})
        recovered = await client.post(
            "/api/v1/report", json={"service_name": "svc", "status": "up"}
        )
        incidents = await client.get("/api/v1/incidents")
    assert recovered.json()["incident_closed"] is True
    listed = incidents.json()["incidents"]
    assert len(listed) == 1
    assert listed[0]["service"] == "svc"
    assert listed[0]["closed_at"] is not None
    assert listed[0]["duration_sec"] is not None


@pytest.mark.asyncio
async def test_status_reports_uptime_windows_and_latest_state():
    async with _client() as client:
        await client.post(
            "/api/v1/report",
            json={
                "service_name": "svc",
                "url": "https://svc.example.com",
                "status": "up",
                "latency_ms": 10,
            },
        )
        await client.post("/api/v1/report", json={"service_name": "svc", "status": "down"})
        response = await client.get("/api/v1/status")
    assert response.status_code == 200
    services = response.json()["services"]
    assert len(services) == 1
    status = services[0]
    assert status["service"] == "svc"
    assert status["url"] == "https://svc.example.com"
    assert status["status"] == "down"
    assert status["uptime_24h"] == 50.0
    assert status["uptime_7d"] == 50.0
    assert status["uptime_30d"] == 50.0
