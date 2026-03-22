import os
from fastapi import FastAPI, Request, Response
from dotenv import load_dotenv

from services.audit_listener import AuditListener
from utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

# One shared listener instance (stateless — just routes messages)
listener = AuditListener()

app = FastAPI(
    title="Banking Subscriber Service",
    version="2.0.0",
)


# ── Health / Ready ────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "banking-subscriber"}


@app.get("/ready")
async def ready():
    return {"status": "ready"}


# ── Pub/Sub Push Endpoints ────────────────────────────────────

@app.post("/pubsub/transaction-events")
async def handle_transaction_events(request: Request):
    """
    Pub/Sub push subscription for: transaction_completed events.
    Subscription: transaction-events-sub  →  push to this URL.
    HTTP 200 = ack  |  HTTP 500 = nack (Pub/Sub retries)
    """
    envelope = await request.json()
    logger.info("Push received | sub=transaction-events-sub")

    success = listener.handle_push_message(envelope, subscription_id="transaction-events-sub")
    return Response(status_code=200 if success else 500)


@app.post("/pubsub/audit-events")
async def handle_audit_events(request: Request):
    """
    Pub/Sub push subscription for: user_registered, fraud_alert, simulation_completed.
    Subscription: audit-events-sub  →  push to this URL.
    """
    envelope = await request.json()
    logger.info("Push received | sub=audit-events-sub")

    success = listener.handle_push_message(envelope, subscription_id="audit-events-sub")
    return Response(status_code=200 if success else 500)