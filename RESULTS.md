# Results

No real-world scientific accuracy result is claimed. No independent surveyed height dataset was supplied or discovered. Day 3 synthetic truth verifies calibration software and rejection behavior only.

## Engineering results

The deterministic upload-to-artifact path and the separately implemented real-model path are both verified. The CUDA API smoke downloaded every declared artifact and checked its SHA-256 digest. The revised browser workflow rendered a real result from the downloaded 512×512 TIR preview, showed the required domain warning, and displayed the Three.js surface without presenting it as validated TIR science.

Day 2 verified real four-tile CUDA inference, a seven-artifact workflow including parsed GLB 2.0 output, browser A/B relative sampling, navigation-mode switching, and responsive containment. These are engineering results; scientific accuracy remains unevaluated without compatible height truth.

Day 3 verified exact-grid calibration, robust outlier handling, held-out metrics, poor-evidence refusal, independent GCP validation, source-mask preservation, and gated metric/error artifacts. A real CUDA browser run recovered the known synthetic relation (scale 40, offset 100) with held-out RMSE `3.37×10⁻⁶` m and R² 1.000. That near-zero error is expected because the reference was deliberately derived from the result; it is a pipeline oracle, not model accuracy.

## Test table

| Test | Command | Result | Duration | Evidence | Environment |
|---|---|---:|---:|---|---|
| Backend fast suite | `.venv\\Scripts\\python.exe -m pytest -q` | PASS | 0.87 s pytest | `handoff/DAY_1_TEST_REPORT.md` | Python 3.12.13 |
| Frontend components (2) | `npm test` | PASS | 1.75 s | `handoff/DAY_1_TEST_REPORT.md` | Node 22.23.1 |
| Frontend production build | `npm run build` | PASS | 0.284 s Vite | `handoff/DAY_1_TEST_REPORT.md` | Vite 8.2.2 |
| Python dependency consistency | `.venv\\Scripts\\python.exe -m pip check` | PASS | <1 s | console + report | isolated `.venv` |
| npm production audit | `npm audit --omit=dev` | PASS | 1.2 s | console + report | lockfile present |
| Real CPU model | `scripts\\smoke_real_model.py --device cpu` | PASS | 34.916 s | `handoff/DAY_1_TEST_REPORT.md` | PyTorch 2.12.1+cu130 |
| Real CUDA model | `scripts\\smoke_real_model.py --device cuda` | PASS | 5.402 s | `handoff/DAY_1_TEST_REPORT.md` | RTX 5060 8 GB |
| Real CUDA API workflow | `scripts\\smoke_real_api.py --device cuda` | PASS | 4.773 s | `handoff/DAY_1_TEST_REPORT.md` | six artifact hashes verified |
| Browser workflow | local app + downloaded TIR preview | PASS | ~8 s inference | external empty/result screenshots | real cached model + warning + WebGL |
| Responsive browser workflow | 390×844 viewport | PASS | interactive | no horizontal document overflow | completed result state |
| Windows launcher parse | PowerShell parser | PASS | <1 s | no syntax errors | readiness + auto-open path |
| Extracted revised source ZIP | manifest verifier + extracted pytest | PASS | 1.12 s pytest | `handoff/DAY_1_TEST_REPORT.md` | 64 hashes; fresh path contains spaces |

## Day 2 test table

| Test | Result | Duration | Evidence |
|---|---:|---:|---|
| Backend suite (20) | PASS | 1.10 s | `handoff/DAY_2_TEST_REPORT.md` |
| Frontend suite (4) | PASS | 2.05 s | orientation and scientific-contract components |
| Production build | PASS | 0.359 s | strict TypeScript + Vite |
| Real aligned four-tile CUDA inference | PASS | 21.734 s | 320×480 float32; 4 tiles; output hash recorded |
| Real CUDA upload-to-seven-artifact API | PASS | 5.101 s | GLB and every declared artifact hash matched |
| Browser RGB workflow | PASS | interactive | orbit/first-person switching, A/B samples, GLB link, WebGL |
| 390×844 browser layout | PASS | interactive | document and repaired canvas remained contained |
| Extracted Day 2 source ZIP | PASS | 0.78 s pytest | 72 hashes; 20 backend tests; fresh path contains spaces |

## Day 3 test table

