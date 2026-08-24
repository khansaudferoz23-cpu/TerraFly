from __future__ import annotations

import io
import hashlib

import numpy as np
import pytest

from .conftest import encoded_image


@pytest.mark.parametrize("mode", ["RGB", "RGBA", "L"])
def test_upload_pipeline_handles_odd_dimensions_and_modes(client, mode):
    response = client.post(
        "/api/jobs",
        files={"upload": (f"scene-{mode}.png", encoded_image(mode=mode), "image/png")},
    )
    assert response.status_code == 202
    job = client.get(f"/api/jobs/{response.json()['job_id']}").json()
    assert job["status"] == "complete"
    assert job["scientific_state"] == "Relative"
    assert job["units"] == "relative_0_1"
    assert job["calibration"]["metric_output_allowed"] is False
    names = {artifact["name"] for artifact in job["artifacts"]}
    assert {"numeric_surface", "preview", "texture", "height_texture", "surface_grid", "manifest"} <= names
    surface_response = client.get(f"/api/jobs/{job['job_id']}/artifacts/numeric_surface")
    surface = np.load(io.BytesIO(surface_response.content), allow_pickle=False)
    assert surface.shape == (23, 37)
    assert surface.dtype == np.float32
    assert np.isfinite(surface).all()
    assert 0 <= float(surface.min()) <= float(surface.max()) <= 1
    assert any("TEST-ONLY" in warning for warning in job["warnings"])
    for artifact in job["artifacts"]:
        downloaded = client.get(f"/api/jobs/{job['job_id']}/artifacts/{artifact['name']}")
        assert downloaded.status_code == 200
        assert hashlib.sha256(downloaded.content).hexdigest() == artifact["sha256"]


@pytest.mark.parametrize(
    ("filename", "content", "expected"),
    [
        ("corrupt.png", b"not-an-image", 400),
        ("scene.gif", b"GIF89a", 415),
        ("../scene.png", b"x", 400),
        ("..\\scene.png", b"x", 400),
        ("scene.png", b"", 400),
    ],
)
def test_rejects_invalid_uploads(client, filename, content, expected):
    response = client.post("/api/jobs", files={"upload": (filename, content, "application/octet-stream")})
    assert response.status_code == expected


def test_rejects_oversized_upload_before_decode(client, settings):
    settings.max_upload_bytes = 10
    response = client.post(
        "/api/jobs", files={"upload": ("scene.png", encoded_image(), "image/png")}
    )
    assert response.status_code == 413


def test_capabilities_state_the_metric_contract(client):
    response = client.get("/api/capabilities")
    assert response.status_code == 200
    payload = response.json()
    assert payload["metric_requires_calibration"] is True
    assert payload["scientific_states"] == [
        "Relative",
        "Georeferenced Relative",
        "Metric Calibrated",
    ]
\n