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


def surface_tilt_diagnostics(relative: np.ndarray) -> dict[str, object]:
    """Report a dominant image-plane trend without altering the numeric surface."""

    rows = np.linspace(0, relative.shape[0] - 1, min(relative.shape[0], 256)).astype(int)
    columns = np.linspace(0, relative.shape[1] - 1, min(relative.shape[1], 256)).astype(int)
    sampled = relative[np.ix_(rows, columns)].astype(np.float64)
    row_axis = np.linspace(-1.0, 1.0, sampled.shape[0], dtype=np.float64)
    column_axis = np.linspace(-1.0, 1.0, sampled.shape[1], dtype=np.float64)
    row_grid, column_grid = np.meshgrid(row_axis, column_axis, indexing="ij")
    values = sampled.ravel()
    design = np.column_stack((np.ones(values.size), row_grid.ravel(), column_grid.ravel()))
    coefficients, *_ = np.linalg.lstsq(design, values, rcond=None)
    fitted = design @ coefficients
    total_variance = float(np.square(values - values.mean()).sum())
    residual_variance = float(np.square(values - fitted).sum())
    plane_fraction = 0.0 if total_variance <= 1e-12 else 1.0 - residual_variance / total_variance

    def correlation(axis: np.ndarray) -> float:
        if float(values.std()) <= 1e-12 or float(axis.std()) <= 1e-12:
            return 0.0
        return float(np.corrcoef(values, axis)[0, 1])

    return {
        "method": "least_squares_plane_on_max_256x256_sample",
        "plane_coefficients": {
            "offset": float(coefficients[0]),
            "normalized_row": float(coefficients[1]),
            "normalized_column": float(coefficients[2]),
        },
        "plane_variance_fraction": float(np.clip(plane_fraction, 0.0, 1.0)),
        "row_correlation": correlation(row_grid.ravel()),
        "column_correlation": correlation(column_grid.ravel()),
        "warning": (
            "A dominant image-plane trend is present; it may be monocular perspective bias, not terrain slope."
            if plane_fraction >= 0.5
            else None
        ),
        "correction_applied": False,
    }


def _convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    unique = sorted(set(points))
    if len(unique) <= 2:
        return unique

    def cross(
        origin: tuple[float, float],
        first: tuple[float, float],
        second: tuple[float, float],
    ) -> float:
        return (first[0] - origin[0]) * (second[1] - origin[1]) - (
            first[1] - origin[1]
        ) * (second[0] - origin[0])

    lower: list[tuple[float, float]] = []
    for point in unique:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper: list[tuple[float, float]] = []
    for point in reversed(unique):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    return lower[:-1] + upper[:-1]


def reconstruct_structure_candidates(grid: np.ndarray) -> dict[str, object]:
    """Find conservative raised components for an optional visual extrusion layer.

    This is not semantic building segmentation. A fitted plane is removed only
    for candidate detection; the source DSM and rendered terrain are untouched.
    """

    rows, columns = grid.shape
    row_axis = np.linspace(-1.0, 1.0, rows, dtype=np.float64)
    column_axis = np.linspace(-1.0, 1.0, columns, dtype=np.float64)
    row_grid, column_grid = np.meshgrid(row_axis, column_axis, indexing="ij")
    values = grid.astype(np.float64).ravel()
    design = np.column_stack((np.ones(values.size), row_grid.ravel(), column_grid.ravel()))
    coefficients, *_ = np.linalg.lstsq(design, values, rcond=None)
    residual = grid.astype(np.float64) - (design @ coefficients).reshape(grid.shape)
    threshold = max(float(np.percentile(residual, 82)), 0.035)
    candidate = residual >= threshold
    padded = np.pad(candidate.astype(np.uint8), 1)
    neighbour_count = np.zeros_like(candidate, dtype=np.uint8)
    for row_offset in range(3):
        for column_offset in range(3):
            neighbour_count += padded[
                row_offset : row_offset + rows,
                column_offset : column_offset + columns,
            ]
    candidate &= neighbour_count >= 4

    visited = np.zeros_like(candidate, dtype=bool)
    minimum_area = max(4, int(round(candidate.size * 0.0002)))
    maximum_area = max(minimum_area, int(round(candidate.size * 0.35)))
    structures: list[dict[str, object]] = []
    for start_row, start_column in zip(*np.nonzero(candidate), strict=True):
        if visited[start_row, start_column]:
            continue
        stack = [(int(start_row), int(start_column))]
        visited[start_row, start_column] = True
        component: list[tuple[int, int]] = []
        while stack:
            row, column = stack.pop()
            component.append((row, column))
            for row_delta in (-1, 0, 1):
                for column_delta in (-1, 0, 1):
                    if row_delta == 0 and column_delta == 0:
                        continue
                    next_row = row + row_delta
                    next_column = column + column_delta
                    if (
                        0 <= next_row < rows
                        and 0 <= next_column < columns
                        and candidate[next_row, next_column]
                        and not visited[next_row, next_column]
                    ):
                        visited[next_row, next_column] = True
                        stack.append((next_row, next_column))
        if not minimum_area <= len(component) <= maximum_area:
            continue

        component_set = set(component)
        ring: set[tuple[int, int]] = set()
        for row, column in component:
            for row_delta in (-1, 0, 1):
                for column_delta in (-1, 0, 1):
                    neighbour = (row + row_delta, column + column_delta)
                    if (
                        0 <= neighbour[0] < rows
                        and 0 <= neighbour[1] < columns
                        and neighbour not in component_set
                    ):
                        ring.add(neighbour)
        roof_relative = float(np.median([grid[row, column] for row, column in component]))
        base_relative = (
            float(np.median([grid[row, column] for row, column in ring]))
            if ring
            else float(np.percentile(grid, 25))
        )
        relative_height = roof_relative - base_relative
        if relative_height < 0.025:
            continue

        footprint_points: list[tuple[float, float]] = []
        for row, column in component:
            for row_corner, column_corner in (
                (row - 0.5, column - 0.5),
                (row - 0.5, column + 0.5),
                (row + 0.5, column - 0.5),
                (row + 0.5, column + 0.5),
            ):
                footprint_points.append(
                    (
                        float(np.clip(column_corner / max(columns - 1, 1), 0, 1)),
                        float(np.clip(row_corner / max(rows - 1, 1), 0, 1)),
                    )
                )
        hull = _convex_hull(footprint_points)
        if len(hull) < 3:
            continue
        if len(hull) > 16:
            hull = [hull[index] for index in np.linspace(0, len(hull) - 1, 16).astype(int)]
        visual_score = float(
            np.clip(
                0.35
                + 0.35 * relative_height / 0.2
                + 0.3 * len(component) / max(minimum_area * 8, 1),
                0,
                0.95,
            )
        )
        structures.append(
            {
                "footprint": [
                    {"x_fraction": point[0], "y_fraction": point[1]} for point in hull
                ],
                "base_relative": float(np.clip(base_relative, 0, 1)),
                "roof_relative": float(np.clip(roof_relative, 0, 1)),
                "relative_height": float(np.clip(relative_height, 0, 1)),
                "pixel_area_on_viewer_grid": len(component),
                "visual_score": visual_score,
            }
        )

    structures.sort(
        key=lambda item: float(item["relative_height"])
        * int(item["pixel_area_on_viewer_grid"]),
        reverse=True,
    )
    structures = structures[:36]
    for index, structure in enumerate(structures, start=1):
        structure["id"] = f"candidate-{index:02d}"
    return {
        "schema_version": "1.0",
        "method": "detrended_relative_height_components_v1",
        "scientific_role": "optional visual reconstruction candidates",
        "source": "relative_grid.json",
        "affects_numeric_dsm": False,
        "candidate_threshold_residual": threshold,
        "minimum_component_area": minimum_area,
        "score_role": "visual ranking heuristic only; not a calibrated probability",
        "warning": (
            "Candidates come from local relative-height contrast, not semantic building labels. "
            "They may include trees or miss low-contrast roofs."
        ),
        "structures": structures,
    }


