# Project status

Last updated: 2026-08-25 IST

## Intake result

Greenfield bootstrap. The authenticated GitHub account `khansaudferoz23-cpu` owned only the unrelated private repository `content-portal`; no user-owned TerraFly repository existed. The current workspace contained no source files.

## Implemented baseline

- Single FastAPI + React/Three.js project structure.
- Size, extension, filename, pixel-count, corrupt-image, and decompression-bomb boundaries.
- PNG/JPEG mode normalization and GeoTIFF CRS/transform/NoData inspection.
- Strict `Relative`, `Georeferenced Relative`, and `Metric Calibrated` state vocabulary.
- Real Depth Anything V2 Small adapter with CUDA/CPU selection and CUDA-OOM fallback.
- Test-only deterministic adapter with a normal-run safety interlock.
- Per-job input hash, scientific state, model/device/revision, warnings, calibration refusal, and artifact hashes.
- Numeric `.npy`, colour preview, texture, 16-bit display height texture, and 3D grid exports.
- React upload/progress/results UI and interactive Three.js orbit/pan/zoom viewer.

## Verified Day 1 baseline

- PASS — 13 backend tests, including unsafe/corrupt/oversized inputs and GeoTIFF metadata.
- PASS — frontend scientific-contract component test.
- PASS — strict TypeScript/Vite production build.
- PASS — PyTorch 2.12.1+cu130 CUDA allocation on RTX 5060; no broken Python requirements.
- PASS — real Depth Anything V2 Small CPU inference at revision `5426e4f0f36572d16453bbda7a8389317b1bef99`.
- PASS — real CUDA inference and complete upload-to-six-artifact workflow with verified SHA-256 hashes.
- PASS — browser upload/progress/result/3D render workflow; screenshot captured outside the source repository.
- PASS — npm reported zero production dependency vulnerabilities.
- PASS — source archive extracted to a fresh path containing spaces; 61 manifest hashes and all 13 backend tests passed from the extracted files.

## Not yet complete

First-person navigation, point comparison, calibration, evaluation, GeoTIFF result export, GLB export, tiled inference, dependency-bundled portable release, and Day 2–4 judge packaging.
