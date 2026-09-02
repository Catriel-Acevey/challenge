import json

from app.notifications.base import NotificationStrategy, logger


class PushNotificationStrategy(NotificationStrategy):
    """
    Handles Push Notifications. Validates token format and builds JSON payload.
    """

    def send(self, recipient: str, title: str, content: str) -> bool:
        # 1. Validate token format (Simulated constraint: min length)
        if len(recipient) < 10:
            logger.error(f"Invalid device token: {recipient}")
            return False

        # 2. Format payload
        payload = json.dumps(
            {"title": title, "body": content, "badge": 1, "sound": "default"}
        )

        # 3. Log delivery (Simulated)
        logger.info(
            f"Simulating Push Notification sent to token {recipient}. "
            f"Payload: {payload}"
        )
        return True
