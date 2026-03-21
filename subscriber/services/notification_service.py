import os
from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    def send(self, data: dict):
        event_type = data.get("event_type")

        if event_type == "transaction_completed":
            txn_type = data.get("type")
            amount   = data.get("amount")
            if txn_type == "deposit":
                logger.info(f"[Notification] Deposit ₹{amount} to account {data.get('to_account_id')}")
            elif txn_type == "withdraw":
                logger.info(f"[Notification] Withdrawal ₹{amount} from account {data.get('from_account_id')}")
            elif txn_type == "transfer":
                logger.info(f"[Notification] Transfer ₹{amount} from {data.get('from_account_id')} to {data.get('to_account_id')}")

        elif event_type == "user_registered":
            logger.info(f"[Notification] New user registered: {data.get('full_name')} | {data.get('phone')}")

        elif event_type == "fraud_alert":
            logger.warning(f"[FRAUD ALERT] txn={data.get('transaction_id')} | amount=₹{data.get('amount')} | reason={data.get('reason')}")

        # ── Extend: SendGrid, Firebase, SMS ──────────────────