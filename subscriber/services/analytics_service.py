import os
import logging
from datetime import datetime, timezone
from google.cloud import bigquery

logger = logging.getLogger(__name__)

PROJECT      = os.getenv("GCP_PROJECT_ID", "banking-system-prod")
DATASET      = "banking_analytics"
TXN_TABLE    = f"{PROJECT}.{DATASET}.transactions_stream"
LEDGER_TABLE = f"{PROJECT}.{DATASET}.ledger_analytics"
USERS_TABLE  = f"{PROJECT}.{DATASET}.user_registrations"
FRAUD_TABLE  = f"{PROJECT}.{DATASET}.fraud_alerts"
SIM_TABLE    = f"{PROJECT}.{DATASET}.simulation_logs"


class AnalyticsService:
    def __init__(self):
        self.client = bigquery.Client()

    # ── Transactions ─────────────────────────────────────────
    def record_transaction(self, data: dict):
        try:
            row = [{
                "transaction_id":  int(data.get("transaction_id", 0)),
                "reference_id":    data.get("reference_id", ""),
                "from_account_id": data.get("from_account_id"),
                "to_account_id":   data.get("to_account_id"),
                "bank_id":         data.get("bank_id"),
                "transaction_type": data.get("type", ""),
                "amount":          float(data.get("amount", 0)),
                "currency":        "INR",
                "status":          data.get("status", ""),
                "created_at":      datetime.now(timezone.utc).isoformat(),
            }]
            self._insert(TXN_TABLE, row)
            self._write_ledger(data)
        except Exception as e:
            logger.error(f"BQ transaction write failed: {e}")

    def _write_ledger(self, data: dict):
        rows = [
            {
                "transaction_id": int(data.get("transaction_id", 0)),
                "account_id":     entry.get("account_id"),
                "entry_type":     entry.get("entry_type", ""),
                "amount":         float(entry.get("amount", 0)),
                "running_balance": float(entry.get("running_balance", 0)),
                "created_at":     datetime.now(timezone.utc).isoformat(),
            }
            for entry in data.get("ledger_entries", [])
        ]
        if rows:
            self._insert(LEDGER_TABLE, rows)

    # ── User Registrations ───────────────────────────────────
    def record_user(self, data: dict):
        try:
            row = [{
                "user_id":        data.get("user_id"),
                "full_name":      data.get("full_name", ""),
                "email":          data.get("email", ""),
                "phone":          data.get("phone", ""),
                "account_number": data.get("account_number", ""),
                "bank_name":      data.get("bank_name", ""),
                "branch_name":    data.get("branch_name", ""),
                "registered_at":  datetime.now(timezone.utc).isoformat(),
            }]
            self._insert(USERS_TABLE, row)
        except Exception as e:
            logger.error(f"BQ user write failed: {e}")

    # ── Fraud Alerts ─────────────────────────────────────────
    def record_fraud(self, data: dict):
        try:
            row = [{
                "transaction_id":   str(data.get("transaction_id", "")),
                "account_id":       data.get("account_id"),
                "amount":           float(data.get("amount", 0)),
                "transaction_type": data.get("transaction_type", ""),
                "reason":           data.get("reason", ""),
                "severity":         data.get("severity", "HIGH"),
                "detected_at":      datetime.now(timezone.utc).isoformat(),
            }]
            self._insert(FRAUD_TABLE, row)
        except Exception as e:
            logger.error(f"BQ fraud write failed: {e}")

    # ── Simulation Logs ──────────────────────────────────────
    def record_simulation(self, data: dict):
        try:
            row = [{
                "accounts_created":   data.get("accounts_created", 0),
                "transfers_executed": data.get("transfers_executed", 0),
                "transfers_skipped":  data.get("transfers_skipped", 0),
                "initial_deposit":    data.get("initial_deposit", 0),
                "simulated_at":       datetime.now(timezone.utc).isoformat(),
            }]
            self._insert(SIM_TABLE, row)
        except Exception as e:
            logger.error(f"BQ simulation write failed: {e}")

    # ── Helper ───────────────────────────────────────────────
    def _insert(self, table: str, rows: list):
        errors = self.client.insert_rows_json(table, rows)
        if errors:
            logger.error(f"BQ insert error | table={table} | {errors}")
        else:
            logger.info(f"BQ written | table={table} | rows={len(rows)}")