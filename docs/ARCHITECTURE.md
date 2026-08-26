# TerraFly architecture and evidence map

## Runtime system

```mermaid
flowchart TB
    UI[React workbench + Three.js viewer]
    API[FastAPI local service]
    SAFE[Image/GeoTIFF validation]
    MODEL[Depth Anything V2 adapter]
    TILE[Bounded overlap tiling]
    JOB[Per-job state + SHA-256 manifest]
    ART[Relative NPY / preview / texture / grid / structures / GLB]
    CAL[Calibration and held-out evaluation]
    METRIC[Metric NPY / analysis grid / GeoTIFF / residual / report]

    UI -->|POST image; poll job| API
    API --> SAFE --> MODEL
    MODEL -->|large image| TILE
    MODEL --> JOB
    TILE --> JOB
    JOB --> ART --> UI
    UI -->|aligned DSM or API GCPs| CAL
    JOB --> CAL
    CAL -->|reject| JOB
    CAL -->|pass| METRIC --> UI
```

## Scientific state machine

```mermaid
stateDiagram-v2
    [*] --> Relative: PNG/JPEG or TIFF without CRS
    [*] --> GeoreferencedRelative: GeoTIFF with CRS/transform
    GeoreferencedRelative --> GeoreferencedRelative: missing/misaligned/failed evidence
    GeoreferencedRelative --> MetricCalibrated: independent gate passes
    MetricCalibrated --> GeoreferencedRelative: later recalibration is rejected
```

Metric artifacts are a consequence of the state, not a UI toggle. The viewer/GLB display geometry remains normalized in every state; after a pass, point inspection samples the separate metric analysis grid. The optional Structures layer is visual only and never changes scientific state or DSM values.

## Calibration decision

```mermaid
flowchart TD
    E[Vertical evidence] --> A{Input georeferenced?}
    A -- No --> R0[HTTP 409; metric impossible]
    A -- Yes --> B{Aligned DSM or GCP request?}
    B -- DSM --> C[Exact CRS + shape + affine + mask]
    B -- GCP --> D[6+ controls + 3+ independent checks]
    C --> F[Robust affine fit]
    D --> F
    F --> G[Held-out RMSE / MAE / bias / p95 / R²]
    G --> H{Positive scale, span, inliers, coverage, count, RMSE, R²?}
    H -- No --> R[Rejected report; no metric artifact]
    H -- Yes --> P[Metric Calibrated + metre files + datum + residuals]
```

## Ownership map

| Concern | Primary files | What the owner must explain |
|---|---|---|
| API and state | `main.py`, `schemas.py`, `jobs.py` | routes, typed states, persistence, safe artifact lookup |
| Image/geospatial | `imaging.py`, `calibration.py` | CRS versus vertical datum, masks, exact alignment, gates |
| Inference | `depth_anything_v2.py`, `tiling.py`, `factory.py` | relative model, real/test split, CUDA fallback, overlap alignment |
| Artifacts | `artifacts.py`, `pipeline.py` | why each file exists, GLB limits, hashes, orientation |
| 3D/UI | `App.tsx`, `SurfaceViewer.tsx`, `surfaceGeometry.ts` | progress, scientific labels, navigation, relative/metric A/B samples, optional structures, responsive design |
| Release/evidence | `verify.ps1`, `package_release.ps1`, `handoff/` | tests, clean extraction, checksums, limitations, reproducibility |

The complete tracked-file explanation is in `FILE_GUIDE.md`.
