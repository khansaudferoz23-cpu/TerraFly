from __future__ import annotations

from collections.abc import Callable

import numpy as np


def tile_starts(length: int, tile_size: int, overlap: int) -> list[int]:
    if length < 1:
        raise ValueError("Image dimensions must be positive.")
    if tile_size < 32:
        raise ValueError("Tile size must be at least 32 pixels.")
    if overlap < 0 or overlap >= tile_size:
        raise ValueError("Tile overlap must be non-negative and smaller than the tile size.")
    if length <= tile_size:
        return [0]
    stride = tile_size - overlap
    starts = list(range(0, length - tile_size + 1, stride))
    last = length - tile_size
    if starts[-1] != last:
        if len(starts) > 1 and last - starts[-1] < overlap:
            starts[-1] = last
        else:
            starts.append(last)
    return starts


def _axis_weights(length: int, overlap: int, has_before: bool, has_after: bool) -> np.ndarray:
    weights = np.ones(length, dtype=np.float32)
    feather = min(overlap, length // 2)
    if feather == 0:
        return weights
    ramp = np.linspace(1 / (feather + 1), 1.0, feather, dtype=np.float32)
    if has_before:
        weights[:feather] = ramp
    if has_after:
        weights[-feather:] = ramp[::-1]
    return weights


def predict_tiled(
    rgb: np.ndarray,
    predict_tile: Callable[[np.ndarray], np.ndarray],
    *,
    tile_size: int,
    overlap: int,
    max_tiles: int,
) -> tuple[np.ndarray, int]:
    """Align overlapping raw predictions, feather-blend them, then normalize only globally."""
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("Tiled inference expects an RGB image.")
    height, width = rgb.shape[:2]
    y_starts = tile_starts(height, tile_size, overlap)
    x_starts = tile_starts(width, tile_size, overlap)
    tile_count = len(y_starts) * len(x_starts)
    if tile_count > max_tiles:
        raise RuntimeError(
            f"Image requires {tile_count} tiles, above the configured safety limit of {max_tiles}."
        )
    accumulator = np.zeros((height, width), dtype=np.float64)
    weight_sum = np.zeros((height, width), dtype=np.float32)
    for y_index, y_start in enumerate(y_starts):
        y_stop = min(y_start + tile_size, height)
        y_weights = _axis_weights(
            y_stop - y_start,
            overlap,
            has_before=y_index > 0,
            has_after=y_index < len(y_starts) - 1,
        )
        for x_index, x_start in enumerate(x_starts):
            x_stop = min(x_start + tile_size, width)
            raw = np.asarray(predict_tile(rgb[y_start:y_stop, x_start:x_stop]), dtype=np.float32)
            expected_shape = (y_stop - y_start, x_stop - x_start)
            if raw.shape != expected_shape:
                raise RuntimeError(
                    f"Tile predictor returned {raw.shape}; expected {expected_shape}."
                )
            target_accumulator = accumulator[y_start:y_stop, x_start:x_stop]
            target_weights = weight_sum[y_start:y_stop, x_start:x_stop]
            overlap_mask = (target_weights > 0) & np.isfinite(raw)
            if np.count_nonzero(overlap_mask) >= 32:
                source_values = raw[overlap_mask].astype(np.float64)
                target_values = target_accumulator[overlap_mask] / target_weights[overlap_mask]
                if float(np.std(source_values)) > 1e-8:
                    design = np.column_stack((source_values, np.ones_like(source_values)))
                    scale, offset = np.linalg.lstsq(design, target_values, rcond=None)[0]
                    if np.isfinite(scale) and np.isfinite(offset) and 0.05 <= scale <= 20:
                        raw = (raw.astype(np.float64) * scale + offset).astype(np.float32)
            weights = y_weights[:, None] * _axis_weights(
                x_stop - x_start,
                overlap,
                has_before=x_index > 0,
                has_after=x_index < len(x_starts) - 1,
            )[None, :]
            accumulator[y_start:y_stop, x_start:x_stop] += raw * weights
            weight_sum[y_start:y_stop, x_start:x_stop] += weights
    if np.any(weight_sum <= 0):
        raise RuntimeError("Tiled inference left uncovered pixels.")
    return (accumulator / weight_sum).astype(np.float32), tile_count
