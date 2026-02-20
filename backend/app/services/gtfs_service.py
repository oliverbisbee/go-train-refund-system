import requests
from google.transit import gtfs_realtime_pb2
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
from app.core.config import settings


class GTFSService:
    def __init__(self):
        self.api_key = settings.OPENMETROLINX_API_KEY
        self.realtime_url = settings.GTFS_REALTIME_URL
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def fetch_trip_updates(self) -> gtfs_realtime_pb2.FeedMessage:
        """Fetch GTFS Realtime TripUpdates feed"""
        try:
            response = requests.get(
                self.realtime_url,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            return feed
        except Exception as e:
            print(f"Error fetching GTFS feed: {e}")
            raise

    def get_delays_for_route(self, route_id: str) -> List[Dict]:
        """
        Parse TripUpdates and extract delays for a specific route
        Returns list of dicts with delay information
        """
        feed = self.fetch_trip_updates()
        delays = []

        for entity in feed.entity:
            if entity.HasField('trip_update'):
                trip_update = entity.trip_update
                trip = trip_update.trip

                # Filter by route_id (e.g., "01" for Lakeshore West)
                if trip.route_id != route_id:
                    continue

                # Extract stop time updates
                for stop_time_update in trip_update.stop_time_update:
                    if stop_time_update.HasField('arrival'):
                        delay_seconds = stop_time_update.arrival.delay
                        
                        delays.append({
                            'trip_id': trip.trip_id,
                            'route_id': trip.route_id,
                            'stop_id': stop_time_update.stop_id,
                            'scheduled_arrival': stop_time_update.arrival.time,
                            'delay_seconds': delay_seconds,
                            'timestamp': datetime.fromtimestamp(feed.header.timestamp)
                        })

        return delays

    def is_within_time_window(
        self, 
        scheduled_time: time, 
        feed_time: datetime, 
        window_seconds: int = 300
    ) -> bool:
        """
        Check if feed time is within ±window_seconds of scheduled time
        Default window: 5 minutes (300 seconds)
        """
        # Convert scheduled_time to today's datetime for comparison
        today = datetime.now().date()
        scheduled_dt = datetime.combine(today, scheduled_time)
        
        # Extract time from feed datetime
        feed_time_only = feed_time.time()
        feed_dt = datetime.combine(today, feed_time_only)
        
        diff = abs((scheduled_dt - feed_dt).total_seconds())
        return diff <= window_seconds


gtfs_service = GTFSService()