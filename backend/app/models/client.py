from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, ForeignKey, JSON
from app.models.base_types import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class BusinessSector(str, enum.Enum):
    REAL_ESTATE = "real_estate"
    RESTAURANTS = "restaurants"
    HEALTHCARE = "healthcare"
    LEGAL = "legal"
    ACCOUNTING = "accounting"
    CONSTRUCTION = "construction"
    RETAIL = "retail"
    IT_SERVICES = "it_services"
    COACHING = "coaching"
    OTHER = "other"


class Client(Base):
    __tablename__ = "clients"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    owner_id = Column(GUID(), ForeignKey("users.id"), nullable=False)
    business_name = Column(String, nullable=False)
    sector = Column(Enum(BusinessSector), nullable=False)
    target_location = Column(String)
    target_keywords = Column(JSON, default=list)
    website = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="clients")
    leads = relationship("Lead", back_populates="client")
    campaigns = relationship("Campaign", back_populates="client")
