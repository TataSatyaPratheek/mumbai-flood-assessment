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
