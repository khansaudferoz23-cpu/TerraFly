from __future__ import annotations

import numpy as np
import pytest

from terrafly.config import Settings
from terrafly.inference.deterministic import DeterministicTestAdapter
from terrafly.inference.factory import create_adapter


def test_deterministic_adapter_is_stable_and_finite():
    rgb = np.arange(9 * 13 * 3, dtype=np.uint8).reshape(9, 13, 3)
    first = DeterministicTestAdapter().predict(rgb).relative_height
    second = DeterministicTestAdapter().predict(rgb).relative_height
    np.testing.assert_array_equal(first, second)
    assert first.shape == (9, 13)
    assert np.isfinite(first).all()


def test_test_adapter_cannot_be_enabled_accidentally(tmp_path):
    settings = Settings(jobs_root=tmp_path, model_adapter="deterministic", allow_test_adapter=False)
    with pytest.raises(RuntimeError, match="test-only"):
        create_adapter(settings)
