import sqlite3
from datetime import datetime
from config import DB_NAME

def create_table():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS train_positions (
            TrainId INTEGER,
            TrainNumber INTEGER,
            CarCount INTEGER,
            DirectionNum TEXT,
            CircuitId INTEGER,
            DestinationStationCode TEXT,
            LineCode TEXT,
            SecondsAtLocation INTEGER,
            ServiceType TEXT,
            DateTime TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_position(trains):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # List of tuples from your DataFrame
    records = trains[[
        "TrainId", "TrainNumber", "CarCount", "DirectionNum",
        "CircuitId", "DestinationStationCode", "LineCode",
        "SecondsAtLocation", "ServiceType", "DateTime"
    ]].to_records(index=False)

    # Insert many at once
    cursor.executemany('''
        INSERT INTO train_positions (
            TrainId, TrainNumber, CarCount, DirectionNum,
            CircuitId, DestinationStationCode, LineCode,
            SecondsAtLocation, ServiceType, DateTime
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)

    conn.commit()
    conn.close()
