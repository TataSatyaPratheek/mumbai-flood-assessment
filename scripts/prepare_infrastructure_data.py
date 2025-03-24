#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to download and prepare infrastructure data for Mumbai using OpenStreetMap.
"""

import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
from pathlib import Path
import time
from shapely.geometry import LineString, Polygon, Point
import requests
import zipfile
import tempfile

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def download_osm_infrastructure(output_dir):
    """Download Mumbai infrastructure data from OpenStreetMap using OSMnx."""
    try:
        import osmnx as ox
        print("Downloading Mumbai infrastructure data from OpenStreetMap...")
        
        # Get Mumbai boundary to limit the data extraction
        mumbai_boundary_file = Path("data/raw/boundaries/mumbai_boundary.shp")
        
        if not mumbai_boundary_file.exists():
            print("Mumbai boundary file not found. Falling back to bounding box.")
            # Define Mumbai's bounding box - approximate
            north, south, east, west = 19.28, 18.85, 73.05, 72.75
            
            # Download roads network
            print("Downloading road network...")
            roads = ox.graph_from_bbox(north, south, east, west, network_type='drive')
            roads_gdf = ox.graph_to_gdfs(roads, nodes=False)
            
            # Download buildings
            print("Downloading buildings...")
            buildings = ox.features.features_from_bbox(north, south, east, west, tags={'building': True})
            
            # Download water bodies
            print("Downloading water bodies...")
            water = ox.features.features_from_bbox(north, south, east, west, tags={'natural': 'water'})
            
            # Download landuse
            print("Downloading landuse...")
            landuse = ox.features.features_from_bbox(north, south, east, west, tags={'landuse': True})
            
            # Download critical infrastructure
            print("Downloading critical infrastructure...")
            hospitals = ox.features.features_from_bbox(north, south, east, west, tags={'amenity': 'hospital'})
            schools = ox.features.features_from_bbox(north, south, east, west, tags={'amenity': 'school'})
            fire_stations = ox.features.features_from_bbox(north, south, east, west, tags={'amenity': 'fire_station'})
            police = ox.features.features_from_bbox(north, south, east, west, tags={'amenity': 'police'})
            
        else:
            # Use the boundary shapefile to limit the data extraction
            mumbai_boundary = gpd.read_file(mumbai_boundary_file)
            polygon = mumbai_boundary.unary_union  # Get the combined geometry
            
            # Download roads network
            print("Downloading road network using Mumbai boundary...")
            roads = ox.graph_from_polygon(polygon, network_type='drive')
            roads_gdf = ox.graph_to_gdfs(roads, nodes=False)
            
            # Download buildings
            print("Downloading buildings...")
            buildings = ox.features.features_from_polygon(polygon, tags={'building': True})
            
            # Download water bodies
            print("Downloading water bodies...")
            water = ox.features.features_from_polygon(polygon, tags={'natural': 'water'})
            
            # Download landuse
            print("Downloading landuse...")
            landuse = ox.features.features_from_polygon(polygon, tags={'landuse': True})
            
            # Download critical infrastructure
            print("Downloading critical infrastructure...")
            hospitals = ox.features.features_from_polygon(polygon, tags={'amenity': 'hospital'})
            schools = ox.features.features_from_polygon(polygon, tags={'amenity': 'school'})
            fire_stations = ox.features.features_from_polygon(polygon, tags={'amenity': 'fire_station'})
            police = ox.features.features_from_polygon(polygon, tags={'amenity': 'police'})
        
        # Save all datasets
        roads_gdf.to_file(output_dir / "mumbai_roads.shp")
        print(f"Saved {len(roads_gdf)} road segments to {output_dir / 'mumbai_roads.shp'}")
        
        if len(buildings) > 0:
            buildings.to_file(output_dir / "mumbai_buildings.shp")
            print(f"Saved {len(buildings)} buildings to {output_dir / 'mumbai_buildings.shp'}")
        
        if len(water) > 0:
            water.to_file(output_dir / "mumbai_water.shp")
            print(f"Saved {len(water)} water bodies to {output_dir / 'mumbai_water.shp'}")
        
        if len(landuse) > 0:
            landuse.to_file(output_dir / "mumbai_landuse.shp")
            print(f"Saved {len(landuse)} landuse polygons to {output_dir / 'mumbai_landuse.shp'}")
        
        # Combine critical infrastructure
        critical_infra = pd.concat([hospitals, schools, fire_stations, police])
        if len(critical_infra) > 0:
            critical_infra.to_file(output_dir / "mumbai_critical.shp")
            print(f"Saved {len(critical_infra)} critical infrastructure points to {output_dir / 'mumbai_critical.shp'}")
        
        # Download drainage network (rivers, streams, canals)
        print("Downloading drainage network...")
        try:
            drainage = ox.features.features_from_polygon(polygon if 'polygon' in locals() else None, 
                                                     tags={'waterway': ['river', 'stream', 'canal', 'drain']})
            if len(drainage) > 0:
                drainage.to_file(output_dir / "mumbai_drainage.shp")
                print(f"Saved {len(drainage)} drainage features to {output_dir / 'mumbai_drainage.shp'}")
        except Exception as e:
            print(f"Error downloading drainage network: {e}")
        
        return True
    
    except ImportError:
        print("OSMnx package not available. Trying alternative download method...")
        return download_osm_extract(output_dir)
    
    except Exception as e:
        print(f"Error downloading from OSM using OSMnx: {e}")
        return download_osm_extract(output_dir)

def download_osm_extract(output_dir):
    """
    Download Mumbai OSM extract using Overpass API or a pre-made extract.
    """
    print("Downloading Mumbai OSM data using Overpass API...")
    
    try:
        # First, try using the Overpass API
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Create query to extract all infrastructure in Mumbai
        # Define Mumbai's bounding box
        bbox = "18.85,72.75,19.28,73.05"
        
        # Query for roads, buildings, and water bodies
        query = f"""
        [out:xml][timeout:300];
        (
            way["highway"]({bbox});
            way["building"]({bbox});
            way["natural"="water"]({bbox});
            way["waterway"]({bbox});
            node["amenity"="hospital"]({bbox});
            node["amenity"="school"]({bbox});
            node["amenity"="fire_station"]({bbox});
            node["amenity"="police"]({bbox});
            relation["natural"="water"]({bbox});
        );
        (._;>;);
        out body;
        """
        
        # Make the request
        response = requests.post(overpass_url, data={"data": query})
        
        if response.status_code == 200:
            # Save the OSM data
            osm_file = output_dir / "mumbai_osm.xml"
            with open(osm_file, "wb") as f:
                f.write(response.content)
            
            print(f"Downloaded OSM data to {osm_file}")
            
            # Process with GDAL/OGR to convert to shapefiles
            try:
                import subprocess
                
                # Extract roads
                subprocess.run([
                    "ogr2ogr",
                    "-f", "ESRI Shapefile",
                    str(output_dir / "mumbai_roads.shp"),
                    str(osm_file),
                    "lines",
                    "-where", "highway IS NOT NULL"
                ])
                
                # Extract buildings
                subprocess.run([
                    "ogr2ogr",
                    "-f", "ESRI Shapefile",
                    str(output_dir / "mumbai_buildings.shp"),
                    str(osm_file),
                    "multipolygons",
                    "-where", "building IS NOT NULL"
                ])
                
                # Extract water
                subprocess.run([
                    "ogr2ogr",
                    "-f", "ESRI Shapefile",
                    str(output_dir / "mumbai_water.shp"),
                    str(osm_file),
                    "multipolygons",
                    "-where", "natural='water'"
                ])
                
                # Extract drainage
                subprocess.run([
                    "ogr2ogr",
                    "-f", "ESRI Shapefile",
                    str(output_dir / "mumbai_drainage.shp"),
                    str(osm_file),
                    "lines",
                    "-where", "waterway IS NOT NULL"
                ])
                
                print("Processed OSM data into shapefiles")
                return True
            
            except (ImportError, subprocess.SubprocessError) as e:
                print(f"Error processing OSM data: {e}")
                print("Please install GDAL/OGR tools for processing.")
                
                # Even if processing fails, we still have the raw OSM data
                return True
        else:
            print(f"Overpass API request failed with status code {response.status_code}")
    
    except Exception as e:
        print(f"Error with Overpass API: {e}")
    
    # Fallback: Try to download from Geofabrik
    print("Trying to download Mumbai extract from Geofabrik...")
    try:
        # Geofabrik provides regional extracts of OSM data
        # India extract
        geofabrik_url = "https://download.geofabrik.de/asia/india-latest.osm.pbf"
        
        # Download to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".osm.pbf", delete=False) as temp:
            response = requests.get(geofabrik_url, stream=True)
            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=8192):
                    temp.write(chunk)
                temp_filename = temp.name
                
                print(f"Downloaded India OSM extract to {temp_filename}")
                
                # Process to extract Mumbai region
                # This would require osmium or other tools
                print("To extract Mumbai region from India extract:")
                print("1. Install osmium tool: https://osmcode.org/osmium-tool/")
                print("2. Run: osmium extract -b 72.75,18.85,73.05,19.28 india-latest.osm.pbf -o mumbai.osm.pbf")
                print("3. Convert to shapefiles using ogr2ogr")
                
                # Cleanup
                os.unlink(temp_filename)
            else:
                print(f"Failed to download from Geofabrik: {response.status_code}")
                os.unlink(temp_filename)
    
    except Exception as e:
        print(f"Error downloading from Geofabrik: {e}")
    
    # Final fallback: Provide instructions for manual download
    print("\nAutomated downloads failed. Please download Mumbai infrastructure data manually:")
    print("1. Visit https://www.openstreetmap.org/export")
    print("2. Navigate to Mumbai and use the 'Export' feature")
    print("3. Or use the HOT Export Tool: https://export.hotosm.org/")
    print("4. Place downloaded files in: data/raw/infrastructure/")
    
    return False

def download_mumbai_drainage_network():
    """
    Download additional drainage network data from government sources if available.
    """
    output_dir = Path("data/raw/infrastructure")
    
    # In a real implementation, you would check if official drainage data is available
    # For example, from Mumbai Municipal Corporation (BMC)
    
    # List of potential sources
    sources = [
        "https://portal.mcgm.gov.in/",  # Mumbai Municipal Corporation
        "https://mrsac.maharashtra.gov.in/",  # Maharashtra Remote Sensing Application Centre
        "https://www.maharashtra.gov.in/",  # Maharashtra Government
    ]
    
    print("Checking for official drainage network data...")
    print("Note: Official drainage data usually requires direct contact with agencies")
    print("Please check these sources for official data:")
    for source in sources:
        print(f"- {source}")
    
    # Check if OSM drainage data exists already
    drainage_file = output_dir / "mumbai_drainage.shp"
    if drainage_file.exists():
        print(f"Using OpenStreetMap drainage data from {drainage_file}")
        return True
    
    return False

def main():
    """Main function to prepare infrastructure data."""
    # Define the output path
    output_dir = Path("data/raw/infrastructure")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download primary infrastructure data
    success = download_osm_infrastructure(output_dir)
    
    # Download specific drainage network data
    download_mumbai_drainage_network()
    
    if success:
        print("Infrastructure data download complete.")
    else:
        print("Infrastructure data download encountered issues. Please check the logs.")

if __name__ == "__main__":
    main()