from __future__ import annotations

import numpy as np
import pytest

from terrafly.evaluation import compute_height_metrics
from scripts.benchmark_height_model import verify_grid_registration


def test_height_metrics_match_hand_calculation_and_mask_invalid_pixels():
    prediction = np.array([[1.0, 2.0], [4.0, np.nan]])
    reference = np.array([[1.0, 3.0], [5.0, 99.0]])
    metrics = compute_height_metrics(prediction, reference)
    assert metrics["valid_pixel_count"] == 3
    assert metrics["rmse_m"] == pytest.approx(np.sqrt(2 / 3))
    assert metrics["mae_m"] == pytest.approx(2 / 3)
    assert metrics["bias_m"] == pytest.approx(-2 / 3)
    assert metrics["pearson_correlation"] == pytest.approx(
        np.corrcoef([1.0, 2.0, 4.0], [1.0, 3.0, 5.0])[0, 1]
    )


def test_height_metrics_apply_explicit_nodata_mask():
    prediction = np.array([[10.0, 20.0], [30.0, 40.0]])
    reference = np.array([[11.0, 19.0], [300.0, 39.0]])
    mask = np.array([[True, True], [False, True]])
    metrics = compute_height_metrics(prediction, reference, mask)
    assert metrics["valid_pixel_count"] == 3
    assert metrics["rmse_m"] == pytest.approx(1.0)
    assert metrics["mae_m"] == pytest.approx(1.0)


def test_height_metrics_refuse_misaligned_or_insufficient_evidence():
    with pytest.raises(ValueError, match="aligned"):
        compute_height_metrics(np.zeros((2, 2)), np.zeros((2, 3)))
    with pytest.raises(ValueError, match="At least two"):
        compute_height_metrics(np.array([[1.0]]), np.array([[1.0]]))


def test_real_benchmark_requires_matching_geospatial_grids():
    prediction = {
        "format": "geotiff",
        "crs": "EPSG:32643",
        "transform": [1.0, 0.0, 500000.0, 0.0, -1.0, 2000000.0],
    }
    reference = dict(prediction)
    assert verify_grid_registration(
        prediction,
        reference,
        require_geospatial=True,
    ) == "exact shape, CRS, and affine grid"

    shifted = dict(reference, transform=[1.0, 0.0, 500001.0, 0.0, -1.0, 2000000.0])
    with pytest.raises(ValueError, match="affine"):
        verify_grid_registration(prediction, shifted, require_geospatial=True)
    with pytest.raises(ValueError, match="requires GeoTIFF"):
        verify_grid_registration(
            {"format": "npy"},
            {"format": "npy"},
            require_geospatial=True,
        )
