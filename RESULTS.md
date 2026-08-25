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
