#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to prepare census data for Mumbai flood vulnerability assessment.
For demonstration, we'll create a synthetic dataset as actual census data
may need to be manually downloaded from Census of India.
"""

import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def create_synthetic_census_data():
    """
    Create synthetic census data for Mumbai wards.
    In a real scenario, you would import actual census data.
    """
    # Define the output path
    output_dir = Path("data/raw/census")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if we have Mumbai boundary/wards data
    ward_file = Path("data/raw/boundaries/mumbai_wards.shp")
    
    if not ward_file.exists():
        print("Mumbai wards shapefile not found.")
        print("Creating synthetic ward data for demonstration...")
        
        # Create a synthetic wards GeoDataFrame
        # For a real project, you would use actual ward boundaries
        from shapely.geometry import Polygon
        
        # Create some ward polygons (very simplified)
        ward_polygons = []
        ward_names = []
        ward_ids = []
        
        # Divide Mumbai area into a 3x3 grid for demonstration
        mumbai_bounds = (72.75, 18.85, 73.05, 19.25)
        x_step = (mumbai_bounds[2] - mumbai_bounds[0]) / 3
        y_step = (mumbai_bounds[3] - mumbai_bounds[1]) / 3
        
        for i in range(3):
            for j in range(3):
                x_min = mumbai_bounds[0] + i * x_step
                y_min = mumbai_bounds[1] + j * y_step
                x_max = mumbai_bounds[0] + (i + 1) * x_step
                y_max = mumbai_bounds[1] + (j + 1) * y_step
                
                ward_poly = Polygon([
                    (x_min, y_min), (x_max, y_min),
                    (x_max, y_max), (x_min, y_max),
                    (x_min, y_min)
                ])
                
                ward_polygons.append(ward_poly)
                ward_name = f"Ward-{chr(65+i)}{j+1}"  # A1, A2, ..., C3
                ward_names.append(ward_name)
                ward_ids.append(f"W{i*3+j+1:02d}")
        
        # Create the GeoDataFrame
        wards_gdf = gpd.GeoDataFrame({
            'ward_id': ward_ids,
            'ward_name': ward_names,
            'geometry': ward_polygons
        })
        wards_gdf.crs = "EPSG:4326"  # WGS 84
        
        # Save to file
        wards_gdf.to_file(Path("data/raw/boundaries/mumbai_wards.shp"))
        
        print(f"Created synthetic ward boundaries with {len(wards_gdf)} wards.")
    else:
        # Load actual ward boundaries
        wards_gdf = gpd.read_file(ward_file)
        print(f"Loaded ward boundaries with {len(wards_gdf)} wards.")
    
    # Create synthetic census data for these wards
    census_data = []
    
    for idx, ward in wards_gdf.iterrows():
        ward_id = ward['ward_id'] if 'ward_id' in ward else f"W{idx+1:02d}"
        
        # Generate synthetic population and housing data
        population = np.random.randint(50000, 200000)
        area_sqkm = ward.geometry.area * 111 * 111  # Rough conversion from degrees to km²
        
        census_data.append({
            'ward_id': ward_id,
            'ward_name': ward['ward_name'] if 'ward_name' in ward else f"Ward-{idx+1}",
            'population': population,
            'population_density': population / area_sqkm,
            'households': int(population / 4.5),  # Average household size
            'literacy_rate': np.random.uniform(70, 95),
            'poverty_index': np.random.uniform(10, 40),
            'vulnerable_population_pct': np.random.uniform(5, 25),
            'slum_household_pct': np.random.uniform(5, 40),
            'concrete_building_pct': np.random.uniform(40, 90),
            'area_sqkm': area_sqkm
        })
    
    # Create DataFrame
    census_df = pd.DataFrame(census_data)
    
    # Save to CSV
    output_file = output_dir / "mumbai_ward_census_synthetic.csv"
    census_df.to_csv(output_file, index=False)
    
    print(f"Created synthetic census data for {len(census_df)} wards.")
    print(f"Saved to {output_file}")
    
    return census_df

def main():
    """Main function to prepare census data."""
    create_synthetic_census_data()

if __name__ == "__main__":
    main()
