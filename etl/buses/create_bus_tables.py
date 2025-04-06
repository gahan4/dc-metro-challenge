import sqlite3
from config import DB_PATH
from etl.buses.wmata import get_wmata_bus_positions, get_wmata_bus_routes, get_wmata_bus_stops

def create_static_bus_tables():

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create bus table (shows which bus routes exist)
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

def insert_wmata_bus_info():
    """Fetch WMATA bus routes and insert them into dim_bus."""

    routes = get_wmata_bus_routes()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    for route in routes:
        c.execute('''
            INSERT OR IGNORE INTO dim_bus (Agency, RouteID, RouteName, Description)
            VALUES (?, ?, ?, ?)
        ''', (
            "WMATA",
            route.get("RouteID"),
            route.get("Name"),
            route.get("Description")
        ))

    conn.commit()
    conn.close()
    print(f"Inserted {len(routes)} WMATA routes into dim_bus.")

