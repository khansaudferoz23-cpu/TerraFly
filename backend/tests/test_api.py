from __future__ import annotations

import io
import hashlib

import numpy as np
import pytest
from fastapi.testclient import TestClient

from terrafly.main import create_app

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
    assert {
        "raw_model_output",
        "numeric_surface",
        "preview",
        "texture",
        "height_texture",
        "surface_grid",
        "structure_layer",
        "glb_mesh",
        "height_diagnostics",
        "manifest",
    } <= names
    surface_response = client.get(f"/api/jobs/{job['job_id']}/artifacts/numeric_surface")
    surface = np.load(io.BytesIO(surface_response.content), allow_pickle=False)
    raw_response = client.get(f"/api/jobs/{job['job_id']}/artifacts/raw_model_output")
    raw = np.load(io.BytesIO(raw_response.content), allow_pickle=False)
    assert surface.shape == (23, 37)
    assert raw.shape == surface.shape
    assert surface.dtype == np.float32
    assert np.isfinite(surface).all()
    assert 0 <= float(surface.min()) <= float(surface.max()) <= 1
    diagnostics = client.get(
        f"/api/jobs/{job['job_id']}/artifacts/height_diagnostics"
    ).json()
    assert diagnostics["conversion"]["normalization"]["applied_count"] == 1
    assert diagnostics["geometry"]["source"] == "relative_surface.npy"
    assert diagnostics["geometry"]["colour_preview_is_geometry_source"] is False
    assert any("TEST-ONLY" in warning for warning in job["warnings"])
    if mode == "L":
        assert any("Single-band input" in warning for warning in job["warnings"])
        assert any("Thermal/TIR" in warning for warning in job["warnings"])
    else:
        assert not any("Single-band input" in warning for warning in job["warnings"])
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
    assert payload["tiled_inference"] is True
    assert payload["tile_size"] > payload["tile_overlap"]
    assert payload["calibration_methods"] == [
        "aligned_reference_dsm",
        "ground_control_points",
    ]
    assert payload["reference_dsm_requires_exact_alignment"] is True


def test_rejects_dimensions_above_processing_memory_budget(client, settings):
    settings.max_working_bytes = 100
    response = client.post(
        "/api/jobs", files={"upload": ("scene.png", encoded_image(), "image/png")}
    )
    assert response.status_code == 413
    assert "memory" in response.json()["detail"]


def test_completed_job_can_be_cleared_without_path_escape(client):
    created = client.post(
        "/api/jobs", files={"upload": ("scene.png", encoded_image(), "image/png")}
    ).json()
    job_id = created["job_id"]
    assert client.delete(f"/api/jobs/{job_id}").status_code == 204
    assert client.get(f"/api/jobs/{job_id}").status_code == 404
    assert client.delete("/api/jobs/not-a-job").status_code == 404


def test_prebuilt_frontend_is_served_without_a_development_server(settings):
    settings.frontend_dist.mkdir(parents=True)
    (settings.frontend_dist / "index.html").write_text(
        "<!doctype html><title>TerraFly release shell</title>", encoding="utf-8"
    )
    with TestClient(create_app(settings)) as release_client:
        response = release_client.get("/")
        assert response.status_code == 200
        assert "TerraFly release shell" in response.text
        assert release_client.get("/api/health").json()["version"] == "1.0.0"
