import re

from app.notifications.base import NotificationStrategy, logger


class EmailNotificationStrategy(NotificationStrategy):
    """
    Handles Email notifications. Validates format and simulates sending.
    """

    def send(self, recipient: str, title: str, content: str) -> bool:
        # 1. Validate email format
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, recipient):
            logger.error(f"Invalid email format: {recipient}")
            return False

        # 2. Generate template (Simulated)
        html_template = f"<h1>{title}</h1><p>{content}</p>"

        # 3. Log delivery (Simulated)
        logger.info(f"Simulating Email sent to {recipient}. Body: {html_template}")
        return True
