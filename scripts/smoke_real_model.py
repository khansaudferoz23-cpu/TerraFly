from __future__ import annotations

import argparse
import hashlib
import json
import time

import numpy as np
import torch

from terrafly.inference.depth_anything_v2 import DepthAnythingV2Adapter


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one honest Depth Anything V2 smoke inference.")
    parser.add_argument("--device", choices=("cpu", "cuda"), required=True)
    parser.add_argument(
        "--model-id", default="depth-anything/Depth-Anything-V2-Large-hf"
    )
    args = parser.parse_args()

    height, width = 59, 73
    yy, xx = np.mgrid[0:height, 0:width]
    rgb = np.zeros((height, width, 3), dtype=np.uint8)
    rgb[..., 0] = np.clip(xx * 3, 0, 255)
    rgb[..., 1] = np.clip(yy * 4, 0, 255)
    rgb[..., 2] = np.where((xx < 23) & (yy > 31), 245, 31).astype(np.uint8)

    if args.device == "cuda" and torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
    started = time.perf_counter()
    prediction = DepthAnythingV2Adapter(args.model_id, args.device).predict(rgb)
    duration = time.perf_counter() - started
    peak_vram_mb = (
        round(torch.cuda.max_memory_allocated() / (1024 * 1024), 1)
        if prediction.device == "cuda"
        else None
    )
    surface = prediction.relative_height
    if surface.shape != (height, width):
        raise AssertionError(f"Unexpected output shape: {surface.shape}")
    if surface.dtype != np.float32 or not np.isfinite(surface).all():
        raise AssertionError("Output is not a finite float32 surface.")
    if float(surface.min()) < 0 or float(surface.max()) > 1:
        raise AssertionError("Output escaped its relative 0-1 contract.")
    print(
        json.dumps(
            {
                "result": "PASS",
                "adapter": "real_depth_anything_v2",
                "model_id": prediction.model_id,
                "model_revision": prediction.model_revision,
                "device": prediction.device,
                "input_shape": list(rgb.shape),
                "input_sha256": hashlib.sha256(rgb.tobytes()).hexdigest(),
                "output_shape": list(surface.shape),
                "output_dtype": str(surface.dtype),
                "output_min": float(surface.min()),
                "output_max": float(surface.max()),
                "output_sha256": hashlib.sha256(surface.tobytes()).hexdigest(),
                "duration_seconds": round(duration, 3),
                "peak_vram_mb": peak_vram_mb,
                "gpu": torch.cuda.get_device_name(0) if prediction.device == "cuda" else None,
                "warnings": prediction.warnings,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
