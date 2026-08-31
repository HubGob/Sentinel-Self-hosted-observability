import asyncio
import json
import logging
import re
from datetime import datetime

import httpx

from sentinel.config import Settings

settings = Settings()
logger = logging.getLogger(__name__)

LOG_PATTERN = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?\s*"
    r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)?\s*"
    r"(?P<message>.*)$",
    re.IGNORECASE,
)


def parse_docker_log(line: str, container_name: str, container_id: str) -> dict:
    match = LOG_PATTERN.match(line.strip())
    if match:
        groups = match.groupdict()
        level = (groups.get("level") or "INFO").upper()
        timestamp_str = groups.get("timestamp")
        if timestamp_str:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        else:
            timestamp = datetime.utcnow()
        return {
            "service_name": container_name,
            "timestamp": timestamp.isoformat(),
            "level": level,
            "message": groups.get("message", line),
            "container_id": container_id,
            "container_name": container_name,
            "raw": line,
        }
    return {
        "service_name": container_name,
        "timestamp": datetime.utcnow().isoformat(),
        "level": "INFO",
        "message": line,
        "container_id": container_id,
        "container_name": container_name,
        "raw": line,
    }


async def send_to_api(log_entry: dict):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://api:8000/api/v1/ingest",
                json=log_entry,
                timeout=5.0,
            )
        except Exception as e:
            logger.error(f"Failed to send log: {e}")


async def collect_logs():
    import docker
    client = docker.from_env()
    containers = client.containers.list()

    for container in containers:
        name = container.name or "unknown"
        cid = container.short_id or "unknown"
        logs = container.logs(stream=True, follow=True, tail=100)
        for line in logs:
            log_entry = parse_docker_log(
                line.decode("utf-8", errors="replace").strip(),
                name,
                cid,
            )
            await send_to_api(log_entry)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(collect_logs())
