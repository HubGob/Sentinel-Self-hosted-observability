"""Outbound notifications for incident open/close.

A no-op when DISCORD_WEBHOOK_URL is unset, so the app works without it and
tests never touch the network.
"""

import logging
from typing import Any

import httpx

from sentinel.config import settings

logger = logging.getLogger(__name__)

RED = 0xE74C3C
GREEN = 0x2ECC71


def build_payload(service_name: str, opened: bool, url: str | None = None) -> dict[str, Any]:
    """Discord webhook body for one incident transition."""
    return {
        "embeds": [
            {
                "title": f"{service_name} is {'DOWN' if opened else 'UP'}",
                "description": url or "",
                "color": RED if opened else GREEN,
            }
        ]
    }


async def notify_incident(service_name: str, opened: bool, url: str | None = None) -> bool:
    """Post an incident transition. Returns True only on a confirmed 2xx.

    Never raises: a failing webhook must not fail the report that triggered it.
    """
    webhook = settings.discord_webhook_url
    if not webhook:
        return False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(webhook, json=build_payload(service_name, opened, url))
            response.raise_for_status()
        return True
    except Exception as exc:  # noqa: BLE001 - notification must never break ingestion
        logger.warning("Discord notification failed for %s: %s", service_name, exc)
        return False
