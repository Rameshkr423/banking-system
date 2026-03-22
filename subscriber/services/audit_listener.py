import json
import base64
from utils.logger import get_logger
from services.notification_service import NotificationService
from services.analytics_service import AnalyticsService

logger = get_logger(__name__)


class AuditListener:
    """
    Push-based listener — no streaming pull, no min-instances cost.
    Pub/Sub POSTs each message to our HTTP endpoint.
    FastAPI route decodes the envelope and calls handle_push_message().
    """

    def handle_push_message(self, envelope: dict, subscription_id: str = "unknown") -> bool:
        """
        envelope format from Pub/Sub push:
        {
          "message": {
            "data": "<base64-encoded JSON string>",
            "messageId": "...",
            "attributes": {}
          },
          "subscription": "projects/.../subscriptions/..."
        }
        Returns True  → caller responds HTTP 200 (Pub/Sub acks the message)
        Returns False → caller responds HTTP 500 (Pub/Sub will retry)
        """
        try:
            message  = envelope.get("message", {})
            raw_data = message.get("data", "")

            # Pub/Sub always base64-encodes the payload
            decoded    = base64.b64decode(raw_data).decode("utf-8")
            data       = json.loads(decoded)
            event_type = data.get("event_type")

            logger.info(f"Received: {event_type} | sub={subscription_id}")

            analytics    = AnalyticsService()
            notification = NotificationService()

            if event_type == "transaction_completed":
                analytics.record_transaction(data)
                notification.send(data)

            elif event_type == "user_registered":
                analytics.record_user(data)
                notification.send(data)

            elif event_type == "fraud_alert":
                analytics.record_fraud(data)
                notification.send(data)

            elif event_type == "simulation_completed":
                analytics.record_simulation(data)

            else:
                # Unknown event — still ack to avoid poison-pill retries
                logger.warning(f"Unknown event_type '{event_type}' | sub={subscription_id}")

            logger.info(f"Acked: {event_type} | sub={subscription_id}")
            return True

        except Exception as e:
            logger.error(f"Message processing failed [{subscription_id}]: {e}", exc_info=True)
            return False  # Pub/Sub will retry after ack deadline