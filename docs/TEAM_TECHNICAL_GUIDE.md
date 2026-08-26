# TerraFly team technical guide

Read this before presenting the project. The goal is not to memorize code; it is to understand the chain of evidence well enough to explain every decision honestly.

## The 30-second explanation

TerraFly accepts one PNG, JPEG, or GeoTIFF. It validates the file and runs Depth Anything V2 Small, which estimates **relative monocular depth**, not physical elevation. TerraFly creates a 0–1 surface and an interactive 3D inspection view. A georeferenced run may then be calibrated only with independent vertical evidence. Robust scale/offset fitting and held-out quality gates decide whether separate metric GeoTIFF/`.npy` files exist; after a pass, A/B inspection reads a separate metric analysis grid while the display geometry remains normalized.

## Request flow

```text
Browser
  │ POST /api/jobs (one image)
  ▼
FastAPI validation ── rejects unsafe name/format/size/pixel count
  │
  ├─ records image metadata, hash, CRS/transform when present
  ▼
Inference adapter ── Depth Anything V2 Small on CUDA, CPU fallback
  │ large input: bounded overlap tiles → affine align → feather blend
  ▼
Raw output ── preserve `.npy` → apply declared convention once → relative 0–1 surface
  ▼
Artifact writer ── .npy + preview + texture + viewer grid + optional structure candidates + GLB + manifest
  ▼
React polls progress ── Three.js renders orbit/first-person inspection + A/B samples

Georeferenced completed job
  │ aligned DSM OR control + separate validation GCPs
  ▼
Calibration gate ── robust fit → held-out RMSE/MAE/bias/p95/R² + coverage/inliers
  ├─ reject: report only; state stays Georeferenced Relative
  └─ pass: metric .npy + analysis grid + GeoTIFF + residual evidence; state becomes Metric Calibrated
```

## Why the result is relative

A single image is a 2D projection. Many physically different 3D scenes can produce similar pixels, so one uncalibrated image cannot establish an absolute vertical scale or offset. Depth Anything V2 estimates ordering and structure from learned visual cues. TerraFly therefore stores values between 0 and 1 and refuses to label them metres.

A GeoTIFF can add a coordinate reference system, pixel size, map position, and bounds. Those are horizontal facts. They still do not prove vertical scale, vertical datum, or elevation.

## Why each runtime output exists

| Runtime file | What it contains | Why it exists | What it is not |
|---|---|---|---|
| `raw_model_output.npy` | Full-resolution float32 prediction before height conversion | Audit the model output and prove normalization was not repeated | Directly displayable height or metres |
| `relative_surface.npy` | Lossless float32 2D array in the 0–1 relative range | Numeric source for analysis, later calibration, and reproducible tests | A DSM or height map in metres |
| `height_diagnostics.json` | Output convention, one-pass normalization record, geometry source, and plane-trend indicator | Diagnose reversal/tilt without deriving geometry from a preview | A claim that perspective bias was corrected |
| `relative_preview.png` | Colourized rendering of the relative array | Quick human quality check and presentation | Training ground truth or lossless science data |
| `texture.png` | Input converted into the model/viewer RGB convention | Texture for the 3D surface | A model prediction |
| `relative_height_16bit.png` | 16-bit display encoding of the relative surface | Renderer/export interoperability without reducing to 8 bits | Metric elevation |
| `relative_grid.json` | Downsampled surface values, maximum 192×192 | Keeps the browser mesh responsive | The full-resolution numeric result |
| `reconstructed_structures.json` | Convex raised-object candidates derived from local relative contrast | Optional Bhuvan-style upright visual layer | Semantic buildings, surveyed geometry, or a DSM edit |
| `relative_surface.glb` | GLB 2.0 triangle mesh with embedded vertex colours and relative Y | Portable 3D inspection in compatible tools | Metric or full-resolution elevation |
| `job.json` | Live persisted job state | Lets progress survive separate API requests | Final immutable evidence |
| `job_manifest.json` | Final input/model/warning/artifact record | Reproducibility and audit trail | A secret or credential file |
| `calibration_reference.tif` | Exact submitted aligned DSM evidence | Reproduce the gate decision and its source hash | Automatically trustworthy ground truth |
| `calibration_report.json` | Source/datum, fit, held-out metrics, thresholds, failures, and decision | Explain exactly why metres were unlocked or refused | A substitute for understanding reference quality |
| `metric_surface.npy` | Full-resolution float32 calibrated array in metres | Lossless numeric metric result after a pass | The relative viewer grid |
| `metric_analysis_grid.json` | Calibrated metre samples on the identical viewer-grid indices | Metric A/B elevation, height difference, and projected-metre slope inspection | A replacement for the full-resolution metric raster |
| `metric_surface.tif` | Calibrated float32 elevation with source CRS/transform/NoData and vertical tags | GIS-compatible passing-gate result | Available after a rejection |
| `calibration_error.tif` | Candidate metric surface minus aligned reference, in metres | Spatial residual diagnosis | Absolute truth about every object |

