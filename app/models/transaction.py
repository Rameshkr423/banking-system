from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
    CheckConstraint,
)
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class TransactionType(str, enum.Enum):
    deposit = "deposit"
    withdraw = "withdraw"
    transfer = "transfer"


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    success = "success"
    failed = "failed"


class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_transaction_amount_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)

    reference_id = Column(String(100), unique=True, index=True, nullable=False)

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)

    type = Column(String(20), nullable=False)  # or use Enum(TransactionType)

    amount = Column(Numeric(15, 2), nullable=False)

    currency = Column(String(10), default="INR")

    status = Column(String(20), default="pending")  # pending / success / failed

    failure_reason = Column(String(255), nullable=True)

    idempotency_key = Column(String(100), unique=True, index=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
