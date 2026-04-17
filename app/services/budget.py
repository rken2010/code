from collections import defaultdict

from sqlmodel import Session, select

from app.models.supply import Supply, SupplyItem, SupplyStage
from app.schemas.supply import BudgetSummaryItem


def partida_level3(code: str) -> str:
    parts = code.split(".")
    if len(parts) >= 3:
        return ".".join(parts[:3])
    return code


def get_budget_summary(session: Session) -> list[BudgetSummaryItem]:
    items = session.exec(select(SupplyItem, Supply).join(Supply, SupplyItem.supply_id == Supply.id)).all()

    totals = defaultdict(lambda: {"estimated": 0.0, "committed": 0.0, "paid": 0.0})

    for item, supply in items:
        partida = partida_level3(item.code)
        totals[partida]["estimated"] += item.estimated_cost

        if supply.current_stage in {
            SupplyStage.PURCHASE_ORDER,
            SupplyStage.DELIVERY_NOTE,
            SupplyStage.INVOICE,
            SupplyStage.PAYMENT_ORDER,
            SupplyStage.CLOSED,
        }:
            totals[partida]["committed"] += item.estimated_cost

        if supply.current_stage in {SupplyStage.PAYMENT_ORDER, SupplyStage.CLOSED}:
            totals[partida]["paid"] += item.estimated_cost

    return [
        BudgetSummaryItem(
            partida=partida,
            total_estimated=vals["estimated"],
            committed=vals["committed"],
            paid=vals["paid"],
        )
        for partida, vals in sorted(totals.items(), key=lambda x: x[0])
    ]
