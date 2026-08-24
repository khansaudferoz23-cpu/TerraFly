from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np


@dataclass(slots=True)
class Prediction:
    relative_height: np.ndarray
    model_id: str
    model_revision: str | None
    device: str
    warnings: list[str]


class InferenceAdapter(Protocol):
    def predict(self, rgb: np.ndarray) -> Prediction: ...

\n