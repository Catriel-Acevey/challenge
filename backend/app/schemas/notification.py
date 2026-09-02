from datetime import datetime

from pydantic import BaseModel, Field

from app.models.notification import NotificationChannel, NotificationStatus


# Request schema for notification creation
class NotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    channel: NotificationChannel
    recipient: str = Field(
        ...,
        min_length=1,
        description="Email address, phone number, or device token depending on channel",
    )


# Request schema for notification update
class NotificationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)


# Response schema for notification output
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    channel: NotificationChannel
    recipient: str
    status: NotificationStatus
    created_at: datetime

    class Config:
        from_attributes = True
