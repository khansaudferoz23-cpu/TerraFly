from __future__ import annotations

from ..config import Settings
from .base import InferenceAdapter
from .depth_anything_v2 import DepthAnythingV2Adapter
from .deterministic import DeterministicTestAdapter


def create_adapter(settings: Settings) -> InferenceAdapter:
    if settings.model_adapter == "depth-anything-v2":
        return DepthAnythingV2Adapter(
            settings.model_id,
            settings.device,
            tile_trigger_pixels=settings.tile_trigger_pixels,
            tile_size=settings.tile_size,
            tile_overlap=settings.tile_overlap,
            max_tiles=settings.max_tiles,
        )
    if settings.model_adapter == "deterministic":
        if not settings.allow_test_adapter:
            raise RuntimeError("The deterministic adapter is test-only and disabled for normal runs.")
        return DeterministicTestAdapter()
    raise RuntimeError(f"Unknown inference adapter: {settings.model_adapter}")
