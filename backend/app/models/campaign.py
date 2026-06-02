from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Integer, Boolean, Text, JSON
from app.models.base_types import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"
    BOUNCED = "bounced"
    UNSUBSCRIBED = "unsubscribed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(GUID(), ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    sequence_days = Column(JSON, default=lambda: [0, 3, 7, 14])  # follow-up intervals
    email_subject = Column(String)
    email_body_template = Column(Text)
    total_sent = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_replied = Column(Integer, default=0)
    total_converted = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)

    client = relationship("Client", back_populates="campaigns")
    emails = relationship("CampaignEmail", back_populates="campaign")


class CampaignEmail(Base):
    __tablename__ = "campaign_emails"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(GUID(), ForeignKey("campaigns.id"), nullable=False)
    lead_id = Column(GUID(), ForeignKey("leads.id"), nullable=False)
    sequence_step = Column(Integer, default=0)
    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING)
    subject = Column(String)
    body = Column(Text)
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True), nullable=True)
    opened_at = Column(DateTime(timezone=True), nullable=True)
    tracking_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))

    campaign = relationship("Campaign", back_populates="emails")
    lead = relationship("Lead", back_populates="campaign_emails")
