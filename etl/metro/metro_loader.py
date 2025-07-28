import time
import yagmail
import os
import pandas as pd
import sqlite3
from dotenv import load_dotenv


from etl.metro import (load_line_station_orderings,
                        load_lines, 
                        load_standard_routes, 
                        load_station_entrances,
                        load_stations,
                        load_track_circuits,
                        get_train_positions)

def send_summary_email(num_rows_written, db_path: str = "etl/data/metro_challenge.db"):
    """
    Send an email indicating the number of rows that have been written
    to the train positions db, given by the parameter passed in.
    """
    load_dotenv()
    user = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASSWORD")
    recipient = os.getenv("EMAIL_TO")

    conn = sqlite3.connect(db_path)
    last_ten_rows_written =  pd.read_sql_query("""
                                               SELECT * 
                                              FROM fact_train_position
                                               order by loaddate desc
                                               limit 10
                                               """, conn)
    last_ten_rows_written_as_table =  last_ten_rows_written.to_html(index=False, border=1)
    conn.close()

    # Create the email info
    subject = "WMATA Train Data Summary"
    body = (
        f"""
        Total rows written in fact_train_position since last email: {num_rows_written}\n

        Last ten rows:
        {last_ten_rows_written_as_table}
        """
    )

    yag = yagmail.SMTP(user, password)
    yag.send(to=recipient, subject=subject, contents=body)

def metro_loader(db_path: str = "etl/data/metro_challenge.db"):
    """
    A function to log and load information related to the DC metro,
    including real-time train information
    """
    load_stations()
    load_station_entrances()
    load_lines()
    load_standard_routes()
    load_line_station_orderings()
    load_track_circuits()

    # get the train positions...this also writes results to db
    EMAIL_MINUTES = 5 # how often to send an email
    SLEEP_SECONDS = 15 # how long to sleep before getting train info again
    iteration = 0
    last_number_of_rows_written = 0
    while True:
        try:
            get_train_positions() 
            if EMAIL_MINUTES > (SLEEP_SECONDS * iteration) * 60:
                iteration = iteration + 1
            else:
                num_rows_now = 
                send_summary_email()
        except Exception as e:
            print(f"Error during train position fetch: {e}")
        time.sleep(SLEEP_SECONDS)
    


    