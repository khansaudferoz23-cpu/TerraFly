from __future__ import annotations

import hashlib
import json
import traceback
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from rasterio.fill import fillnodata
from rasterio.io import MemoryFile
from rasterio.warp import Resampling, reproject

from .artifacts import _artifact, sha256_file, write_surface_artifacts
from .calibration import _write_metric_grid
from .config import Settings
from .imaging import inspect_image
from .jobs import JobStore
from .schemas import Artifact, JobManifest, JobStatus, ScientificState


class TerrainInputError(ValueError):
    """The supplied image/DEM pair cannot form an honest terrain product."""


@dataclass(slots=True)
class DemInspection:
    metadata: dict[str, Any]
    geospatial: dict[str, Any]


def inspect_source_dem(data: bytes, filename: str, max_pixels: int) -> DemInspection:
    if Path(filename).suffix.lower() not in {".tif", ".tiff"}:
        raise TerrainInputError("Terrain mode requires a single-band DEM GeoTIFF.")
    try:
        with MemoryFile(data) as memory_file, memory_file.open() as dataset:
            if dataset.count != 1:
                raise TerrainInputError("The source DEM must contain exactly one raster band.")
            if dataset.crs is None:
                raise TerrainInputError("The source DEM needs a CRS so it can be aligned to the optical image.")
            if dataset.width < 2 or dataset.height < 2:
                raise TerrainInputError("The source DEM must be at least 2×2 pixels.")
            if dataset.width * dataset.height > max_pixels:
                raise TerrainInputError(f"The source DEM exceeds the {max_pixels}-pixel safety limit.")
            values = dataset.read(1, masked=True).filled(np.nan).astype(np.float64)
            valid = values[np.isfinite(values)]
            if valid.size < 16:
                raise TerrainInputError("The source DEM needs at least 16 finite elevation samples.")
            transform = dataset.transform
            return DemInspection(
                metadata={
                    "filename": filename,
                    "width": dataset.width,
                    "height": dataset.height,
                    "dtype": dataset.dtypes[0],
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "bytes": len(data),
                    "valid_fraction": float(valid.size / values.size),
                    "minimum_m": float(valid.min()),
                    "maximum_m": float(valid.max()),
                    "reported_vertical_units": dataset.units[0] or None,
                },
                geospatial={
                    "crs": dataset.crs.to_string(),
                    "transform": [transform.a, transform.b, transform.c, transform.d, transform.e, transform.f],
                    "bounds": [dataset.bounds.left, dataset.bounds.bottom, dataset.bounds.right, dataset.bounds.top],
                    "pixel_size": [abs(transform.a), abs(transform.e)],
                    "horizontal_units": dataset.crs.linear_units if dataset.crs.is_projected else "degree",
                    "nodata": dataset.nodata,
                },
            )
    except TerrainInputError:
        raise
    except Exception as exc:
        raise TerrainInputError(f"Unreadable source DEM GeoTIFF: {exc}") from exc


def _transform_list(transform: rasterio.Affine) -> list[float]:
    return [transform.a, transform.b, transform.c, transform.d, transform.e, transform.f]


def _align_dem(imagery_path: Path, dem_path: Path) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    with rasterio.open(imagery_path) as imagery, rasterio.open(dem_path) as dem:
        if imagery.crs is None or dem.crs is None:
            raise TerrainInputError("Both terrain inputs need a CRS.")
        source = dem.read(1, masked=True).filled(np.nan).astype(np.float32)
        aligned = np.full((imagery.height, imagery.width), np.nan, dtype=np.float32)
        exact_grid = (
            imagery.crs == dem.crs
            and imagery.width == dem.width
            and imagery.height == dem.height
            and np.allclose(_transform_list(imagery.transform), _transform_list(dem.transform), rtol=0, atol=1e-9)
        )
        if exact_grid:
            aligned[:] = source
            resampling = "none; grids were already identical"
        else:
            reproject(
                source=source,
                destination=aligned,
                src_transform=dem.transform,
                src_crs=dem.crs,
                src_nodata=np.nan,
                dst_transform=imagery.transform,
                dst_crs=imagery.crs,
                dst_nodata=np.nan,
                resampling=Resampling.bilinear,
                init_dest_nodata=True,
            )
            resampling = "bilinear reprojection onto the optical image grid"
        imagery_valid = imagery.dataset_mask() > 0
        aligned[~imagery_valid] = np.nan
        denominator = max(int(imagery_valid.sum()), 1)
        valid_fraction = float(np.count_nonzero(np.isfinite(aligned) & imagery_valid) / denominator)
        if valid_fraction < 0.90:
            raise TerrainInputError(
                f"The DEM covers only {valid_fraction:.1%} of valid optical pixels after alignment; at least 90% is required. "
                "Download both files for the same area of interest."
            )
        valid = aligned[np.isfinite(aligned)]
        if valid.size < 64 or float(np.ptp(valid)) < 1.0:
            raise TerrainInputError("The aligned DEM does not contain enough finite elevation variation.")
        report = {
            "schema_version": "1.0",
            "alignment": resampling,
            "exact_input_grid": exact_grid,
            "source_dem": {
                "crs": dem.crs.to_string(),
                "shape": [dem.height, dem.width],
                "transform": _transform_list(dem.transform),
                "pixel_size": [abs(dem.transform.a), abs(dem.transform.e)],
                "nodata": dem.nodata,
            },
            "output_grid": {
                "crs": imagery.crs.to_string(),
                "shape": [imagery.height, imagery.width],
                "transform": _transform_list(imagery.transform),
                "pixel_size": [abs(imagery.transform.a), abs(imagery.transform.e)],
            },
            "valid_coverage_fraction": valid_fraction,
            "important": "Reprojection/resampling changes the grid but does not improve the DEM's native spatial resolution or accuracy.",
        }
        return aligned, imagery_valid, report


