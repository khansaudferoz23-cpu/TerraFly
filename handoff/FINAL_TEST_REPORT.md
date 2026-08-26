# TerraFly 1.0 final test report

Date: 2026-08-26 IST
Environment: Windows, Python 3.12.13, Node 22.23.1, RTX 5060 8 GB, PyTorch 2.12.1+cu130  
Model: `depth-anything/Depth-Anything-V2-Small-hf` revision `5426e4f0f36572d16453bbda7a8389317b1bef99`

## Automated release gate

| Check | Result | Final observation |
|---|---:|---|
| Python dependency consistency | PASS | `pip check`: no broken requirements |
| Backend scientific/safety suite | PASS | 32 tests, including constant-output, direction, and raised-roof GLB regressions |
| Frontend interaction suite | PASS | 7 tests, including upward structure extrusion, projected-affine distance, metric interpolation, and NoData behavior |
| Strict production build | PASS | TypeScript/Vite passed; JS 803.57 kB, gzip 215.82 kB; non-failing chunk advisory |
| npm production audit | PASS | 0 vulnerabilities |
| PowerShell/CMD entry points | PASS | setup/start/verify/package parse; checker completed with PASS |
| Python compilation/diff whitespace | PASS | all backend/scripts compile; `git diff --check` clean |

## Full real-model and calibration proof

The final `scripts\smoke_final_workflow.py --device cuda` rerun completed in 28.196 seconds with the prepared local cache.

| Contract | Result |
|---|---:|
| Initial GeoTIFF state | `Georeferenced Relative` |
| Final state after held-out gate | `Metric Calibrated` |
| Declared artifacts downloaded/hashed | 17/17 PASS |
| Recovered scale | 40.000000072 m per relative unit |
| Recovered offset | 99.999999966 m |
| Held-out RMSE | 0.000002948 m |
| Held-out R² | 0.9999999999999 |
| Metric GeoTIFF | EPSG:32643, original affine/grid, float32, metre units, datum/source tags PASS |

The model loader was also checked with a prepared cache and no usable network. It now tries local files first, avoiding delay on a demonstration machine, and uses the normal download path only when files are absent.

The passing artifact set now includes `metric_analysis_grid.json`, whose values and source indices are tested against the full metric surface, and the separate `reconstructed_structures.json` visual-candidate layer. A real CUDA stadium run also hash-verified 10/10 normal artifacts and produced eight optional structure candidates without changing the DSM.

## Browser acceptance

- PASS — final production UI and API served together at `http://127.0.0.1:8000`; Vite was not required.
- PASS — real CUDA GeoTIFF upload, progress, textured WebGL mesh, evidence/provenance, and metric calibration.
- PASS — Orbit mode, Texture/Wireframe state changes, two point samples, source pixels, and relative A/B difference `0.433`.
- PASS — First-person mode and visible control contract: click, mouse-look, W/A/S/D, Q/E, Shift boost, and Escape.
- PASS — 390×844 viewport: inner width 390 px, document width 375 px, no horizontal page overflow.
- PASS — final desktop full-page visual inspection showed the complete professional workbench, gate result, and evidence list.
- PASS — supplied stadium scene showed raised local structures instead of inverted holes; raw prediction and convention/tilt diagnostic links were visible.
- INFO — automated Chromium is not permitted to grant pointer lock and logged that denial. Normal manual browser pointer lock is therefore the presentation-rehearsal acceptance step; no scientific/export path depends on it.
- INFO — after the metric/Structures update, the in-app browser rendered the revised initial page but security auto-review denied the final upload/generate interaction. No workaround or alternate browser was attempted. Backend end-to-end smoke and frontend automation cover the new data paths.

## Archive and clean-folder acceptance

- Both source and Windows ZIPs were extracted into fresh folders whose names contain spaces.
- Every tracked source blob matched the committed Git object before the final evidence refresh.
- All 32 backend tests passed in the repaired source using the prepared test environment; release archives must be regenerated before external delivery.
- The extracted Windows release contained `frontend\dist` and served both `/` and `/api/health` as TerraFly 1.0.0 on isolated port 8010.
- The final rerun verifies `handoff\FINAL_MANIFEST.json` entries and both archive checksums. Exact ZIP byte lengths and SHA-256 values are written beside the archives in `TerraFly_FINAL_SHA256.txt`, avoiding a circular archive-hash claim inside the archive itself.

## Scientific acceptance boundary

This report proves software behavior, the repaired height convention, the separated structure layer, metric viewer sampling, and the synthetic calibration oracle. It does not prove real-world height accuracy, semantic building reconstruction, or disaster prediction. No compatible independently surveyed remote-sensing height dataset was supplied, and strong scene-wide perspective tilt remains diagnosed rather than corrected.
