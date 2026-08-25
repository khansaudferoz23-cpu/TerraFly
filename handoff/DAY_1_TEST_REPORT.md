# Day 1 test report

Status vocabulary is restricted to PASS, FAIL, BLOCKED, or SKIPPED.

| Test | Result | Duration | Evidence |
|---|---:|---:|---|
| Backend safe upload, adapter, artifacts, and GeoTIFF suite (13 tests) | PASS | 1.66 s | final repair pytest output; artifact response hashes asserted |
| Frontend scientific-contract component | PASS | 19.59 s | final repair Vitest output |
| Strict TypeScript/Vite production build | PASS | 0.178 s | final repair build output |
| Python dependency consistency | PASS | <1 s | `No broken requirements found` |
| npm production dependency audit | PASS | 1.2 s | `found 0 vulnerabilities` |
| CUDA tensor allocation | PASS | <1 s after import | RTX 5060; PyTorch 2.12.1+cu130; CUDA runtime 13.0 |
| Real Depth Anything V2 Small CPU inference | PASS | 34.916 s | revision `5426e4f0f36572d16453bbda7a8389317b1bef99`; finite float32 59×73 output |
| Real Depth Anything V2 Small CUDA inference | PASS | 5.402 s | same revision/input; finite float32 59×73 output |
| Real CUDA upload-to-six-artifact API workflow | PASS | 4.773 s | every downloaded artifact SHA-256 matched the manifest after sample regeneration |
| Browser upload/progress/result/Three.js workflow | PASS | interactive | 1177×446 WebGL canvas; screenshot in task outputs |
| Metric claim gate for ordinary PNG | PASS | included above | state `Relative`; units `relative_0_1`; metric output false |
| GeoTIFF CRS/transform/NoData preservation | PASS | included above | EPSG:32643 asymmetric fixture; still `Georeferenced Relative` |
| CPU fallback on forced CUDA OOM | SKIPPED | — | recovery branch implemented; deterministic safe OOM injection test is Day 2 |
| Extracted source archive smoke | PASS | 1.12 s pytest | fresh path containing spaces; 61 committed-file hashes and all 13 backend tests passed |

## Observable real-model hashes

- Synthetic input array SHA-256: `f2205b3676133173fa3c9324652a681ca41cac7c32e34d1d786e37e5ebadb647`
- CPU output SHA-256: `68fa9b9ded654a17e523653a9088884477b04462b7c9605ae95f151da9abf49d`
- CUDA output SHA-256: `85694d61d0fce957aac4adc04d892a6bfa7ca05fc9333d2a2266587b91be5e8d`

CPU and CUDA hashes are not expected to be byte-identical because floating-point kernels differ; both passed shape, dtype, finite-value, and range checks.
