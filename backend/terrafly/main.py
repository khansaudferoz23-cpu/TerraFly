from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import Settings
from .imaging import SUPPORTED_EXTENSIONS, inspect_image, read_upload
from .jobs import JobStore
from .pipeline import run_job
from .schemas import Capabilities, JobManifest


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or Settings()
    app = FastAPI(title="TerraFly API", version="0.1.0")
    app.state.settings = active_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "TerraFly", "version": "0.1.0"}

    @app.get("/api/capabilities", response_model=Capabilities)
    def capabilities() -> Capabilities:
        return Capabilities(
            accepted_extensions=sorted(SUPPORTED_EXTENSIONS),
            max_upload_bytes=active_settings.max_upload_bytes,
            max_pixels=active_settings.max_pixels,
            default_model=active_settings.model_id,
            scientific_states=["Relative", "Georeferenced Relative", "Metric Calibrated"],
        )

    @app.post("/api/jobs", response_model=JobManifest, status_code=202)
    async def create_job(upload: UploadFile, background_tasks: BackgroundTasks) -> JobManifest:
        filename, data = await read_upload(upload, active_settings.max_upload_bytes)
        inspected = inspect_image(data, filename, active_settings.max_pixels)
        store = JobStore(active_settings.jobs_root)
        manifest = store.create(filename, inspected.metadata, inspected.geospatial, inspected.warnings)
        suffix = Path(filename).suffix.lower()
        stored_filename = f"input{suffix}"
        manifest.input["stored_filename"] = stored_filename
        (store.job_dir(manifest.job_id) / stored_filename).write_bytes(data)
        store.save(manifest)
        background_tasks.add_task(run_job, manifest.job_id, active_settings)
        return manifest

    @app.get("/api/jobs/{job_id}", response_model=JobManifest)
    def get_job(job_id: str) -> JobManifest:
        try:
            return JobStore(active_settings.jobs_root).get(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Job not found.") from exc

    @app.get("/api/jobs/{job_id}/artifacts/{artifact_name}")
    def get_artifact(job_id: str, artifact_name: str) -> FileResponse:
        try:
            store = JobStore(active_settings.jobs_root)
            manifest = store.get(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Job not found.") from exc
        artifact = next((item for item in manifest.artifacts if item.name == artifact_name), None)
        if artifact is None:
            raise HTTPException(status_code=404, detail="Artifact is unavailable for this job.")
        path = (store.job_dir(job_id) / artifact.filename).resolve()
        if path.parent != store.job_dir(job_id) or not path.is_file():
            raise HTTPException(status_code=404, detail="Artifact file is missing.")
        return FileResponse(path, media_type=artifact.media_type, filename=artifact.filename)

    return app


app = create_app()

\n