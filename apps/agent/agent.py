import asyncio
import json
import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)

DOWN_STATUS_THRESHOLD = 500
CHECK_TIMEOUT_S = 5.0


def classify(status_code: int) -> str:
    """A service that answers at all is up; only server errors count as down."""
    return "down" if status_code >= DOWN_STATUS_THRESHOLD else "up"


def load_targets(raw: str) -> list[dict[str, str]]:
    """Parse the TARGETS env var: a JSON array of {"name": ..., "url": ...}."""
    if not raw.strip():
        return []
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("TARGETS must be a JSON array of {name, url} objects")
    return [{"name": str(item["name"]), "url": str(item["url"])} for item in data]


async def check_target(
    target: dict[str, str],
    client: httpx.AsyncClient | None = None,
) -> dict[str, Any]:
    """Probe one URL and return the report payload for it."""
    started = time.monotonic()
    try:
        if client is None:
            async with httpx.AsyncClient(
                timeout=CHECK_TIMEOUT_S, follow_redirects=True
            ) as owned_client:
                response = await owned_client.get(target["url"])
        else:
            response = await client.get(target["url"])
    except Exception as exc:  # noqa: BLE001 - any transport failure means down
        logger.warning("check failed for %s: %s", target.get("name"), exc)
        return {
            "service_name": target["name"],
            "url": target["url"],
            "status": "down",
            "latency_ms": None,
        }
    return {
        "service_name": target["name"],
        "url": target["url"],
        "status": classify(response.status_code),
        "latency_ms": int((time.monotonic() - started) * 1000),
    }


async def run_checks_once(
    targets: list[dict[str, str]],
    collector_url: str,
    client: httpx.AsyncClient | None = None,
) -> list[dict[str, Any]]:
    """Check every target and report each result to the collector API."""
    results: list[dict[str, Any]] = []
    owns_client = client is None
    active = client or httpx.AsyncClient(timeout=CHECK_TIMEOUT_S, follow_redirects=True)
    try:
        for target in targets:
            result = await check_target(target, client=active)
            results.append(result)
            try:
                await active.post(f"{collector_url}/api/v1/report", json=result)
            except Exception as exc:  # noqa: BLE001 - one bad report must not stop the sweep
                logger.warning("report failed for %s: %s", target.get("name"), exc)
    finally:
        if owns_client:
            await active.aclose()
    return results


async def run_forever() -> None:
    collector_url = os.environ.get("COLLECTOR_URL", "http://localhost:8000")
    interval = float(os.environ.get("CHECK_INTERVAL_S", "60"))
    targets = load_targets(os.environ.get("TARGETS", "[]"))
    if not targets:
        logger.warning("no TARGETS configured - agent will idle")
    while True:
        if targets:
            await run_checks_once(targets, collector_url)
        await asyncio.sleep(interval)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_forever())
