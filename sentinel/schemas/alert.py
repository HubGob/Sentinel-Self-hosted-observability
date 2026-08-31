from datetime import datetime
from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: str
    rule_id: str
    service_id: str
    triggered_at: datetime
    resolved_at: datetime | None
    value: float
    message: str

    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    limit: int
    offset: int
