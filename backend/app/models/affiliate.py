import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base
from app.models.base_types import GUID


class PayoutStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    FAILED = "failed"


class Affiliate(Base):
    __tablename__ = "affiliates"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), unique=True, nullable=False)
    referral_code = Column(String(16), unique=True, nullable=False, index=True)
    total_referrals = Column(Integer, default=0)
    total_earned = Column(Float, default=0.0)
    total_paid = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    referrals = relationship("Referral", back_populates="affiliate")
    payouts = relationship("AffiliatePayout", back_populates="affiliate")


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    affiliate_id = Column(GUID, ForeignKey("affiliates.id"), nullable=False)
    referred_user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    plan = Column(String, nullable=False)
    commission_eur = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    affiliate = relationship("Affiliate", back_populates="referrals")
    referred_user = relationship("User", foreign_keys=[referred_user_id])


class AffiliatePayout(Base):
    __tablename__ = "affiliate_payouts"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    affiliate_id = Column(GUID, ForeignKey("affiliates.id"), nullable=False)
    amount = Column(Float, nullable=False)
    paypal_email = Column(String, nullable=False)
    status = Column(SAEnum(PayoutStatus), default=PayoutStatus.PENDING)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    affiliate = relationship("Affiliate", back_populates="payouts")
