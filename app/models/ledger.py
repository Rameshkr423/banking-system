from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Numeric
)
from sqlalchemy.sql import func
from app.db.base import Base
import enum


class EntryType(str, enum.Enum):
    debit = "debit"
    credit = "credit"


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)

    entry_type = Column(String(10), nullable=False)  # or use Enum(EntryType)

    amount = Column(Numeric(15, 2), nullable=False)

    currency = Column(String(10), default="INR")

    description = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
