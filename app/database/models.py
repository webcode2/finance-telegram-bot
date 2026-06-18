from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import enum

class SubscriptionPlan(str, enum.Enum):
    HOURLY = "hourly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class UserStatus(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    EXPIRED = "expired"

class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"

class User(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    subscription_status: UserStatus = UserStatus.FREE
    subscription_end_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Payment(BaseModel):
    user_id: str  # String of telegram_id
    paystack_reference: str
    amount: int
    status: PaymentStatus = PaymentStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Subscription(BaseModel):
    user_id: str
    plan_type: SubscriptionPlan
    start_date: datetime
    end_date: datetime

class InviteLink(BaseModel):
    user_id: str
    link: str
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class WebhookEvent(BaseModel):
    id: str  # Paystack event ID
    processed_at: datetime = Field(default_factory=datetime.utcnow)
