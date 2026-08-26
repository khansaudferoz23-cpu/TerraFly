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
            "id": "depth-anything/Depth-Anything-V2-Small-hf",
            "revision_verified": "5426e4f0f36572d16453bbda7a8389317b1bef99",
            "scientific_role": "relative monocular depth only",
            "weights_included": False,
        },
        "tests": {
            "backend": "PASS (32)",
            "frontend": "PASS (7)",
            "frontend_build": "PASS",
            "real_cpu": "PASS",
            "real_cuda": "PASS",
            "real_cuda_api": "PASS",
            "real_tiled_cuda": "PASS (4 tiles)",
            "browser_workflow": "PARTIAL (updated page rendered; final interaction denied by browser auto-review)",
            "single_band_domain_gate": "PASS",
            "responsive_layout": "PASS",
            "glb_contract": "PASS",
            "point_comparison": "PASS",
            "aligned_reference_calibration": "PASS",
            "gcp_control_validation": "PASS",
            "robust_outlier_handling": "PASS",
            "poor_or_misaligned_evidence": "refused",
            "metric_geotiff_contract": "PASS",
            "metric_viewer_grid": "PASS",
            "structure_layer_separation": "PASS",
            "source_nodata_preservation": "PASS",
            "single_server_production_ui": "PASS",
            "real_final_calibration_workflow": "PASS (17 artifact hashes)",
            "release_archives_and_checksums": "STALE after current source change; regenerate before delivery",
            "clean_extracted_path_with_spaces": "PASS on prior release; current source not repackaged",
        },
        "files": files,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
