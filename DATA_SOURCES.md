# Data sources

## Current inputs

No private dataset, paired RGB/height ground truth, GCP set, reference DSM/DTM, or SRTM tile has been committed. Three preview PNGs from the related SAC IR-colorization repository were downloaded by the team and inspected outside this repository; they are documented below and are not height ground truth.

The repository includes one original, CC0 synthetic asymmetric image at `sample_data/terrafly_synthetic_aerial.png`. It exists only for offline workflow/orientation demonstrations and is not real remote-sensing data or height ground truth.

The final release also includes a reproducible synthetic calibration pair:

| File | SHA-256 | Role |
|---|---|---|
| `terrafly_calibration_demo_input.tif` | `f3d2a85c934434ba3f19196a6d3357eee2b6be4d7cc412631edea0ac11e62091` | 480×320 RGB GeoTIFF input with EPSG:32643 and a fixed affine grid |
| `terrafly_calibration_demo_reference.tif` | `64b22294ad5200a3659f7ee96e6b9b4924e3609791e7f545c3b3f0c00dd41e0b` | Large-model-aligned synthetic software oracle defined as `40 × relative + 100`, with 12 training-only outliers |
| `terrafly_calibration_demo_metadata.json` | Reproducibility record | Generator inputs, model revision/device, hashes, affine relation, and exact disclaimer |

This pair is allowed only for software demonstration: it proves grid validation, robust fitting, held-out evaluation, state transitions, artifact integrity, and GeoTIFF metadata. It is not independently surveyed evidence and cannot establish real-world height accuracy.

## Official SAC reference

- Repository: `IMG-PROCESS-SAC/SIH-DepthWizard-2026`
- Inspected: 2026-08-25
- Commit: `feb4dc63596fdf8c801d1a4f07ef8f2ff4e107be`
- Observed contents: one README saying the repository contains the DepthWizard dataset; GitHub reported repository size 0. No dataset/code was available to inspect.

## Related SAC IR-colorization reference

- Repository: [`IMG-PROCESS-SAC/IR-colorization-BAH2026`](https://github.com/IMG-PROCESS-SAC/IR-colorization-BAH2026)
- Inspected: 2026-08-25
- Commit: [`c6735fbffd0d7b08383572357e95d55f91c719e1`](https://github.com/IMG-PROCESS-SAC/IR-colorization-BAH2026/commit/c6735fbffd0d7b08383572357e95d55f91c719e1)
- Problem: Thermal Infrared super-resolution and colorization, not the DepthWizard/TerraFly height problem.
- The [official README](https://github.com/IMG-PROCESS-SAC/IR-colorization-BAH2026/blob/c6735fbffd0d7b08383572357e95d55f91c719e1/README.md) says `.npy` files are for training because they preserve radiometric resolution; PNGs are visualization only.
- The [patch-generation script](https://github.com/IMG-PROCESS-SAC/IR-colorization-BAH2026/blob/c6735fbffd0d7b08383572357e95d55f91c719e1/scripts/create_patches.py) saves these co-registered arrays:

| File | Shape/role from the baseline | Correct interpretation |
|---|---|---|
| `tir_200m.npy` | 256×256 low-resolution TIR input | Super-resolution input |
| `tir_100m_512.npy` | 512×512 higher-resolution TIR target | Super-resolution target and later colorization input |
| `rgb_100m_512.npy` | 512×512 RGB target | Colorization target |

None is a DSM, DTM, nDSM, depth map, or elevation label. The repository belongs to a different problem statement and cannot supply TerraFly metric-height supervision.

### Team-downloaded preview audit

These files remain in the user's Downloads folder and are deliberately not copied into TerraFly because the source repository does not provide a project license.

| Preview | Mode and dimensions | SHA-256 | Use in TerraFly |
|---|---|---|---|
| `tir_200m.png` | single-band `L`, 256×256 | `65b0d79d1ef8462e731738308cfd7ebe68440dbdbaa963d8cd74ee5ca15dce9c` | Software/domain-warning demonstration only |
| `tir_100m_512.png` | single-band `L`, 512×512 | `93df051dc486187474efb0faaa6cde3ed78d215141f6d6840276333cbd9e6adf` | Software/domain-warning demonstration only |
| `rgb_100m_512.png` | `RGB`, 512×512 | `49fffd0f4117b042c4318d7256b5f9aaf5369f822632bfec717082e229e0467b` | Optical pipeline demonstration only; still not height truth |

Depth Anything V2 was not validated here for TIR. TerraFly repeats readable single-band inputs into RGB so the pipeline can execute, but the API and UI warn that execution is not scientific validation.

## Model

- Default checkpoint identifier: `depth-anything/Depth-Anything-V2-Large-hf`
- Intended role: relative monocular depth only.
- Weight files are downloaded to local caches and ignored by Git.
- Verified checkpoint revision: `7581137eff8d4e94f6e796d3baea0e9fa79b22d2`.
- Verified `model.safetensors`: 1,341,322,868 bytes; SHA-256 `4e01e34ed5549b529b70b92d53226bc370f03041977b390d3dde45d47f516cf9`.
- Checkpoint licence: CC-BY-NC-4.0 according to the official model card; current use is non-commercial evaluation only.

## Future training gate

Fine-tuning requires aligned RGB, target DSM/DTM/nDSM, valid mask, source-scene identity, units, alignment/resolution metadata, and hashes. Split by geographic scene before cropping. RGB-only inputs do not pass this gate.

## Measured terrain demonstration

The repository includes a generated software-demonstration pair:

| File | Role |
|---|---|
| `terrafly_terrain_demo_imagery.tif` | 640×480 georeferenced synthetic optical texture on a 10 m grid |
| `terrafly_terrain_demo_dem.tif` | 320×240 georeferenced synthetic elevation surface on a 20 m grid |
| `terrafly_terrain_demo_metadata.json` | generator settings, hashes, grids, source label, datum label, and disclaimer |

This pair intentionally exercises cross-resolution alignment. It is not a satellite scene, surveyed elevation source, or accuracy result.

For a real mountain demonstration, use licensed optical imagery and a DEM that overlaps the same area and whose CRS, grid, vertical datum, resolution, date, and accuracy are documented. Recommended starting points are [Copernicus Sentinel-2 Level-2A](https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/Data/S2L2A.html) for optical imagery and [NASA LP DAAC elevation data](https://www.earthdata.nasa.gov/centers/lp-daac) for SRTM access. Google Earth screenshots are not training or reconstruction inputs; Google’s [Geo usage guidelines](https://about.google/brand-resource-center/products-and-services/geo-guidelines/) apply.

For the later overhead building model, the official [IEEE GRSS Data Fusion Contest 2023](https://www.grss-ieee.org/community/technical-committees/2023-ieee-grss-data-fusion-contest/) is the most relevant starting point. Dataset terms must be reviewed and accepted before download or training.
