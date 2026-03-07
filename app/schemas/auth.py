from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import List, Optional


# -------------------------------------------------------
# Login
# -------------------------------------------------------
class LoginRequest(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    full_name: str
    phone: str


# -------------------------------------------------------
# Dashboard
# -------------------------------------------------------
class AccountSummary(BaseModel):
    account_id: int
    account_number: str
    account_type: str
    balance: Decimal
    bank_name: str
    branch_name: str

class RecentTransaction(BaseModel):
    transaction_id: int
    reference_id: str
    type: str
    amount: Decimal
    status: str
    created_at: datetime

class DashboardResponse(BaseModel):
    user_id: int
    full_name: str
    phone: str
    total_balance: Decimal
    accounts: List[AccountSummary]
    recent_transactions: List[RecentTransaction]