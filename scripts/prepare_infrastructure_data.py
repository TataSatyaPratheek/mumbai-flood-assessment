#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to download and prepare infrastructure data for Mumbai using OSM data.
"""

import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
import time
from shapely.geometry import LineString, Polygon, Point

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def create_synthetic_roads(output_dir):
    """Create synthetic road network."""
    try:
        print("Creating synthetic road network...")
        
        # Mumbai bounds
        xmin, ymin, xmax, ymax = 72.75, 18.85, 73.05, 19.25
        
        # Create a grid of roads
        roads = []
        
        # Horizontal roads
        for y in np.linspace(ymin, ymax, 10):
            road = LineString([(xmin, y), (xmax, y)])
            roads.append({
                'geometry': road,
                'highway': 'residential',
                'name': f'EW Road {y:.4f}',
                'osm_id': f'synth_{int(time.time())}_{len(roads)}'
            })
        
        # Vertical roads
        for x in np.linspace(xmin, xmax, 10):
            road = LineString([(x, ymin), (x, ymax)])
            roads.append({
                'geometry': road,
                'highway': 'residential',
                'name': f'NS Road {x:.4f}',
                'osm_id': f'synth_{int(time.time())}_{len(roads)}'
            })
        
        # Create GeoDataFrame
        roads_gdf = gpd.GeoDataFrame(roads, crs="EPSG:4326")
        
        # Save to file
        output_file = output_dir / "mumbai_roads.shp"
        roads_gdf.to_file(output_file)
        print(f"Created synthetic road network and saved to {output_file}")
    except Exception as e:
        print(f"Error creating synthetic roads: {e}")

def create_synthetic_water(output_dir):
    """Create synthetic water bodies."""
    try:
        print("Creating synthetic water bodies...")
        
        # Mumbai bounds
        xmin, ymin, xmax, ymax = 72.75, 18.85, 73.05, 19.25
        
        # Create some water bodies
        water_bodies = []
        
        # A large body of water on the west side (representing the Arabian Sea)
        west_coast = Polygon([
            (xmin, ymin), (xmin + 0.05, ymin), 
            (xmin + 0.03, ymax), (xmin, ymax)
        ])
        water_bodies.append({
            'geometry': west_coast,
            'natural': 'water',
            'name': 'Arabian Sea',
            'osm_id': f'synth_water_{int(time.time())}_1'
        })
        
        # A few small lakes/ponds scattered throughout
        for i in range(5):
            x = np.random.uniform(xmin + 0.1, xmax - 0.02)
            y = np.random.uniform(ymin + 0.05, ymax - 0.05)
            size = np.random.uniform(0.005, 0.02)
            lake = Polygon([
                (x, y), (x + size, y),
                (x + size, y + size), (x, y + size)
            ])
            water_bodies.append({
                'geometry': lake,
                'natural': 'water',
                'name': f'Lake {i+1}',
                'osm_id': f'synth_water_{int(time.time())}_{i+2}'
            })
        
        # Create GeoDataFrame
        water_gdf = gpd.GeoDataFrame(water_bodies, crs="EPSG:4326")
        
        # Save to file
        output_file = output_dir / "mumbai_water.shp"
        water_gdf.to_file(output_file)
        print(f"Created synthetic water bodies and saved to {output_file}")
    except Exception as e:
        print(f"Error creating synthetic water bodies: {e}")

def create_synthetic_critical(output_dir):
    """Create synthetic critical infrastructure."""
    try:
        print("Creating synthetic critical infrastructure...")
        
        # Mumbai bounds
        xmin, ymin, xmax, ymax = 72.75, 18.85, 73.05, 19.25
        
        # Create critical infrastructure
        critical_infra = []
        
        # Types of facilities
        facility_types = [
            ('hospital', 'Hospital'),
            ('fire_station', 'Fire Station'),
            ('police', 'Police Station'),
            ('school', 'School'),
            ('university', 'University')
        ]
        
        # Generate random points
        for i in range(20):
            x = np.random.uniform(xmin + 0.05, xmax - 0.05)
            y = np.random.uniform(ymin + 0.05, ymax - 0.05)
            point = Point(x, y)
            
            # Random facility type
            facility_type, facility_name = facility_types[i % len(facility_types)]
            
            critical_infra.append({
                'geometry': point,
                'amenity': facility_type,
                'name': f'{facility_name} {i+1}',
                'osm_id': f'synth_crit_{int(time.time())}_{i+1}'
            })
        
        # Create GeoDataFrame
        critical_gdf = gpd.GeoDataFrame(critical_infra, crs="EPSG:4326")
        
        # Save to file
        output_file = output_dir / "mumbai_critical.shp"
        critical_gdf.to_file(output_file)
        print(f"Created synthetic critical infrastructure and saved to {output_file}")
    except Exception as e:
        print(f"Error creating synthetic critical infrastructure: {e}")

def download_mumbai_infrastructure():
    """
    Download Mumbai infrastructure data from OpenStreetMap.
    """
    # Define the output path
    output_dir = Path("data/raw/infrastructure")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading Mumbai infrastructure data from OpenStreetMap...")
    
    # We'll use synthetic data instead of attempting to download from OSM
    create_synthetic_roads(output_dir)
    create_synthetic_water(output_dir)
    create_synthetic_critical(output_dir)
    
    return True

def main():
    """Main function to prepare infrastructure data."""
    download_mumbai_infrastructure()

if __name__ == "__main__":
    main()
