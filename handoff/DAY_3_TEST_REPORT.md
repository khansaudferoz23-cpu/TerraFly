# Day 3 test report

Status vocabulary is restricted to PASS, FAIL, BLOCKED, or SKIPPED.

| Test | Result | Duration | Evidence |
|---|---:|---:|---|
| Backend full suite (25) | PASS | 1.35 s | upload, artifacts, tiling, GLB, cleanup, geospatial, calibration pass/reject, NoData preservation |
| Aligned reference DSM with injected training outliers | PASS | included | recovered scale 40 and offset 100; held-out pixels excluded from fit |
| Reference alignment mismatch | PASS | included | shifted affine returned HTTP 400; metric state/artifacts absent |
| Poor aligned reference | PASS | included | gate rejected on independent metrics; report/reference retained; metric absent |
| Independent GCP validation | PASS | included | separate controls/checks unlocked metric output only after validation |
| Metric GeoTIFF | PASS | included | float32, EPSG:32643, input affine, NoData, metre/datum/source tags |
| Calibration artifact hashes | PASS | included | every declared download matched SHA-256 |
| Frontend suite (4) | PASS | 2.37 s | app scientific contract + geometry/orientation sampling |
| Strict TypeScript/Vite build | PASS | 0.336 s | 23 modules transformed |
| Real CUDA browser workflow | PASS | interactive | 512×512 georeferenced SAC RGB-derived fixture, real cached model, WebGL |
| Browser metric gate | PASS | interactive | scale 40.000, offset 100.000, held-out RMSE 0.0000034 m, R² 1.000 |
| Browser evidence presentation | PASS | interactive | report, metric GeoTIFF/NPY, residual map, truthful relative viewer labels |
| 390×844 responsive layout | PASS | interactive | no page overflow; 307 px viewer and canvas match |
| Extracted Day 3 source archive | PASS | 1.44 s pytest | fresh path containing spaces; 77 source hashes and all 25 backend tests passed |

## Interpretation

The near-zero calibration error is expected for a deliberately derived synthetic reference and must not be presented as model accuracy. The scientifically important test is that the software separates fit/evaluation pixels, survives injected fit outliers, refuses bad or misaligned evidence, and creates no metric file on rejection.
