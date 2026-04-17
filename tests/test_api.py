from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.db import session as session_module
from app.db.session import get_session
from app.main import app


def test_supply_flow_and_budget_summary():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    session_module.engine = engine

    client = TestClient(app)

    created = client.post(
        "/supplies",
        json={
            "date": "2026-04-17",
            "requester_dependency": "Obras Públicas",
            "executing_unit": "Secretaría de Infraestructura",
            "title": "Compra de materiales",
            "description": "MVP test",
        },
    )
    assert created.status_code == 201
    supply_id = created.json()["id"]

    added_item = client.post(
        f"/supplies/{supply_id}/items",
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
