import os
from google.cloud import bigquery
from utils.logger import get_logger

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self):
        self.client    = bigquery.Client()
        self.table_id  = os.getenv(
            "BIGQUERY_TABLE",
            "banking-system-prod.banking_analytics.transactions"
        )

    def record(self, event: dict):
        rows = [{
            "event_type":  event.get("event_type"),
            "user_id":     str(event.get("user_id", "")),
            "account_id":  str(event.get("account_id", "")),
            "amount":      float(event.get("amount", 0)),
            "currency":    event.get("currency", "INR"),
            "timestamp":   event.get("timestamp"),
            "metadata":    str(event.get("metadata", {})),
        }]

        errors = self.client.insert_rows_json(self.table_id, rows)

        if errors:
            logger.error(f"BigQuery insert failed: {errors}")
        else:
            logger.info(f"[Analytics] recorded {event.get('event_type')}")