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

A surface click becomes an image x/y fraction, source pixel coordinate, and bilinearly sampled relative value. Comparing A and B is useful for inspecting ordering and contrast. It is not a claim about metres or geographic distance.

## What the GLB contains

The GLB is a portable triangle mesh built from the responsive 192×192-or-smaller viewer grid. Its vertical coordinate is the same 0–1 relative value, and scene appearance is stored as vertex colour. The full-resolution `.npy` remains the numeric source of truth.
