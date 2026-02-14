from pydantic import BaseModel
from decimal import Decimal


class DepositRequest(BaseModel):
    account_id: int
    amount: Decimal


class BalanceResponse(BaseModel):
    balance: Decimal

class WithdrawRequest(BaseModel):
    account_id: int
    amount: Decimal


class TransactionResponse(BaseModel):
    transaction_id: int
    reference_id: str
    status: str
    amount: Decimal

class TransferRequest(BaseModel):
    from_account_id: int
    to_account_id: int
    amount: Decimal
    idempotency_key: str

