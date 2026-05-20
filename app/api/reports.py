"""Payment report API routes."""

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import Numeric, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.dependencies import check_admin_or_report_role
from app.models.payments import Payment
from app.models.users import User
from app.schemas.payments import PaymentMethod, PaymentReportByMethodSchema, PaymentReportResponseSchema

from app.utils import _range_bounds

router = APIRouter(prefix="/api", tags=["reports"], dependencies=[Depends(check_admin_or_report_role)])


@router.get("/reports", response_model=PaymentReportResponseSchema)
async def get_report(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(check_admin_or_report_role),
):
    start_date, end_date = _range_bounds(start_date, end_date)
    
    if start_date:
        start_dt = datetime.combine(start_date, time.min)
    if end_date:
        end_dt = datetime.combine(end_date, time.max)

    amount_expr = cast(Payment.amount, Numeric(10, 2))
    total_stmt = select(func.coalesce(func.sum(amount_expr), 0)).where(
        Payment.created_at >= start_dt, Payment.created_at <= end_dt
    )
    total_result = await db.execute(total_stmt)
    total_payment = Decimal(str(total_result.scalar_one()))

    by_method = {
        PaymentMethod.PAYME.value: Decimal("0"),
        PaymentMethod.CLICK.value: Decimal("0"),
        PaymentMethod.UZUM.value: Decimal("0"),
    }

    payment_by_methods = (
        select(
            Payment.method,
            func.coalesce(func.sum(amount_expr), 0),
        )
        .where(Payment.created_at >= start_dt, Payment.created_at <= end_dt)
        .group_by(Payment.method)
    )
    method_result = await db.execute(payment_by_methods)

    for method, total in method_result.all():
        method_name = getattr(method, "value", method)
        by_method[str(method_name)] = Decimal(str(total))

    response = PaymentReportResponseSchema(
        start_date=start_dt,
        end_date=end_dt,
        total_payment=total_payment,
        payments_by_method=PaymentReportByMethodSchema(
            payme=by_method[PaymentMethod.PAYME.value],
            click=by_method[PaymentMethod.CLICK.value],
            uzum=by_method[PaymentMethod.UZUM.value],
        ),
    )
    return response
