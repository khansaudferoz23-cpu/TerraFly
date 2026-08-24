from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ScientificState(StrEnum):
    RELATIVE = "Relative"
    GEOREFERENCED_RELATIVE = "Georeferenced Relative"
    METRIC_CALIBRATED = "Metric Calibrated"


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
    artifacts: list[Artifact] = []


class Capabilities(BaseModel):
    accepted_extensions: list[str]
    max_upload_bytes: int
    max_pixels: int
    default_model: str
    scientific_states: list[str]
    metric_requires_calibration: bool = True
