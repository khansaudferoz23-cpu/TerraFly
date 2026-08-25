# TerraFly file guide

Use this as the answer to “why does this file exist?” Paths are grouped by responsibility. Machine-generated runtime folders are explained at the end.

## Root: project contract and operation

| File | Purpose and reason to keep it |
|---|---|
| `.env.example` | Documents optional environment settings without committing real secrets. Copy to `.env` only when a local override is needed. |
| `.gitattributes` | Normalizes committed text line endings so Windows/Linux checkouts and release hashes are predictable. |
| `.gitignore` | Prevents environments, model weights, uploads, generated jobs, credentials, builds, and archives from entering Git. |
| `README.md` | First-run explanation, launch steps, verified commands, architecture summary, and links to deeper guides. |
| `FILE_GUIDE.md` | This repository ledger; gives every tracked file an explicit owner and purpose. |
| `PROJECT_STATUS.md` | Separates implemented/verified work from future work so the team never overclaims completion. |
| `FOUR_DAY_PLAN.md` | Orders work by risk: stable relative path, 3D robustness, calibration/evaluation, then release proof. |
| `DECISIONS.md` | Records why important choices were made so they are not mistaken for arbitrary AI output. |
| `DATA_SOURCES.md` | Records exact dataset/model provenance and what data has *not* been obtained. |
| `LEARNING_NOTES.md` | Beginner explanations of depth, height, GeoTIFF metadata, adapters, and display exaggeration. |
| `LIMITATIONS.md` | Scientific and engineering boundaries that must be disclosed to judges/users. |
| `RESULTS.md` | Dated verification evidence and measured smoke-test results. |
| `BUILD_LOG.md` | Chronological implementation/testing record for handoff and debugging. |
| `THIRD_PARTY_NOTICES.md` | Names third-party model/code licenses and prevents accidental license misrepresentation. |
| `pyproject.toml` | Python package metadata, pinned runtime/test dependencies, pytest configuration, and source path. |
| `requirements-ml-cu130.txt` | Explicit CUDA 13.0 PyTorch installation set for the observed RTX 5060 environment. |
| `Start-TerraFly.cmd` | Beginner Windows entry point; changes into the repository and invokes the PowerShell launcher. |
| `Check-TerraFly.cmd` | Beginner Windows verification entry point; keeps the window open and reports the final automated gate clearly. |

## Backend: application and scientific pipeline

| File | Purpose and reason to keep it |
|---|---|
| `backend/terrafly/__init__.py` | Marks `terrafly` as a Python package and exposes the package version boundary. |
| `backend/terrafly/config.py` | Central settings for job storage, upload/memory/tile limits, model ID, adapter, device, and test safety flag. |
| `backend/terrafly/schemas.py` | Pydantic contracts for scientific states, jobs, artifacts, capabilities, and bounded GCP calibration requests; stops undocumented API shapes. |
| `backend/terrafly/main.py` | FastAPI routes for health, capabilities, upload, status, calibration, safe artifact download, completed-job deletion, and final prebuilt-interface serving. |
| `backend/terrafly/imaging.py` | Filename/content validation, safe decoding, RGB normalization, GeoTIFF inspection, hashes, and single-band warnings. |
| `backend/terrafly/jobs.py` | Creates per-run IDs/directories and atomically persists live job state. |
| `backend/terrafly/pipeline.py` | Enforces the processing-memory budget, orchestrates validation → inference → artifacts, and converts failures into honest job states. |
| `backend/terrafly/artifacts.py` | Preserves raw/numeric output, writes preview, texture, 16-bit, orientation-aware viewer grid, valid GLB, height/tilt diagnostics, and SHA-256 records. |
| `backend/terrafly/calibration.py` | Validates reference grids/GCPs, robustly fits scale and offset, performs held-out quality gates, preserves NoData, and writes metric/error evidence only on pass. |
| `backend/terrafly/inference/__init__.py` | Marks the inference adapter directory as a package. |
| `backend/terrafly/inference/base.py` | Defines the common prediction result and adapter interface used by real and test implementations. |
| `backend/terrafly/inference/conventions.py` | Defines raw output meanings and performs the single tested conversion to normalized relative height. |
| `backend/terrafly/inference/depth_anything_v2.py` | Real pretrained inference, explicit inverse-depth/proximity convention, CUDA/CPU selection, and OOM fallback. |
| `backend/terrafly/inference/deterministic.py` | Fast repeatable test implementation; fenced and labelled so it cannot masquerade as production science. |
| `backend/terrafly/inference/factory.py` | Chooses an adapter from settings and enforces the test-adapter safety interlock. |
| `backend/terrafly/inference/tiling.py` | Plans bounded overlapping tiles, aligns crop scale/offset, feather-blends raw predictions, and refuses excessive tile counts. |

## Backend tests: evidence that failure paths work

