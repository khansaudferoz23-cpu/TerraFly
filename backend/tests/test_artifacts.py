from __future__ import annotations

import json
import struct

import numpy as np
import pytest
from PIL import Image

from terrafly.artifacts import build_display_grid, write_surface_artifacts
from terrafly.inference.conventions import OutputConvention, to_relative_height


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

    conversion = {
        "output_convention": "relative_height",
        "normalization": {"applied_count": 1},
    }
    artifacts = write_surface_artifacts(
        tmp_path,
        relative,
        rgb,
        raw_model_output=relative.copy(),
        conversion_diagnostics=conversion,
    )
    assert {artifact.name for artifact in artifacts} == {
        "raw_model_output",
        "numeric_surface",
        "preview",
        "texture",
        "height_texture",
        "surface_grid",
        "display_grid",
        "structure_layer",
        "glb_mesh",
        "height_diagnostics",
    }
    np.testing.assert_array_equal(np.load(tmp_path / "raw_model_output.npy"), relative)
    np.testing.assert_array_equal(np.load(tmp_path / "relative_surface.npy"), relative)
    texture = np.asarray(Image.open(tmp_path / "texture.png"))
    np.testing.assert_array_equal(texture, rgb)
    grid = json.loads((tmp_path / "relative_grid.json").read_text(encoding="utf-8"))
    assert grid["source_shape"] == [3, 4]
    assert grid["orientation"] == {"row_zero": "image_top", "column_zero": "image_left"}
    assert grid["values"][0] == 0.0
    assert grid["values"][-1] == 1.0
    display_grid = json.loads((tmp_path / "display_grid.json").read_text(encoding="utf-8"))
    assert display_grid["scientific_role"] == "display geometry only"
    assert display_grid["numeric_source"] == "relative_surface.npy"
    assert display_grid["analysis_grid"] == "relative_grid.json"

    document, binary = _read_glb(tmp_path / "relative_surface.glb")
    assert document["meshes"][0]["extras"]["units"] == "relative_0_1"
    assert document["meshes"][0]["extras"]["vertical_scale_metric"] is False
    assert document["meshes"][0]["extras"]["geometry_source"] == "display_grid.json"
    assert document["meshes"][0]["extras"]["numeric_source"] == "relative_surface.npy"
    assert {material["name"] for material in document["materials"]} == {
        "Embedded scene colours",
        "Synthetic neutral steep faces",
    }
    assert all(view["byteLength"] > 0 for view in document["bufferViews"])
    assert sum(
        document["accessors"][primitive["indices"]]["count"]
        for primitive in document["meshes"][0]["primitives"]
    ) == (relative.shape[0] - 1) * (relative.shape[1] - 1) * 6
    colour_view = document["bufferViews"][1]
    colour_bytes = binary[
        colour_view["byteOffset"] : colour_view["byteOffset"] + colour_view["byteLength"]
    ]
    colours = np.frombuffer(colour_bytes, dtype=np.uint8).reshape(-1, 3)
    np.testing.assert_array_equal(colours[0], rgb[0, 0])
    np.testing.assert_array_equal(colours[-1], rgb[-1, -1])
    diagnostics = json.loads((tmp_path / "height_diagnostics.json").read_text(encoding="utf-8"))
    assert diagnostics["geometry"]["source"] == "display_grid.json"
    assert diagnostics["geometry"]["canonical_numeric_source"] == "relative_surface.npy"
    assert diagnostics["geometry"]["canonical_analysis_grid"] == "relative_grid.json"
    assert diagnostics["geometry"]["display_processing_changes_measurements"] is False
    assert diagnostics["geometry"]["processing"]["numeric_surface_unchanged"] is True
    assert diagnostics["geometry"]["colour_preview_is_geometry_source"] is False
    assert diagnostics["global_tilt_indicator"]["correction_applied"] is False
    structures = json.loads((tmp_path / "reconstructed_structures.json").read_text(encoding="utf-8"))
    assert structures["affects_numeric_dsm"] is False
    assert "not a calibrated probability" in structures["score_role"]


def test_glb_exports_a_synthetic_building_above_flat_ground(tmp_path):
    raw_output = np.full((16, 16), 0.1, dtype=np.float32)
    raw_output[4:12, 4:12] = 0.9
    relative, conversion = to_relative_height(raw_output, OutputConvention.INVERSE_DEPTH)
    rgb = np.full((16, 16, 3), 128, dtype=np.uint8)
    write_surface_artifacts(
        tmp_path,
        relative,
        rgb,
        raw_model_output=raw_output,
        conversion_diagnostics=conversion,
    )

    document, binary = _read_glb(tmp_path / "relative_surface.glb")
    position_view = document["bufferViews"][0]
    position_bytes = binary[
        position_view["byteOffset"] : position_view["byteOffset"] + position_view["byteLength"]
    ]
    positions = np.frombuffer(position_bytes, dtype="<f4").reshape(16, 16, 3)
    roof_height = float(positions[4:12, 4:12, 1].mean())
    ground_height = float(positions[:4, :, 1].mean())
    assert roof_height > ground_height
    assert roof_height > 0.6
    assert ground_height == pytest.approx(0.0)
    assert any(
        primitive["material"] == 1
        and "COLOR_0" not in primitive["attributes"]
        for primitive in document["meshes"][0]["primitives"]
    )
    structures = json.loads((tmp_path / "reconstructed_structures.json").read_text(encoding="utf-8"))
    assert structures["structures"]
    assert all(
        structure["roof_relative"] > structure["base_relative"]
        for structure in structures["structures"]
    )
    assert all(0 <= structure["visual_score"] <= 0.95 for structure in structures["structures"])


def test_display_cleanup_removes_spikes_flattens_roofs_and_preserves_input():
    relative = np.full((32, 32), 0.2, dtype=np.float32)
    rng = np.random.default_rng(7)
    relative[8:24, 8:24] = 0.78 + rng.normal(0, 0.025, (16, 16))
    relative[2, 2] = 1.0
    original = relative.copy()
    rgb = np.full((32, 32, 3), 55, dtype=np.uint8)
    rgb[8:24, 8:24] = [190, 190, 185]

    display, diagnostics = build_display_grid(relative, rgb)

    np.testing.assert_array_equal(relative, original)
    assert display[2, 2] < 0.35
    assert float(display[10:22, 10:22].std()) < float(relative[10:22, 10:22].std())
    assert diagnostics["outlier_pixels_replaced"] >= 1
    assert diagnostics["rooftop_regions_flattened"] >= 1
    assert diagnostics["maximum_adjacent_delta_after"] <= 0.500001
    assert diagnostics["numeric_surface_unchanged"] is True
