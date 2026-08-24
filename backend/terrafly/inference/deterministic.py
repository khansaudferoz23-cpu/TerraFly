from __future__ import annotations

import numpy as np

from .base import Prediction


class DeterministicTestAdapter:
    """Fast deterministic proxy for automated tests only; never scientific/model evidence."""

    model_id = "terrafly/deterministic-test-adapter"

    def predict(self, rgb: np.ndarray) -> Prediction:
        luminance = rgb.astype(np.float32).mean(axis=2) / 255.0
        x_gradient = np.abs(np.diff(luminance, axis=1, prepend=luminance[:, :1]))
        y_gradient = np.abs(np.diff(luminance, axis=0, prepend=luminance[:1, :]))
        proxy = 0.7 * luminance + 0.15 * x_gradient + 0.15 * y_gradient
        minimum = float(proxy.min())
        span = float(proxy.max() - minimum)
        relative = np.zeros_like(proxy, dtype=np.float32) if span < 1e-8 else (proxy - minimum) / span
        return Prediction(
            relative_height=relative.astype(np.float32),
            model_id=self.model_id,
            model_revision="test-only-v1",
            device="cpu",
            warnings=[
                "TEST-ONLY deterministic adapter output: not pretrained inference and not scientific evidence."
            ],
        )

\n