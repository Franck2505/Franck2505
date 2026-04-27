from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class PlanType(str, enum.Enum):
    STARTER = "starter"    # €299/month — 100 leads, 1 campaign
    GROWTH = "growth"      # €599/month — 500 leads, 5 campaigns
    PRO = "pro"            # €999/month — unlimited


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"


PLAN_LIMITS = {
    PlanType.STARTER: {"leads_per_month": 100, "campaigns": 1, "price_eur": 299},
    PlanType.GROWTH:  {"leads_per_month": 500, "campaigns": 5, "price_eur": 599},
    PlanType.PRO:     {"leads_per_month": 999999, "campaigns": 999999, "price_eur": 999},
}


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    plan = Column(Enum(PlanType), nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIALING)
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    leads_used_this_month = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    canceled_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="subscription")
