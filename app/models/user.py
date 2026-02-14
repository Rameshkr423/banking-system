from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Basic identity
    full_name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)

    # Address details (KYC-ready structure)
    address_line = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)
    zipcode = Column(String(20), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True, default="India")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
