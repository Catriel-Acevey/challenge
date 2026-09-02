from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.notification import Notification, NotificationStatus
from app.models.user import User
from app.notifications.factory import NotificationFactory
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)

router = APIRouter()


@router.post(
    "/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED
)
def create_notification(
    notification_in: NotificationCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create and trigger a new notification dispatch.
    """
    # 1. Execute strategy logic according to the channel
    try:
        strategy = NotificationFactory.get_strategy(notification_in.channel)
        is_sent = strategy.send(
            recipient=notification_in.recipient,
            title=notification_in.title,
            content=notification_in.content,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # 2. Throw 400 if validation/delivery failed in strategy (before persisting)
    if not is_sent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send notification via {notification_in.channel.value}. Check logs/recipient format.",
        )

    # 3. Persist notification in database
    initial_status = NotificationStatus.SENT
    db_notification = Notification(
        title=notification_in.title,
        content=notification_in.content,
        channel=notification_in.channel.value,
        recipient=notification_in.recipient,
        user_id=current_user.id,
        status=initial_status.value,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    return db_notification


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Retrieve all notifications owned by current user.
    """
    return (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Get a specific notification by ID.
    """
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification


@router.put("/{notification_id}", response_model=NotificationResponse)
def update_notification(
    notification_id: int,
    notification_in: NotificationUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Update a notification's title or content.
    """
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    update_data = notification_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(notification, field, value)

    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Delete a notification by ID.
    """
    notification = (
        db.query(Notification)
        .filter(
            Notification.id == notification_id,
            Notification.user_id == current_user.id,
        )
        .first()
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    db.delete(notification)
    db.commit()
    return None
