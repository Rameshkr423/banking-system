from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Bank(Base):
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True, index=True)

    bank_name = Column(String(150), nullable=False)

    bank_code = Column(String(20), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())