from __future__ import annotations

import numpy as np
import pytest

from terrafly.config import Settings
from terrafly.inference.conventions import OutputConvention, to_relative_height
from terrafly.inference.deterministic import DeterministicTestAdapter
from terrafly.inference.factory import create_adapter


def test_deterministic_adapter_is_stable_and_finite():
    rgb = np.arange(9 * 13 * 3, dtype=np.uint8).reshape(9, 13, 3)
    first = DeterministicTestAdapter().predict(rgb)
    second = DeterministicTestAdapter().predict(rgb)
    np.testing.assert_array_equal(first.relative_height, second.relative_height)
    np.testing.assert_array_equal(first.raw_model_output, second.raw_model_output)
    assert first.relative_height.shape == (9, 13)
    assert np.isfinite(first.relative_height).all()
    assert first.output_convention == OutputConvention.RELATIVE_HEIGHT.value
    assert first.conversion_diagnostics["normalization"]["applied_count"] == 1


def test_inverse_depth_convention_keeps_a_raised_building_above_ground():
    raw = np.full((16, 16), 0.1, dtype=np.float32)
    raw[4:12, 4:12] = 0.9

    relative, diagnostics = to_relative_height(raw, OutputConvention.INVERSE_DEPTH)

    assert float(relative[4:12, 4:12].mean()) > float(relative[:4, :].mean())
    assert diagnostics["inversion_applied"] is False
    assert diagnostics["normalization"]["applied_count"] == 1


def test_depth_convention_inverts_once_so_a_nearer_building_is_higher():
    raw_depth = np.full((16, 16), 10.0, dtype=np.float32)
    raw_depth[4:12, 4:12] = 2.0

    relative, diagnostics = to_relative_height(raw_depth, OutputConvention.DEPTH)

    assert float(relative[4:12, 4:12].mean()) > float(relative[:4, :].mean())
    assert diagnostics["inversion_applied"] is True
    assert diagnostics["normalization"]["applied_count"] == 1


@pytest.mark.parametrize("convention", list(OutputConvention))
def test_constant_raw_output_has_a_canonical_flat_zero_surface(convention):
    relative, diagnostics = to_relative_height(
        np.full((5, 7), 3.0, dtype=np.float32),
        convention,
    )

    assert np.count_nonzero(relative) == 0
    assert diagnostics["flat_output"] is True


def test_test_adapter_cannot_be_enabled_accidentally(tmp_path):
    settings = Settings(jobs_root=tmp_path, model_adapter="deterministic", allow_test_adapter=False)
    with pytest.raises(RuntimeError, match="test-only"):
        create_adapter(settings)
