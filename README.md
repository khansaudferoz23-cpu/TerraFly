# TerraFly

TerraFly converts one optical RGB satellite or aerial image into a **relative surface/depth proxy**, preserves geospatial metadata when a GeoTIFF provides it, and renders the result as an inspectable 3D height field.

> A PNG or JPG does not contain enough evidence to recover elevation in metres. A georeferenced GeoTIFF adds horizontal location and scale, not a trustworthy vertical scale. TerraFly unlocks metric DSM output only after a documented vertical calibration succeeds.

## Current working path

Upload PNG, JPG/JPEG, or GeoTIFF → validate safely → run an interchangeable inference adapter → save a float32 relative array → create 2D/3D display artifacts → inspect provenance and export results.

The normal adapter is the real Apache-2.0 `depth-anything/Depth-Anything-V2-Small-hf` checkpoint. Large inputs use bounded overlapping tiles with overlap scale/offset alignment and feather blending before one global normalization. Automated tests use a deterministic adapter that is technically blocked from normal runs and visibly labels every result as test-only.

TerraFly 1.0 adds two evidence-driven calibration paths. An exactly aligned reference DSM can be evaluated in the app; surveyed control points plus separate validation points are available through the API. Robust scale/offset fitting, spatially held-out validation, coverage/inlier/RMSE/R² gates, source NoData preservation, and an explicit pass/reject decision prevent a cosmetic “metres” toggle. Only a passing run receives metric `.npy` and GeoTIFF artifacts. The 3D viewer deliberately remains relative.

### Metric calibration workflow

1. Upload a georeferenced input GeoTIFF and generate its relative surface.
2. In **Metric calibration**, choose an independently sourced single-band DSM with the exact same CRS, width, height, and affine pixel grid.
3. Name the evidence source and vertical datum, then declare the maximum acceptable held-out RMSE in metres.
4. Select **Evaluate and calibrate**. A pass unlocks the metric GeoTIFF, metric `.npy`, residual GeoTIFF, and machine-readable report. A rejection retains the evidence/report but creates no metric output.

The bundled calibration pair proves software correctness with synthetic truth; it is not a real-world accuracy claim. Real operational use requires trustworthy independently surveyed reference data.

## Final Windows launch

1. Run `scripts\setup.ps1` once in PowerShell. The first setup installs dependencies, builds the interface, and downloads model weights when the first real analysis runs.
2. Double-click `Start-TerraFly.cmd`.
3. Keep the launcher window open. TerraFly opens the single production address `http://127.0.0.1:8000` automatically.

The app binds only to this computer (`127.0.0.1`). Model weights and uploaded/generated jobs stay in ignored local folders.

Run `Check-TerraFly.cmd` for the ordinary automated check. For the complete real-model calibration proof, run `scripts\verify.ps1 -Full` in PowerShell.

## Use the 3D viewer

- **Orbit:** left-drag rotates, right-drag pans, and the wheel zooms.
- **Drone-style flight:** select **First-person**, click the 3D scene, use `W/A/S/D`, `Q/E` for down/up, hold `Shift` for faster movement, move the mouse to look, and press `Esc` to release the pointer.
- **Inspect values:** click two surface locations for A/B relative values and their difference. These are never labelled as metres.
- **Visual controls:** Texture, Wireframe, vertical display exaggeration, Clear points, and Reset affect inspection only; they never alter the saved numeric array.

The exact bundled metric demo and troubleshooting steps are in `docs/OPERATOR_GUIDE.md`.

## Understand before presenting

- `docs/TEAM_TECHNICAL_GUIDE.md`: architecture, outputs, model limits, SAC sample distinction, judge answers, and team learning split.
- `docs/OPERATOR_GUIDE.md`: launch, orbit/drone controls, bundled calibration demo, checks, and troubleshooting.
- `docs/cookbook/TERRAFLY_COOKBOOK.md`: final explain-everything cookbook for the team.
- `docs/DEMO_SCRIPT.md` and `docs/JUDGE_QA.md`: the presentation sequence and defence answers.
- `docs/ARCHITECTURE.md`: runtime, state, evidence-gate, and ownership diagrams.
- `FILE_GUIDE.md`: why every tracked source/config/test/document exists.
- `docs/UX_RATIONALE.md`: what was wrong and right in the first interface and why the revised design looks the way it does.
- `DATA_SOURCES.md`: exact source commits, local sample hashes, and the boundary between thermal/colorization data and height ground truth.

## Verification

```powershell
.\scripts\verify.ps1
.\scripts\verify.ps1 -Full
```

The first command runs dependency, backend, frontend, and production-build checks. `-Full` also runs the real Depth Anything V2 CUDA/CPU calibration workflow and verifies every declared artifact hash plus metric GeoTIFF metadata.

## Layout

- `backend/terrafly`: FastAPI, safe image inspection, model adapters, jobs, manifests, artifacts, and calibration gates.
- `backend/tests`: deterministic inference, geospatial, artifact, tiling, and calibration pass/reject contracts.
- `frontend`: React/TypeScript/Vite and the Three.js textured surface viewer.
- `scripts`: setup, single-server Windows launch, final verification, fixtures, and packaging.
- `runtime/jobs`: ignored uploads and generated results.
- `docs/cookbook`: final evidence-backed cookbook and its source index.

See `PROJECT_STATUS.md` for verified versus pending work and `LIMITATIONS.md` before making scientific claims.