| Test | Result | Duration | Evidence |
|---|---:|---:|---|
| Backend suite (25) | PASS | 1.35 s | reference/GCP pass, alignment/error rejection, hashes, NoData contract |
| Frontend suite (4) | PASS | 2.37 s | scientific contract and asymmetric orientation components |
| Production build | PASS | 0.336 s | strict TypeScript; 23 modules transformed |
| Real CUDA browser inference + calibration | PASS | interactive | 512×512 RGB GeoTIFF; real model; exact synthetic reference |
| Robust fit with injected training outliers | PASS | included | scale 40.000; offset 100.000; held-out pixels excluded from fit |
| Metric GeoTIFF contract | PASS | included | EPSG:32643, original affine, float32, metre/datum tags |
| Calibrated run artifact integrity | PASS | included | all 13 declared hashes matched |
| Poor or misaligned evidence | PASS | included | rejected or HTTP 400; no metric artifacts |
| 390×844 browser layout | PASS | interactive | 375 px document; 351 px panel; 307 px viewer/canvas; no overflow |
| Extracted Day 3 source ZIP | PASS | 1.44 s pytest | 77 hashes; 25 backend tests; fresh path contains spaces |

## Day 4 final-release test table

| Test | Result | Evidence |
|---|---:|---|
| Backend suite (32) | PASS | safety, serving, output convention, raised-roof GLB, artifacts, tiling, geospatial, calibration, rejection |
| Frontend suite (4) | PASS | scientific contract, real file action, asymmetric orientation and point sampling |
| Production interface build | PASS | strict TypeScript/Vite; interface served by FastAPI without Vite |
| Full real-model workflow | PASS | CUDA; `Metric Calibrated`; 15/15 artifact hashes; 5.875 s direct smoke |
| Bundled robust calibration oracle | PASS | scale 39.99999998, offset 100.0, held-out RMSE 0.0000035 m, R² 1.0 |
| Metric GeoTIFF | PASS | EPSG:32643, matching affine/dimensions, float32, metre units, datum tags |
| Production browser workflow | PASS | upload, progress, real WebGL, Orbit/First-person modes, A/B, toggles, calibration, exports |
| Responsive 390×844 | PASS | 390 px viewport, 375 px document, no horizontal overflow |
| Final Windows/source packages | PASS | SHA-256 checksums and clean path-with-spaces extraction in `handoff/FINAL_TEST_REPORT.md` |

The synthetic oracle result is deliberately almost perfect because it is derived from the generated relative surface. It validates the implementation and its refusal rules; it must never be quoted as satellite/aerial height accuracy.

## Output-convention repair evidence

The original adapter performed `1 - normalized_depth` even though this checkpoint's relative output behaves like inverse depth/proximity. That extra inversion made closer rooftops appear as holes. TerraFly now preserves raw output, declares the convention, normalizes exactly once, and uses `relative_surface.npy`—not a colour PNG—as the geometry source.

| Check | Result | Evidence |
|---|---:|---|
| Backend suite | PASS | 32 tests, including all constant-output conventions, inverse-depth/depth mappings, and raised-roof GLB ordering |
| Frontend suite/build | PASS | 4 tests; strict 23-module production build |
| Supplied stadium CUDA rerun | PASS | 9/9 hashes; larger raw values mapped higher; plane fraction 0.9459 |
| Supplied residential CUDA rerun | PASS | 9/9 hashes; rooftops above nearby roads; plane fraction 0.7674 |
| Local production browser | PASS | corrected textured 3D stadium, raw/diagnostic links, warnings, and no browser errors |
| Full calibration workflow | PASS | 15/15 hashes; regenerated software oracle; scale 40.00000007; RMSE 0.00000295 m |

The hole/reversal bug is fixed. The large plane fractions are a separate monocular perspective-bias limitation; they are reported but not automatically removed.

## Problem-statement alignment evidence — 2026-08-26

| Check | Result | Evidence |
|---|---:|---|
| Backend suite | PASS | 32 tests; structure separation, metric grid, horizontal units, calibration, direction, GLB, safety |
| Frontend suite | PASS | 7 tests; upward structure extrusion, projected-affine distance, relative/metric sampling including NoData, and existing interaction/orientation contracts |
| Production build | PASS | strict TypeScript/Vite; 803.57 kB JavaScript (215.82 kB gzip), with a non-failing chunk-size advisory |
| Supplied stadium real CUDA run | PASS | 10/10 hashes in 6.105 s, exact model revision, 8 optional structure candidates, DSM unchanged |
| Real calibration workflow | PASS | 17/17 hashes in 28.196 s; metric state; scale 40.00000007; offset 99.99999997; RMSE 0.00000295 m |
| Updated in-app browser | PARTIAL | initial page rendered; upload/generate interaction was denied by browser security auto-review, so no workaround was attempted |

The new Structures layer is visualization evidence, not accuracy evidence. The metric numbers above come from the synthetic software oracle and prove the software relation/export path only.
