import os
import glob
import rasterio
import numpy as np
from rasterio.mask import mask
from shapely.geometry import box
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
import warnings

# Suppress specific matplotlib warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Define the bounding box for Mumbai (approximate coordinates)
min_lon, min_lat = 72.67494596150834, 18.822731593095607
max_lon, max_lat = 73.09788598906245, 19.4042741309825

# Create a GeoDataFrame with the bounding box
bbox = box(min_lon, min_lat, max_lon, max_lat)
geo = gpd.GeoDataFrame({"geometry": [bbox]}, crs="EPSG:4326")

# Define input and output directories
input_dirs = {
    "rainfall": Path("data/raw/rainfall"),
    "census": Path("data/raw/census")
}
output_dirs = {
    "rainfall": Path("data/processed/rainfall"),
    "census": Path("data/processed/census")
}

# Ensure the output directories exist
for output_dir in output_dirs.values():
    output_dir.mkdir(parents=True, exist_ok=True)

# Process each directory
for dir_name, input_dir in input_dirs.items():
    output_dir = output_dirs[dir_name]

    # Find all .tif files in the input directory and subdirectories
    tif_files = glob.glob(str(input_dir / "**/*.tif"), recursive=True)
    print(f"Found {len(tif_files)} TIFF files to process in {dir_name}")

    # Process each .tif file
    for tif_path in tif_files:
        try:
            # Determine the relative path to preserve directory structure
            relative_path = Path(tif_path).relative_to(input_dir)
            output_path = output_dir / relative_path
            print(f"Processing: {relative_path}")

            # Ensure the output directory for the file exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Load the GeoTIFF file
            with rasterio.open(tif_path) as src:
                # Reproject the bounding box to match the CRS of the raster
                geo_reprojected = geo.to_crs(src.crs)

                try:
                    # Clip the raster using the bounding box
                    out_image, out_transform = mask(src, geo_reprojected.geometry, crop=True)
                    out_meta = src.meta

                    # Handle nodata values to prevent math domain errors
                    if src.nodata is not None:
                        out_image = np.where(out_image == src.nodata, np.nan, out_image)

                    # Remove infinite values if any
                    out_image = np.where(np.isinf(out_image), np.nan, out_image)

                    # Update metadata for the clipped raster
                    out_meta.update({
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform
                    })

                    # Save the clipped raster
                    with rasterio.open(output_path, "w", **out_meta) as dest:
                        # Replace NaN values with nodata value before saving
                        if src.nodata is not None:
                            out_image = np.where(np.isnan(out_image), src.nodata, out_image)
                        dest.write(out_image)

                    # Plot the clipped region with error handling
                    try:
                        # Use masked arrays to handle NaN values
                        masked_data = np.ma.masked_invalid(out_image[0])

                        # Only create plot if we have valid data
                        if not np.all(np.ma.getmask(masked_data)):
                            plt.figure(figsize=(8, 6))

                            # Determine appropriate colormap based on filename
                            if "prec" in str(relative_path).lower():
                                cmap = "Blues"
                                label = "Precipitation (mm)"
                            elif "elev" in str(relative_path).lower():
                                cmap = "terrain"
                                label = "Elevation (m)"
                            else:
                                cmap = "viridis"
                                label = "Value"

                            # Use robust plotting with vmin/vmax to avoid extreme values
                            valid_data = masked_data.compressed()
                            if len(valid_data) > 0:
                                # Calculate 2nd and 98th percentiles for robust plotting
                                vmin = np.percentile(valid_data, 2)
                                vmax = np.percentile(valid_data, 98)

                                im = plt.imshow(masked_data, cmap=cmap, vmin=vmin, vmax=vmax)
                                plt.colorbar(im, label=label)
                                plt.title(f"Mumbai Region: {relative_path.name}")
                                plt.axis('off')

                                # Save the plot instead of displaying it
                                plot_path = output_dir / f"{relative_path.stem}_plot.png"
                                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                                plt.close()
                                print(f"  Plot saved to {plot_path}")
                            else:
                                print(f"  No valid data in {relative_path.name} to plot")
                        else:
                            print(f"  All data masked in {relative_path.name} - skipping plot")

                    except Exception as plot_error:
                        print(f"  Warning: Could not create plot for {relative_path.name}: {plot_error}")
                        plt.close()

                    print(f"  Processed and saved: {output_path}")

                except ValueError as e:
                    if "Input shapes do not overlap raster" in str(e):
                        print(f"  Warning: Mumbai region does not overlap with {relative_path.name}")
                    else:
                        print(f"  Error processing {relative_path.name}: {e}")

        except Exception as e:
            print(f"  Error with file {tif_path}: {e}")

print("\nProcessing complete. Cropped files saved in:", output_dirs)