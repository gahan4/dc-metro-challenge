"""
WMATA API client module.
"""

import requests
from typing import Dict, Optional
import os
from dotenv import load_dotenv

class WMATAClient:
    """Base client for interacting with WMATA API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional API key, otherwise use environment variable."""
        load_dotenv()
        self.api_key = api_key or os.getenv('WMATA_API_KEY')
        if not self.api_key:
            raise ValueError("WMATA API key must be provided or set in WMATA_API_KEY environment variable")
        
        self.base_url = "https://api.wmata.com"
        self.headers = {'api_key': self.api_key}
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to the WMATA API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {e}")
            return None 