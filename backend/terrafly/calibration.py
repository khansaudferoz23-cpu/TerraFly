from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import rasterio
from PIL import Image
from rasterio.io import MemoryFile

from .artifacts import _artifact
from .jobs import JobStore
from .schemas import Artifact, CalibrationPoint, JobManifest, ScientificState


CALIBRATION_ARTIFACTS = {
    "calibration_reference",
    "calibration_report",
    "metric_surface",
    "metric_grid",
    "metric_geotiff",
    "error_geotiff",
    "error_preview",
}


class CalibrationInputError(ValueError):
    """The supplied calibration evidence cannot be compared safely."""


def _finite_metrics(predicted: np.ndarray, observed: np.ndarray) -> dict[str, float | int]:
    predicted = np.asarray(predicted, dtype=np.float64)
    observed = np.asarray(observed, dtype=np.float64)
    valid = np.isfinite(predicted) & np.isfinite(observed)
    if not np.any(valid):
        raise CalibrationInputError("No finite validation observations were supplied.")
    residual = predicted[valid] - observed[valid]
    abs_error = np.abs(residual)
    denominator = float(np.sum((observed[valid] - np.mean(observed[valid])) ** 2))
    r_squared = 1.0 - float(np.sum(residual**2)) / denominator if denominator > 0 else 0.0
    return {
        "count": int(residual.size),
        "rmse_m": float(np.sqrt(np.mean(residual**2))),
        "mae_m": float(np.mean(abs_error)),
        "bias_m": float(np.mean(residual)),
        "median_absolute_error_m": float(np.median(abs_error)),
        "p95_absolute_error_m": float(np.percentile(abs_error, 95)),
        "r_squared": r_squared,
    }


def robust_affine_fit(relative: np.ndarray, elevation: np.ndarray) -> tuple[float, float, np.ndarray]:
    """Fit elevation = scale * relative + offset using a robust, auditable clip/refit loop."""
    x = np.asarray(relative, dtype=np.float64).ravel()
    y = np.asarray(elevation, dtype=np.float64).ravel()
    finite = np.isfinite(x) & np.isfinite(y)
    x = x[finite]
    y = y[finite]
    if x.size < 6:
        raise CalibrationInputError("At least six finite calibration observations are required.")
    x_low, x_high = np.percentile(x, (10, 90))
    if x_high - x_low < 1e-6:
        raise CalibrationInputError("Calibration observations do not span enough relative values.")

    low_values = y[x <= x_low]
    high_values = y[x >= x_high]
    scale = float((np.median(high_values) - np.median(low_values)) / (x_high - x_low))
    offset = float(np.median(y - scale * x))
    inliers = np.ones(x.size, dtype=bool)
    y_span = max(float(np.percentile(y, 95) - np.percentile(y, 5)), 1.0)

    for _ in range(8):
        residual = y - (scale * x + offset)
        centre = float(np.median(residual[inliers]))
        mad = float(np.median(np.abs(residual[inliers] - centre)))
        robust_sigma = 1.4826 * mad
        threshold = max(3.5 * robust_sigma, y_span * 0.001, 1e-5)
        next_inliers = np.abs(residual - centre) <= threshold
        if int(next_inliers.sum()) < 6:
            break
        design = np.column_stack((x[next_inliers], np.ones(int(next_inliers.sum()))))
        scale, offset = np.linalg.lstsq(design, y[next_inliers], rcond=None)[0].astype(float)
        if np.array_equal(next_inliers, inliers):
            inliers = next_inliers
            break
        inliers = next_inliers
    return float(scale), float(offset), inliers


def _sample_bilinear(surface: np.ndarray, points: list[CalibrationPoint]) -> np.ndarray:
    height, width = surface.shape
    values: list[float] = []
    for point in points:
        if point.column > width - 1 or point.row > height - 1:
            raise CalibrationInputError(
                f"Control point ({point.column}, {point.row}) falls outside the {width}×{height} image."
            )
        x0 = int(np.floor(point.column))
        y0 = int(np.floor(point.row))
        x1 = min(x0 + 1, width - 1)
        y1 = min(y0 + 1, height - 1)
        dx = point.column - x0
        dy = point.row - y0
        neighbourhood = surface[np.ix_([y0, y1], [x0, x1])]
        if not np.isfinite(neighbourhood).all():
            raise CalibrationInputError(
                f"Control point ({point.column}, {point.row}) touches a NoData source pixel."
            )
        value = (
            surface[y0, x0] * (1 - dx) * (1 - dy)
            + surface[y0, x1] * dx * (1 - dy)
            + surface[y1, x0] * (1 - dx) * dy
            + surface[y1, x1] * dx * dy
        )
        values.append(float(value))
    return np.asarray(values, dtype=np.float64)


