# TerraFly model upgrade evaluation

Status date: 2026-08-27 IST

## Decision

TerraFly now selects `depth-anything/Depth-Anything-V2-Large-hf` by default. The checkpoint remains a general-purpose relative monocular-depth model: switching from Small to Large does not make its output an overhead DSM or metres. `TERRAFLY_MODEL_ID` can still select Small for a controlled comparison or low-resource fallback, but every manifest must record the checkpoint actually used.

The official Large Transformers model card reports approximately 0.3 billion parameters, float32 weights, Transformers compatibility, and a CC-BY-NC-4.0 checkpoint licence. TerraFly uses CUDA autocast for inference and retains its existing CPU retry after CUDA out-of-memory. Commercial use requires a separate licence review.

`scripts/compare_model_variants.py` runs Small and Large on an identical input and records revision, runtime, peak VRAM, relative-surface spread/local gradients, cross-model correlation, and side-by-side height previews. Those diagnostics support visual/resource review but cannot declare an accuracy winner without height truth.

Primary source inspected: <https://huggingface.co/depth-anything/Depth-Anything-V2-Large-hf>

## Remote-sensing domain-adaptation audit

### RDAH-Net

An author-labelled public implementation exists at <https://github.com/Elenairene/RDAH-Net>. The repository is MIT-licensed and links to Figshare-hosted checkpoints and paper datasets. Its current source includes training/testing entry points and predefined geographic split lists. This is a viable research adapter candidate, not a drop-in replacement: its input normalization, checkpoint provenance, dataset licences, expected nDSM units, and reported splits must be independently audited before TerraFly can load its results.

Paper: <https://doi.org/10.3390/rs18071024>

### Depth2Elevation

The peer-reviewed/accepted paper exists with DOI `10.1109/TGRS.2025.3564820` and describes a scale modulator plus resolution-agnostic decoder built around Depth Anything. As of the status date, the author repository, official pretrained weights, and an implementation licence were not identified in searches of the paper repository and public GitHub results. TerraFly will not reimplement it from the paper under the current deadline.

Paper repository: <https://openrepository.aut.ac.nz/items/4d5713c5-f7ea-4a08-9a73-4c2555e29743>

## Candidate real evidence

The official ISPRS Potsdam and Vaihingen semantic-labelling benchmark pages provide aligned true orthophotos and float32 DSMs. Potsdam uses 5 cm grids; Vaihingen uses 9 cm grids. These are research datasets with source-specific conditions and acknowledgements. The supplied normalized DSMs are automatically derived and are explicitly not guaranteed error-free.

- Potsdam: <https://isprs.org/resources/datasets/benchmarks/UrbanSemLab/2d-sem-label-potsdam.aspx>
- Vaihingen: <https://www.isprs.org/resources/datasets/benchmarks/UrbanSemLab/2d-sem-label-vaihingen.aspx>

Before training or benchmarking, the team must retain the downloaded terms, verify RGB versus IRRG band order, define DSM versus nDSM target semantics, split geographically by whole tiles, and keep the held-out tiles out of fitting and calibration.

## Evidence gate for any model change

Run `scripts/benchmark_height_model.py` only on aligned held-out prediction/reference pairs. Its metric card records dataset, licence, split, checkpoint revision, grid metadata, RMSE, MAE, bias, Pearson correlation, runtime, and memory. Synthetic oracle cards are labelled software-only and must never be presented as model accuracy.

No real benchmark number belongs in TerraFly documentation until the corresponding real metric-card JSON exists and its reference licence and held-out split are reviewable.

## Verified local comparison

The Large revision `7581137eff8d4e94f6e796d3baea0e9fa79b22d2` passed both CUDA and CPU smoke inference. CUDA peak allocation was 1,618.2 MB on the tiny smoke and 1,699.6 MB on the 642×661 stadium comparison. On the identical stadium scene, steady-state inference was 0.029 s for Small and 0.072 s for Large; their normalized surfaces correlated at 0.9446 with mean absolute relative difference 0.0839. Visual inspection found that Large delineated the stadium ring and surrounding structures more crisply, while both retained a scene-wide monocular trend. This is a qualitative/resource comparison only, not a height-accuracy result.
