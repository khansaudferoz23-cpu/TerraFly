# TerraFly

TerraFly provides two deliberately separate paths: **DEM Terrain** combines a georeferenced optical image with a supplied elevation model for credible metric mountain terrain, while **Photo AI** converts one optical image into an explicitly relative surface/depth proxy. Both render as inspectable textured 3D height fields and preserve a traceable evidence bundle.

> A PNG or JPG does not contain enough evidence to recover elevation in metres. A georeferenced GeoTIFF adds horizontal location and scale, not a trustworthy vertical scale. TerraFly unlocks metric DSM output only after a documented vertical calibration succeeds.

## Recommended mountain path: DEM Terrain

Optical GeoTIFF + single-band DEM GeoTIFF → validate source metadata → reproject/resample the DEM onto the optical grid when required → preserve metric values and NoData → normalize a separate display surface → texture and inspect in 3D → export the aligned metric GeoTIFF, `.npy`, GLB, grid, provenance, and alignment report.

This workflow is the default in the interface because it solves the central mountain problem honestly: the DEM supplies geometry and the optical image supplies colour. Reprojection is recorded and never described as improving the DEM's native resolution. AI-oriented roof smoothing and neutral-wall substitution are disabled, so real mountain ridges remain faithful and fully textured. TerraFly validates file structure, spatial coverage, and alignment; it does not independently certify the named DEM's accuracy.

Try it offline with:

- `sample_data/terrafly_terrain_demo_imagery.tif`
- `sample_data/terrafly_terrain_demo_dem.tif`
- Source: `TerraFly bundled synthetic mountain DEM`
- Datum: `TerraFly synthetic demo datum`

The pair is synthetic software evidence, not real-world accuracy evidence. `docs/REAL_TERRAIN_DATA_GUIDE.md` explains how to replace it with licensed Sentinel-2 imagery and NASA SRTM elevation.

## Experimental path: Photo AI

Upload PNG, JPG/JPEG, or GeoTIFF → validate safely → run an interchangeable inference adapter → save a float32 relative array → create 2D/3D display artifacts → inspect provenance and export results.

The normal adapter defaults to the real `depth-anything/Depth-Anything-V2-Large-hf` checkpoint. Its raw output convention is explicit: larger inverse-depth/proximity values map to higher relative surface for near-nadir scenes, with one global robust normalization and no second inversion. Every run preserves the pre-conversion array and writes a global-tilt diagnostic. Large inputs use bounded overlapping tiles with overlap scale/offset alignment and feather blending before normalization. Automated tests use a deterministic adapter that is technically blocked from normal runs and visibly labels every result as test-only. The Large checkpoint is CC-BY-NC-4.0 and does not itself establish remote-sensing height accuracy.

The viewer now uses a separate, recorded display grid: isolated spikes are replaced, an RGB-guided bilateral pass suppresses within-surface noise, conservative raised connected regions are median-flattened, and an adjacent-delta safety cap removes only extreme display faces. Steep triangles receive a neutral wall material instead of stretched top-down image pixels. The portable GLB embeds the source PNG as a UV texture, exports smooth unit normals, and uses lit PBR materials rather than vertex colours or an unlit extension. None of these display operations touch `relative_surface.npy`, `relative_grid.json`, metric calibration, or A/B measurements.

TerraFly 1.0 adds two evidence-driven calibration paths. An exactly aligned reference DSM can be evaluated in the app; surveyed control points plus separate validation points are available through the API. Robust scale/offset fitting, spatially held-out validation, coverage/inlier/RMSE/R² gates, source NoData preservation, and an explicit pass/reject decision prevent a cosmetic “metres” toggle. Only a passing run receives metric `.npy`, analysis-grid, and GeoTIFF artifacts. The display mesh remains a responsive normalized surface, while its A/B inspection reads calibrated elevations, height difference, and—when the source has projected metre units—horizontal distance and slope.

An optional **Structures** control adds a separate Bhuvan-style visual reconstruction layer with upright walls. It is inferred from local relative-height components, remains off by default, never changes the numeric DSM, and is explicitly warned as non-semantic: trees may be included and low-contrast roofs may be missed.

