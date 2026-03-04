from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi import HTTPException
from decimal import Decimal
import uuid

from app.models.transaction import (
    Transaction,
    TransactionType,
    TransactionStatus,
)
from app.models.ledger import LedgerEntry, EntryType
from app.models.account import Account


# ---------------------------------------------------------
# Helper: Get Current Balance (Single Query Optimized)
# ---------------------------------------------------------

def get_balance(db: Session, account_id: int) -> Decimal:
    balance = db.query(
        func.coalesce(
            func.sum(
                case(
                    (LedgerEntry.entry_type == EntryType.credit, LedgerEntry.amount),
                    else_=-LedgerEntry.amount
                )
            ), 0
        )
    ).filter(
        LedgerEntry.account_id == account_id
    ).scalar()

    return balance or Decimal("0.00")


# ---------------------------------------------------------
# Deposit
# ---------------------------------------------------------

def deposit(db: Session, account_id: int, amount: Decimal):

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    # Lock account row
    account = (
        db.query(Account)
        .filter(Account.id == account_id)
        .with_for_update()
        .first()
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transaction = Transaction(
        reference_id=str(uuid.uuid4()),
        type=TransactionType.deposit,
        amount=amount,
        status=TransactionStatus.pending,
        to_account_id=account_id
    )

    db.add(transaction)
    db.flush()

    current_balance = get_balance(db, account_id)
    new_balance = current_balance + amount

    ledger_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=account_id,
        counterparty_account_id=None,
        entry_type=EntryType.credit,
        amount=amount,
        running_balance=new_balance,
        description="Cash Deposit"
    )

    db.add(ledger_entry)

    transaction.status = TransactionStatus.success

    return transaction


# ---------------------------------------------------------
# Withdraw
# ---------------------------------------------------------

def withdraw(db: Session, account_id: int, amount: Decimal):

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    account = (
        db.query(Account)
        .filter(Account.id == account_id)
        .with_for_update()
        .first()
    )

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    current_balance = get_balance(db, account_id)

    if current_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    transaction = Transaction(
        reference_id=str(uuid.uuid4()),
        type=TransactionType.withdraw,
        amount=amount,
        status=TransactionStatus.pending,
        from_account_id=account_id
    )

    db.add(transaction)
    db.flush()

    new_balance = current_balance - amount

    ledger_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=account_id,
        counterparty_account_id=None,
        entry_type=EntryType.debit,
        amount=amount,
        running_balance=new_balance,
        description="Cash Withdrawal"
    )

    db.add(ledger_entry)

    transaction.status = TransactionStatus.success

    return transaction


# ---------------------------------------------------------
# Transfer
# ---------------------------------------------------------

def transfer(
    db: Session,
    from_account_id: int,
    to_account_id: int,
    amount: Decimal,
    idempotency_key: str
):

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    if from_account_id == to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to same account")

    # Idempotency protection
    existing_tx = db.query(Transaction).filter(
        Transaction.idempotency_key == idempotency_key
    ).first()

    if existing_tx:
        return existing_tx

    # Lock accounts to prevent race condition
    from_account = (
        db.query(Account)
        .filter(Account.id == from_account_id)
        .with_for_update()
        .first()
    )

    to_account = (
        db.query(Account)
        .filter(Account.id == to_account_id)
        .with_for_update()
        .first()
    )

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Account not found")

    from_balance = get_balance(db, from_account_id)

    if from_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    transaction = Transaction(
        reference_id=str(uuid.uuid4()),
        type=TransactionType.transfer,
        amount=amount,
        status=TransactionStatus.pending,
        from_account_id=from_account_id,
        to_account_id=to_account_id,
        idempotency_key=idempotency_key
    )

    db.add(transaction)
    db.flush()

    # -----------------------------
    # Debit Entry
    # -----------------------------
    new_from_balance = from_balance - amount

    debit_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=from_account_id,
        counterparty_account_id=to_account_id,
        entry_type=EntryType.debit,
        amount=amount,
        running_balance=new_from_balance,
        description=f"Transfer to A/C {to_account.account_number}"
    )

    db.add(debit_entry)

    # -----------------------------
    # Credit Entry
    # -----------------------------
    to_balance = get_balance(db, to_account_id)
    new_to_balance = to_balance + amount

    credit_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=to_account_id,
        counterparty_account_id=from_account_id,
        entry_type=EntryType.credit,
        amount=amount,
        running_balance=new_to_balance,
        description=f"Transfer from A/C {from_account.account_number}"
    )

    db.add(credit_entry)

    transaction.status = TransactionStatus.success

    return transaction