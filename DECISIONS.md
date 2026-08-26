# Decisions

## D-001 — Greenfield, one repository

Evidence showed no user-owned TerraFly project. Create one `TerraFly` repository here, with backend and frontend as parts of the same application.

## D-002 — Python 3.12 project environment

The only system Python is 3.14.0, while the Codex runtime provides Python 3.12.13. Use a repository-local `.venv` created from 3.12 and do not modify the global Python installation.

## D-003 — Separate inference truth from test speed

Production defaults to Depth Anything V2 Small through Transformers. Fast tests use `DeterministicTestAdapter`, which requires an explicit test flag and writes a test-only warning into every result.

## D-004 — Initial relative-height assumption (superseded by D-017)

The first implementation treated the checkpoint field as ordinary depth and used `1 - normalized_depth`. Real overhead-scene inspection and a synthetic raised-roof regression showed that assumption reversed local structure. D-017 replaces it; this entry remains so the repair is auditable rather than silently rewritten.

## D-005 — CUDA wheel

Use the official PyTorch 2.12.1 CUDA 13.0 wheel. PyTorch documents CUDA 13.0 as the default current wheel and suitable for Blackwell; the observed Windows driver 610.88 exceeds the documented minimum 580.88. CPU fallback remains mandatory.

## D-006 — Task-first professional interface

Replace the decorative dark-green dashboard style with a neutral analysis workbench. Give the 3D result visual priority, use one restrained accent, collapse provenance, explain every downloadable artifact, implement actual drag/drop, and remove disabled future-feature controls. Preserve real progress and the scientific-state contract.

## D-007 — Related SAC TIR files are domain checks, not height data

Document the IR-colorization repository at its exact commit without copying its unlicensed samples. Its `.npy` arrays are TIR/RGB super-resolution and colorization pairs, not elevation supervision. Allow single-band inputs for robust software handling but attach an explicit TIR/out-of-domain warning to the manifest and UI.

## D-008 — Align tiles before global normalization

Do not normalize each large-image tile independently because monocular depth scale and offset can vary per crop. Fit a positive affine alignment from each overlap to the already blended surface, feather the overlap, then normalize the complete raw surface once. Bound tile count and input-dependent memory before accepting work.

## D-009 — GLB carries colour but never implies metres

Export a dependency-free GLB 2.0 triangle mesh using the same sampled row/column order as the viewer. Embed scene colour as normalized vertex colour and store `relative_0_1`, `vertical_scale_metric=false`, and orientation in mesh extras. A portable 3D file is useful evidence; it does not unlock metric claims.

## D-010 — Point comparison reports samples, not distance

Raycast clicks into the rendered mesh, map UV coordinates back to source-image pixels, and bilinearly sample relative values. Show A/B and their absolute difference only in relative units. Do not label the result as metres, slope, or real-world distance before calibration.

## D-011 — Calibration must be fitted and judged on separate evidence

For an aligned reference DSM, reserve a spatial checkerboard subset before fitting. For GCPs, require separate control and validation lists. Fit one robust positive affine relation, reject outliers, and unlock metric output only when independent validation passes declared RMSE plus fixed R², coverage, span, and inlier gates. Training-fit error is never accepted as validation evidence.

## D-012 — Require exact grids and preserve NoData

Day 3 performs no silent reprojection or resampling. A reference DSM must match CRS, dimensions, and affine transform exactly so interpolation cannot hide alignment errors. Metric outputs inherit the input GeoTIFF grid and mask source NoData pixels. A future resampling workflow must be explicit, configurable, and separately tested.

## D-013 — Keep metric files separate from the relative viewer (extended by D-018)

Calibration changes the exported numeric interpretation, not the evidence used to build the existing 3D viewer. Keep the viewer and A/B comparison in relative units, write metric `.npy`/GeoTIFF as distinct artifacts, and show the vertical datum and held-out diagnostics beside the gate decision.

## D-014 — One production server, one address

Build the React/Three.js interface during setup and let FastAPI serve it after all API routes. Final users launch only `http://127.0.0.1:8000`; Vite remains a development fallback when no build exists. This removes a second terminal/service from the judge workflow without changing the typed API boundary.

## D-015 — Bundle a synthetic oracle, label it precisely

Include a small georeferenced input and aligned synthetic reference so any judge can exercise the complete gate without private data. The reference is generated from the model output with a known affine relation and training-only outliers. It proves alignment, fitting, held-out validation, metadata, and export behavior—not remote-sensing accuracy.

## D-016 — Release source plus prebuilt interface, not third-party caches

The final Windows ZIP contains all tracked source and `frontend/dist`, while Python/npm environments and model weights remain reproducible setup downloads governed by their own licenses. This keeps the release auditable and reasonably sized; it must not be described as fully offline or dependency-bundled.

## D-017 — Make model-output direction explicit and preserve the pre-conversion array

Treat Depth Anything V2 Small's raw relative output as inverse depth/proximity: larger means closer. Under the app's near-nadir overhead assumption, closer maps directly to higher relative surface after one global 2nd–98th percentile normalization; no extra inversion is applied. Preserve `raw_model_output.npy`, make `relative_surface.npy` the sole numeric geometry source, and write `height_diagnostics.json` with the convention, normalization count, geometry source, and a non-correcting global-tilt indicator. Synthetic flat-ground/raised-building tests must prove that both the numeric result and GLB keep the roof above the ground.

## D-018 — Add metric inspection without replacing display geometry

Keep the responsive Three.js mesh normalized for stable rendering, but after a calibration pass write `metric_analysis_grid.json` on the identical sampled row/column grid. A/B clicks may then report calibrated elevation and vertical difference in metres. Derive horizontal distance and slope only when GeoTIFF horizontal units are projected metres; never treat geographic degrees as metres.

## D-019 — Separate Bhuvan-style structures from the scientific DSM

A single DSM heightfield cannot create the clean vertical façades shown by object-based 3D map systems. Detect conservative local raised components on the viewer grid, export convex footprints and relative base/roof values, and render them only in an optional Structures layer. Keep it off by default, mark it non-semantic, and never feed it back into the numeric DSM or calibration metrics.
