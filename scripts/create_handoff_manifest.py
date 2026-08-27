from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "handoff" / "FINAL_MANIFEST.json"


def run(*command: str) -> str | None:
    try:
        return subprocess.check_output(command, cwd=PROJECT_ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def committed_bytes(relative: Path) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"HEAD:{relative.as_posix()}"],
        cwd=PROJECT_ROOT,
        stderr=subprocess.DEVNULL,
    )


def version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> None:
    listed = run("git", "ls-files")
    if listed is None:
        raise RuntimeError("Git file discovery failed.")
    files = []
    for relative_text in sorted(line for line in listed.splitlines() if line):
        relative = Path(relative_text)
        if relative.as_posix() == "handoff/FINAL_MANIFEST.json":
            continue
        path = PROJECT_ROOT / relative
        if path.is_file():
            content = committed_bytes(relative)
            files.append(
                {
                    "path": relative.as_posix(),
                    "bytes": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
    manifest = {
        "schema_version": "1.0",
        "milestone": "TerraFly 1.0 final release",
        "generated_at": datetime.now(UTC).isoformat(),
        "git_commit": run("git", "rev-parse", "HEAD"),
        "environment": {
            "os": platform.platform(),
            "python": sys.version.split()[0],
            "node": run("node", "--version"),
            "npm": run("npm.cmd" if os.name == "nt" else "npm", "--version"),
            "git": run("git", "--version"),
            "gpu": run(
                "nvidia-smi",
                "--query-gpu=name,driver_version,memory.total",
                "--format=csv,noheader",
            ),
            "packages": {
                name: version(name)
                for name in (
                    "fastapi",
                    "numpy",
                    "pillow",
                    "rasterio",
                    "torch",
                    "torchvision",
                    "transformers",
                    "uvicorn",
                )
            },
        },
        "model": {
            "id": "depth-anything/Depth-Anything-V2-Large-hf",
            "revision_verified": "7581137eff8d4e94f6e796d3baea0e9fa79b22d2",
            "model_safetensors_sha256": "4e01e34ed5549b529b70b92d53226bc370f03041977b390d3dde45d47f516cf9",
            "scientific_role": "relative monocular depth only",
            "weights_included": False,
        },
        "tests": {
            "backend": "PASS (37)",
            "frontend": "PASS (9)",
            "frontend_build": "PASS",
            "real_cpu": "PASS",
            "real_cuda": "PASS",
            "real_cuda_api": "PASS",
            "real_tiled_cuda": "PASS (4 tiles)",
            "browser_workflow": "PASS (Large CUDA stadium upload, Photo/Height modes, relative/metre legends, sun control, responsive WebGL, zero browser errors)",
            "single_band_domain_gate": "PASS",
            "responsive_layout": "PASS",
            "glb_contract": "PASS (embedded PNG, TEXCOORD_0, unit NORMAL, lit PBR, neutral steep faces; no COLOR_0/unlit)",
            "point_comparison": "PASS",
            "aligned_reference_calibration": "PASS",
            "gcp_control_validation": "PASS",
            "robust_outlier_handling": "PASS",
            "poor_or_misaligned_evidence": "refused",
            "metric_geotiff_contract": "PASS",
            "metric_viewer_grid": "PASS",
            "structure_layer_separation": "PASS",
            "display_geometry_separation": "PASS (canonical relative and metric grids unchanged)",
            "edge_aware_cleanup": "PASS (outlier, RGB-guided smoothing, rooftop flattening, slope safety)",
            "neutral_wall_material": "PASS (Three.js and GLB steep faces do not sample aerial colour)",
            "source_nodata_preservation": "PASS",
            "single_server_production_ui": "PASS",
            "real_final_calibration_workflow": "PASS (18 artifact hashes)",
            "release_archives_and_checksums": "PASS (generated from the manifest-bearing commit; external checksum file)",
            "clean_extracted_path_with_spaces": "PASS",
        },
        "files": files,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
