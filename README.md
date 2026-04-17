# RAFAM Workflow (Base)

Base en **Python + FastAPI** para gestionar flujo de suministros/compras, proveedores y KPIs operativos.

## Cómo descargar y probar

### Opción A: con Git

```bash
git clone <URL_DEL_REPO>
cd code
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

Abrí: `http://127.0.0.1:8000/docs`

### Opción B: ZIP

1. Descargar el repositorio en ZIP desde tu hosting Git.
2. Descomprimir.
3. Entrar a la carpeta del proyecto.
4. Ejecutar los mismos pasos de entorno virtual e instalación.

## Endpoints MVP

- `GET /health`
- `POST /providers` crear proveedor
- `GET /providers` listar proveedores
- `POST /supplies` crear suministro
- `GET /supplies` listar suministros
- `GET /supplies/{supply_id}` detalle
- `POST /supplies/{supply_id}/items` agregar ítem
- `POST /supplies/{supply_id}/transitions` mover etapa
- `GET /budget/summary` resumen por partida (3 primeros niveles, ej. `2.9.6`)
- `GET /dashboard/kpis` KPIs de gestión
- `GET /dashboard/alerts` alertas por falta de movimiento

## Mejoras sugeridas (siguiente sprint)

1. Importación de PDF/Excel con mapeo de columnas y validaciones.
2. Agenda de contacto por proveedor con historial de compras.
3. Módulo de expedientes/memos con ubicación por oficina y fecha.
4. Kanban con tareas vinculadas a suministros y expedientes.
5. Roles y permisos + auditoría completa.
6. Dashboard visual con gráficos y filtros por secretaría/dependencia.
