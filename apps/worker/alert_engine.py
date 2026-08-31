import logging
from datetime import datetime, timedelta

from sqlalchemy import select, func

from sentinel.database import async_session
from sentinel.models import Alert, AlertRule, AlertRuleType, Log

logger = logging.getLogger(__name__)


def evaluate_error_count(count: int, threshold: float) -> bool:
    return count > threshold


def evaluate_error_rate(rate: float, threshold: float) -> bool:
    return rate > threshold


async def evaluate_rules():
    """Evaluate all enabled alert rules."""
    async with async_session() as session:
        result = await session.execute(
            select(AlertRule).where(AlertRule.enabled == True)
        )
        rules = result.scalars().all()

        for rule in rules:
            await evaluate_rule(session, rule)


async def evaluate_rule(session, rule: AlertRule):
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=rule.window_seconds)

    query = select(func.count(Log.id)).where(
        Log.timestamp >= window_start,
        Log.level == "ERROR",
    )

    if rule.service_name:
        from sentinel.models import Service
        service_result = await session.execute(
            select(Service.id).where(Service.name == rule.service_name)
        )
        service_id = service_result.scalar_one_or_none()
        if not service_id:
            return
        query = query.where(Log.service_id == service_id)

    result = await session.execute(query)
    count = result.scalar_one()

    if rule.rule_type == AlertRuleType.ERROR_COUNT:
        triggered = evaluate_error_count(count, rule.threshold)
    elif rule.rule_type == AlertRuleType.ERROR_RATE:
        rate = count / rule.window_seconds
        triggered = evaluate_error_rate(rate, rule.threshold)
    else:
        return

    if triggered:
        from sentinel.models import Service
        service_query = select(Service.id)
        if rule.service_name:
            service_query = service_query.where(Service.name == rule.service_name)
        service_result = await session.execute(service_query)
        service_id = service_result.scalar_one_or_none()

        alert = Alert(
            rule_id=rule.rule_id if hasattr(rule, 'rule_id') else rule.id,
            service_id=service_id or "",
            value=float(count),
            message=f"Alert: {rule.name} triggered (value: {count})",
        )
        session.add(alert)
        await session.commit()
        logger.info(f"Alert triggered: {rule.name}")
