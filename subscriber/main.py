import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from services.audit_listener import AuditListener
from services.notification_service import NotificationService
from services.analytics_service import AnalyticsService
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

audit_listener = AuditListener()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    logger.info("Starting subscriber service...")
    asyncio.create_task(audit_listener.start())
    yield
    # ── Shutdown ─────────────────────────────────────────────
    logger.info("Shutting down subscriber service...")
    await audit_listener.stop()


app = FastAPI(
    title="Banking Subscriber Service",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "banking-subscriber"
    }


@app.get("/ready")
async def ready():
    return {
        "status": "ready",
        "listener": audit_listener.is_running
    }