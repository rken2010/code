# RAFAM Workflow (Base)

Base en **Python + FastAPI** para gestionar flujo de suministros/compras y estado presupuestario por partida.

## Requisitos

- Python 3.11+

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Ejecutar

```bash
uvicorn app.main:app --reload
```

Documentación:
- Swagger: `http://127.0.0.1:8000/docs`

## Endpoints MVP

- `GET /health`
- `POST /supplies` crear suministro
- `GET /supplies` listar suministros
- `GET /supplies/{supply_id}` detalle
- `POST /supplies/{supply_id}/items` agregar ítem
- `POST /supplies/{supply_id}/transitions` mover etapa
- `GET /budget/summary` resumen por partida (3 primeros niveles, ej. `2.9.6`)

## Nota

Este MVP se centra en el núcleo del flujo. Se puede extender con:
- OCR de PDF/imagen
- Proveedores/agenda
- Expedientes/memos
- Kanban y recordatorios
