#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to download and prepare elevation data for Mumbai.
"""

import os
import sys
from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.transform import from_origin
import numpy as np

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def download_mumbai_dem():
    """Download DEM for Mumbai region or create synthetic data."""
    output_dir = Path("data/raw/dem")
    # Ensure the directory exists before trying to save files there
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Output file path
    output_dem = output_dir / "mumbai_dem.tif"
    
    print(f"Creating synthetic DEM for Mumbai region...")
    
    try:
        # Create a simple synthetic DEM
        # Higher values on the east, lower on the west (like Mumbai's actual topography)
        width, height = 300, 400
        dem_data = np.zeros((height, width), dtype=np.float32)
        
        # Create a gradient from west to east (higher on the east)
        for i in range(width):
            dem_data[:, i] = i / width * 100  # 0-100m elevation range
            
        # Add some random variation
        np.random.seed(42)  # For reproducibility
        dem_data += np.random.normal(0, 5, size=(height, width))
        
        # Add some lower areas near the coast (west)
        dem_data[:, :width//5] = np.random.normal(2, 1, size=(height, width//5))
        
        # Set transform
        transform = from_origin(72.75, 19.25, 0.001, 0.001)  # Approximate resolution
        
        # Write synthetic DEM
        with rasterio.open(
            output_dem, 'w',
            driver='GTiff',
            height=height,
            width=width,
            count=1,
            dtype=dem_data.dtype,
            crs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
            transform=transform,
        ) as dst:
            dst.write(dem_data, 1)
            
        print(f"Created synthetic DEM at {output_dem}")
    except Exception as e:
        print(f"Failed to create synthetic DEM: {e}")
    
    return str(output_dem)

def clip_dem_with_boundary():
    """Clip the DEM with Mumbai boundary (if available)."""
    boundary_path = Path("data/raw/boundaries")
    
    # Find Mumbai boundary file
    # First, check if we have a specific Mumbai boundary
    mumbai_boundary = Path("data/raw/boundaries/mumbai_boundary.shp")
    
    if not mumbai_boundary.exists():
        # If no specific Mumbai boundary, we need to extract it from GADM data
        print("Mumbai specific boundary not found.")
        print("You will need to extract Mumbai from GADM data manually.")
        print("Open the GADM shapefile in QGIS, filter for Mumbai, and save as mumbai_boundary.shp")
        return
    
    # If we have a Mumbai boundary, clip the DEM
    dem_path = Path("data/raw/dem/mumbai_dem.tif")
    if not dem_path.exists():
        print("DEM file not found. Please download it first.")
        return
    
    output_path = Path("data/processed/hydrology/mumbai_dem_clipped.tif")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Clipping DEM with Mumbai boundary...")
    
    try:
        # Read the boundary shapefile
        boundary = gpd.read_file(mumbai_boundary)
        
        # Make sure it's in the same CRS as the raster
        with rasterio.open(dem_path) as src:
            boundary = boundary.to_crs(src.crs)
            
            # Get the geometry as a GeoJSON-like dict
            shapes = boundary.geometry.values
            
            # Clip the raster
            out_image, out_transform = mask(src, shapes, crop=True)
            out_meta = src.meta.copy()
            
            # Update metadata
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })
            
            # Write clipped raster
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(out_image)
        
        print(f"Clipped DEM saved to {output_path}")
    except Exception as e:
        print(f"Error clipping DEM: {e}")

def main():
    """Main function to download and prepare elevation data."""
    dem_path = download_mumbai_dem()
    clip_dem_with_boundary()

if __name__ == "__main__":
    main()
