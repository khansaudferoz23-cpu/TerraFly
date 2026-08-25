# Day 3 handoff

Date: 2026-08-25 IST

## Outcome

PASS — TerraFly 0.3.0 now has an evidence-driven path from a georeferenced relative surface to separate metric files. Metric output is created only after robust calibration and independent validation pass documented quality gates. Rejected evidence remains auditable and produces no metric artifact.

## Launch

1. Complete one-time setup with `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1` if needed.
2. Double-click `Start-TerraFly.cmd`.
3. Upload a georeferenced GeoTIFF, generate the surface, and use the **Metric calibration** section with an exactly aligned reference DSM.

## Fast verification

Run `.\.venv\Scripts\python.exe -m pytest -q`; expect `25 passed`. In `frontend`, run `npm test`; expect `4 passed`, then `npm run build`.

## What truly works

- Exact CRS/dimensions/affine reference-DSM alignment checks; no silent reprojection.
- Robust global `elevation_m = scale × relative + offset` fit with outlier rejection.
- Spatially held-out raster evaluation and independent control/validation GCP sets.
- Positive scale, span, inlier, coverage, count, declared RMSE, and R² gates.
- Locked, Passed, and Rejected UI states with compact RMSE/MAE/bias/R²/scale/datum evidence.
- Metric float32 `.npy` and GeoTIFF, source NoData preservation, vertical tags, residual GeoTIFF/preview, reference evidence, report, and hashes.
- Real CUDA inference plus visible desktop/mobile browser verification.

## Scientific boundary

The Day 3 reference fixture is derived from the generated relative surface so the expected scale/offset is known. It proves implementation correctness and outlier/gate behavior, not real-world model accuracy. A real claim requires independent surveyed evidence with a known vertical datum and appropriate domain coverage. The GLB, 3D viewer, and A/B points remain relative even after metric export passes.

## Day 4 entry point

Freeze promises; run full regressions; create the requested cookbook, diagrams, judge Q&A, demo script, screenshots, checksums, and portable Windows package; then verify from a fresh path containing spaces.

## Git/remote

The final Day 3 source, handoff evidence, and manifest are synchronized to the private `khansaudferoz23-cpu/TerraFly` repository before handoff.
