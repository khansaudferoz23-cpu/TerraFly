from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import Settings
from .imaging import SUPPORTED_EXTENSIONS, inspect_image, read_upload
from .jobs import JobStore
from .pipeline import estimated_working_bytes, run_job
from .schemas import Capabilities, JobManifest, JobStatus


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or Settings()
    app = FastAPI(title="TerraFly API", version="0.2.0")
    app.state.settings = active_settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
    )

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "TerraFly", "version": "0.2.0"}

    @app.get("/api/capabilities", response_model=Capabilities)
    def capabilities() -> Capabilities:
        return Capabilities(
            accepted_extensions=sorted(SUPPORTED_EXTENSIONS),
            max_upload_bytes=active_settings.max_upload_bytes,
            max_pixels=active_settings.max_pixels,
            max_working_bytes=active_settings.max_working_bytes,
            default_model=active_settings.model_id,
            tile_size=active_settings.tile_size,
            tile_overlap=active_settings.tile_overlap,
            scientific_states=["Relative", "Georeferenced Relative", "Metric Calibrated"],
        )

    @app.post("/api/jobs", response_model=JobManifest, status_code=202)
    async def create_job(upload: UploadFile, background_tasks: BackgroundTasks) -> JobManifest:
        filename, data = await read_upload(upload, active_settings.max_upload_bytes)
        inspected = inspect_image(data, filename, active_settings.max_pixels)
        estimate = estimated_working_bytes(inspected.rgb.shape[1], inspected.rgb.shape[0])
        if estimate > active_settings.max_working_bytes:
            raise HTTPException(
                status_code=413,
                detail="Image dimensions exceed the configured processing-memory safety budget.",
            )
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

    @app.delete("/api/jobs/{job_id}", status_code=204)
    def delete_job(job_id: str) -> None:
        store = JobStore(active_settings.jobs_root)
        try:
            manifest = store.get(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Job not found.") from exc
        if manifest.status in {JobStatus.QUEUED, JobStatus.RUNNING}:
            raise HTTPException(status_code=409, detail="A running job cannot be cleared.")
        directory = store.job_dir(job_id)
        shutil.rmtree(directory)

    return app


app = create_app()
