import os
import requests
import sqlite3
from dotenv import load_dotenv
import pandas as pd

def load_station_entrances(db_path: str = "etl/data/metro_challenge.db"):
    """
    Fetches WMATA station entrances.

    Parameters:
    - db_path: Path to SQLite database file. 
    """

    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("WMATA_API_KEY")
    if not api_key:
        raise ValueError("WMATA_API_KEY not found in environment variables.")

    # Call WMATA API
    url = "http://api.wmata.com/Rail.svc/json/jStationEntrances"
    headers = {"api_key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse line data. It's a pretty simple df with columns for color,
    # name, code, start and end station code, as well as internal destinations
    lines = response.json().get("Lines", [])
    lines_df = pd.DataFrame(lines)

    # Step 4: Save to SQLite
    conn = sqlite3.connect(db_path)
    lines_df.to_sql("dim_train_line", conn, if_exists="replace", index=False)