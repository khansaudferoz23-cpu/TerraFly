from __future__ import annotations

import argparse
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


def create_reference(surface_path: Path, output: Path, scale: float, offset: float) -> None:
    relative = np.load(surface_path, allow_pickle=False).astype(np.float64)
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
        dataset.set_band_description(1, "independent reference elevation")
        dataset.update_tags(units="metre", vertical_datum="Demo benchmark datum")


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
    args = parser.parse_args()
    if args.command == "input":
        create_input(args.image, args.output)
    else:
        create_reference(args.surface, args.output, args.scale, args.offset)


if __name__ == "__main__":
    main()
