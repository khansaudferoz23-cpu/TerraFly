# Build log

Status vocabulary: PASS, FAIL, BLOCKED, SKIPPED.

## 2026-08-25 — intake and bootstrap

- PASS — Workspace inspected; only `outputs/` and `work/` scaffolding existed, with no TerraFly source or Git history.
- PASS — Authenticated GitHub account inspected through the connected GitHub service: `khansaudferoz23-cpu`, one unrelated owned private repository, no TerraFly repository.
- PASS — Official SAC reference inspected at commit `feb4dc63596fdf8c801d1a4f07ef8f2ff4e107be`; repository size 0 and only README content was available.
- PASS — Local environment observed: Windows NT 10.0.26200.0, PowerShell 7.6.4, Git 2.53.0, Node 22.23.1/npm 10.9.8, system Python 3.14.0, bundled project runtime Python 3.12.13.
- PASS — GPU observed: NVIDIA GeForce RTX 5060, 8151 MiB, driver 610.88, reported CUDA UMD 13.3.
- PASS — Global/bundled runtimes contained no PyTorch; no CUDA inference claim has been made.
- PASS — Initial source, safety boundary, documentation, API, model adapters, tests, and frontend created.
- FAIL — First Python dependency attempt timed out; repaired by splitting core/ML installs and increasing the read timeout.
- FAIL — First backend collection failed because the tests lacked a package marker; added `backend/tests/__init__.py` and reran without weakening tests.
- PASS — Backend fast suite: 13 passed in 0.65 seconds initially and 1.66 seconds after final repair.
- FAIL — First frontend test lacked explicit Vitest imports; added them and reran.
- FAIL — Initial frontend production compile exposed missing Vite CSS types and conflicting config; corrected the strict TypeScript config.
- PASS — Frontend component test: 1 passed. Production build completed in 456 ms of Vite build time.
- FAIL — First real-model load identified missing Torchvision; installed the official matching `torchvision==0.27.1+cu130` wheel.
- PASS — PyTorch 2.12.1+cu130, CUDA 13.0 runtime, CUDA allocation, RTX 5060, and Transformers 5.15.1 observed; `pip check` found no broken requirements.
- PASS — Real Depth Anything V2 Small CPU smoke: 34.916 seconds, finite float32 59×73 relative output.
- PASS — Real CUDA smoke: 5.402 seconds, finite float32 59×73 relative output.
- PASS — Real CUDA upload-to-artifacts API smoke: 4.773 seconds after final repair; six artifact downloads and hashes verified; metric remained disabled.
- PASS — Browser workflow rendered real progress, preview, provenance, exports, and a 1177×446 WebGL canvas; viewer buttons changed state.
- PASS — Offline audit removed the only remote font request. npm production audit found 0 vulnerabilities.
- FAIL — An EOF-normalization command appended a literal `\n` suffix to staged text and trailing bytes to the synthetic PNG; the manifest generator detected the Python syntax error before any remote push or ZIP.
- PASS — Repaired every text suffix, compiled all Python, regenerated the PNG byte-for-byte from source, verified its decoder/hash, and reran backend, frontend, production build, and real CUDA API checks.
- FAIL — First two ZIP verification attempts exposed Windows archive line-ending conversion mismatches; no failed ZIP was delivered or retained.
- PASS — Normalized release text to LF, hashed committed export bytes, and repeated packaging.
- PASS — Clean path-with-spaces extraction verified all 61 manifest hashes and ran all 13 backend tests from extracted source in 1.12 seconds.

## 2026-08-25 — professional UI and explainability hardening

- PASS — Audited the original browser result screens against the team's requested professional direction and the supplied anti-pattern video.
- PASS — Rebuilt the interface around a neutral palette, one accent, clear hierarchy, one primary action, a dominant 3D workspace, and a compact result inspector; removed decorative badges, repeated card chrome, and fake future exports.
- PASS — Added file drop, viewer loading/error states, responsive layout, meaningful evidence-download explanations, and a collapsed detailed-method/provenance layer.
- PASS — Audited the related SAC IR-colorization repository at commit `c6735fbffd0d7b08383572357e95d55f91c719e1`; documented why its `.npy` arrays are radiometric training data for a different problem and why its PNGs are previews rather than height labels.
- PASS — Added single-band/TIR domain warnings to the backend response and visible UI, with regression assertions that RGB/RGBA inputs do not receive the warning.
- PASS — Ran the downloaded 512×512 TIR preview through the real cached model in the browser; result, warning, viewer, comparison, and evidence sections rendered successfully.
- PASS — Phone-size QA at 390×844 showed no horizontal page overflow after the process-line wrap repair.
- FAIL — The new file-selection component test initially retained the first rendered page; explicit cleanup was added and the isolated suite passed 2/2.
- PASS — Final revised checks: 13 backend tests, 2 frontend tests, production build, Python compilation/dependency consistency, and PowerShell launcher parsing.
- PASS — Revised source archive extracted to a fresh path containing spaces; all 64 manifest hashes and all 13 backend tests passed in 1.12 seconds.

## 2026-08-25 — Day 2 robust 3D and large-image inference

