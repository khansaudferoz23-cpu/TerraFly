from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image

from terrafly.inference.depth_anything_v2 import DepthAnythingV2Adapter


def main() -> int:
    parser = argparse.ArgumentParser(description="Force and verify real overlapping-tile inference.")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    sample_path = project_root / "sample_data" / "terrafly_synthetic_aerial.png"
    rgb = np.asarray(Image.open(sample_path).convert("RGB"), dtype=np.uint8)
    adapter = DepthAnythingV2Adapter(
        "depth-anything/Depth-Anything-V2-Small-hf",
        args.device,
        tile_trigger_pixels=1,
        tile_size=256,
        tile_overlap=48,
        max_tiles=16,
    )
    started = time.perf_counter()
    prediction = adapter.predict(rgb)
    surface = prediction.relative_height
    assert prediction.metadata["inference_mode"] == "tiled"
    assert prediction.metadata["tile_count"] == 4
    assert surface.shape == rgb.shape[:2]
    assert surface.dtype == np.float32
    assert np.isfinite(surface).all()
    assert 0 <= float(surface.min()) <= float(surface.max()) <= 1
    print(
        json.dumps(
            {
                "result": "PASS",
                "workflow": "real_tiled_inference",
                "duration_seconds": round(time.perf_counter() - started, 3),
                "device": prediction.device,
                "shape": list(surface.shape),
                "metadata": prediction.metadata,
                "output_sha256": hashlib.sha256(surface.tobytes()).hexdigest(),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
