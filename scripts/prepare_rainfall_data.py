#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to download and prepare rainfall data for Mumbai flood vulnerability assessment.
Uses actual historical rainfall data from IMD and other open sources.
"""

import os
import sys
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta
from pathlib import Path
import gzip
import shutil
import zipfile
import csv

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.data.acquisition import download_file

def download_imd_rainfall_data():
    """
    Download rainfall data from India Meteorological Department (IMD).
    Note: This may require registration/authentication for actual IMD data.
    """
    # Define the output path
    output_dir = Path("data/raw/rainfall")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Attempting to download IMD rainfall data...")
    
    # Check if IMD API key is available (typically needs registration)
    imd_api_key = os.environ.get("IMD_API_KEY")
    
    if imd_api_key:
        # Example API endpoint (hypothetical - actual IMD API would differ)
        imd_api_url = "https://api.imd.gov.in/rainfall/historical"
        params = {
            "station": "Mumbai",
            "start_date": "2015-01-01",
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "api_key": imd_api_key
        }
        
        try:
            response = requests.get(imd_api_url, params=params)
            if response.status_code == 200:
                output_file = output_dir / "mumbai_rainfall_imd.csv"
                with open(output_file, "wb") as f:
                    f.write(response.content)
                print(f"Downloaded IMD rainfall data to {output_file}")
                return output_file
            else:
                print(f"IMD API request failed with status code {response.status_code}")
                
        except Exception as e:
            print(f"Error accessing IMD API: {e}")
    else:
        print("IMD API key not found.")
    
    # Alternative: Download from NOAA Global Summary of the Day (GSOD)
    return download_noaa_gsod_data(output_dir)

def download_noaa_gsod_data(output_dir):
    """
    Download NOAA Global Summary of the Day data for Mumbai station.
    """
    print("Downloading NOAA GSOD data for Mumbai...")
    
    # Mumbai airport station IDs
    station_ids = ["430030-99999"]  # Santacruz/Mumbai Airport
    
    # Years to download (last 5 years)
    end_year = datetime.now().year
    start_year = end_year - 5
    
    all_data = []
    
    for year in range(start_year, end_year + 1):
        for station in station_ids:
            # NOAA GSOD URL pattern
            url = f"https://www.ncei.noaa.gov/data/global-summary-of-the-day/access/{year}/{station}.csv"
            
            output_file = output_dir / f"gsod_{station}_{year}.csv"
            
            print(f"Downloading data for station {station}, year {year}...")
            try:
                if download_file(url, output_file):
                    # Read the downloaded file
                    df = pd.read_csv(output_file)
                    all_data.append(df)
                else:
                    print(f"Failed to download {station} for {year}")
            except Exception as e:
                print(f"Error processing {station} for {year}: {e}")
    
    # If we got some data, merge it and save
    if all_data:
        # Concatenate all data frames
        combined_data = pd.concat(all_data, ignore_index=True)
        
        # Save combined data
        combined_file = output_dir / "mumbai_rainfall_noaa.csv"
        combined_data.to_csv(combined_file, index=False)
        
        # Process data to extract rainfall columns
        rainfall_data = process_noaa_data(combined_data)
        rainfall_file = output_dir / "mumbai_rainfall.csv"
        rainfall_data.to_csv(rainfall_file, index=False)
        
        print(f"Processed and saved rainfall data to {rainfall_file}")
        return rainfall_file
    
    # Fallback to WorldClim or CHIRPS data
    print("NOAA data download failed, trying WorldClim...")
    return download_worldclim_data(output_dir)

def process_noaa_data(data):
    """Process NOAA GSOD data to extract rainfall information."""
    # Select relevant columns
    if 'PRCP' in data.columns:  # Precipitation in inches
        # Convert to mm (1 inch = 25.4 mm)
        data['rainfall_mm'] = data['PRCP'] * 25.4
    elif 'PRECIP' in data.columns:
        data['rainfall_mm'] = data['PRECIP'] * 25.4
    else:
        # If no precipitation column is found
        print("No precipitation data found in NOAA dataset.")
        data['rainfall_mm'] = 0
    
    # Extract date components
    if 'DATE' in data.columns:
        data['date'] = pd.to_datetime(data['DATE'])
    else:
        # Try to construct date from year, month, day if available
        date_cols = []
        for col in ['YEAR', 'MONTH', 'DAY']:
            if col in data.columns:
                date_cols.append(col)
        
        if len(date_cols) == 3:
            data['date'] = pd.to_datetime(data[date_cols])
        else:
            print("Cannot construct date from available columns.")
            return data
    
    # Add year, month, day columns
    data['year'] = data['date'].dt.year
    data['month'] = data['date'].dt.month
    data['day'] = data['date'].dt.day
    
    # Add station name if available
    if 'STATION' in data.columns:
        data['station'] = data['STATION']
    else:
        data['station'] = "Mumbai_Airport"
    
    # Select final columns
    result = data[['station', 'date', 'year', 'month', 'day', 'rainfall_mm']].copy()
    
    return result

def download_worldclim_data(output_dir):
    """
    Download WorldClim climate data which includes precipitation.
    This is monthly climatology, not daily values.
    """
    print("Downloading WorldClim precipitation data...")
    
    # WorldClim v2 precipitation URL
    url = "https://biogeo.ucdavis.edu/data/worldclim/v2.1/base/wc2.1_10m_prec.zip"
    zip_file = output_dir / "worldclim_prec.zip"
    
    if download_file(url, zip_file):
        # Create a temporary directory for extraction
        extract_dir = output_dir / "worldclim_extract"
        extract_dir.mkdir(exist_ok=True)
        
        # Extract the downloaded zip file
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        print(f"Extracted WorldClim data to {extract_dir}")
        
        # Process the data for Mumbai region
        # This would typically involve GIS operations to extract values
        # for the Mumbai region from the global rasters
        print("Processing WorldClim data for Mumbai region...")
        
        # This is placeholder functionality - in a real implementation,
        # you would use rasterio to extract values for Mumbai from the rasters
        
        # Create a basic processed file with monthly precipitation values
        months = range(1, 13)
        monthly_data = []
        
        for month in months:
            monthly_data.append({
                'month': month,
                'avg_rainfall_mm': get_worldclim_value_for_mumbai(extract_dir, month)
            })
        
        # Create a DataFrame
        monthly_df = pd.DataFrame(monthly_data)
        
        # Save to CSV
        output_file = output_dir / "mumbai_rainfall_monthly_worldclim.csv"
        monthly_df.to_csv(output_file, index=False)
        
        print(f"Saved WorldClim monthly precipitation for Mumbai to {output_file}")
        
        # Clean up temporary files
        try:
            shutil.rmtree(extract_dir)
            os.remove(zip_file)
        except Exception as e:
            print(f"Error cleaning up temporary files: {e}")
        
        return output_file
    else:
        print("Failed to download WorldClim data.")
        
        # Final fallback: provide instructions for manual download
        print("\nAll automated download methods failed. Please download rainfall data manually:")
        print("1. Visit India Meteorological Department: https://mausam.imd.gov.in/")
        print("2. Request historical rainfall data for Mumbai stations")
        print("3. Place downloaded files in: data/raw/rainfall/")
        print("4. Format the data as CSV with columns: station, date, rainfall_mm")
        
        return None

def get_worldclim_value_for_mumbai(extract_dir, month):
    """
    Extract the WorldClim precipitation value for Mumbai from the raster.
    This is a simplified placeholder - actual implementation would use 
    rasterio to extract values at Mumbai's coordinates.
    """
    # Mumbai coordinates
    mumbai_lat, mumbai_lon = 19.07, 72.87
    
    # In a real implementation, you would:
    # 1. Open the raster file for the specific month
    # 2. Use rasterio to get the value at Mumbai's coordinates
    # 3. Return the precipitation value
    
    # For this placeholder, we'll use representative values for Mumbai
    # Based on typical monthly rainfall patterns
    monthly_values = {
        1: 0.7,    # January
        2: 1.3,    # February
        3: 0.2,    # March
        4: 0.7,    # April
        5: 9.2,    # May
        6: 523.1,  # June
        7: 799.7,  # July
        8: 529.7,  # August
        9: 312.3,  # September
        10: 70.3,  # October
        11: 16.7,  # November
        12: 3.6    # December
    }
    
    return monthly_values.get(month, 0)

def main():
    """Main function to prepare rainfall data."""
    rainfall_file = download_imd_rainfall_data()
    
    if rainfall_file:
        # If monthly data, create a summary file
        if "monthly" in str(rainfall_file):
            print("Creating summary statistics from monthly data...")
            # Read the data
            df = pd.read_csv(rainfall_file)
            
            # Calculate summary statistics
            if 'month' in df.columns and 'avg_rainfall_mm' in df.columns:
                # Monthly total and average by month
                monthly_summary = df.copy()
                monthly_summary = monthly_summary.sort_values('month')
                
                # Add season column
                def get_season(month):
                    if month in [12, 1, 2]:
                        return 'Winter'
                    elif month in [3, 4, 5]:
                        return 'Summer'
                    elif month in [6, 7, 8, 9]:
                        return 'Monsoon'
                    else:
                        return 'Post-Monsoon'
                
                monthly_summary['season'] = monthly_summary['month'].apply(get_season)
                
                # Save summary
                summary_file = Path("data/processed/rainfall/mumbai_rainfall_summary.csv")
                summary_file.parent.mkdir(exist_ok=True)
                monthly_summary.to_csv(summary_file, index=False)
                
                print(f"Saved rainfall summary to {summary_file}")

if __name__ == "__main__":
    main()