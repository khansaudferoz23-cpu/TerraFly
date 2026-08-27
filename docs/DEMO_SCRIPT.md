# TerraFly final demo script

Target length: 6–8 minutes. Lead with measured mountain terrain, not a boxy city or an unsupported screenshot reconstruction.

## Before judges arrive

1. Run `Check-TerraFly.cmd`; keep the PASS result available.
2. Start TerraFly with `Start-TerraFly.cmd` and confirm `http://127.0.0.1:8000`.
3. Keep the two `terrafly_terrain_demo_*.tif` files and the two calibration demo GeoTIFFs easy to find.
4. If using real terrain, rehearse that exact pair once and keep its source/attribution visible.
5. Do not depend on internet during the presentation.

## 0:00–0:40 — problem and two honest paths

Say:

> “A photograph provides colour but not reliable elevation. TerraFly therefore has two separate workflows. DEM Terrain uses a named elevation source for measured mountains; Photo AI estimates only relative shape until independent calibration passes.”

Point to **DEM Terrain — Recommended** and **Photo AI — Experimental**.

## 0:40–2:15 — build the mountain hero result

1. Keep **DEM Terrain** selected.
2. Upload `sample_data\terrafly_terrain_demo_imagery.tif` as optical texture.
3. Upload `sample_data\terrafly_terrain_demo_dem.tif` as source DEM.
4. Source: `TerraFly bundled synthetic mountain DEM`.
5. Datum: `TerraFly synthetic demo datum`.
6. Select **Build measured terrain**.

Say:

> “The texture is 10 metre grid imagery and the DEM is a coarser 20 metre grid. TerraFly aligns the DEM, but explicitly records that resampling does not create higher-resolution evidence.”

Immediately disclose that the bundled pair is a synthetic software demonstration. For the final real-world presentation, replace it with the licensed pair prepared through `REAL_TERRAIN_DATA_GUIDE.md`.

## 2:15–3:45 — inspect metric terrain

1. Orbit and zoom; compare **Photo** and **Height colours**.
2. Move the simulated sun and show that steep mountain slopes remain textured.
3. Toggle Wireframe so judges see that the surface is a real height mesh.
4. Click valley A and ridge B. Show both elevations, vertical difference, horizontal distance, and slope.
5. Briefly enter First-person mode if time allows.

Say:

> “The DEM controls geometry and metre values; the optical image controls colour. Display normalization and exaggeration never change the saved elevation.”

## 3:45–4:40 — prove provenance

Open the run provenance and evidence bundle. Show:

- Source DEM hash and original file.
- Aligned metric `.npy` and GeoTIFF.
- `terrain_alignment_report.json` with both grids, coverage, resampling method, source, and datum.
- Textured GLB with embedded image, UVs, normals, and lit material.

Say:

> “TerraFly validates file structure and alignment. The named DEM provider remains responsible for source accuracy; we never call resampled 30 metre data ten metre truth.”

## 4:40–5:35 — show the experimental AI boundary

Clear the result and select **Photo AI**. Explain that a screenshot can produce an interesting relative visualization but not Google Earth-quality measured terrain. If time permits, upload `terrafly_synthetic_aerial.png` and generate it.

Point out `relative — not metres`, model revision, device, input hash, and warnings.

Say:

> “This path is useful for rapid visual hypothesis generation. It is not our measured mountain claim.”

## 5:35–6:35 — prove the metric calibration gate

Use the bundled calibration input/reference and follow the form values in `OPERATOR_GUIDE.md`. Show that Photo AI-derived metric files appear only after held-out checks pass.

Immediately disclose:

> “This reference was derived from the output with a known relation and training-only outliers. It proves calibration software, not real-world model accuracy.”

## 6:35–7:15 — future training answer

Say:

> “Mountains are solved through evidence-backed DEM geometry. Urban photo-only improvement is a separate model-training phase using aligned overhead RGB/SAR, building masks, and nDSM labels split by city. We will not train on unrelated images and height files or on our own predictions.”

Reference `TRAINING_ROADMAP.md` and the DFC23 data gate.

## Never say

- “Google Earth generated this for us.”
- “A screenshot contains true mountain elevation.”
- “Resampling improves DEM resolution.”
- “The bundled synthetic pair proves Himalayan accuracy.”
- “The AI knows building height.”
- “The synthetic calibration RMSE is model accuracy.”
- “Structures are verified buildings.”
- “TerraFly predicts disasters.”
