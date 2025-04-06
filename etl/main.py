import time
import pandas as pd

from etl.metro.wmata_api import get_train_positions
from etl.metro.db import create_table, insert_position
from etl.config import *
from etl.

def main():
    create_table()
    create_static_bus_tables()
    while True:
        try:
            trains = get_train_positions()
            insert_position(trains)
            print(f"Inserted {len(trains)} records")
        except Exception as e:
            print("Error:", e)
        time.sleep(10)  # 10 seconds between calls

if __name__ == "__main__":
    main()