def _source_valid_mask(input_path: Path) -> np.ndarray:
    with rasterio.open(input_path) as source:
        return source.dataset_mask() > 0


def _spatial_coverage(points: list[CalibrationPoint], shape: tuple[int, int]) -> dict[str, float]:
    height, width = shape
    columns = np.asarray([point.column for point in points], dtype=np.float64)
    rows = np.asarray([point.row for point in points], dtype=np.float64)
    return {
        "column_fraction": float((columns.max() - columns.min()) / max(width - 1, 1)),
        "row_fraction": float((rows.max() - rows.min()) / max(height - 1, 1)),
    }


def _gate(
    *,
    scale: float,
    relative_span: float,
    inlier_ratio: float,
    evaluation: dict[str, float | int],
    max_rmse_m: float,
    coverage: dict[str, float],
    minimum_evaluation_count: int,
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not np.isfinite(scale) or scale <= 0:
        failures.append("The fitted vertical scale is not positive.")
    if relative_span < 0.05:
        failures.append("Calibration evidence spans less than 0.05 relative units.")
    if inlier_ratio < 0.75:
        failures.append("Fewer than 75% of calibration observations agree with one affine scale and offset.")
    if int(evaluation["count"]) < minimum_evaluation_count:
        failures.append(f"Held-out evaluation needs at least {minimum_evaluation_count} valid observations.")
    if float(evaluation["rmse_m"]) > max_rmse_m:
        failures.append(
            f"Held-out RMSE {float(evaluation['rmse_m']):.3f} m exceeds the declared {max_rmse_m:.3f} m limit."
        )
    if float(evaluation["r_squared"]) < 0.5:
        failures.append("Held-out R² is below 0.50.")
    if coverage["column_fraction"] < 0.4 or coverage["row_fraction"] < 0.4:
        failures.append("Calibration evidence does not cover at least 40% of both image axes.")
    return not failures, failures


def _remove_old_calibration(job_dir: Path, manifest: JobManifest) -> None:
    retained: list[Artifact] = []
    for artifact in manifest.artifacts:
        if artifact.name in CALIBRATION_ARTIFACTS or artifact.name == "manifest":
            if artifact.name in CALIBRATION_ARTIFACTS:
                path = job_dir / artifact.filename
                if path.is_file():
                    path.unlink()
        else:
            retained.append(artifact)
    manifest.artifacts = retained


def _write_manifest(store: JobStore, manifest: JobManifest) -> None:
    job_dir = store.job_dir(manifest.job_id)
    manifest.artifacts = [artifact for artifact in manifest.artifacts if artifact.name != "manifest"]
    store.save(manifest)
    path = job_dir / "job_manifest.json"
    path.write_text(manifest.model_dump_json(indent=2), encoding="utf-8")
    manifest.artifacts.append(_artifact("manifest", path, "application/json"))
    store.save(manifest)


def _write_metric_geotiff(
    path: Path,
    input_path: Path,
    values: np.ndarray,
    *,
    vertical_datum: str,
    source_description: str,
    kind: str,
) -> None:
    with rasterio.open(input_path) as source:
        profile = source.profile.copy()
        profile.update(
            driver="GTiff",
            count=1,
            dtype="float32",
            nodata=-9999.0,
            compress="deflate",
            predictor=3,
        )
        output = np.where(np.isfinite(values), values, -9999.0).astype(np.float32)
        with rasterio.open(path, "w", **profile) as target:
            target.write(output, 1)
            target.set_band_description(1, kind)
            target.update_tags(
                units="metre",
                vertical_datum=vertical_datum,
                calibration_source=source_description,
                calibration_model="elevation_m = scale * relative_surface + offset",
                scientific_state="Metric Calibrated",
            )


def _write_metric_grid(
    path: Path,
    relative_grid_path: Path,
    metric: np.ndarray,
    *,
    vertical_datum: str,
) -> None:
    """Write metric samples on the exact same grid used by the 3D viewer."""

    relative_grid = json.loads(relative_grid_path.read_text(encoding="utf-8"))
    row_indices = np.asarray(relative_grid["row_indices"], dtype=np.int64)
    column_indices = np.asarray(relative_grid["column_indices"], dtype=np.int64)
    sampled = metric[np.ix_(row_indices, column_indices)].astype(np.float64)
    values: list[float | None] = [
        float(value) if np.isfinite(value) else None for value in sampled.ravel()
    ]
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "shape": list(sampled.shape),
                "source_shape": list(metric.shape),
                "row_indices": row_indices.tolist(),
                "column_indices": column_indices.tolist(),
                "orientation": relative_grid["orientation"],
                "units": "metre",
                "vertical_datum": vertical_datum,
                "measurement_role": "calibrated elevation samples for 3D point analysis",
                "geometry_source": "relative_grid.json",
                "values": values,
            },
            separators=(",", ":"),
            allow_nan=False,
        ),
        encoding="utf-8",
    )


