from __future__ import annotations

import io
import hashlib
import json

import numpy as np
import pytest
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin


WIDTH = 48
HEIGHT = 36
TRANSFORM = from_origin(500000, 2000000, 2, 2)


def georeferenced_input() -> bytes:
    yy, xx = np.indices((HEIGHT, WIDTH))
    data = np.empty((3, HEIGHT, WIDTH), dtype=np.uint8)
    data[0] = np.clip(xx * 5 + yy, 0, 255)
    data[1] = np.clip(yy * 7 + xx // 2, 0, 255)
    data[2] = np.clip(40 + xx * 2 + yy * 2, 0, 255)
    return raster_bytes(data, count=3, transform=TRANSFORM, dtype="uint8")


def raster_bytes(
    data: np.ndarray,
    *,
    count: int,
    transform=TRANSFORM,
    dtype: str = "float32",
    crs: str = "EPSG:32643",
    nodata: float | None = None,
) -> bytes:
    if data.ndim == 2:
        data = data[None, ...]
    profile = {
        "driver": "GTiff",
        "height": data.shape[1],
        "width": data.shape[2],
        "count": count,
        "dtype": dtype,
        "crs": crs,
        "transform": transform,
        "nodata": nodata,
    }
    with MemoryFile() as memory_file:
        with memory_file.open(**profile) as dataset:
            dataset.write(data.astype(dtype))
        return memory_file.read()


def completed_georeferenced_job(client) -> tuple[dict, np.ndarray]:
    created = client.post(
        "/api/jobs", files={"upload": ("input.tif", georeferenced_input(), "image/tiff")}
    )
    assert created.status_code == 202
    job = client.get(f"/api/jobs/{created.json()['job_id']}").json()
    assert job["status"] == "complete"
    surface_bytes = client.get(
        f"/api/jobs/{job['job_id']}/artifacts/numeric_surface"
    ).content
    return job, np.load(io.BytesIO(surface_bytes), allow_pickle=False)


def test_aligned_reference_dsm_passes_held_out_gate_and_writes_metric_evidence(client):
    job, relative = completed_georeferenced_job(client)
    reference = 100.0 + 40.0 * relative.astype(np.float64)
    rows, columns = np.indices(relative.shape)
    held_out = ((rows // (HEIGHT // 4)) + (columns // (WIDTH // 4))) % 4 == 0
    outlier_locations = np.flatnonzero(~held_out)[::80]
    reference.ravel()[outlier_locations] += 250.0
    response = client.post(
        f"/api/jobs/{job['job_id']}/calibrate/reference",
        files={"reference": ("survey-dsm.tif", raster_bytes(reference, count=1), "image/tiff")},
        data={
            "source_description": "Independent synthetic survey DSM",
            "vertical_datum": "EGM96 orthometric height",
            "max_rmse_m": "0.05",
        },
    )
    assert response.status_code == 200, response.text
    calibrated = response.json()
    assert calibrated["scientific_state"] == "Metric Calibrated"
    assert calibrated["units"] == "metre"
    assert calibrated["calibration"]["status"] == "passed"
    assert calibrated["calibration"]["metric_output_allowed"] is True
    assert calibrated["calibration"]["fit"]["scale_m_per_relative_unit"] == pytest.approx(40.0, abs=0.01)
    assert calibrated["calibration"]["fit"]["offset_m"] == pytest.approx(100.0, abs=0.01)
    assert calibrated["calibration"]["evaluation"]["rmse_m"] < 0.01
    names = {artifact["name"] for artifact in calibrated["artifacts"]}
    assert {
        "calibration_reference",
        "calibration_report",
        "metric_surface",
        "metric_grid",
        "metric_geotiff",
        "error_geotiff",
        "error_preview",
        "manifest",
    } <= names
    for artifact in calibrated["artifacts"]:
        downloaded = client.get(
            f"/api/jobs/{job['job_id']}/artifacts/{artifact['name']}"
        )
        assert downloaded.status_code == 200
        assert hashlib.sha256(downloaded.content).hexdigest() == artifact["sha256"]

    metric_response = client.get(
        f"/api/jobs/{job['job_id']}/artifacts/metric_geotiff"
    )
    assert metric_response.status_code == 200
    with MemoryFile(metric_response.content) as memory_file, memory_file.open() as dataset:
        metric = dataset.read(1)
        assert dataset.crs.to_string() == "EPSG:32643"
        assert dataset.transform == TRANSFORM
        assert dataset.dtypes == ("float32",)
        assert dataset.tags()["units"] == "metre"
        assert dataset.tags()["vertical_datum"] == "EGM96 orthometric height"
    np.testing.assert_allclose(metric, 100.0 + 40.0 * relative, atol=0.02)
    metric_grid_response = client.get(
        f"/api/jobs/{job['job_id']}/artifacts/metric_grid"
    )
    metric_grid = json.loads(metric_grid_response.content)
    relative_grid = client.get(
        f"/api/jobs/{job['job_id']}/artifacts/surface_grid"
    ).json()
    assert metric_grid["units"] == "metre"
    assert metric_grid["vertical_datum"] == "EGM96 orthometric height"
    assert metric_grid["shape"] == relative_grid["shape"]
    assert metric_grid["row_indices"] == relative_grid["row_indices"]
    assert metric_grid["column_indices"] == relative_grid["column_indices"]
    np.testing.assert_allclose(
        np.asarray(metric_grid["values"]),
        100.0 + 40.0 * np.asarray(relative_grid["values"]),
        atol=0.02,
    )


def test_reference_alignment_mismatch_is_rejected_before_any_metric_claim(client):
    job, relative = completed_georeferenced_job(client)
    shifted = from_origin(500002, 2000000, 2, 2)
    reference = 100.0 + 40.0 * relative
    response = client.post(
        f"/api/jobs/{job['job_id']}/calibrate/reference",
        files={"reference": ("shifted.tif", raster_bytes(reference, count=1, transform=shifted), "image/tiff")},
        data={
            "source_description": "Shifted survey DSM",
            "vertical_datum": "EGM96",
            "max_rmse_m": "1",
        },
    )
    assert response.status_code == 400
    assert "transform" in response.json()["detail"]
    unchanged = client.get(f"/api/jobs/{job['job_id']}").json()
    assert unchanged["scientific_state"] == "Georeferenced Relative"
    assert "metric_geotiff" not in {item["name"] for item in unchanged["artifacts"]}


def test_poor_reference_is_evaluated_but_metric_output_stays_locked(client):
    job, _ = completed_georeferenced_job(client)
    rng = np.random.default_rng(26175)
    unrelated = rng.normal(250, 15, size=(HEIGHT, WIDTH)).astype(np.float32)
    response = client.post(
        f"/api/jobs/{job['job_id']}/calibrate/reference",
        files={"reference": ("unrelated.tif", raster_bytes(unrelated, count=1), "image/tiff")},
        data={
            "source_description": "Unrelated validation raster",
            "vertical_datum": "EGM96",
            "max_rmse_m": "0.5",
        },
    )
    assert response.status_code == 200
    rejected = response.json()
    assert rejected["calibration"]["status"] == "rejected"
    assert rejected["calibration"]["metric_output_allowed"] is False
    assert rejected["scientific_state"] == "Georeferenced Relative"
    names = {artifact["name"] for artifact in rejected["artifacts"]}
    assert {"calibration_reference", "calibration_report", "manifest"} <= names
    assert "metric_geotiff" not in names
    assert "metric_surface" not in names


def test_independent_gcp_validation_can_unlock_metric_geotiff(client):
    job, relative = completed_georeferenced_job(client)
    control_pixels = [(1, 1), (12, 2), (25, 4), (46, 1), (3, 17), (20, 20), (44, 18), (2, 34), (25, 33), (46, 34)]
    validation_pixels = [(8, 8), (38, 10), (10, 29), (40, 30)]

    def point(column: int, row: int) -> dict[str, float]:
        return {
            "column": column,
            "row": row,
            "elevation_m": float(50.0 + 20.0 * relative[row, column]),
        }

    response = client.post(
        f"/api/jobs/{job['job_id']}/calibrate/gcps",
        json={
            "source_description": "Surveyed control and independent check points",
            "vertical_datum": "Local benchmark datum",
            "max_rmse_m": 0.02,
            "controls": [point(column, row) for column, row in control_pixels],
            "validation": [point(column, row) for column, row in validation_pixels],
        },
    )
    assert response.status_code == 200, response.text
    calibrated = response.json()
    assert calibrated["scientific_state"] == "Metric Calibrated"
    assert calibrated["calibration"]["method"] == "ground_control_points"
    assert calibrated["calibration"]["evaluation"]["count"] == 4
    assert calibrated["calibration"]["evaluation"]["rmse_m"] < 0.01
    names = {artifact["name"] for artifact in calibrated["artifacts"]}
    assert {"metric_surface", "metric_grid", "metric_geotiff", "calibration_report"} <= names
    assert "error_geotiff" not in names


def test_metric_outputs_preserve_source_nodata(client):
    yy, xx = np.indices((HEIGHT, WIDTH))
    data = np.empty((3, HEIGHT, WIDTH), dtype=np.uint8)
    data[0] = 20 + xx * 3
    data[1] = 20 + yy * 4
    data[2] = 80 + (xx + yy) % 120
    data[:, :4, :5] = 0
    source = raster_bytes(data, count=3, dtype="uint8", nodata=0)
    created = client.post(
        "/api/jobs", files={"upload": ("masked-input.tif", source, "image/tiff")}
    ).json()
    job = client.get(f"/api/jobs/{created['job_id']}").json()
    relative_response = client.get(
        f"/api/jobs/{job['job_id']}/artifacts/numeric_surface"
    )
    relative = np.load(io.BytesIO(relative_response.content), allow_pickle=False)
    reference = 70.0 + 25.0 * relative
    response = client.post(
        f"/api/jobs/{job['job_id']}/calibrate/reference",
        files={"reference": ("reference.tif", raster_bytes(reference, count=1), "image/tiff")},
        data={
            "source_description": "Masked source regression reference",
            "vertical_datum": "Test datum",
            "max_rmse_m": "0.05",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["calibration"]["status"] == "passed"
    metric_npy = np.load(
        io.BytesIO(
            client.get(
                f"/api/jobs/{job['job_id']}/artifacts/metric_surface"
            ).content
        ),
        allow_pickle=False,
    )
    assert np.isnan(metric_npy[:4, :5]).all()
    metric_tiff = client.get(
        f"/api/jobs/{job['job_id']}/artifacts/metric_geotiff"
    ).content
    with MemoryFile(metric_tiff) as memory_file, memory_file.open() as dataset:
        masked = dataset.read(1, masked=True)
        assert masked.mask[:4, :5].all()