The web UI always offers preview, relative numeric surface, raw model output, height diagnostics, colour GLB, and manifest. Calibration/report/metric/residual files appear only when they actually exist.

## The model adapters

### Real adapter

`DepthAnythingV2Adapter` loads `depth-anything/Depth-Anything-V2-Small-hf`, records its exact revision, prefers CUDA, and falls back to CPU after a CUDA out-of-memory error. It preserves the raw output, declares it `inverse_depth_or_proximity`, and maps larger/closer values directly to higher relative surface for near-nadir scenes after one robust global normalization. It also warns that this is not metric and that global perspective tilt may remain.

When an image exceeds the configured trigger, the adapter predicts overlapping tiles. Because tile crops can have different arbitrary depth scale and offset, overlap values fit a positive affine alignment before feather blending. Only the complete blended raw surface is normalized. Tile count, size, overlap, and mode are written to the job configuration.

### Deterministic test adapter

Automated tests must be fast, repeatable, and offline. `DeterministicTestAdapter` produces a predictable surface from the input so tests can verify API and artifact behavior. It requires the explicit `allow_test_adapter` safety flag and marks every result `TEST-ONLY`; normal runs cannot silently use it.

## The SAC IR-colorization files

The related SAC repository is a different problem: TIR super-resolution and colorization. Its sample pairing is:

```text
tir_200m.npy       → tir_100m_512.npy       (super-resolution)
tir_100m_512.npy   → rgb_100m_512.npy       (colorization)
```

The matching PNGs are visual checks. The repository explicitly says training should use `.npy` so radiometric values are preserved.

These are **not TerraFly height labels**. The TIR arrays contain thermal imagery, and the RGB array is the colorization target. Uploading a TIR preview to TerraFly checks that the software can process a single-band image, but it does not validate the optical pretrained model scientifically. The API and UI now say this explicitly.

## What each technology contributes

| Technology | Role | Why this choice |
|---|---|---|
| FastAPI | Upload, validation, job status, artifact download | Typed Python API close to the ML stack |
| Pydantic | Validated job/manifest schema | Prevents undocumented response shapes |
| Pillow | Safe PNG/JPEG inspection and conversion | Mature image decoding with bomb warnings |
| Rasterio | GeoTIFF bands, CRS, transform, mask, bounds | Preserves geospatial facts rather than treating TIFF as a normal picture |
| NumPy | Float32 arrays and artifact encoding | Standard numeric representation with lossless `.npy` support |
| PyTorch + Transformers | Real pretrained inference | Auditable checkpoint and GPU/CPU execution |
| React + TypeScript | Stateful upload/result interface | Typed client contract and component testing |
| Three.js | Interactive textured height field | Orbit, pan, zoom, material, lighting, and mesh rendering in-browser |
| Vite + Vitest | Development/build/test tooling | Fast local workflow and deterministic frontend verification |

## Likely judge questions

### “Did AI build this?”

Yes, AI accelerated implementation. The team owns the decisions and can explain the request flow, scientific contract, model limitations, tests, and every output. The evidence is the exact model revision, input/artifact hashes, test suite, decision log, and refusal to claim metres without calibration.

### “Is this a digital elevation model?”

The first result is always a relative surface proxy. For a georeferenced input, TerraFly can produce a metric DSM-like GeoTIFF only after independent vertical evidence passes its documented gate. A synthetic pass proves the software path; a real scientific claim still depends on trustworthy surveyed evidence and domain evaluation.

### “Why Depth Anything if it was trained on normal images?”

It provides a practical pretrained relative-depth baseline for proving the product pipeline. It is not treated as a satellite-height oracle. Domain evaluation against aligned remote-sensing reference data is still required.

### “Why did the TIR image produce a surface?”

The software converts a single band to three identical RGB channels, so the model can execute. Execution is not validation. TIR is outside the intended optical domain, and the result is labelled as a demonstration.

### “Why `.npy` instead of only PNG?”

