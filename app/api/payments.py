from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Numeric, cast
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.db import get_db
from app.dependencies import check_payment_role
from app.models.payments import Payment
from app.models.users import User
from app.schemas.payments import PaymentCreateSchema, PaymentMethod, PaymentResponseSchema

router = APIRouter(prefix="/api/payments", tags=["payments"], dependencies=[Depends(check_payment_role)])


@router.get("/", response_model=list[PaymentResponseSchema])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    method: PaymentMethod | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(check_payment_role),
):
    query = select(Payment).options(
        selectinload(Payment.user).selectinload(User.roles),
    )

    if method is not None:
        query = query.where(Payment.method == method.value)

    amount_value = cast(Payment.amount, Numeric(10, 2))
    if min_amount is not None:
        query = query.where(amount_value >= min_amount)
    if max_amount is not None:
        query = query.where(amount_value <= max_amount)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()
