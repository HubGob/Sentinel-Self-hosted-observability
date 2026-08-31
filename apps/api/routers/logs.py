from fastapi import APIRouter, Query
from sqlalchemy import select, func

from sentinel.database import async_session
from sentinel.models import Log
from sentinel.schemas.log import LogListResponse, LogResponse

router = APIRouter(prefix="/api/v1", tags=["logs"])


@router.get("/logs", response_model=LogListResponse)
async def list_logs(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service_id: str | None = None,
    level: str | None = None,
):
    async with async_session() as session:
        query = select(Log).order_by(Log.timestamp.desc()).limit(limit).offset(offset)
        count_query = select(func.count(Log.id))

        if service_id:
            query = query.where(Log.service_id == service_id)
            count_query = count_query.where(Log.service_id == service_id)
        if level:
            query = query.where(Log.level == level.upper())
            count_query = count_query.where(Log.level == level.upper())

        result = await session.execute(query)
        logs = result.scalars().all()

        total_result = await session.execute(count_query)
        total = total_result.scalar_one()

        return LogListResponse(
            logs=[LogResponse.model_validate(log) for log in logs],
            total=total,
            limit=limit,
            offset=offset,
        )
