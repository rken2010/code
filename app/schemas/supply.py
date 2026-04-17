from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.supply import SupplyStage


class SupplyCreate(BaseModel):
    date: date
    requester_dependency: str = Field(min_length=2)
    executing_unit: str = Field(min_length=2)
    title: str = Field(min_length=3)
    description: Optional[str] = None


class SupplyRead(BaseModel):
    id: int
    created_at: datetime
    date: date
    requester_dependency: str
    executing_unit: str
    title: str
    description: Optional[str]
    current_stage: SupplyStage


class SupplyItemCreate(BaseModel):
    code: str = Field(min_length=3)
    quantity: float = Field(gt=0)
    detail: str = Field(min_length=2)
    unit_cost: float = Field(ge=0)
    category_program: Optional[str] = None
    unit_measure: Optional[str] = None


class SupplyItemRead(BaseModel):
    id: int
    supply_id: int
    code: str
    quantity: float
    detail: str
    unit_cost: float
    category_program: Optional[str]
    unit_measure: Optional[str]
    estimated_cost: float
    created_at: datetime


class SupplyTransitionCreate(BaseModel):
    to_stage: SupplyStage
    document_number: Optional[str] = None
    document_date: Optional[date] = None
    notes: Optional[str] = None


class SupplyTransitionRead(BaseModel):
    id: int
    supply_id: int
    from_stage: SupplyStage
    to_stage: SupplyStage
    document_number: Optional[str]
    document_date: Optional[date]
    notes: Optional[str]
    created_at: datetime


class BudgetSummaryItem(BaseModel):
    partida: str
    total_estimated: float
    committed: float
    paid: float
    available: Optional[float] = None
