from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class AccountType(str, enum.Enum):
    savings = "savings"
    salary = "salary"
    current = "current"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    account_number = Column(String(20), unique=True, index=True, nullable=False)

    # NEW: Account Type
    account_type = Column(String(20), nullable=False)  # savings / salary / current

    status = Column(String(20), default="active")  # active / blocked / closed

    created_at = Column(DateTime(timezone=True), server_default=func.now())
