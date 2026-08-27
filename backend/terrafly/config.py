from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


@dataclass(slots=True)
class Settings:
    jobs_root: Path = Path(os.getenv("TERRAFLY_JOBS_ROOT", REPOSITORY_ROOT / "runtime" / "jobs"))
    frontend_dist: Path = Path(
        os.getenv("TERRAFLY_FRONTEND_DIST", REPOSITORY_ROOT / "frontend" / "dist")
    )
    model_adapter: str = os.getenv("TERRAFLY_MODEL_ADAPTER", "depth-anything-v2")
    model_id: str = os.getenv(
        "TERRAFLY_MODEL_ID", "depth-anything/Depth-Anything-V2-Large-hf"
    )
    device: str = os.getenv("TERRAFLY_DEVICE", "auto")
    max_upload_bytes: int = int(os.getenv("TERRAFLY_MAX_UPLOAD_BYTES", str(25 * 1024 * 1024)))
    max_pixels: int = int(os.getenv("TERRAFLY_MAX_PIXELS", "50000000"))
    max_working_bytes: int = int(
        os.getenv("TERRAFLY_MAX_WORKING_BYTES", str(768 * 1024 * 1024))
    )
    tile_trigger_pixels: int = int(os.getenv("TERRAFLY_TILE_TRIGGER_PIXELS", "4194304"))
    tile_size: int = int(os.getenv("TERRAFLY_TILE_SIZE", "1024"))
    tile_overlap: int = int(os.getenv("TERRAFLY_TILE_OVERLAP", "128"))
    max_tiles: int = int(os.getenv("TERRAFLY_MAX_TILES", "256"))
    allow_test_adapter: bool = os.getenv("TERRAFLY_ALLOW_TEST_ADAPTER", "0") == "1"
