from __future__ import annotations

import numpy as np

from .base import Prediction
from .conventions import OutputConvention, to_relative_height


class DeterministicTestAdapter:
    """Fast deterministic proxy for automated tests only; never scientific/model evidence."""

    model_id = "terrafly/deterministic-test-adapter"

    def predict(self, rgb: np.ndarray) -> Prediction:
        luminance = rgb.astype(np.float32).mean(axis=2) / 255.0
        x_gradient = np.abs(np.diff(luminance, axis=1, prepend=luminance[:, :1]))
        y_gradient = np.abs(np.diff(luminance, axis=0, prepend=luminance[:1, :]))
        proxy = 0.7 * luminance + 0.15 * x_gradient + 0.15 * y_gradient
        raw_model_output = proxy.astype(np.float32)
        relative, conversion_diagnostics = to_relative_height(
            raw_model_output,
            OutputConvention.RELATIVE_HEIGHT,
        )
        return Prediction(
            raw_model_output=raw_model_output,
            relative_height=relative.astype(np.float32),
            output_convention=OutputConvention.RELATIVE_HEIGHT.value,
            model_id=self.model_id,
            model_revision="test-only-v1",
            device="cpu",
            warnings=[
                "TEST-ONLY deterministic adapter output: not pretrained inference and not scientific evidence."
            ],
            metadata={
                "inference_mode": "single_pass",
                "tile_count": 1,
                "output_convention": OutputConvention.RELATIVE_HEIGHT.value,
                "normalization": conversion_diagnostics["normalization"],
            },
            conversion_diagnostics=conversion_diagnostics,
        )
