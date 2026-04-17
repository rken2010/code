from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.supply import Supply, SupplyItem, SupplyTransition
from app.schemas.supply import (
    BudgetSummaryItem,
    SupplyCreate,
    SupplyItemCreate,
    SupplyItemRead,
    SupplyRead,
    SupplyTransitionCreate,
    SupplyTransitionRead,
)
from app.services.budget import get_budget_summary

router = APIRouter()


@router.post("/supplies", response_model=SupplyRead, status_code=201)
def create_supply(payload: SupplyCreate, session: Session = Depends(get_session)) -> Supply:
    supply = Supply(**payload.model_dump())
    session.add(supply)
    session.commit()
    session.refresh(supply)
    return supply


@router.get("/supplies", response_model=list[SupplyRead])
def list_supplies(session: Session = Depends(get_session)) -> list[Supply]:
    return list(session.exec(select(Supply).order_by(Supply.id.desc())).all())


@router.get("/supplies/{supply_id}", response_model=SupplyRead)
def get_supply(supply_id: int, session: Session = Depends(get_session)) -> Supply:
    supply = session.get(Supply, supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Suministro no encontrado")
    return supply


@router.post("/supplies/{supply_id}/items", response_model=SupplyItemRead, status_code=201)
def add_item(
    supply_id: int,
    payload: SupplyItemCreate,
    session: Session = Depends(get_session),
) -> SupplyItem:
    supply = session.get(Supply, supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Suministro no encontrado")

    estimated_cost = payload.quantity * payload.unit_cost
    item = SupplyItem(
        supply_id=supply_id,
        **payload.model_dump(),
        estimated_cost=estimated_cost,
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.post("/supplies/{supply_id}/transitions", response_model=SupplyTransitionRead, status_code=201)
def transition_supply(
    supply_id: int,
    payload: SupplyTransitionCreate,
    session: Session = Depends(get_session),
) -> SupplyTransition:
    supply = session.get(Supply, supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Suministro no encontrado")

    transition = SupplyTransition(
        supply_id=supply_id,
        from_stage=supply.current_stage,
        to_stage=payload.to_stage,
        document_number=payload.document_number,
        document_date=payload.document_date,
        notes=payload.notes,
    )
    supply.current_stage = payload.to_stage

    session.add(transition)
    session.add(supply)
    session.commit()
    session.refresh(transition)
    return transition


@router.get("/budget/summary", response_model=list[BudgetSummaryItem])
def budget_summary(session: Session = Depends(get_session)) -> list[BudgetSummaryItem]:
    return get_budget_summary(session)
