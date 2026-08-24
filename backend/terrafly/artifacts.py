from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

from .schemas import Artifact


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _artifact(name: str, path: Path, media_type: str) -> Artifact:
    return Artifact(
        name=name,
        filename=path.name,
        media_type=media_type,
        sha256=sha256_file(path),
        bytes=path.stat().st_size,
    )


def _colourize(relative: np.ndarray) -> np.ndarray:
    stops = np.array(
        [[15, 23, 42], [14, 116, 144], [34, 197, 94], [250, 204, 21], [239, 68, 68]],
        dtype=np.float32,
    )
    scaled = np.clip(relative, 0, 1) * (len(stops) - 1)
    lower = np.floor(scaled).astype(np.int32)
    upper = np.minimum(lower + 1, len(stops) - 1)
    fraction = (scaled - lower)[..., None]
    return (stops[lower] * (1 - fraction) + stops[upper] * fraction).astype(np.uint8)


def write_surface_artifacts(job_dir: Path, relative: np.ndarray, rgb: np.ndarray) -> list[Artifact]:
    if relative.ndim != 2 or relative.shape != rgb.shape[:2]:
        raise ValueError("Surface and texture dimensions must match.")
    if not np.isfinite(relative).all():
        raise ValueError("Surface contains non-finite values.")
    surface_path = job_dir / "relative_surface.npy"
    np.save(surface_path, relative.astype(np.float32), allow_pickle=False)
    preview_path = job_dir / "relative_preview.png"
    Image.fromarray(_colourize(relative), mode="RGB").save(preview_path, optimize=True)
    texture_path = job_dir / "texture.png"
    Image.fromarray(rgb.astype(np.uint8), mode="RGB").save(texture_path, optimize=True)
    height_path = job_dir / "relative_height_16bit.png"
    height_u16 = np.round(np.clip(relative, 0, 1) * 65535).astype(np.uint16)
    Image.fromarray(height_u16).save(height_path)

    max_grid_side = 192
    y_index = np.linspace(0, relative.shape[0] - 1, min(relative.shape[0], max_grid_side)).astype(int)
    x_index = np.linspace(0, relative.shape[1] - 1, min(relative.shape[1], max_grid_side)).astype(int)
    grid = relative[np.ix_(y_index, x_index)].astype(float)
    grid_path = job_dir / "relative_grid.json"
    grid_path.write_text(
        json.dumps({"shape": list(grid.shape), "values": grid.ravel().tolist()}, separators=(",", ":")),
        encoding="utf-8",
    )
    return [
        _artifact("numeric_surface", surface_path, "application/octet-stream"),
        _artifact("preview", preview_path, "image/png"),
        _artifact("texture", texture_path, "image/png"),
        _artifact("height_texture", height_path, "image/png"),
        _artifact("surface_grid", grid_path, "application/json"),
    ]
