from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from fastapi.testclient import TestClient

from terrafly.config import Settings
from terrafly.main import create_app


def main() -> int:
    parser = argparse.ArgumentParser(description="Exercise upload-to-artifacts with the real model.")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    sample_path = project_root / "sample_data" / "terrafly_synthetic_aerial.png"
    settings = Settings(
        jobs_root=project_root / "runtime" / "real-api-smoke",
        model_adapter="depth-anything-v2",
        model_id="depth-anything/Depth-Anything-V2-Small-hf",
        device=args.device,
    )
    started = time.perf_counter()
    with TestClient(create_app(settings)) as client:
        response = client.post(
            "/api/jobs",
            files={"upload": (sample_path.name, sample_path.read_bytes(), "image/png")},
        )
        if response.status_code != 202:
            raise AssertionError(response.text)
        job = client.get(f"/api/jobs/{response.json()['job_id']}").json()
        if job["status"] != "complete":
            raise AssertionError(job)
        verified_artifacts: list[str] = []
        for artifact in job["artifacts"]:
            downloaded = client.get(
                f"/api/jobs/{job['job_id']}/artifacts/{artifact['name']}"
            )
            if downloaded.status_code != 200:
                raise AssertionError(f"Artifact unavailable: {artifact['name']}")
            digest = hashlib.sha256(downloaded.content).hexdigest()
            if digest != artifact["sha256"]:
                raise AssertionError(f"Artifact hash mismatch: {artifact['name']}")
            verified_artifacts.append(artifact["name"])
    result = {
        "result": "PASS",
        "workflow": "real_upload_to_artifacts",
        "duration_seconds": round(time.perf_counter() - started, 3),
        "scientific_state": job["scientific_state"],
        "units": job["units"],
        "model": job["model"],
        "input_sha256": job["input"]["sha256"],
        "verified_artifacts": verified_artifacts,
        "metric_output_allowed": job["calibration"]["metric_output_allowed"],
        "warnings": job["warnings"],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
