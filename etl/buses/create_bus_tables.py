import sqlite3
from config import DB_PATH

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create dim_bus table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bus_route (
    Agency TEXT,
    RouteID TEXT,
    RouteName TEXT,
    Description TEXT,
    PRIMARY KEY (Agency, RouteID)
)
''')

# Create bus_stop_station_map table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bus_stop_station_map (
    StopID TEXT,
    MetroStationCode TEXT,
    StopName TEXT,
    DistanceToStation REAL,
    Agency TEXT,
    RouteID TEXT,
    PRIMARY KEY (StopID, MetroStationCode)
)
''')

# Create bus_movements table
cursor.execute('''
CREATE TABLE IF NOT EXISTS bus_movements (
    Timestamp TEXT,
    VehicleID TEXT,
    Agency TEXT,
    RouteID TEXT,
    StopID TEXT,
    Latitude REAL,
    Longitude REAL,
    Speed REAL,
    Direction TEXT,
    TripID TEXT,
    PRIMARY KEY (Timestamp, VehicleID)
)
''')

# Commit and close
conn.commit()
conn.close()
