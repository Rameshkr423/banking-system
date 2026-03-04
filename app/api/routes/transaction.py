from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db

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