# Final cookbook source index

This index shows which final evidence grounds each cookbook section.

| Cookbook section | Final source | Evidence status |
|---|---|---|
| Problem and scientific states | `README.md`, `LIMITATIONS.md`, schemas/tests | verified |
| Ingredients/environment | `BUILD_LOG.md`, final manifest | verified versions/environment |
| Preparation/upload | `imaging.py`, API/geospatial tests | verified pass/refusal paths |
| Inference/tiling | real/test adapters, tiling tests, CUDA smokes | verified |
| Calibration | `calibration.py`, calibration tests, real final smoke | verified synthetic oracle + refusal paths |
| 3D plating | viewer/geometry tests and browser QA | verified desktop/mobile/WebGL |
| Evaluation | calibration report, `RESULTS.md`, final test report | verified software metrics; no real accuracy claim |
| Packaging/serving | setup/start/verify/package scripts, extracted release | verified |
| Troubleshooting | `BUILD_LOG.md`, launcher/parser/browser repairs | verified observed failures/repairs |
| Judge explanation | decisions, file guide, team guide, Q&A | traceable |
