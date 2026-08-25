from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .calibration import CalibrationInputError, calibrate_gcps, calibrate_reference
from .config import Settings
from .imaging import SUPPORTED_EXTENSIONS, inspect_image, read_upload
from .jobs import JobStore
from .pipeline import estimated_working_bytes, run_job
from .schemas import Capabilities, GcpCalibrationRequest, JobManifest, JobStatus


def create_app(settings: Settings | None = None) -> FastAPI:
    active_settings = settings or Settings()
    app = FastAPI(title="TerraFly API", version="1.0.0")
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
        return {"status": "ok", "service": "TerraFly", "version": "1.0.0"}

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

    def completed_georeferenced_job(job_id: str) -> tuple[JobStore, JobManifest]:
        store = JobStore(active_settings.jobs_root)
        try:
            manifest = store.get(job_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Job not found.") from exc
        if manifest.status != JobStatus.COMPLETE:
            raise HTTPException(status_code=409, detail="Calibration requires a completed job.")
        if manifest.geospatial is None:
            raise HTTPException(status_code=409, detail="Calibration requires a georeferenced input GeoTIFF.")
        return store, manifest

    @app.post("/api/jobs/{job_id}/calibrate/reference", response_model=JobManifest)
    async def calibrate_with_reference(
        job_id: str,
        reference: UploadFile,
        source_description: str = Form(min_length=3, max_length=300),
        vertical_datum: str = Form(min_length=2, max_length=100),
        max_rmse_m: float = Form(gt=0, le=100_000),
    ) -> JobManifest:
        store, manifest = completed_georeferenced_job(job_id)
        filename, data = await read_upload(reference, active_settings.max_upload_bytes)
        if Path(filename).suffix.lower() not in {".tif", ".tiff"}:
            raise HTTPException(status_code=415, detail="Reference calibration requires a GeoTIFF DSM.")
        source = source_description.strip()
        datum = vertical_datum.strip()
        if len(source) < 3 or len(datum) < 2:
            raise HTTPException(status_code=400, detail="Evidence source and vertical datum cannot be blank.")
        try:
            return calibrate_reference(
                store,
                manifest,
                data,
                filename,
                source,
                datum,
                max_rmse_m,
            )
        except CalibrationInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/jobs/{job_id}/calibrate/gcps", response_model=JobManifest)
    def calibrate_with_gcps(job_id: str, request: GcpCalibrationRequest) -> JobManifest:
        store, manifest = completed_georeferenced_job(job_id)
        source = request.source_description.strip()
        datum = request.vertical_datum.strip()
        if len(source) < 3 or len(datum) < 2:
            raise HTTPException(status_code=400, detail="Evidence source and vertical datum cannot be blank.")
        try:
            return calibrate_gcps(
                store,
                manifest,
                controls=request.controls,
                validation=request.validation,
                source_description=source,
                vertical_datum=datum,
                max_rmse_m=request.max_rmse_m,
            )
        except CalibrationInputError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

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

    frontend_index = active_settings.frontend_dist / "index.html"
    if frontend_index.is_file():
        app.mount(
            "/",
            StaticFiles(directory=str(active_settings.frontend_dist), html=True),
            name="frontend",
        )

    return app


app = create_app()
