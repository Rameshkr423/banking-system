import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from urllib.parse import quote_plus


def _build_engine():
    # Read DIRECTLY from os.environ — not from settings object.
    # settings.ENV may be stale if Settings() was instantiated before
    # Cloud Run injected the env vars.
    env         = os.environ.get("ENV", "development")
    db_host     = os.environ.get("DB_HOST", "")
    db_user     = os.environ.get("DB_USER", "")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_name     = os.environ.get("DB_NAME", "")

    import logging
    logger = logging.getLogger(__name__)
    logger.info("=== SESSION _build_engine ===")
    logger.info(f"ENV={env}")
    logger.info(f"DB_HOST={db_host}")
    logger.info(f"DB_USER={db_user}")
    logger.info(f"DB_NAME={db_name}")
    logger.info(f"DB_PASSWORD set: {bool(db_password)}")

    password = quote_plus(db_password)

    if env == "production":
        socket_path = f"/cloudsql/{db_host}"
        url = f"mysql+pymysql://{db_user}:{password}@/{db_name}"
        logger.info(f"Using UNIX SOCKET: {socket_path}")
        logger.info(f"URL (masked): {url.replace(password, '***')}")
        return create_engine(
            url,
            connect_args={"unix_socket": socket_path},
            pool_pre_ping=True,
        )
    else:
        url = f"mysql+pymysql://{db_user}:{password}@{db_host}:3306/{db_name}"
        logger.info(f"Using TCP: {db_host}:3306")
        return create_engine(url, pool_pre_ping=True)


class _LazyEngine:
    _engine = None

    def _get(self):
        if self._engine is None:
            object.__setattr__(self, '_engine', _build_engine())
        return self._engine

    def __getattr__(self, name):
        return getattr(self._get(), name)

    def __repr__(self):
        return repr(self._get())


engine = _LazyEngine()

_SessionLocal = None


def _get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine._get(),
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = _get_session_local()()
    try:
        yield db
    finally:
        db.close()