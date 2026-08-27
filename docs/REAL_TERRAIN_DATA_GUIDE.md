# TerraFly real mountain data guide

Use this guide for the judge-facing real-world terrain scene. Do not use a Google Earth screenshot as reconstruction input: it is not a DEM, it loses source metadata, and Google's Geo Guidelines prohibit using captured Earth output to reconstruct 3D models.

## Recommended data pair

1. **Optical texture:** Copernicus Sentinel-2 Level-2A true-colour imagery. Bands B02, B03, and B04 are available at 10 m. Prefer a low-cloud scene and inspect the supplied cloud/shadow classification.
2. **Elevation geometry:** NASA SRTMGL1 v3, approximately 30 m, or another licensed DEM whose source, resolution, units, and vertical datum you can state precisely.

Official sources:

- Sentinel-2 L2A: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html
- Copernicus Browser: https://dataspace.copernicus.eu/browser/
- NASA SRTM product list: https://www.earthdata.nasa.gov/centers/lp-daac
- Google Geo Guidelines: https://about.google/brand-resource-center/products-and-services/geo-guidelines/

## Choose a scene that will look good

- Use a 10–20 km crop containing two or more distinct ridges and a valley.
- Avoid clouds and broad featureless snowfields where possible; the optical image is the texture even though the DEM controls shape.
- Do not choose a crop so small that a 30 m DEM has only a handful of samples.
- Keep the original acquisition/source details and required attribution with the demo.

## Prepare the files

Export the optical image as a georeferenced three-band GeoTIFF. Export the DEM as a georeferenced single-band GeoTIFF covering at least 90% of the same area. They may have different CRS, resolution, dimensions, or affine grids: TerraFly reprojects the DEM onto the optical grid with bilinear resampling and records both grids. This does **not** turn a 30 m DEM into 10 m evidence.

Before presenting, verify:

- The optical GeoTIFF has a CRS, transform, valid RGB pixels, and the intended crop.
- The DEM contains elevation—not a colourized screenshot or hillshade—and uses metre values.
- The named vertical datum is copied from the product documentation, not guessed.
- The optical/DEM areas overlap by at least 90%.
- Attribution and licensing text are kept with the project.

## Run it in TerraFly

1. Select **DEM Terrain**.
2. Choose the optical GeoTIFF and source DEM GeoTIFF.
3. Enter the exact product/source and vertical datum.
4. Select **Build measured terrain**.
5. Show Photo and Height colours, rotate the sun, click two points, and inspect the alignment report.
6. Download `metric_surface.tif`, `metric_surface.npy`, `terrain_surface.glb`, and `terrain_alignment_report.json`.

## What to claim

Say: “The DEM supplies measured terrain elevation; the optical image supplies texture. TerraFly validates and records alignment, preserves the source and metric outputs, and provides an interactive analysis layer.”

Do not say: “TerraFly independently measured the Himalayas,” “resampling improved the DEM resolution,” or “this is survey-grade.” Accuracy remains bounded by the supplied source DEM.
