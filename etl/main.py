import time
from wmata_api import get_train_positions
from db import create_table, insert_position
import pandas as pd
from config import *

def main():
    create_table()
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
