from pydantic import BaseModel, EmailStr
from datetime import time
from uuid import UUID


class SubscriptionCreate(BaseModel):
    route_id: str
    day_of_week: str
    origin_stop_id: str
    destination_stop_id: str
    scheduled_departure_time: time
    scheduled_arrival_time: time
    email: EmailStr


class SubscriptionResponse(BaseModel):
    id: UUID
    route_id: str
    day_of_week: str
    origin_stop_id: str
    destination_stop_id: str
    scheduled_departure_time: time
    scheduled_arrival_time: time
    email: str
    verified: bool

    class Config:
        from_attributes = True