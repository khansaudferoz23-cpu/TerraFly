from __future__ import annotations

import traceback

from .artifacts import sha256_file, write_surface_artifacts
from .config import Settings
from .imaging import inspect_image
from .inference.factory import create_adapter
from .jobs import JobStore
from .schemas import Artifact, JobStatus


def run_job(job_id: str, settings: Settings) -> None:
    store = JobStore(settings.jobs_root)
    manifest = store.get(job_id)
    job_dir = store.job_dir(job_id)
    input_path = job_dir / manifest.input["stored_filename"]
    try:
        manifest.status = JobStatus.RUNNING
        manifest.stage = "validation"
        manifest.progress = 15
        store.save(manifest)
        inspected = inspect_image(input_path.read_bytes(), manifest.input["filename"], settings.max_pixels)

        manifest.stage = "preprocessing"
        manifest.progress = 30
        store.save(manifest)
        adapter = create_adapter(settings)

        manifest.stage = "inference"
        manifest.progress = 50
        store.save(manifest)
        prediction = adapter.predict(inspected.rgb)

        manifest.stage = "meshing"
        manifest.progress = 80
        manifest.model = {
            "adapter": settings.model_adapter,
            "checkpoint": prediction.model_id,
            "revision": prediction.model_revision,
            "device": prediction.device,
        }
        manifest.warnings = list(dict.fromkeys(manifest.warnings + prediction.warnings))
        artifacts = write_surface_artifacts(job_dir, prediction.relative_height, inspected.rgb)
        manifest.artifacts = artifacts
        manifest.status = JobStatus.COMPLETE
        manifest.stage = "complete"
        manifest.progress = 100
        store.save(manifest)
        manifest_path = job_dir / "job_manifest.json"
        manifest_path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        manifest.artifacts.append(
            Artifact(
                name="manifest",
                filename=manifest_path.name,
                media_type="application/json",
                sha256=sha256_file(manifest_path),
                bytes=manifest_path.stat().st_size,
            )
        )
        store.save(manifest)
    except Exception as exc:  # error is deliberately converted into a friendly persisted job failure
        manifest.status = JobStatus.FAILED
        manifest.stage = "failed"
        manifest.error = str(exc)
        manifest.warnings.append("The job failed without claiming a scientific result.")
        manifest.configuration["diagnostic"] = traceback.format_exc(limit=8)
        store.save(manifest)
