from __future__ import annotations

import io

import numpy as np
import rasterio
from rasterio.io import MemoryFile
from rasterio.transform import from_origin


def make_geotiff() -> bytes:
    data = np.zeros((3, 11, 17), dtype=np.uint8)
    data[0] = np.arange(17, dtype=np.uint8)[None, :]
    data[1] = np.arange(11, dtype=np.uint8)[:, None]
    data[2] = 91
    profile = {
        "driver": "GTiff",
        "height": 11,
        "width": 17,
        "count": 3,
        "dtype": "uint8",
        "crs": "EPSG:32643",
        "transform": from_origin(500000, 2000000, 2, 2),
        "nodata": 0,
    }
    with MemoryFile() as memory_file:
        with memory_file.open(**profile) as dataset:
            dataset.write(data)
        return memory_file.read()


def test_geotiff_metadata_is_preserved_but_not_called_metric(client):
    response = client.post(
        "/api/jobs", files={"upload": ("asymmetric.tif", make_geotiff(), "image/tiff")}
    )
    assert response.status_code == 202
    job = client.get(f"/api/jobs/{response.json()['job_id']}").json()
    assert job["scientific_state"] == "Georeferenced Relative"
    assert job["geospatial"]["crs"] == "EPSG:32643"
    assert job["geospatial"]["transform"] == [2.0, 0.0, 500000.0, 0.0, -2.0, 2000000.0]
    assert job["geospatial"]["horizontal_units"] == "metre"
    assert job["geospatial"]["nodata"] == 0.0
    assert job["calibration"]["metric_output_allowed"] is False
    assert any("does not establish vertical scale" in warning for warning in job["warnings"])
