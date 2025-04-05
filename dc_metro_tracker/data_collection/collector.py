"""
Metro data collection module.
"""

from typing import Dict, Optional
import pandas as pd
from datetime import datetime
import os
import json

from ..api.wmata import WMATAClient

class MetroDataCollector(WMATAClient):
    """Class to handle Metro data collection and processing."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional API key, otherwise use environment variable."""
        super().__init__(api_key)
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
        raw_data = self._make_request('Rail.svc/json/jStations')
        if not raw_data:
            return None
            
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
        return self._make_request(f'StationPrediction.svc/json/GetPrediction/{station_code}')
    
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
                'api_version': '1.0'
            }
        }
        
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data_with_meta, f, indent=2)
        print(f"Data saved to {filepath}") 