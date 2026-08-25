# Day 2 test report

Status vocabulary is restricted to PASS, FAIL, BLOCKED, or SKIPPED.

| Test | Result | Duration | Evidence |
|---|---:|---:|---|
| Backend upload, artifacts, GLB, tiling, cleanup, memory, and geospatial suite (20) | PASS | 1.10 s | all deterministic contracts and failure paths passed |
| Frontend scientific and asymmetric orientation suite (4) | PASS | 2.05 s | App + pure geometry/pixel sampling tests |
| Strict TypeScript/Vite production build | PASS | 0.359 s | 23 modules transformed |
| Python compilation and dependency consistency | PASS | <3 s | no broken requirements |
| Windows PowerShell launcher parse | PASS | <1 s | zero parser errors |
| Real four-tile CUDA model | PASS | 21.734 s | 320×480 finite float32 output; 4×256 px tiles with 48 px overlap |
| Real CUDA upload-to-seven-artifact API | PASS | 5.101 s | all downloads, including GLB, matched manifest hashes |
| GLB 2.0 binary/container contract | PASS | included | magic/version/length/accessors/relative extras and corner colours parsed |
| Asymmetric image/grid/viewer orientation | PASS | included | top-left/bottom-right geometry, UV, pixel, texture, and GLB assertions |
| Browser real RGB workflow | PASS | interactive | WebGL, orbit/first-person toggle, A/B points, GLB evidence link |
| Phone-size result workflow | PASS | interactive | 390×844; 307 px viewer and canvas matched; no horizontal overflow |
| Browser console after final reload | PASS | interactive | no new warnings or errors after deprecated-clock removal |
| Completed-job deletion | PASS | included | HTTP 204 then job 404; unsafe identifier refused |
| Extracted Day 2 source archive | PASS | 0.78 s pytest | fresh path containing spaces; 72 source hashes and all 20 backend tests passed |

## Real tiled output

- Device: CUDA on RTX 5060.
- Output shape: 320×480.
- Output SHA-256: `636994577c70a199173165a5e119025c4882a2eede3dede0db8709889dde3606`.
- Strategy: 4 tiles, tile size 256, overlap 48, overlap affine alignment, feather blend, global normalization.

No scientific accuracy result is claimed because compatible aligned height truth is still unavailable.
