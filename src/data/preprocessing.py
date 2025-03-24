#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Data preprocessing functions for Mumbai flood vulnerability assessment.
"""

import os
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import numpy as np
from pathlib import Path

def standardize_projection(input_file, output_file, target_epsg=32643):
    """
    Standardize projection of vector data to UTM 43N (EPSG:32643).
    
    Parameters:
    -----------
    input_file : str
        Path to input shapefile
    output_file : str
        Path to output shapefile
    target_epsg : int
        Target EPSG code (default: 32643 for UTM 43N)
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        data = gpd.read_file(input_file)
        data = data.to_crs(epsg=target_epsg)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        data.to_file(output_file)
        return True
    except Exception as e:
        print(f"Error standardizing projection: {e}")
        return False

def clip_raster_with_boundary(raster_path, boundary_path, output_path):
    """
    Clip a raster to a boundary shapefile.
    
    Parameters:
    -----------
    raster_path : str
        Path to input raster file
    boundary_path : str
        Path to boundary shapefile
    output_path : str
        Path to output clipped raster
    
    Returns:
    --------
    bool
        True if successful, False otherwise
    """
    try:
        # Read the boundary shapefile
        boundary = gpd.read_file(boundary_path)
        
        # Make sure it's in the same CRS as the raster
        with rasterio.open(raster_path) as src:
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
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write clipped raster
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(out_image)
        
        return True
    except Exception as e:
        print(f"Error clipping raster: {e}")
        return False

def create_basic_test_data():
    """
    Create some basic test data for development purposes.
    This is useful when actual data is not yet available.
    """
    try:
        # Create a simple boundary polygon for testing
        from shapely.geometry import Polygon
        
        # Create a polygon roughly around Mumbai
        mumbai_poly = Polygon([
            (72.75, 18.85), (72.75, 19.25), 
            (73.05, 19.25), (73.05, 18.85), 
            (72.75, 18.85)
        ])
        
        # Create a GeoDataFrame
        gdf = gpd.GeoDataFrame(geometry=[mumbai_poly])
        gdf.crs = "EPSG:4326"  # WGS 84
        
        # Save to file
        output_dir = Path("data/raw/boundaries")
        output_dir.mkdir(parents=True, exist_ok=True)
        gdf.to_file(output_dir / "mumbai_test_boundary.shp")
        
        print("Test boundary created successfully")
        return True
    except Exception as e:
        print(f"Error creating test data: {e}")
        return False

if __name__ == "__main__":
    # Test the functions
    create_basic_test_data()
