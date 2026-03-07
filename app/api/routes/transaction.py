from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import get_db

from app.schemas.statement import StatementResponse
from app.services.statement_service import get_statement

from app.schemas.transaction import (
    DepositRequest,
    TransactionResponse,
    BalanceResponse,
    WithdrawRequest,
    TransferRequest
)

from app.services.transaction_service import (
    deposit,
    get_balance,
    withdraw,
    transfer
)

router = APIRouter()


# ---------------------------------------------------
# Deposit
# ---------------------------------------------------
@router.post("/deposit", response_model=TransactionResponse)
def deposit_money(request: DepositRequest, db: Session = Depends(get_db)):

    try:
        transaction = deposit(db, request.account_id, request.amount)

        db.commit()      # ⭐ save changes
        db.refresh(transaction)

        return {
            "transaction_id": transaction.id,
            "reference_id": transaction.reference_id,
            "status": transaction.status,
            "amount": transaction.amount
        }

    except Exception as e:
        db.rollback()
        raise


# ---------------------------------------------------
# Balance
# ---------------------------------------------------
@router.get("/balance/{account_id}", response_model=BalanceResponse)
def balance(account_id: int, db: Session = Depends(get_db)):
    return {"balance": get_balance(db, account_id)}



@router.get("/statement/{user_id}", response_model=StatementResponse, summary="Transaction Statement")
def transaction_statement(
    user_id: int,
    account_id: Optional[int] = Query(None, description="Filter by specific account ID"),
    from_date: Optional[datetime] = Query(None, description="Start date e.g. 2026-01-01T00:00:00"),
    to_date: Optional[datetime] = Query(None, description="End date e.g. 2026-03-07T23:59:59"),
    db: Session = Depends(get_db),
):
    """
    Get flat transaction statement for a user.
    - Filter by account_id, from_date, to_date
    - Returns all ledger entries + summary (total credit, debit, closing balance)
    """
    return get_statement(
        db=db,
        user_id=user_id,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
    )


# ---------------------------------------------------
# Withdraw
# ---------------------------------------------------
@router.post("/withdraw", response_model=TransactionResponse)
def withdraw_money(request: WithdrawRequest, db: Session = Depends(get_db)):

    try:
        transaction = withdraw(db, request.account_id, request.amount)

        db.commit()     # ⭐ save changes
        db.refresh(transaction)

        return {
            "transaction_id": transaction.id,
            "reference_id": transaction.reference_id,
            "status": transaction.status,
            "amount": transaction.amount
        }

    except Exception as e:
        db.rollback()
        raise


# ---------------------------------------------------
# Transfer
# ---------------------------------------------------
@router.post("/transfer", response_model=TransactionResponse)
def transfer_money(request: TransferRequest, db: Session = Depends(get_db)):

    try:
        transaction = transfer(
            db,
            request.from_account_id,
            request.to_account_id,
            request.amount,
            request.idempotency_key
        )

        db.commit()    # ⭐ VERY IMPORTANT
        db.refresh(transaction)

        return {
            "transaction_id": transaction.id,
            "reference_id": transaction.reference_id,
            "status": transaction.status,
            "amount": transaction.amount
        }

    except Exception as e:
        db.rollback()
        raise