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
from app.services.transaction_service import deposit, get_balance, withdraw,transfer



router = APIRouter()


@router.post("/deposit", response_model=TransactionResponse)
def deposit_money(request: DepositRequest, db: Session = Depends(get_db)):

    transaction = deposit(db, request.account_id, request.amount)

    return {
        "transaction_id": transaction.id,
        "reference_id": transaction.reference_id,
        "status": transaction.status,
        "amount": transaction.amount
    }


@router.get("/balance/{account_id}", response_model=BalanceResponse)
def balance(account_id: int, db: Session = Depends(get_db)):
    return {"balance": get_balance(db, account_id)}


@router.post("/withdraw", response_model=TransactionResponse)
def withdraw_money(request: WithdrawRequest, db: Session = Depends(get_db)):

    transaction = withdraw(db, request.account_id, request.amount)

    return {
        "transaction_id": transaction.id,
        "reference_id": transaction.reference_id,
        "status": transaction.status,
        "amount": transaction.amount
    }


@router.post("/transfer", response_model=TransactionResponse)
def transfer_money(request: TransferRequest, db: Session = Depends(get_db)):

    transaction = transfer(
         db,
        request.from_account_id,
        request.to_account_id,
        request.amount,
        request.idempotency_key
    )

    return {
        "transaction_id": transaction.id,
        "reference_id": transaction.reference_id,
        "status": transaction.status,
        "amount": transaction.amount
    }
