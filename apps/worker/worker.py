import asyncio
import logging
from datetime import datetime

from sentinel.config import Settings
from sentinel.database import async_session
from sentinel.models import Service, Log
from sentinel.queue.redis_queue import RedisQueue
from sentinel.worker.processors import normalize_log

settings = Settings()
logger = logging.getLogger(__name__)


async def get_or_create_service(session, name: str) -> Service:
    from sqlalchemy import select
    result = await session.execute(select(Service).where(Service.name == name))
    service = result.scalar_one_or_none()
    if not service:
        service = Service(name=name)
        session.add(service)
        await session.flush()
    service.last_seen_at = datetime.utcnow()
    return service


async def process_log(raw_log: dict) -> None:
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


async def run_worker():
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
