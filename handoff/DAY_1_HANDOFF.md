# Day 1 handoff

Date: 2026-08-25 IST

## Outcome

PASS — TerraFly now has a coherent Windows-first upload-to-relative-surface application with a restrained professional workbench UI. The real Depth Anything V2 Small checkpoint works on both CPU and the RTX 5060; the full CUDA API workflow and visible browser workflow are verified.

## Launch

1. Complete the one-time setup with `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1`.
2. Double-click `Start-TerraFly.cmd`.
3. Keep the launcher window open. It waits for readiness and opens `http://127.0.0.1:5173` automatically.

The first real generation needs network access to cache the roughly 99 MB model checkpoint. Later runs can use that project-local cache offline.

## Fast smoke test

Run `.\.venv\Scripts\python.exe -m pytest -q`. Expected result for this milestone: `13 passed`.

## What truly works

- Safe PNG/JPEG/GeoTIFF intake and friendly rejection of corrupt, unsupported, oversized, or unsafe filenames.
- Correct relative versus georeferenced-relative labels and metric refusal without vertical evidence.
- Real pretrained CPU and CUDA inference, with automatic CPU fallback on CUDA OOM.
- Float32 `.npy`, preview, texture, 16-bit height texture, 3D grid, and immutable manifest snapshot exports with hashes.
- Textured Three.js orbit/pan/zoom viewer with reset, wireframe, texture, and display-only exaggeration controls.
- Task-first responsive interface with one primary action, a dominant 3D viewer, a compact result inspector, and no non-working future controls.
- Explicit visible/API warning when single-band thermal/TIR data is repeated into RGB for software compatibility but lacks scientific validation for this optical model.
- Project-local Python environment, project-local model cache, synthetic CC0 offline sample, localhost-only service.
- Team technical guide, file-by-file repository ledger, UI rationale, and exact SAC sample provenance/hashes.

## Next Day 2 entry point

Start with asymmetric raster/texture orientation assertions, then add first-person navigation, point inspection, GLB export, tiled inference, browser automation, and port-conflict recovery. Do not begin calibration until the stable P0 regression stays green.

## Still missing

First-person mode, point comparison, GLB, output GeoTIFF, tiled inference, calibration/evaluation, dependency-bundled portable release, and final judge materials.

## Git/remote

PASS — The project uses the private repository [`khansaudferoz23-cpu/TerraFly`](https://github.com/khansaudferoz23-cpu/TerraFly). Local `main` contains ordinary audited milestone commits; the revised Day 1 source is synchronized before handoff.
