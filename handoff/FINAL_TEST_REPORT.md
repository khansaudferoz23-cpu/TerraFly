# TerraFly 1.0 final test report

Date: 2026-08-25 IST  
Environment: Windows, Python 3.12.13, Node 22.23.1, RTX 5060 8 GB, PyTorch 2.12.1+cu130  
Model: `depth-anything/Depth-Anything-V2-Small-hf` revision `5426e4f0f36572d16453bbda7a8389317b1bef99`

## Automated release gate

| Check | Result | Final observation |
|---|---:|---|
| Python dependency consistency | PASS | `pip check`: no broken requirements |
| Backend scientific/safety suite | PASS | 32 tests, including constant-output, direction, and raised-roof GLB regressions |
| Frontend interaction suite | PASS | 4 tests in 1.83 s |
| Strict production build | PASS | 23 modules; 0.200 s Vite build; JS gzip 205.67 kB |
| npm production audit | PASS | 0 vulnerabilities |
| PowerShell/CMD entry points | PASS | setup/start/verify/package parse; checker completed with PASS |
| Python compilation/diff whitespace | PASS | all backend/scripts compile; `git diff --check` clean |

## Full real-model and calibration proof

`scripts\verify.ps1 -Full` completed in approximately 17 seconds with the prepared local cache. The real workflow itself completed in 5.485 seconds on CUDA.

| Contract | Result |
|---|---:|
| Initial GeoTIFF state | `Georeferenced Relative` |
| Final state after held-out gate | `Metric Calibrated` |
| Declared artifacts downloaded/hashed | 15/15 PASS |
| Recovered scale | 40.000000072 m per relative unit |
| Recovered offset | 99.999999966 m |
| Held-out RMSE | 0.000002948 m |
| Held-out R² | 0.9999999999999 |
| Metric GeoTIFF | EPSG:32643, original affine/grid, float32, metre units, datum/source tags PASS |

The model loader was also checked with a prepared cache and no usable network. It now tries local files first, avoiding delay on a demonstration machine, and uses the normal download path only when files are absent.

## Browser acceptance

- PASS — final production UI and API served together at `http://127.0.0.1:8000`; Vite was not required.
- PASS — real CUDA GeoTIFF upload, progress, textured WebGL mesh, evidence/provenance, and metric calibration.
- PASS — Orbit mode, Texture/Wireframe state changes, two point samples, source pixels, and relative A/B difference `0.433`.
- PASS — First-person mode and visible control contract: click, mouse-look, W/A/S/D, Q/E, Shift boost, and Escape.
- PASS — 390×844 viewport: inner width 390 px, document width 375 px, no horizontal page overflow.
- PASS — final desktop full-page visual inspection showed the complete professional workbench, gate result, and evidence list.
- PASS — supplied stadium scene showed raised local structures instead of inverted holes; raw prediction and convention/tilt diagnostic links were visible.
- INFO — automated Chromium is not permitted to grant pointer lock and logged that denial. Normal manual browser pointer lock is therefore the presentation-rehearsal acceptance step; no scientific/export path depends on it.

## Archive and clean-folder acceptance

- Both source and Windows ZIPs were extracted into fresh folders whose names contain spaces.
- Every tracked source blob matched the committed Git object before the final evidence refresh.
- All 32 backend tests passed in the repaired source using the prepared test environment; release archives must be regenerated before external delivery.
- The extracted Windows release contained `frontend\dist` and served both `/` and `/api/health` as TerraFly 1.0.0 on isolated port 8010.
- The final rerun verifies `handoff\FINAL_MANIFEST.json` entries and both archive checksums. Exact ZIP byte lengths and SHA-256 values are written beside the archives in `TerraFly_FINAL_SHA256.txt`, avoiding a circular archive-hash claim inside the archive itself.

## Scientific acceptance boundary

This report proves software behavior, the repaired height convention, and the synthetic calibration oracle. It does not prove real-world height accuracy. No compatible independently surveyed remote-sensing height dataset was supplied, and strong scene-wide perspective tilt remains diagnosed rather than corrected.
