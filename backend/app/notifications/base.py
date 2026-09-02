import abc
import logging

logger = logging.getLogger(__name__)


class NotificationStrategy(abc.ABC):
    """
    Abstract base class for notification channels.
    All channels must implement the send method.
    """

    @abc.abstractmethod
    def send(self, recipient: str, title: str, content: str) -> bool:
        """
        Executes the logic to send a notification.

        Args:
            recipient: The destination address/number/token.
            title: Notification title.
            content: Notification body.

        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        pass
