import os
import json
import asyncio
from google.cloud import pubsub_v1
from utils.logger import get_logger
from services.notification_service import NotificationService
from services.analytics_service import AnalyticsService

logger = get_logger(__name__)


class AuditListener:
    def __init__(self, subscription_id: str = None):
        self.project_id      = os.getenv("GCP_PROJECT_ID", "banking-system-prod")
        self.subscription_id = subscription_id or os.getenv(
            "PUBSUB_SUBSCRIPTION", "transaction-events-sub"
        )
        self.is_running  = False
        self._subscriber = None

    async def start(self):
        self.is_running = True
        logger.info(f"Starting listener for {self.subscription_id}")

        # ── Auto-reconnect loop ───────────────────────────────
        while self.is_running:
            try:
                await self._connect_and_pull()
            except Exception as e:
                logger.error(f"Listener crashed: {e} — reconnecting in 5s...")
                await asyncio.sleep(5)

    async def _connect_and_pull(self):
        self._subscriber = pubsub_v1.SubscriberClient()
        subscription_path = self._subscriber.subscription_path(
            self.project_id, self.subscription_id
        )
        logger.info(f"Listening on {subscription_path}")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._pull_messages, subscription_path)

    def _pull_messages(self, subscription_path: str):
        streaming_pull = self._subscriber.subscribe(
            subscription_path, callback=self._handle_message
        )
        try:
            streaming_pull.result()
        except Exception as e:
            logger.error(f"Subscriber error: {e}")
            streaming_pull.cancel()
            raise  # ← re-raise so auto-reconnect loop catches it

    def _handle_message(self, message):
        try:
            data       = json.loads(message.data.decode("utf-8"))
            event_type = data.get("event_type")
            logger.info(f"Received: {event_type} | sub={self.subscription_id}")

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

            message.ack()
            logger.info(f"Acked: {event_type}")

        except Exception as e:
            logger.error(f"Message processing failed: {e}")
            message.nack()

    async def stop(self):
        self.is_running = False
        if self._subscriber:
            self._subscriber.close()