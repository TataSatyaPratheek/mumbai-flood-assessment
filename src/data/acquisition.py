#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data acquisition functions for Mumbai flood vulnerability assessment.
"""

import os
import requests
import zipfile
import geopandas as gpd
from pathlib import Path

def download_file(url, output_path):
    """
    Download a file from a URL to the specified path.
    
    Parameters:
    -----------
    url : str
        URL to download from
    output_path : str
        Path where the file should be saved
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False

def download_mumbai_boundaries():
    """
    Download Mumbai administrative boundaries.
    """
    # Example URL - replace with actual source
    url = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_IND_shp.zip"
    output_dir = Path("data/raw/boundaries")
    zip_path = output_dir / "gadm41_IND_shp.zip"
    
    # Create directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download and extract
    if download_file(url, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        print(f"Mumbai boundaries downloaded and extracted to {output_dir}")
        return True
    return False

def download_srtm_dem():
    """
    Download SRTM DEM data for Mumbai region.
    """
    # For demonstration - in reality, you might use APIs like elevatr or whitebox
    # Or download from sources like https://earthexplorer.usgs.gov/
    print("For SRTM data, please download manually from Earth Explorer")
    print("1. Visit https://earthexplorer.usgs.gov/")
    print("2. Search for Mumbai region")
    print("3. Select SRTM 1 Arc-Second Global dataset")
    print("4. Download and save to data/raw/dem/")
    
    # For automated download, you could use elevation package:
    # import elevation
    # elevation.clip(bounds=(72.7, 18.8, 73.1, 19.3), output='data/raw/dem/mumbai_dem.tif')
    
    return True

if __name__ == "__main__":
    # Test the functions
    download_mumbai_boundaries()
    download_srtm_dem()
