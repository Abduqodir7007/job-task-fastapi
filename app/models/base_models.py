from datetime import datetime
from sqlalchemy import Column, DateTime
from app.db import Base


class TimestampedModel(Base):
    """Base model with timestamps."""

    __abstract__ = True

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

