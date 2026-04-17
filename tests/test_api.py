from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.db import session as session_module
from app.db.session import get_session
from app.main import app
from app.models.supply import Supply
from app.services.files import memo_folder_name, supply_folder_name
from app.services.imports import parse_mapping

AUTH = {"X-User": "tester", "X-Role": "admin"}


def test_supply_flow_budget_and_dashboard():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    session_module.engine = engine

    client = TestClient(app)

    provider = client.post(
        "/providers",
        headers=AUTH,
        json={
            "business_name": "Proveedor Demo SA",
            "tax_id": "30-12345678-9",
            "email": "ventas@demo.com",
        },
    )
    assert provider.status_code == 201
    provider_id = provider.json()["id"]

    created = client.post(
        "/supplies",
        headers=AUTH,
        json={
            "date": "2026-04-17",
            "requester_dependency": "Obras Públicas",
            "executing_unit": "Secretaría de Infraestructura",
            "title": "Compra de materiales",
            "description": "MVP test",
            "provider_id": provider_id,
        },
    )
    assert created.status_code == 201
    supply_id = created.json()["id"]

    added_item = client.post(
        f"/supplies/{supply_id}/items",
        headers=AUTH,
        json={
            "code": "2.9.6.01355.0045",
            "quantity": 2,
            "detail": "Bolsa de cemento",
            "unit_cost": 1000,
            "category_program": "cat-1",
            "unit_measure": "unidad",
        },
    )
    assert added_item.status_code == 201
    assert added_item.json()["estimated_cost"] == 2000

    moved = client.post(
        f"/supplies/{supply_id}/transitions",
        headers=AUTH,
        json={
            "to_stage": "purchase_order",
            "document_number": "OC-12",
            "document_date": "2026-04-17",
        },
    )
    assert moved.status_code == 201

    summary = client.get("/budget/summary")
    assert summary.status_code == 200
    data = summary.json()
    assert data[0]["partida"] == "2.9.6"
    assert data[0]["committed"] == 2000

    kpis = client.get("/dashboard/kpis")
    assert kpis.status_code == 200
    assert kpis.json()["total_supplies"] == 1


def test_alerts_for_stale_supply():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    session_module.engine = engine

    with Session(engine) as session:
        stale_supply = Supply(
            date=datetime.utcnow().date(),
            requester_dependency="Salud",
            executing_unit="Secretaría de Salud",
            title="Insumos médicos",
            updated_at=datetime.utcnow() - timedelta(days=20),
        )
        session.add(stale_supply)
        session.commit()

    client = TestClient(app)
    alerts = client.get("/dashboard/alerts?stale_days=10")
    assert alerts.status_code == 200
    assert len(alerts.json()) == 1
    assert alerts.json()[0]["title"] == "Insumos médicos"


def test_folder_naming_and_mapping_rules():
    supply_folder = supply_folder_name(15, "Compra de tornillos / herramientas")
    memo_folder = memo_folder_name("4079-23", "Nota: envío urgente")
    mapping = parse_mapping('{"Código":"code","Cantidad":"quantity"}')

    assert supply_folder.startswith("Suministro N° 15 - ")
    assert "/" not in supply_folder

    assert memo_folder.startswith("Memo N° 4079-23 - ")
    assert ":" not in memo_folder

    assert mapping["código"] == "code"
    assert mapping["cantidad"] == "quantity"
