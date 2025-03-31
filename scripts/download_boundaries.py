#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
<<<<<<< HEAD
Script to extract Mumbai administrative boundaries and integrate census data.
=======
Script to extract Mumbai administrative boundaries from GADM data.
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
"""

import os
import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
<<<<<<< HEAD
import numpy as np

def extract_mumbai_boundaries():
    """Extract Mumbai boundaries from GADM data and integrate census data."""
=======

def extract_mumbai_boundaries():
    """Extract Mumbai boundaries from GADM data at different levels."""
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
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
    
<<<<<<< HEAD
    # Load census data to identify required wards
    census_file = Path("mumbai-census.csv")
    if census_file.exists():
        print("Loading census data...")
        census = pd.read_csv(census_file)
        
        # Get unique ward names
        census_wards = census['Ward Name'].unique()
        print(f"Census data contains {len(census_wards)} wards: {census_wards}")
    else:
        print("Census data file not found. Creating boundaries without census integration.")
        census = None
    
    # Load GADM Level 2 data (districts)
    print("Loading GADM district data...")
    districts = gpd.read_file(gadm_level2)
    
    # Check Maharashtra districts
    print("Available districts in Maharashtra:")
    maharashtra_districts = districts[districts['NAME_1'] == 'Maharashtra']
    print(maharashtra_districts['NAME_2'].unique())
    
    # Filter for Mumbai districts - both Mumbai and Mumbai Suburban
    mumbai_criteria = maharashtra_districts['NAME_2'].str.contains('Mumbai', case=False, na=False)
    mumbai_districts = maharashtra_districts[mumbai_criteria]
    
    if len(mumbai_districts) == 0:
        print("No Mumbai districts found with standard naming.")
        print("Checking alternative spellings or names...")
        
        # Try with Bombay spelling
        bombay_criteria = maharashtra_districts['NAME_2'].str.contains('Bombay', case=False, na=False)
=======
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
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
        mumbai_districts = maharashtra_districts[bombay_criteria]
        
        if len(mumbai_districts) == 0:
            print("Still no Mumbai districts found. Showing all Maharashtra districts:")
            print(maharashtra_districts[['NAME_2', 'VARNAME_2']])
            print("Please modify the script to select the correct district names.")
            return False
    
<<<<<<< HEAD
    print(f"Found {len(mumbai_districts)} Mumbai-related districts:")
    print(mumbai_districts['NAME_2'].tolist())
    
    # Save Mumbai boundary
    mumbai_districts.to_file(mumbai_boundary_file)
    print(f"Mumbai boundaries saved to {mumbai_boundary_file}")
    
    # Load GADM Level 3 data (sub-districts) if available - for more detailed boundaries
    gadm_level3 = boundary_dir / "gadm41_IND_3.shp"
    
    if gadm_level3.exists():
        print("Loading GADM level 3 (sub-district) data...")
=======
    print(f"Found {len(mumbai_districts)} Mumbai-related districts")
    print("Districts: ", mumbai_districts['NAME_2'].tolist())
    
    # Save Mumbai boundaries
    mumbai_districts.to_file(mumbai_boundary_file)
    print(f"Mumbai boundaries saved to {mumbai_boundary_file}")
    
    # Load GADM Level 3 data (sub-districts) if available
    gadm_level3 = boundary_dir / "gadm41_IND_3.shp"
    if gadm_level3.exists():
        print("Loading GADM sub-district data...")
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
        subdistricts = gpd.read_file(gadm_level3)
        
        # Filter for Mumbai sub-districts
        mumbai_subdistricts = subdistricts[subdistricts['NAME_2'].isin(mumbai_districts['NAME_2'])]
        
<<<<<<< HEAD
        print(f"Found {len(mumbai_subdistricts)} sub-districts within Mumbai districts:")
        if len(mumbai_subdistricts) > 0:
            print("Sub-districts: ", mumbai_subdistricts['NAME_3'].tolist())
            
            # Check if the number of sub-districts matches the 24 wards from census
            if census is not None and len(mumbai_subdistricts) != len(census_wards):
                print(f"Warning: Number of sub-districts ({len(mumbai_subdistricts)}) doesn't match number of census wards ({len(census_wards)})")
            
            # Prepare to save these as wards
            wards = mumbai_subdistricts.copy()
            
            # Add ward_id field matching with census if possible
            if census is not None:
                # Create a mapping from subdistrict names to census ward codes if possible
                # This is a simplified approach and might need manual adjustment
                ward_mapping = {}
                
                # First, try to match by name similarity
                for _, ward in wards.iterrows():
                    ward_name = ward['NAME_3']
                    best_match = None
                    best_score = 0
                    
                    for census_ward in census_wards:
                        # Calculate similarity (very simple approach)
                        if ward_name in census_ward or census_ward in ward_name:
                            score = len(set(ward_name.lower()) & set(census_ward.lower())) / len(set(ward_name.lower()) | set(census_ward.lower()))
                            if score > best_score:
                                best_score = score
                                best_match = census_ward
                    
                    ward_mapping[ward_name] = best_match if best_score > 0.3 else None
                
                # Apply the mapping where possible, otherwise use sequential IDs
                wards['ward_id'] = wards['NAME_3'].map(ward_mapping)
                wards.loc[wards['ward_id'].isna(), 'ward_id'] = [f"W{i+1:02d}" for i in range(sum(wards['ward_id'].isna()))]
            else:
                # Use sequential IDs if no census data
                wards['ward_id'] = [f"W{i+1:02d}" for i in range(len(wards))]
            
            # Save the ward boundaries
            wards.to_file(mumbai_wards_file)
            print(f"Mumbai wards saved to {mumbai_wards_file}")
        else:
            print("No sub-districts found within Mumbai. Will need to create custom ward boundaries.")
    else:
        print("GADM level 3 file not found. Checking for level 4 data or will create approximate ward boundaries.")
        
        # Check for GADM level 4 data
        gadm_level4 = boundary_dir / "gadm41_IND_4.shp"
        if gadm_level4.exists():
            print("Loading GADM level 4 data (more detailed boundaries)...")
            detailed = gpd.read_file(gadm_level4)
            
            # Filter for Mumbai areas
            mumbai_detailed = detailed[detailed['NAME_2'].isin(mumbai_districts['NAME_2'])]
            
            if len(mumbai_detailed) > 0:
                print(f"Found {len(mumbai_detailed)} detailed areas within Mumbai.")
                
                # Check if this matches better with census wards
                if census is not None and abs(len(mumbai_detailed) - len(census_wards)) < abs(len(mumbai_districts) - len(census_wards)):
                    print(f"Level 4 boundaries provide a better match to census wards ({len(mumbai_detailed)} vs {len(census_wards)}).")
                    wards = mumbai_detailed.copy()
                    
                    # Add ward_id field
                    wards['ward_id'] = [f"W{i+1:02d}" for i in range(len(wards))]
                    
                    # Save the ward boundaries
                    wards.to_file(mumbai_wards_file)
                    print(f"Mumbai wards (from level 4) saved to {mumbai_wards_file}")
                else:
                    print("Level 4 data doesn't provide a better match to census wards. Creating custom boundaries...")
            else:
                print("No detailed areas found within Mumbai. Creating custom ward boundaries.")
    
    # If no ward file yet, create custom ward boundaries if we have census data
    if not mumbai_wards_file.exists() and census is not None:
        print("Creating approximate ward boundaries based on Mumbai districts and census data...")
        
        # This is an approximation - ideally, you'd have actual ward boundaries
        # We'll divide the Mumbai districts into rough equal sections based on ward counts
        
        # Simplified approach: divide each district into equal parts
        wards_list = []
        
        for idx, district in mumbai_districts.iterrows():
            district_name = district['NAME_2']
            district_geom = district.geometry
            
            # Count wards in this district based on ward name prefix
            # This assumes ward names in census follow district-based naming
            if district_name == "Mumbai":
                # Assuming wards A-G are in Mumbai district
                district_ward_count = sum(1 for w in census_wards if w[0] in "ABCDEFG")
            else:  # Mumbai Suburban
                # Assuming wards H-T are in Mumbai Suburban district
                district_ward_count = sum(1 for w in census_wards if w[0] in "HIJKLMNOPQRST")
            
            # If no matches, use a default count
            if district_ward_count == 0:
                district_ward_count = max(1, len(census_wards) // len(mumbai_districts))
            
            print(f"Creating {district_ward_count} wards for {district_name} district")
            
            # Very simple division - this doesn't create proper ward boundaries
            # In a real project, you'd need actual ward boundary files
            
            # Create a square grid over the district
            bounds = district_geom.bounds  # (minx, miny, maxx, maxy)
            
            # Calculate grid dimensions
            grid_dim = max(1, int(np.sqrt(district_ward_count)))
            
            x_step = (bounds[2] - bounds[0]) / grid_dim
            y_step = (bounds[3] - bounds[1]) / grid_dim
            
            ward_idx = 0
            for i in range(grid_dim):
                for j in range(grid_dim):
                    if ward_idx < district_ward_count:
                        # Calculate grid cell bounds
                        minx = bounds[0] + i * x_step
                        miny = bounds[1] + j * y_step
                        maxx = bounds[0] + (i + 1) * x_step
                        maxy = bounds[1] + (j + 1) * y_step
                        
                        # Create a rectangle
                        rect = gpd.GeoDataFrame(
                            {'ward_id': [f"W{len(wards_list)+1:02d}"], 
                             'district': [district_name],
                             'geometry': [gpd.GeoSeries.from_shapely([gpd.box(minx, miny, maxx, maxy)])[0]]
                            }, 
                            crs=mumbai_districts.crs
                        )
                        
                        # Clip to district boundary
                        ward_geom = gpd.overlay(rect, gpd.GeoDataFrame({'geometry': [district_geom]}, crs=mumbai_districts.crs), how='intersection')
                        
                        if not ward_geom.empty:
                            ward_geom['ward_id'] = f"W{len(wards_list)+1:02d}"
                            ward_geom['district'] = district_name
                            
                            # Try to match with census ward
                            if len(census_wards) > len(wards_list):
                                ward_geom['ward_name'] = census_wards[len(wards_list)]
                            
                            wards_list.append(ward_geom)
                            ward_idx += 1
        
        # Combine all wards
        if wards_list:
            wards = pd.concat(wards_list, ignore_index=True)
            
            # Save ward boundaries
            wards.to_file(mumbai_wards_file)
            print(f"Created approximate ward boundaries and saved to {mumbai_wards_file}")
        else:
            print("Failed to create ward boundaries. Please provide actual ward boundary files.")
    
    # Create a visualization of the boundaries
    create_boundary_visualization(mumbai_boundary_file, mumbai_wards_file, census)
    
    print("Completed boundary extraction and preparation.")
    return True

def create_boundary_visualization(boundary_file, wards_file, census=None):
    """Create visualizations of Mumbai boundaries with census data integration."""
=======
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
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
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
<<<<<<< HEAD
        
        # Add district labels
        for idx, row in boundary.iterrows():
            centroid = row.geometry.centroid
            plt.text(centroid.x, centroid.y, row['NAME_2'], fontsize=12, ha='center')
        
        plt.title("Mumbai Administrative Boundary")
        plt.savefig(output_dir / "mumbai_boundary.png", dpi=300, bbox_inches='tight')
        plt.close()
=======
        plt.title("Mumbai Administrative Boundary")
        plt.savefig(output_dir / "mumbai_boundary.png", dpi=300, bbox_inches='tight')
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
        
        # Plot wards if available
        if wards_file.exists():
            wards = gpd.read_file(wards_file)
            
            # Plot wards
<<<<<<< HEAD
            fig, ax = plt.subplots(figsize=(15, 12))
            boundary.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.5)
            wards.plot(ax=ax, column='ward_id', cmap='tab20', edgecolor='black', alpha=0.7)
            
            # Add ward labels
            for idx, row in wards.iterrows():
                centroid = row.geometry.centroid
                plt.text(centroid.x, centroid.y, row['ward_id'], fontsize=9, ha='center')
            
            plt.title("Mumbai Administrative Wards")
            plt.savefig(output_dir / "mumbai_wards.png", dpi=300, bbox_inches='tight')
            plt.close()
=======
            fig, ax = plt.subplots(figsize=(12, 10))
            boundary.plot(ax=ax, color='lightgrey', edgecolor='black')
            wards.plot(ax=ax, column='ward_id', cmap='tab20', edgecolor='black', alpha=0.7)
            plt.title("Mumbai Administrative Wards")
            plt.savefig(output_dir / "mumbai_wards.png", dpi=300, bbox_inches='tight')
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
            
            # Create ward statistics
            ward_stats = pd.DataFrame({
                'ward_id': wards['ward_id'],
<<<<<<< HEAD
                'district': wards['NAME_2'] if 'NAME_2' in wards.columns else (
                           wards['district'] if 'district' in wards.columns else "Unknown"),
                'area_sqkm': wards.to_crs(epsg=32643).area / 1_000_000  # Convert to sq km
            })
            
            # If we have census data, attempt to integrate it
            if census is not None:
                print("Integrating census data with ward boundaries...")
                
                # Prepare census summary by ward
                census_summary = census.groupby('Ward Name').agg({
                    'Total Population': 'sum',
                    'Total Males': 'sum',
                    'Total Females': 'sum',
                    'SC Population': 'sum',
                    'ST Population': 'sum'
                }).reset_index()
                
                # Try to match census wards to our ward boundaries
                ward_census_data = []
                
                for _, ward in wards.iterrows():
                    ward_id = ward['ward_id']
                    ward_name = ward.get('ward_name', '')
                    
                    # Try to find matching census ward
                    matching_census = None
                    
                    if ward_name and not ward_name.isna():
                        # Direct match by name
                        matching_census = census_summary[census_summary['Ward Name'] == ward_name]
                    
                    if matching_census is None or len(matching_census) == 0:
                        # If no direct match, use ward ID to try to match
                        ward_num = int(ward_id[1:]) if ward_id.startswith('W') and ward_id[1:].isdigit() else -1
                        
                        if 0 < ward_num <= len(census_summary):
                            # Just use position as fallback
                            matching_census = census_summary.iloc[ward_num-1:ward_num]
                    
                    if matching_census is not None and len(matching_census) > 0:
                        # Add census data for this ward
                        census_data = matching_census.iloc[0].to_dict()
                        ward_census_data.append({
                            'ward_id': ward_id,
                            'ward_name': census_data['Ward Name'],
                            'population': census_data['Total Population'],
                            'male_population': census_data['Total Males'],
                            'female_population': census_data['Total Females'],
                            'sc_population': census_data['SC Population'],
                            'st_population': census_data['ST Population']
                        })
                    else:
                        # No matching census data
                        ward_census_data.append({
                            'ward_id': ward_id,
                            'ward_name': 'Unknown',
                            'population': 0,
                            'male_population': 0,
                            'female_population': 0,
                            'sc_population': 0,
                            'st_population': 0
                        })
                
                # Create a DataFrame and merge with ward_stats
                ward_census_df = pd.DataFrame(ward_census_data)
                ward_stats = ward_stats.merge(ward_census_df, on='ward_id', how='left')
                
                # Calculate population density
                ward_stats['population_density'] = ward_stats['population'] / ward_stats['area_sqkm']
                
                # Create a choropleth map of population density
                fig, ax = plt.subplots(figsize=(15, 12))
                boundary.plot(ax=ax, color='lightgrey', edgecolor='black', alpha=0.5)
                
                # Join with spatial data
                ward_density_map = wards.merge(ward_stats[['ward_id', 'population_density']], on='ward_id', how='left')
                
                # Plot choropleth
                ward_density_map.plot(column='population_density', cmap='YlOrRd', 
                                      edgecolor='black', alpha=0.7, ax=ax,
                                      legend=True, legend_kwds={'label': "Population Density (per sq km)"})
                
                # Add ward labels
                for idx, row in ward_density_map.iterrows():
                    centroid = row.geometry.centroid
                    plt.text(centroid.x, centroid.y, row['ward_id'], fontsize=9, ha='center')
                
                plt.title("Mumbai Ward Population Density")
                plt.savefig(output_dir / "mumbai_population_density.png", dpi=300, bbox_inches='tight')
                plt.close()
                
                # Create a bar chart of ward populations
                plt.figure(figsize=(15, 8))
                sorted_stats = ward_stats.sort_values('population', ascending=False)
                plt.bar(sorted_stats['ward_id'], sorted_stats['population'], color='skyblue')
                plt.xticks(rotation=90)
                plt.title("Population by Ward")
                plt.xlabel("Ward ID")
                plt.ylabel("Population")
                plt.grid(axis='y', alpha=0.3)
                plt.tight_layout()
                plt.savefig(output_dir / "ward_population_chart.png", dpi=300)
                plt.close()
            
            # Save the ward statistics
            stats_file = output_dir / "mumbai_ward_statistics.csv"
            ward_stats.to_csv(stats_file, index=False)
            print(f"Ward statistics saved to {stats_file}")
=======
                'name': wards['NAME_3'] if 'NAME_3' in wards.columns else wards['ward_id'],
                'area_sqkm': wards.to_crs(epsg=32643).area / 1_000_000  # Convert to sq km
            })
            
            # Save stats
            ward_stats.to_csv(output_dir / "mumbai_ward_stats.csv", index=False)
            print(f"Ward statistics saved to {output_dir / 'mumbai_ward_stats.csv'}")
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
        
        print(f"Visualizations saved to {output_dir}")
        
    except Exception as e:
<<<<<<< HEAD
        print(f"Error creating visualizations: {e}")
        import traceback
        traceback.print_exc()
=======
        print(f"Error creating visualization: {e}")
>>>>>>> ea4a7f5ba1542b222f3729eb06ca54c4eb22c654
        return False

if __name__ == "__main__":
    extract_mumbai_boundaries()