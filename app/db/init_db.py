from app.db.base import Base
from app.db.session import engine

# Import all models so SQLAlchemy knows about them before create_all
from app.models import user, account, transaction, ledger, audit_log


def init_db():
    from app.core.config import settings
    import logging
    logging.basicConfig(level=logging.INFO)
    # Log URL with password masked
    url = settings.database_url
    masked = url.replace(settings.DB_PASSWORD or "", "***") if settings.DB_PASSWORD else url
    logging.info(f"DB URL: {masked}")
    logging.info(f"ENV: {settings.ENV}")
    logging.info(f"DB_HOST: {settings.DB_HOST}")
    Base.metadata.create_all(bind=engine._get())