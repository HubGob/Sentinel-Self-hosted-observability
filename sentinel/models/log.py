from datetime import datetime
from uuid import uuid4

from sqlalchemy import String, DateTime, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from sentinel.database import Base


class Log(Base):
    __tablename__ = "logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    service_id: Mapped[str] = mapped_column(String(36), ForeignKey("services.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=True)
    container_id: Mapped[str] = mapped_column(String(100), nullable=True)
    container_name: Mapped[str] = mapped_column(String(255), nullable=True)
    raw: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("ix_logs_service_timestamp", "service_id", "timestamp"),
    )
