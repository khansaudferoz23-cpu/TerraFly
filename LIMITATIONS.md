# Limitations

- Monocular output is a relative depth-derived surface, not surveyed elevation.
- GeoTIFF georeferencing alone does not supply vertical scale or a vertical datum.
- The inversion from relative depth to relative height is a display convention and can be wrong for scene geometry such as sloped terrain, façades, water, sky, haze, or unusual viewpoints.
- Single-band imagery is repeated into RGB for compatibility. Thermal/TIR is outside the current pretrained model's validated optical domain and receives an explicit demonstration-only warning.
- Calibration is a single global affine scale and offset. It cannot correct spatially varying model distortion, local relief errors, temporal change, occlusion, or domain shift.
- The reference-DSM path requires the exact same CRS, dimensions, and affine pixel grid; Day 3 does not reproject or resample evidence.
- A pass is only as trustworthy as the reference source, vertical datum, declared RMSE threshold, spatial coverage, and independence of held-out data.
- The bundled calibration evidence is synthetic and proves software behavior, not real-world satellite/aerial height accuracy.
- SRTM is not integrated and would be coarse terrain context, not reliable individual building/tree height.
- The real checkpoint is verified locally on CPU and CUDA, but its ignored cache is not included in the Day 1 source archive. An offline machine must prepare that cache before disconnecting.
- First-person navigation is a free-flight inspection mode; it does not yet collide with or walk on the inferred surface.
- Point A/B values and their difference are relative samples, not physical distance, slope, or height change.
- Tiling reduces memory pressure and aligns overlap scale/offset, but no remote-sensing ground truth is available to quantify whether it improves scientific accuracy.
- Numeric `.npy` is canonical for the relative result. The GLB and viewer stay relative even after calibration; metric `.npy`/GeoTIFF are separate passing-gate artifacts.
- There is no real-world accuracy figure because no compatible independent surveyed ground truth was supplied.
- GCP calibration is available through the typed API; the minimal UI exposes the aligned-reference workflow rather than an error-prone free-form point editor.
- The private GitHub repository is a source milestone, not a dependency-bundled offline release; setup still downloads third-party packages and model weights.
