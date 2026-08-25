# TerraFly

TerraFly converts one optical RGB satellite or aerial image into a **relative surface/depth proxy**, preserves geospatial metadata when a GeoTIFF provides it, and renders the result as an inspectable 3D height field.

> A PNG or JPG does not contain enough evidence to recover elevation in metres. A georeferenced GeoTIFF adds horizontal location and scale, not a trustworthy vertical scale. TerraFly unlocks metric DSM output only after a documented vertical calibration succeeds.

## Current working path

Upload PNG, JPG/JPEG, or GeoTIFF → validate safely → run an interchangeable inference adapter → save a float32 relative array → create 2D/3D display artifacts → inspect provenance and export results.

The normal adapter is the real Apache-2.0 `depth-anything/Depth-Anything-V2-Small-hf` checkpoint. Large inputs use bounded overlapping tiles with overlap scale/offset alignment and feather blending before one global normalization. Automated tests use a deterministic adapter that is technically blocked from normal runs and visibly labels every result as test-only.

Day 3 adds two evidence-driven calibration paths. An exactly aligned reference DSM can be evaluated in the app; surveyed control points plus separate validation points are available through the API. Robust scale/offset fitting, spatially held-out validation, coverage/inlier/RMSE/R² gates, source NoData preservation, and an explicit pass/reject decision prevent a cosmetic “metres” toggle. Only a passing run receives metric `.npy` and GeoTIFF artifacts. The 3D viewer deliberately remains relative.

### Metric calibration workflow

1. Upload a georeferenced input GeoTIFF and generate its relative surface.
2. In **Metric calibration**, choose an independently sourced single-band DSM with the exact same CRS, width, height, and affine pixel grid.
3. Name the evidence source and vertical datum, then declare the maximum acceptable held-out RMSE in metres.
4. Select **Evaluate and calibrate**. A pass unlocks the metric GeoTIFF, metric `.npy`, residual GeoTIFF, and machine-readable report. A rejection retains the evidence/report but creates no metric output.

The included Day 3 fixture proves software correctness with synthetic truth; it is not a real-world accuracy claim. Real operational use requires trustworthy independently surveyed reference data.

## Beginner launch (Windows)

1. Run `scripts\setup.ps1` once in PowerShell. The first setup downloads PyTorch and the web packages.
2. Double-click `Start-TerraFly.cmd`.
3. Keep the launcher window open. TerraFly waits for both services and opens `http://127.0.0.1:5173` automatically.

The app binds only to this computer (`127.0.0.1`). Model weights and uploaded/generated jobs stay in ignored local folders.

## Understand before presenting

- `docs/TEAM_TECHNICAL_GUIDE.md`: architecture, outputs, model limits, SAC sample distinction, judge answers, and team learning split.
- `FILE_GUIDE.md`: why every tracked source/config/test/document exists.
- `docs/UX_RATIONALE.md`: what was wrong and right in the first interface and why the revised design looks the way it does.
- `DATA_SOURCES.md`: exact source commits, local sample hashes, and the boundary between thermal/colorization data and height ground truth.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest
cd frontend
npm test
npm run build
```

Real-model smoke checks are deliberately separate because they download a checkpoint and use substantially more time and storage.

## Layout

- `backend/terrafly`: FastAPI, safe image inspection, model adapters, jobs, manifests, artifacts, and calibration gates.
- `backend/tests`: deterministic inference, geospatial, artifact, tiling, and calibration pass/reject contracts.
- `frontend`: React/TypeScript/Vite and the Three.js textured surface viewer.
- `scripts`: project-local setup and Windows launcher.
- `runtime/jobs`: ignored uploads and generated results.
- `docs/cookbook`: source index for later evidence-backed cookbook creation.

See `PROJECT_STATUS.md` for verified versus pending work and `LIMITATIONS.md` before making scientific claims.
