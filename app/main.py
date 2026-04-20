from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.db.session import init_db

app = FastAPI(title="RAFAM Workflow API", version="0.1.0")

WEB_DIR = Path(__file__).parent / "web"


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> JSONResponse:
    return JSONResponse(status_code=204, content=None)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")
app.include_router(router)
