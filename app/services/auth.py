from collections.abc import Callable

from fastapi import Header, HTTPException

from app.models.workflow import UserRole


RoleChecker = Callable[[str | None], tuple[str, str]]


def require_roles(allowed: set[UserRole]):
    def _checker(x_user: str | None = Header(default=None), x_role: str | None = Header(default=None)) -> tuple[str, str]:
        if not x_user or not x_role:
            raise HTTPException(status_code=401, detail="Headers requeridos: X-User y X-Role")

        try:
            role = UserRole(x_role.lower())
        except ValueError as exc:
            raise HTTPException(status_code=403, detail="Rol inválido") from exc

        if role not in allowed:
            raise HTTPException(status_code=403, detail="No autorizado")

        return x_user, role.value

    return _checker
