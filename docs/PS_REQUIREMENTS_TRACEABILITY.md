# Problem-statement traceability

This document maps the supplied elevation/DSM problem statement to implemented TerraFly behavior. It is the fastest honest answer when a judge asks whether a feature is real, partial, or future work.

| Problem-statement requirement | TerraFly implementation | Verification | Boundary to state aloud |
|---|---|---|---|
| PNG/JPG input | Safe RGB intake followed by real Depth Anything V2 Small inference and a normalized relative surface | API, adapter-contract, artifact, and real CUDA smoke tests | Output is an rDSM/relative surface proxy, never metres |
| Georeferenced GeoTIFF input | CRS, affine transform, bounds, pixel size, NoData, and horizontal units are preserved | GeoTIFF tests and real calibration smoke | Georeferencing gives horizontal facts; it does not create vertical scale |
| Pretrained monocular backbone | `depth-anything/Depth-Anything-V2-Small-hf`, with exact revision recorded, CUDA preference, and CPU fallback | Real CPU/CUDA checks and manifest provenance | It is a general relative-depth baseline, not a satellite-height oracle |
| Correct raised/near structure direction | Raw inverse-depth/proximity output maps directly to higher relative surface; no second inversion | Synthetic raised-building NumPy/GLB regressions and supplied-scene CUDA rerun | Strong scene-wide perspective tilt can remain |
| Absolute height calibration | Robust positive affine mapping from an aligned DSM or separate control/validation GCPs | Held-out pass/reject, outlier, coverage, NoData, and metadata tests | Only a passing gate creates metric files; the bundled reference is a software oracle |
| Standard geospatial DSM | Passing jobs export full-resolution float32 GeoTIFF and `.npy` in metres, retaining source grid and vertical metadata | Metric GeoTIFF contract and artifact-hash verification | Real accuracy is only as good as independent aligned reference evidence |
| Textured 3D terrain | Original optical texture is projected onto an orientation-tested Three.js heightfield; GLB export is also available | Geometry/UV tests, production build, and real scene run | The responsive display grid is downsampled and is not the full scientific raster |
| First-person navigation | Orbit plus pointer-lock free flight with W/A/S/D, Q/E, Shift boost, mouse-look, and Escape | Frontend contract and manual presentation checklist | Free flight has no collision physics |
| Height and slope analysis | A passing calibration emits `metric_analysis_grid.json`; A/B clicks show elevation and vertical difference in metres. Projected metre CRS inputs also show horizontal distance and slope | Metric-grid sampling and calibration tests | Relative jobs show relative differences only; geographic-degree CRS does not pretend to be metres |
| Bhuvan-style structures | Optional `reconstructed_structures.json` is rendered as separate clean extrusions with vertical walls | Synthetic raised-square candidate test and frontend build | It is a visual candidate layer, not semantic building truth; it can include trees or miss roofs and never changes the DSM |
| Accuracy metrics | Held-out RMSE, MAE, bias, median error, P95 error, R², inlier ratio, and spatial coverage | Calibration test suite | Synthetic near-zero RMSE proves plumbing, not real-world model accuracy |
| Unified local application | One Windows launcher serves the API and prebuilt interface on `127.0.0.1:8000` | Launcher, health, production-serving, and extracted-folder checks | First setup/model download needs internet unless already cached |
| Urban planning/disaster/reconnaissance utility | Exports DSM/GLB plus interactive height/slope inspection as an auditable base layer | End-to-end artifact and viewer verification | TerraFly does not yet predict floods, landslides, damage, or safe routes. Those modules require a validated metric DSM plus domain data |

## Why the Bhuvan screenshot looks different

The supplied Bhuvan 3D screenshot shows textured ground plus a separately authored or reconstructed building object. A DSM is a 2.5D heightfield: each image location has one height. It can raise a roof but cannot represent a roof overhang, two heights at one pixel, or a perfectly vertical façade by itself.

TerraFly therefore exposes two distinct layers:

1. **Scientific surface:** the actual model-derived relative surface, or calibrated metric DSM after evidence passes.
2. **Structures:** optional convex extrusions inferred from local relative-height components for Bhuvan-style visual interpretation.

Keeping those layers separate prevents a clean-looking building from being mistaken for measured geometry.

## Why TerraFly does not claim a newly trained “own model”

A credible satellite-height model needs licensed, co-registered RGB–DSM/nDSM pairs, masks, known units and datum, and geographically separated train/validation/test scenes. None was supplied. Training against RGB, TIR colorization arrays, or TerraFly’s own predictions would only teach the system to reproduce fabricated labels. The implemented contribution is therefore an auditable end-to-end pipeline around a real pretrained backbone, explicit direction repair, evidence-gated calibration, metric analysis, separated structure visualization, and reproducibility tests.

The next scientific milestone is data acquisition followed by domain evaluation and, only if the baseline warrants it, remote-sensing fine-tuning.