### Metric calibration workflow

1. Upload a georeferenced input GeoTIFF and generate its relative surface.
2. In **Metric calibration**, choose an independently sourced single-band DSM with the exact same CRS, width, height, and affine pixel grid.
3. Name the evidence source and vertical datum, then declare the maximum acceptable held-out RMSE in metres.
4. Select **Evaluate and calibrate**. A pass unlocks the metric GeoTIFF, metric `.npy`, residual GeoTIFF, and machine-readable report. A rejection retains the evidence/report but creates no metric output.

The bundled calibration pair proves software correctness with synthetic truth; it is not a real-world accuracy claim. Real operational use requires trustworthy independently surveyed reference data.

### Why the two paths must remain separate

- DEM Terrain reports metre values because the user supplied a named metric elevation source.
- Photo AI reports relative 0–1 structure because one photograph cannot establish metre scale or hidden terrain.
- Photo AI may unlock calibrated metres only when independent held-out evidence passes the existing gate.
- Building-focused training is a later model-development project; it is not needed to render measured mountain terrain.

## Final Windows launch

1. Run `scripts\setup.ps1` once in PowerShell. The first setup installs dependencies, builds the interface, and downloads model weights when the first real analysis runs.
2. Double-click `Start-TerraFly.cmd`.
3. Keep the launcher window open. TerraFly opens the single production address `http://127.0.0.1:8000` automatically.

The app binds only to this computer (`127.0.0.1`). Model weights and uploaded/generated jobs stay in ignored local folders.

Run `Check-TerraFly.cmd` for the ordinary automated check. For the complete real-model calibration proof, run `scripts\verify.ps1 -Full` in PowerShell.

## Use the 3D viewer

- **Orbit:** left-drag rotates, right-drag pans, and the wheel zooms.
- **Drone-style flight:** select **First-person**, click the 3D scene, use `W/A/S/D`, `Q/E` for down/up, hold `Shift` for faster movement, move the mouse to look, and press `Esc` to release the pointer.
- **Inspect values:** click ground A and roof/terrain B. Relative jobs show relative values; a passing calibration shows elevation and vertical difference in metres. Projected metre CRS inputs also show horizontal distance and slope.
- **Visual controls:** Photo/Height colours, a numeric relative-or-metre legend, simulated sun direction, Wireframe, optional Structures, vertical display exaggeration, Clear points, and Reset affect inspection only; they never alter the saved numeric array.

The exact bundled metric demos and troubleshooting steps are in `docs/OPERATOR_GUIDE.md`.

## Understand before presenting

- `docs/TEAM_TECHNICAL_GUIDE.md`: architecture, outputs, model limits, SAC sample distinction, judge answers, and team learning split.
- `docs/PS_REQUIREMENTS_TRACEABILITY.md`: official problem-statement requirement-by-requirement implementation and limitation map.
- `docs/OPERATOR_GUIDE.md`: launch, orbit/drone controls, bundled calibration demo, checks, and troubleshooting.
- `docs/REAL_TERRAIN_DATA_GUIDE.md`: how to obtain and prepare a licensed real mountain imagery/DEM pair.
- `docs/TRAINING_ROADMAP.md`: gated DFC23 building-height training plan for the later model phase.
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

The first command runs dependency, backend, frontend, production-build, and bundled measured-terrain workflow checks. `-Full` also runs the real Depth Anything V2 CUDA/CPU calibration workflow and verifies every declared artifact hash plus metric GeoTIFF metadata.

## Layout

- `backend/terrafly`: FastAPI, safe image inspection, model adapters, jobs, manifests, artifacts, and calibration gates.
- `backend/tests`: deterministic inference, geospatial, artifact, tiling, and calibration pass/reject contracts.
- `frontend`: React/TypeScript/Vite and the Three.js textured surface viewer.
- `scripts`: setup, single-server Windows launch, final verification, fixtures, and packaging.
- `runtime/jobs`: ignored uploads and generated results.
- `docs/cookbook`: final evidence-backed cookbook and its source index.

See `PROJECT_STATUS.md` for verified versus pending work and `LIMITATIONS.md` before making scientific claims.