def _display_normalize(metric: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    valid = metric[np.isfinite(metric)].astype(np.float64)
    low, high = np.percentile(valid, (0.5, 99.5)).astype(float)
    if high - low < 1.0:
        low, high = float(valid.min()), float(valid.max())
    source_mask = np.isfinite(metric).astype(np.uint8)
    filled = fillnodata(
        metric.astype(np.float32),
        mask=source_mask,
        max_search_distance=max(metric.shape),
        smoothing_iterations=0,
    ).astype(np.float32)
    filled[~np.isfinite(filled)] = float(np.median(valid))
    relative = np.clip((filled - low) / max(high - low, 1e-6), 0, 1).astype(np.float32)
    return relative, {
        "clip_p005_m": low,
        "clip_p995_m": high,
        "source_minimum_m": float(valid.min()),
        "source_maximum_m": float(valid.max()),
        "nodata_filled_for_display_only": int(np.count_nonzero(~np.isfinite(metric))),
    }


def _write_metric_geotiff(
    output_path: Path,
    imagery_path: Path,
    metric: np.ndarray,
    *,
    source_description: str,
    vertical_datum: str,
) -> None:
    with rasterio.open(imagery_path) as imagery:
        profile = imagery.profile.copy()
        profile.update(driver="GTiff", count=1, dtype="float32", nodata=-9999.0, compress="deflate", predictor=3)
        output = np.where(np.isfinite(metric), metric, -9999.0).astype(np.float32)
        with rasterio.open(output_path, "w", **profile) as target:
            target.write(output, 1)
            target.set_band_description(1, "source DEM elevation aligned to optical grid")
            target.update_tags(
                units="metre",
                vertical_datum=vertical_datum,
                elevation_source=source_description,
                processing="source DEM reprojected/resampled to optical image grid where required",
                scientific_state="Metric Source DEM",
            )


def _write_manifest(store: JobStore, manifest: JobManifest) -> None:
    job_dir = store.job_dir(manifest.job_id)
    manifest.artifacts = [artifact for artifact in manifest.artifacts if artifact.name != "manifest"]
    store.save(manifest)
    path = job_dir / "job_manifest.json"
    path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    manifest.artifacts.append(
        Artifact(
            name="manifest",
            filename=path.name,
            media_type="application/json",
            sha256=sha256_file(path),
            bytes=path.stat().st_size,
        )
    )
    store.save(manifest)


def run_source_dem_job(job_id: str, settings: Settings) -> None:
    store = JobStore(settings.jobs_root)
    manifest = store.get(job_id)
    job_dir = store.job_dir(job_id)
    imagery_path = job_dir / str(manifest.input["stored_filename"])
    dem_path = job_dir / str(manifest.input["dem"]["stored_filename"])
    try:
        manifest.status = JobStatus.RUNNING
        manifest.stage = "validation"
        manifest.progress = 15
        store.save(manifest)
        inspected = inspect_image(imagery_path.read_bytes(), str(manifest.input["filename"]), settings.max_pixels)
        if inspected.geospatial is None:
            raise TerrainInputError("Terrain mode requires a georeferenced optical GeoTIFF.")

        manifest.stage = "preprocessing"
        manifest.progress = 40
        store.save(manifest)
        metric, _, alignment = _align_dem(imagery_path, dem_path)
        relative, normalization = _display_normalize(metric)

        manifest.stage = "meshing"
        manifest.progress = 75
        store.save(manifest)
        source_description = str(manifest.calibration["evidence"]["source_description"])
        vertical_datum = str(manifest.calibration["evidence"]["vertical_datum"])
        reported_vertical_units = manifest.input["dem"].get("reported_vertical_units")
        conversion = {
            "source": "uploaded metric DEM",
            "operation": "robust normalization for display geometry only",
            "metric_values_changed": False,
            "display_normalization": normalization,
        }
        artifacts = write_surface_artifacts(
            job_dir,
            relative,
            inspected.rgb,
            raw_model_output=np.where(np.isfinite(metric), metric, np.nan).astype(np.float32),
            conversion_diagnostics=conversion,
            source_kind="source_dem",
        )
        metric_path = job_dir / "metric_surface.npy"
        np.save(metric_path, metric.astype(np.float32), allow_pickle=False)
        artifacts.append(_artifact("metric_surface", metric_path, "application/octet-stream"))
        metric_grid_path = job_dir / "metric_analysis_grid.json"
        _write_metric_grid(
            metric_grid_path,
            job_dir / "relative_grid.json",
            metric,
            vertical_datum=vertical_datum,
            measurement_role="source DEM elevation samples for 3D point analysis",
        )
        artifacts.append(_artifact("metric_grid", metric_grid_path, "application/json"))
        metric_geotiff_path = job_dir / "metric_surface.tif"
        _write_metric_geotiff(
            metric_geotiff_path,
            imagery_path,
            metric,
            source_description=source_description,
            vertical_datum=vertical_datum,
        )
        artifacts.append(_artifact("metric_geotiff", metric_geotiff_path, "image/tiff"))
        artifacts.append(_artifact("source_dem", dem_path, "image/tiff"))
        report = {
            **alignment,
            "source_description": source_description,
            "vertical_datum": vertical_datum,
            "vertical_units": "metre",
            "source_dem_reported_vertical_units": reported_vertical_units,
            "source_dem_filename": manifest.input["dem"]["filename"],
            "source_dem_sha256": manifest.input["dem"]["sha256"],
            "display_normalization": normalization,
            "accuracy_statement": "TerraFly validated format, coverage, and alignment. Elevation accuracy remains the responsibility of the named DEM source.",
        }
        report_path = job_dir / "terrain_alignment_report.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        artifacts.append(_artifact("terrain_alignment_report", report_path, "application/json"))

        manifest.artifacts = artifacts
        manifest.scientific_state = ScientificState.METRIC_SOURCE_DEM
        manifest.units = "metre"
        manifest.model = {
            "adapter": "source_dem",
            "checkpoint": "uploaded metric DEM",
            "revision": manifest.input["dem"]["sha256"],
            "device": "not applicable",
        }
        manifest.configuration.update(
            {
                "workflow": "source_dem_terrain",
                "inference_mode": "not_used",
                "geometry_source": "uploaded_dem",
                "alignment": alignment,
                "display_normalization": normalization,
                "display_cleanup": "disabled for source DEM terrain",
            }
        )
        manifest.calibration.update(
            {
                "status": "source_dem",
                "metric_output_allowed": True,
                "reason": "Elevation values come directly from the named source DEM; no monocular scale fitting was used.",
                "alignment": alignment,
            }
        )
        terrain_warnings = [
            warning
            for warning in manifest.warnings
            if "does not establish vertical scale" not in warning
        ]
        manifest.warnings = list(
            dict.fromkeys(
                terrain_warnings
                + [
                    "Optical georeferencing locates the texture; vertical values come from the named source DEM.",
                    (
                        f"The source DEM reports its vertical units as {reported_vertical_units}; TerraFly accepted them as metres."
                        if reported_vertical_units
                        else "The source DEM did not include a band-unit tag; its numeric values are treated as metres from the source declaration."
                    ),
                    "Metric heights originate from the uploaded DEM. TerraFly checked alignment but did not independently certify the DEM's accuracy.",
                    "Any vertical exaggeration changes only the display; downloaded metric values remain unchanged.",
                ]
            )
        )
        manifest.status = JobStatus.COMPLETE
        manifest.stage = "complete"
        manifest.progress = 100
        _write_manifest(store, manifest)
    except Exception as exc:
        manifest.status = JobStatus.FAILED
        manifest.stage = "failed"
        manifest.error = str(exc)
        manifest.warnings.append("The terrain job failed without claiming a metric result.")
        manifest.configuration["diagnostic"] = traceback.format_exc(limit=8)
        store.save(manifest)
