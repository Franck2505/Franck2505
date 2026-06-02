import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base_types import GUID


class ABTest(Base):
    __tablename__ = "ab_tests"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    subject_a = Column(String, nullable=False)
    subject_b = Column(String, nullable=False)
    body_a = Column(Text, nullable=False)
    body_b = Column(Text, nullable=False)
    sent_a = Column(Integer, default=0)
    sent_b = Column(Integer, default=0)
    opens_a = Column(Integer, default=0)
    opens_b = Column(Integer, default=0)
    replies_a = Column(Integer, default=0)
    replies_b = Column(Integer, default=0)
    winner = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")

    @property
    def open_rate_a(self):
        return round(self.opens_a / max(self.sent_a, 1) * 100, 1)

    @property
    def open_rate_b(self):
        return round(self.opens_b / max(self.sent_b, 1) * 100, 1)


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    url = Column(String, nullable=False)
    secret = Column(String, nullable=False)
    events = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    total_deliveries = Column(Integer, default=0)
    total_failures = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
