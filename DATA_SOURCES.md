# Data sources

## Current inputs

No private dataset, competition dataset, paired RGB/height ground truth, GCP set, reference DSM/DTM, or SRTM tile has been downloaded or committed.

The repository includes one original, CC0 synthetic asymmetric image at `sample_data/terrafly_synthetic_aerial.png`. It exists only for offline workflow/orientation demonstrations and is not real remote-sensing data or height ground truth.

## Official SAC reference

- Repository: `IMG-PROCESS-SAC/SIH-DepthWizard-2026`
- Inspected: 2026-08-25
- Commit: `feb4dc63596fdf8c801d1a4f07ef8f2ff4e107be`
- Observed contents: one README saying the repository contains the DepthWizard dataset; GitHub reported repository size 0. No dataset/code was available to inspect.

## Model

- Checkpoint identifier: `depth-anything/Depth-Anything-V2-Small-hf`
- Intended role: relative monocular depth only.
- Weight files are downloaded to local caches and ignored by Git.

## Future training gate

Fine-tuning requires aligned RGB, target DSM/DTM/nDSM, valid mask, source-scene identity, units, alignment/resolution metadata, and hashes. Split by geographic scene before cropping. RGB-only inputs do not pass this gate.
\n