| File | Purpose and reason to keep it |
|---|---|
| `backend/tests/__init__.py` | Makes relative test imports consistent on Windows and extracted release paths. |
| `backend/tests/conftest.py` | Creates isolated temporary settings, FastAPI client, and synthetic encoded images for tests. |
| `backend/tests/test_adapter_contract.py` | Verifies one-pass output conversion, raised-building ordering, finite output, and the test-adapter production interlock. |
| `backend/tests/test_api.py` | Tests valid modes, numeric artifacts/hashes, single-band/TIR warnings, corrupt/unsafe/oversized rejection, and metric refusal. |
| `backend/tests/test_geotiff.py` | Proves CRS/transform/NoData survive while vertical metric claims remain locked. |
| `backend/tests/test_artifacts.py` | Parses GLB and proves grid/texture orientation, diagnostic provenance, and that a synthetic roof exports above flat ground. |
| `backend/tests/test_tiling.py` | Proves coverage, overlap blending, affine scale/offset alignment, and maximum-tile refusal. |
| `backend/tests/test_calibration.py` | Proves reference-DSM pass, outlier robustness, alignment refusal, poor-evidence rejection, GCP validation, metric metadata, and hashes. |

## Frontend: user experience and 3D inspection

| File | Purpose and reason to keep it |
|---|---|
| `frontend/index.html` | Minimal HTML mount point and browser metadata for the React application. |
| `frontend/package.json` | Frontend dependencies and the `dev`, `test`, and `build` commands. |
| `frontend/package-lock.json` | Exact transitive npm dependency graph for repeatable installation; generated but intentionally committed. |
| `frontend/vite.config.ts` | Local-only Vite server, strict port, FastAPI proxy, React plugin, and Vitest environment. |
| `frontend/tsconfig.json` | TypeScript project-reference entry point. |
| `frontend/tsconfig.app.json` | Strict TypeScript settings for browser application source. |
| `frontend/tsconfig.node.json` | TypeScript settings for Vite configuration code running in Node. |
| `frontend/src/main.tsx` | Creates the React root and mounts `App`. |
| `frontend/src/App.tsx` | Complete upload/progress/result/calibration/evidence workflow with visible Locked/Passed/Rejected decisions. |
| `frontend/src/SurfaceViewer.tsx` | Three.js render lifecycle, orbit/first-person controls, raycast point markers, loading/error state, and display-only exaggeration. |
| `frontend/src/surfaceGeometry.ts` | Pure orientation, mesh-building, pixel mapping, and bilinear point-sampling logic separated for direct tests. |
| `frontend/src/api.ts` | Typed boundary for jobs, reference calibration, cleanup, and artifact URLs. |
| `frontend/src/types.ts` | TypeScript mirror of job, artifact, scientific-state, fit, evaluation, and gate responses. |
| `frontend/src/styles.css` | Deliberate design tokens, layout hierarchy, responsive behavior, and viewer styling. |
| `frontend/src/App.test.tsx` | Guards the non-metric promise, clean initial state, real file-selection action, and absence of fake future controls. |
| `frontend/src/SurfaceViewer.test.ts` | Guards asymmetric image-to-geometry/UV orientation and source-pixel point sampling. |
| `frontend/src/test-setup.ts` | Loads DOM matchers used by Vitest/Testing Library. |

## Scripts: setup, launch, fixtures, and smoke evidence

| File | Purpose and reason to keep it |
|---|---|
| `scripts/setup.ps1` | Creates the local Python environment, installs Python/frontend dependencies, and builds the final interface without changing global Python. |
| `scripts/start.ps1` | Reuses a healthy TerraFly 1.0 service, refuses unknown port owners, serves the prebuilt interface/API at one address, records readable logs, opens the browser, and stops only children it started. |
| `scripts/verify.ps1` | Runs dependency, backend, frontend, production-build, health, and optional full real-model calibration checks behind one command. |
| `scripts/package_release.ps1` | Creates the tracked-source ZIP, Windows source/prebuilt-interface folder and ZIP, and SHA-256 checksum record without overwriting an existing release. |
| `scripts/smoke_final_workflow.py` | Executes the real GeoTIFF → relative → aligned-reference → metric path and verifies all 13 hashes plus metre/CRS GeoTIFF tags. |
| `scripts/smoke_real_model.py` | Measures a direct real-model inference and records device/revision/output statistics. |
| `scripts/smoke_real_api.py` | Exercises the complete real upload-to-artifacts API path for the bundled or a supplied scene, including every hash. |
| `scripts/smoke_tiled_model.py` | Forces four real CUDA tiles and verifies strategy metadata, shape, range, dtype, finiteness, and output hash. |
| `scripts/create_offline_sample.py` | Regenerates the deterministic CC0 orientation/workflow fixture from code. |
| `scripts/create_calibration_demo.py` | Reproducibly creates the bundled georeferenced input/reference software-oracle pair and its metadata; never claims survey truth. |
| `scripts/create_handoff_manifest.py` | Hashes all committed source files into the final handoff manifest and records the verified environment/model/test boundary. |

## Documentation: team ownership and later evidence

