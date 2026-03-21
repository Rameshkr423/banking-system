import json
import logging
import os
from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)

publisher  = pubsub_v1.PublisherClient()
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "banking-system-prod")


def publish_event(topic_id: str, data: dict):
    """Publish to Pub/Sub — never raises, just logs on failure"""
    try:
        topic_path    = publisher.topic_path(PROJECT_ID, topic_id)
        message_bytes = json.dumps(data, default=str).encode("utf-8")
        future        = publisher.publish(topic_path, message_bytes)
        message_id    = future.result(timeout=10)
        logger.info(f"Published | topic={topic_id} | event={data.get('event_type')} | msg_id={message_id}")
    except Exception as e:
        logger.error(f"Pub/Sub publish failed | topic={topic_id} | error={e}")


# ── Transaction Events ────────────────────────────────────────
def publish_transaction_event(transaction, ledger_entries: list):
    payload = {
        "event_type":       "transaction_completed",
        "transaction_id":   str(transaction.id),
        "reference_id":     transaction.reference_id,
        "type":             transaction.type.value,
        "amount":           str(transaction.amount),
        "status":           transaction.status.value,
        "from_account_id":  transaction.from_account_id,
        "to_account_id":    transaction.to_account_id,
        "bank_id":          transaction.bank_id,
        "branch_id":        transaction.branch_id,
        "ledger_entries": [
            {
                "account_id":              e.account_id,
                "entry_type":              e.entry_type.value,
                "amount":                  str(e.amount),
                "running_balance":         str(e.running_balance),
                "counterparty_account_id": e.counterparty_account_id,
                "description":             e.description,
            }
            for e in ledger_entries
        ],
    }
    publish_event("transaction-events", payload)


# ── User Registration Event ───────────────────────────────────
def publish_user_registered_event(user_id: int, full_name: str,
                                   email: str, phone: str,
                                   account_number: str, bank_name: str,
                                   branch_name: str):
    payload = {
        "event_type":     "user_registered",
        "user_id":        user_id,
        "full_name":      full_name,
        "email":          email,
        "phone":          phone,
        "account_number": account_number,
        "bank_name":      bank_name,
        "branch_name":    branch_name,
    }
    publish_event("audit-events", payload)


# ── Fraud Alert Event ─────────────────────────────────────────
def publish_fraud_alert_event(transaction_id: int, account_id: int,
                               amount: float, reason: str,
                               transaction_type: str):
    payload = {
        "event_type":        "fraud_alert",
        "transaction_id":    str(transaction_id),
        "account_id":        account_id,
        "amount":            str(amount),
        "transaction_type":  transaction_type,
        "reason":            reason,
        "severity":          "HIGH",
    }
    publish_event("audit-events", payload)


# ── Simulation Event ──────────────────────────────────────────
def publish_simulation_event(accounts_created: int,
                              transfers_executed: int,
                              transfers_skipped: int,
                              initial_deposit: int):
    payload = {
        "event_type":         "simulation_completed",
        "accounts_created":   accounts_created,
        "transfers_executed": transfers_executed,
        "transfers_skipped":  transfers_skipped,
        "initial_deposit":    initial_deposit,
    }
    publish_event("audit-events", payload)