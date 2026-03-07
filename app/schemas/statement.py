from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional, List


class StatementEntry(BaseModel):
    ledger_id: int
    transaction_id: int
    reference_id: str
    account_id: int
    account_number: str
    entry_type: str
    transaction_type: str
    amount: Decimal
    running_balance: Decimal
    counterparty_account_number: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class StatementSummary(BaseModel):
    total_credit: Decimal
    total_debit: Decimal
    closing_balance: Decimal


class StatementResponse(BaseModel):
    user_id: int
    entries: List[StatementEntry]
    summary: StatementSummary