def write_surface_artifacts(
    job_dir: Path,
    relative: np.ndarray,
    rgb: np.ndarray,
    *,
    raw_model_output: np.ndarray,
    conversion_diagnostics: dict[str, object],
    tilt_diagnostics: dict[str, object] | None = None,
) -> list[Artifact]:
    if relative.ndim != 2 or relative.shape != rgb.shape[:2]:
        raise ValueError("Surface and texture dimensions must match.")
    if not np.isfinite(relative).all():
        raise ValueError("Surface contains non-finite values.")
    raw_model_output = np.asarray(raw_model_output, dtype=np.float32)
    if raw_model_output.ndim != 2 or raw_model_output.shape != relative.shape:
        raise ValueError("Raw model output and relative height dimensions must match.")

    raw_path = job_dir / "raw_model_output.npy"
    np.save(raw_path, raw_model_output, allow_pickle=False)
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
    structure_path = job_dir / "reconstructed_structures.json"
    structure_path.write_text(
        json.dumps(reconstruct_structure_candidates(grid.astype(np.float32)), indent=2),
        encoding="utf-8",
    )
    glb_path = job_dir / "relative_surface.glb"
    _write_glb(glb_path, grid.astype(np.float32), grid_colours)
    diagnostic_path = job_dir / "height_diagnostics.json"
    diagnostic_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "conversion": conversion_diagnostics,
                "raw_model_output": {
                    "filename": raw_path.name,
                    "shape": list(raw_model_output.shape),
                    "dtype": str(raw_model_output.dtype),
                    "preserved_before_height_conversion": True,
                },
                "relative_height": {
                    "filename": surface_path.name,
                    "shape": list(relative.shape),
                    "dtype": "float32",
                    "minimum": float(relative.min()),
                    "maximum": float(relative.max()),
                },
                "geometry": {
                    "source": surface_path.name,
                    "colour_preview_is_geometry_source": False,
                    "mesh_grid_max_side": max_grid_side,
                },
                "global_tilt_indicator": tilt_diagnostics or surface_tilt_diagnostics(relative),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return [
        _artifact("raw_model_output", raw_path, "application/octet-stream"),
        _artifact("numeric_surface", surface_path, "application/octet-stream"),
        _artifact("preview", preview_path, "image/png"),
        _artifact("texture", texture_path, "image/png"),
        _artifact("height_texture", height_path, "image/png"),
        _artifact("surface_grid", grid_path, "application/json"),
        _artifact("structure_layer", structure_path, "application/json"),
        _artifact("glb_mesh", glb_path, "model/gltf-binary"),
        _artifact("height_diagnostics", diagnostic_path, "application/json"),
    ]
