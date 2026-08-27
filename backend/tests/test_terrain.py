from __future__ import annotations

import io
import json
import struct

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin


def _geotiff_bytes(
    values: np.ndarray,
    *,
    transform,
    crs: str = "EPSG:32643",
    nodata: float | None = None,
    unit: str | None = None,
) -> bytes:
    bands = values if values.ndim == 3 else values[None, ...]
    profile = {
        "driver": "GTiff",
        "height": bands.shape[1],
        "width": bands.shape[2],
        "count": bands.shape[0],
        "dtype": str(bands.dtype),
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
    }
    with MemoryFile() as memory_file:
        with memory_file.open(**profile) as dataset:
            dataset.write(bands)
            if unit:
                dataset.set_band_unit(1, unit)
        return memory_file.read()


def _terrain_pair(*, overlap: bool = True) -> tuple[bytes, bytes]:
    image_height, image_width = 48, 64
    rows, columns = np.indices((image_height, image_width))
    imagery = np.stack(
        (
            np.clip(70 + columns * 2 + rows, 0, 255),
            np.clip(45 + rows * 3, 0, 255),
            np.clip(35 + columns + rows * 2, 0, 255),
        ),
        axis=0,
    ).astype(np.uint8)
    image_transform = from_origin(500_000, 3_000_000, 10, 10)

    dem_height, dem_width = 24, 32
    y, x = np.indices((dem_height, dem_width), dtype=np.float32)
    ridge = 1300 + 900 * np.exp(-((x - 14) ** 2 / 70 + (y - 10) ** 2 / 35))
    ridge += 450 * np.exp(-((x - 24) ** 2 / 18 + (y - 15) ** 2 / 55))
    dem = ridge.astype(np.float32)
    dem_transform = from_origin(500_000 if overlap else 700_000, 3_000_000, 20, 20)
    return (
        _geotiff_bytes(imagery, transform=image_transform),
        _geotiff_bytes(dem, transform=dem_transform),
    )


def test_source_dem_workflow_creates_metric_textured_terrain(client):
    imagery, dem = _terrain_pair()
    response = client.post(
        "/api/terrain-jobs",
        files={
            "imagery": ("mountain-rgb.tif", imagery, "image/tiff"),
            "dem": ("mountain-dem.tif", dem, "image/tiff"),
        },
        data={
            "source_description": "Synthetic mountain DEM software fixture",
            "vertical_datum": "Fixture orthometric datum",
        },
    )
    assert response.status_code == 202
    job = client.get(f"/api/jobs/{response.json()['job_id']}").json()
    assert job["status"] == "complete"
    assert job["scientific_state"] == "Metric Source DEM"
    assert job["units"] == "metre"
    assert job["calibration"]["status"] == "source_dem"
    assert job["calibration"]["metric_output_allowed"] is True
    assert job["model"]["adapter"] == "source_dem"
    assert job["configuration"]["inference_mode"] == "not_used"
    assert job["calibration"]["evidence"]["vertical_units"] == "metre"
    assert not any("does not establish vertical scale" in warning for warning in job["warnings"])

    names = {artifact["name"] for artifact in job["artifacts"]}
    assert {
        "source_dem",
        "source_dem_aligned",
        "numeric_surface",
        "metric_surface",
        "metric_grid",
        "metric_geotiff",
        "terrain_alignment_report",
        "glb_mesh",
        "manifest",
    } <= names
    assert "raw_model_output" not in names
    assert "structure_layer" not in names

    metric_response = client.get(f"/api/jobs/{job['job_id']}/artifacts/metric_surface")
    metric = np.load(io.BytesIO(metric_response.content), allow_pickle=False)
    assert metric.shape == (48, 64)
    assert np.isfinite(metric).mean() > 0.99
    assert float(np.nanmax(metric) - np.nanmin(metric)) > 500

    report = client.get(f"/api/jobs/{job['job_id']}/artifacts/terrain_alignment_report").json()
    assert report["exact_input_grid"] is False
    assert "bilinear" in report["alignment"]
    assert report["valid_coverage_fraction"] > 0.99
    assert "does not improve" in report["important"]

    diagnostics = client.get(f"/api/jobs/{job['job_id']}/artifacts/height_diagnostics").json()
    assert diagnostics["geometry"]["processing"]["processing_mode"] == "source_dem_faithful"
    assert diagnostics["geometry"]["canonical_numeric_source"] == "metric_surface.npy"
    display_grid = client.get(f"/api/jobs/{job['job_id']}/artifacts/display_grid").json()
    assert display_grid["wall_delta_threshold"] == 2.0

    metric_tiff = client.get(f"/api/jobs/{job['job_id']}/artifacts/metric_geotiff").content
    with MemoryFile(metric_tiff) as memory_file, memory_file.open() as dataset:
        assert dataset.crs.to_string() == "EPSG:32643"
        assert dataset.tags()["scientific_state"] == "Metric Source DEM"
        assert dataset.tags()["vertical_datum"] == "Fixture orthometric datum"

    glb = client.get(f"/api/jobs/{job['job_id']}/artifacts/glb_mesh").content
    json_length, json_type = struct.unpack_from("<I4s", glb, 12)
    assert json_type == b"JSON"
    document = json.loads(glb[20 : 20 + json_length].decode("utf-8"))
    assert document["meshes"][0]["extras"]["scientific_state"] == "Metric Source DEM"
    assert document["meshes"][0]["extras"]["numeric_source"] == "metric_surface.npy"
    assert document["meshes"][0]["extras"]["wall_delta_threshold"] == 2.0
    assert {primitive["material"] for primitive in document["meshes"][0]["primitives"]} == {0}


def test_source_dem_workflow_rejects_insufficient_overlap_without_metric_claim(client):
    imagery, dem = _terrain_pair(overlap=False)
    response = client.post(
        "/api/terrain-jobs",
        files={
            "imagery": ("mountain-rgb.tif", imagery, "image/tiff"),
            "dem": ("mountain-dem.tif", dem, "image/tiff"),
        },
        data={"source_description": "Non-overlapping fixture", "vertical_datum": "Fixture datum"},
    )
    assert response.status_code == 202
    job = client.get(f"/api/jobs/{response.json()['job_id']}").json()
    assert job["status"] == "failed"
    assert job["scientific_state"] != "Metric Source DEM"
    assert job["calibration"]["metric_output_allowed"] is False
    assert "covers only" in job["error"]


def test_source_dem_workflow_rejects_non_metre_band_units(client):
    imagery, dem = _terrain_pair()
    with MemoryFile(dem) as source_memory, source_memory.open() as source:
        values = source.read(1)
        dem_feet = _geotiff_bytes(
            values,
            transform=source.transform,
            crs=source.crs.to_string(),
            unit="foot",
        )
    response = client.post(
        "/api/terrain-jobs",
        files={
            "imagery": ("mountain-rgb.tif", imagery, "image/tiff"),
            "dem": ("mountain-dem-feet.tif", dem_feet, "image/tiff"),
        },
        data={"source_description": "Feet fixture", "vertical_datum": "Fixture datum"},
    )
    assert response.status_code == 400
    assert "Convert its elevation values to metres" in response.json()["detail"]
