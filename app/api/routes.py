from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.supply import Memo, Provider, Supply, SupplyItem, SupplyTransition
from app.models.workflow import (
    AuditLog,
    Expediente,
    ExpedienteMovement,
    ProviderContact,
    Task,
    User,
    UserRole,
)
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
from app.schemas.workflow import (
    AuditLogRead,
    DashboardChartData,
    ExpedienteCreate,
    ExpedienteMovementCreate,
    ExpedienteMovementRead,
    ExpedienteRead,
    ImportResult,
    PdfPreview,
    ProviderContactCreate,
    ProviderContactRead,
    ProviderHistoryItem,
    TaskCreate,
    TaskRead,
    TaskStatusUpdate,
    UserCreate,
    UserRead,
)
from app.services.audit import log_audit
from app.services.auth import require_roles
from app.services.budget import get_budget_summary
from app.services.charts import get_chart_data
from app.services.dashboard import get_dashboard_kpis, get_stale_alerts
from app.services.files import (
    base_storage_dir,
    memo_folder_name,
    save_upload_to_folder,
    supply_folder_name,
)
from app.services.imports import parse_excel_rows, parse_mapping, parse_pdf_preview

router = APIRouter()


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(
    payload: UserCreate,
    auth=Depends(require_roles({UserRole.ADMIN})),
    session: Session = Depends(get_session),
) -> User:
    user = User(**payload.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)
    log_audit(session, auth[0], auth[1], "create", "user", user.id, user.username)
    return user


@router.get("/audit/logs", response_model=list[AuditLogRead])
def list_audit_logs(
    limit: int = Query(default=200, ge=1, le=1000),
    _: tuple[str, str] = Depends(require_roles({UserRole.ADMIN})),
    session: Session = Depends(get_session),
) -> list[AuditLog]:
    return list(session.exec(select(AuditLog).order_by(AuditLog.id.desc()).limit(limit)).all())


@router.post("/providers", response_model=ProviderRead, status_code=201)
def create_provider(
    payload: ProviderCreate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
    session: Session = Depends(get_session),
) -> Provider:
    provider = Provider(**payload.model_dump())
    session.add(provider)
    session.commit()
    session.refresh(provider)
    log_audit(session, auth[0], auth[1], "create", "provider", provider.id, provider.business_name)
    return provider


@router.get("/providers", response_model=list[ProviderRead])
def list_providers(session: Session = Depends(get_session)) -> list[Provider]:
    return list(session.exec(select(Provider).order_by(Provider.business_name)).all())


@router.post("/providers/{provider_id}/contacts", response_model=ProviderContactRead, status_code=201)
def add_provider_contact(
    provider_id: int,
    payload: ProviderContactCreate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
    session: Session = Depends(get_session),
) -> ProviderContact:
    if session.get(Provider, provider_id) is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    contact = ProviderContact(provider_id=provider_id, **payload.model_dump())
    session.add(contact)
    session.commit()
    session.refresh(contact)
    log_audit(session, auth[0], auth[1], "create", "provider_contact", contact.id, payload.name)
    return contact


@router.get("/providers/{provider_id}/contacts", response_model=list[ProviderContactRead])
def list_provider_contacts(provider_id: int, session: Session = Depends(get_session)) -> list[ProviderContact]:
    return list(session.exec(select(ProviderContact).where(ProviderContact.provider_id == provider_id)).all())


@router.get("/providers/{provider_id}/history", response_model=list[ProviderHistoryItem])
def provider_history(provider_id: int, session: Session = Depends(get_session)) -> list[ProviderHistoryItem]:
    supplies = list(session.exec(select(Supply).where(Supply.provider_id == provider_id)).all())
    result: list[ProviderHistoryItem] = []
    for supply in supplies:
        items = list(session.exec(select(SupplyItem).where(SupplyItem.supply_id == supply.id)).all())
        result.append(
            ProviderHistoryItem(
                supply_id=supply.id,
                title=supply.title,
                stage=supply.current_stage.value,
                total_estimated=sum(i.estimated_cost for i in items),
                created_at=supply.created_at,
            )
        )
    return result


