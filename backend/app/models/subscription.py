from sqlalchemy import Column, String, Time, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.base_class import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    route_id = Column(String, nullable=False)  # e.g., "01" for Lakeshore West
    day_of_week = Column(String, nullable=False)  # e.g., "monday"
    origin_stop_id = Column(String, nullable=False)
    destination_stop_id = Column(String, nullable=False)
    scheduled_departure_time = Column(Time, nullable=False)
    scheduled_arrival_time = Column(Time, nullable=False)
    email = Column(String, nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())