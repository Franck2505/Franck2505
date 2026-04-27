from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Float, Boolean
from app.models.base_types import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    REPLIED = "replied"
    INTERESTED = "interested"
    CONVERTED = "converted"
    NOT_INTERESTED = "not_interested"
    BOUNCED = "bounced"


class LeadSource(str, enum.Enum):
    GOOGLE_MAPS = "google_maps"
    LINKEDIN = "linkedin"
    DIRECTORIES = "directories"
    MANUAL = "manual"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    client_id = Column(GUID(), ForeignKey("clients.id"), nullable=False)
    business_name = Column(String)
    contact_name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    address = Column(String, nullable=True)
    source = Column(Enum(LeadSource), default=LeadSource.GOOGLE_MAPS)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    score = Column(Float, default=0.0)
    is_email_verified = Column(Boolean, default=False)
    last_contacted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    client = relationship("Client", back_populates="leads")
    campaign_emails = relationship("CampaignEmail", back_populates="lead")
