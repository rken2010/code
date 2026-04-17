from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.models.supply import Supply, SupplyStage, SupplyTransition
from app.schemas.supply import AlertItem, DashboardKpi


def _last_movement_for_supply(session: Session, supply: Supply) -> datetime:
    transition = session.exec(
        select(SupplyTransition)
        .where(SupplyTransition.supply_id == supply.id)
        .order_by(SupplyTransition.created_at.desc())
    ).first()
    return transition.created_at if transition else supply.updated_at


def get_dashboard_kpis(session: Session, stale_days: int = 10) -> DashboardKpi:
    supplies = list(session.exec(select(Supply)).all())
    now = datetime.utcnow()

    total = len(supplies)
    closed = sum(1 for s in supplies if s.current_stage == SupplyStage.CLOSED)
    open_supplies = total - closed

    closed_supplies = [s for s in supplies if s.current_stage == SupplyStage.CLOSED]
    avg_cycle = 0.0
    if closed_supplies:
        avg_cycle = sum((s.updated_at - s.created_at).days for s in closed_supplies) / len(closed_supplies)

    overdue = 0
    for supply in supplies:
        last_movement = _last_movement_for_supply(session, supply)
        if now - last_movement > timedelta(days=stale_days):
            overdue += 1

    return DashboardKpi(
        total_supplies=total,
        open_supplies=open_supplies,
        closed_supplies=closed,
        avg_cycle_days_closed=round(avg_cycle, 2),
        overdue_without_movement=overdue,
    )


def get_stale_alerts(session: Session, stale_days: int = 10) -> list[AlertItem]:
    supplies = list(session.exec(select(Supply)).all())
    now = datetime.utcnow()
    alerts: list[AlertItem] = []

    for supply in supplies:
        last_movement = _last_movement_for_supply(session, supply)
        delta_days = (now - last_movement).days
        if delta_days > stale_days and supply.current_stage != SupplyStage.CLOSED:
            alerts.append(
                AlertItem(
                    supply_id=supply.id,
                    title=supply.title,
                    current_stage=supply.current_stage,
                    last_movement_at=last_movement,
                    days_without_movement=delta_days,
                )
            )

    return sorted(alerts, key=lambda x: x.days_without_movement, reverse=True)
