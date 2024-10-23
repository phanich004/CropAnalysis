# CropAnalysis

This project demonstrates the analysis of agricultural data using satellite imagery and shapefiles, calculating vegetation indices (NDVI and GCI) for crop monitoring.
This is just an initial phase of ML analytics of our web application.

## Prerequisites

Required Python packages:
```
rasterio
fiona
geopandas
matplotlib
numpy
pandas
```

Install dependencies using:
```bash
pip install rasterio fiona geopandas matplotlib numpy pandas
```

## Data Requirements

The project expects the following input files:
- `2022_cc_driscoll_grid_9m_sorghum.shp` - Shapefile containing field boundaries
- `20190309.tif` - Multi-band satellite imagery (containing NIR, Red, and Green bands)

## Features

- Shapefile and raster data visualization
- Masking satellite imagery using field boundaries
- Calculation of vegetation indices:
  - Normalized Difference Vegetation Index (NDVI)
  - Green Chlorophyll Index (GCI)
- Statistical analysis of vegetation indices
- Heatmap generation for spatial visualization

## Usage

1. **Load and Visualize Data**
   - Display shapefile boundaries
   - Visualize satellite imagery
   - Overlay boundaries on satellite imagery

2. **Mask and Process Imagery**
   - Create masked version of satellite imagery using field boundaries
   - Rasterize field boundaries for analysis

3. **Calculate Vegetation Indices**
   - NDVI calculation using NIR (band 4) and Red (band 3) bands
   - GCI calculation using NIR (band 4) and Green (band 2) bands

4. **Analysis and Visualization**
   - Generate pixel-level statistics for each field
   - Create distribution plots of NDVI and GCI values
   - Produce heatmaps showing spatial distribution of indices

## Code Structure

The script performs the following operations:

1. Data Loading
```python
data = gpd.read_file('2022_cc_driscoll_grid_9m_sorghum.shp')
```

2. Image Masking
```python
with rasterio.open("20190309.tif") as src:
    out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True)
```

3. Index Calculation
```python
ndvi = np.where(
    (nir_band + red_band) != 0,
    (nir_band - red_band) / (nir_band + red_band),
    np.nan
)

gci = np.where(
    green_band != 0,
    (nir_band / green_band) - 1,
    np.nan
)
```

4. Statistical Analysis and Visualization
```python
# Calculate average indices per field
average_ndvi = {index: np.nanmean(values) if values else np.nan 
                for index, values in ndvi_values.items()}
average_gci = {index: np.nanmean(values) if values else np.nan 
               for index, values in gci_values.items()}
```

## Output

The script generates several visualizations:
- Field boundary overlays
- Masked satellite imagery
- NDVI and GCI distribution plots
- Spatial heatmaps of vegetation indices

## Notes

- Ensure all input files are in the same coordinate reference system (CRS)
- Band ordering in the satellite imagery should be verified before processing
- Memory usage may be significant for large datasets

## Error Handling

The code includes error handling for:
- Zero division in index calculations
- Missing or invalid pixel values
- Geometry masking operations

