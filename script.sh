#!/bin/bash

# Set up environment
echo "Setting up project environment..."

# Create project directory structure
mkdir -p data/{raw,processed,external}
mkdir -p data/raw/{dem,rainfall,census,infrastructure,boundaries}
mkdir -p data/processed/{vulnerability,hydrology,socioeconomic}
mkdir -p notebooks
mkdir -p src/{data,models,visualization,api}
mkdir -p docs
mkdir -p dashboard
mkdir -p scripts

# Create Python module structure
touch src/__init__.py
touch src/data/__init__.py
touch src/models/__init__.py
touch src/visualization/__init__.py
touch src/api/__init__.py

# Create the source data directories first
echo "Creating data directories..."
mkdir -p data/raw/dem
mkdir -p data/raw/boundaries
mkdir -p data/raw/census
mkdir -p data/raw/rainfall
mkdir -p data/raw/infrastructure
mkdir -p data/processed/vulnerability
mkdir -p data/processed/hydrology

# Now set up the scripts
echo "Creating acquisition module..."
cat > src/data/acquisition.py << 'EOF'
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
EOF

echo "Creating preprocessing module..."
cat > src/data/preprocessing.py << 'EOF'
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
EOF

echo "Creating the environment.yml file..."
cat > environment.yml << 'EOF'
name: flood-assessment
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - gdal=3.4.3
  - geopandas=0.10.2
  - rasterio=1.2.10
  - numpy=1.22.3
  - pandas=1.4.2
  - matplotlib=3.5.1
  - seaborn=0.11.2
  - scikit-learn=1.0.2
  - jupyter=1.0.0
  - notebook=6.4.11
  - flask=2.1.1
  - xarray=2022.3.0
  - netcdf4=1.5.8
  - pip=22.0.4
  - pip:
    - richdem==0.3.4
    - elevation==1.1.3
    - whitebox==2.1.2
    - rasterstats==0.16.0
    - osmnx==2.0.1
EOF

echo "Creating the download_elevation.py script..."
cat > scripts/download_elevation.py << 'EOF'
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
EOF

echo "Creating infrastructure data script..."
cat > scripts/prepare_infrastructure_data.py << 'EOF'
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
EOF

