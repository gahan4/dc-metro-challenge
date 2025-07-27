import os
import requests
import sqlite3
from dotenv import load_dotenv
import pandas as pd

def load_standard_routes(db_path: str = "etl/data/metro_challenge.db"):
    """
    Fetches WMATA train routes.

    Parameters:
    - db_path: Path to SQLite database file. 
    """

    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("WMATA_API_KEY")
    if not api_key:
        raise ValueError("WMATA_API_KEY not found in environment variables.")

    # Call WMATA API
    url = "http://api.wmata.com/TrainPositions/StandardRoutes?contentType=json"
    headers = {"api_key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse entrance data. It's a pretty simple df with columns for ID,
    # name, station code, lat/lon
    routes = response.json().get("StandardRoutes", [])
    routes_df = pd.DataFrame(routes)
    
    # The circuits within the routes_df are nested in an unusual way,
    # going to need to flatten them out
    flat_rows = []

    for _, row in routes_df.iterrows():
        line = row["LineCode"]
        track = row["TrackNum"]
        circuits = row["TrackCircuits"]

        for circuit in circuits:
            flat_rows.append({
                "line_code": line,
                "track_num": track,
                "seq_num": circuit["SeqNum"],
                "circuit_id": circuit["CircuitId"],
                "station_code": circuit.get("StationCode")
            })

    flat_df = pd.DataFrame(flat_rows)

    # Step 4: Save to SQLite
    conn = sqlite3.connect(db_path)
    entrances_df.to_sql("dim_station_entrances", conn, if_exists="replace", index=False)