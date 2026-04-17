from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.supply import Memo, Provider, Supply, SupplyItem, SupplyTransition
from app.schemas.supply import (
    AlertItem,
    BudgetSummaryItem,
    DashboardKpi,
    FileUploadResponse,
    MemoCreate,
    MemoRead,
    ProviderCreate,
    ProviderRead,
    SupplyCreate,
    SupplyItemCreate,
    SupplyItemRead,
    SupplyRead,
    SupplyTransitionCreate,
    SupplyTransitionRead,
)
from app.services.budget import get_budget_summary
from app.services.dashboard import get_dashboard_kpis, get_stale_alerts
from app.services.files import (
    base_storage_dir,
    memo_folder_name,
    save_upload_to_folder,
    supply_folder_name,
)

router = APIRouter()


@router.post("/providers", response_model=ProviderRead, status_code=201)
def create_provider(payload: ProviderCreate, session: Session = Depends(get_session)) -> Provider:
    provider = Provider(**payload.model_dump())
    session.add(provider)
    session.commit()
    session.refresh(provider)
    return provider


@router.get("/providers", response_model=list[ProviderRead])
def list_providers(session: Session = Depends(get_session)) -> list[Provider]:
    return list(session.exec(select(Provider).order_by(Provider.business_name)).all())


@router.post("/memos", response_model=MemoRead, status_code=201)
def create_memo(payload: MemoCreate, session: Session = Depends(get_session)) -> Memo:
    memo = Memo(**payload.model_dump())
    session.add(memo)
    session.commit()
    session.refresh(memo)
    return memo


@router.get("/memos", response_model=list[MemoRead])
def list_memos(session: Session = Depends(get_session)) -> list[Memo]:
    return list(session.exec(select(Memo).order_by(Memo.id.desc())).all())


@router.post("/supplies", response_model=SupplyRead, status_code=201)
def create_supply(payload: SupplyCreate, session: Session = Depends(get_session)) -> Supply:
    if payload.provider_id is not None and session.get(Provider, payload.provider_id) is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

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
    supply.updated_at = datetime.utcnow()

    session.add(item)
    session.add(supply)
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
    supply.updated_at = datetime.utcnow()

    session.add(transition)
    session.add(supply)
    session.commit()
    session.refresh(transition)
    return transition


@router.post("/supplies/{supply_id}/files", response_model=FileUploadResponse, status_code=201)
def upload_supply_file(
    supply_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> FileUploadResponse:
    supply = session.get(Supply, supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Suministro no encontrado")

    folder = base_storage_dir() / "suministros" / Path(supply_folder_name(supply.id, supply.description))
    stored_path = save_upload_to_folder(folder=folder, uploaded_file=file)

    return FileUploadResponse(message="Archivo guardado", path=stored_path)


@router.post("/memos/{memo_id}/files", response_model=FileUploadResponse, status_code=201)
def upload_memo_file(
    memo_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> FileUploadResponse:
    memo = session.get(Memo, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Memo no encontrado")

    folder = base_storage_dir() / "memos" / Path(memo_folder_name(memo.number, memo.description))
    stored_path = save_upload_to_folder(folder=folder, uploaded_file=file)

    return FileUploadResponse(message="Archivo guardado", path=stored_path)


@router.get("/budget/summary", response_model=list[BudgetSummaryItem])
def budget_summary(session: Session = Depends(get_session)) -> list[BudgetSummaryItem]:
    return get_budget_summary(session)


@router.get("/dashboard/kpis", response_model=DashboardKpi)
def dashboard_kpis(
    stale_days: int = Query(default=10, ge=1, le=90),
    session: Session = Depends(get_session),
) -> DashboardKpi:
    return get_dashboard_kpis(session=session, stale_days=stale_days)


@router.get("/dashboard/alerts", response_model=list[AlertItem])
def dashboard_alerts(
    stale_days: int = Query(default=10, ge=1, le=90),
    session: Session = Depends(get_session),
) -> list[AlertItem]:
    return get_stale_alerts(session=session, stale_days=stale_days)
