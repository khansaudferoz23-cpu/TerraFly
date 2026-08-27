from __future__ import annotations

import io
import tempfile
from pathlib import Path

import numpy as np
from fastapi.testclient import TestClient

from terrafly.config import Settings
from terrafly.main import create_app


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    imagery_path = project_root / "sample_data" / "terrafly_terrain_demo_imagery.tif"
    dem_path = project_root / "sample_data" / "terrafly_terrain_demo_dem.tif"
    if not imagery_path.is_file() or not dem_path.is_file():
        raise RuntimeError("Bundled terrain demo inputs are missing.")

    with tempfile.TemporaryDirectory(prefix="terrafly-terrain-smoke-") as temporary:
        settings = Settings(
            jobs_root=Path(temporary) / "jobs",
            frontend_dist=project_root / "frontend" / "dist",
            max_upload_bytes=25 * 1024 * 1024,
            max_pixels=30_000_000,
        )
        with TestClient(create_app(settings)) as client:
            with imagery_path.open("rb") as imagery, dem_path.open("rb") as dem:
                response = client.post(
                    "/api/terrain-jobs",
                    files={
                        "imagery": (imagery_path.name, imagery, "image/tiff"),
                        "dem": (dem_path.name, dem, "image/tiff"),
                    },
                    data={
                        "source_description": "TerraFly bundled synthetic mountain DEM",
                        "vertical_datum": "TerraFly synthetic demo datum",
                    },
                )
            response.raise_for_status()
            job_id = response.json()["job_id"]
            job = client.get(f"/api/jobs/{job_id}").json()
            if job["status"] != "complete" or job["scientific_state"] != "Metric Source DEM":
                raise RuntimeError(f"Terrain workflow did not complete: {job.get('error')}")
            names = {artifact["name"] for artifact in job["artifacts"]}
            required = {"metric_surface", "metric_geotiff", "metric_grid", "glb_mesh", "terrain_alignment_report"}
            if not required <= names:
                raise RuntimeError(f"Terrain workflow is missing artifacts: {sorted(required - names)}")
            metric_response = client.get(f"/api/jobs/{job_id}/artifacts/metric_surface")
            metric = np.load(io.BytesIO(metric_response.content), allow_pickle=False)
            if metric.shape != (480, 640) or not np.isfinite(metric).all():
                raise RuntimeError("Aligned terrain metric surface has an unexpected shape or NoData.")
            print(
                "Terrain smoke PASS:",
                job_id,
                f"{metric.shape[1]}x{metric.shape[0]}",
                f"{float(metric.min()):.1f}..{float(metric.max()):.1f} m",
                f"{len(job['artifacts'])} artifacts",
            )


if __name__ == "__main__":
    main()
