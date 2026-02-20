from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base_class import Base


class DelayEvent(Base):
    __tablename__ = "delay_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(String, nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=False)
    route_id = Column(String, nullable=False)
    origin_stop_id = Column(String, nullable=False)
    destination_stop_id = Column(String, nullable=False)
    scheduled_departure = Column(DateTime(timezone=True), nullable=False)
    scheduled_arrival = Column(DateTime(timezone=True), nullable=True)
    actual_arrival = Column(DateTime(timezone=True), nullable=True)
    delay_seconds = Column(Integer, nullable=False)
    trip_completed = Column(Boolean, default=False)
    email_generated = Column(Boolean, default=False)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('trip_id', 'scheduled_departure', 'subscription_id', 
                        name='unique_trip_per_day_per_subscription'),
    )