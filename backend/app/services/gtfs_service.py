import requests
from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
from app.core.config import settings


class ServiceAtGlanceService:
    def __init__(self):
        self.api_key = settings.OPENMETROLINX_API_KEY
        self.trains_url = "https://api.openmetrolinx.com/OpenDataAPI/api/V1/ServiceataGlance/Trains/All"

    def fetch_live_trains(self) -> dict:
        """Fetch live train data from ServiceataGlance endpoint"""
        try:
            url = f"{self.trains_url}?key={self.api_key}"
            
            # Add headers to mimic browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            print(f"Error fetching train data: {e}")
            raise

    def get_delays_for_route(self, route_id: str) -> List[Dict]:
        """
        Parse ServiceataGlance data and extract delays for a specific route
        Returns list of dicts with delay information
        
        route_id: Line code like "LW" for Lakeshore West
        """
        data = self.fetch_live_trains()
        delays = []

        # Check if we have valid data
        if 'Trips' not in data or 'Trip' not in data['Trips']:
            print("No trips in feed")
            return delays

        trips = data['Trips']['Trip']
        
        # Handle both list and single dict
        if not isinstance(trips, list):
            trips = [trips]

        for trip in trips:
            # Filter by line code (e.g., "LW" for Lakeshore West)
            if trip.get('LineCode') != route_id:
                continue

            delay_seconds = trip.get('DelaySeconds', 0)
            
            # Create delay record for this trip
            delays.append({
                'trip_id': trip.get('TripNumber'),
                'route_id': trip.get('LineCode'),
                'origin_stop': trip.get('FirstStopCode'),
                'destination_stop': trip.get('LastStopCode'),
                'scheduled_start_time': trip.get('StartTime'),  # Format: "19:17"
                'scheduled_end_time': trip.get('EndTime'),      # Format: "20:27"
                'delay_seconds': delay_seconds,
                'current_stop': trip.get('AtStationCode'),
                'is_in_motion': trip.get('IsInMotion'),
                'timestamp': datetime.now()
            })

        return delays

    def is_within_time_window(
        self, 
        scheduled_time: time, 
        trip_time_str: str, 
        window_seconds: int = 300
    ) -> bool:
        """
        Check if trip time is within ±window_seconds of scheduled time
        
        scheduled_time: time object from subscription (e.g., time(7, 15))
        trip_time_str: string from API (e.g., "19:17")
        window_seconds: tolerance window (default 5 minutes)
        """
        try:
            # Parse trip time string "HH:MM"
            trip_hour, trip_minute = map(int, trip_time_str.split(':'))
            trip_time = time(trip_hour, trip_minute)
            
            # Convert both to datetime for comparison
            today = datetime.now().date()
            scheduled_dt = datetime.combine(today, scheduled_time)
            trip_dt = datetime.combine(today, trip_time)
            
            diff = abs((scheduled_dt - trip_dt).total_seconds())
            return diff <= window_seconds
            
        except Exception as e:
            print(f"Error comparing times: {e}")
            return False


# Create singleton instance
gtfs_service = ServiceAtGlanceService()