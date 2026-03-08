from fastapi import APIRouter, Depends, Query, HTTPException
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
    transfer,
    get_account_balance,
)

from app.core.security import get_current_user_id
from app.models.account import Account

router = APIRouter()


# -------------------------------------------------------
# Helper: Verify account belongs to the authenticated user
# -------------------------------------------------------
def verify_account_owner(account_id: int, user_id: int, db: Session):
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == user_id
    ).first()
    if not account:
        raise HTTPException(
            status_code=403,
            detail="Access denied: account does not belong to this user"
        )
    return account


# ---------------------------------------------------
# POST /transactions/deposit   🔒 Protected
# ---------------------------------------------------
@router.post("/deposit", response_model=TransactionResponse, summary="Deposit Money")
def deposit_money(
    request: DepositRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),   # ⭐ Auth
):
    # Ensure the account belongs to the logged-in user
    verify_account_owner(request.account_id, user_id, db)

    try:
        transaction = deposit(db, request.account_id, request.amount)
        db.commit()
        db.refresh(transaction)

        return {
            "transaction_id": transaction.id,
            "reference_id": transaction.reference_id,
            "status": transaction.status,
            "amount": transaction.amount,
        }

    except Exception:
        db.rollback()
        raise


# ---------------------------------------------------
# GET /transactions/balance/{account_id}   🔒 Protected
# ---------------------------------------------------
@router.get("/balance/{account_id}", response_model=BalanceResponse, summary="Balance")
def balance(
    account_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),   # ⭐ Auth
):
    # Ensure the account belongs to the logged-in user
    verify_account_owner(account_id, user_id, db)

    return get_account_balance(db, account_id)


# ---------------------------------------------------
# GET /transactions/statement/{user_id}   🔒 Protected
# ---------------------------------------------------
@router.get("/statement/{user_id}", response_model=StatementResponse, summary="Transaction Statement")
def transaction_statement(
    user_id: int,
    account_id: Optional[int] = Query(None, description="Filter by specific account ID"),
    from_date: Optional[datetime] = Query(None, description="Start date e.g. 2026-01-01T00:00:00"),
    to_date: Optional[datetime] = Query(None, description="End date e.g. 2026-03-07T23:59:59"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id),   # ⭐ Auth
):
    """
    Protected route - users can only access their own statement.
    Filter by account_id, from_date, to_date.
    Returns all ledger entries + summary (total credit, debit, closing balance).
    """
    # Prevent users from viewing another user's statement
    if user_id != current_user_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: you can only view your own statement"
        )

    return get_statement(
        db=db,
        user_id=user_id,
        account_id=account_id,
        from_date=from_date,
        to_date=to_date,
    )


# ---------------------------------------------------
# POST /transactions/withdraw   🔒 Protected
# ---------------------------------------------------
@router.post("/withdraw", response_model=TransactionResponse, summary="Withdraw Money")
def withdraw_money(
    request: WithdrawRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),   # ⭐ Auth
):
    # Ensure the account belongs to the logged-in user
    verify_account_owner(request.account_id, user_id, db)

    try:
        transaction = withdraw(db, request.account_id, request.amount)
        db.commit()
        db.refresh(transaction)

        return {
            "transaction_id": transaction.id,
            "reference_id": transaction.reference_id,
            "status": transaction.status,
            "amount": transaction.amount,
        }

    except Exception:
        db.rollback()
        raise


# ---------------------------------------------------
# POST /transactions/transfer   🔒 Protected
# ---------------------------------------------------
@router.post("/transfer", response_model=TransactionResponse, summary="Transfer Money")
def transfer_money(
    request: TransferRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),   # ⭐ Auth
):
    # Only the owner of the source account can initiate a transfer
    verify_account_owner(request.from_account_id, user_id, db)

    try:
        transaction = transfer(
            db,
            request.from_account_id,
            request.to_account_id,
            request.amount,
            request.idempotency_key,
        )
        db.commit()
        db.refresh(transaction)

        return {
            "transaction_id": transaction.id,
            "reference_id": transaction.reference_id,
            "status": transaction.status,
            "amount": transaction.amount,
        }

    except Exception:
        db.rollback()
        raise