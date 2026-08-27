# Third-party notices

TerraFly source is being assembled from original project code and the listed dependencies; third-party packages retain their own licenses.

- Depth Anything V2 Large Transformers checkpoint (`depth-anything/Depth-Anything-V2-Large-hf`): CC-BY-NC-4.0 according to its official Hugging Face model card. TerraFly selects it for non-commercial SIH evaluation; any commercial use requires a separate licensing review. The surrounding Depth Anything V2 code has its own upstream licence terms.
- PyTorch: BSD-style license; installed from the official PyTorch wheel index.
- Hugging Face Transformers: Apache License 2.0.
- FastAPI: MIT License.
- React: MIT License.
- Three.js: MIT License.
- Vite: MIT License.
- NumPy: BSD-3-Clause.
- Pillow: HPND License.
- Rasterio: BSD-3-Clause.

No model weights, Python environment, or `node_modules` tree are committed or redistributed. Package lockfiles and declared dependency pins are the install record; each installed distribution retains its own bundled license/metadata.

## Final verified environment

The final checks ran with Python 3.12.13 and these direct scientific/runtime packages: FastAPI 0.141.1, NumPy 2.5.2, Pillow 12.3.0, Rasterio 1.5.1, PyTorch 2.12.1+cu130, Torchvision 0.27.1+cu130, Transformers 5.15.1, and Uvicorn 0.52.4.

The final interface lockfile resolved React/React DOM 19.2.8, Three.js 0.185.1, Vite 8.2.2, TypeScript 7.0.2, and Vitest 4.1.11. `npm audit --omit=dev` and Python `pip check` are rerun as release gates; exact transitive versions remain in `frontend/package-lock.json` and the Python environment installer metadata.

The bundled `sample_data` fixtures are original generated work released under CC0 through `sample_data/LICENSE.txt`. The related SAC preview files are not redistributed because their inspected repository did not provide a project license.
