from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.schemas.delay_event import DelayEventResponse
from app.models.subscription import Subscription
from app.models.delay_event import DelayEvent

router = APIRouter()


@router.get("/routes")
def get_routes():
    """Return available routes (hardcoded for MVP)"""
    return [
        {
            "route_id": "LW",
            "route_name": "Lakeshore West",
            "description": "Union Station to Aldershot GO"
        }
    ]


@router.get("/stops")
def get_stops(route_id: str):
    """Return stops for a given route (hardcoded for MVP - Lakeshore West)"""
    if route_id != "01":
        raise HTTPException(status_code=404, detail="Route not found")
    
    # This would normally come from GTFS Static data
    # For MVP, hardcode Lakeshore West stops
    return [
        {"stop_id": "USTN", "stop_name": "Union Station"},
        {"stop_id": "EXHI", "stop_name": "Exhibition"},
        {"stop_id": "MIMI", "stop_name": "Mimico"},
        {"stop_id": "LONG", "stop_name": "Long Branch"},
        {"stop_id": "PORT", "stop_name": "Port Credit"},
        {"stop_id": "CLAR", "stop_name": "Clarkson"},
        {"stop_id": "OAKV", "stop_name": "Oakville"},
        {"stop_id": "BURL", "stop_name": "Burlington"},
        {"stop_id": "APPL", "stop_name": "Appleby"},
        {"stop_id": "ALDN", "stop_name": "Aldershot"}
    ]


@router.get("/trains")
def get_trains(
    route_id: str,
    day: str,
    origin_stop: str,
    destination_stop: str
):
    """
    Return available trains for given criteria
    This would parse GTFS Static schedule data
    For MVP, return hardcoded sample trains
    """
    # TODO: Implement actual GTFS Static parsing
    # For now, return sample data
    return [
        {
            "trip_id": "LSW_001",
            "departure_time": "06:15:00",
            "arrival_time": "07:15:00",
            "duration_minutes": 60
        },
        {
            "trip_id": "LSW_002",
            "departure_time": "07:15:00",
            "arrival_time": "08:15:00",
            "duration_minutes": 60
        },
        {
            "trip_id": "LSW_003",
            "departure_time": "08:15:00",
            "arrival_time": "09:15:00",
            "duration_minutes": 60
        }
    ]


@router.post("/subscriptions", response_model=SubscriptionResponse)
def create_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db)
):
    """Create a new subscription"""
    db_subscription = Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription


@router.get("/delayed_trains", response_model=List[DelayEventResponse])
def get_delayed_trains(db: Session = Depends(get_db)):
    """Get all currently delayed trains (system-wide dashboard)"""
    delayed = db.query(DelayEvent).filter(
        DelayEvent.delay_seconds >= 900,
        DelayEvent.trip_completed == True
    ).all()
    return delayed


@router.post("/generate_email")
def generate_email(delay_event_id: str, db: Session = Depends(get_db)):
    """Generate refund email draft for a specific delay event"""
    from uuid import UUID
    
    event = db.query(DelayEvent).filter(
        DelayEvent.id == UUID(delay_event_id)
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Delay event not found")
    
    if event.email_generated:
        raise HTTPException(status_code=400, detail="Email already generated")
    
    # Get subscription details
    subscription = db.query(Subscription).filter(
        Subscription.id == event.subscription_id
    ).first()
    
    # Generate email content
    delay_minutes = event.delay_seconds // 60
    
    email_content = f"""Subject: GO Transit Refund Request - {event.scheduled_departure.strftime('%B %d, %Y')}

Dear GO Transit Customer Service,

I am requesting compensation under the GO Transit Service Guarantee policy for the following delayed trip:

Route: Lakeshore West
Origin: {event.origin_stop_id}
Destination: {event.destination_stop_id}
Date: {event.scheduled_departure.strftime('%B %d, %Y')}
Scheduled Departure: {event.scheduled_departure.strftime('%I:%M %p')}
Scheduled Arrival: {event.scheduled_arrival.strftime('%I:%M %p')}
Actual Arrival: {event.actual_arrival.strftime('%I:%M %p')}
Delay: {delay_minutes} minutes

This delay exceeds the 15-minute service guarantee threshold.

Thank you for your attention to this matter.

Sincerely,
{subscription.email}
"""
    
    # Mark email as generated
    event.email_generated = True
    db.commit()
    
    return {
        "email_content": email_content,
        "delay_event_id": str(event.id)
    }