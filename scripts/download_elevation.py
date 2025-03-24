#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to download and prepare elevation data for Mumbai.
Uses SRTM 30m and processes it for the Mumbai region.
"""

import os
import sys
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
import requests
import tempfile
import shutil
import subprocess

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def download_mumbai_dem():
    """Download DEM for Mumbai region using elevation package or direct SRTM access."""
    output_dir = Path("data/raw/dem")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Output file path
    output_dem = output_dir / "mumbai_dem.tif"
    
    try:
        # First, check if the elevation package is available (preferred method)
        try:
            import elevation
            
            # Mumbai approximate bounding box
            bounds = (72.75, 18.85, 73.05, 19.25)  # (xmin, ymin, xmax, ymax)
            
            print(f"Downloading SRTM DEM for Mumbai region using elevation package...")
            # Download and crop the DEM
            elevation.clip(bounds=bounds, output=str(output_dem), product="SRTM3")
            print(f"Downloaded SRTM DEM to {output_dem}")
            return str(output_dem)
        
        except ImportError:
            print("Elevation package not available, trying alternative download method...")
        
        # Alternative: Download from OpenTopography using their API
        # Requires API key from OpenTopography
        print("Downloading DEM from OpenTopography API...")
        
        api_url = "https://portal.opentopography.org/API/globaldem"
        params = {
            'demtype': 'SRTM GL3',
            'west': 72.75,
            'east': 73.05,
            'south': 18.85,
            'north': 19.25,
            'outputFormat': 'GTiff',
            'API_Key': 'd9770e3ef066cd18058f9c948df7c485'  # Replace with your API key
        }
        
        response = requests.get(api_url, params=params, stream=True)
        if response.status_code == 200:
            with open(output_dem, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded DEM from OpenTopography to {output_dem}")
            return str(output_dem)
        else:
            print(f"Failed to download from OpenTopography. Status: {response.status_code}")
            print(response.text)
        
        # Another alternative: Direct download from USGS EarthExplorer
        # This requires authentication and is more complex
        # Instead, we'll use GMTED2010 which is publicly available through Google Earth Engine
        try:
            import ee
            
            print("Attempting download using Google Earth Engine...")
            
            # Initialize Earth Engine
            ee.Initialize()
            
            # Define Mumbai region of interest
            mumbai_bbox = ee.Geometry.Rectangle([72.75, 18.85, 73.05, 19.25])
            
            # Get SRTM dataset
            srtm = ee.Image('USGS/SRTMGL1_003')
            
            # Clip to Mumbai region
            srtm_mumbai = srtm.clip(mumbai_bbox)
            
            # Export to Drive or directly download
            # This is a placeholder - actual GEE implementation would be more complex
            print("GEE implementation requires additional setup. Please use manual download.")
            
        except ImportError:
            print("Google Earth Engine not available.")
        
        # Final fallback: Instructions for manual download
        print("\nAutomated download failed. Please download manually:")
        print("1. Visit https://earthexplorer.usgs.gov/")
        print("2. Create an account and log in")
        print("3. Define AOI for Mumbai (72.75, 18.85, 73.05, 19.25)")
        print("4. Select 'Digital Elevation' > 'SRTM' > 'SRTM 1-Arc Second Global'")
        print("5. Find tiles covering Mumbai and download")
        print("6. Place downloaded files in: data/raw/dem/\n")
        
        return None
        
    except Exception as e:
        print(f"Failed to download DEM: {e}")
        return None

def clip_dem_with_boundary():
    """Clip the DEM with Mumbai boundary."""
    # Define file paths
    dem_path = Path("data/raw/dem/mumbai_dem.tif")
    boundary_path = Path("data/raw/boundaries/mumbai_boundary.shp")
    output_path = Path("data/processed/hydrology/mumbai_dem_clipped.tif")
    
    if not dem_path.exists():
        print("DEM file not found. Please download it first.")
        return False
    
    if not boundary_path.exists():
        print("Mumbai boundary file not found. Please run download_boundaries.py first.")
        return False
    
    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Clipping DEM with Mumbai boundary...")
    
    try:
        # Try using GDAL command line tool first (more efficient for large rasters)
        try:
            cmd = [
                'gdalwarp',
                '-cutline', str(boundary_path),
                '-crop_to_cutline',
                '-dstnodata', '-9999',
                str(dem_path),
                str(output_path)
            ]
            subprocess.run(cmd, check=True)
            print(f"Clipped DEM saved to {output_path} using GDAL")
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("GDAL command line tool failed, falling back to rasterio...")
        
        # Fallback to rasterio if GDAL command line fails
        # Read the boundary shapefile
        boundary = gpd.read_file(boundary_path)
        
        # Make sure it's in the same CRS as the raster
        with rasterio.open(dem_path) as src:
            boundary = boundary.to_crs(src.crs)
            
            # Get the geometry as GeoJSON-like dict
            shapes = boundary.geometry.values
            
            # Clip the raster
            out_image, out_transform = mask(src, shapes, crop=True)
            out_meta = src.meta.copy()
            
            # Update metadata
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "nodata": -9999
            })
            
            # Write clipped raster
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(out_image)
        
        print(f"Clipped DEM saved to {output_path} using rasterio")
        return True
    except Exception as e:
        print(f"Error clipping DEM: {e}")
        return False

def main():
    """Main function to download and prepare elevation data."""
    dem_path = download_mumbai_dem()
    if dem_path:
        clip_dem_with_boundary()
    else:
        print("DEM download failed. Cannot proceed with clipping.")

if __name__ == "__main__":
    main()