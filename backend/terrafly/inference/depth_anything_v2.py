from __future__ import annotations

import numpy as np
from PIL import Image

from .base import Prediction


class DepthAnythingV2Adapter:
    """Lazy real-model adapter for the Apache-2.0 Depth Anything V2 Small checkpoint."""

    def __init__(self, model_id: str, requested_device: str = "auto") -> None:
        self.model_id = model_id
        self.requested_device = requested_device
        self._model = None
        self._processor = None
        self._torch = None
        self._device = "cpu"

    def _load(self) -> None:
        try:
            import torch
            from transformers import AutoImageProcessor, AutoModelForDepthEstimation
        except ImportError as exc:
            raise RuntimeError(
                "Real inference dependencies are missing. Run scripts/setup.ps1 before generating."
            ) from exc
        if self.requested_device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        elif self.requested_device in {"cpu", "cuda"}:
            device = self.requested_device
        else:
            raise RuntimeError(f"Unsupported inference device: {self.requested_device}")
        if device == "cuda" and not torch.cuda.is_available():
            device = "cpu"
        self._processor = AutoImageProcessor.from_pretrained(self.model_id)
        self._model = AutoModelForDepthEstimation.from_pretrained(self.model_id).to(device).eval()
        self._torch = torch
        self._device = device

    def _predict_on_device(self, rgb: np.ndarray) -> np.ndarray:
        torch = self._torch
        pil_image = Image.fromarray(rgb, mode="RGB")
        inputs = self._processor(images=pil_image, return_tensors="pt")
        inputs = {name: value.to(self._device) for name, value in inputs.items()}
        with torch.inference_mode():
            with torch.autocast(
                device_type="cuda", dtype=torch.float16, enabled=self._device == "cuda"
            ):
                predicted_depth = self._model(**inputs).predicted_depth
            resized = torch.nn.functional.interpolate(
                predicted_depth.unsqueeze(1),
                size=rgb.shape[:2],
                mode="bicubic",
                align_corners=False,
            ).squeeze()
        return resized.float().cpu().numpy()

    def predict(self, rgb: np.ndarray) -> Prediction:
        if self._model is None:
            self._load()
        notes = [
            "Depth Anything V2 produces relative monocular depth, not elevation or height in metres.",
            "The displayed relative surface inverts normalized depth; its scale and offset are arbitrary.",
        ]
        try:
            depth = self._predict_on_device(rgb)
        except RuntimeError as exc:
            if self._device != "cuda" or "out of memory" not in str(exc).lower():
                raise
            self._torch.cuda.empty_cache()
            self._device = "cpu"
            self._model = self._model.to("cpu")
            notes.append("CUDA ran out of memory; TerraFly recovered by retrying on CPU.")
            depth = self._predict_on_device(rgb)
        finite = np.isfinite(depth)
        if not finite.any():
            raise RuntimeError("The model returned no finite depth values.")
        low = float(np.percentile(depth[finite], 1))
        high = float(np.percentile(depth[finite], 99))
        if high <= low:
            relative_height = np.zeros_like(depth, dtype=np.float32)
            notes.append("Model depth had no usable range; the relative surface is flat.")
        else:
            normalized_depth = np.clip((depth - low) / (high - low), 0, 1)
            relative_height = (1.0 - normalized_depth).astype(np.float32)
            relative_height[~finite] = 0.0
        revision = getattr(getattr(self._model, "config", None), "_commit_hash", None)
        return Prediction(
            relative_height=relative_height,
            model_id=self.model_id,
            model_revision=revision,
            device=self._device,
            warnings=notes,
        )
