"""uptime checks and incidents

Revision ID: 0002_uptime
Revises: 0001_initial
Create Date: 2026-09-14 00:00:00.000000

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_uptime"
down_revision: str | Sequence[str] | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("services", sa.Column("url", sa.String(500), nullable=True))

    op.create_table(
        "uptime_checks",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("service_id", sa.String(36), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("status", sa.String(8), nullable=False),
        sa.Column("latency_ms", sa.Integer, nullable=True),
        sa.Column("checked_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_uptime_checks_service_id", "uptime_checks", ["service_id"])
    op.create_index(
        "ix_uptime_checks_service_checked", "uptime_checks", ["service_id", "checked_at"]
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("service_id", sa.String(36), sa.ForeignKey("services.id"), nullable=False),
        sa.Column("opened_at", sa.DateTime, nullable=False),
        sa.Column("closed_at", sa.DateTime, nullable=True),
        sa.Column("duration_sec", sa.Integer, nullable=True),
    )
    op.create_index("ix_incidents_service_id", "incidents", ["service_id"])


def downgrade() -> None:
    op.drop_index("ix_incidents_service_id", table_name="incidents")
    op.drop_table("incidents")
    op.drop_index("ix_uptime_checks_service_checked", table_name="uptime_checks")
    op.drop_index("ix_uptime_checks_service_id", table_name="uptime_checks")
    op.drop_table("uptime_checks")
    op.drop_column("services", "url")