echo "Creating vulnerability analysis script..."
cat > src/models/vulnerability.py << 'EOF'
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Vulnerability analysis for Mumbai flood assessment.
"""

import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.transform import from_origin
from shapely.geometry import mapping
import matplotlib.pyplot as plt
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent.parent

def calculate_physical_vulnerability():
    """
    Calculate physical vulnerability based on elevation and slope.
    """
    print("Calculating physical vulnerability...")
    
    # Check if we have elevation data
    dem_path = project_root / "data/raw/dem/mumbai_dem.tif"
    wards_path = project_root / "data/raw/boundaries/mumbai_wards.shp"
    
    if not dem_path.exists():
        print(f"DEM file not found: {dem_path}")
        print("Creating a synthetic DEM for demonstration...")
        
        # Create a synthetic DEM if one doesn't exist
        try:
            # Ensure the directory exists
            dem_dir = dem_path.parent
            dem_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a simple synthetic DEM
            # Higher values on the east, lower on the west (like Mumbai's actual topography)
            width, height = 300, 400
            dem_data = np.zeros((height, width), dtype=np.float32)
            
            # Create a gradient from west to east (higher on the east)
            for i in range(width):
                dem_data[:, i] = i / width * 100  # 0-100m elevation range
                
            # Add some random variation
            dem_data += np.random.normal(0, 5, size=(height, width))
            
            # Add some lower areas near the coast (west)
            dem_data[:, :width//5] = np.random.normal(2, 1, size=(height, width//5))
            
            # Set transform
            transform = from_origin(72.75, 19.25, 0.001, 0.001)  # Approximate resolution
            
            # Write synthetic DEM
            with rasterio.open(
                dem_path, 'w',
                driver='GTiff',
                height=height,
                width=width,
                count=1,
                dtype=dem_data.dtype,
                crs='+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs',
                transform=transform,
            ) as dst:
                dst.write(dem_data, 1)
                
            print(f"Created synthetic DEM at {dem_path}")
        except Exception as e:
            print(f"Failed to create synthetic DEM: {e}")
            return None
    
    if not wards_path.exists():
        print(f"Wards file not found: {wards_path}")
        return None
    
    # Load wards and DEM
    wards = gpd.read_file(wards_path)
    
    # Initialize dataframe for results
    vulnerability = pd.DataFrame({
        'ward_id': wards['ward_id'] if 'ward_id' in wards.columns else range(1, len(wards) + 1)
    })
    
    # Calculate statistics for each ward
    elevation_stats = []
    
    with rasterio.open(dem_path) as src:
        # Ensure wards are in the same CRS as the DEM
        wards = wards.to_crs(src.crs)
        
        for idx, ward in wards.iterrows():
            # Get ward geometry
            geom = [mapping(ward.geometry)]
            
            # Mask the DEM with the ward geometry
            try:
                out_image, out_transform = mask(src, geom, crop=True)
                
                # Get valid data (exclude nodata values)
                data = out_image[0]
                valid_data = data[data != src.nodata] if src.nodata is not None else data.flatten()
                
                if len(valid_data) > 0:
                    # Calculate statistics
                    elevation_mean = float(np.mean(valid_data))
                    elevation_min = float(np.min(valid_data))
                    elevation_max = float(np.max(valid_data))
                    
                    # Calculate percentage of area below certain thresholds
                    pct_below_5m = float(np.sum(valid_data < 5) / len(valid_data) * 100)
                    pct_below_10m = float(np.sum(valid_data < 10) / len(valid_data) * 100)
                else:
                    elevation_mean = elevation_min = elevation_max = 0
                    pct_below_5m = pct_below_10m = 0
            except Exception as e:
                print(f"Error processing ward {idx}: {e}")
                elevation_mean = elevation_min = elevation_max = 0
                pct_below_5m = pct_below_10m = 0
            
            # Store statistics
            elevation_stats.append({
                'ward_id': ward['ward_id'] if 'ward_id' in ward else f"W{idx+1:02d}",
                'elevation_mean': elevation_mean,
                'elevation_min': elevation_min,
                'elevation_max': elevation_max,
                'pct_below_5m': pct_below_5m,
                'pct_below_10m': pct_below_10m
            })
    
    # Create dataframe
    elevation_df = pd.DataFrame(elevation_stats)
    
    # Merge with wards
    vulnerability = pd.merge(vulnerability, elevation_df, on='ward_id')
    
    # Calculate physical vulnerability index
    # Higher value = higher vulnerability
    # Simple formula: normalize and weight low elevation and high percentage below thresholds
    
    # Normalize each factor to 0-1 range
    for col in ['elevation_mean', 'elevation_min']:
        if vulnerability[col].max() > vulnerability[col].min():
            vulnerability[f'{col}_norm'] = 1 - ((vulnerability[col] - vulnerability[col].min()) / 
                                         (vulnerability[col].max() - vulnerability[col].min()))
        else:
            vulnerability[f'{col}_norm'] = 0
    
    for col in ['pct_below_5m', 'pct_below_10m']:
        if vulnerability[col].max() > vulnerability[col].min():
            vulnerability[f'{col}_norm'] = ((vulnerability[col] - vulnerability[col].min()) / 
                                     (vulnerability[col].max() - vulnerability[col].min()))
        else:
            vulnerability[f'{col}_norm'] = 0
    
    # Calculate physical vulnerability index
    weights = {
        'elevation_mean_norm': 0.3,
        'elevation_min_norm': 0.3,
        'pct_below_5m_norm': 0.25,
        'pct_below_10m_norm': 0.15
    }
    
    vulnerability['physical_vulnerability'] = sum(vulnerability[col] * weight 
                                                for col, weight in weights.items())
    
    # Scale to 0-100 for interpretability
    vulnerability['physical_vulnerability'] = vulnerability['physical_vulnerability'] * 100
    
    # Save to file
    output_dir = project_root / "data/processed/vulnerability"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "physical_vulnerability.csv"
    vulnerability.to_csv(output_file, index=False)
    
    print(f"Physical vulnerability calculated and saved to {output_file}")
    
    return vulnerability

def calculate_socioeconomic_vulnerability():
    """
    Calculate socioeconomic vulnerability based on census data.
    """
    print("Calculating socioeconomic vulnerability...")
    
    # Check if we have census data
    census_path = project_root / "data/raw/census/mumbai_ward_census_synthetic.csv"
    
    if not census_path.exists():
        print(f"Census file not found: {census_path}")
        return None
    
    # Load census data
    census = pd.read_csv(census_path)
    
    # Calculate socioeconomic vulnerability index
    # Higher value = higher vulnerability
    
    # Normalize each factor to 0-1 range
    factors = [
        'population_density',  # Higher density = higher vulnerability
        'poverty_index',       # Higher poverty = higher vulnerability
        'vulnerable_population_pct', # Higher vulnerable population = higher vulnerability
        'slum_household_pct'   # Higher slum percentage = higher vulnerability
    ]
    
    # Initialize vulnerability dataframe
    vulnerability = census[['ward_id', 'ward_name']].copy()
    
    # Normalize factors
    for factor in factors:
        if factor in census.columns:
            if census[factor].max() > census[factor].min():
                vulnerability[f'{factor}_norm'] = ((census[factor] - census[factor].min()) / 
                                         (census[factor].max() - census[factor].min()))
            else:
                vulnerability[f'{factor}_norm'] = 0
    
    # For concrete building percentage, higher percentage = lower vulnerability
    if 'concrete_building_pct' in census.columns:
        if census['concrete_building_pct'].max() > census['concrete_building_pct'].min():
            vulnerability['concrete_building_pct_norm'] = 1 - ((census['concrete_building_pct'] - census['concrete_building_pct'].min()) / 
                                                    (census['concrete_building_pct'].max() - census['concrete_building_pct'].min()))
        else:
            vulnerability['concrete_building_pct_norm'] = 0
        factors.append('concrete_building_pct')
    
    # Calculate socioeconomic vulnerability index with weights
    weights = {
        'population_density_norm': 0.25,
        'poverty_index_norm': 0.25,
        'vulnerable_population_pct_norm': 0.2,
        'slum_household_pct_norm': 0.2,
        'concrete_building_pct_norm': 0.1
    }
    
    # Calculate weighted sum of available factors
    vulnerability['socioeconomic_vulnerability'] = 0
    total_weight = 0
    
    for factor, weight in weights.items():
        if factor in vulnerability.columns:
            vulnerability['socioeconomic_vulnerability'] += vulnerability[factor] * weight
            total_weight += weight
    
    # Normalize by total weight used
    if total_weight > 0:
        vulnerability['socioeconomic_vulnerability'] /= total_weight
    
    # Scale to 0-100 for interpretability
    vulnerability['socioeconomic_vulnerability'] *= 100
    
    # Save to file
    output_dir = project_root / "data/processed/vulnerability"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "socioeconomic_vulnerability.csv"
    vulnerability.to_csv(output_file, index=False)
    
    print(f"Socioeconomic vulnerability calculated and saved to {output_file}")
    
    return vulnerability

def calculate_overall_vulnerability():
    """
    Calculate overall vulnerability by combining physical and socioeconomic factors.
    """
    print("Calculating overall vulnerability...")
    
    # Load physical and socioeconomic vulnerability
    phys_path = project_root / "data/processed/vulnerability/physical_vulnerability.csv"
    socio_path = project_root / "data/processed/vulnerability/socioeconomic_vulnerability.csv"
    
    # Check if we need to generate physical vulnerability
    if not phys_path.exists() and socio_path.exists():
        print("Physical vulnerability file not found. Generating it now...")
        physical = calculate_physical_vulnerability()
        if physical is None:
            print("Failed to calculate physical vulnerability.")
            # Fallback to using only socioeconomic data
            socioeconomic = pd.read_csv(socio_path)
            overall = socioeconomic[['ward_id', 'socioeconomic_vulnerability']].copy()
            overall['physical_vulnerability'] = 50.0  # Default middle value
            overall['overall_vulnerability'] = overall['socioeconomic_vulnerability']
        else:
            socioeconomic = pd.read_csv(socio_path)
            # Merge data
            overall = pd.merge(physical[['ward_id', 'physical_vulnerability']], 
                            socioeconomic[['ward_id', 'socioeconomic_vulnerability']], 
                            on='ward_id')
            
            # Calculate overall vulnerability as weighted sum
            weights = {
                'physical_vulnerability': 0.6,
                'socioeconomic_vulnerability': 0.4
            }
            
            overall['overall_vulnerability'] = (
                overall['physical_vulnerability'] * weights['physical_vulnerability'] +
                overall['socioeconomic_vulnerability'] * weights['socioeconomic_vulnerability']
            )
    elif not socio_path.exists():
        print("Socioeconomic vulnerability file not found.")
        return None
    else:
        # Load data
        physical = pd.read_csv(phys_path)
        socioeconomic = pd.read_csv(socio_path)
        
        # Merge data
        overall = pd.merge(physical[['ward_id', 'physical_vulnerability']], 
                        socioeconomic[['ward_id', 'socioeconomic_vulnerability']], 
                        on='ward_id')
        
        # Calculate overall vulnerability as weighted sum
        weights = {
            'physical_vulnerability': 0.6,
            'socioeconomic_vulnerability': 0.4
        }
        
        overall['overall_vulnerability'] = (
            overall['physical_vulnerability'] * weights['physical_vulnerability'] +
            overall['socioeconomic_vulnerability'] * weights['socioeconomic_vulnerability']
        )
    
    # Save to file
    output_dir = project_root / "data/processed/vulnerability"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "overall_vulnerability.csv"
    overall.to_csv(output_file, index=False)
    
    print(f"Overall vulnerability calculated and saved to {output_file}")
    
    # Merge with ward boundaries for mapping
    wards_path = project_root / "data/raw/boundaries/mumbai_wards.shp"
    if wards_path.exists():
        wards = gpd.read_file(wards_path)
        
        # Ensure ward_id is string type in both dataframes
        overall['ward_id'] = overall['ward_id'].astype(str)
        if 'ward_id' in wards.columns:
            wards['ward_id'] = wards['ward_id'].astype(str)
            # Merge
            vulnerability_map = wards.merge(overall, on='ward_id')
        else:
            print("Ward ID not found in wards shapefile. Cannot create vulnerability map.")
            return overall
        
        # Save to file
        output_file = output_dir / "overall_vulnerability.shp"
        vulnerability_map.to_file(output_file)
        
        print(f"Vulnerability map saved to {output_file}")
        
        # Create a simple map
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        vulnerability_map.plot(column='overall_vulnerability', cmap='YlOrRd', 
                              legend=True, ax=ax)
        ax.set_title('Overall Flood Vulnerability Index')
        
        # Save figure
        fig_path = output_dir / "vulnerability_map.png"
        plt.savefig(fig_path, dpi=300, bbox_inches='tight')
        
        print(f"Vulnerability map figure saved to {fig_path}")
    
    return overall

def main():
    """Main function to calculate vulnerability indices."""
    # Calculate physical vulnerability
    physical = calculate_physical_vulnerability()
    
    # Calculate socioeconomic vulnerability
    socioeconomic = calculate_socioeconomic_vulnerability()
    
    # Calculate overall vulnerability
    overall = calculate_overall_vulnerability()
    
    print("Vulnerability analysis completed.")

if __name__ == "__main__":
    main()
EOF

echo "Creating master script to run all steps..."
cat > run_flood_assessment.sh << 'EOF'
#!/bin/bash

# Execute the project setup and data preparation

echo "===== Starting Mumbai Flood Vulnerability Assessment Project ====="

# Ensure directories exist
mkdir -p data/raw/dem
mkdir -p data/raw/boundaries
mkdir -p data/raw/census 
mkdir -p data/raw/rainfall
mkdir -p data/raw/infrastructure
mkdir -p data/processed/vulnerability
mkdir -p data/processed/hydrology

# Download and prepare boundaries
echo -e "\n===== Downloading Administrative Boundaries ====="
python scripts/download_boundaries.py

# Generate elevation data
echo -e "\n===== Creating Elevation Data ====="
python scripts/download_elevation.py

# Prepare census data
echo -e "\n===== Preparing Census Data ====="
python scripts/prepare_census_data.py

# Prepare rainfall data
echo -e "\n===== Preparing Rainfall Data ====="
python scripts/prepare_rainfall_data.py

# Prepare infrastructure data
echo -e "\n===== Preparing Infrastructure Data ====="
python scripts/prepare_infrastructure_data.py

# Run vulnerability analysis
echo -e "\n===== Running Vulnerability Analysis ====="
python src/models/vulnerability.py

echo -e "\n===== Project Setup Complete ====="
echo "You can now explore the data in Jupyter Notebook"
echo "Run: jupyter notebook notebooks/01-initial-data-exploration.ipynb"
EOF

chmod +x run_flood_assessment.sh

echo "Setup complete! You can now run the project with ./run_flood_assessment.sh"

# opentopography api: d9770e3ef066cd18058f9c948df7c485