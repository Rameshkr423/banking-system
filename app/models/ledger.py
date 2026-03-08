from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric,
    Enum,
    CheckConstraint
)
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class EntryType(str, enum.Enum):
    debit = "debit"
    credit = "credit"


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_ledger_amount_positive"),
    )

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)

    counterparty_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True, index=True)

    bank_id = Column(Integer, ForeignKey("banks.id"), nullable=True, index=True)        # ← added

    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=True, index=True)   # ← added

    entry_type = Column(Enum(EntryType), nullable=False)

    amount = Column(Numeric(15, 2), nullable=False)

    currency = Column(String(10), default="INR")

    description = Column(String(255), nullable=True)

    running_balance = Column(Numeric(15, 2), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())