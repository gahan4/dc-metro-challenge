import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WMATA_API_KEY")

BASE_URL = "https://api.wmata.com/Bus.svc/json"

def get_bus_positions(route_ids=None):
    """Get current WMATA bus positions. Optionally filter by route IDs."""
    url = f"{BASE_URL}/jBusPositions"
    params = {}
    if route_ids:
        params["RouteID"] = ",".join(route_ids)
    headers = {"api_key": API_KEY}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("BusPositions", [])

def get_bus_routes():
    \"\"\"Get a list of all WMATA bus routes.\"\"\"
    url = f"{BASE_URL}/jRoutes"
    headers = {"api_key": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("Routes", [])

def get_bus_stops(route_id):
    """Get all stops for a specific bus route."""
    url = f"{BASE_URL}/jRouteDetails"
    headers = {"api_key": API_KEY}
    params = {"RouteID": route_id}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("Direction0", {}).get("Stops", []) + \
           response.json().get("Direction1", {}).get("Stops", [])