@router.post("/memos", response_model=MemoRead, status_code=201)
def create_memo(
    payload: MemoCreate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
    session: Session = Depends(get_session),
) -> Memo:
    memo = Memo(**payload.model_dump())
    session.add(memo)
    session.commit()
    session.refresh(memo)
    log_audit(session, auth[0], auth[1], "create", "memo", memo.id, memo.number)
    return memo


@router.get("/memos", response_model=list[MemoRead])
def list_memos(session: Session = Depends(get_session)) -> list[Memo]:
    return list(session.exec(select(Memo).order_by(Memo.id.desc())).all())


@router.post("/expedientes", response_model=ExpedienteRead, status_code=201)
def create_expediente(
    payload: ExpedienteCreate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
    session: Session = Depends(get_session),
) -> Expediente:
    exp = Expediente(**payload.model_dump())
    session.add(exp)
    session.commit()
    session.refresh(exp)
    log_audit(session, auth[0], auth[1], "create", "expediente", exp.id, exp.code)
    return exp


@router.get("/expedientes", response_model=list[ExpedienteRead])
def list_expedientes(session: Session = Depends(get_session)) -> list[Expediente]:
    return list(session.exec(select(Expediente).order_by(Expediente.id.desc())).all())


@router.post("/expedientes/{expediente_id}/movements", response_model=ExpedienteMovementRead, status_code=201)
def move_expediente(
    expediente_id: int,
    payload: ExpedienteMovementCreate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
    session: Session = Depends(get_session),
) -> ExpedienteMovement:
    exp = session.get(Expediente, expediente_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")

    movement = ExpedienteMovement(expediente_id=expediente_id, **payload.model_dump())
    exp.current_office = payload.office
    exp.current_office_since = payload.moved_at

    session.add(movement)
    session.add(exp)
    session.commit()
    session.refresh(movement)
    log_audit(session, auth[0], auth[1], "move", "expediente", exp.id, payload.office)
    return movement


@router.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(
    payload: TaskCreate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS, UserRole.TESORERIA})),
    session: Session = Depends(get_session),
) -> Task:
    task = Task(**payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    log_audit(session, auth[0], auth[1], "create", "task", task.id, task.title)
    return task


@router.get("/tasks", response_model=list[TaskRead])
def list_tasks(status: str | None = None, session: Session = Depends(get_session)) -> list[Task]:
    query = select(Task).order_by(Task.id.desc())
    if status:
        query = query.where(Task.status == status)
    return list(session.exec(query).all())


@router.patch("/tasks/{task_id}/status", response_model=TaskRead)
def update_task_status(
    task_id: int,
    payload: TaskStatusUpdate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS, UserRole.TESORERIA})),
    session: Session = Depends(get_session),
) -> Task:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")

    task.status = payload.status
    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    log_audit(session, auth[0], auth[1], "update_status", "task", task.id, payload.status.value)
    return task


@router.post("/supplies", response_model=SupplyRead, status_code=201)
def create_supply(
    payload: SupplyCreate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
    session: Session = Depends(get_session),
) -> Supply:
    if payload.provider_id is not None and session.get(Provider, payload.provider_id) is None:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")

    supply = Supply(**payload.model_dump())
    session.add(supply)
    session.commit()
    session.refresh(supply)
    log_audit(session, auth[0], auth[1], "create", "supply", supply.id, supply.title)
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
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
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
    log_audit(session, auth[0], auth[1], "create", "supply_item", item.id, item.code)
    return item


