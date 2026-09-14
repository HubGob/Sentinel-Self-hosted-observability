import asyncio
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.worker.processors import normalize_log
from sentinel.config import Settings
from sentinel.database import async_session
from sentinel.models import Log, Service
from sentinel.queue.redis_queue import RedisQueue

settings = Settings()
logger = logging.getLogger(__name__)


async def get_or_create_service(session: AsyncSession, name: str) -> Service:
    result = await session.execute(select(Service).where(Service.name == name))
    service: Service | None = result.scalar_one_or_none()
    if service is None:
        service = Service(name=name)
        session.add(service)
        await session.flush()
    service.last_seen_at = datetime.utcnow()
    return service


async def process_log(raw_log: dict[str, Any]) -> None:
    normalized = normalize_log(raw_log)
    async with async_session() as session:
        service = await get_or_create_service(session, normalized["service_name"])
        log = Log(
            service_id=service.id,
            timestamp=normalized["timestamp"],
            level=normalized["level"],
            message=normalized["message"],
            source=normalized["source"],
            container_id=normalized["container_id"],
            container_name=normalized["container_name"],
            raw=str(normalized["raw"]) if normalized["raw"] else None,
        )
        session.add(log)
        await session.commit()


async def run_worker() -> None:
    queue = RedisQueue()
    logger.info("Worker started")
    while True:
        item = queue.dequeue(timeout=int(settings.worker_poll_interval))
        if item:
            try:
                await process_log(item)
            except Exception as e:
                logger.error(f"Failed to process log: {e}")
        await asyncio.sleep(0.1)
