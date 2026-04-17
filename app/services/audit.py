from sqlmodel import Session

from app.models.workflow import AuditLog


def log_audit(
    session: Session,
    username: str | None,
    role: str | None,
    action: str,
    entity: str,
    entity_id: int | None = None,
    detail: str | None = None,
) -> None:
    entry = AuditLog(
        username=username,
        role=role,
        action=action,
        entity=entity,
        entity_id=entity_id,
        detail=detail,
    )
    session.add(entry)
    session.commit()
