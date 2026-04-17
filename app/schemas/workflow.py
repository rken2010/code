from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.workflow import TaskStatus, UserRole


class ProviderContactCreate(BaseModel):
    name: str = Field(min_length=2)
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ProviderContactRead(BaseModel):
    id: int
    provider_id: int
    name: str
    role: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime


class ProviderHistoryItem(BaseModel):
    supply_id: int
    title: str
    stage: str
    total_estimated: float
    created_at: datetime


class ExpedienteCreate(BaseModel):
    code: str
    description: str
    expediente_type: str
    current_office: Optional[str] = None
    current_office_since: Optional[date] = None


class ExpedienteRead(BaseModel):
    id: int
    code: str
    description: str
    expediente_type: str
    current_office: Optional[str]
    current_office_since: Optional[date]
    created_at: datetime


class ExpedienteMovementCreate(BaseModel):
    office: str
    moved_at: date
    notes: Optional[str] = None


class ExpedienteMovementRead(BaseModel):
    id: int
    expediente_id: int
    office: str
    moved_at: date
    notes: Optional[str]
    created_at: datetime


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    supply_id: Optional[int] = None
    expediente_id: Optional[int] = None


class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    due_date: Optional[date]
    supply_id: Optional[int]
    expediente_id: Optional[int]
    created_at: datetime
    updated_at: datetime


class TaskStatusUpdate(BaseModel):
    status: TaskStatus


class UserCreate(BaseModel):
    username: str
    role: UserRole


class UserRead(BaseModel):
    id: int
    username: str
    role: UserRole
    is_active: bool


class AuditLogRead(BaseModel):
    id: int
    username: Optional[str]
    role: Optional[str]
    action: str
    entity: str
    entity_id: Optional[int]
    detail: Optional[str]
    created_at: datetime


class DashboardChartData(BaseModel):
    stage_counts: dict[str, int]
    monthly_totals: dict[str, float]


class ImportResult(BaseModel):
    items_created: int
    errors: list[str]


class PdfPreview(BaseModel):
    filename: str
    detected_date: Optional[str]
    detected_dependency: Optional[str]
    preview_lines: list[str]
