from __future__ import annotations

import hashlib
import io
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff"}


@dataclass(slots=True)
class InspectedImage:
    rgb: np.ndarray
    metadata: dict[str, Any]
    geospatial: dict[str, Any] | None
    warnings: list[str]


def sanitize_filename(filename: str | None) -> str:
    if not filename:
        raise HTTPException(status_code=400, detail="The upload needs a filename.")
    if len(filename) > 180 or "\x00" in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Unsafe upload filename.")
    safe = Path(filename).name
    if safe != filename or Path(safe).suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="Supported formats are PNG, JPG/JPEG, and GeoTIFF.",
        )
    return safe


async def read_upload(upload: UploadFile, max_bytes: int) -> tuple[str, bytes]:
    filename = sanitize_filename(upload.filename)
    chunks: list[bytes] = []
    size = 0
    while True:
        chunk = await upload.read(min(1024 * 1024, max_bytes + 1 - size))
        if not chunk:
            break
        size += len(chunk)
        if size > max_bytes:
            raise HTTPException(status_code=413, detail=f"Upload exceeds the {max_bytes}-byte limit.")
        chunks.append(chunk)
    if size == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    return filename, b"".join(chunks)


def _stretch_to_u8(bands: np.ndarray, valid: np.ndarray | None) -> np.ndarray:
    output = np.zeros_like(bands, dtype=np.uint8)
    for band_index in range(bands.shape[0]):
        band = bands[band_index].astype(np.float32)
        usable = band[np.isfinite(band) & valid] if valid is not None else band[np.isfinite(band)]
        if usable.size == 0:
            continue
        low, high = np.percentile(usable, (2, 98))
        if high <= low:
            high = low + 1.0
        output[band_index] = np.clip((band - low) / (high - low) * 255.0, 0, 255).astype(np.uint8)
    return output


def _inspect_geotiff(data: bytes, max_pixels: int) -> InspectedImage:
    try:
        from rasterio.io import MemoryFile
    except ImportError as exc:  # pragma: no cover - install contract catches this
        raise HTTPException(status_code=503, detail="GeoTIFF support is not installed.") from exc

    try:
        with MemoryFile(data) as memory_file, memory_file.open() as dataset:
            pixels = dataset.width * dataset.height
            if pixels > max_pixels:
                raise HTTPException(status_code=413, detail=f"Image exceeds the {max_pixels}-pixel limit.")
            if dataset.count < 1:
                raise HTTPException(status_code=400, detail="GeoTIFF has no readable raster bands.")
            indexes = list(range(1, min(dataset.count, 3) + 1))
            bands = dataset.read(indexes)
            if bands.shape[0] == 1:
                bands = np.repeat(bands, 3, axis=0)
            elif bands.shape[0] == 2:
                bands = np.concatenate([bands, bands[-1:]], axis=0)
            masks = dataset.read_masks(indexes[0]) > 0
            rgb = np.moveaxis(_stretch_to_u8(bands[:3], masks), 0, -1)
            transform = dataset.transform
            has_georef = dataset.crs is not None
            geospatial = None
            notes: list[str] = []
            if has_georef:
                geospatial = {
                    "crs": dataset.crs.to_string(),
                    "transform": [transform.a, transform.b, transform.c, transform.d, transform.e, transform.f],
                    "bounds": [dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top],
                    "pixel_size": [abs(transform.a), abs(transform.e)],
                    "nodata": dataset.nodata,
                    "ground_units": None,
                    "vertical_datum": None,
                }
                notes.append(
                    "Georeferencing was preserved, but it does not establish vertical scale or elevation in metres."
                )
            else:
                notes.append("This TIFF has no CRS; it is handled as an ordinary relative image.")
            metadata = {
                "width": dataset.width,
                "height": dataset.height,
                "bands": dataset.count,
                "dtype": list(dataset.dtypes),
                "format": dataset.driver,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "has_valid_mask": not bool(np.all(masks)),
            }
            return InspectedImage(rgb=rgb, metadata=metadata, geospatial=geospatial, warnings=notes)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unreadable GeoTIFF: {exc}") from exc


def inspect_image(data: bytes, filename: str, max_pixels: int) -> InspectedImage:
    suffix = Path(filename).suffix.lower()
    if suffix in {".tif", ".tiff"}:
        return _inspect_geotiff(data, max_pixels)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as image:
                if image.format not in {"PNG", "JPEG"}:
                    raise HTTPException(status_code=415, detail="File contents do not match PNG or JPEG.")
                pixels = image.width * image.height
                if pixels > max_pixels:
                    raise HTTPException(status_code=413, detail=f"Image exceeds the {max_pixels}-pixel limit.")
                original_mode = image.mode
                image.load()
                rgb = np.asarray(image.convert("RGB"), dtype=np.uint8).copy()
                metadata = {
                    "width": image.width,
                    "height": image.height,
                    "bands": len(image.getbands()),
                    "mode": original_mode,
                    "format": image.format,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                }
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise HTTPException(status_code=400, detail="The image is corrupt or unsafe to decode.") from exc
    return InspectedImage(rgb=rgb, metadata=metadata, geospatial=None, warnings=[])
