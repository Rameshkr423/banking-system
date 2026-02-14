from sqlalchemy.orm import Session
from fastapi import HTTPException
from decimal import Decimal
import uuid

from app.models.transaction import Transaction
from app.models.ledger import LedgerEntry
from app.models.account import Account

from sqlalchemy import func
from app.models.ledger import LedgerEntry


def deposit(db: Session, account_id: int, amount: Decimal):

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    reference_id = str(uuid.uuid4())

    transaction = Transaction(
        reference_id=reference_id,
        account_id=account_id,
        type="deposit",
        amount=amount,
        status="completed"
    )

    db.add(transaction)
    db.flush()

    ledger_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=account_id,
        entry_type="credit",
        amount=amount
    )

    db.add(ledger_entry)

    db.commit()

    return transaction


def get_balance(db: Session, account_id: int):

    credits = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0))\
        .filter(
            LedgerEntry.account_id == account_id,
            LedgerEntry.entry_type == "credit"
        ).scalar()

    debits = db.query(func.coalesce(func.sum(LedgerEntry.amount), 0))\
        .filter(
            LedgerEntry.account_id == account_id,
            LedgerEntry.entry_type == "debit"
        ).scalar()

    return credits - debits


def withdraw(db: Session, account_id: int, amount: Decimal):

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    account = db.query(Account).filter(Account.id == account_id).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    current_balance = get_balance(db, account_id)

    if current_balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    reference_id = str(uuid.uuid4())

    transaction = Transaction(
        reference_id=reference_id,
        account_id=account_id,
        type="withdraw",
        amount=amount,
        status="completed"
    )

    db.add(transaction)
    db.flush()

    ledger_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=account_id,
        entry_type="debit",
        amount=amount
    )

    db.add(ledger_entry)

    db.commit()

    return transaction

def transfer(db: Session, from_account_id: int, to_account_id: int, amount: Decimal, idempotency_key: str):

    existing_tx = db.query(Transaction).filter(
        Transaction.idempotency_key == idempotency_key
    ).first()

    if existing_tx:
        return existing_tx

    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    if from_account_id == to_account_id:
        raise HTTPException(status_code=400, detail="Cannot transfer to same account")

    from_account = db.query(Account).filter(Account.id == from_account_id).first()
    to_account = db.query(Account).filter(Account.id == to_account_id).first()

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail="Account not found")

    if get_balance(db, from_account_id) < amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    reference_id = str(uuid.uuid4())

    transaction = Transaction(
        reference_id=reference_id,
        account_id=from_account_id,
        type="transfer",
        amount=amount,
        status="completed",
        idempotency_key=idempotency_key
    )

    db.add(transaction)
    db.flush()

    debit_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=from_account_id,
        entry_type="debit",
        amount=amount
    )

    credit_entry = LedgerEntry(
        transaction_id=transaction.id,
        account_id=to_account_id,
        entry_type="credit",
        amount=amount
    )

    db.add(debit_entry)
    db.add(credit_entry)

    db.commit()

    return transaction
