import os
import rasterio
import geopandas as gpd
import numpy as np
import pandas as pd
from rasterio.mask import mask


def process_satellite_images(base_dir, top_shp_path, bottom_shp_path, output_base_dir):
    """
    Process all TIF files in yearly folders and create organized CSV outputs
    """
    # Create output directories
    ndvi_dir = os.path.join(output_base_dir, 'NDVI')
    gci_dir = os.path.join(output_base_dir, 'GCI')
    os.makedirs(ndvi_dir, exist_ok=True)
    os.makedirs(gci_dir, exist_ok=True)

    # Process each year directory
    for year_folder in sorted(os.listdir(base_dir)):
        year_path = os.path.join(base_dir, year_folder)

        # Skip if not a directory or not a year folder
        if not os.path.isdir(year_path) or not year_folder.isdigit():
            continue

        print(f"\nProcessing year: {year_folder}")

        try:
            # Select appropriate shapefile based on year
            year = int(year_folder)
            shapefile_path = bottom_shp_path if year % 2 == 0 else top_shp_path
            print(f"Using {'bottom' if year % 2 == 0 else 'top'} shapefile")

            shapefile = gpd.read_file(shapefile_path)

            # Initialize DataFrames for the year
            ndvi_df = pd.DataFrame({'FID': shapefile['FID']})
            gci_df = pd.DataFrame({'FID': shapefile['FID']})

            # Get all TIF files in the year folder
            tif_files = sorted([f for f in os.listdir(year_path) if f.endswith('.tif')])
            print(f"Found {len(tif_files)} TIF files")

            for tif_file in tif_files:
                try:
                    print(f"Processing: {tif_file}")
                    tif_path = os.path.join(year_path, tif_file)

                    # Calculate indices
                    ndvi_values, gci_values = calculate_indices(tif_path, shapefile)

                    # Use the file name (without extension) as column name
                    column_name = os.path.splitext(tif_file)[0]

                    # Add to DataFrames
                    ndvi_df[column_name] = pd.Series(ndvi_values)
                    gci_df[column_name] = pd.Series(gci_values)

                except Exception as e:
                    print(f"Error processing {tif_file}: {str(e)}")
                    continue

            # Save yearly results
            ndvi_output = os.path.join(ndvi_dir, f'NDVI_{year}.csv')
            gci_output = os.path.join(gci_dir, f'GCI_{year}.csv')

            ndvi_df.to_csv(ndvi_output, index=False)
            gci_df.to_csv(gci_output, index=False)

            print(f"Saved NDVI data to: {ndvi_output}")
            print(f"Saved GCI data to: {gci_output}")

        except Exception as e:
            print(f"Error processing year {year_folder}: {str(e)}")
            continue


def calculate_indices(raster_path, shapefile):
    """
    Calculate NDVI and GCI for the masked image
    """
    with rasterio.open(raster_path) as src:
        # Read bands (BGRNIR order)
        blue = src.read(1)
        green = src.read(2)
        red = src.read(3)
        nir = src.read(4)

        ndvi_values = {}
        gci_values = {}

        for idx, row in shapefile.iterrows():
            try:
                geometry = [row['geometry']]

                # Mask the image for current geometry
                masked_nir, _ = mask(src, geometry, crop=True, indexes=4)
                masked_red, _ = mask(src, geometry, crop=True, indexes=3)
                masked_green, _ = mask(src, geometry, crop=True, indexes=2)

                # Convert to float32
                masked_nir = masked_nir.astype(np.float32)
                masked_red = masked_red.astype(np.float32)
                masked_green = masked_green.astype(np.float32)

                # Create valid pixel masks
                valid_pixels = (masked_nir > 0) & (masked_red > 0) & (masked_green > 0)

                if np.any(valid_pixels):
                    # Calculate NDVI
                    ndvi = np.where(valid_pixels,
                                    (masked_nir - masked_red) / (masked_nir + masked_red),
                                    np.nan)

                    # Calculate GCI
                    gci = np.where(valid_pixels,
                                   (masked_nir / masked_green) - 1,
                                   np.nan)

                    # Store means
                    ndvi_values[row['FID']] = np.nanmean(ndvi)
                    gci_values[row['FID']] = np.nanmean(gci)
                else:
                    ndvi_values[row['FID']] = np.nan
                    gci_values[row['FID']] = np.nan

            except Exception as e:
                print(f"Error processing FID {row['FID']}: {e}")
                ndvi_values[row['FID']] = np.nan
                gci_values[row['FID']] = np.nan

    return ndvi_values, gci_values



if __name__ == "__main__":
    base_dir = "/Users/phani/Desktop/Crop_yield_data copy/Extra_data/imagesSR"
    top_shp_path = "/Users/phani/Desktop/Crop_yield_data copy/9x9 Grids/Top Field/2022_cc_driscoll_grid_9m_sorghum.shp"
    bottom_shp_path = "/Users/phani/Desktop/Crop_yield_data copy/9x9 Grids/Bottom Field /2022_cc_driscoll_grid_9m_cotton.shp"
    output_base_dir = "/Users/phani/Desktop/Crop_yield_data copy/Indices"

    process_satellite_images(base_dir, top_shp_path, bottom_shp_path, output_base_dir)