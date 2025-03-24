# Mumbai Urban Flood Vulnerability Assessment System

## Project Overview

This project aims to create a comprehensive flood vulnerability assessment system for Mumbai, India. The system integrates physical, socioeconomic, and infrastructure data to identify areas at risk of flooding under various rainfall scenarios.

## Setup

### Prerequisites

- QGIS
- Python 3.9+
- Conda

### Installation

#### Clone repository
```
git clone https://github.com/yourusername/mumbai-flood-assessment.git

cd mumbai-flood-assessment
```

#### Create conda environment
```
conda env create -f environment.yml
```

#### Activate environment
```
conda activate flood-assessment
```

## Data Sources

Elevation: SRTM 30m DEM, Cartosat-1
Administrative Boundaries: Mumbai Municipal Corporation
Rainfall: India Meteorological Department
Census: Census of India
Infrastructure: OpenStreetMap, Mumbai Development Plan

## Project Structure
```
mumbai-flood-assessment/
├── data/                      # Data directory
│   ├── raw/                   # Raw, immutable data
│   ├── processed/             # Processed data
│   └── external/              # External data sources
├── notebooks/                 # Jupyter notebooks
├── src/                       # Source code
│   ├── data/                  # Data processing scripts
│   ├── models/                # Analysis models
│   ├── visualization/         # Visualization code
│   └── api/                   # API for dashboard
├── dashboard/                 # Web dashboard
└── docs/                      # Documentation
```

## Usage

Data Preprocessing: python src/data/preprocessing.py
Vulnerability Analysis: python src/models/vulnerability.py
Run Dashboard: python src/api/app.py

## License
MIT License
