import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WMATA_API_KEY")

BASE_URL = "https://api.wmata.com/Bus.svc/json"

def get_wmata_bus_positions(route_ids=None):
    """Get current WMATA bus positions. Optionally filter by route IDs."""
    url = f"{BASE_URL}/jBusPositions"
    params = {}
    if route_ids:
        params["RouteID"] = ",".join(route_ids)
    headers = {"api_key": API_KEY}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("BusPositions", [])

def get_wmata_bus_routes():
    """Get a list of all WMATA bus routes."""
    url = f"{BASE_URL}/jRoutes"
    headers = {"api_key": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get("Routes", [])

def get_wmata_bus_stops(route_id):
    """Get all stops for a specific bus route."""
    url = f"{BASE_URL}/jRouteDetails"
    headers = {"api_key": API_KEY}
    params = {"RouteID": route_id}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("Direction0", {}).get("Stops", []) + \
           response.json().get("Direction1", {}).get("Stops", [])


def populate_dim_bus_from_api():
    """Fetch WMATA bus routes and insert them into dim_bus."""

    routes = get_bus_routes()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    for route in routes:
        c.execute('''
            INSERT OR IGNORE INTO dim_bus (Agency, RouteID, RouteName, Description)
            VALUES (?, ?, ?, ?)
        ''', (
            "WMATA",
            route.get("RouteID"),
            route.get("Name"),
            route.get("Description")
        ))

    conn.commit()
    conn.close()
    print(f"Inserted {len(routes)} WMATA routes into dim_bus.")
