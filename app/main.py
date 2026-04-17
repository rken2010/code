from fastapi import FastAPI

from app.api.routes import router
from app.db.session import init_db

app = FastAPI(title="RAFAM Workflow API", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router)
