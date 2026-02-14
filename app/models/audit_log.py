from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from app.db.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)

    event_type = Column(String(100), nullable=False)  # account.created, transaction.completed

    user_id = Column(Integer, nullable=True)  # who triggered the action

    reference_id = Column(String(100), nullable=True)  # transaction ref or request id

    service_name = Column(String(100), nullable=True)  # account-service / transaction-service

    status = Column(String(20), nullable=False, default="success")  # success / failure

    ip_address = Column(String(50), nullable=True)

    payload = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
