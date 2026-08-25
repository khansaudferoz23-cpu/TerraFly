from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np


@dataclass(slots=True)
class Prediction:
    relative_height: np.ndarray
    model_id: str
    model_revision: str | None
    device: str
    warnings: list[str]
    metadata: dict[str, Any]


class InferenceAdapter(Protocol):
    def predict(self, rgb: np.ndarray) -> Prediction: ...
