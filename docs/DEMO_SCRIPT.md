# TerraFly final demo script

Target length: 6–8 minutes. Rehearse once with `docs/OPERATOR_GUIDE.md` open nearby.

## Before judges arrive

1. Run `Check-TerraFly.cmd`; photograph or keep the PASS result available.
2. Start TerraFly with `Start-TerraFly.cmd`.
3. Confirm the app opens at `http://127.0.0.1:8000`.
4. Keep the two calibration demo GeoTIFFs easy to find under `sample_data`.
5. Do not depend on internet during the presentation after the model cache is ready.

## 0:00–0:40 — problem and promise

Say:

> “TerraFly turns one optical image into a traceable relative 3D surface. A single image cannot honestly prove elevation in metres, so metric files stay locked until independent vertical evidence passes held-out quality gates.”

Point to **Output scope**. Explain the three states: Relative, Georeferenced Relative, Metric Calibrated.

## 0:40–2:00 — generate the real result

1. Upload `sample_data\terrafly_calibration_demo_input.tif`.
2. Select **Generate surface**.
3. As progress moves, say: validation → preprocessing → real Depth Anything V2 inference → mesh/evidence.
4. On completion, point out **Georeferenced Relative**, model revision, device, input hash, and CRS.

Say:

> “The CRS locates pixels horizontally. It still does not provide vertical scale or datum, so TerraFly correctly refuses metres here.”

## 2:00–3:20 — inspect in 3D like a drone

1. Orbit with left drag, pan with right drag, and zoom.
2. Switch between **Photo** and **Height colours**; point out the numeric `relative — not metres` legend, then toggle **Wireframe**.
3. Toggle **Structures** and explain that its clean upright objects are a separate Bhuvan-style visual candidate layer, not a DSM correction or building truth.
4. Move the vertical display slider and the simulated sun direction; state that both change display only.
5. Click two points in Orbit; show relative A/B values and pixel coordinates.
6. Choose **First-person**, click the viewer, mouse-look, fly with W/A/S/D, ascend with E, descend with Q, hold Shift for boost, and press Escape.

Say:

> “This is a responsive inspection mesh. RGB-guided cleanup calms noisy roofs, and neutral steep faces prevent the top-down photograph from dripping down walls. The untouched `.npy` and analysis grid remain the measurement sources; the GLB and viewer never pretend to be surveyed geometry.”

## 3:20–5:00 — prove the metric gate

1. Upload `terrafly_calibration_demo_reference.tif` in the calibration panel.
2. Evidence source: `Bundled synthetic software oracle`.
3. Vertical datum: `Demo benchmark datum`.
4. Maximum held-out RMSE: `0.5`.
5. Select **Evaluate and calibrate**.
6. Show Passed, scale near 40, RMSE near zero, R² near 1, datum, and new metric/error files.
7. Click a ground-like point then a raised feature. Show calibrated elevation and vertical difference. If the projected-metre input yields horizontal separation, show distance and slope.

Immediately disclose:

> “This reference was derived from the output with a known relation and training-only outliers. It proves our robust calibration software, not real-world model accuracy. Real claims require independent surveyed truth.”

## 5:00–6:20 — reproducibility and safety

Show the evidence list and explain:

- `.npy` is lossless numeric data; PNG is a visual preview.
- GLB is portable relative 3D; it embeds the source image as a real UV texture, exports smooth normals and lit PBR materials, and keeps steep faces synthetic-neutral.
- Manifest records input, model/device/revision, warnings, and hashes.
- Metric GeoTIFF preserves CRS, grid, NoData, metre units, datum, and source.
- Error map is estimate minus reference.
- Bad/misaligned evidence produces a rejection report and no metric file.

Mention the current backend/frontend counts and real CUDA artifact totals from `handoff/FINAL_TEST_REPORT.md`; do not memorize an older number after changing the artifact contract.

## 6:20–7:00 — AI-assisted development answer

Say:

> “We used AI-assisted development and we own the result. We can trace a request through the API, model, artifacts, UI, calibration gate, and tests; explain why every file exists; reproduce the build; and state what the system does not prove.”

End with the limitation and next scientific step: obtain independent, aligned, surveyed remote-sensing ground truth and evaluate spatially held-out real scenes.

## Never say

- “The PNG gives elevation.”
- “The AI knows building height.”
- “The synthetic RMSE is our model accuracy.”
- “The SAC thermal `.npy` files are our height labels.”
- “The display exaggeration changes the data.”
- “Calibration passed because the screen turned green.”
- “Structures are verified buildings.”
- “TerraFly predicts disasters.”

Use the measured report, artifact files, and gate criteria instead.
