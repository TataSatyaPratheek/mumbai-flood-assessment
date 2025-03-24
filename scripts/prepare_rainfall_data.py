#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to prepare rainfall data for Mumbai flood vulnerability assessment.
For demonstration, we'll create synthetic rainfall data based on Mumbai's
typical monsoon patterns.
"""

import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def create_synthetic_rainfall_data():
    """
    Create synthetic rainfall data for Mumbai.
    In a real scenario, you would import actual rainfall data from IMD.
    """
    # Define the output path
    output_dir = Path("data/raw/rainfall")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a date range for the past 5 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    
    # Create a date range with daily frequency
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Initialize data
    rainfall_data = []
    
    # Weather stations in Mumbai
    stations = [
        "Colaba", "Santacruz", "Worli", "Dahisar", "Mulund", "Andheri"
    ]
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    for station in stations:
        # Create station-specific data
        station_data = []
        
        for date in dates:
            # Mumbai has a monsoon season from June to September
            # Higher rainfall during these months
            month = date.month
            
            # Base rainfall parameters (mean, std) by month
            if month in [6, 7, 8, 9]:  # Monsoon months
                if month == 7:  # Peak monsoon (July)
                    mean_rain = 20  # mm
                    std_rain = 25   # mm
                else:
                    mean_rain = 12  # mm
                    std_rain = 15   # mm
            else:
                mean_rain = 1   # mm
                std_rain = 3    # mm
            
            # Generate random rainfall with occasional extreme events
            if np.random.random() < 0.05 and month in [6, 7, 8, 9]:
                # Extreme rainfall event (5% chance during monsoon)
                rainfall = np.random.uniform(80, 250)  # mm
            else:
                # Normal rainfall (with possibility of negative values set to 0)
                rainfall = max(0, np.random.normal(mean_rain, std_rain))
            
            station_data.append({
                'station': station,
                'date': date,
                'rainfall_mm': round(rainfall, 1),
                'year': date.year,
                'month': date.month,
                'day': date.day
            })
        
        rainfall_data.extend(station_data)
    
    # Create DataFrame
    rainfall_df = pd.DataFrame(rainfall_data)
    
    # Save to CSV
    output_file = output_dir / "mumbai_rainfall_synthetic.csv"
    rainfall_df.to_csv(output_file, index=False)
    
    print(f"Created synthetic rainfall data for {len(stations)} stations.")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Saved to {output_file}")
    
    # Also create a summary by month and year
    monthly_summary = rainfall_df.groupby(['station', 'year', 'month'])['rainfall_mm'].agg(
        ['sum', 'mean', 'max']
    ).reset_index()
    monthly_summary.columns = ['station', 'year', 'month', 'total_rainfall', 'avg_daily_rainfall', 'max_daily_rainfall']
    
    # Save monthly summary
    output_summary = output_dir / "mumbai_rainfall_monthly_summary.csv"
    monthly_summary.to_csv(output_summary, index=False)
    
    print(f"Created monthly rainfall summary.")
    print(f"Saved to {output_summary}")
    
    return rainfall_df

def main():
    """Main function to prepare rainfall data."""
    create_synthetic_rainfall_data()

if __name__ == "__main__":
    main()