def _error_preview(error: np.ndarray) -> np.ndarray:
    valid = error[np.isfinite(error)]
    limit = max(float(np.percentile(np.abs(valid), 95)), 1e-6)
    scaled = np.clip(error / limit, -1, 1)
    rgb = np.zeros((*error.shape, 3), dtype=np.uint8)
    negative = scaled < 0
    positive = scaled > 0
    rgb[..., :] = 245
    rgb[negative, 0] = (245 * (1 + scaled[negative])).astype(np.uint8)
    rgb[negative, 1] = (245 * (1 + scaled[negative])).astype(np.uint8)
    rgb[positive, 1] = (245 * (1 - scaled[positive])).astype(np.uint8)
    rgb[positive, 2] = (245 * (1 - scaled[positive])).astype(np.uint8)
    rgb[~np.isfinite(error)] = 35
    return rgb


def _finish(
    store: JobStore,
    manifest: JobManifest,
    report: dict[str, Any],
    *,
    accepted: bool,
    metric: np.ndarray | None = None,
    reference: np.ndarray | None = None,
    reference_bytes: bytes | None = None,
) -> JobManifest:
    job_dir = store.job_dir(manifest.job_id)
    _remove_old_calibration(job_dir, manifest)
    if reference_bytes is not None:
        reference_path = job_dir / "calibration_reference.tif"
        reference_path.write_bytes(reference_bytes)
        manifest.artifacts.append(_artifact("calibration_reference", reference_path, "image/tiff"))

    if accepted and metric is not None:
        metric_path = job_dir / "metric_surface.npy"
        np.save(metric_path, metric.astype(np.float32), allow_pickle=False)
        manifest.artifacts.append(_artifact("metric_surface", metric_path, "application/octet-stream"))
        metric_grid_path = job_dir / "metric_analysis_grid.json"
        _write_metric_grid(
            metric_grid_path,
            job_dir / "relative_grid.json",
            metric,
            vertical_datum=str(report["evidence"]["vertical_datum"]),
        )
        manifest.artifacts.append(_artifact("metric_grid", metric_grid_path, "application/json"))
        geotiff_path = job_dir / "metric_surface.tif"
        _write_metric_geotiff(
            geotiff_path,
            job_dir / manifest.input["stored_filename"],
            metric,
            vertical_datum=str(report["evidence"]["vertical_datum"]),
            source_description=str(report["evidence"]["source_description"]),
            kind="calibrated elevation",
        )
        manifest.artifacts.append(_artifact("metric_geotiff", geotiff_path, "image/tiff"))
        if reference is not None:
            error = metric - reference
            error_path = job_dir / "calibration_error.tif"
            _write_metric_geotiff(
                error_path,
                job_dir / manifest.input["stored_filename"],
                error,
                vertical_datum=str(report["evidence"]["vertical_datum"]),
                source_description=str(report["evidence"]["source_description"]),
                kind="calibration residual (candidate minus reference)",
            )
            manifest.artifacts.append(_artifact("error_geotiff", error_path, "image/tiff"))
            preview_path = job_dir / "calibration_error_preview.png"
            Image.fromarray(_error_preview(error), mode="RGB").save(preview_path, optimize=True)
            manifest.artifacts.append(_artifact("error_preview", preview_path, "image/png"))

    report_path = job_dir / "calibration_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    manifest.artifacts.append(_artifact("calibration_report", report_path, "application/json"))
    manifest.calibration = report
    if accepted:
        manifest.scientific_state = ScientificState.METRIC_CALIBRATED
        manifest.units = "metre"
        note = "Metric outputs passed held-out validation; their vertical datum and error metrics are recorded in the calibration report."
    else:
        manifest.scientific_state = ScientificState.GEOREFERENCED_RELATIVE
        manifest.units = "relative_0_1"
        note = "Calibration evidence was evaluated but did not pass; metric output remains locked."
    manifest.warnings = list(dict.fromkeys(manifest.warnings + [note]))
    _write_manifest(store, manifest)
    return manifest


