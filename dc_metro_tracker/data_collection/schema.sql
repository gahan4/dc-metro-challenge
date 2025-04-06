-- Train predictions table
CREATE TABLE IF NOT EXISTS train_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    station_code TEXT NOT NULL,
    train_id TEXT,
    line TEXT,
    destination_station TEXT,
    minutes_away INTEGER,
    raw_data JSON,
    FOREIGN KEY (station_code) REFERENCES stations(code)
);

-- Train positions table
CREATE TABLE IF NOT EXISTS train_positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    train_id TEXT NOT NULL,
    line TEXT,
    current_station_code TEXT,
    next_station_code TEXT,
    direction_number INTEGER,
    circuit_id INTEGER,
    raw_data JSON,
    FOREIGN KEY (current_station_code) REFERENCES stations(code),
    FOREIGN KEY (next_station_code) REFERENCES stations(code)
);

-- Actual train arrivals (derived from position data)
CREATE TABLE IF NOT EXISTS train_arrivals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_id TEXT NOT NULL,
    station_code TEXT NOT NULL,
    arrival_time DATETIME NOT NULL,
    departure_time DATETIME,
    line TEXT,
    FOREIGN KEY (station_code) REFERENCES stations(code)
);

-- Service incidents
CREATE TABLE IF NOT EXISTS service_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    lines_affected TEXT[],
    description TEXT,
    raw_data JSON
);

-- Create indexes for common queries
CREATE INDEX idx_predictions_station_time ON train_predictions(station_code, timestamp);
CREATE INDEX idx_positions_train_time ON train_positions(train_id, timestamp);
CREATE INDEX idx_arrivals_station_time ON train_arrivals(station_code, arrival_time); 