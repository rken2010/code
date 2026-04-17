from datetime import date, datetime
from enum import StrEnum
from typing import Optional

from sqlmodel import Field, SQLModel


class SupplyStage(StrEnum):
    BUDGET = "budget"
    REQUEST = "request"
    EXPENSE_REQUEST = "expense_request"
    QUOTATION_REQUEST = "quotation_request"
    AWARD = "award"
    PURCHASE_ORDER = "purchase_order"
    DELIVERY_NOTE = "delivery_note"
    INVOICE = "invoice"
    PAYMENT_ORDER = "payment_order"
    CLOSED = "closed"


class Provider(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    business_name: str = Field(index=True)
    tax_id: Optional[str] = Field(default=None, index=True)
    email: Optional[str] = None
    phone: Optional[str] = None
    contact_name: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Supply(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    date: date
    requester_dependency: str
    executing_unit: str

    title: str
    description: Optional[str] = None
    current_stage: SupplyStage = Field(default=SupplyStage.BUDGET)
    provider_id: Optional[int] = Field(default=None, foreign_key="provider.id", index=True)


class SupplyItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supply_id: int = Field(foreign_key="supply.id", index=True)

    code: str = Field(index=True)
    quantity: float
    detail: str
    unit_cost: float
    category_program: Optional[str] = None
    unit_measure: Optional[str] = None
    estimated_cost: float

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class SupplyTransition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    supply_id: int = Field(foreign_key="supply.id", index=True)

    from_stage: SupplyStage
    to_stage: SupplyStage

    document_number: Optional[str] = None
    document_date: Optional[date] = None
    notes: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Memo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    number: str = Field(index=True)
    description: str
    office: Optional[str] = None
    office_since: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
