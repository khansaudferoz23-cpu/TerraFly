# TerraFly 1.0 final handoff

Date: 2026-08-27 IST
Repository: `khansaudferoz23-cpu/TerraFly` (private)  
Scientific promise: one optical image produces a traceable relative surface; metric exports exist only after documented vertical evidence passes held-out quality gates.

## What is complete

- Real Depth Anything V2 Large CUDA/CPU inference with exact revision recording and an explicit non-commercial checkpoint-licence boundary.
- Explicit inverse-depth/proximity direction, preserved raw prediction, single conversion, raised-roof GLB regression, and per-run tilt diagnostics.
- Safe PNG/JPEG/GeoTIFF intake, metadata/NoData preservation, tiling, hashes, and evidence artifacts.
- Professional responsive React/Three.js workbench with Orbit, drone-style First-person flight, relative/metric A/B inspection, Photo/Height colours, numeric legend, adjustable sun direction, wireframe, optional Bhuvan-style Structures, and display-only exaggeration.
- Portable GLB with the embedded source PNG, orientation-tested UVs, smooth unit normals, lit PBR materials, and neutral synthetic steep faces instead of baked vertex colour or stretched façade texture.
- Aligned-reference and API GCP calibration with separate fit/evaluation evidence, robust outlier handling, strict pass/reject gates, metric/error GeoTIFF artifacts, and a matching metric analysis grid for height/slope inspection.
- One-address final operation: the backend serves the prebuilt interface and API at `http://127.0.0.1:8000`.
- Beginner launcher/checker, full real-model checker, non-overwriting packager, final cookbook, operator guide, architecture diagrams, judge demo/Q&A, file ledger, test report, and manifest.

## Exact operation

1. On a new Windows machine, extract `TerraFly_FINAL_WINDOWS.zip`, connect to the internet, and run `scripts\setup.ps1` once.
2. Double-click `Start-TerraFly.cmd` and keep its window open.
3. Read `docs\OPERATOR_GUIDE.md` for every viewer control and the bundled calibration demonstration.
4. Double-click `Check-TerraFly.cmd` before presenting.
5. Run `powershell -ExecutionPolicy Bypass -File scripts\verify.ps1 -Full` for the real-model, 18-artifact, metric-GeoTIFF proof.

## Judge demonstration files

- Input: `sample_data\terrafly_calibration_demo_input.tif`
- Reference: `sample_data\terrafly_calibration_demo_reference.tif`
- Evidence source: `Bundled synthetic software oracle`
- Vertical datum: `Demo benchmark datum`
- Maximum held-out RMSE: `0.5`

Expected sequence: `Georeferenced Relative` before evidence, then `Metric Calibrated` after the gate. Scale is near 40, offset near 100, held-out error near zero, and the metric/error artifacts appear. State immediately that this is a software oracle, not a real height-accuracy score.

## Final deliverables

The repository source is current. The previously generated ZIP/checksum files predate the final metric/Structures patch and must be regenerated with `scripts\package_release.ps1` before external delivery.

- `TerraFly_FINAL_WINDOWS\`: inspectable Windows source plus prebuilt interface.
- `TerraFly_FINAL_WINDOWS.zip`: shareable Windows release.
- `TerraFly_FINAL_SOURCE.zip`: exact committed source archive.
- `TerraFly_FINAL_SHA256.txt`: authoritative byte lengths and SHA-256 values for both ZIPs.
- `handoff\FINAL_MANIFEST.json`: committed-file hashes and verified environment/test boundary.

## Remaining boundary

The four-day software objective, critical visual/GLB repair, model-capacity upgrade, roof-inversion repair, metric analysis grid, and separated structure visualization are complete. Real-world remote-sensing height accuracy is not established: the evaluator is ready, while its model metric card remains blocked until real evidence exists. Strong global perspective tilt is measured but not automatically removed. Structures are visual candidates, not verified buildings. TerraFly supplies a DSM foundation rather than a hazard predictor. The next scientific milestone is a licensed, compatible, independently surveyed optical/DSM or nDSM dataset with geographic train/validation/test separation, masks, units, alignment, resolution, datum, and provenance.
