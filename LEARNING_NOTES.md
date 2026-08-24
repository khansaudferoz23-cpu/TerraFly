# Learning notes

## Depth is not height

A monocular model learns visual clues about what appears nearer or farther. Its numbers can order the scene and reveal structure, but there are infinitely many physical scenes that could create one image. TerraFly therefore normalizes these numbers to 0–1 and calls them relative.

## What a GeoTIFF adds

A CRS says how map coordinates relate to Earth. An affine transform says where pixels land and their horizontal spacing. Neither fact says that a model value of `0.7` means 7 metres. That needs vertical evidence.

## Why two model adapters exist

The real adapter proves the application can use a pretrained model. The deterministic adapter makes tests fast, offline, and repeatable. It is fenced off so a fast fake can never silently replace a scientific run.

## Display exaggeration

The viewer may multiply vertex heights so small relative differences are visible. The stored float32 array never changes, and the UI labels the multiplier as display-only.

\n