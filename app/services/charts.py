from collections import defaultdict
from datetime import date

from sqlmodel import Session, select

from app.models.supply import Supply, SupplyItem
from app.schemas.workflow import DashboardChartData


def get_chart_data(
    session: Session,
    executing_unit: str | None = None,
    requester_dependency: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> DashboardChartData:
    query = select(Supply)
    if executing_unit:
        query = query.where(Supply.executing_unit == executing_unit)
    if requester_dependency:
        query = query.where(Supply.requester_dependency == requester_dependency)
    if date_from:
        query = query.where(Supply.date >= date_from)
    if date_to:
        query = query.where(Supply.date <= date_to)

    supplies = list(session.exec(query).all())
    supply_ids = [s.id for s in supplies if s.id is not None]

    stage_counts = defaultdict(int)
    monthly_totals = defaultdict(float)

    for supply in supplies:
        stage_counts[supply.current_stage.value] += 1
        monthly_totals[supply.date.strftime("%Y-%m")] += 0.0

    if supply_ids:
        items = list(session.exec(select(SupplyItem).where(SupplyItem.supply_id.in_(supply_ids))).all())
        by_supply = defaultdict(float)
        for item in items:
            by_supply[item.supply_id] += item.estimated_cost

        for supply in supplies:
            monthly_totals[supply.date.strftime("%Y-%m")] += by_supply.get(supply.id, 0.0)

    return DashboardChartData(stage_counts=dict(stage_counts), monthly_totals=dict(monthly_totals))
