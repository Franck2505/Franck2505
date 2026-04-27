from sqlalchemy import Column, String, Boolean, DateTime, Enum
from app.models.base_types import GUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    CLIENT = "client"


class User(Base):
    __tablename__ = "users"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    stripe_customer_id = Column(String, unique=True, nullable=True)

    # Internationalisation
    language = Column(String(5), default="fr")       # ISO 639-1
    country = Column(String(2), default="FR")         # ISO 3166-1 alpha-2
    timezone = Column(String(50), default="Europe/Paris")
    currency = Column(String(3), default="EUR")       # ISO 4217

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    subscription = relationship("Subscription", back_populates="user", uselist=False)
    clients = relationship("Client", back_populates="owner")