PNG previews are designed for viewing and may be colorized or quantized. `.npy` preserves the original float32 array shape and values needed for computation and calibration.

### “Why store SHA-256 hashes?”

They prove which exact input and artifacts belong to a run. If a file changes, its hash changes, so results can be audited and reproduced.

### “Why is the 3D surface vertically exaggerated?”

Relative differences can be visually small. The slider changes vertex display only; it never alters the saved numeric array. The UI labels this explicitly.

### “What does point A versus B measure?”

Before calibration it compares bilinearly sampled relative values. After a pass it samples the aligned metric grid and reports metre elevation and vertical difference. It reports horizontal distance/slope only when the source CRS uses projected metre units.

### “Why can GLB be available while metric GeoTIFF is locked?”

GLB is an inspection format and explicitly stores relative values. Metric GeoTIFF implies a vertical scale, offset, units, and datum, so it exists only after independent evidence passes. Portability and metric validity are different questions.

### “Why tile instead of shrinking every large image?”

Shrinking discards local detail. Tiles bound per-pass memory while retaining more spatial structure. TerraFly aligns crop scale/offset in overlaps and records the strategy, but still requires evaluation before claiming greater remote-sensing accuracy.

### “How do you prevent calibration from cheating?”

Reference-raster pixels are split spatially before fitting; GCP requests contain separate control and validation sets. Held-out observations never fit scale or offset. The gate also requires positive scale, sufficient relative span, at least 75% fit inliers, at least 40% coverage on both axes, RMSE below the declared limit, and R² of at least 0.50.

### “Why no automatic reprojection?”

Silent resampling can blur edges and hide misregistration. Day 3 fails closed unless CRS, dimensions, and affine transform match exactly. That narrow contract is easier to explain and verify; explicit reprojection can be a later tested feature.

### “Why does the 3D display geometry remain relative after a metric pass?”

The viewer is a responsive downsampled inspection surface, so its geometry stays normalized. Metric values are preserved at full resolution and on a separate matching analysis grid. Keeping those roles separate allows correct point labels without making a display mesh look like full-resolution survey geometry.

### “What is the Structures button?”

It renders optional convex extrusions from local raised-component candidates so structures have upright walls similar to object-based 3D map systems. It is off by default, may include trees or miss roofs, and never changes the DSM or calibration result.

## Team learning split

1. **Pipeline owner:** `main.py`, `pipeline.py`, adapters, scientific states.
2. **Data/geospatial owner:** `imaging.py`, `artifacts.py`, GeoTIFF tests, calibration limits.
3. **UI/UX owner:** `App.tsx`, `SurfaceViewer.tsx`, `styles.css`, `UX_RATIONALE.md`, Figma frames.
4. **Evidence/release owner:** tests, manifests, hashes, source/release archives, demo script.

Every member should still be able to give the 30-second explanation and distinguish relative depth, relative surface, and metric elevation.

## Five-minute self-test

Without looking at this file, explain:

1. Why a PNG cannot produce trustworthy metres.
2. Why a GeoTIFF can be georeferenced but still non-metric vertically.
3. What `relative_surface.npy` contains.
4. Why the deterministic adapter is not fake production inference.
5. Why the SAC thermal arrays do not train TerraFly height.
6. What the Three.js exaggeration slider changes—and what it does not.
7. How hashes and the manifest support reproducibility.
8. Why tile overlaps need scale/offset alignment before blending.
9. Why a GLB can be valid while still non-metric.
10. Why calibration controls and validation evidence must be separate.
11. Which six checks can keep metric export locked.
12. Why a synthetic calibration pass is not a real accuracy claim.

If an answer is unclear, open the named source file in `FILE_GUIDE.md` and trace the relevant function.

## Final operation every member must rehearse

1. Double-click `Start-TerraFly.cmd`; the final API and interface share `127.0.0.1:8000`.
2. Use Orbit for left-drag rotate, right-drag pan, wheel zoom, and A/B point comparison.
3. Use First-person for mouse-look, `W/A/S/D`, `Q/E`, Shift boost, and `Esc` release.
4. Run the bundled GeoTIFF/reference pair and say “synthetic software oracle” before showing the near-zero error.
5. Double-click `Check-TerraFly.cmd`, and know that `scripts\verify.ps1 -Full` adds the real model, 17 artifact hashes, metric analysis-grid verification, and metric GeoTIFF inspection.
6. If asked for the final release proof, open `handoff/FINAL_TEST_REPORT.md`; if asked how anything works, open `docs/cookbook/TERRAFLY_COOKBOOK.md`.
