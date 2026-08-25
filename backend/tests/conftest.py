from __future__ import annotations

import io

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from terrafly.config import Settings
from terrafly.main import create_app


@pytest.fixture()
def settings(tmp_path):
    return Settings(
        jobs_root=tmp_path / "jobs",
        frontend_dist=tmp_path / "frontend-dist",
        model_adapter="deterministic",
        model_id="terrafly/deterministic-test-adapter",
        device="cpu",
        max_upload_bytes=1024 * 1024,
        max_pixels=200_000,
        allow_test_adapter=True,
    )


@pytest.fixture()
def client(settings):
    with TestClient(create_app(settings)) as test_client:
        yield test_client


def encoded_image(mode: str = "RGB", size: tuple[int, int] = (37, 23), fmt: str = "PNG") -> bytes:
    height, width = size[1], size[0]
    if mode == "L":
        array = np.arange(height * width, dtype=np.uint8).reshape(height, width)
    else:
        channels = 4 if mode == "RGBA" else 3
        array = np.zeros((height, width, channels), dtype=np.uint8)
        array[..., 0] = np.arange(width, dtype=np.uint8)[None, :]
        array[..., 1] = np.arange(height, dtype=np.uint8)[:, None]
        array[..., 2] = 173
        if channels == 4:
            array[..., 3] = 200
    buffer = io.BytesIO()
    Image.fromarray(array, mode=mode).save(buffer, format=fmt)
    return buffer.getvalue()
