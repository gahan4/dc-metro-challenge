"""
Example usage of the DC Metro Tracker package.
"""

from dc_metro_tracker.data_collection.collector import MetroDataCollector
from datetime import datetime

def main():
    """Example usage of the MetroDataCollector class."""
    collector = MetroDataCollector()
    
    # Get stations DataFrame
    stations_df = collector.stations
    
    if stations_df is not None:
        print("\nDataFrame Preview:")
        print(stations_df.head())
        print("\nColumns:", stations_df.columns.tolist())
        
        # Example: Get predictions for a transfer station
        transfer_stations = stations_df[stations_df['is_transfer']].index
        if len(transfer_stations) > 0:
            example_station = transfer_stations[0]
            predictions = collector.get_station_predictions(example_station)
            if predictions:
                collector.save_data(
                    predictions,
                    f"predictions_{example_station}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
        
        return stations_df
    else:
        print("Failed to fetch station data")
        return None

if __name__ == "__main__":
    stations_df = main() 