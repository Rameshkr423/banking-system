import os
from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    def send(self, event: dict):
        event_type = event.get("event_type")
        user_id    = event.get("user_id")
        amount     = event.get("amount")

        logger.info(
            f"[Notification] {event_type} | user={user_id} | amount={amount}"
        )

        # ── Extend here ──────────────────────────────────────
        # e.g. SendGrid email, Firebase push notification, SMS
        # sendgrid_client.send(to=user_email, subject=..., body=...)