@router.post("/supplies/{supply_id}/transitions", response_model=SupplyTransitionRead, status_code=201)
def transition_supply(
    supply_id: int,
    payload: SupplyTransitionCreate,
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
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
    log_audit(session, auth[0], auth[1], "transition", "supply", supply.id, payload.to_stage.value)
    return transition


@router.post("/supplies/{supply_id}/files", response_model=FileUploadResponse, status_code=201)
def upload_supply_file(
    supply_id: int,
    file: UploadFile = File(...),
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS, UserRole.TESORERIA})),
    session: Session = Depends(get_session),
) -> FileUploadResponse:
    supply = session.get(Supply, supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Suministro no encontrado")

    folder = base_storage_dir() / "suministros" / Path(supply_folder_name(supply.id, supply.description))
    stored_path = save_upload_to_folder(folder=folder, uploaded_file=file)
    log_audit(session, auth[0], auth[1], "upload", "supply_file", supply.id, stored_path)
    return FileUploadResponse(message="Archivo guardado", path=stored_path)


@router.post("/memos/{memo_id}/files", response_model=FileUploadResponse, status_code=201)
def upload_memo_file(
    memo_id: int,
    file: UploadFile = File(...),
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS, UserRole.TESORERIA})),
    session: Session = Depends(get_session),
) -> FileUploadResponse:
    memo = session.get(Memo, memo_id)
    if not memo:
        raise HTTPException(status_code=404, detail="Memo no encontrado")

    folder = base_storage_dir() / "memos" / Path(memo_folder_name(memo.number, memo.description))
    stored_path = save_upload_to_folder(folder=folder, uploaded_file=file)
    log_audit(session, auth[0], auth[1], "upload", "memo_file", memo.id, stored_path)
    return FileUploadResponse(message="Archivo guardado", path=stored_path)


@router.post("/imports/supplies/{supply_id}/excel-items", response_model=ImportResult)
def import_supply_items_from_excel(
    supply_id: int,
    file: UploadFile = File(...),
    mapping_json: str | None = Form(default=None),
    auth=Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS})),
    session: Session = Depends(get_session),
) -> ImportResult:
    supply = session.get(Supply, supply_id)
    if not supply:
        raise HTTPException(status_code=404, detail="Suministro no encontrado")

    content = file.file.read()
    items_data, errors = parse_excel_rows(content, parse_mapping(mapping_json))

    created = 0
    for data in items_data:
        quantity = float(data["quantity"])
        unit_cost = float(data["unit_cost"])
        item = SupplyItem(
            supply_id=supply.id,
            code=str(data["code"]),
            quantity=quantity,
            detail=str(data["detail"]),
            unit_cost=unit_cost,
            category_program=(str(data.get("category_program")) if data.get("category_program") else None),
            unit_measure=(str(data.get("unit_measure")) if data.get("unit_measure") else None),
            estimated_cost=float(data.get("estimated_cost") or quantity * unit_cost),
        )
        session.add(item)
        created += 1

    supply.updated_at = datetime.utcnow()
    session.add(supply)
    session.commit()
    log_audit(session, auth[0], auth[1], "import_excel", "supply", supply.id, f"items={created}")
    return ImportResult(items_created=created, errors=errors)


@router.post("/imports/supplies/pdf-preview", response_model=PdfPreview)
def preview_pdf_import(
    file: UploadFile = File(...),
    _: tuple[str, str] = Depends(require_roles({UserRole.ADMIN, UserRole.COMPRAS, UserRole.LECTURA})),
) -> PdfPreview:
    data = parse_pdf_preview(file.file.read(), file.filename or "documento.pdf")
    return PdfPreview(**data)


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


@router.get("/dashboard/charts", response_model=DashboardChartData)
def dashboard_charts(
    executing_unit: str | None = None,
    requester_dependency: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    session: Session = Depends(get_session),
) -> DashboardChartData:
    return get_chart_data(
        session,
        executing_unit=executing_unit,
        requester_dependency=requester_dependency,
        date_from=date_from,
        date_to=date_to,
    )