| File | Purpose and reason to keep it |
|---|---|
| `docs/TEAM_TECHNICAL_GUIDE.md` | Architecture, output meanings, technology roles, SAC distinction, judge answers, and team learning split. |
| `docs/UX_RATIONALE.md` | What was right/wrong with the first UI and the human design rationale for the revision. |
| `docs/cookbook/COOKBOOK_SOURCE_INDEX.md` | Curated evidence/source index reserved for the later requested cookbook deliverable. |
| `docs/cookbook/TERRAFLY_COOKBOOK.md` | Final team cookbook explaining the promise, architecture, inference, files, calibration math, tests, limitations, and judge defence. |
| `docs/OPERATOR_GUIDE.md` | Exact setup/launch, 3D orbit and drone controls, bundled calibration run, visual checks, and troubleshooting. |
| `docs/ARCHITECTURE.md` | Compact diagrams for runtime ownership, state transitions, evidence gating, and file responsibilities. |
| `docs/DEMO_SCRIPT.md` | Timed 6–8 minute judge demonstration with exact clicks, spoken claims, and fallback path. |
| `docs/JUDGE_QA.md` | Defensible short answers to scientific, UI, architecture, AI-use, `.npy`, and limitation questions. |

## Sample data

| File | Purpose and reason to keep it |
|---|---|
| `sample_data/terrafly_synthetic_aerial.png` | Small deterministic asymmetric scene for offline orientation/workflow checks; explicitly not real remote sensing or height truth. |
| `sample_data/README.md` | Explains exactly how the fixture may and may not be used. |
| `sample_data/LICENSE.txt` | CC0 declaration for the generated fixture so redistribution is unambiguous. |
| `sample_data/terrafly_calibration_demo_input.tif` | Small georeferenced RGB input used to exercise the final aligned-reference workflow. |
| `sample_data/terrafly_calibration_demo_reference.tif` | Pixel-aligned synthetic software oracle for gate/metadata testing only; never real ground truth. |
| `sample_data/terrafly_calibration_demo_metadata.json` | Reproducibility facts, generator relation, hashes, model revision, and disclaimer for the pair. |

The downloaded SAC TIR/RGB preview PNGs are **not committed** here because they belong to a separate challenge repository and no project license was supplied. Their source, hashes, dimensions, and meanings are recorded in `DATA_SOURCES.md`.

## Handoff evidence

| File | Purpose and reason to keep it |
|---|---|
| `handoff/DAY_1_HANDOFF.md` | Human-readable milestone scope, launch instructions, verified evidence, and known limits. |
| `handoff/DAY_1_TEST_REPORT.md` | Compact record of automated, real-model, GPU, browser, and extracted-archive checks. |
| `handoff/DAY_1_MANIFEST.json` | Machine-readable SHA-256 list of committed source files; regenerated after final changes. |
| `handoff/DAY_2_HANDOFF.md` | Day 2 launch, working-feature, next-step, and known-limit summary. |
| `handoff/DAY_2_TEST_REPORT.md` | Day 2 automated, real tiled CUDA, API artifact, browser, responsive, and launcher evidence. |
| `handoff/DAY_2_MANIFEST.json` | Machine-readable SHA-256 list for the final Day 2 source revision. |
| `handoff/DAY_3_HANDOFF.md` | Day 3 calibration contract, launch, evidence, limits, and Day 4 entry point. |
| `handoff/DAY_3_TEST_REPORT.md` | Day 3 automated, real-model browser, metric-artifact, rejection, and responsive evidence. |
| `handoff/DAY_3_MANIFEST.json` | Machine-readable SHA-256 list for the final Day 3 source revision. |
| `handoff/FINAL_HANDOFF.md` | Human final handoff: what is done, exact launch/demo/check sequence, release files, and remaining scientific boundary. |
| `handoff/FINAL_TEST_REPORT.md` | Final automated, real-model, browser, responsive, launcher, artifact, archive, and extracted-folder evidence. |
| `handoff/FINAL_MANIFEST.json` | Machine-readable SHA-256 list of the final committed source plus environment/test/model record. |

## Generated but intentionally untracked

| Path | Why it stays outside Git |
|---|---|
| `.venv/` | Large machine-specific Python environment that setup can recreate. |
| `frontend/node_modules/` and repository `frontend/dist/` | Recreated from the lockfile/source; `dist` is copied into the Windows release ZIP so final operation needs no Vite server. |
| `runtime/model-cache/` | Downloaded model weights are large third-party binaries. |
| `runtime/jobs/` | Contains user uploads and generated outputs; may be private and is not source code. |
| `outputs/*.zip` | Release deliverables are derived artifacts with separate checksums, not editable source. |

## Safe removal rule

Before deleting a tracked file, answer all three questions:

1. Which code, test, setup step, document, or evidence record consumes it?
2. Can it be reproducibly regenerated, and from what source?
3. Does deleting it weaken the scientific contract, licensing, security, or judge explanation?

If the team cannot answer, inspect `rg <filename-or-symbol>` and the relevant section above before changing anything.
