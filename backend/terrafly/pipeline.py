from __future__ import annotations

import traceback

from .artifacts import sha256_file, surface_tilt_diagnostics, write_surface_artifacts
from .config import Settings
from .imaging import inspect_image
from .inference.factory import create_adapter
from .jobs import JobStore
from .schemas import Artifact, JobStatus


def estimated_working_bytes(width: int, height: int) -> int:
    """Conservative input-dependent budget for RGB, predictions, blending, and artifacts."""
    return width * height * 32


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
        working_bytes = estimated_working_bytes(inspected.rgb.shape[1], inspected.rgb.shape[0])
        if working_bytes > settings.max_working_bytes:
            raise RuntimeError(
                "Image exceeds the configured processing-memory safety budget. "
                "Reduce its dimensions or raise TERRAFLY_MAX_WORKING_BYTES deliberately."
            )

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
        manifest.configuration.update(prediction.metadata)
        manifest.configuration["estimated_working_bytes"] = working_bytes
        tilt_diagnostics = surface_tilt_diagnostics(prediction.relative_height)
        manifest.configuration["global_tilt_indicator"] = tilt_diagnostics
        if tilt_diagnostics["warning"]:
            prediction.warnings.append(
                "This scene has a dominant image-plane trend "
                f"({float(tilt_diagnostics['plane_variance_fraction']):.1%} of sampled variance); "
                "it may be perspective bias rather than terrain slope. No automatic correction was applied."
            )
        manifest.warnings = list(dict.fromkeys(manifest.warnings + prediction.warnings))
        artifacts = write_surface_artifacts(
            job_dir,
            prediction.relative_height,
            inspected.rgb,
            raw_model_output=prediction.raw_model_output,
            conversion_diagnostics=prediction.conversion_diagnostics,
            tilt_diagnostics=tilt_diagnostics,
        )
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
