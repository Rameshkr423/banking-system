import json
import logging
from google.cloud import pubsub_v1
from app.core.config import settings

logger = logging.getLogger(__name__)

publisher = pubsub_v1.PublisherClient()


def publish_event(topic_id: str, data: dict):
    """Publish to Pub/Sub — never raises, just logs on failure"""
    try:
        topic_path = publisher.topic_path(settings.GCP_PROJECT_ID, topic_id)
        message_bytes = json.dumps(data, default=str).encode("utf-8")
        future = publisher.publish(topic_path, message_bytes)
        message_id = future.result(timeout=10)
        logger.info(f"Published | topic={topic_id} | msg_id={message_id}")
    except Exception as e:
        logger.error(f"Pub/Sub publish failed | topic={topic_id} | error={e}")


def publish_transaction_event(transaction, ledger_entries: list):
    """Called after every deposit / withdraw / transfer"""
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