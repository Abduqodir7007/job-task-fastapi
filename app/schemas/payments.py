from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from decimal import Decimal
from app.schemas.users import UserResponseSchema


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    PAYME = "payme"
    CLICK = "click"
    UZUM = "uzum"


class PaymentResponseSchema(BaseModel):
    id: int
    user: UserResponseSchema
    amount: str
    method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentCreateSchema(BaseModel):
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Payment amount must be greater than zero.")
    method: PaymentMethod
    status: PaymentStatus

    class Config:
        from_attributes = True


class PaymentReportByMethodSchema(BaseModel):
    payme: Decimal
    click: Decimal
    uzum: Decimal

    class Config:
        from_attributes = True


class PaymentReportResponseSchema(BaseModel):
    start_date: datetime
    end_date: datetime
    total_payment: Decimal
    payments_by_method: PaymentReportByMethodSchema

    model_config = {
        "json_schema_extra": {
            "example": {
                "start_date": "2023-01-01T00:00:00",
                "end_date": "2023-01-31T23:59:59",
                "total_payment": "1000.00",
                "payments_by_method": {"payme": "500.00", "click": "300.00", "uzum": "200.00"},
            }
        }
    }
