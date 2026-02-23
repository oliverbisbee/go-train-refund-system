import requests
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
from app.core.config import settings


class GTFSService:
    def __init__(self):
        self.api_key = settings.OPENMETROLINX_API_KEY
        # Don't add .json - API returns JSON by default
        self.realtime_url = settings.GTFS_REALTIME_URL

    def fetch_trip_updates(self) -> dict:
        """Fetch GTFS Realtime TripUpdates feed in JSON format"""
        try:
            # API key goes as query parameter
            url = f"{self.realtime_url}?key={self.api_key}"
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            return response.json()
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

        # Parse JSON response
        if 'entity' not in feed:
            print("No entities in feed")
            return delays

        for entity in feed['entity']:
            if 'trip_update' not in entity:
                continue
                
            trip_update = entity['trip_update']
            trip = trip_update.get('trip', {})

            # Filter by route_id (e.g., "01" for Lakeshore West)
            if route_id not in trip.get('route_id', ''):
                continue

            # Extract stop time updates
            for stop_time_update in trip_update.get('stop_time_updates', []):
                arrival = stop_time_update.get('arrival', {})
                
                if arrival:
                    delay_seconds = arrival.get('delay', 0)
                    arrival_time = arrival.get('time', 0)
                    
                    delays.append({
                        'trip_id': trip.get('trip_id'),
                        'route_id': trip.get('route_id'),
                        'stop_id': stop_time_update.get('stop_id'),
                        'scheduled_arrival': arrival_time,
                        'delay_seconds': delay_seconds,
                        'timestamp': datetime.now()
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