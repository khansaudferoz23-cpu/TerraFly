# TerraFly operator guide

This is the practical “open it, fly it, and prove it works” guide. Read `docs/cookbook/TERRAFLY_COOKBOOK.md` when you want the deeper explanation.

## 1. Start TerraFly

### On the computer where setup is already complete

1. Open the TerraFly folder.
2. Double-click `Start-TerraFly.cmd`.
3. Keep the launcher window open.
4. The final release opens `http://127.0.0.1:8000` automatically. It runs only on this computer.

If the app does not open, read the launcher message. Logs are in `runtime\logs`. Do not start random extra terminals or kill unknown processes.

### On a new Windows computer

1. Extract `TerraFly_FINAL_WINDOWS.zip` to a normal folder. Paths containing spaces are supported.
2. Connect to the internet for the one-time dependency/model setup.
3. Open PowerShell in the extracted folder and run:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
   ```

4. Double-click `Start-TerraFly.cmd`.

The setup is large because the real CUDA/CPU ML runtime is several gigabytes. Model weights are not redistributed inside the source release; the real checkpoint is downloaded into the ignored local cache.

## 2. Fastest measured mountain demonstration

1. Keep **DEM Terrain · Recommended** selected.
2. Choose `sample_data\terrafly_terrain_demo_imagery.tif` as the optical texture.
3. Choose `sample_data\terrafly_terrain_demo_dem.tif` as the source DEM.
4. Enter source `TerraFly bundled synthetic mountain DEM`.
5. Enter datum `TerraFly synthetic demo datum`.
6. Select **Build measured terrain** and wait for **Complete · 100%**.
7. Scroll to **Measured terrain analysis**.

Expected state: **Metric Source DEM**. The texture grid is 10 m and the supplied DEM grid is 20 m; the alignment report must say that resampling did not improve the DEM's native information. The pair is a synthetic workflow demonstration, not evidence of real Himalayan accuracy.

For a real judge scene, follow `docs\REAL_TERRAIN_DATA_GUIDE.md` and rehearse the licensed pair before presentation.

### Photo-only comparison

Select **Photo AI · Experimental**, choose `sample_data\terrafly_synthetic_aerial.png`, and select **Generate relative surface**. Expected state: **Relative**. That is correct for a PNG and it must not say metres.

## 3. Move around the 3D model

### Orbit mode

Orbit is best for showing the whole model and comparing points.

| Action | Control |
|---|---|
| Rotate around the scene | Hold left mouse button and drag |
| Pan sideways/up/down | Hold right mouse button and drag |
| Zoom | Mouse wheel/trackpad scroll |
| Select point A | Click once on the surface |
| Select point B | Click a different place |
| Replace point B | Click another place after A and B exist |
| Remove markers | **Clear points** |
| Return to the starting camera | **Reset** |

Before calibration, the point panel shows source pixel coordinates and relative A/B values. After a valid metric pass, choose ground as A and a roof or terrain feature as B: the panel shows metric elevation and vertical difference. It also shows horizontal distance and slope when the GeoTIFF uses projected metre units.

### First-person “drone” mode

1. Select **First-person**.
2. Click inside the 3D viewer to capture the mouse.
3. Use the controls below.

| Movement | Control |
|---|---|
| Look around | Move the mouse |
| Fly forward/back | `W` / `S` or up/down arrows |
| Fly left/right | `A` / `D` or left/right arrows |
| Descend/ascend | `Q` / `E` |
| Faster flight | Hold `Shift` while moving |
| Release mouse | `Esc` |
| Restore camera | Exit with `Esc`, choose **Orbit**, then **Reset** |

This is free-flight inspection. It does not collide with or walk on the surface.

### Other viewer controls

- **Photo / Height colours:** switches between the sharp source-photo texture and a green-to-red height view. The fixed legend says either `relative — not metres` or calibrated metres and shows minimum, midpoint, and maximum values.
- **Wireframe:** exposes the triangles used by the browser surface.
- **Structures:** appears only for Photo AI and shows/hides optional upright footprint extrusions inferred from local relative-height contrast. This Bhuvan-style visual layer may include trees or miss roofs and never changes the DSM. It is intentionally absent in mountain DEM mode.
- **Vertical display:** changes only visual exaggeration from 0.2× to 4×. It never edits the saved `.npy` values.
- **Sun direction:** rotates the simulated directional light so normals and surface relief can be checked under different illumination without changing geometry or measurements.
- **Clear points:** removes A/B markers.
- **Reset:** restores the camera; it does not rerun the model.

## 4. Demonstrate metric calibration

This pair is a software oracle, not real surveyed truth.

1. Choose `sample_data\terrafly_calibration_demo_input.tif`.
2. Select **Generate surface** and wait for completion.
3. Confirm the result says **Georeferenced Relative**. A CRS alone must not unlock metres.
4. In **Metric calibration**, choose `sample_data\terrafly_calibration_demo_reference.tif`.
5. Enter:
   - Evidence source: `Bundled synthetic software oracle`
   - Vertical datum: `Demo benchmark datum`
   - Maximum held-out RMSE: `0.5`
6. Select **Evaluate and calibrate**.

Expected visible result:

- **Passed** and **Metric export unlocked**.
- Scale close to `40.000 m / relative unit`.
- Held-out RMSE close to zero and R² close to `1.000`.
- `metric_surface.tif`, `metric_surface.npy`, `metric_analysis_grid.json`, `calibration_error.tif`, and `calibration_report.json` appear.
- The display shape remains normalized, but A/B point labels now read the validated metric grid. Pick ground then roof/terrain to see metre difference; projected-metre inputs also show horizontal distance and slope.

For real data, replace the demo reference with an independently sourced single-band DSM whose CRS, width, height, and affine pixel grid exactly match the input. Use its true vertical datum and a defensible RMSE threshold.

## 5. Check that everything works

### One-click fast checker

Double-click `Check-TerraFly.cmd`.

Expected final line: **TerraFly verification PASSED**. It checks dependencies, all backend safety/scientific tests, the complete bundled measured-terrain workflow, frontend interactions, and the production build.

### Full real-model checker

Run this in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify.ps1 -Full
```

