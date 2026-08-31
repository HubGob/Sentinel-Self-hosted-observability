from datetime import datetime
from pydantic import BaseModel, Field


class LogIngest(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=255)
    timestamp: datetime
    level: str = Field(..., pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    message: str = Field(..., min_length=1)
    source: str | None = None
    container_id: str | None = None
    container_name: str | None = None
    raw: str | None = None


class IngestResponse(BaseModel):
    accepted: int
