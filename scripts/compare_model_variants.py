from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from terrafly.imaging import inspect_image
from terrafly.inference.depth_anything_v2 import DepthAnythingV2Adapter


MODEL_IDS = {
    "small": "depth-anything/Depth-Anything-V2-Small-hf",
    "large": "depth-anything/Depth-Anything-V2-Large-hf",
}


def colourize(relative: np.ndarray) -> np.ndarray:
    stops = np.asarray(
        [[44, 162, 95], [254, 224, 139], [215, 48, 39]],
        dtype=np.float32,
    )
    scaled = np.clip(relative, 0, 1) * (len(stops) - 1)
    lower = np.floor(scaled).astype(np.int32)
    upper = np.minimum(lower + 1, len(stops) - 1)
    fraction = (scaled - lower)[..., None]
    return (stops[lower] * (1 - fraction) + stops[upper] * fraction).astype(np.uint8)


def run_variant(name: str, rgb: np.ndarray, output: Path, device: str) -> dict[str, object]:
    if device == "cuda":
        torch.cuda.empty_cache()
    adapter = DepthAnythingV2Adapter(MODEL_IDS[name], device)
    initialization_started = time.perf_counter()
    adapter.predict(rgb)
    initialization_duration = time.perf_counter() - initialization_started
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    inference_started = time.perf_counter()
    prediction = adapter.predict(rgb)
    inference_duration = time.perf_counter() - inference_started
    relative = prediction.relative_height.astype(np.float32)
    np.save(output / f"{name}_relative.npy", relative, allow_pickle=False)
    Image.fromarray(colourize(relative), mode="RGB").save(output / f"{name}_height_preview.png")
    gradients = np.concatenate(
        [np.abs(np.diff(relative, axis=0)).ravel(), np.abs(np.diff(relative, axis=1)).ravel()]
    )
    return {
        "checkpoint": prediction.model_id,
        "revision": prediction.model_revision,
        "device": prediction.device,
        "initial_load_and_warmup_seconds": round(initialization_duration, 3),
        "steady_state_inference_seconds": round(inference_duration, 3),
        "peak_vram_mb": (
            round(torch.cuda.max_memory_allocated() / (1024**2), 1)
            if device == "cuda"
            else None
        ),
        "shape": list(relative.shape),
        "relative_standard_deviation": float(np.std(relative)),
        "absolute_local_gradient_p90": float(np.percentile(gradients, 90)),
        "output_npy": f"{name}_relative.npy",
        "height_preview": f"{name}_height_preview.png",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Small and Large on one identical scene without inventing an accuracy winner."
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    args = parser.parse_args()

    inspected = inspect_image(args.input.read_bytes(), args.input.name, max_pixels=20_000_000)
    args.output.mkdir(parents=True, exist_ok=True)
    results = {
        name: run_variant(name, inspected.rgb, args.output, args.device)
        for name in ("small", "large")
    }
    small = np.load(args.output / "small_relative.npy", allow_pickle=False)
    large = np.load(args.output / "large_relative.npy", allow_pickle=False)
    report = {
        "schema_version": "1.0",
        "input": str(args.input),
        "input_shape": list(inspected.rgb.shape),
        "variants": results,
        "same_scene_comparison": {
            "pearson_relative_surface": float(np.corrcoef(small.ravel(), large.ravel())[0, 1]),
            "mean_absolute_relative_difference": float(np.mean(np.abs(small - large))),
        },
        "selection": "Large is the TerraFly default required by the critical-fix specification.",
        "scientific_boundary": (
            "These same-scene diagnostics and previews compare behavior and resource cost only. "
            "They cannot identify an accuracy winner without independent aligned height truth."
        ),
    }
    report_path = args.output / "comparison.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
