# Decisions

## D-001 — Greenfield, one repository

Evidence showed no user-owned TerraFly project. Create one `TerraFly` repository here, with backend and frontend as parts of the same application.

## D-002 — Python 3.12 project environment

The only system Python is 3.14.0, while the Codex runtime provides Python 3.12.13. Use a repository-local `.venv` created from 3.12 and do not modify the global Python installation.

## D-003 — Separate inference truth from test speed

Production defaults to Depth Anything V2 Small through Transformers. Fast tests use `DeterministicTestAdapter`, which requires an explicit test flag and writes a test-only warning into every result.

## D-004 — Relative height display convention

The pretrained model predicts relative depth. TerraFly robustly normalizes it and uses `1 - normalized_depth` as a visually intuitive relative surface. This does not create a physical height scale.

## D-005 — CUDA wheel

Use the official PyTorch 2.12.1 CUDA 13.0 wheel. PyTorch documents CUDA 13.0 as the default current wheel and suitable for Blackwell; the observed Windows driver 610.88 exceeds the documented minimum 580.88. CPU fallback remains mandatory.
