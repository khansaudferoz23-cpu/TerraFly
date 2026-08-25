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
