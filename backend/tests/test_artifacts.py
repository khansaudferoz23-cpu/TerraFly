from __future__ import annotations

import json
import struct

import numpy as np
from PIL import Image

from terrafly.artifacts import write_surface_artifacts


def _read_glb(path):
    content = path.read_bytes()
    magic, version, total_length = struct.unpack_from("<4sII", content, 0)
    assert magic == b"glTF"
    assert version == 2
    assert total_length == len(content)
    json_length, json_type = struct.unpack_from("<I4s", content, 12)
    assert json_type == b"JSON"
    document = json.loads(content[20 : 20 + json_length].decode("utf-8"))
    binary_header = 20 + json_length
    binary_length, binary_type = struct.unpack_from("<I4s", content, binary_header)
    assert binary_type == b"BIN\x00"
    binary = content[binary_header + 8 : binary_header + 8 + binary_length]
    return document, binary


def test_artifact_orientation_and_glb_contract(tmp_path):
    relative = (np.arange(12, dtype=np.float32).reshape(3, 4) / 11).astype(np.float32)
    rgb = np.zeros((3, 4, 3), dtype=np.uint8)
    rgb[0, 0] = [255, 0, 0]
    rgb[0, -1] = [0, 255, 0]
    rgb[-1, 0] = [0, 0, 255]
    rgb[-1, -1] = [255, 255, 0]

    artifacts = write_surface_artifacts(tmp_path, relative, rgb)
    assert {artifact.name for artifact in artifacts} == {
        "numeric_surface",
        "preview",
        "texture",
        "height_texture",
        "surface_grid",
        "glb_mesh",
    }
    texture = np.asarray(Image.open(tmp_path / "texture.png"))
    np.testing.assert_array_equal(texture, rgb)
    grid = json.loads((tmp_path / "relative_grid.json").read_text(encoding="utf-8"))
    assert grid["source_shape"] == [3, 4]
    assert grid["orientation"] == {"row_zero": "image_top", "column_zero": "image_left"}
    assert grid["values"][0] == 0.0
    assert grid["values"][-1] == 1.0

    document, binary = _read_glb(tmp_path / "relative_surface.glb")
    assert document["meshes"][0]["extras"]["units"] == "relative_0_1"
    assert document["meshes"][0]["extras"]["vertical_scale_metric"] is False
    colour_view = document["bufferViews"][1]
    colour_bytes = binary[
        colour_view["byteOffset"] : colour_view["byteOffset"] + colour_view["byteLength"]
    ]
    colours = np.frombuffer(colour_bytes, dtype=np.uint8).reshape(-1, 3)
    np.testing.assert_array_equal(colours[0], rgb[0, 0])
    np.testing.assert_array_equal(colours[-1], rgb[-1, -1])
