from app.db.base import Base
from app.db.session import engine

# Import all models
from app.models import user, account, transaction, ledger, audit_log


def init_db():
    Base.metadata.create_all(bind=engine)
