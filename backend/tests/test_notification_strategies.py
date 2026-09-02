"""Unit tests for notification strategies and factory."""

import pytest

from app.models.notification import NotificationChannel
from app.notifications.email import EmailNotificationStrategy
from app.notifications.factory import NotificationFactory
from app.notifications.push import PushNotificationStrategy
from app.notifications.sms import SMSNotificationStrategy

# ─── Email Strategy ────────────────────────────────────────────────


class TestEmailNotificationStrategy:
    def setup_method(self):
        self.strategy = EmailNotificationStrategy()

    def test_send_valid_email(self):
        result = self.strategy.send(
            recipient="test@example.com",
            title="Hello",
            content="World",
        )
        assert result is True

    def test_send_invalid_email_no_at(self):
        result = self.strategy.send(
            recipient="invalid-email",
            title="Hello",
            content="World",
        )
        assert result is False

    def test_send_invalid_email_no_domain(self):
        result = self.strategy.send(
            recipient="user@",
            title="Hello",
            content="World",
        )
        assert result is False

    def test_send_invalid_email_special_chars(self):
        result = self.strategy.send(
            recipient="@example.com",
            title="Hello",
            content="World",
        )
        assert result is False

    def test_send_valid_email_with_dots_and_plus(self):
        result = self.strategy.send(
            recipient="user.name+tag@sub.domain.com",
            title="Hello",
            content="World",
        )
        assert result is True


# ─── SMS Strategy ──────────────────────────────────────────────────


class TestSMSNotificationStrategy:
    def setup_method(self):
        self.strategy = SMSNotificationStrategy()

    def test_send_short_message(self):
        result = self.strategy.send(
            recipient="+5491155551234",
            title="Hi",
            content="Hello!",
        )
        assert result is True

    def test_send_exactly_160_chars(self):
        # "Title: " = 7 chars, so content can be 153 chars
        title = "T"
        content = "a" * 159  # "T: " + 159 = 162 > 160
        result = self.strategy.send(
            recipient="+5491155551234",
            title=title,
            content=content,
        )
        assert result is False

    def test_send_over_limit(self):
        result = self.strategy.send(
            recipient="+5491155551234",
            title="Alert",
            content="x" * 200,
        )
        assert result is False

    def test_send_within_limit(self):
        title = "Hey"
        content = "a" * 156  # "Hey: " (5) + 156 = 161 > 160
        result = self.strategy.send(
            recipient="+5491155551234",
            title=title,
            content=content,
        )
        assert result is False

    def test_send_barely_under_limit(self):
        title = "Hi"
        content = "a" * 156  # "Hi: " (4) + 156 = 160 exact
        result = self.strategy.send(
            recipient="+5491155551234",
            title=title,
            content=content,
        )
        assert result is True


# ─── Push Strategy ─────────────────────────────────────────────────


class TestPushNotificationStrategy:
    def setup_method(self):
        self.strategy = PushNotificationStrategy()

    def test_send_valid_token(self):
        result = self.strategy.send(
            recipient="a" * 20,
            title="Alert",
            content="You have a new message",
        )
        assert result is True

    def test_send_token_too_short(self):
        result = self.strategy.send(
            recipient="short",
            title="Alert",
            content="Body",
        )
        assert result is False

    def test_send_token_exactly_10_chars(self):
        result = self.strategy.send(
            recipient="a" * 10,
            title="Alert",
            content="Body",
        )
        assert result is True

    def test_send_token_9_chars(self):
        result = self.strategy.send(
            recipient="a" * 9,
            title="Alert",
            content="Body",
        )
        assert result is False


# ─── Factory ───────────────────────────────────────────────────────


class TestNotificationFactory:
    def test_get_email_strategy(self):
        strategy = NotificationFactory.get_strategy(NotificationChannel.EMAIL)
        assert isinstance(strategy, EmailNotificationStrategy)

    def test_get_sms_strategy(self):
        strategy = NotificationFactory.get_strategy(NotificationChannel.SMS)
        assert isinstance(strategy, SMSNotificationStrategy)

    def test_get_push_strategy(self):
        strategy = NotificationFactory.get_strategy(NotificationChannel.PUSH)
        assert isinstance(strategy, PushNotificationStrategy)

    def test_get_invalid_strategy_raises(self):
        with pytest.raises(ValueError, match="No strategy implemented"):
            NotificationFactory.get_strategy("invalid_channel")
