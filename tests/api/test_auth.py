"""Tests for the auth endpoints and the gate they put in front of the API."""

import pytest
from httpx import ASGITransport, AsyncClient

from apps.api.main import app

EMAIL = "owner@example.com"
PASSWORD = "correct-horse-battery"

GATED_PATHS = ["/api/v1/services", "/api/v1/alerts", "/api/v1/logs"]


def _client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


async def _register(client: AsyncClient, email: str = EMAIL, password: str = PASSWORD) -> dict:
    response = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    return response.json()


def _bearer(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def test_register_returns_an_access_and_refresh_token() -> None:
    async with _client() as client:
        tokens = await _register(client)

    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]


async def test_registering_the_same_email_twice_conflicts() -> None:
    async with _client() as client:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/register", json={"email": EMAIL, "password": PASSWORD}
        )

    assert response.status_code == 409


async def test_register_normalises_the_email_case() -> None:
    async with _client() as client:
        await _register(client, email="Owner@Example.com")
        response = await client.post(
            "/api/v1/auth/login", json={"email": "owner@example.com", "password": PASSWORD}
        )

    assert response.status_code == 200


@pytest.mark.parametrize("password", ["", "short"])
async def test_register_rejects_a_password_below_the_minimum(password: str) -> None:
    async with _client() as client:
        response = await client.post(
            "/api/v1/auth/register", json={"email": EMAIL, "password": password}
        )

    assert response.status_code == 422


async def test_register_rejects_a_malformed_email() -> None:
    async with _client() as client:
        response = await client.post(
            "/api/v1/auth/register", json={"email": "not-an-email", "password": PASSWORD}
        )

    assert response.status_code == 422


async def test_login_succeeds_with_the_right_password() -> None:
    async with _client() as client:
        await _register(client)
        response = await client.post(
            "/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD}
        )

    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_login_failure_does_not_reveal_whether_the_account_exists() -> None:
    """A wrong password and an unknown address must be indistinguishable."""
    async with _client() as client:
        await _register(client)
        wrong_password = await client.post(
            "/api/v1/auth/login", json={"email": EMAIL, "password": "definitely-wrong"}
        )
        unknown_email = await client.post(
            "/api/v1/auth/login", json={"email": "nobody@example.com", "password": PASSWORD}
        )

    assert wrong_password.status_code == 401
    assert unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()


async def test_refresh_exchanges_a_refresh_token_for_a_new_access_token() -> None:
    async with _client() as client:
        tokens = await _register(client)
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
        )

    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_refresh_rejects_an_access_token() -> None:
    async with _client() as client:
        tokens = await _register(client)
        response = await client.post(
            "/api/v1/auth/refresh", json={"refresh_token": tokens["access_token"]}
        )

    assert response.status_code == 401


@pytest.mark.parametrize("path", GATED_PATHS)
async def test_read_routers_require_a_token(path: str) -> None:
    async with _client() as client:
        response = await client.get(path)

    assert response.status_code == 401


@pytest.mark.parametrize("path", GATED_PATHS)
async def test_a_valid_token_unlocks_the_read_routers(path: str) -> None:
    async with _client() as client:
        tokens = await _register(client)
        response = await client.get(path, headers=_bearer(tokens))

    assert response.status_code == 200


@pytest.mark.parametrize("header", ["", "Bearer", "Bearer ", "Basic abc", "Bearer not.a.token"])
async def test_malformed_authorization_headers_are_rejected(header: str) -> None:
    async with _client() as client:
        response = await client.get("/api/v1/services", headers={"Authorization": header})

    assert response.status_code == 401


@pytest.mark.parametrize("path", ["/api/v1/status", "/health", "/ready"])
async def test_public_endpoints_stay_reachable_without_a_token(path: str) -> None:
    async with _client() as client:
        response = await client.get(path)

    assert response.status_code == 200
