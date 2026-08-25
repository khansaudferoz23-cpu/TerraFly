from __future__ import annotations

import hashlib
import json
import struct
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


def _append_aligned(buffer: bytearray, content: bytes) -> tuple[int, int]:
    while len(buffer) % 4:
        buffer.append(0)
    offset = len(buffer)
    buffer.extend(content)
    return offset, len(content)


def _write_glb(path: Path, grid: np.ndarray, colours: np.ndarray) -> None:
    """Write a standards-based GLB with relative Y values and embedded vertex colours."""
    rows, columns = grid.shape
    aspect = rows / columns
    positions = np.empty((rows * columns, 3), dtype="<f4")
    positions[:, 0] = np.tile(np.linspace(-5, 5, columns, dtype=np.float32), rows)
    positions[:, 1] = grid.astype(np.float32).ravel()
    positions[:, 2] = np.repeat(
        np.linspace(-5 * aspect, 5 * aspect, rows, dtype=np.float32), columns
    )
    indices = []
    for row in range(rows - 1):
        for column in range(columns - 1):
            index = row * columns + column
            right = index + 1
            below = index + columns
            indices.extend((index, below, right, right, below, below + 1))
    index_array = np.asarray(indices, dtype="<u4")
    colour_array = np.ascontiguousarray(colours.reshape(-1, 3), dtype=np.uint8)

    binary = bytearray()
    position_offset, position_length = _append_aligned(binary, positions.tobytes())
    colour_offset, colour_length = _append_aligned(binary, colour_array.tobytes())
    index_offset, index_length = _append_aligned(binary, index_array.tobytes())
    while len(binary) % 4:
        binary.append(0)

    document = {
        "asset": {"version": "2.0", "generator": "TerraFly Day 2"},
        "extensionsUsed": ["KHR_materials_unlit"],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": position_offset, "byteLength": position_length, "target": 34962},
            {"buffer": 0, "byteOffset": colour_offset, "byteLength": colour_length, "target": 34962},
            {"buffer": 0, "byteOffset": index_offset, "byteLength": index_length, "target": 34963},
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": int(positions.shape[0]),
                "type": "VEC3",
                "min": positions.min(axis=0).astype(float).tolist(),
                "max": positions.max(axis=0).astype(float).tolist(),
            },
            {
                "bufferView": 1,
                "componentType": 5121,
                "normalized": True,
                "count": int(colour_array.shape[0]),
                "type": "VEC3",
            },
            {
                "bufferView": 2,
                "componentType": 5125,
                "count": int(index_array.size),
                "type": "SCALAR",
                "min": [int(index_array.min())],
                "max": [int(index_array.max())],
            },
        ],
        "materials": [
            {
                "name": "Embedded scene colours",
                "doubleSided": True,
                "pbrMetallicRoughness": {
                    "baseColorFactor": [1, 1, 1, 1],
                    "metallicFactor": 0,
                    "roughnessFactor": 1,
                },
                "extensions": {"KHR_materials_unlit": {}},
            }
        ],
        "meshes": [
            {
                "name": "Relative surface",
                "primitives": [
                    {
                        "attributes": {"POSITION": 0, "COLOR_0": 1},
                        "indices": 2,
                        "material": 0,
                        "mode": 4,
                    }
                ],
                "extras": {
                    "scientific_state": "Relative",
                    "units": "relative_0_1",
                    "vertical_scale_metric": False,
                    "orientation": "row 0 is image top; column 0 is image left",
                },
            }
        ],
        "nodes": [{"mesh": 0, "name": "TerraFly relative surface"}],
        "scenes": [{"nodes": [0]}],
        "scene": 0,
    }
    json_bytes = json.dumps(document, separators=(",", ":")).encode("utf-8")
    json_bytes += b" " * ((-len(json_bytes)) % 4)
    total_length = 12 + 8 + len(json_bytes) + 8 + len(binary)
    glb = (
        struct.pack("<4sII", b"glTF", 2, total_length)
        + struct.pack("<I4s", len(json_bytes), b"JSON")
        + json_bytes
        + struct.pack("<I4s", len(binary), b"BIN\x00")
        + bytes(binary)
    )
    path.write_bytes(glb)


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
    grid_colours = rgb[np.ix_(y_index, x_index)]
    grid_path = job_dir / "relative_grid.json"
    grid_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "shape": list(grid.shape),
                "source_shape": list(relative.shape),
                "row_indices": y_index.tolist(),
                "column_indices": x_index.tolist(),
                "orientation": {"row_zero": "image_top", "column_zero": "image_left"},
                "values": grid.ravel().tolist(),
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    glb_path = job_dir / "relative_surface.glb"
    _write_glb(glb_path, grid.astype(np.float32), grid_colours)
    return [
        _artifact("numeric_surface", surface_path, "application/octet-stream"),
        _artifact("preview", preview_path, "image/png"),
        _artifact("texture", texture_path, "image/png"),
        _artifact("height_texture", height_path, "image/png"),
        _artifact("surface_grid", grid_path, "application/json"),
        _artifact("glb_mesh", glb_path, "model/gltf-binary"),
    ]
