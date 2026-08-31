from fastapi import APIRouter
from sqlalchemy import select, func

from sentinel.database import async_session
from sentinel.models import Service
from sentinel.schemas.service import ServiceListResponse, ServiceResponse

router = APIRouter(prefix="/api/v1", tags=["services"])


@router.get("/services", response_model=ServiceListResponse)
async def list_services():
    async with async_session() as session:
        result = await session.execute(select(Service).order_by(Service.name))
        services = result.scalars().all()

        count_result = await session.execute(select(func.count(Service.id)))
        total = count_result.scalar_one()

        return ServiceListResponse(
            services=[ServiceResponse.model_validate(s) for s in services],
            total=total,
        )
