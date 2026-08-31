from datetime import datetime
from pydantic import BaseModel


class ServiceResponse(BaseModel):
    id: str
    name: str
    created_at: datetime
    last_seen_at: datetime | None

    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    services: list[ServiceResponse]
    total: int
