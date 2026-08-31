from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, Integer, Float, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from sentinel.database import Base


class AlertRuleType(str, enum.Enum):
    ERROR_COUNT = "error_count"
    ERROR_RATE = "error_rate"


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    service_name: Mapped[str] = mapped_column(String(255), nullable=True)
    rule_type: Mapped[AlertRuleType] = mapped_column(SAEnum(AlertRuleType), nullable=False)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    window_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
