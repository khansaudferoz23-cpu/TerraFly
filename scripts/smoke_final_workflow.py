from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import time
import warnings
from pathlib import Path

import rasterio
warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated.*")
from fastapi.testclient import TestClient

from terrafly.config import Settings
from terrafly.main import create_app


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run TerraFly's complete real-model and calibration release workflow."
    )
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    sample_root = project_root / "sample_data"
    input_path = sample_root / "terrafly_calibration_demo_input.tif"
    reference_path = sample_root / "terrafly_calibration_demo_reference.tif"
    started = time.perf_counter()
    runtime_root = project_root / "runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="final-smoke-", dir=runtime_root) as temporary:
        settings = Settings(
            jobs_root=Path(temporary) / "jobs",
            frontend_dist=project_root / "frontend" / "dist",
            model_adapter="depth-anything-v2",
            model_id="depth-anything/Depth-Anything-V2-Small-hf",
            device=args.device,
        )
        with TestClient(create_app(settings)) as client:
            health = client.get("/api/health")
            if health.status_code != 200 or health.json()["version"] != "1.0.0":
                raise AssertionError("Release health/version check failed.")
            created = client.post(
                "/api/jobs",
                files={"upload": (input_path.name, input_path.read_bytes(), "image/tiff")},
            )
            if created.status_code != 202:
                raise AssertionError(created.text)
            job_id = created.json()["job_id"]
            relative_job = client.get(f"/api/jobs/{job_id}").json()
            if relative_job["status"] != "complete":
                raise AssertionError(relative_job)
            if relative_job["scientific_state"] != "Georeferenced Relative":
                raise AssertionError("GeoTIFF skipped the required relative state.")
            calibrated_response = client.post(
                f"/api/jobs/{job_id}/calibrate/reference",
                files={
                    "reference": (
                        reference_path.name,
                        reference_path.read_bytes(),
                        "image/tiff",
                    )
                },
                data={
                    "source_description": "Bundled synthetic software oracle",
                    "vertical_datum": "Demo benchmark datum",
                    "max_rmse_m": "0.5",
                },
            )
            if calibrated_response.status_code != 200:
                raise AssertionError(calibrated_response.text)
            calibrated = calibrated_response.json()
            if calibrated["scientific_state"] != "Metric Calibrated":
                raise AssertionError(calibrated["calibration"])
            names = {artifact["name"] for artifact in calibrated["artifacts"]}
            expected = {
                "raw_model_output",
                "numeric_surface",
                "height_diagnostics",
                "structure_layer",
                "glb_mesh",
                "calibration_reference",
                "calibration_report",
                "metric_surface",
                "metric_grid",
                "metric_geotiff",
                "error_geotiff",
                "manifest",
            }
            if not expected <= names:
                raise AssertionError(f"Missing artifacts: {sorted(expected - names)}")
            for artifact in calibrated["artifacts"]:
                downloaded = client.get(f"/api/jobs/{job_id}/artifacts/{artifact['name']}")
                if downloaded.status_code != 200:
                    raise AssertionError(f"Artifact unavailable: {artifact['name']}")
                if hashlib.sha256(downloaded.content).hexdigest() != artifact["sha256"]:
                    raise AssertionError(f"Artifact hash mismatch: {artifact['name']}")
            metric_bytes = client.get(f"/api/jobs/{job_id}/artifacts/metric_geotiff").content
            metric_path = Path(temporary) / "metric.tif"
            metric_path.write_bytes(metric_bytes)
            with rasterio.open(metric_path) as metric:
                if metric.crs is None or metric.tags().get("units") != "metre":
                    raise AssertionError("Metric GeoTIFF lost its CRS or metre tag.")

    result = {
        "result": "PASS",
        "workflow": "real GeoTIFF upload -> relative 3D artifacts -> held-out calibration -> metric artifacts",
        "duration_seconds": round(time.perf_counter() - started, 3),
        "device": calibrated["model"]["device"],
        "model_revision": calibrated["model"]["revision"],
        "scientific_state": calibrated["scientific_state"],
        "artifact_count": len(calibrated["artifacts"]),
        "all_artifact_hashes_verified": True,
        "scale_m_per_relative_unit": calibrated["calibration"]["fit"][
            "scale_m_per_relative_unit"
        ],
        "offset_m": calibrated["calibration"]["fit"]["offset_m"],
        "held_out_rmse_m": calibrated["calibration"]["evaluation"]["rmse_m"],
        "held_out_r_squared": calibrated["calibration"]["evaluation"]["r_squared"],
        "scientific_warning": "Bundled reference is a synthetic software oracle, not real accuracy evidence.",
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
