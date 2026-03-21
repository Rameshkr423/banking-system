import os
from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    def send(self, data: dict):
        event_type     = data.get("event_type")
        transaction_id = data.get("transaction_id")
        txn_type       = data.get("type")
        amount         = data.get("amount")
        from_acc       = data.get("from_account_id")
        to_acc         = data.get("to_account_id")

        if event_type == "transaction_completed":
            if txn_type == "deposit":
                logger.info(
                    f"[Notification] Deposit ₹{amount} "
                    f"to account {to_acc} | txn={transaction_id}"
                )
            elif txn_type == "withdraw":
                logger.info(
                    f"[Notification] Withdrawal ₹{amount} "
                    f"from account {from_acc} | txn={transaction_id}"
                )
            elif txn_type == "transfer":
                logger.info(
                    f"[Notification] Transfer ₹{amount} "
                    f"from {from_acc} to {to_acc} | txn={transaction_id}"
                )

        # ── Extend here ──────────────────────────────────
        # SendGrid email, Firebase push, SMS etc.