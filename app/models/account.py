from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
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

    bank_id = Column(Integer, ForeignKey("banks.id"), nullable=False)

    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)

    account_number = Column(String(20), unique=True, index=True, nullable=False)

    account_type = Column(String(20), nullable=False)

    status = Column(String(20), default="active")

    created_at = Column(DateTime(timezone=True), server_default=func.now())


    