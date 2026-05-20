from sqlalchemy import Column, Integer, String, ForeignKey
from app.schemas.payments import PaymentStatus, PaymentMethod
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import relationship
from app.models.base_models import TimestampedModel
from app.db import Base
from app.models.users import User


class Payment(TimestampedModel):

    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    amount: Mapped[str] = mapped_column(String(10), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(default=PaymentMethod.PAYME)
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING)

    user: Mapped["User"] = relationship("User", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount})>"
