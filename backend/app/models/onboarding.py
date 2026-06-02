import uuid
from datetime import datetime
from sqlalchemy import Column, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base_types import GUID


class OnboardingProgress(Base):
    __tablename__ = "onboarding_progress"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), unique=True, nullable=False)
    subscription_activated = Column(Boolean, default=False)
    last_email_step = Column(Integer, default=-1)
    last_email_sent_at = Column(DateTime, nullable=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
