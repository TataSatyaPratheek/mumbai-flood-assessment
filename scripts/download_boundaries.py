#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to download Mumbai administrative boundaries.
"""

import os
import sys
import requests
import zipfile
from pathlib import Path

# Add the project root directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data.acquisition import download_file

def main():
    """Main function to download Mumbai administrative boundaries."""
    # Create output directory
    output_dir = Path("data/raw/boundaries")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Download from GADM (Global Administrative Areas)
    print("Downloading Mumbai administrative boundaries...")
    
    # GADM India Level 2 (Districts)
    gadm_url = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_IND_shp.zip"
    zip_path = output_dir / "gadm41_IND_shp.zip"
    
    if download_file(gadm_url, zip_path):
        print(f"Successfully downloaded to {zip_path}")
        
        # Extract the zip file
        print("Extracting files...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        print("Downloaded and extracted GADM data for India.")
        print("You will need to filter for Mumbai (Maharashtra) districts.")
    else:
        print("Failed to download GADM data.")

if __name__ == "__main__":
    main()
