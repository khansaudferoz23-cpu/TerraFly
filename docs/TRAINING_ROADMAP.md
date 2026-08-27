# TerraFly building-height training roadmap

Training is a later, separately gated project. It improves photo-only urban building extraction and height estimation; it is not required for the new DEM Terrain mountain workflow.

## Decision gate before training

Do not start an overnight run until all five are true:

1. The DFC23 terms have been read and accepted and the required acknowledgement/citation text is recorded.
2. RGB, optional SAR, building annotations, and nDSM tiles are confirmed to be pixel-aligned pairs from the same scenes.
3. City identifiers are available so train/validation/test can be split geographically before tiles are generated.
4. A dataset audit reports shapes, CRS/transform where present, NoData, metre units, height distribution, missing pairs, and duplicate hashes.
5. A simple frozen-encoder baseline and its metrics/report format are fixed before tuning begins.

The official IEEE GRSS DFC23 page describes data from 17 cities, optical/SAR inputs, building annotations, and roughly 2 m nDSM reference data for Track 2: https://www.grss-ieee.org/community/technical-committees/2023-ieee-grss-data-fusion-contest/

## Recommended model

- Pretrained compact encoder; do not train Depth Anything from scratch.
- Shared overhead-image encoder.
- Building-footprint segmentation decoder.
- nDSM/height-above-ground regression decoder.
- Uncertainty decoder predicting a positive scale or log-variance.
- RGB baseline first; add SAR only after the RGB experiment is reproducible.

## Targets and losses

- Footprint target: Dice + binary cross-entropy.
- Building height: masked Huber or L1 in metres, with higher weight inside buildings.
- Boundary/shape preservation: gradient or Sobel loss on valid building edges.
- Uncertainty: heteroscedastic regression loss, followed by held-out calibration checking.
- Never train height loss on unknown/NoData pixels or on TerraFly's own predictions.

## Split and sampling rules

- Split by entire city/geographic region, never by random overlapping tiles.
- Create 384 or 512 pixel tiles only after the split.
- Keep empty/background tiles but cap their proportion so the model cannot win by predicting no buildings.
- Record every parent scene and tile window in a manifest to prevent leakage.
- Use 90° rotations and flips; use bounded radiometric/atmospheric changes. Do not apply geometry augmentations that break RGB/SAR/label alignment.

## RTX 5060 8 GB starting configuration

- 384 px tiles initially; increase to 512 only after memory profiling.
- Automatic mixed precision.
- Batch size 1–2 with gradient accumulation to an effective batch of 8–16.
- Freeze the encoder for the first stage, then unfreeze progressively with a smaller encoder learning rate.
- Save the best checkpoint by geographic validation score, not training loss.
- Use early stopping and a fixed random seed; record package, CUDA, checkpoint, and dataset hashes.

## Required evaluation

Report on cities never used for fitting:

- Building-mask IoU and F1.
- Height MAE, RMSE, bias, median absolute error, and P95 absolute error on valid building pixels.
- Per-building median/mean height error after instance matching.
- Boundary/edge score.
- Error by height range, roof type, city, sensor, and land-cover context.
- Uncertainty coverage/calibration: error versus predicted interval and empirical coverage at stated confidence levels.

## Milestones

1. **Data audit only:** no training; produce the licence record, pair manifest, city split, and histograms.
2. **RGB baseline:** footprint + height, frozen encoder, one reproducible configuration.
3. **Error analysis:** inspect worst cities/buildings and rule out misalignment or datum mistakes.
4. **Multi-task refinement:** boundary and uncertainty heads.
5. **Optional SAR ablation:** keep only if geographic held-out metrics improve consistently.
6. **TerraFly integration:** a separately versioned overhead checkpoint and model card; never silently replace the general Depth Anything adapter.

Your independent `RGB.byte.tif` and Mumbai SRTM files remain ingestion examples unless they cover the same exact scene and are intentionally paired. Unrelated RGB and DEM files must never be treated as a training sample.
