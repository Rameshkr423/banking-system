import json
import logging
import os
from google.cloud import pubsub_v1

logger = logging.getLogger(__name__)

publisher   = pubsub_v1.PublisherClient()
PROJECT_ID  = os.getenv("GCP_PROJECT_ID", "banking-system-prod")  # ← hardcoded fallback


def publish_event(topic_id: str, data: dict):
    try:
        topic_path    = publisher.topic_path(PROJECT_ID, topic_id)
        message_bytes = json.dumps(data, default=str).encode("utf-8")
        future        = publisher.publish(topic_path, message_bytes)
        message_id    = future.result(timeout=10)
        logger.info(f"Published | topic={topic_id} | msg_id={message_id}")
    except Exception as e:
        logger.error(f"Pub/Sub publish failed | topic={topic_id} | error={e}")


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