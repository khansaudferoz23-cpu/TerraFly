# Learning notes

## Depth is not height

A monocular model learns visual clues about what appears nearer or farther. Its numbers can order the scene and reveal structure, but there are infinitely many physical scenes that could create one image. TerraFly therefore normalizes these numbers to 0–1 and calls them relative.

## What a GeoTIFF adds

A CRS says how map coordinates relate to Earth. An affine transform says where pixels land and their horizontal spacing. Neither fact says that a model value of `0.7` means 7 metres. That needs vertical evidence.

## Why two model adapters exist

The real adapter proves the application can use a pretrained model. The deterministic adapter makes tests fast, offline, and repeatable. It is fenced off so a fast fake can never silently replace a scientific run.

## Display exaggeration

The viewer may multiply vertex heights so small relative differences are visible. The stored float32 array never changes, and the UI labels the multiplier as display-only.

## Execution is not validation

A grayscale or thermal image can be repeated into three channels, so an RGB model can execute without a shape error. That does not mean the model understands thermal radiance or has been validated for TIR. TerraFly records a warning for single-band inputs and treats SAC TIR previews as software demonstrations only.

## Why `.npy` and PNG have different jobs

An `.npy` file preserves numeric array shape, dtype, and values. A PNG is convenient for human viewing but may be stretched, colorized, or quantized. Training, evaluation, and calibration should use the numeric array when it is the authoritative source; previews are for visual quality checks.

## Why large images need aligned overlapping tiles

Running a very large raster at once can exceed memory. Simple independent tiles are also unsafe because monocular depth may choose a different scale and offset for each crop. TerraFly uses shared overlap pixels to align each raw tile to the growing surface, blends the overlap gradually, and performs one final normalization. The manifest records whether the run was single-pass or tiled.

## What point comparison means

A surface click becomes an image x/y fraction, source pixel coordinate, and bilinearly sampled value. Before calibration, comparing A and B is relative only. After a passing gate, the same sampled grid location reads calibrated metres. A projected metre CRS also permits horizontal distance and slope; longitude/latitude degrees are never treated as metres.

## What the GLB contains

The GLB is a portable triangle mesh built from the responsive 192×192-or-smaller viewer grid. Its vertical coordinate is the same 0–1 relative value, and scene appearance is stored as vertex colour. The full-resolution `.npy` remains the numeric source of truth.

## DSM versus a Bhuvan-style building

A DSM is a 2.5D heightfield: each image x/y position stores one height. It cannot represent a perfectly vertical wall or two surfaces above the same pixel. Object-based 3D maps add separate building geometry. TerraFly’s optional Structures layer follows that separation by extruding conservative local raised candidates. It is for visual interpretation only and may include vegetation or miss roofs.

## What calibration actually fits

TerraFly fits `elevation_metres = scale × relative_value + offset`. Scale says how many metres correspond to one relative unit; offset anchors the zero point. A positive scale is required because the saved relative surface uses larger values for visually higher/nearer structure. This global relation is simple and auditable, but it cannot repair local shape errors.

## Why held-out validation matters

A model can look accurate on the same observations used to fit it. TerraFly therefore hides a spatial subset of an aligned reference DSM before fitting, or accepts separately surveyed GCP validation points. RMSE, MAE, bias, p95 absolute error, and R² are computed only on that independent subset. If any quality gate fails, the report is retained and metric output stays locked.

## Why exact alignment and NoData matter

Comparing different pixel grids can turn a location error into a fake height error. Day 3 accepts only an identical CRS, transform, width, and height. Source NoData pixels remain NoData in metric outputs; TerraFly never fills unknown source regions with invented calibrated elevation.

## Why the final app uses one server

Vite is excellent while editing the interface, but judges should not need two running services. Setup builds static HTML/CSS/JavaScript once; FastAPI then serves those files after its `/api` routes. The browser and API therefore use one local address, while the source still keeps frontend/backend responsibilities separate.

## What “portable Windows release” means here

The release ZIP includes the full tracked source and prebuilt interface, so it does not need Vite during normal use. It deliberately does not redistribute multi-gigabyte Python/npm environments or third-party model weights. A new machine performs one internet-connected setup, then can operate from its prepared local environment/cache.

## What the bundled calibration demo proves

The demo reference is calculated from the saved relative surface with `metric = 40 × relative + 100` and a few outliers placed only in fitting cells. Passing it proves exact-grid checks, robust fitting, independent held-out evaluation, state/artifact rules, hashes, and GeoTIFF metadata. Because the same output helped create the oracle, the error is not model accuracy.
