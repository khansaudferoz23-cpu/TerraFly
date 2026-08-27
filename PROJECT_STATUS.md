# Project status

Last updated: 2026-08-27 IST

## Intake result

Greenfield bootstrap. The authenticated GitHub account `khansaudferoz23-cpu` owned only the unrelated private repository `content-portal`; no user-owned TerraFly repository existed. The current workspace contained no source files.

## Implemented baseline

- Single FastAPI + React/Three.js project structure.
- Size, extension, filename, pixel-count, corrupt-image, and decompression-bomb boundaries.
- PNG/JPEG mode normalization and GeoTIFF CRS/transform/NoData inspection.
- Strict `Relative`, `Georeferenced Relative`, and `Metric Calibrated` state vocabulary.
- Real Depth Anything V2 Large adapter configured as the default, with CUDA/CPU selection and CUDA-OOM fallback; its non-commercial checkpoint licence and unvalidated remote-sensing accuracy remain explicit.
- Explicit inverse-depth/proximity convention with one normalization pass, preserved raw prediction, and no accidental roof inversion.
- Test-only deterministic adapter with a normal-run safety interlock.
- Per-job input hash, scientific state, model/device/revision, warnings, calibration refusal, and artifact hashes.
- Numeric `.npy`, colour preview, texture, 16-bit display height texture, and 3D grid exports.
- Per-run height diagnostics name the numeric geometry source and quantify dominant image-plane tilt without silently flattening it.
- React upload/progress/results UI and interactive Three.js orbit/pan/zoom viewer.
- Task-first neutral UI with working drag/drop, dominant 3D workspace, responsive result inspector, loading/error states, and explained evidence downloads.
- Explicit single-band/TIR domain warning in the API manifest and visible result UI.
- Team technical guide, file-by-file repository ledger, UI rationale, and exact related-SAC sample audit.
- Overlapping tiled inference with bounded tile count, overlap affine alignment, feather blending, global normalization, and recorded strategy metadata.
- Input-dependent processing-memory budget enforced before job acceptance.
- Asymmetric orientation contract shared by viewer grid, image texture, point sampling, GLB UVs, and A/B analysis values.
- Orbit and pointer-lock first-person navigation plus two-point relative comparison with source pixel coordinates.
- Standards-based GLB 2.0 mesh export with embedded source-image texture, UVs, smooth unit normals, lit PBR materials, neutral steep faces, and explicit non-metric metadata.
- Completed-result deletion and launcher reuse/port/log diagnostics without killing unknown processes.
- Exact-grid aligned reference-DSM calibration with robust affine outlier handling and spatially held-out evaluation.
- Ground-control calibration with separate control and validation point sets, bilinear relative sampling, and coverage gates.
- Strict positive-scale, relative-span, inlier-ratio, axis-coverage, RMSE, and R² gate before metric state/output exists.
- Source NoData preservation, calibrated float32 `.npy`/GeoTIFF, residual GeoTIFF/preview, retained reference evidence, and calibration report hashes.
- Professional calibration panel with explicit Locked/Passed/Rejected states and dynamically truthful evidence downloads.
- Passing calibration writes a metric analysis grid aligned exactly with the responsive 3D grid; A/B inspection reports metre elevation/height difference and projected-metre distance/slope.
- Every run writes a separate optional Bhuvan-style structure-candidate layer with upright visual extrusions; it is off by default, non-semantic, and cannot modify the DSM.
- Problem-statement traceability explicitly distinguishes implemented elevation/visualization features from future hazard prediction and domain-specific training.
- Canonical relative/metric arrays are now separated from a recorded display grid with isolated-spike replacement, RGB-guided bilateral smoothing, conservative rooftop flattening, and an extreme adjacent-delta safety cap.
- Steep heightfield triangles use a neutral synthetic wall material in both Three.js and GLB instead of stretching top-down image pixels; default vertical exaggeration was retuned to 1.4×.
- Viewer-selectable Photo and Height colours, a numeric relative/metre legend, and adjustable sun azimuth make height ordering and surface normals inspectable without changing saved data.
- A reusable held-out height benchmark computes RMSE, MAE, bias, and Pearson correlation only from aligned finite masked truth; the metric card stays visibly blocked until a licensed real dataset is evaluated.

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

## Final release status

TerraFly 1.0 is feature-complete for the four-day build: relative inference, geospatial preservation, interactive 3D inspection, evidence-gated calibration, reproducible artifacts, professional responsive UI, one-address Windows launch, automated/full checkers, final cookbook/judge materials, and checked archives are complete.

The remaining scientific work is intentionally outside this software milestone: real-world accuracy evaluation against compatible, independently surveyed height evidence. The Windows release includes the prebuilt interface but not the large third-party Python/npm environments or model weights; first-machine setup still requires internet access.

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
- PASS — Day 3 source archive extracted to a fresh path containing spaces; all 77 manifest hashes and all 25 backend tests passed from extracted source.
- LIMIT — this is a synthetic calibration correctness result, not a real-world remote-sensing accuracy score.

## Verified Day 4 final release and convention repair

