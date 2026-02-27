import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_and_clean_data(file_path):
    """Load and clean parking meter data"""
    print("Loading parking meter data...")
    df = pd.read_excel(file_path)

    print(f"Original dataset: {len(df)} records")

    # Select relevant columns
    columns_to_keep = [
        'ObjectID', 'Meter Number', 'Status', 'Meter_Hours',
        'Parking_Facility_Name', 'Facility', 'Borough',
        'On_Street', 'From_Street', 'To_Street',
        'Latitude', 'Longitude'
    ]

    df = df[columns_to_keep]

    # Remove inactive meters
    df = df[df['Status'] == 'Active']

    # Remove records with missing coordinates
    df = df.dropna(subset=['Latitude', 'Longitude'])

    # Estimate parking spaces (default to 1 for individual meters)
    df['parking_spaces'] = 1

    # For parking facilities (lots), estimate more spaces
    df.loc[df['Facility'] == 'Off Street', 'parking_spaces'] = np.random.randint(20, 100,
                                                                                  size=len(df[df['Facility'] == 'Off Street']))

    # Extract meter type and hours
    df['meter_type'] = df['Meter_Hours'].apply(lambda x: 'Commercial' if 'Com' in str(x) else 'Passenger')

    # Clean borough names
    df['Borough'] = df['Borough'].str.strip().str.title()

    print(f"Cleaned dataset: {len(df)} records")
    print(f"\nBreakdown by borough:")
    print(df['Borough'].value_counts())

    return df

def extract_time_features(df, start_date='2024-01-01', days=90):
    """Generate time-based features for each parking location"""
    print(f"\nGenerating {days} days of hourly data...")

    # Create date range (hourly intervals)
    dates = pd.date_range(start=start_date, periods=days*24, freq='h')

    # Create all combinations of parking locations and times
    parking_times = []

    for idx, row in df.iterrows():
        for date in dates:
            parking_times.append({
                'location_id': row['ObjectID'],
                'latitude': row['Latitude'],
                'longitude': row['Longitude'],
                'borough': row['Borough'],
                'parking_spaces': row['parking_spaces'],
                'meter_type': row['meter_type'],
                'facility_type': row['Facility'],
                'datetime': date,
                'hour': date.hour,
                'day_of_week': date.dayofweek,  # 0=Monday, 6=Sunday
                'month': date.month,
                'day': date.day,
                'is_weekend': 1 if date.dayofweek >= 5 else 0,
                'is_business_hours': 1 if 9 <= date.hour <= 17 else 0,
                'is_rush_hour': 1 if date.hour in [7, 8, 9, 17, 18, 19] else 0,
            })

    df_expanded = pd.DataFrame(parking_times)
    print(f"Generated {len(df_expanded):,} training records")

    return df_expanded

def simulate_occupancy(df):
    """Simulate occupancy rates based on time patterns"""
    print("\nSimulating occupancy patterns...")

    # Base occupancy rates by hour (0-23)
    hourly_base_rate = {
        0: 0.15, 1: 0.10, 2: 0.08, 3: 0.07, 4: 0.08, 5: 0.12,
        6: 0.25, 7: 0.55, 8: 0.75, 9: 0.85, 10: 0.80, 11: 0.85,
        12: 0.90, 13: 0.85, 14: 0.80, 15: 0.75, 16: 0.80, 17: 0.85,
        18: 0.75, 19: 0.65, 20: 0.50, 21: 0.35, 22: 0.25, 23: 0.20
    }

    occupancy_rates = []

    for _, row in df.iterrows():
        base_rate = hourly_base_rate[row['hour']]

        # Adjust for weekend (lower occupancy in business districts)
        if row['is_weekend']:
            if row['borough'] in ['Manhattan', 'Brooklyn']:
                base_rate *= 0.7  # Business districts less busy on weekends
            else:
                base_rate *= 1.1  # Residential areas busier on weekends

        # Adjust for commercial vs passenger meters
        if row['meter_type'] == 'Commercial':
            if row['is_business_hours']:
                base_rate *= 1.2  # More occupied during business hours
            else:
                base_rate *= 0.6  # Less occupied outside business hours

        # Adjust for rush hour
        if row['is_rush_hour']:
            base_rate *= 1.15

        # Add random variation
        rate = base_rate + np.random.normal(0, 0.08)
        rate = max(0, min(1, rate))  # Clamp between 0 and 1

        occupancy_rates.append(rate)

    df['occupancy_rate'] = occupancy_rates
    df['occupied_spaces'] = (df['parking_spaces'] * df['occupancy_rate']).round().astype(int)
    df['free_spaces'] = df['parking_spaces'] - df['occupied_spaces']
    df['free_spaces'] = df['free_spaces'].clip(lower=0)  # Ensure non-negative

    print(f"Average occupancy rate: {df['occupancy_rate'].mean():.2%}")
    print(f"Average free spaces per location: {df['free_spaces'].mean():.2f}")

    return df

if __name__ == "__main__":
    import os
    # Get absolute path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    data_file = os.path.join(project_dir, 'data', 'Parking_Meters_Locations_and_Status_20260227.xlsx')

    # Load and clean data
    df = load_and_clean_data(data_file)

    # Save cleaned locations
    output_file = os.path.join(project_dir, 'data', 'parking_locations_cleaned.csv')
    df.to_csv(output_file, index=False)
    print(f"\nSaved cleaned locations to: {output_file}")

    # Generate time-based features and simulate occupancy
    df_expanded = extract_time_features(df, days=90)
    df_expanded = simulate_occupancy(df_expanded)

    # Save training data
    training_file = os.path.join(project_dir, 'data', 'training_data.csv')
    df_expanded.to_csv(training_file, index=False)
    print(f"Saved training data to: {training_file}")
    print(f"Training data size: {len(df_expanded):,} records")
