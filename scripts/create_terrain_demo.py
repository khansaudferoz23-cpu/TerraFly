from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin


def terrain_field(height: int, width: int) -> np.ndarray:
    y, x = np.meshgrid(
        np.linspace(-1.0, 1.0, height, dtype=np.float64),
        np.linspace(-1.0, 1.0, width, dtype=np.float64),
        indexing="ij",
    )
    ridge_a = 2900 * np.exp(-((x + 0.34 + 0.18 * y) ** 2 / 0.055 + (y + 0.08) ** 2 / 0.62))
    ridge_b = 2350 * np.exp(-((x - 0.28 + 0.12 * y) ** 2 / 0.075 + (y - 0.04) ** 2 / 0.75))
    peak_a = 1850 * np.exp(-((x + 0.18) ** 2 / 0.045 + (y + 0.28) ** 2 / 0.035))
    peak_b = 1600 * np.exp(-((x - 0.45) ** 2 / 0.035 + (y - 0.14) ** 2 / 0.055))
    foothills = 420 * (np.sin(10 * x + 2 * y) + 0.5 * np.sin(17 * y - 3 * x))
    valley = -850 * np.exp(-((x + 0.02) ** 2 / 0.035 + (y - 0.30) ** 2 / 0.7))
    fine = 95 * np.sin(38 * x + 7 * y) * np.sin(31 * y - 5 * x)
    return (1550 + ridge_a + ridge_b + peak_a + peak_b + foothills + valley + fine).astype(np.float32)


def optical_texture(elevation: np.ndarray) -> np.ndarray:
    dy, dx = np.gradient(elevation.astype(np.float64))
    slope = np.hypot(dx, dy)
    light = np.clip(0.72 - 0.010 * dx + 0.014 * dy, 0.38, 1.15)
    normalized = np.clip((elevation - 900) / 5200, 0, 1)
    green = np.array([47, 92, 55], dtype=np.float64)
    ochre = np.array([144, 105, 66], dtype=np.float64)
    rock = np.array([151, 145, 134], dtype=np.float64)
    snow = np.array([238, 242, 239], dtype=np.float64)
    colour = np.empty((*elevation.shape, 3), dtype=np.float64)
    lower = np.clip(normalized / 0.48, 0, 1)[..., None]
    colour[:] = green * (1 - lower) + ochre * lower
    upper_mask = normalized > 0.48
    upper = np.clip((normalized - 0.48) / 0.30, 0, 1)[..., None]
    colour[upper_mask] = (ochre * (1 - upper) + rock * upper)[upper_mask]
    snow_mask = normalized > 0.78
    snow_mix = np.clip((normalized - 0.78) / 0.16, 0, 1)[..., None]
    colour[snow_mask] = (rock * (1 - snow_mix) + snow * snow_mix)[snow_mask]
    exposed = np.clip(slope / max(float(np.percentile(slope, 99)), 1e-6), 0, 1)[..., None]
    colour = colour * (0.88 + 0.12 * exposed) * light[..., None]
    return np.clip(colour, 0, 255).astype(np.uint8)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    output_root = project_root / "sample_data"
    imagery_path = output_root / "terrafly_terrain_demo_imagery.tif"
    dem_path = output_root / "terrafly_terrain_demo_dem.tif"
    metadata_path = output_root / "terrafly_terrain_demo_metadata.json"

    image_height, image_width = 480, 640
    dem_height, dem_width = 240, 320
    image_elevation = terrain_field(image_height, image_width)
    imagery = optical_texture(image_elevation)
    dem = terrain_field(dem_height, dem_width)
    crs = "EPSG:32643"
    image_transform = from_origin(500_000, 3_400_000, 10, 10)
    dem_transform = from_origin(500_000, 3_400_000, 20, 20)

    with rasterio.open(
        imagery_path,
        "w",
        driver="GTiff",
        width=image_width,
        height=image_height,
        count=3,
        dtype="uint8",
        crs=crs,
        transform=image_transform,
        compress="deflate",
    ) as dataset:
        dataset.write(np.moveaxis(imagery, -1, 0))
        dataset.update_tags(role="synthetic optical texture for TerraFly terrain software demonstration")

    with rasterio.open(
        dem_path,
        "w",
        driver="GTiff",
        width=dem_width,
        height=dem_height,
        count=1,
        dtype="float32",
        crs=crs,
        transform=dem_transform,
        nodata=-9999.0,
        compress="deflate",
        predictor=3,
    ) as dataset:
        dataset.write(dem, 1)
        dataset.set_band_description(1, "synthetic terrain elevation")
        dataset.update_tags(units="metre", vertical_datum="TerraFly synthetic demo datum")

    metadata_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "scientific_role": "synthetic software demonstration only",
                "not_real_world_accuracy": True,
                "imagery": imagery_path.name,
                "dem": dem_path.name,
                "source_description": "TerraFly bundled synthetic mountain DEM",
                "vertical_datum": "TerraFly synthetic demo datum",
                "crs": crs,
                "imagery_resolution_m": 10,
                "dem_resolution_m": 20,
                "purpose": "Exercise DEM alignment, metric artifacts, texture mapping, and mountain-preserving rendering without external downloads.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
