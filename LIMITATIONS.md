# Limitations

- Monocular output is a relative depth-derived surface, not surveyed elevation.
- GeoTIFF georeferencing alone does not supply vertical scale or a vertical datum.
- The inversion from relative depth to relative height is a display convention and can be wrong for scene geometry such as sloped terrain, façades, water, sky, haze, or unusual viewpoints.
- No calibration method is implemented yet; metric output is therefore refused.
- SRTM is not integrated and would be coarse terrain context, not reliable individual building/tree height.
- The real checkpoint is verified locally on CPU and CUDA, but its ignored cache is not included in the Day 1 source archive. An offline machine must prepare that cache before disconnecting.
- Day 1 viewer provides orbit, pan, zoom, reset, wireframe, texture, and display exaggeration; first-person navigation and measurement arrive after orientation tests.
- Numeric `.npy` is canonical for the current relative result; result GeoTIFF and GLB export are pending.
- There is no accuracy figure because no compatible ground truth was available.
\n