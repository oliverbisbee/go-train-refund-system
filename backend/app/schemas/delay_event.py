from pydantic import BaseModel
from datetime import datetime
from uuid import UUID


class DelayEventResponse(BaseModel):
    id: UUID
    trip_id: str
    route_id: str
    origin_stop_id: str
    destination_stop_id: str
    scheduled_departure: datetime
    delay_seconds: int
    trip_completed: bool
    email_generated: bool

    class Config:
        from_attributes = True