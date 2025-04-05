"""
Scheduled data collection for DC Metro.
"""

import schedule
import time
from datetime import datetime
import pytz
from typing import Optional
import sqlite3
import os
from pathlib import Path

from ..api.wmata import WMATAClient
from ..utils.email_reporter import create_report, send_email

class MetroDataScheduler:
    def __init__(self, db_path: str = "data/metro_data.db"):
        self.wmata_client = WMATAClient()
        self.db_path = db_path
        self.eastern_tz = pytz.timezone('US/Eastern')
        self.recipient_email = "neilwgahart@gmail.com"
        
        # Ensure database directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database if it doesn't exist
        if not os.path.exists(db_path):
            self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database with schema."""
        with open(Path(__file__).parent / 'schema.sql', 'r') as f:
            schema = f.read()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
    
    def _is_collection_time(self) -> bool:
        """Check if current time is within collection window (6 AM - 10 PM Eastern)."""
        now = datetime.now(self.eastern_tz)
        return 6 <= now.hour < 22
    
    def collect_data(self):
        """Collect data if within time window."""
        if not self._is_collection_time():
            return
        
        try:
            # Collect train positions
            positions = self.wmata_client._make_request('Train.svc/json/jPositions')
            
            # Collect predictions for all stations
            stations = self.wmata_client.stations
            for station_code in stations.index:
                predictions = self.wmata_client.get_station_predictions(station_code)
                
                # Store in database (to be implemented)
                self._store_predictions(predictions)
            
            # Store positions in database (to be implemented)
            self._store_positions(positions)
            
        except Exception as e:
            print(f"Error collecting data: {e}")
    
    def send_daily_reports(self):
        """Send scheduled reports."""
        now = datetime.now(self.eastern_tz)
        
        # Only send at specified hours
        if now.hour not in [6, 13, 20]:
            return
            
        with sqlite3.connect(self.db_path) as conn:
            report = create_report(conn)
            
        subject = f"DC Metro Report - {now.strftime('%Y-%m-%d %H:%M')}"
        send_email(subject, report, self.recipient_email)
    
    def run(self):
        """Run the scheduler."""
        # Schedule data collection every 2 minutes
        schedule.every(2).minutes.do(self.collect_data)
        
        # Schedule reports
        schedule.every().day.at("06:00").do(self.send_daily_reports)
        schedule.every().day.at("13:00").do(self.send_daily_reports)
        schedule.every().day.at("20:00").do(self.send_daily_reports)
        
        print("Starting Metro data collection scheduler...")
        print("Collection window: 6 AM - 10 PM Eastern")
        print("Reports scheduled for: 6 AM, 1 PM, 8 PM Eastern")
        
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    scheduler = MetroDataScheduler()
    scheduler.run() 