# TerraFly judge Q&A

## What is TerraFly?

A local workbench that estimates a relative surface from one optical image, renders it in 3D, preserves reproducibility evidence, and creates metric elevation files only after independent vertical calibration passes held-out checks.

## Is the first result a DSM?

No. The first result is a relative monocular depth-derived surface normalized to 0–1. A georeferenced input can become a metric DSM-like GeoTIFF only after valid vertical evidence passes.

## Why is one image insufficient for metres?

Projection destroys absolute scale and offset; many differently sized 3D scenes can form similar 2D pixels. A CRS and pixel size add horizontal location/scale, not vertical datum or elevation.

## Which model is real?

`depth-anything/Depth-Anything-V2-Small-hf` at recorded revision `5426e4f0f36572d16453bbda7a8389317b1bef99`. It is a relative monocular depth baseline. The deterministic adapter is test-only, gated by configuration, and visibly labelled.

## How does calibration work?

TerraFly fits `elevation_m = scale × relative + offset` robustly. An aligned raster reserves a spatial checkerboard for evaluation before fitting. GCP mode requires separate controls and checks. Metric output needs positive scale, span, inliers, two-axis coverage, enough held-out data, RMSE below the declared threshold, and R² ≥ 0.50.

## Can the gate be fooled by using training error?

The normal workflow prevents that specific mistake: held-out raster pixels or separate validation GCPs never fit scale/offset. It cannot prove that a dishonest user supplied genuinely independent evidence, so evidence provenance still matters and is recorded.

## Why require an exact reference grid?

Silent reprojection/resampling can hide misregistration and blur edges. Exact CRS, dimensions, and affine transform make the Day 3 contract narrow, reproducible, and auditable.

## What is RMSE versus MAE and bias?

- RMSE penalizes large errors more strongly.
- MAE is the average absolute error.
- Bias shows systematic over/under-estimation.
- P95 absolute error shows a high-error tail.
- R² shows how much held-out variation the affine result explains.

## Why does the viewer remain relative after calibration?

It is a downsampled responsive inspection mesh. Metric `.npy` and GeoTIFF remain full-resolution separate artifacts. This avoids presenting a display mesh or A/B click as surveyed measurement.

## What do the `.npy` files mean?

TerraFly preserves `raw_model_output.npy` before any conversion. `relative_surface.npy` is the normalized float32 0–1 geometry source; `metric_surface.npy` exists only after a calibration pass and contains metres. The related SAC repository’s `.npy` files are TIR super-resolution/colorization arrays, not height data and not required TerraFly runtime files.

## Why did buildings initially look like holes?

The first adapter treated the checkpoint field as ordinary depth and inverted it. Depth Anything V2's relative output behaves like inverse depth/proximity, so that extra inversion reversed local height ordering. The repair declares the convention, preserves raw output, normalizes once, and has a synthetic regression that fails unless a raised roof remains above flat ground in both NumPy and GLB geometry.

## Is the strong whole-image slope fixed?

Not yet, and TerraFly does not hide it. `height_diagnostics.json` fits a reporting-only plane and warns when it dominates the surface. Correcting that bias needs independently evaluated overhead-data logic; silently flattening every scene could remove real terrain slope.

## Why can TIR run if it is not validated?

The pipeline repeats a readable single band into three channels so tensor shapes work. That only proves software compatibility. The model was not validated here for thermal radiance, so TerraFly displays a warning.

## What happens on a large image?

TerraFly plans a bounded overlapping grid, fits positive scale/offset in tile overlaps, feather-blends raw predictions, and globally normalizes once. It refuses excessive tile count and processing-memory estimates.

## What happens if CUDA fails?

The real adapter catches CUDA out-of-memory, clears the cache, moves the model to CPU, retries, and records the device/warning. CPU is slower but honest.

## What security checks exist?

Safe filename rules, accepted extensions/content checks, byte/pixel/memory limits, corrupt/decompression-bomb refusal, opaque validated job IDs, safe artifact lookup, and refusal to delete running jobs.

## Why SHA-256?

It binds each result to exact input/artifact bytes and binds the release to exact committed source. A changed file produces a changed hash.

## Is the bundled near-zero RMSE an accuracy score?

No. The reference is a synthetic oracle derived from the output with a known scale/offset. It verifies implementation, held-out separation, outlier handling, artifacts, and UI. Real accuracy requires independent surveyed truth.

## Did AI build this?

AI accelerated implementation. The team owns the problem framing, decisions, tests, scientific refusal rules, evidence, and presentation. We can explain and reproduce every subsystem rather than hiding AI use.

## Why so many files?

They separate responsibilities so mistakes are testable: validation, model adapter, tiling, calibration, artifacts, API, UI, geometry, setup, verification, and evidence. `FILE_GUIDE.md` gives a purpose for every tracked file; generated caches/jobs/builds remain ignored.

## What is the strongest limitation?

Real-world height accuracy is not established without independent aligned surveyed ground truth. The global affine calibration cannot repair spatially varying prediction errors or domain shift.

## What would you do next?

Acquire licensed paired optical/DSM or nDSM scenes with masks and vertical metadata; split geographically before tiles; establish baselines; evaluate per land-cover/object class; then consider domain-specific fine-tuning only if the data gate passes.
