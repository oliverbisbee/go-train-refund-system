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
        print(f"🔄 Background job running at {datetime.now()}")
        
        # Get today's day of week
        today = datetime.now().strftime('%A').lower()  # e.g., "monday"
        
        print(f"📅 Checking subscriptions for: {today}")
        
        # Get all subscriptions for today
        subscriptions = self.db.query(Subscription).filter(
            Subscription.day_of_week == today,
            Subscription.verified == True
        ).all()

        print(f"📊 Found {len(subscriptions)} verified subscriptions")

        if not subscriptions:
            print(f"No verified subscriptions for {today}")
            return

        # Fetch live delay data for Lakeshore West (route_id = "LW")
        print("🚂 Fetching live train data from API...")
        try:
            delays = gtfs_service.get_delays_for_route(route_id="LW")
            print(f"✅ Found {len(delays)} trains on route LW")

            # DEBUG: Show what routes are actually available
            print("\n📍 Available routes right now:")
            for d in delays:
                print(f"  {d['origin_stop']} → {d['destination_stop']} at {d['scheduled_start_time']} (Delay: {d['delay_seconds']}s)")
            print()

        except Exception as e:
            print(f"❌ Failed to fetch delays: {e}")
            return

        # Match delays to subscriptions
        print(f"🔍 Matching {len(delays)} trains to {len(subscriptions)} subscriptions...")
        for subscription in subscriptions:
            self._process_subscription(subscription, delays)
        
        print(f"✅ Background job completed at {datetime.now()}")

    def _process_subscription(self, subscription: Subscription, delays: List[dict]):
        """Process a single subscription against delay data"""
        
        print(f"\n🔎 Checking subscription: {subscription.origin_stop_id} → {subscription.destination_stop_id} at {subscription.scheduled_departure_time}")
        
        matched_route = False
        matched_time = False
        
        for delay_data in delays:
            # Match by origin and destination stops
            if delay_data['origin_stop'] != subscription.origin_stop_id:
                continue
            if delay_data['destination_stop'] != subscription.destination_stop_id:
                continue

            matched_route = True
            print(f"  ✓ Found matching route: Trip {delay_data['trip_id']} ({delay_data['scheduled_start_time']})")

            # Check if this delay matches the subscription's scheduled time
            if not gtfs_service.is_within_time_window(
                subscription.scheduled_departure_time,
                delay_data['scheduled_start_time'],
                self.TIME_MATCHING_WINDOW
            ):
                print(f"  ✗ Time mismatch: Train departs at {delay_data['scheduled_start_time']}, subscription is for {subscription.scheduled_departure_time}")
                continue

            matched_time = True
            print(f"  ✓ Time matches! Delay: {delay_data['delay_seconds']} seconds ({delay_data['delay_seconds']//60} minutes)")

            # We found a match! Check if delay is significant
            delay_seconds = delay_data['delay_seconds']
            
            if delay_seconds < self.DELAY_THRESHOLD_SECONDS:
                print(f"  ✗ Delay too small: {delay_seconds}s < {self.DELAY_THRESHOLD_SECONDS}s threshold")
                continue  # Not delayed enough

            print(f"  🎯 DELAY ELIGIBLE! Creating delay event...")

            # Check if we already have a delay_event for this trip today
            scheduled_departure_dt = datetime.combine(
                datetime.now().date(),
                subscription.scheduled_departure_time
            )

            existing_event = self.db.query(DelayEvent).filter(
                DelayEvent.trip_id == str(delay_data['trip_id']),
                DelayEvent.scheduled_departure == scheduled_departure_dt,
                DelayEvent.subscription_id == subscription.id
            ).first()

            if existing_event:
                # Update existing event
                existing_event.delay_seconds = delay_seconds
                existing_event.updated_at = datetime.now()
                existing_event.trip_completed = True  # Simplified for MVP
                print(f"  ✅ Updated existing delay event")
                
            else:
                # Create new delay event
                new_event = DelayEvent(
                    trip_id=str(delay_data['trip_id']),
                    subscription_id=subscription.id,
                    route_id=delay_data['route_id'],
                    origin_stop_id=subscription.origin_stop_id,
                    destination_stop_id=subscription.destination_stop_id,
                    scheduled_departure=scheduled_departure_dt,
                    scheduled_arrival=datetime.combine(
                        datetime.now().date(),
                        subscription.scheduled_arrival_time
                    ),
                    actual_arrival=None,  # Not available in this feed
                    delay_seconds=delay_seconds,
                    trip_completed=True,  # Simplified for MVP
                    email_generated=False
                )
                self.db.add(new_event)
                print(f"  ✅ Created new delay event")

            self.db.commit()
            print(f"✅ Detected delay: {delay_seconds}s for subscription {subscription.id}")
        
        if not matched_route:
            print(f"  ✗ No trains found matching route {subscription.origin_stop_id} → {subscription.destination_stop_id}")
        elif not matched_time:
            print(f"  ✗ Route matched but no trains at the scheduled time")