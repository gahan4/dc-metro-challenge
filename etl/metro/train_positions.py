import os
import requests
import sqlite3
from dotenv import load_dotenv
import pandas as pd

def get_train_positions(db_path: str = "etl/data/metro_challenge.db"):
    """
    Fetches WMATA line data using an API key stored in .env,
    and writes the result to a local SQLite database.

    Parameters:
    - db_path: Path to SQLite database file. 
    """

    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("WMATA_API_KEY")
    if not api_key:
        raise ValueError("WMATA_API_KEY not found in environment variables.")

    # Call WMATA API
    url = "http://api.wmata.com/TrainPositions/TrainPositions?contentType=json"
    headers = {"api_key": api_key}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    # Parse line data. It's a pretty simple df with columns for color,
    # name, code, start and end station code, as well as internal destinations
    train_positions = response.json().get("TrainPositions", [])
    train_positions_df = pd.DataFrame(train_positions)

    # Step 4: Save to SQLite
    conn = sqlite3.connect(db_path)
    train_positions_df.to_sql("fact_train_position", conn, if_exists="append", index=False)
    conn.close()