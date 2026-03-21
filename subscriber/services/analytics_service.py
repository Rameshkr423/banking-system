import os
import logging
from datetime import datetime, timezone
from google.cloud import bigquery

logger = logging.getLogger(__name__)

PROJECT      = os.getenv("GCP_PROJECT_ID", "banking-system-prod")
DATASET      = "banking_analytics"
TXN_TABLE    = f"{PROJECT}.{DATASET}.transactions_stream"
LEDGER_TABLE = f"{PROJECT}.{DATASET}.ledger_analytics"


class AnalyticsService:
    def __init__(self):
        self.client = bigquery.Client()

    def record(self, data: dict):
        try:
            self._write_transaction(data)
            self._write_ledger_entries(data)
        except Exception as e:
            logger.error(f"BigQuery write failed: {e}")

    def _write_transaction(self, data: dict):
        row = [{
            "transaction_id":   int(data.get("transaction_id", 0)),  # INTEGER
            "reference_id":     data.get("reference_id", ""),        # STRING
            "from_account_id":  data.get("from_account_id"),         # INTEGER NULLABLE
            "to_account_id":    data.get("to_account_id"),           # INTEGER NULLABLE
            "bank_id":          data.get("bank_id"),                  # INTEGER NULLABLE
            "transaction_type": data.get("type", ""),                # STRING — mapped from "type"
            "amount":           float(data.get("amount", 0)),        # NUMERIC
            "currency":         "INR",                                # STRING — hardcoded
            "status":           data.get("status", ""),              # STRING
            "created_at":       datetime.now(timezone.utc).isoformat(),
        }]

        errors = self.client.insert_rows_json(TXN_TABLE, row)
        if errors:
            logger.error(f"BQ transactions_stream error: {errors}")
        else:
            logger.info(f"BQ txn written: {data.get('transaction_id')}")

    def _write_ledger_entries(self, data: dict):
        ledger_rows = [
            {
                "transaction_id": int(data.get("transaction_id", 0)),  # INTEGER
                "account_id":     entry.get("account_id"),             # INTEGER
                "entry_type":     entry.get("entry_type", ""),         # STRING
                "amount":         float(entry.get("amount", 0)),       # NUMERIC
                "running_balance": float(entry.get("running_balance", 0)),  # NUMERIC
                "created_at":     datetime.now(timezone.utc).isoformat(),
            }
            for entry in data.get("ledger_entries", [])
        ]

        if not ledger_rows:
            return

        errors = self.client.insert_rows_json(LEDGER_TABLE, ledger_rows)
        if errors:
            logger.error(f"BQ ledger_analytics error: {errors}")
        else:
            logger.info(f"BQ ledger rows written: {len(ledger_rows)}")