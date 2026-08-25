from __future__ import annotations

from enum import StrEnum
from typing import Any

import numpy as np


class OutputConvention(StrEnum):
    """Meaning of increasing values in an adapter's raw numeric output."""

    INVERSE_DEPTH = "inverse_depth_or_proximity"
    DEPTH = "depth"
    RELATIVE_HEIGHT = "relative_height"


def to_relative_height(
    raw_output: np.ndarray,
    convention: OutputConvention,
    *,
    lower_percentile: float = 2.0,
    upper_percentile: float = 98.0,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Convert one raw model output to finite relative height exactly once.

    Depth Anything V2's relative checkpoint output behaves like inverse depth:
    a larger value means a closer surface. For a near-nadir overhead view, closer
    is mapped to higher. A conventional depth output requires the opposite map.
    """

    raw = np.asarray(raw_output, dtype=np.float32)
    if raw.ndim != 2:
        raise ValueError("Raw model output must be a two-dimensional array.")
    if not 0 <= lower_percentile < upper_percentile <= 100:
        raise ValueError("Normalization percentiles must satisfy 0 <= low < high <= 100.")

    finite = np.isfinite(raw)
    if not finite.any():
        raise RuntimeError("The model returned no finite values.")
    finite_values = raw[finite]
    low = float(np.percentile(finite_values, lower_percentile))
    high = float(np.percentile(finite_values, upper_percentile))

    if high <= low:
        normalized = np.zeros_like(raw, dtype=np.float32)
        flat_output = True
    else:
        normalized = np.clip((raw - low) / (high - low), 0.0, 1.0).astype(np.float32)
        flat_output = False
    normalized[~finite] = 0.0

    if flat_output:
        relative_height = np.zeros_like(normalized, dtype=np.float32)
        mapping = "constant raw output -> flat zero-relative surface"
        inversion_applied = convention is OutputConvention.DEPTH
    elif convention is OutputConvention.DEPTH:
        relative_height = 1.0 - normalized
        mapping = "smaller raw depth -> higher relative surface"
        inversion_applied = True
    elif convention in {OutputConvention.INVERSE_DEPTH, OutputConvention.RELATIVE_HEIGHT}:
        relative_height = normalized
        mapping = "larger raw value -> higher relative surface"
        inversion_applied = False
    else:  # defensive guard for callers crossing a non-typed boundary
        raise ValueError(f"Unsupported output convention: {convention}")

    relative_height = relative_height.astype(np.float32, copy=False)
    relative_height[~finite] = 0.0
    diagnostics: dict[str, Any] = {
        "schema_version": "1.0",
        "output_convention": convention.value,
        "mapping": mapping,
        "normalization": {
            "method": "global_percentile_clip_then_unit_scale",
            "lower_percentile": lower_percentile,
            "upper_percentile": upper_percentile,
            "lower_value": low,
            "upper_value": high,
            "applied_count": 1,
        },
        "inversion_applied": inversion_applied,
        "flat_output": flat_output,
        "raw_statistics": {
            "minimum": float(finite_values.min()),
            "median": float(np.median(finite_values)),
            "maximum": float(finite_values.max()),
            "finite_fraction": float(finite.mean()),
        },
        "relative_height_statistics": {
            "minimum": float(relative_height.min()),
            "maximum": float(relative_height.max()),
        },
    }
    return relative_height, diagnostics
