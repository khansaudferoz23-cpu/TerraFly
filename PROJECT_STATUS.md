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
- Task-first neutral UI with working drag/drop, dominant 3D workspace, responsive result inspector, loading/error states, and explained evidence downloads.
- Explicit single-band/TIR domain warning in the API manifest and visible result UI.
- Team technical guide, file-by-file repository ledger, UI rationale, and exact related-SAC sample audit.
- Overlapping tiled inference with bounded tile count, overlap affine alignment, feather blending, global normalization, and recorded strategy metadata.
- Input-dependent processing-memory budget enforced before job acceptance.
- Asymmetric orientation contract shared by viewer grid, image texture, point sampling, and GLB vertex colours.
- Orbit and pointer-lock first-person navigation plus two-point relative comparison with source pixel coordinates.
- Standards-based GLB 2.0 mesh export with embedded vertex colours and explicit non-metric metadata.
- Completed-result deletion and launcher reuse/port/log diagnostics without killing unknown processes.
- Exact-grid aligned reference-DSM calibration with robust affine outlier handling and spatially held-out evaluation.
- Ground-control calibration with separate control and validation point sets, bilinear relative sampling, and coverage gates.
- Strict positive-scale, relative-span, inlier-ratio, axis-coverage, RMSE, and R² gate before metric state/output exists.
- Source NoData preservation, calibrated float32 `.npy`/GeoTIFF, residual GeoTIFF/preview, retained reference evidence, and calibration report hashes.
- Professional calibration panel with explicit Locked/Passed/Rejected states and dynamically truthful evidence downloads.

## Verified Day 1 baseline

- PASS — 13 backend tests, including unsafe/corrupt/oversized inputs and GeoTIFF metadata.
- PASS — 2 frontend tests covering the scientific contract and real file-selection action.
- PASS — strict TypeScript/Vite production build.
- PASS — PyTorch 2.12.1+cu130 CUDA allocation on RTX 5060; no broken Python requirements.
- PASS — real Depth Anything V2 Small CPU inference at revision `5426e4f0f36572d16453bbda7a8389317b1bef99`.
- PASS — real CUDA inference and complete upload-to-six-artifact workflow with verified SHA-256 hashes.
- PASS — browser upload/progress/result/3D render workflow using the downloaded 512×512 TIR preview; domain warning and screenshots captured outside the source repository.
- PASS — responsive browser check at 390×844 with no horizontal page overflow.
- PASS — npm reported zero production dependency vulnerabilities.
- PASS — the Windows launcher parses cleanly, waits for readiness, and opens the app automatically.
- PASS — private GitHub repository exists at `khansaudferoz23-cpu/TerraFly`; revised Day 1 source is prepared for synchronization.
- PASS — revised source archive extracted to a fresh path containing spaces; 64 manifest hashes and all 13 backend tests passed from the extracted files.

## Not yet complete

Real-world accuracy evaluation against an independently surveyed dataset, dependency-bundled portable release, final cookbook/judge materials, and Day 4 packaging.

## Verified Day 2 baseline

- PASS — 20 backend tests and 4 frontend tests, including tiling, memory refusal, GLB structure/colour orientation, point sampling, cleanup, and asymmetric corner mapping.
- PASS — real four-tile CUDA inference in 21.734 seconds with finite 320×480 float32 output.
- PASS — real CUDA upload-to-seven-artifact API workflow in 5.101 seconds; every artifact hash matched.
- PASS — browser RGB upload, real inference, WebGL render, orbit/first-person switching, two-point comparison, GLB link, and completed-result presentation.
- PASS — 390×844 responsive QA with page width and canvas width contained; no new browser errors after the canvas repair.
- PASS — PowerShell launcher syntax, explicit occupied-port diagnostics, readable service logs, reuse of an already-running TerraFly service, and a persistent CMD error message.
- PASS — Day 2 source archive extracted to a fresh path containing spaces; 72 manifest hashes and all 20 backend tests passed from the extracted files.

## Verified Day 3 baseline

- PASS — 25 backend tests, including exact reference-grid checks, robust outlier handling, poor-evidence rejection, independent GCP validation, source NoData preservation, metric GeoTIFF metadata, and artifact hashes.
- PASS — 4 frontend tests and strict 23-module TypeScript/Vite production build.
- PASS — visible browser workflow using a real CUDA Depth Anything V2 run on a 512×512 georeferenced RGB fixture.
- PASS — reference DSM gate recovered scale 40.000 and offset 100.000 despite injected training outliers; held-out RMSE was 0.0000034 m with R² 1.000 on synthetic truth.
- PASS — all 13 real calibrated-run artifact hashes matched; output GeoTIFF preserved EPSG:32643, affine transform, float32 type, metre units, and vertical datum tags.
- PASS — 390×844 responsive QA: document contained at 375 px, calibration panel 351 px, viewer/canvas both 307 px, and no horizontal overflow.
- LIMIT — this is a synthetic calibration correctness result, not a real-world remote-sensing accuracy score.
