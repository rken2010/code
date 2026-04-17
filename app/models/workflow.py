from datetime import date, datetime
from enum import StrEnum
from typing import Optional

from sqlmodel import Field, SQLModel


class UserRole(StrEnum):
    ADMIN = "admin"
    COMPRAS = "compras"
    TESORERIA = "tesoreria"
    LECTURA = "lectura"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    role: UserRole = Field(default=UserRole.LECTURA)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = None
    role: Optional[str] = None
    action: str
    entity: str
    entity_id: Optional[int] = None
    detail: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ProviderContact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    provider_id: int = Field(foreign_key="provider.id", index=True)
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Expediente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True)
    description: str
    expediente_type: str = Field(index=True)
    current_office: Optional[str] = None
    current_office_since: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class ExpedienteMovement(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    expediente_id: int = Field(foreign_key="expediente.id", index=True)
    office: str
    moved_at: date
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    status: TaskStatus = Field(default=TaskStatus.TODO)
    due_date: Optional[date] = None
    supply_id: Optional[int] = Field(default=None, foreign_key="supply.id", index=True)
    expediente_id: Optional[int] = Field(default=None, foreign_key="expediente.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
