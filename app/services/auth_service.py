from sqlalchemy.orm import Session
from sqlalchemy import func, case
from fastapi import HTTPException
from decimal import Decimal

from app.models.user import User
from app.models.account import Account
from app.models.bank import Bank
from app.models.branch import Branch
from app.models.transaction import Transaction
from app.models.ledger import LedgerEntry, EntryType
from app.core.security import verify_password, create_access_token, hash_password


# -------------------------------------------------------
# Helper: Get balance for one account
# -------------------------------------------------------
def _get_balance(db: Session, account_id: int) -> Decimal:
    balance = db.query(
        func.coalesce(
            func.sum(
                case(
                    (LedgerEntry.entry_type == EntryType.credit, LedgerEntry.amount),
                    else_=-LedgerEntry.amount
                )
            ), 0
        )
    ).filter(LedgerEntry.account_id == account_id).scalar()
    return balance or Decimal("0.00")


# -------------------------------------------------------
# Login
# -------------------------------------------------------
def login(db: Session, phone: str, password: str):
    user = db.query(User).filter(User.phone == phone).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    if not user.password_hash:
        raise HTTPException(status_code=401, detail="Password not set for this account. Contact support.")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    token = create_access_token(data={"user_id": user.id, "phone": user.phone})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "full_name": user.full_name,
        "phone": user.phone,
    }


# -------------------------------------------------------
# Dashboard
# -------------------------------------------------------
def get_dashboard(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get all accounts with bank + branch info
    accounts_data = (
        db.query(Account, Bank, Branch)
        .join(Bank, Bank.id == Account.bank_id)
        .join(Branch, Branch.id == Account.branch_id)
        .filter(Account.user_id == user_id)
        .all()
    )

    accounts = []
    total_balance = Decimal("0.00")

    for account, bank, branch in accounts_data:
        balance = _get_balance(db, account.id)
        total_balance += balance
        accounts.append({
            "account_id": account.id,
            "account_number": account.account_number,
            "account_type": account.account_type,
            "balance": balance,
            "bank_name": bank.bank_name,
            "branch_name": branch.branch_name,
        })

    # Get last 10 transactions for this user's accounts
    account_ids = [a[0].id for a in accounts_data]

    recent_txns = (
        db.query(Transaction)
        .filter(
            (Transaction.from_account_id.in_(account_ids)) |
            (Transaction.to_account_id.in_(account_ids))
        )
        .order_by(Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    recent_transactions = [
        {
            "transaction_id": txn.id,
            "reference_id": txn.reference_id,
            "type": txn.type.value if hasattr(txn.type, "value") else str(txn.type),
            "amount": txn.amount,
            "status": txn.status.value if hasattr(txn.status, "value") else str(txn.status),
            "created_at": txn.created_at,
        }
        for txn in recent_txns
    ]

    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "phone": user.phone,
        "total_balance": total_balance,
        "accounts": accounts,
        "recent_transactions": recent_transactions,
    }