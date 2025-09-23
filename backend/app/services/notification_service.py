import logging
from typing import Optional

from .. import sns_utils

logger = logging.getLogger(__name__)


class NotificationService:
    def send_itinerary_notification(self, user_email: str, itinerary_id: str) -> None:
        try:
            message = f"A new itinerary ({itinerary_id}) has been created for {user_email}."
            sns_utils.publish(message, subject="Itinerary Created")
        except Exception as exc:
            logger.warning("Failed to publish SNS notification: %s", exc)


notification_service = NotificationService()
