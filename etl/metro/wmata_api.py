import requests
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import pytz

load_dotenv()
API_KEY = os.getenv("WMATA_API_KEY")

def get_train_positions():
    url = "https://api.wmata.com/TrainPositions/TrainPositions?contentType=json"
    headers = {"api_key": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    train_positions = response.json().get("TrainPositions", [])
    train_positions_df = pd.DataFrame(train_positions)
    # Only want trains that are in normal service
    train_positions_df = train_positions_df[train_positions_df['ServiceType'] == "Normal"]
    # Adjust types of variables to match intuition, raise errors if required
    train_positions_df['TrainId'] = pd.to_numeric(train_positions_df['TrainId'], errors='raise')
    train_positions_df['TrainNumber'] = pd.to_numeric(train_positions_df['TrainNumber'], errors='raise')
    # Add a timestamp
    train_positions_df["DateTime"] = datetime.now(pytz.timezone("America/New_York")).isoformat()

    return train_positions_df