- PASS — 32 backend tests, 4 frontend tests, strict production build, Python dependency consistency, and final launcher/checker parser checks.
- PASS — complete real CUDA calibration smoke in 5.875 seconds: `Metric Calibrated`, 15 artifact hashes, EPSG:32643, float32 metre GeoTIFF, scale 40, offset 100, held-out RMSE 0.00000295 m, and R² 1.0 on the regenerated bundled synthetic oracle.
- PASS — supplied stadium and residential scenes reran on CUDA with all 9 artifacts hashed; local rooftops/rim are no longer inverted into holes.
- PASS — synthetic flat ground plus raised square proves the normalized array and exported GLB keep the roof above ground.
- PASS — backend serves the prebuilt React/Three.js interface and API together at `127.0.0.1:8000`; no Vite process is required for final operation.
- PASS — visible production browser workflow: real CUDA inference, WebGL 3D result, A/B inspection, orbit/first-person mode, texture/wireframe toggles, calibration pass, and truthful evidence links.
- PASS — responsive production QA at 390×844 with document width contained and no horizontal page overflow.
- PASS — final source/release ZIP checksums and clean extracted-folder-with-spaces verification are recorded in `handoff/FINAL_TEST_REPORT.md`.
- LIMIT — pointer lock cannot be granted by automated browser control; the first-person mode/help/key contract was verified and the normal interactive browser path remains the manual acceptance step.
- LIMIT — measured global plane trends remain strong on the supplied scenes (94.6% stadium, 76.7% residential); the diagnostic warns, and no unvalidated flattening is applied.

## Post-repair problem-statement alignment — 2026-08-26

- PASS — 33 backend tests and 8 frontend tests cover separate canonical/display grids, spike cleanup, conservative rooftop flattening, adjacent-delta safety, neutral steep-face material groups, upward structure extrusion, raised-object ordering, metric-grid value alignment, NoData-safe metric sampling, projected-affine distance, geospatial horizontal units, calibration refusal, and existing safety contracts.
- PASS — strict TypeScript/Vite production build; the large Three.js bundle emits a size advisory but compiles successfully.
- PASS — real CUDA stadium run generated 11 declared job artifacts (10 embedded in the self-excluding manifest), preserved the exact model revision, kept `relative_surface.npy` and `relative_grid.json` canonical, and recorded 11 flattened raised regions covering 3,222 viewer-grid pixels in `height_diagnostics.json`.
- PASS — final real CUDA calibration workflow completed in 25.335 seconds, reached `Metric Calibrated`, hash-verified 18 artifacts, recovered scale `40.00000007` and offset `99.99999997`, and wrote the matching metric analysis grid.
- PASS — updated production app completed an in-app-browser CUDA stadium upload. At the retuned 1.4× default, mild faces retained aerial colour and steep faces rendered neutral without long texture drips; A/B inspection returned canonical relative values, and the browser logged no warnings or errors.
- PASS — reproduced the reported non-opening CMD launcher: inherited duplicate `PATH`/`Path` entries caused PowerShell `Start-Process` to fail before Uvicorn launched. The launcher now normalizes that process environment, keeps TerraFly running if automatic browser opening fails, and passed an exact CMD launch plus live `http://127.0.0.1:8000` health/page check.
- LIMIT — visual structure candidates are not building segmentation, and the synthetic calibration oracle is not a real accuracy score.

## Critical-fix acceptance — 2026-08-27

- PASS — GLB export now contains an embedded source PNG, `TEXCOORD_0`, smooth unit `NORMAL` vectors, lit PBR materials, and neutral steep faces; regression tests reject `COLOR_0` and `KHR_materials_unlit`.
- PASS — the production viewer exposes Photo/Height colours, a fixed numeric legend (`relative — not metres` or calibrated metres), a responsive sun-direction slider, wireframe, Structures, and display-only exaggeration.
- PASS — 37 backend tests and 9 frontend tests passed; strict TypeScript/Vite built 23 modules (807.84 kB JavaScript, 217.02 kB gzip) with only the existing non-failing chunk advisory.
- PASS — default Depth Anything V2 Large revision `7581137eff8d4e94f6e796d3baea0e9fa79b22d2` passed CUDA and CPU smoke inference. CUDA peak allocation was 1,618.2 MB on the direct smoke and 1,699.6 MB on the same-stadium comparison.
- PASS — Small/Large same-stadium comparison preserved both previews and numeric outputs; Large showed sharper local delineation, while the report explicitly refuses to infer accuracy without truth.
- PASS — the Large-derived calibration fixture completed the full CUDA workflow in 7.517 s, reached `Metric Calibrated`, hash-verified 18 artifacts, recovered scale 39.99999987 and offset 100.00000004, and produced synthetic-oracle RMSE 0.00000210 m.
- PASS — production browser acceptance covered a real stadium scene, Photo/Height switching, the relative legend, live sun update from 35° to 140°, a calibrated 100–140 m legend, and a 390×844 layout with 375 px document and 307 px toolbar/viewer/canvas. Browser warnings/errors: zero.
- PASS — a masked benchmark utility now requires matching GeoTIFF CRS/affine grids for real evidence and writes RMSE, MAE, bias, Pearson correlation, data licence/split, hashes, and resource facts.
- LIMIT — real height RMSE/MAE/Pearson remain intentionally blocked because no licensed independent RGB–DSM/nDSM held-out truth was supplied. RDAH-Net is documented as an audit candidate; Depth2Elevation has no verified author code/weights in scope.