- PASS — Added bounded overlapping-tile planning, overlap affine scale/offset alignment, feather blending, one global normalization, and persisted strategy metadata.
- FAIL — Initial tiling tests used incorrect manual tile-count expectations; corrected the expectations, then improved the planner to remove redundant near-terminal tiles without leaving edge pixels uncovered.
- PASS — Added an input-dependent processing-memory estimate and pre-acceptance HTTP 413 refusal.
- PASS — Added GLB 2.0 export with triangle geometry, embedded normalized vertex colours, and explicit relative/non-metric extras; binary container, corner colours, and hashes are parsed in tests.
- PASS — Added image/grid orientation metadata plus asymmetric backend and frontend corner assertions.
- PASS — Added orbit and pointer-lock first-person navigation, raycast A/B point sampling, source pixel mapping, relative difference, markers, and clear/reset controls.
- PASS — Added completed-job deletion; path validation and post-delete 404 are covered by API tests.
- PASS — Hardened the Windows launcher to reuse healthy TerraFly services, refuse unknown occupied ports, write readable logs, and leave CMD errors visible.
- PASS — Final automated gate: 20 backend tests in 1.10 seconds, 4 frontend tests in 2.05 seconds, strict 23-module production build in 0.359 seconds, Python compilation, dependency consistency, and launcher parser.
- PASS — Forced real four-tile CUDA inference completed in 21.734 seconds; shape/dtype/range/finiteness/strategy and SHA-256 passed.
- PASS — Real CUDA API completed in 5.101 seconds and verified seven artifact downloads including GLB.
- PASS — Browser QA used the downloaded SAC RGB preview: real result, WebGL mesh, orbit/first-person toggle, A/B samples, evidence links, and no new error-level logs.
- FAIL — Phone QA found a 320 px canvas inside a 307 px viewer; removed the fixed minimum and reran at 390×844 with exact 307 px containment and no page overflow.
- PASS — Day 2 source archive verified all 72 committed-file hashes and ran all 20 backend tests in 0.78 seconds from a fresh path containing spaces.

## 2026-08-25 — Day 3 calibration and held-out evaluation

- PASS — Added typed aligned-reference and GCP calibration contracts; normal PNG/JPEG and ungeoreferenced TIFF jobs remain unable to request metric output.
- PASS — Required exact reference CRS, dimensions, and affine transform with no silent reprojection/resampling.
- PASS — Added robust positive affine fitting, iterative median-deviation outlier rejection, bounded raster training samples, spatially held-out reference pixels, and independent GCP validation lists.
- PASS — Enforced relative span, 75% inliers, 40% two-axis coverage, declared RMSE, minimum R², and evaluation-count gates.
- PASS — Wrote passing-gate metric `.npy`/GeoTIFF, vertical source/datum tags, reference evidence, residual GeoTIFF/preview, calibration report, refreshed manifest, and verified hashes.
- PASS — Poor but aligned evidence returns a documented rejection and no metric files; misaligned evidence fails before fitting.
- PASS — Applied the original GeoTIFF mask to calibration and metric outputs; GCPs touching source NoData are refused.
- PASS — Added a neutral calibration panel with explicit Locked/Passed/Rejected state, exact-grid instructions, held-out metrics, and only real evidence links. GeoTIFF input comparison now uses the generated RGB texture rather than a browser-incompatible TIFF preview.
- PASS — Final automated gate: 25 backend tests in 1.35 seconds, 4 frontend tests in 2.37 seconds, strict 23-module build in 0.336 seconds, Python compilation, dependency consistency, launcher parsing, and diff whitespace checks.
- PASS — Visible real CUDA browser workflow calibrated a 512×512 georeferenced RGB run against a reproducible synthetic reference with injected fit outliers: scale 40.000, offset 100.000, held-out RMSE 0.0000034 m, R² 1.000.
- PASS — All 13 declared calibrated-run artifacts matched hashes; metric GeoTIFF preserved EPSG:32643, the input affine transform, float32 values, metre units, and vertical datum.
- PASS — Responsive QA at 390×844 found no horizontal overflow; document/panel/viewer/canvas widths were 375/351/307/307 px.
- PASS — Day 3 source archive verified all 77 committed-file hashes and ran all 25 backend tests in 1.44 seconds from a fresh path containing spaces.
- LIMIT — The synthetic reference is a software oracle, not independent real-world height truth; no model-accuracy claim was made.

## 2026-08-25 — Day 4 final proof and release

- PASS — Froze TerraFly 1.0’s promise and version: relative monocular structure first; metric outputs only after independently judged vertical evidence; viewer stays relative.
- PASS — Changed final operation to one local service/address: FastAPI serves the prebuilt React/Three.js interface at `127.0.0.1:8000`; Vite remains a development fallback only.
- PASS — Added a beginner checker, full real-model checker, non-overwriting release packager, and a 13-artifact calibrated workflow smoke.
- PASS — Added the reproducible CC0 georeferenced calibration input/reference pair and metadata. The reference identifies itself as a synthetic software oracle, with a fixed relation and training-only outliers.
- PASS — Added the final cookbook, operator guide, architecture/state/gate diagrams, timed demo script, judge Q&A, final handoff, file ledger updates, and exact dependency/release boundaries.
- PASS — Automated gate: 26 backend tests, 4 frontend tests, strict production build, Python dependency consistency, and production health/version.
- PASS — Real CUDA final smoke completed in 4.924 seconds, reached Metric Calibrated, verified all 13 hashes, and inspected CRS/metre/float32 GeoTIFF tags.
- PASS — Visible production browser QA covered real upload/inference, WebGL texture/wireframe, Orbit/First-person selection, A/B sampling, calibration, evidence links, and full desktop presentation.
- PASS — Phone-size QA at 390×844 found a 375 px document inside the viewport with no horizontal overflow.
- INFO — Automated Chromium cannot grant pointer lock and logged its own denial when first-person was clicked; the mode, help/key contract, and normal manual-browser controls are documented for rehearsal.
- PASS — Final archives were extracted to a fresh path containing spaces, source hashes/tests/static serving were verified, and archive SHA-256 values were recorded in the final report.
- LIMIT — No independent surveyed dataset exists in scope; the final release makes no real-world height-accuracy claim.
