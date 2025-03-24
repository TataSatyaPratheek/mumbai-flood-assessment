#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Main script to run all data preparation steps for the Mumbai flood vulnerability project.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_script(script_path):
    """Run a Python script and return success/failure."""
    print(f"\n{'='*80}\nRunning {script_path}\n{'='*80}")
    result = subprocess.run([sys.executable, script_path])
    return result.returncode == 0

def main():
    """Main function to run all data preparation scripts."""
    scripts_dir = Path("scripts")
    
    # Define the order of scripts to run
    scripts = [
        "download_boundaries.py",
        "download_elevation.py",
        "prepare_census_data.py",
        "prepare_rainfall_data.py",
        "prepare_infrastructure_data.py"
    ]
    
    # Run each script
    for script in scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            success = run_script(script_path)
            if not success:
                print(f"Error running {script}. Stopping.")
                return False
        else:
            print(f"Script {script} not found. Skipping.")
    
    print("\nAll data preparation steps completed successfully!")
    return True

if __name__ == "__main__":
    main()
