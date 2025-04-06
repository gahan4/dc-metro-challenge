#!/usr/bin/env python3
"""
Simple script to fetch DC Metro station information using the WMATA API.
"""

import requests
import json
from typing import Dict, List, Optional
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_KEY = os.getenv('WMATA_API_KEY')
if not API_KEY:
    raise ValueError("WMATA_API_KEY not found in environment variables. Please create a .env file with your API key.")

BASE_URL = "https://api.wmata.com"

class MetroDataCollector:
    """Class to handle Metro data collection and processing."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional API key, otherwise use environment variable."""
        self.api_key = api_key or os.getenv('WMATA_API_KEY')
        if not self.api_key:
            raise ValueError("WMATA API key must be provided or set in WMATA_API_KEY environment variable")
        
        self.base_url = "https://api.wmata.com"
        self.headers = {'api_key': self.api_key}
        self._stations_df = None  # Cache for stations DataFrame
    
    @property
    def stations(self) -> pd.DataFrame:
        """Get stations DataFrame, fetch if not already cached."""
        if self._stations_df is None:
            self._stations_df = self.get_stations_df()
        return self._stations_df

    def get_all_stations(self) -> Dict:
        """
        Fetch information about all Metro stations.
        
        Returns:
            Dict: A dictionary with station codes as keys
        """
        url = f"{self.base_url}/Rail.svc/json/jStations"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            raw_data = response.json()
            
            # Convert the list of stations to a dictionary with station codes as keys
            stations_dict = {
                station['Code']: {
                    'name': station['Name'],
                    'lines': [line for line in [
                        station.get('LineCode1'),
                        station.get('LineCode2'),
                        station.get('LineCode3'),
                        station.get('LineCode4')
                    ] if line],
                    'lat': station['Lat'],
                    'lon': station['Lon'],
                    'address': {
                        'street': station.get('Address', {}).get('Street', ''),
                        'city': station.get('Address', {}).get('City', ''),
                        'state': station.get('Address', {}).get('State', ''),
                        'zip': station.get('Address', {}).get('Zip', '')
                    },
                    'transfer_stations': [station.get('StationTogether1', ''), 
                                        station.get('StationTogether2', '')] if station.get('StationTogether1') or station.get('StationTogether2') else []
                }
                for station in raw_data['Stations']
            }
            
            return stations_dict
        except requests.exceptions.RequestException as e:
            print(f"Error fetching station data: {e}")
            return None

    def get_stations_df(self) -> pd.DataFrame:
        """Get stations data as a DataFrame with useful additional columns."""
        stations_dict = self.get_all_stations()
        if not stations_dict:
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(stations_dict, orient='index')
        
        # Expand address dictionary into columns
        address_df = pd.json_normalize(df['address'])
        df = df.drop('address', axis=1).join(address_df.add_prefix('address_'))
        
        # Add useful derived columns
        df['n_lines'] = df['lines'].apply(len)
        df['is_transfer'] = df['transfer_stations'].apply(lambda x: len(x) > 0)
        df['station_code'] = df.index
        
        # Reorder columns
        first_cols = ['name', 'station_code', 'lines', 'n_lines', 'is_transfer']
        other_cols = [col for col in df.columns if col not in first_cols]
        df = df[first_cols + other_cols]
        
        return df
    
    def get_station_predictions(self, station_code: str) -> Dict:
        """Get real-time predictions for a specific station."""
        url = f"{self.base_url}/StationPrediction.svc/json/GetPrediction/{station_code}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching predictions for station {station_code}: {e}")
            return None
    
    def save_data(self, data: Dict, filename: str, subdir: str = "raw"):
        """Save data to a JSON file with timestamp in specified subdirectory."""
        data_dir = os.path.join('data', subdir)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Add metadata
        data_with_meta = {
            'data': data,
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'api_version': '1.0'  # You might want to track API versions
            }
        }
        
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data_with_meta, f, indent=2)
        print(f"Data saved to {filepath}")

def main():
    """Example usage of the MetroDataCollector class."""
    collector = MetroDataCollector()
    
    # Get stations DataFrame
    stations_df = collector.stations
    
    if stations_df is not None:
        print("\nDataFrame Preview:")
        print(stations_df.head())
        print("\nColumns:", stations_df.columns.tolist())
        
        # Example: Get predictions for a transfer station
        transfer_stations = stations_df[stations_df['is_transfer']].index
        if len(transfer_stations) > 0:
            example_station = transfer_stations[0]
            predictions = collector.get_station_predictions(example_station)
            if predictions:
                collector.save_data(
                    predictions,
                    f"predictions_{example_station}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
        
        return stations_df
    else:
        print("Failed to fetch station data")
        return None

if __name__ == "__main__":
    stations_df = main() 