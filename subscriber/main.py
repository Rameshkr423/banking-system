import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv

from services.audit_listener import AuditListener
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# ── Two listeners — one per subscription ─────────────────────
txn_listener   = AuditListener(
    subscription_id=os.getenv("PUBSUB_SUBSCRIPTION", "transaction-events-sub")
)
audit_listener = AuditListener(
    subscription_id=os.getenv("AUDIT_SUBSCRIPTION", "audit-events-sub")
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting subscriber service...")
    asyncio.create_task(txn_listener.start())    # transactions
    asyncio.create_task(audit_listener.start())  # user/fraud/simulation
    yield
    logger.info("Shutting down subscriber service...")
    await txn_listener.stop()
    await audit_listener.stop()


app = FastAPI(
    title="Banking Subscriber Service",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health():
    return {
        "status":  "ok",
        "service": "banking-subscriber"
    }


@app.get("/ready")
async def ready():
    return {
        "status":        "ready",
        "txn_listener":   txn_listener.is_running,
        "audit_listener": audit_listener.is_running,
    }