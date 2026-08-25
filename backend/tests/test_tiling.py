from __future__ import annotations

import numpy as np
import pytest

from terrafly.inference.tiling import predict_tiled, tile_starts


def test_tile_starts_covers_the_last_pixel_without_duplicate_tiles():
    assert tile_starts(20, tile_size=32, overlap=4) == [0]
    assert tile_starts(41, tile_size=40, overlap=8) == [0, 1]
    assert tile_starts(100, tile_size=40, overlap=8) == [0, 32, 60]


def test_tiled_blending_preserves_an_asymmetric_coordinate_field():
    height, width = 73, 101
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    rgb[..., 0] = np.arange(width, dtype=np.uint8)[None, :]
    rgb[..., 1] = np.arange(height, dtype=np.uint8)[:, None]

    def predictor(tile: np.ndarray) -> np.ndarray:
        return tile[..., 0].astype(np.float32) + tile[..., 1].astype(np.float32) * 1000

    result, tile_count = predict_tiled(
        rgb,
        predictor,
        tile_size=40,
        overlap=9,
        max_tiles=20,
    )
    expected = predictor(rgb)
    assert tile_count == 6
    np.testing.assert_allclose(result, expected, rtol=5e-7, atol=2e-2)
    assert result[0, 0] != result[-1, -1]


def test_tiled_inference_refuses_unbounded_tile_counts():
    rgb = np.zeros((100, 100, 3), dtype=np.uint8)
    with pytest.raises(RuntimeError, match="safety limit"):
        predict_tiled(rgb, lambda tile: tile[..., 0], tile_size=32, overlap=8, max_tiles=2)


def test_tiled_blending_aligns_tile_local_scale_and_offset():
    height, width = 72, 96
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    rgb[..., 0] = np.arange(width, dtype=np.uint8)[None, :]
    rgb[..., 1] = np.arange(height, dtype=np.uint8)[:, None]
    expected = rgb[..., 0].astype(np.float32) + rgb[..., 1].astype(np.float32) * 3

    def shifted_predictor(tile: np.ndarray) -> np.ndarray:
        base = tile[..., 0].astype(np.float32) + tile[..., 1].astype(np.float32) * 3
        scale = 1.0 + float(tile[0, 0, 0]) / 200
        offset = float(tile[0, 0, 1]) * 0.7
        return base * scale + offset

    result, tile_count = predict_tiled(
        rgb,
        shifted_predictor,
        tile_size=40,
        overlap=10,
        max_tiles=20,
    )
    assert tile_count == 6
    np.testing.assert_allclose(result, expected, rtol=1e-5, atol=1e-3)
