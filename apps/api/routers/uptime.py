from collections.abc import Sequence
from datetime import datetime

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field
from sqlalchemy import select

from sentinel.database import async_session
from sentinel.models import Incident, Service, UptimeCheck
from sentinel.notify import notify_incident

router = APIRouter(prefix="/api/v1", tags=["uptime"])

CONSECUTIVE_FAILURES = 3
DAY = 86400


class ReportIn(BaseModel):
    service_name: str = Field(..., min_length=1, max_length=255)
    url: str | None = None
    status: str = Field(..., pattern="^(up|down)$")
    latency_ms: int | None = None
    checked_at: datetime | None = None


class ReportOut(BaseModel):
    accepted: int
    incident_opened: bool = False
    incident_closed: bool = False


class ServiceStatus(BaseModel):
    service: str
    url: str | None
    status: str
    latency_ms: int | None
    uptime_24h: float
    uptime_7d: float
    uptime_30d: float
    last_checked_at: datetime | None


class StatusResponse(BaseModel):
    services: list[ServiceStatus]


class IncidentOut(BaseModel):
    id: str
    service: str
    opened_at: datetime
    closed_at: datetime | None
    duration_sec: int | None


class IncidentListResponse(BaseModel):
    incidents: list[IncidentOut]


def uptime_percentage(checks: Sequence[UptimeCheck], now: datetime, window_seconds: int) -> float:
    """Percentage of checks in the window that reported 'up'. 100.0 when there is no data."""
    recent = [c for c in checks if (now - c.checked_at).total_seconds() <= window_seconds]
    if not recent:
        return 100.0
    return round(100 * sum(1 for c in recent if c.status == "up") / len(recent), 2)


@router.post("/report", response_model=ReportOut)
async def report(body: ReportIn) -> ReportOut:
    now = body.checked_at or datetime.utcnow()
    async with async_session() as session:
        service = (
            await session.execute(select(Service).where(Service.name == body.service_name))
        ).scalar_one_or_none()
        if service is None:
            service = Service(name=body.service_name)
            session.add(service)
            await session.flush()
        if body.url:
            service.url = body.url
        service.last_seen_at = now

        session.add(
            UptimeCheck(
                service_id=service.id,
                status=body.status,
                latency_ms=body.latency_ms,
                checked_at=now,
            )
        )
        await session.flush()

        opened = False
        closed = False
        if body.status == "down":
            recent = (
                (
                    await session.execute(
                        select(UptimeCheck.status)
                        .where(UptimeCheck.service_id == service.id)
                        .order_by(UptimeCheck.checked_at.desc())
                        .limit(CONSECUTIVE_FAILURES)
                    )
                )
                .scalars()
                .all()
            )
            active = (
                (
                    await session.execute(
                        select(Incident).where(
                            Incident.service_id == service.id, Incident.closed_at.is_(None)
                        )
                    )
                )
                .scalars()
                .first()
            )
            fails = len(recent) >= CONSECUTIVE_FAILURES and all(s == "down" for s in recent)
            if fails and active is None:
                session.add(Incident(service_id=service.id, opened_at=now))
                opened = True
        else:
            for incident in (
                (
                    await session.execute(
                        select(Incident).where(
                            Incident.service_id == service.id, Incident.closed_at.is_(None)
                        )
                    )
                )
                .scalars()
                .all()
            ):
                incident.closed_at = now
                incident.duration_sec = int((now - incident.opened_at).total_seconds())
                closed = True

        await session.commit()
    if opened or closed:
        await notify_incident(body.service_name, opened=opened, url=body.url)
    return ReportOut(accepted=1, incident_opened=opened, incident_closed=closed)


@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    now = datetime.utcnow()
    async with async_session() as session:
        services = (await session.execute(select(Service).order_by(Service.name))).scalars().all()
        out: list[ServiceStatus] = []
        for service in services:
            checks = (
                (
                    await session.execute(
                        select(UptimeCheck)
                        .where(UptimeCheck.service_id == service.id)
                        .order_by(UptimeCheck.checked_at.desc())
                        .limit(1000)
                    )
                )
                .scalars()
                .all()
            )
            last = checks[0] if checks else None
            out.append(
                ServiceStatus(
                    service=service.name,
                    url=service.url,
                    status=last.status if last else "unknown",
                    latency_ms=last.latency_ms if last else None,
                    uptime_24h=uptime_percentage(checks, now, DAY),
                    uptime_7d=uptime_percentage(checks, now, 7 * DAY),
                    uptime_30d=uptime_percentage(checks, now, 30 * DAY),
                    last_checked_at=last.checked_at if last else None,
                )
            )
    return StatusResponse(services=out)


@router.get("/incidents", response_model=IncidentListResponse)
async def list_incidents(limit: int = Query(20, ge=1, le=200)) -> IncidentListResponse:
    async with async_session() as session:
        incidents = (
            (
                await session.execute(
                    select(Incident).order_by(Incident.opened_at.desc()).limit(limit)
                )
            )
            .scalars()
            .all()
        )
        names: dict[str, str] = {}
        if incidents:
            rows = (
                await session.execute(
                    select(Service.id, Service.name).where(
                        Service.id.in_([i.service_id for i in incidents])
                    )
                )
            ).all()
            names = {service_id: name for service_id, name in rows}
    return IncidentListResponse(
        incidents=[
            IncidentOut(
                id=i.id,
                service=names.get(i.service_id, "unknown"),
                opened_at=i.opened_at,
                closed_at=i.closed_at,
                duration_sec=i.duration_sec,
            )
            for i in incidents
        ]
    )
