from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app.models.subscription import Subscription
from app.models.delay_event import DelayEvent
from app.services.gtfs_service import gtfs_service


class DelayDetector:
    DELAY_THRESHOLD_SECONDS = 900  # 15 minutes
    TIME_MATCHING_WINDOW = 300  # ±5 minutes

    def __init__(self, db: Session):
        self.db = db

    def check_delays_for_subscriptions(self):
        """
        Main function: Check all subscriptions for delays
        Called by background scheduler every 1-2 minutes
        """
        # Get today's day of week
        today = datetime.now().strftime('%A').lower()  # e.g., "monday"
        
        # Get all subscriptions for today
        subscriptions = self.db.query(Subscription).filter(
            Subscription.day_of_week == today,
            Subscription.verified == True
        ).all()

        if not subscriptions:
            print(f"No verified subscriptions for {today}")
            return

        # Fetch live delay data for Lakeshore West (route_id = "01")
        try:
            delays = gtfs_service.get_delays_for_route(route_id="01")
        except Exception as e:
            print(f"Failed to fetch delays: {e}")
            return

        # Match delays to subscriptions
        for subscription in subscriptions:
            self._process_subscription(subscription, delays)

    def _process_subscription(self, subscription: Subscription, delays: List[dict]):
        """Process a single subscription against delay data"""
        
        for delay_data in delays:
            # Match by stop_id and time window
            if delay_data['stop_id'] != subscription.destination_stop_id:
                continue

            # Check if this delay matches the subscription's scheduled time
            feed_arrival_time = datetime.fromtimestamp(delay_data['scheduled_arrival'])
            
            if not gtfs_service.is_within_time_window(
                subscription.scheduled_arrival_time,
                feed_arrival_time,
                self.TIME_MATCHING_WINDOW
            ):
                continue

            # We found a match! Check if delay is significant
            delay_seconds = delay_data['delay_seconds']
            
            if delay_seconds < self.DELAY_THRESHOLD_SECONDS:
                continue  # Not delayed enough

            # Check if we already have a delay_event for this trip today
            scheduled_departure_dt = datetime.combine(
                datetime.now().date(),
                subscription.scheduled_departure_time
            )

            existing_event = self.db.query(DelayEvent).filter(
                DelayEvent.trip_id == delay_data['trip_id'],
                DelayEvent.scheduled_departure == scheduled_departure_dt,
                DelayEvent.subscription_id == subscription.id
            ).first()

            if existing_event:
                # Update existing event
                existing_event.delay_seconds = delay_seconds
                existing_event.updated_at = datetime.now()
                
                # Check if trip is completed (we'll implement this logic next)
                # For now, assume trip is completed if delay data exists
                # In reality, you'd check if the train has reached destination
                existing_event.trip_completed = True
                
            else:
                # Create new delay event
                new_event = DelayEvent(
                    trip_id=delay_data['trip_id'],
                    subscription_id=subscription.id,
                    route_id=delay_data['route_id'],
                    origin_stop_id=subscription.origin_stop_id,
                    destination_stop_id=subscription.destination_stop_id,
                    scheduled_departure=scheduled_departure_dt,
                    scheduled_arrival=datetime.combine(
                        datetime.now().date(),
                        subscription.scheduled_arrival_time
                    ),
                    actual_arrival=feed_arrival_time + timedelta(seconds=delay_seconds),
                    delay_seconds=delay_seconds,
                    trip_completed=True,  # Simplified for now
                    email_generated=False
                )
                self.db.add(new_event)

            self.db.commit()
            print(f"Detected delay: {delay_seconds}s for subscription {subscription.id}")