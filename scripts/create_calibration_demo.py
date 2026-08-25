from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.transform import from_origin


def create_input(source: Path, output: Path) -> None:
    rgb = np.asarray(Image.open(source).convert("RGB"), dtype=np.uint8)
    output.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": rgb.shape[0],
        "width": rgb.shape[1],
        "count": 3,
        "dtype": "uint8",
        "crs": "EPSG:32643",
        "transform": from_origin(500000, 2000000, 1, 1),
        "compress": "deflate",
    }
    with rasterio.open(output, "w", **profile) as dataset:
        dataset.write(np.moveaxis(rgb, -1, 0))
        dataset.update_tags(
            evidence_role="synthetic georeferenced software-demo input",
            source_image=source.name,
        )


def write_reference(
    relative: np.ndarray,
    output: Path,
    scale: float,
    offset: float,
    *,
    model_revision: str = "not recorded",
) -> None:
    relative = relative.astype(np.float64)
    reference = offset + scale * relative
    rows, columns = np.indices(relative.shape)
    block_height = max(relative.shape[0] // 4, 1)
    block_width = max(relative.shape[1] // 4, 1)
    held_out = ((rows // block_height) + (columns // block_width)) % 4 == 0
    training_locations = np.flatnonzero(~held_out)
    reference.ravel()[training_locations[:: max(training_locations.size // 12, 1)]] += scale * 4
    output.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": relative.shape[0],
        "width": relative.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": "EPSG:32643",
        "transform": from_origin(500000, 2000000, 1, 1),
        "compress": "deflate",
        "predictor": 3,
    }
    with rasterio.open(output, "w", **profile) as dataset:
        dataset.write(reference.astype(np.float32), 1)
        dataset.set_band_description(1, "synthetic calibration software oracle")
        dataset.update_tags(
            units="metre",
            vertical_datum="Demo benchmark datum",
            evidence_role="synthetic software oracle; not surveyed ground truth",
            model_revision=model_revision,
        )


def create_reference(surface_path: Path, output: Path, scale: float, offset: float) -> None:
    relative = np.load(surface_path, allow_pickle=False)
    write_reference(relative, output, scale, offset)


def create_bundle(
    source: Path,
    input_output: Path,
    reference_output: Path,
    metadata_output: Path,
    device: str,
    scale: float,
    offset: float,
) -> None:
    from terrafly.imaging import inspect_image
    from terrafly.inference.depth_anything_v2 import DepthAnythingV2Adapter

    create_input(source, input_output)
    inspected = inspect_image(input_output.read_bytes(), input_output.name, max_pixels=2_000_000)
    prediction = DepthAnythingV2Adapter(
        "depth-anything/Depth-Anything-V2-Small-hf", device
    ).predict(inspected.rgb)
    write_reference(
        prediction.relative_height,
        reference_output,
        scale,
        offset,
        model_revision=prediction.model_revision or "unknown",
    )
    metadata = {
        "schema_version": "1.0",
        "purpose": "TerraFly calibration software demonstration only",
        "scientific_warning": "The reference was derived from the model result and is not surveyed ground truth or model-accuracy evidence.",
        "source_image": source.name,
        "source_image_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "input_geotiff": input_output.name,
        "input_geotiff_sha256": hashlib.sha256(input_output.read_bytes()).hexdigest(),
        "reference_geotiff": reference_output.name,
        "reference_geotiff_sha256": hashlib.sha256(reference_output.read_bytes()).hexdigest(),
        "model_id": prediction.model_id,
        "model_revision": prediction.model_revision,
        "device_used_to_generate": prediction.device,
        "known_relation": {
            "equation": "synthetic_elevation_m = scale * relative_surface + offset",
            "scale": scale,
            "offset": offset,
        },
        "fit_outliers": "Twelve training-only synthetic outliers are injected to exercise robust fitting.",
    }
    metadata_output.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create reproducible TerraFly Day 3 browser-test fixtures.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    input_parser = subparsers.add_parser("input")
    input_parser.add_argument("--image", type=Path, required=True)
    input_parser.add_argument("--output", type=Path, required=True)
    reference_parser = subparsers.add_parser("reference")
    reference_parser.add_argument("--surface", type=Path, required=True)
    reference_parser.add_argument("--output", type=Path, required=True)
    reference_parser.add_argument("--scale", type=float, default=40.0)
    reference_parser.add_argument("--offset", type=float, default=100.0)
    bundle_parser = subparsers.add_parser("bundle")
    bundle_parser.add_argument("--image", type=Path, required=True)
    bundle_parser.add_argument("--input-output", type=Path, required=True)
    bundle_parser.add_argument("--reference-output", type=Path, required=True)
    bundle_parser.add_argument("--metadata-output", type=Path, required=True)
    bundle_parser.add_argument("--device", choices=("cpu", "cuda"), default="cuda")
    bundle_parser.add_argument("--scale", type=float, default=40.0)
    bundle_parser.add_argument("--offset", type=float, default=100.0)
    args = parser.parse_args()
    if args.command == "input":
        create_input(args.image, args.output)
    elif args.command == "reference":
        create_reference(args.surface, args.output, args.scale, args.offset)
    else:
        create_bundle(
            args.image,
            args.input_output,
            args.reference_output,
            args.metadata_output,
            args.device,
            args.scale,
            args.offset,
        )


if __name__ == "__main__":
    main()
