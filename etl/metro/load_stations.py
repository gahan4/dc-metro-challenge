import os
import requests
import sqlite3
from dotenv import load_dotenv
import pandas as pd

def load_stations(db_path: str = "etl/data/metro_challenge.db"):
    """
    Fetches WMATA station data using an API key stored in .env,
    and writes the result to a local SQLite database.

    Parameters:
    - db_path: Path to SQLite database file. Default is 'metro_stations.db'.
    """

    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("WMATA_API_KEY")
    if not api_key:
        raise ValueError("WMATA_API_KEY not found in environment variables.")

    # Call WMATA API
    url = "https://api.wmata.com/Rail.svc/json/jStations"
    headers = {"api_key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse station data, keeping all columns that are returned from the WMATA API
    # Note that the Address part of the returned dict has many components, so will
    # need to unpack those
    stations = response.json().get("Stations", [])
    stations_df = pd.DataFrame(stations)
    addresses = pd.json_normalize(stations_df['Address'])
    stations_df = stations_df.drop(columns=['Address']).join(addresses)

    # Step 4: Save to SQLite
    conn = sqlite3.connect(db_path)
    stations_df.to_sql("dim_station", conn, if_exists="replace", index=False)