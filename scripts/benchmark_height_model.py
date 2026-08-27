from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

from terrafly.evaluation import compute_height_metrics


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_grid(path: Path) -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    if path.suffix.lower() == ".npy":
        values = np.load(path, allow_pickle=False).astype(np.float64)
        return values, np.isfinite(values), {"format": "npy"}
    if path.suffix.lower() not in {".tif", ".tiff"}:
        raise ValueError(f"Unsupported benchmark grid: {path.name}")
    with rasterio.open(path) as dataset:
        if dataset.count != 1:
            raise ValueError(f"Benchmark grid must have one band: {path.name}")
        values = dataset.read(1).astype(np.float64)
        valid = dataset.read_masks(1) > 0
        if dataset.nodata is not None:
            valid &= values != dataset.nodata
        return values, valid & np.isfinite(values), {
            "format": "geotiff",
            "crs": dataset.crs.to_string() if dataset.crs else None,
            "transform": list(dataset.transform)[:6],
            "resolution": list(dataset.res),
            "nodata": dataset.nodata,
        }


def verify_grid_registration(
    prediction_metadata: dict[str, object],
    reference_metadata: dict[str, object],
    *,
    require_geospatial: bool,
) -> str:
    prediction_is_geotiff = prediction_metadata["format"] == "geotiff"
    reference_is_geotiff = reference_metadata["format"] == "geotiff"
    if require_geospatial and not (prediction_is_geotiff and reference_is_geotiff):
        raise ValueError(
            "A real held-out benchmark requires GeoTIFF prediction and reference files "
            "so CRS and affine registration can be verified."
        )
    if prediction_is_geotiff != reference_is_geotiff:
        raise ValueError("Use two GeoTIFF grids or two NPY grids; mixed formats cannot prove registration.")
    if prediction_is_geotiff:
        if prediction_metadata["crs"] != reference_metadata["crs"]:
            raise ValueError("Prediction and reference CRS values do not match.")
        prediction_transform = np.asarray(prediction_metadata["transform"], dtype=np.float64)
        reference_transform = np.asarray(reference_metadata["transform"], dtype=np.float64)
        if not np.allclose(prediction_transform, reference_transform, rtol=0, atol=1e-9):
            raise ValueError("Prediction and reference affine grids do not match.")
        return "exact shape, CRS, and affine grid"
    return "shape only; NPY synthetic software check"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an evidence-backed metric card from an aligned held-out height pair."
    )
    parser.add_argument("--prediction", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--dataset-license", required=True)
    parser.add_argument("--split", required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--checkpoint-revision", required=True)
    parser.add_argument(
        "--reference-kind",
        choices=("lidar_dsm", "surveyed_dsm", "photogrammetric_dsm", "synthetic_oracle"),
        required=True,
    )
    parser.add_argument("--scale", type=float, default=1.0)
    parser.add_argument("--offset", type=float, default=0.0)
    parser.add_argument("--runtime-seconds", type=float)
    parser.add_argument("--peak-vram-mb", type=float)
    parser.add_argument("--peak-ram-mb", type=float)
    parser.add_argument("--landscape-category", action="append", default=[])
    args = parser.parse_args()

    prediction, prediction_valid, prediction_metadata = read_grid(args.prediction)
    reference, reference_valid, reference_metadata = read_grid(args.reference)
    if prediction.shape != reference.shape:
        raise ValueError("Prediction and reference grids are not aligned.")
    real_reference = args.reference_kind != "synthetic_oracle"
    registration = verify_grid_registration(
        prediction_metadata,
        reference_metadata,
        require_geospatial=real_reference,
    )
    metric_prediction = args.scale * prediction + args.offset
    metrics = compute_height_metrics(
        metric_prediction,
        reference,
        prediction_valid & reference_valid,
    )
    card = {
        "schema_version": "1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "REAL_HELD_OUT_BENCHMARK" if real_reference else "SYNTHETIC_SOFTWARE_CHECK_ONLY",
        "model": {
            "checkpoint": args.checkpoint,
            "revision": args.checkpoint_revision,
            "scale": args.scale,
            "offset": args.offset,
        },
        "evidence": {
            "dataset": args.dataset,
            "dataset_license": args.dataset_license,
            "split": args.split,
            "reference_kind": args.reference_kind,
            "prediction": str(args.prediction),
            "reference": str(args.reference),
            "prediction_sha256": sha256_file(args.prediction),
            "reference_sha256": sha256_file(args.reference),
            "registration_check": registration,
            "prediction_grid": prediction_metadata,
            "reference_grid": reference_metadata,
        },
        "metrics": metrics,
        "resources": {
            "runtime_seconds": args.runtime_seconds,
            "peak_vram_mb": args.peak_vram_mb,
            "peak_ram_mb": args.peak_ram_mb,
        },
        "landscape_categories": args.landscape_category,
        "scientific_boundary": (
            "Metrics use aligned held-out real reference pixels."
            if real_reference
            else "Synthetic evidence verifies software only and is not a real model-accuracy claim."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(card, indent=2), encoding="utf-8")
    print(json.dumps(card, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