def calibrate_reference(
    store: JobStore,
    manifest: JobManifest,
    reference_bytes: bytes,
    reference_filename: str,
    source_description: str,
    vertical_datum: str,
    max_rmse_m: float,
) -> JobManifest:
    if manifest.geospatial is None:
        raise CalibrationInputError("Metric calibration requires a georeferenced input GeoTIFF.")
    job_dir = store.job_dir(manifest.job_id)
    surface = np.load(job_dir / "relative_surface.npy", allow_pickle=False)
    source_valid = _source_valid_mask(job_dir / manifest.input["stored_filename"])
    try:
        with MemoryFile(reference_bytes) as memory_file, memory_file.open() as dataset:
            if dataset.count != 1:
                raise CalibrationInputError("The reference DSM must contain exactly one raster band.")
            expected_transform = np.asarray(manifest.geospatial["transform"], dtype=float)
            actual_transform = np.asarray(
                [dataset.transform.a, dataset.transform.b, dataset.transform.c, dataset.transform.d, dataset.transform.e, dataset.transform.f]
            )
            if dataset.crs is None or dataset.crs.to_string() != manifest.geospatial["crs"]:
                raise CalibrationInputError("Reference DSM CRS must exactly match the input GeoTIFF CRS.")
            if dataset.width != surface.shape[1] or dataset.height != surface.shape[0]:
                raise CalibrationInputError("Reference DSM width and height must exactly match the input.")
            if not np.allclose(actual_transform, expected_transform, rtol=0, atol=1e-9):
                raise CalibrationInputError("Reference DSM pixel grid and affine transform must exactly match the input.")
            reference = dataset.read(1, masked=True).filled(np.nan).astype(np.float64)
    except CalibrationInputError:
        raise
    except Exception as exc:
        raise CalibrationInputError(f"Unreadable reference GeoTIFF: {exc}") from exc

    valid = source_valid & np.isfinite(reference) & np.isfinite(surface)
    rows, columns = np.indices(surface.shape)
    held_out = ((rows // max(surface.shape[0] // 4, 1)) + (columns // max(surface.shape[1] // 4, 1))) % 4 == 0
    training = valid & ~held_out
    evaluation_mask = valid & held_out
    if int(valid.sum()) < 256 or int(training.sum()) < 128 or int(evaluation_mask.sum()) < 64:
        raise CalibrationInputError("Reference DSM needs at least 256 aligned valid pixels with a usable held-out split.")

    training_indexes = np.flatnonzero(training)
    if training_indexes.size > 50_000:
        training_indexes = training_indexes[np.linspace(0, training_indexes.size - 1, 50_000).astype(int)]
    x_train = surface.ravel()[training_indexes]
    y_train = reference.ravel()[training_indexes]
    scale, offset, inliers = robust_affine_fit(x_train, y_train)
    predicted_eval = scale * surface[evaluation_mask] + offset
    evaluation = _finite_metrics(predicted_eval, reference[evaluation_mask])
    relative_span = float(np.percentile(x_train, 95) - np.percentile(x_train, 5))
    valid_rows, valid_columns = np.nonzero(valid)
    coverage = {
        "column_fraction": float((valid_columns.max() - valid_columns.min()) / max(surface.shape[1] - 1, 1)),
        "row_fraction": float((valid_rows.max() - valid_rows.min()) / max(surface.shape[0] - 1, 1)),
    }
    accepted, failures = _gate(
        scale=scale,
        relative_span=relative_span,
        inlier_ratio=float(inliers.mean()),
        evaluation=evaluation,
        max_rmse_m=max_rmse_m,
        coverage=coverage,
        minimum_evaluation_count=64,
    )
    reason = (
        "Held-out reference DSM evaluation passed every declared quality gate."
        if accepted
        else " ".join(failures)
    )
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "method": "aligned_reference_dsm",
        "status": "passed" if accepted else "rejected",
        "metric_output_allowed": accepted,
        "reason": reason,
        "evidence": {
            "source_description": source_description,
            "vertical_datum": vertical_datum,
            "reference_filename": reference_filename,
            "reference_sha256": hashlib.sha256(reference_bytes).hexdigest(),
            "alignment": "exact CRS, dimensions, and affine transform",
        },
        "fit": {
            "equation": "elevation_m = scale * relative_surface + offset",
            "scale_m_per_relative_unit": scale,
            "offset_m": offset,
            "training_count": int(x_train.size),
            "training_inlier_count": int(inliers.sum()),
            "training_inlier_ratio": float(inliers.mean()),
            "relative_p05_p95_span": relative_span,
        },
        "evaluation": evaluation,
        "quality_gate": {
            "passed": accepted,
            "declared_max_rmse_m": max_rmse_m,
            "minimum_r_squared": 0.5,
            "minimum_inlier_ratio": 0.75,
            "minimum_axis_coverage": 0.4,
            "coverage": coverage,
            "failures": failures,
            "split": "spatial checkerboard; evaluation pixels were never used for fitting",
        },
    }
    metric = np.where(source_valid, scale * surface + offset, np.nan).astype(np.float32)
    return _finish(
        store,
        manifest,
        report,
        accepted=accepted,
        metric=metric if accepted else None,
        reference=reference if accepted else None,
        reference_bytes=reference_bytes,
    )


def calibrate_gcps(
    store: JobStore,
    manifest: JobManifest,
    *,
    controls: list[CalibrationPoint],
    validation: list[CalibrationPoint],
    source_description: str,
    vertical_datum: str,
    max_rmse_m: float,
) -> JobManifest:
    if manifest.geospatial is None:
        raise CalibrationInputError("Metric calibration requires a georeferenced input GeoTIFF.")
    job_dir = store.job_dir(manifest.job_id)
    surface = np.load(job_dir / "relative_surface.npy", allow_pickle=False)
    source_valid = _source_valid_mask(job_dir / manifest.input["stored_filename"])
    masked_surface = np.where(source_valid, surface, np.nan)
    x_train = _sample_bilinear(masked_surface, controls)
    y_train = np.asarray([point.elevation_m for point in controls], dtype=np.float64)
    x_eval = _sample_bilinear(masked_surface, validation)
    y_eval = np.asarray([point.elevation_m for point in validation], dtype=np.float64)
    scale, offset, inliers = robust_affine_fit(x_train, y_train)
    evaluation = _finite_metrics(scale * x_eval + offset, y_eval)
    relative_span = float(np.percentile(x_train, 95) - np.percentile(x_train, 5))
    coverage = _spatial_coverage(controls + validation, surface.shape)
    accepted, failures = _gate(
        scale=scale,
        relative_span=relative_span,
        inlier_ratio=float(inliers.mean()),
        evaluation=evaluation,
        max_rmse_m=max_rmse_m,
        coverage=coverage,
        minimum_evaluation_count=3,
    )
    reason = "Independent validation GCPs passed every declared quality gate." if accepted else " ".join(failures)
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "method": "ground_control_points",
        "status": "passed" if accepted else "rejected",
        "metric_output_allowed": accepted,
        "reason": reason,
        "evidence": {
            "source_description": source_description,
            "vertical_datum": vertical_datum,
            "controls": [point.model_dump() for point in controls],
            "validation": [point.model_dump() for point in validation],
        },
        "fit": {
            "equation": "elevation_m = scale * relative_surface + offset",
            "scale_m_per_relative_unit": scale,
            "offset_m": offset,
            "training_count": len(controls),
            "training_inlier_count": int(inliers.sum()),
            "training_inlier_ratio": float(inliers.mean()),
            "relative_p05_p95_span": relative_span,
        },
        "evaluation": evaluation,
        "quality_gate": {
            "passed": accepted,
            "declared_max_rmse_m": max_rmse_m,
            "minimum_r_squared": 0.5,
            "minimum_inlier_ratio": 0.75,
            "minimum_axis_coverage": 0.4,
            "coverage": coverage,
            "failures": failures,
            "split": "validation points were independent and never used for fitting",
        },
    }
    metric = np.where(source_valid, scale * surface + offset, np.nan).astype(np.float32)
    return _finish(store, manifest, report, accepted=accepted, metric=metric if accepted else None)
