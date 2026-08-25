from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np


@dataclass(slots=True)
class Prediction:
    raw_model_output: np.ndarray
    relative_height: np.ndarray
    output_convention: str
    model_id: str
    model_revision: str | None
    device: str
    warnings: list[str]
    metadata: dict[str, Any]
    conversion_diagnostics: dict[str, Any]


class InferenceAdapter(Protocol):
    def predict(self, rgb: np.ndarray) -> Prediction: ...
