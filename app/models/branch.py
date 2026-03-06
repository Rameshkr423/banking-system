from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)

    bank_id = Column(Integer, ForeignKey("banks.id"), nullable=False)

    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)

    branch_name = Column(String(150))

    branch_code = Column(String(50))

    ifsc_code = Column(String(20))

    address = Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())