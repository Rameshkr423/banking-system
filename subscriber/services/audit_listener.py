import os
import json
import asyncio
from google.cloud import pubsub_v1
from utils.logger import get_logger
from services.notification_service import NotificationService
from services.analytics_service import AnalyticsService

logger = get_logger(__name__)


class AuditListener:
    def __init__(self):
        self.project_id = os.getenv("PROJECT_ID")
        self.subscription_id = os.getenv("PUBSUB_SUBSCRIPTION", "banking-events-sub")
        self.is_running = False
        self._subscriber = None

    async def start(self):
        self.is_running = True
        self._subscriber = pubsub_v1.SubscriberClient()
        subscription_path = self._subscriber.subscription_path(
            self.project_id,
            self.subscription_id
        )
        logger.info(f"Listening on {subscription_path}")

        # Run blocking pull in thread pool so it doesn't block event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._pull_messages, subscription_path)

    def _pull_messages(self, subscription_path: str):
        streaming_pull = self._subscriber.subscribe(
            subscription_path,
            callback=self._handle_message
        )
        try:
            streaming_pull.result()
        except Exception as e:
            logger.error(f"Subscriber error: {e}")
            streaming_pull.cancel()

    def _handle_message(self, message):
        try:
            data = json.loads(message.data.decode("utf-8"))
            event_type = data.get("event_type")
            logger.info(f"Received event: {event_type}")

            notification_service = NotificationService()
            analytics_service = AnalyticsService()

            # Route event to correct handler
            if event_type in ("DEPOSIT", "WITHDRAWAL", "TRANSFER"):
                notification_service.send(data)
                analytics_service.record(data)
            elif event_type == "AUDIT":
                analytics_service.record(data)

            message.ack()

        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            message.nack()

    async def stop(self):
        self.is_running = False
        if self._subscriber:
            self._subscriber.close()