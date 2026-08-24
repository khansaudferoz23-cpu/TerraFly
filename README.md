# TerraFly

TerraFly converts one optical RGB satellite or aerial image into a **relative surface/depth proxy**, preserves geospatial metadata when a GeoTIFF provides it, and renders the result as a textured interactive 3D height field.

> A PNG or JPG does not contain enough evidence to recover elevation in metres. A georeferenced GeoTIFF adds horizontal location and scale, not a trustworthy vertical scale. TerraFly unlocks metric DSM output only after a documented vertical calibration succeeds.

## Current working path

Upload PNG, JPG/JPEG, or GeoTIFF → validate safely → run an interchangeable inference adapter → save a float32 relative array → create 2D/3D display artifacts → inspect provenance and export results.

The normal adapter is the real Apache-2.0 `depth-anything/Depth-Anything-V2-Small-hf` checkpoint. Automated tests use a deterministic adapter that is technically blocked from normal runs and visibly labels every result as test-only.

## Beginner launch (Windows)

1. Run `scripts\setup.ps1` once in PowerShell. The first setup downloads PyTorch and the web packages.
2. Double-click `Start-TerraFly.cmd`.
3. Open `http://127.0.0.1:5173` if it does not open automatically.

The app binds only to this computer (`127.0.0.1`). Model weights and uploaded/generated jobs stay in ignored local folders.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest
cd frontend
npm test
npm run build
```

Real-model smoke checks are deliberately separate because they download a checkpoint and use substantially more time and storage.

## Layout

- `backend/terrafly`: FastAPI, safe image inspection, model adapters, jobs, manifests, and artifacts.
- `backend/tests`: fast deterministic and geospatial contract tests.
- `frontend`: React/TypeScript/Vite and the Three.js textured surface viewer.
- `scripts`: project-local setup and Windows launcher.
- `runtime/jobs`: ignored uploads and generated results.
- `docs/cookbook`: source index for later evidence-backed cookbook creation.

See `PROJECT_STATUS.md` for verified versus pending work and `LIMITATIONS.md` before making scientific claims.
