from datetime import datetime
from pydantic import BaseModel


class LogResponse(BaseModel):
    id: str
    service_id: str
    timestamp: datetime
    level: str
    message: str
    source: str | None
    container_id: str | None
    container_name: str | None

    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    logs: list[LogResponse]
    total: int
    limit: int
    offset: int
