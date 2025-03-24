#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to extract Mumbai administrative boundaries from GADM data.
"""

import os
import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

def extract_mumbai_boundaries():
    """Extract Mumbai boundaries from GADM data at different levels."""
    # Define paths
    boundary_dir = Path("data/raw/boundaries")
    boundary_dir.mkdir(parents=True, exist_ok=True)
    
    # Output files
    mumbai_boundary_file = boundary_dir / "mumbai_boundary.shp"
    mumbai_wards_file = boundary_dir / "mumbai_wards.shp"
    
    # Check for GADM files
    gadm_level2 = boundary_dir / "gadm41_IND_2.shp"
    
    if not gadm_level2.exists():
        print(f"GADM level 2 file not found at {gadm_level2}")
        print("Please run the download_boundaries.py script first.")
        return False
    
    # Load GADM Level 2 data (districts)
    print("Loading GADM district data...")
    districts = gpd.read_file(gadm_level2)
    
    # Check Maharashtra districts
    print("Available districts in Maharashtra:")
    maharashtra_districts = districts[districts['NAME_1'] == 'Maharashtra']
    print(maharashtra_districts['NAME_2'].unique())
    
    # Filter for Mumbai districts
    mumbai_criteria = maharashtra_districts['NAME_2'].str.contains('Mumbai', case=False, na=False)
    mumbai_districts = maharashtra_districts[mumbai_criteria]
    
    if len(mumbai_districts) == 0:
        print("No Mumbai districts found with standard naming.")
        print("Checking alternative spellings or names...")
        
        # Try with Bombay spelling or partial matches
        bombay_criteria = maharashtra_districts['NAME_2'].str.contains('Bombay|मुंबई|Thane', case=False, na=False)
        mumbai_districts = maharashtra_districts[bombay_criteria]
        
        if len(mumbai_districts) == 0:
            print("Still no Mumbai districts found. Showing all Maharashtra districts:")
            print(maharashtra_districts[['NAME_2', 'VARNAME_2']])
            print("Please modify the script to select the correct district names.")
            return False
    
    print(f"Found {len(mumbai_districts)} Mumbai-related districts")
    print("Districts: ", mumbai_districts['NAME_2'].tolist())
    
    # Save Mumbai boundaries
    mumbai_districts.to_file(mumbai_boundary_file)
    print(f"Mumbai boundaries saved to {mumbai_boundary_file}")
    
    # Load GADM Level 3 data (sub-districts) if available
    gadm_level3 = boundary_dir / "gadm41_IND_3.shp"
    if gadm_level3.exists():
        print("Loading GADM sub-district data...")
        subdistricts = gpd.read_file(gadm_level3)
        
        # Filter for Mumbai sub-districts
        mumbai_subdistricts = subdistricts[subdistricts['NAME_2'].isin(mumbai_districts['NAME_2'])]
        
        if len(mumbai_subdistricts) > 0:
            print(f"Found {len(mumbai_subdistricts)} Mumbai sub-districts")
            
            # Save as ward-level boundaries if wards don't exist yet
            if not mumbai_wards_file.exists():
                # Add ward_id field
                mumbai_subdistricts['ward_id'] = [f"W{i+1:02d}" for i in range(len(mumbai_subdistricts))]
                mumbai_subdistricts.to_file(mumbai_wards_file)
                print(f"Mumbai sub-districts saved as wards to {mumbai_wards_file}")
    
    # Create a simple visualization of the boundaries
    create_boundary_visualization(mumbai_boundary_file, mumbai_wards_file)
    
    return True

def create_boundary_visualization(boundary_file, wards_file):
    """Create a simple visualization of Mumbai boundaries."""
    try:
        # Check if files exist
        if not boundary_file.exists():
            print(f"Boundary file not found: {boundary_file}")
            return False
        
        # Create output directory
        output_dir = Path("visualizations")
        output_dir.mkdir(exist_ok=True)
        
        # Load Mumbai boundary
        boundary = gpd.read_file(boundary_file)
        
        # Plot Mumbai boundary
        fig, ax = plt.subplots(figsize=(12, 10))
        boundary.plot(ax=ax, color='lightgrey', edgecolor='black')
        plt.title("Mumbai Administrative Boundary")
        plt.savefig(output_dir / "mumbai_boundary.png", dpi=300, bbox_inches='tight')
        
        # Plot wards if available
        if wards_file.exists():
            wards = gpd.read_file(wards_file)
            
            # Plot wards
            fig, ax = plt.subplots(figsize=(12, 10))
            boundary.plot(ax=ax, color='lightgrey', edgecolor='black')
            wards.plot(ax=ax, column='ward_id', cmap='tab20', edgecolor='black', alpha=0.7)
            plt.title("Mumbai Administrative Wards")
            plt.savefig(output_dir / "mumbai_wards.png", dpi=300, bbox_inches='tight')
            
            # Create ward statistics
            ward_stats = pd.DataFrame({
                'ward_id': wards['ward_id'],
                'name': wards['NAME_3'] if 'NAME_3' in wards.columns else wards['ward_id'],
                'area_sqkm': wards.to_crs(epsg=32643).area / 1_000_000  # Convert to sq km
            })
            
            # Save stats
            ward_stats.to_csv(output_dir / "mumbai_ward_stats.csv", index=False)
            print(f"Ward statistics saved to {output_dir / 'mumbai_ward_stats.csv'}")
        
        print(f"Visualizations saved to {output_dir}")
        
    except Exception as e:
        print(f"Error creating visualization: {e}")
        return False

if __name__ == "__main__":
    extract_mumbai_boundaries()