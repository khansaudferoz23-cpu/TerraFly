# Day 2 handoff

Date: 2026-08-25 IST

## Outcome

PASS — TerraFly 0.2.0 now has a robust relative-surface inspection workflow: bounded large-image inference, orbit and first-person navigation, A/B point comparison, and a real portable GLB mesh. Every visible feature works and remains explicitly non-metric.

## Launch

1. Complete one-time setup with `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1` if needed.
2. Double-click `Start-TerraFly.cmd`.
3. Keep the launcher window open. It reuses healthy TerraFly services, detects conflicting ports, saves readable logs under `runtime\logs`, and opens the app automatically.

## Fast verification

Run `.\.venv\Scripts\python.exe -m pytest -q`; expect `20 passed`. In `frontend`, run `npm test`; expect `4 passed`.

## What truly works

- Single-pass or bounded overlapping-tile Depth Anything V2 inference with CUDA/CPU recovery.
- Positive affine tile overlap alignment, feather blending, one global normalization, tile-count refusal, and input working-memory refusal.
- Shared top/left orientation contract across numeric grid, texture, frontend geometry, point samples, and GLB vertex colours.
- Orbit navigation plus pointer-lock first-person free flight with W/A/S/D, Q/E, and Escape.
- Two raycast-selected points with source pixel coordinates, relative values, and relative absolute difference.
- Valid GLB 2.0 triangle mesh with embedded scene colours and explicit `relative_0_1`/non-metric metadata.
- Completed-job cleanup and safer Windows restart diagnostics.
- Professional responsive UI tested at desktop and 390×844.

## Scientific boundary

Point comparison is not measurement in metres. The GLB is not a metric terrain model. Tiling is an engineering strategy whose scientific accuracy still needs compatible ground truth. Metric GeoTIFF remains locked.

## Day 3 entry point

Define a calibration evidence schema first. Then build synthetic georeferenced reference/GCP fixtures, alignment checks, robust affine vertical calibration with diagnostics/outlier handling, evaluation metrics/masks/error maps, and only then a strict metric export gate.

## Git/remote

The final Day 2 source, evidence manifest, and ordinary commits are synchronized to the private `khansaudferoz23-cpu/TerraFly` repository before handoff.
