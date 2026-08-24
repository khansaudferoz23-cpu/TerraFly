from __future__ import annotations

from ..config import Settings
from .base import InferenceAdapter
from .depth_anything_v2 import DepthAnythingV2Adapter
from .deterministic import DeterministicTestAdapter


def create_adapter(settings: Settings) -> InferenceAdapter:
    if settings.model_adapter == "depth-anything-v2":
        return DepthAnythingV2Adapter(settings.model_id, settings.device)
    if settings.model_adapter == "deterministic":
        if not settings.allow_test_adapter:
            raise RuntimeError("The deterministic adapter is test-only and disabled for normal runs.")
        return DeterministicTestAdapter()
    raise RuntimeError(f"Unknown inference adapter: {settings.model_adapter}")

\n