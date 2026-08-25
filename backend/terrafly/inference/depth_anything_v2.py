from __future__ import annotations

import numpy as np
from PIL import Image

from .base import Prediction
from .conventions import OutputConvention, to_relative_height
from .tiling import predict_tiled


class DepthAnythingV2Adapter:
    """Lazy real-model adapter for the Apache-2.0 Depth Anything V2 Small checkpoint."""

    def __init__(
        self,
        model_id: str,
        requested_device: str = "auto",
        *,
        tile_trigger_pixels: int = 4_194_304,
        tile_size: int = 1024,
        tile_overlap: int = 128,
        max_tiles: int = 256,
    ) -> None:
        self.model_id = model_id
        self.requested_device = requested_device
        self._model = None
        self._processor = None
        self._torch = None
        self._device = "cpu"
        self.tile_trigger_pixels = tile_trigger_pixels
        self.tile_size = tile_size
        self.tile_overlap = tile_overlap
        self.max_tiles = max_tiles

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
        try:
            processor = AutoImageProcessor.from_pretrained(
                self.model_id, local_files_only=True
            )
            model = AutoModelForDepthEstimation.from_pretrained(
                self.model_id, local_files_only=True
            )
        except OSError:
            # A prepared demonstration machine must not pause for network probes.
            # On the first machine setup, fall back to the normal authenticated
            # Hugging Face download and let its cache serve later runs.
            processor = AutoImageProcessor.from_pretrained(self.model_id)
            model = AutoModelForDepthEstimation.from_pretrained(self.model_id)
        self._processor = processor
        self._model = model.to(device).eval()
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
            "The checkpoint output is treated as inverse depth/proximity: larger raw values are closer.",
            "For a near-nadir scene, closer is mapped directly to higher relative surface; no extra inversion is applied.",
            "Perspective-driven global tilt can remain and must not be interpreted as terrain slope.",
        ]
        try:
            if rgb.shape[0] * rgb.shape[1] > self.tile_trigger_pixels:
                depth, tile_count = predict_tiled(
                    rgb,
                    self._predict_on_device,
                    tile_size=self.tile_size,
                    overlap=self.tile_overlap,
                    max_tiles=self.max_tiles,
                )
                inference_mode = "tiled"
                notes.append(
                    f"Large image inference used {tile_count} overlapping tiles; raw depth was feather-blended before global normalization."
                )
            else:
                depth = self._predict_on_device(rgb)
                tile_count = 1
                inference_mode = "single_pass"
        except RuntimeError as exc:
            if self._device != "cuda" or "out of memory" not in str(exc).lower():
                raise
            self._torch.cuda.empty_cache()
            self._device = "cpu"
            self._model = self._model.to("cpu")
            notes.append("CUDA ran out of memory; TerraFly recovered by retrying on CPU.")
            if rgb.shape[0] * rgb.shape[1] > self.tile_trigger_pixels:
                depth, tile_count = predict_tiled(
                    rgb,
                    self._predict_on_device,
                    tile_size=self.tile_size,
                    overlap=self.tile_overlap,
                    max_tiles=self.max_tiles,
                )
                inference_mode = "tiled"
            else:
                depth = self._predict_on_device(rgb)
                tile_count = 1
                inference_mode = "single_pass"
        raw_model_output = np.asarray(depth, dtype=np.float32)
        relative_height, conversion_diagnostics = to_relative_height(
            raw_model_output,
            OutputConvention.INVERSE_DEPTH,
        )
        if conversion_diagnostics["flat_output"]:
            notes.append("Model output had no usable range; the relative surface is flat.")
        revision = getattr(getattr(self._model, "config", None), "_commit_hash", None)
        return Prediction(
            raw_model_output=raw_model_output,
            relative_height=relative_height,
            output_convention=OutputConvention.INVERSE_DEPTH.value,
            model_id=self.model_id,
            model_revision=revision,
            device=self._device,
            warnings=notes,
            metadata={
                "inference_mode": inference_mode,
                "tile_count": tile_count,
                "tile_size": self.tile_size if inference_mode == "tiled" else None,
                "tile_overlap": self.tile_overlap if inference_mode == "tiled" else None,
                "output_convention": OutputConvention.INVERSE_DEPTH.value,
                "normalization": conversion_diagnostics["normalization"],
            },
            conversion_diagnostics=conversion_diagnostics,
        )
