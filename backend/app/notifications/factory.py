from app.models.notification import NotificationChannel
from app.notifications.base import NotificationStrategy
from app.notifications.email import EmailNotificationStrategy
from app.notifications.push import PushNotificationStrategy
from app.notifications.sms import SMSNotificationStrategy


class NotificationFactory:
    """
    Factory to retrieve the appropriate notification strategy based on channel enum.
    """

    _strategies: dict[NotificationChannel, NotificationStrategy] = {
        NotificationChannel.EMAIL: EmailNotificationStrategy(),
        NotificationChannel.SMS: SMSNotificationStrategy(),
        NotificationChannel.PUSH: PushNotificationStrategy(),
    }

    @classmethod
    def get_strategy(cls, channel: NotificationChannel) -> NotificationStrategy:
        """
        Returns the instantiated strategy for the requested channel.
        Raises ValueError if the channel is not supported.
        """
        strategy = cls._strategies.get(channel)
        if not strategy:
            raise ValueError(f"No strategy implemented for channel: {channel}")
        return strategy
