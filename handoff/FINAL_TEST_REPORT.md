# TerraFly 1.0 final test report

Date: 2026-08-27 IST
Environment: Windows, Python 3.12.13, Node 22.23.1, RTX 5060 8 GB, PyTorch 2.12.1+cu130  
Model: `depth-anything/Depth-Anything-V2-Large-hf` revision `7581137eff8d4e94f6e796d3baea0e9fa79b22d2`

## Automated release gate

| Check | Result | Final observation |
|---|---:|---|
| Python dependency consistency | PASS | `pip check`: no broken requirements |
| Backend scientific/safety suite | PASS | 37 tests, including embedded GLB texture/UV/normals/PBR, canonical/display separation, cleanup, direction, metric registration, and safety gates |
| Frontend interaction suite | PASS | 9 tests, including relative/metre height-colour semantics plus existing geometry, sampling, and interaction contracts |
| Strict production build | PASS | TypeScript/Vite passed; JS 807.84 kB, gzip 217.02 kB; non-failing chunk advisory |
| npm production audit | PASS | 0 vulnerabilities |
| PowerShell/CMD entry points | PASS | Reproduced and repaired duplicate `PATH`/`Path` `Start-Process` crash; exact CMD launch, production readiness, browser-open path, parser, and checker passed |
| Python compilation/diff whitespace | PASS | all backend/scripts compile; `git diff --check` clean |

## Full real-model and calibration proof

The final `scripts\smoke_final_workflow.py --device cuda` rerun completed in 7.517 seconds with the prepared local Large cache.

| Contract | Result |
|---|---:|
| Initial GeoTIFF state | `Georeferenced Relative` |
| Final state after held-out gate | `Metric Calibrated` |
| Declared artifacts downloaded/hashed | 18/18 PASS |
| Recovered scale | 39.999999869 m per relative unit |
| Recovered offset | 100.000000037 m |
| Held-out RMSE | 0.000002102 m |
| Held-out R² | 0.99999999999996 |
| Metric GeoTIFF | EPSG:32643, original affine/grid, float32, metre units, datum/source tags PASS |

The model loader was also checked with a prepared cache and no usable network. It now tries local files first, avoiding delay on a demonstration machine, and uses the normal download path only when files are absent.

The passing artifact set includes `metric_analysis_grid.json`, whose values and source indices are tested against the full metric surface; the separate `reconstructed_structures.json` visual-candidate layer; and `display_grid.json`, which is explicitly excluded from calibration and measurements. A real CUDA stadium run produced 11 job artifacts, kept the canonical numeric/analysis files unchanged, and recorded 11 flattened raised regions covering 3,222 viewer-grid pixels.

## Browser acceptance

- PASS — final production UI and API served together at `http://127.0.0.1:8000`; Vite was not required.
- PASS — real CUDA GeoTIFF upload, progress, textured WebGL mesh, evidence/provenance, and metric calibration.
- PASS — Orbit mode, Photo/Height colours, visible numeric relative legend, Wireframe, sun direction 35°→140°, and one real stadium WebGL scene.
- PASS — First-person mode and visible control contract: click, mouse-look, W/A/S/D, Q/E, Shift boost, and Escape.
- PASS — 390×844 viewport: inner width 390 px, document width 375 px, no horizontal page overflow.
- PASS — final desktop full-page visual inspection showed the complete professional workbench, gate result, and evidence list.
- PASS — supplied stadium scene showed raised local structures instead of inverted holes; raw prediction and convention/tilt diagnostic links were visible.
- PASS — updated real CUDA stadium upload rendered at the retuned 1.4× default with scene texture on mild faces and neutral material on steep faces; close visual inspection showed no long vertical texture drips.
- PASS — `display_grid.json` appeared as an explicitly display-only evidence file; two clicked points still reported canonical relative values and source pixels; browser warnings/errors: zero.
- PASS — calibrated browser demo changed the legend from `relative — not metres` to a 100.0–140.0 m scale and displayed `Metric Calibrated` / `Metric export unlocked`.
- INFO — automated Chromium is not permitted to grant pointer lock and logged that denial. Normal manual browser pointer lock is therefore the presentation-rehearsal acceptance step; no scientific/export path depends on it.

## Archive and clean-folder acceptance

- Both source and Windows ZIPs were extracted into fresh folders whose names contain spaces.
- Every tracked source blob matched the committed Git object before the final evidence refresh.
- All 37 backend tests passed in the repaired source using the prepared test environment; the updated source/Windows archives are generated under `outputs\critical-fix-2026-08-27` after the final commit.
- The extracted Windows release contained `frontend\dist` and served both `/` and `/api/health` as TerraFly 1.0.0 on isolated port 8010.
- The final rerun verifies `handoff\FINAL_MANIFEST.json` entries and both archive checksums. Exact ZIP byte lengths and SHA-256 values are written beside the archives in `TerraFly_FINAL_SHA256.txt`, avoiding a circular archive-hash claim inside the archive itself.

## Scientific acceptance boundary

This report proves software behavior, the repaired height convention, true embedded-texture/normal/PBR GLB export, canonical/display separation, edge-aware visual cleanup, neutral steep-face handling, the separated structure layer, metric viewer sampling, Large-model execution, and the synthetic calibration oracle. It does not prove real-world height accuracy, semantic building reconstruction, recovered façade imagery, or disaster prediction. The real metric card remains blocked because no compatible independently surveyed remote-sensing height dataset was supplied, and strong scene-wide perspective tilt remains diagnosed rather than corrected.