The full check additionally runs the real model and the entire calibration demo, verifies all artifact hashes, and inspects the metric GeoTIFF contract.

### Visual checklist

- Upload area accepts PNG/JPEG/GeoTIFF and shows the chosen filename.
- Progress reaches **Complete · 100%**.
- The textured 3D model appears without a red error.
- Orbit, zoom, pan, First-person, Q/E, and Shift boost respond.
- Photo/Height colours, Wireframe, and Structures visibly toggle. Height colours show the correct numeric legend; Structures starts off and does not alter the DSM.
- Two orbit clicks show relative A/B before calibration and metric elevation/difference after a pass.
- Provenance shows model revision, device, input hash, and CRS.
- Every evidence link downloads a real file; unavailable files are not shown.
- PNG/JPEG remains **Relative**.
- GeoTIFF without vertical evidence remains **Georeferenced Relative**.
- Only passing calibration becomes **Metric Calibrated**.

## 6. Common problems

| Symptom | Meaning and fix |
|---|---|
| “TerraFly is not set up” | Run `scripts\setup.ps1` once. |
| CMD reports `Key in dictionary: Path / PATH` | Use the current repaired launcher. It normalizes duplicate Windows process-path entries before starting Python. |
| Port 8000 is occupied | Close the older TerraFly launcher or the named conflicting program; do not kill random processes. |
| Service starts but no browser appears | Manually open `http://127.0.0.1:8000`. The repaired launcher keeps the service alive and prints this address even if Windows cannot open the default browser. |
| Model download error | Connect to the internet for the first real run; retry. The cache is under `runtime\model-cache`. |
| CUDA unavailable or out of memory | TerraFly falls back to CPU; processing will be slower. |
| 3D viewer is black/red | Wait for completion, then reload once. Check browser WebGL support and `runtime\logs`. |
| First-person mouse seems trapped | Press `Esc`. This is normal pointer-lock behavior. |
| Calibration rejects alignment | Use the exact same CRS, dimensions, transform, and pixel grid; TerraFly does not silently resample. |
| Calibration rejects quality | Read `calibration_report.json`; fix the reference, coverage, validation independence, threshold, or datum. Never force metres. |
| TIR file shows a warning | Expected. Single-band TIR can execute but is outside this optical model’s validated domain. |

## 7. Stop the app

Return to the launcher window and press `Ctrl+C`, or close that launcher window. Jobs remain under ignored `runtime\jobs` until cleared from the UI or removed deliberately.
