# TerraFly team technical guide

Read this before presenting the project. The goal is not to memorize code; it is to understand the chain of evidence well enough to explain every decision honestly.

## The 30-second explanation

TerraFly accepts one PNG, JPEG, or GeoTIFF. It validates the file, converts readable image bands into RGB, and runs the pretrained Depth Anything V2 Small model. That model estimates **relative monocular depth**, not physical elevation. TerraFly robustly normalizes and inverts that result into a 0–1 display surface, writes reproducible artifacts, and renders the input texture on an interactive Three.js mesh. Metre-scale outputs remain locked until external vertical calibration succeeds.

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
  ▼
Relative surface ── normalize depth, invert for display, preserve 0–1 values
  ▼
Artifact writer ── .npy + preview + texture + viewer grid + manifest
  ▼
React polls progress ── Three.js renders the textured surface
```

## Why the result is relative

A single image is a 2D projection. Many physically different 3D scenes can produce similar pixels, so one uncalibrated image cannot establish an absolute vertical scale or offset. Depth Anything V2 estimates ordering and structure from learned visual cues. TerraFly therefore stores values between 0 and 1 and refuses to label them metres.

A GeoTIFF can add a coordinate reference system, pixel size, map position, and bounds. Those are horizontal facts. They still do not prove vertical scale, vertical datum, or elevation.

## Why each runtime output exists

| Runtime file | What it contains | Why it exists | What it is not |
|---|---|---|---|
| `relative_surface.npy` | Lossless float32 2D array in the 0–1 relative range | Numeric source for analysis, later calibration, and reproducible tests | A DSM or height map in metres |
| `relative_preview.png` | Colourized rendering of the relative array | Quick human quality check and presentation | Training ground truth or lossless science data |
| `texture.png` | Input converted into the model/viewer RGB convention | Texture for the 3D surface | A model prediction |
| `relative_height_16bit.png` | 16-bit display encoding of the relative surface | Renderer/export interoperability without reducing to 8 bits | Metric elevation |
| `relative_grid.json` | Downsampled surface values, maximum 192×192 | Keeps the browser mesh responsive | The full-resolution numeric result |
| `job.json` | Live persisted job state | Lets progress survive separate API requests | Final immutable evidence |
| `job_manifest.json` | Final input/model/warning/artifact record | Reproducibility and audit trail | A secret or credential file |

The web UI offers only the three outputs useful to a normal user: preview, numeric surface, and final manifest. Viewer-only support files remain internal.

## The model adapters

### Real adapter

`DepthAnythingV2Adapter` loads `depth-anything/Depth-Anything-V2-Small-hf`, records its exact revision, prefers CUDA, and falls back to CPU after a CUDA out-of-memory error. It returns a float32 relative surface and an explicit warning against metric interpretation.

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

Not yet. The Day 1 result is a relative surface proxy. Calling it a metric DSM would be scientifically false. Day 3 introduces a strict calibration/evaluation path using compatible reference elevation or ground control evidence.

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

### “Why not export GeoTIFF or GLB now?”

Day 1 prioritizes a tested relative pipeline. A metric GeoTIFF must wait for vertical calibration; GLB belongs to the robust viewer/export milestone. The UI does not pretend these unfinished features are available.

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

If an answer is unclear, open the named source file in `FILE_GUIDE.md` and trace the relevant function.
