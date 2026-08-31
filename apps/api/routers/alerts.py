from fastapi import APIRouter, Query
from sqlalchemy import select, func

from sentinel.database import async_session
from sentinel.models import Alert
from sentinel.schemas.alert import AlertListResponse, AlertResponse

router = APIRouter(prefix="/api/v1", tags=["alerts"])


@router.get("/alerts", response_model=AlertListResponse)
async def list_alerts(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    service_id: str | None = None,
):
    async with async_session() as session:
        query = select(Alert).order_by(Alert.triggered_at.desc()).limit(limit).offset(offset)
        count_query = select(func.count(Alert.id))

        if service_id:
            query = query.where(Alert.service_id == service_id)
            count_query = count_query.where(Alert.service_id == service_id)

        result = await session.execute(query)
        alerts = result.scalars().all()

        total_result = await session.execute(count_query)
        total = total_result.scalar_one()

        return AlertListResponse(
            alerts=[AlertResponse.model_validate(a) for a in alerts],
            total=total,
            limit=limit,
            offset=offset,
        )
