from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from .schemas import JobManifest, JobStatus, ScientificState


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


class JobStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def job_dir(self, job_id: str) -> Path:
        if len(job_id) != 32 or any(character not in "0123456789abcdef" for character in job_id):
            raise KeyError(job_id)
        path = (self.root / job_id).resolve()
        if path.parent != self.root:
            raise KeyError(job_id)
        return path

    def create(self, filename: str, input_metadata: dict, geospatial: dict | None, warnings: list[str]) -> JobManifest:
        job_id = uuid4().hex
        timestamp = now_iso()
        state = ScientificState.GEOREFERENCED_RELATIVE if geospatial else ScientificState.RELATIVE
        manifest = JobManifest(
            job_id=job_id,
            status=JobStatus.QUEUED,
            stage="queued",
            progress=5,
            created_at=timestamp,
            updated_at=timestamp,
            input={"filename": filename, **input_metadata},
            scientific_state=state,
            units="relative_0_1",
            geospatial=geospatial,
            calibration={
                "method": None,
                "status": "not_requested",
                "metric_output_allowed": False,
                "reason": "No valid vertical calibration evidence was supplied.",
            },
            model={},
            configuration={"display_vertical_exaggeration": 1.4},
            warnings=warnings,
        )
        directory = self.job_dir(job_id)
        directory.mkdir(parents=False)
        self.save(manifest)
        return manifest

    def save(self, manifest: JobManifest) -> None:
        manifest.updated_at = now_iso()
        path = self.job_dir(manifest.job_id) / "job.json"
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
        temporary.replace(path)

    def get(self, job_id: str) -> JobManifest:
        path = self.job_dir(job_id) / "job.json"
        if not path.is_file():
            raise KeyError(job_id)
        return JobManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))
