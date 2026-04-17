# RAFAM Workflow (Next Sprint)

Base en **Python + FastAPI** para gestionar suministros, proveedores, agenda de contactos, expedientes, kanban, imports y KPIs.

## Estructura recomendada (Windows)

En la raíz del proyecto:

- `install_windows.bat` → instala dependencias
- `run_windows.bat` → arranca la API
- `scripts/install_windows.bat` y `scripts/run_windows.bat` → wrappers de compatibilidad

## Cómo descargar y probar

### Opción A: Git

```bash
git clone <URL_DEL_REPO>
cd code
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .[dev]
uvicorn app.main:app --reload
```

Abrí `http://127.0.0.1:8000/docs`.

### Opción B: ZIP

1. Descargar ZIP del repo.
2. Descomprimir.
3. Ejecutar los comandos anteriores.

### Windows automático (recomendado)

Desde la raíz del proyecto:

```bat
.\install_windows.bat
.\run_windows.bat
```

Compatibilidad (si estás dentro de `/scripts`):

```bat
.\install_windows.bat
.\run_windows.bat
```

## Seguridad básica (roles)

Los endpoints de escritura requieren headers:

- `X-User: tu_usuario`
- `X-Role: admin | compras | tesoreria | lectura`

## Funcionalidades de este sprint

1. **Importación PDF/Excel**
   - `POST /imports/supplies/{supply_id}/excel-items` (con mapeo opcional `mapping_json`)
   - `POST /imports/supplies/pdf-preview`
2. **Agenda por proveedor + historial**
   - `POST /providers/{provider_id}/contacts`
   - `GET /providers/{provider_id}/contacts`
   - `GET /providers/{provider_id}/history`
3. **Expedientes con trazabilidad**
   - `POST /expedientes`
   - `GET /expedientes`
   - `POST /expedientes/{expediente_id}/movements`
4. **Kanban de tareas vinculadas**
   - `POST /tasks`
   - `GET /tasks`
   - `PATCH /tasks/{task_id}/status`
5. **Roles/permisos + auditoría**
   - `POST /users` (admin)
   - `GET /audit/logs` (admin)
6. **Dashboard visual (datos para gráficos)**
   - `GET /dashboard/charts` con filtros por secretaría/dependencia/rango de fechas

## Estructura de archivos cargados

- `storage/suministros/Suministro N° <ID> - <Descripción>/YYYYMMDD-HHMMSS-archivo.ext`
- `storage/memos/Memo N° <NUMERO> - <Descripción>/YYYYMMDD-HHMMSS-archivo.ext`

Con sanitización para caracteres inválidos de Windows.
