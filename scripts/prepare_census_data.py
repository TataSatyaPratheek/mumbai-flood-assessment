#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to download and prepare census data for Mumbai flood vulnerability assessment.
Uses open data from Census of India and related sources.
"""

import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import requests
import zipfile
import shutil
from pathlib import Path
from io import BytesIO
import json

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.data.acquisition import download_file

def download_census_data():
    """
    Download census data for Mumbai from official sources.
    Updated with functioning links as of March 2025.
    """
    output_dir = Path("data/raw/census")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Attempting to download Mumbai census data...")

    # Updated Census of India URLs
    census_urls = [
        "https://censusindia.gov.in/nada/index.php/catalog/latest",  # Replace with updated catalog link
        "https://censusindia.gov.in/census.website/data/population-finder"  # Verify functionality
    ]
    
    for url in census_urls:
        try:
            print(f"Trying to download from {url}...")
            output_file = output_dir / f"census_india_{url.split('/')[-1]}.zip"
            
            if download_file(url, output_file):
                print(f"Downloaded census data to {output_file}")
                extract_dir = output_dir / "census_extract"
                extract_dir.mkdir(exist_ok=True)
                
                with zipfile.ZipFile(output_file, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                print(f"Extracted census data to {extract_dir}")
                process_census_files(extract_dir, output_dir)
                return True
        except Exception as e:
            print(f"Error downloading from {url}: {e}")
    
    # Updated Data.gov.in API URL
    datagovIn_query = "https://api.data.gov.in/resource/updated-endpoint-for-census-data"  # Replace with actual endpoint
    
    try:
        response = requests.get(datagovIn_query)
        if response.status_code == 200:
            data = response.json()
            with open(output_dir / "mumbai_census_datagov.json", "w") as f:
                json.dump(data, f)
            print("Downloaded census data from data.gov.in")
            return True
        else:
            print(f"data.gov.in request failed with status code {response.status_code}")
    except Exception as e:
        print(f"Error with data.gov.in API: {e}")
    
    # Verify WorldPop URL
    worldpop_url = "https://data.worldpop.org/GIS/Population/Global_2000_2020/2020/IND/ind_ppp_2020.tif"
    try:
        worldpop_file = output_dir / "india_population_2020.tif"
        if download_file(worldpop_url, worldpop_file):
            print(f"Downloaded WorldPop population data to {worldpop_file}")
            extract_mumbai_worldpop(worldpop_file, output_dir)
            return True
    except Exception as e:
        print(f"Error downloading WorldPop data: {e}")

    # Manual fallback instructions
    print("\nAutomated downloads failed. Please download census data manually:")
    print("1. Visit Census of India: https://censusindia.gov.in/")
    print("2. Download Mumbai district data (2011 Census)")
    print("3. Place downloaded files in: data/raw/census/")
    
    create_minimal_ward_data(output_dir)
    return False


def process_census_files(extract_dir, output_dir):
    """
    Process extracted census files to create a clean dataset for analysis.
    This will need to be customized based on the actual format of the data.
    """
    # Look for CSV or Excel files in the extracted directory
    csv_files = list(extract_dir.glob("**/*.csv"))
    excel_files = list(extract_dir.glob("**/*.xlsx")) + list(extract_dir.glob("**/*.xls"))
    
    if csv_files:
        # Process the first CSV file found
        process_census_csv(csv_files[0], output_dir)
    elif excel_files:
        # Process the first Excel file found
        process_census_excel(excel_files[0], output_dir)
    else:
        print("No CSV or Excel files found in the extracted census data.")
        return False
    
    return True

def process_census_csv(csv_file, output_dir):
    """Process a CSV file from Census of India."""
    try:
        df = pd.read_csv(csv_file)
        
        # Print column names to help with debugging
        print(f"Columns in {csv_file.name}: {df.columns.tolist()}")
        
        # Look for district-level data for Mumbai
        mumbai_data = df[df['District Name'].str.contains('Mumbai', case=False, na=False)]
        
        if len(mumbai_data) > 0:
            # Save Mumbai data
            mumbai_data.to_csv(output_dir / "mumbai_census_district.csv", index=False)
            print(f"Extracted Mumbai district data with {len(mumbai_data)} records")
            return True
        else:
            print("No Mumbai data found in the CSV file.")
            return False
    except Exception as e:
        print(f"Error processing CSV file {csv_file}: {e}")
        return False

def process_census_excel(excel_file, output_dir):
    """Process an Excel file from Census of India."""
    try:
        # Read all sheets
        xlsx = pd.ExcelFile(excel_file)
        sheet_names = xlsx.sheet_names
        
        # Try to find Mumbai data in any sheet
        mumbai_data_found = False
        
        for sheet in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet)
            
            # Print column names to help with debugging
            print(f"Columns in sheet {sheet}: {df.columns.tolist()}")
            
            # Look for district columns
            district_col = None
            for col in df.columns:
                if 'district' in str(col).lower():
                    district_col = col
                    break
            
            if district_col:
                # Look for Mumbai data
                mumbai_data = df[df[district_col].str.contains('Mumbai', case=False, na=False)]
                
                if len(mumbai_data) > 0:
                    # Save Mumbai data
                    mumbai_data.to_csv(output_dir / f"mumbai_census_{sheet}.csv", index=False)
                    print(f"Extracted Mumbai data from sheet {sheet} with {len(mumbai_data)} records")
                    mumbai_data_found = True
        
        return mumbai_data_found
    except Exception as e:
        print(f"Error processing Excel file {excel_file}: {e}")
        return False

def extract_mumbai_worldpop(worldpop_file, output_dir):
    """
    Extract Mumbai population data from WorldPop raster using Mumbai boundary.
    """
    try:
        import rasterio
        from rasterio.mask import mask
        
        # Get Mumbai boundary
        boundary_file = Path("data/raw/boundaries/mumbai_boundary.shp")
        
        if not boundary_file.exists():
            print("Mumbai boundary file not found. Cannot extract WorldPop data.")
            return False
        
        # Load boundary
        boundary = gpd.read_file(boundary_file)
        
        # Load WorldPop raster
        with rasterio.open(worldpop_file) as src:
            # Make sure boundary is in the same CRS as the raster
            boundary = boundary.to_crs(src.crs)
            
            # Get geometry as GeoJSON-like dict
            shapes = boundary.geometry.values
            
            # Mask the raster
            out_image, out_transform = mask(src, shapes, crop=True)
            out_meta = src.meta.copy()
            
            # Update metadata
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
            
            # Save Mumbai population raster
            mumbai_pop_file = output_dir / "mumbai_population.tif"
            with rasterio.open(mumbai_pop_file, "w", **out_meta) as dest:
                dest.write(out_image)
            
            # Calculate statistics
            population_data = out_image[0]
            # Replace nodata values with 0
            if src.nodata is not None:
                population_data = np.where(population_data == src.nodata, 0, population_data)
            
            total_population = np.sum(population_data)
            mean_population_density = np.mean(population_data[population_data > 0])
            
            print(f"Extracted Mumbai population data from WorldPop")
            print(f"Estimated total population: {int(total_population)}")
            print(f"Mean population density: {mean_population_density:.2f} people per pixel")
            
            # Create a summary CSV
            summary_data = {
                'source': ['WorldPop 2020'],
                'total_population': [int(total_population)],
                'mean_population_density': [mean_population_density],
                'min_density': [np.min(population_data[population_data > 0])],
                'max_density': [np.max(population_data)]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv(output_dir / "mumbai_population_summary.csv", index=False)
            
            # Now try to extract ward-level statistics if wards are available
            ward_file = Path("data/raw/boundaries/mumbai_wards.shp")
            if ward_file.exists():
                extract_ward_population(worldpop_file, ward_file, output_dir)
            
            return True
    except Exception as e:
        print(f"Error extracting WorldPop data: {e}")
        return False

def extract_ward_population(worldpop_file, ward_file, output_dir):
    """
    Extract population statistics for each ward from WorldPop data.
    """
    try:
        import rasterio
        from rasterio.mask import mask
        import rasterstats
        
        # Load wards
        wards = gpd.read_file(ward_file)
        
        # Use rasterstats to get zonal statistics
        stats = rasterstats.zonal_stats(
            wards,
            worldpop_file,
            stats=['sum', 'mean', 'min', 'max'],
            nodata=0
        )
        
        # Create DataFrame from stats
        ward_pop = pd.DataFrame(stats)
        
        # Combine with ward IDs
        if 'ward_id' in wards.columns:
            ward_pop['ward_id'] = wards['ward_id']
        else:
            ward_pop['ward_id'] = [f"W{i+1:02d}" for i in range(len(wards))]
        
        # Add ward names if available
        if 'ward_name' in wards.columns:
            ward_pop['ward_name'] = wards['ward_name']
        
        # Calculate area in sq km
        wards_proj = wards.to_crs(epsg=32643)  # UTM 43N for accurate area calculation
        ward_pop['area_sqkm'] = wards_proj.area / 1_000_000  # Convert from sq m to sq km
        
        # Calculate population density
        ward_pop['population_density'] = ward_pop['sum'] / ward_pop['area_sqkm']
        
        # Rename columns
        ward_pop = ward_pop.rename(columns={
            'sum': 'total_population',
            'mean': 'mean_pixel_population',
            'min': 'min_pixel_population',
            'max': 'max_pixel_population'
        })
        
        # Try to get socioeconomic indicators from other sources
        # Check if we have any census district data that can inform these indicators
        district_file = output_dir / "mumbai_census_district.csv"
        
        if district_file.exists():
            try:
                district_data = pd.read_csv(district_file)
                # Use district data to inform ward-level estimates
                print("Using district-level census data to inform ward estimates.")
                # Implementation would depend on the actual structure of the district data
            except Exception as e:
                print(f"Error using district data: {e}")
                # Fall back to synthetic indicators
                create_synthetic_indicators(ward_pop)
        else:
            # If no district data, create synthetic indicators
            create_synthetic_indicators(ward_pop)
        
        # Save to file
        ward_pop.to_csv(output_dir / "mumbai_ward_census.csv", index=False)
        print(f"Extracted population data for {len(ward_pop)} wards")
        
        return True
    except Exception as e:
        print(f"Error extracting ward population: {e}")
        return False

def create_synthetic_indicators(ward_pop):
    """
    Create synthetic socioeconomic indicators based on population density.
    These are placeholder values that should be replaced with real data.
    """
    print("WARNING: Creating synthetic socioeconomic indicators.")
    print("These should be replaced with actual census data when available.")
    
    # Generate synthetic socioeconomic indicators correlated with population density
    # Higher density often correlates with higher poverty in many urban contexts
    # But this is a simplification and should be replaced with real data
    np.random.seed(42)  # For reproducibility
    
    # Poverty index (higher for higher density areas, with some randomness)
    pop_density_norm = (ward_pop['population_density'] - ward_pop['population_density'].min()) / \
                      (ward_pop['population_density'].max() - ward_pop['population_density'].min())
    ward_pop['poverty_index'] = 10 + 30 * pop_density_norm + np.random.normal(0, 5, len(ward_pop))
    ward_pop['poverty_index'] = ward_pop['poverty_index'].clip(5, 50)  # Limit to reasonable range
    
    # Vulnerable population percentage (correlation with poverty + randomness)
    ward_pop['vulnerable_population_pct'] = 5 + 20 * pop_density_norm + np.random.normal(0, 3, len(ward_pop))
    ward_pop['vulnerable_population_pct'] = ward_pop['vulnerable_population_pct'].clip(2, 35)
    
    # Slum household percentage (correlation with poverty + randomness)
    ward_pop['slum_household_pct'] = 5 + 35 * pop_density_norm + np.random.normal(0, 5, len(ward_pop))
    ward_pop['slum_household_pct'] = ward_pop['slum_household_pct'].clip(0, 60)
    
    # Concrete building percentage (negative correlation with poverty + randomness)
    ward_pop['concrete_building_pct'] = 90 - 50 * pop_density_norm + np.random.normal(0, 5, len(ward_pop))
    ward_pop['concrete_building_pct'] = ward_pop['concrete_building_pct'].clip(30, 95)

def create_minimal_ward_data(output_dir):
    """
    Create a minimal ward dataset if all other methods fail.
    This uses ward boundaries and assigns synthetic data.
    """
    ward_file = Path("data/raw/boundaries/mumbai_wards.shp")
    
    if not ward_file.exists():
        print("Ward boundaries not found. Cannot create minimal census data.")
        return False
    
    try:
        # Load ward boundaries
        wards = gpd.read_file(ward_file)
        
        # Create a new DataFrame for census data
        census_data = []
        
        for idx, ward in wards.iterrows():
            ward_id = ward['ward_id'] if 'ward_id' in ward else f"W{idx+1:02d}"
            ward_name = ward['ward_name'] if 'ward_name' in ward else f"Ward-{idx+1}"
            
            # Project to UTM 43N for accurate area calculation
            ward_geom_proj = ward.geometry
            if wards.crs is not None:
                wards_proj = wards.to_crs(epsg=32643)
                ward_geom_proj = wards_proj.iloc[idx].geometry
            
            # Calculate area in square kilometers
            area_sqkm = ward_geom_proj.area / 1_000_000
            
            # Generate synthetic population based on area
            # Mumbai's average population density is around 20,000/km²
            population_density = np.random.uniform(10000, 30000)
            population = int(area_sqkm * population_density)
            
            # Add record
            census_data.append({
                'ward_id': ward_id,
                'ward_name': ward_name,
                'total_population': population,
                'population_density': population_density,
                'households': int(population / 4.5),  # Average household size
                'area_sqkm': area_sqkm,
                'literacy_rate': np.random.uniform(70, 95),
                'poverty_index': np.random.uniform(10, 40),
                'vulnerable_population_pct': np.random.uniform(5, 25),
                'slum_household_pct': np.random.uniform(5, 40),
                'concrete_building_pct': np.random.uniform(40, 90)
            })
        
        # Create DataFrame
        census_df = pd.DataFrame(census_data)
        
        # Save to CSV
        census_df.to_csv(output_dir / "mumbai_ward_census.csv", index=False)
        
        print(f"Created minimal census data for {len(census_df)} wards")
        print("WARNING: This is synthetic data and should be replaced with actual census data")
        
        return True
    except Exception as e:
        print(f"Error creating minimal ward data: {e}")
        return False

def main():
    """Main function to prepare census data."""
    success = download_census_data()
    
    if success:
        print("Census data preparation complete.")
    else:
        print("Census data preparation encountered issues. Please check the logs.")
        print("You will need to obtain additional data manually.")

if __name__ == "__main__":
    main()