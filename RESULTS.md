# Results

No scientific accuracy result is claimed. No ground-truth height dataset was supplied or discovered.

## Engineering results

The deterministic upload-to-artifact path and the separately implemented real-model path are both verified. The CUDA API smoke downloaded every declared artifact and checked its SHA-256 digest. The revised browser workflow rendered a real result from the downloaded 512×512 TIR preview, showed the required domain warning, and displayed the Three.js surface without presenting it as validated TIR science.

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
