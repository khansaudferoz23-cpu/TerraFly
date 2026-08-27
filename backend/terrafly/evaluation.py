from __future__ import annotations

import math
from typing import Any

import numpy as np


def compute_height_metrics(
    prediction_m: np.ndarray,
    reference_m: np.ndarray,
    valid_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    """Compute real height metrics only where prediction and reference are valid."""

    prediction = np.asarray(prediction_m, dtype=np.float64)
    reference = np.asarray(reference_m, dtype=np.float64)
    if prediction.shape != reference.shape or prediction.ndim != 2:
        raise ValueError("Prediction and reference must be aligned two-dimensional arrays.")
    valid = np.isfinite(prediction) & np.isfinite(reference)
    if valid_mask is not None:
        mask = np.asarray(valid_mask, dtype=bool)
        if mask.shape != prediction.shape:
            raise ValueError("Validity mask must match the prediction grid.")
        valid &= mask
    count = int(valid.sum())
    if count < 2:
        raise ValueError("At least two valid aligned pixels are required for evaluation.")
    predicted = prediction[valid]
    observed = reference[valid]
    residual = predicted - observed
    rmse = float(np.sqrt(np.mean(np.square(residual))))
    mae = float(np.mean(np.abs(residual)))
    bias = float(np.mean(residual))
    prediction_std = float(np.std(predicted))
    reference_std = float(np.std(observed))
    pearson = (
        float(np.corrcoef(predicted, observed)[0, 1])
        if prediction_std > 0 and reference_std > 0
        else None
    )
    if pearson is not None and not math.isfinite(pearson):
        pearson = None
    return {
        "valid_pixel_count": count,
        "rmse_m": rmse,
        "mae_m": mae,
        "bias_m": bias,
        "pearson_correlation": pearson,
    }
