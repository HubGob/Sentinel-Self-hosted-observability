from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, Float, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from sentinel.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    rule_id: Mapped[str] = mapped_column(String(36), ForeignKey("alert_rules.id"), nullable=False)
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), nullable=False)
    triggered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        Index("ix_alerts_service_triggered", "service_id", "triggered_at"),
    )
