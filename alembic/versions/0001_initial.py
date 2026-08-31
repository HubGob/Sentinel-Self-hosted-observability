"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("last_seen_at", sa.DateTime, nullable=True),
    )
    op.create_index("ix_services_name", "services", ["name"])

    op.create_table(
        "logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("service_id", sa.String(36), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime, nullable=False),
        sa.Column("level", sa.String(20), nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("source", sa.String(50), nullable=True),
        sa.Column("container_id", sa.String(100), nullable=True),
        sa.Column("container_name", sa.String(255), nullable=True),
        sa.Column("raw", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_logs_service_id", "logs", ["service_id"])
    op.create_index("ix_logs_timestamp", "logs", ["timestamp"])
    op.create_index("ix_logs_level", "logs", ["level"])
    op.create_index("ix_logs_service_timestamp", "logs", ["service_id", "timestamp"])

    op.create_table(
        "alert_rules",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("service_name", sa.String(255), nullable=True),
        sa.Column("rule_type", sa.Enum("error_count", "error_rate", name="alertruletype"), nullable=False),
        sa.Column("threshold", sa.Float, nullable=False),
        sa.Column("window_seconds", sa.Integer, nullable=False, default=60),
        sa.Column("enabled", sa.Boolean, nullable=False, default=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rule_id", sa.String(36), sa.ForeignKey("alert_rules.id"), nullable=False),
        sa.Column("service_id", sa.String(36), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("triggered_at", sa.DateTime, nullable=False),
        sa.Column("resolved_at", sa.DateTime, nullable=True),
        sa.Column("value", sa.Float, nullable=False),
        sa.Column("message", sa.Text, nullable=False),
    )
    op.create_index("ix_alerts_service_triggered", "alerts", ["service_id", "triggered_at"])


def downgrade() -> None:
    op.drop_table("alerts")
    op.drop_table("alert_rules")
    op.drop_table("logs")
    op.drop_table("services")
