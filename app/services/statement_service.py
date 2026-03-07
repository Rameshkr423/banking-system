from sqlalchemy.orm import Session
from fastapi import HTTPException
from decimal import Decimal
from datetime import datetime
from typing import Optional

from app.models.ledger import LedgerEntry, EntryType
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.user import User


def get_statement(
    db: Session,
    user_id: int,
    account_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
):
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all accounts for this user
    account_query = db.query(Account).filter(Account.user_id == user_id)
    if account_id:
        account_query = account_query.filter(Account.id == account_id)

    user_accounts = account_query.all()
    if not user_accounts:
        raise HTTPException(status_code=404, detail="No accounts found for this user")

    user_account_ids = [a.id for a in user_accounts]

    # account_id -> account_number lookup (user's accounts)
    account_map = {a.id: a.account_number for a in user_accounts}

    # Full system account map for counterparty resolution
    all_account_map = {
        a.id: a.account_number
        for a in db.query(Account).all()
    }

    # Query ledger entries joined with transactions
    query = (
        db.query(LedgerEntry, Transaction)
        .join(Transaction, Transaction.id == LedgerEntry.transaction_id)
        .filter(LedgerEntry.account_id.in_(user_account_ids))
    )

    if from_date:
        query = query.filter(LedgerEntry.created_at >= from_date)
    if to_date:
        query = query.filter(LedgerEntry.created_at <= to_date)

    query = query.order_by(LedgerEntry.created_at.asc())
    results = query.all()

    entries = []
    total_credit = Decimal("0.00")
    total_debit = Decimal("0.00")

    for ledger, txn in results:
        entry_type_val = (
            ledger.entry_type.value
            if hasattr(ledger.entry_type, "value")
            else str(ledger.entry_type)
        )
        txn_type_val = (
            txn.type.value
            if hasattr(txn.type, "value")
            else str(txn.type)
        )

        if ledger.entry_type == EntryType.credit:
            total_credit += ledger.amount
        else:
            total_debit += ledger.amount

        entries.append({
            "ledger_id": ledger.id,
            "transaction_id": txn.id,
            "reference_id": txn.reference_id,
            "account_id": ledger.account_id,
            "account_number": account_map.get(ledger.account_id, ""),
            "entry_type": entry_type_val,
            "transaction_type": txn_type_val,
            "amount": ledger.amount,
            "running_balance": ledger.running_balance or Decimal("0.00"),
            "counterparty_account_number": all_account_map.get(ledger.counterparty_account_id)
            if ledger.counterparty_account_id else None,
            "description": ledger.description,
            "created_at": ledger.created_at,
        })

    closing_balance = entries[-1]["running_balance"] if entries else Decimal("0.00")

    return {
        "user_id": user_id,
        "entries": entries,
        "summary": {
            "total_credit": total_credit,
            "total_debit": total_debit,
            "closing_balance": closing_balance,
        }
    }