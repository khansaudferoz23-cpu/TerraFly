# Decisions

## D-001 — Greenfield, one repository

Evidence showed no user-owned TerraFly project. Create one `TerraFly` repository here, with backend and frontend as parts of the same application.

## D-002 — Python 3.12 project environment

The only system Python is 3.14.0, while the Codex runtime provides Python 3.12.13. Use a repository-local `.venv` created from 3.12 and do not modify the global Python installation.

## D-003 — Separate inference truth from test speed

Production defaults to Depth Anything V2 Small through Transformers. Fast tests use `DeterministicTestAdapter`, which requires an explicit test flag and writes a test-only warning into every result.

## D-004 — Relative height display convention

The pretrained model predicts relative depth. TerraFly robustly normalizes it and uses `1 - normalized_depth` as a visually intuitive relative surface. This does not create a physical height scale.

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
