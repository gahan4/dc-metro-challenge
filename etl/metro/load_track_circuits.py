import os
import requests
import sqlite3
from dotenv import load_dotenv
import pandas as pd

def load_track_circuits(db_path: str = "etl/data/metro_challenge.db"):
    """
    Fetches WMATA train circuits.

    Parameters:
    - db_path: Path to SQLite database file. 
    """

    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("WMATA_API_KEY")
    if not api_key:
        raise ValueError("WMATA_API_KEY not found in environment variables.")

    # Call WMATA API
    url = "http://api.wmata.com/TrainPositions/TrackCircuits?contentType=json"
    headers = {"api_key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse entrance data. It's a pretty simple df with columns for ID,
    # name, station code, lat/lon
    track_circuits = response.json().get("TrackCircuits", [])
    track_circuits_df = pd.DataFrame(track_circuits)
    
    # The neighbors within the track_circuits_df are nested,
    # going to need to flatten them out
    flat_rows = []

    for circuit in track_circuits:
        circuit_id = circuit["CircuitId"]
        track = circuit["Track"]
        for neighbor in circuit["Neighbors"]:
            neighbor_type = neighbor["NeighborType"]
            for neighbor_circuit_id in neighbor["CircuitIds"]:
                flat_rows.append({
                    "circuit_id": circuit_id,
                    "track": track,
                    "neighbor_type": neighbor_type,
                    "neighbor_circuit_id": neighbor_circuit_id
                })

    track_circuits_df_flat = pd.DataFrame(flat_rows)

    # Step 4: Save to SQLite
    conn = sqlite3.connect(db_path)
    track_circuits_df_flat.to_sql("dim_track_circuits", conn, if_exists="replace", index=False)