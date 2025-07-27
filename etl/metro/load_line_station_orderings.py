import os
import requests
import sqlite3
from dotenv import load_dotenv
import pandas as pd

def load_lines(db_path: str = "etl/data/metro_challenge.db"):
    """
    Fetches information about the order of stations along each line.
    Note that must have already loaded info into dim_train_line in order
    for this function to work.

    Parameters:
    - db_path: Path to SQLite database file. 
    """

    # Get info about start/end points of a given lin
    conn = sqlite3.connect(db_path)
    lines_df = pd.read_sql_query("SELECT * FROM dim_train_line", conn)
    conn.close()

    # Load API key from .env file
    load_dotenv()
    api_key = os.getenv("WMATA_API_KEY")
    if not api_key:
        raise ValueError("WMATA_API_KEY not found in environment variables.")

    # Call WMATA API for each pair of station start/end
    url_format = "http://api.wmata.com/Rail.svc/json/jPath[?FromStationCode][&ToStationCode]"
    headers = {"api_key": api_key}
    response = requests.get(url_format, headers=headers)

    # Iterate over all start/end station pairs. Note that will need to go both ways, so going to
    # run the same process twice, once setting the "DirectionId" to be 0, the other time to be 1.
    paths_list = []
    for _, row in lines_df.iterrows():
        start_station_code = row['StartStationCode']
        end_station_code = row['EndStationCode']
        response = requests.get(f"http://api.wmata.com/Rail.svc/json/jPath?FromStationCode={start_station_code}&ToStationCode={end_station_code}",
                                 headers=headers)
        response.raise_for_status()
        path = response.json().get("Path", {})
        path_df = pd.DataFrame(path)
        path_df['NextStationCode'] = path_df['StationCode'].shift(-1)
        path_df = path_df.rename(columns={'DistanceToPrev' : 'DistanceToNext'})
        path_df['DirectionId'] = 0
        paths_list.append(path_df)

        start_station_code = row['EndStationCode']
        end_station_code = row['StartStationCode']
        response = requests.get(f"http://api.wmata.com/Rail.svc/json/jPath?FromStationCode={start_station_code}&ToStationCode={end_station_code}",
                                 headers=headers)
        response.raise_for_status()
        path = response.json().get("Path", {})
        path_df = pd.DataFrame(path)
        path_df['NextStationCode'] = path_df['StationCode'].shift(-1)
        path_df = path_df.rename(columns={'DistanceToPrev' : 'DistanceToNext'})
        path_df['DirectionId'] = 1
        paths_list.append(path_df)

    paths_df = pd.concat(paths_list, ignore_index=True)
        
    # Step 4: Save to SQLite
    conn = sqlite3.connect(db_path)
    paths_df.to_sql("dim_train_paths", conn, if_exists="replace", index=False)

    # Yellow flag here that these don't seem to all be correct. As an example,
    # when finding route from Franconia Springfield to Downtown Largo on other end of BL,
    # this route suggests that we completely cut off everything from Van Dorn to Stadium Armory (i.e.
    # skips directly from Franconia to Benning Rd)

