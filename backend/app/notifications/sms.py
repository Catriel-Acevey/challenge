from datetime import datetime

from app.notifications.base import NotificationStrategy, logger


class SMSNotificationStrategy(NotificationStrategy):
    """
    Handles SMS notifications. Enforces 160 char limit.
    """

    def send(self, recipient: str, title: str, content: str) -> bool:
        # 1. Validate content length
        full_message = f"{title}: {content}"
        if len(full_message) > 160:
            logger.error("SMS content exceeds 160 characters limit")
            return False

        # 2. Log delivery (Simulated)
        timestamp = datetime.utcnow().isoformat()
        logger.info(f"[{timestamp}] Simulating SMS sent to {recipient}: {full_message}")
        return True
