from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.models.notification import NotificationType, NotificationChannel, NotificationStatus


class NotificationLog(BaseModel):
    """Schema for notification log entry."""
    id: int
    order_id: int
    type: NotificationType
    channel: NotificationChannel
    status: NotificationStatus
    phone_hash: str  # SHA-256 hash, not actual phone
    provider_request_id: Optional[str] = None
    message_url: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True
