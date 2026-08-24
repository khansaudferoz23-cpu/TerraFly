# Results

No scientific accuracy result is claimed. No ground-truth height dataset was supplied or discovered.

## Engineering results

The deterministic upload-to-artifact path and the separately implemented real-model path are both verified. The CUDA API smoke downloaded every declared artifact and checked its SHA-256 digest. The browser test rendered the real CUDA result and Three.js surface.

## Test table

| Test | Command | Result | Duration | Evidence | Environment |
|---|---|---:|---:|---|---|
| Backend fast suite | `.venv\\Scripts\\python.exe -m pytest -q` | PASS | 1.77 s pytest | `handoff/DAY_1_TEST_REPORT.md` | Python 3.12.13 |
| Frontend component | `npm test` | PASS | 19.57 s | `handoff/DAY_1_TEST_REPORT.md` | Node 22.23.1 |
| Frontend production build | `npm run build` | PASS | 0.456 s Vite | `handoff/DAY_1_TEST_REPORT.md` | Vite 8.2.2 |
| Python dependency consistency | `.venv\\Scripts\\python.exe -m pip check` | PASS | <1 s | console + report | isolated `.venv` |
| npm production audit | `npm audit --omit=dev` | PASS | 1.2 s | console + report | lockfile present |
| Real CPU model | `scripts\\smoke_real_model.py --device cpu` | PASS | 34.916 s | `handoff/DAY_1_TEST_REPORT.md` | PyTorch 2.12.1+cu130 |
| Real CUDA model | `scripts\\smoke_real_model.py --device cuda` | PASS | 5.402 s | `handoff/DAY_1_TEST_REPORT.md` | RTX 5060 8 GB |
| Real CUDA API workflow | `scripts\\smoke_real_api.py --device cuda` | PASS | 5.250 s | `handoff/DAY_1_TEST_REPORT.md` | six artifact hashes verified |
| Browser workflow | local app + synthetic upload | PASS | interactive | external screenshot output | real CUDA result + WebGL |
\n