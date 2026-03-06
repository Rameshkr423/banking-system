from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)

    city_name = Column(String(100), nullable=False)

    state = Column(String(100))

    country = Column(String(100))

    created_at = Column(DateTime(timezone=True), server_default=func.now())