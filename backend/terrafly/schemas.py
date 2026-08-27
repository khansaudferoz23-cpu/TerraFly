from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any

from pydantic import BaseModel, Field


class ScientificState(StrEnum):
    RELATIVE = "Relative"
    GEOREFERENCED_RELATIVE = "Georeferenced Relative"
    METRIC_CALIBRATED = "Metric Calibrated"
    METRIC_SOURCE_DEM = "Metric Source DEM"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class Artifact(BaseModel):
    name: str
    filename: str
    media_type: str
    sha256: str
    bytes: int


class JobManifest(BaseModel):
    schema_version: str = "1.0"
    job_id: str
    status: JobStatus
    stage: str
    progress: int = Field(ge=0, le=100)
    created_at: str
    updated_at: str
    input: dict[str, Any]
    scientific_state: ScientificState
    units: str
    geospatial: dict[str, Any] | None = None
    calibration: dict[str, Any]
    model: dict[str, Any]
    configuration: dict[str, Any]
    warnings: list[str]
    error: str | None = None
    artifacts: list[Artifact] = Field(default_factory=list)


class Capabilities(BaseModel):
    accepted_extensions: list[str]
    max_upload_bytes: int
    max_pixels: int
    max_working_bytes: int
    default_model: str
    tiled_inference: bool = True
    tile_size: int
    tile_overlap: int
    scientific_states: list[str]
    metric_requires_calibration: bool = True
    calibration_methods: list[str] = Field(
        default_factory=lambda: ["aligned_reference_dsm", "ground_control_points"]
    )
    reference_dsm_requires_exact_alignment: bool = True


FiniteNumber = Annotated[float, Field(allow_inf_nan=False)]
PixelCoordinate = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class CalibrationPoint(BaseModel):
    column: PixelCoordinate
    row: PixelCoordinate
    elevation_m: FiniteNumber


class GcpCalibrationRequest(BaseModel):
    source_description: str = Field(min_length=3, max_length=300)
    vertical_datum: str = Field(min_length=2, max_length=100)
    max_rmse_m: float = Field(gt=0, le=100_000, allow_inf_nan=False)
    controls: list[CalibrationPoint] = Field(min_length=6, max_length=500)
    validation: list[CalibrationPoint] = Field(min_length=3, max_length=500)
