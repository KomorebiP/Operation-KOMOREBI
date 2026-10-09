from __future__ import annotations

import io
import json
import zipfile
from dataclasses import asdict
from typing import Any

import numpy as np
import pytest

from am_spd import (
    AMSpdConfig,
    AMSpdModel,
    TiledAMSpdModel,
    TiledConfig,
    load_model_archive,
    reconstruct,
    tiled_reconstruct,
)
from am_spd.atlas import synthetic_geometry
from am_spd.model import _array_payload, _sha256


def basic_model() -> AMSpdModel:
    return AMSpdModel(
        reconstruction=np.zeros((8, 8, 1)),
        selected_method="core",
        parameter_count=0,
        packet_count=0,
        config={},
        metrics={},
        candidate_rmse={},
        residual_storage="dense",
        archive_residual=np.zeros((8, 8, 1)),
    )


def basic_tiled_model() -> TiledAMSpdModel:
    return TiledAMSpdModel(
        reconstruction=np.zeros((8, 8, 1)),
        config={},
        tiled_config=asdict(TiledConfig(tile_size=8, overlap=0)),
        metrics={},
        parameter_count=0,
        packet_count=0,
        residual_storage="dense",
        archive_residual=np.zeros((8, 8, 1)),
        tile_records=[{
            "region": {
                "index": 0, "y0": 0, "x0": 0, "y1": 8, "x1": 8,
                "top_overlap": 0, "bottom_overlap": 0, "left_overlap": 0, "right_overlap": 0,
            },
            "summary": {"parameter_count": 0, "packet_count": 0},
        }],
    )


@pytest.mark.parametrize("factory", [basic_model, basic_tiled_model])
@pytest.mark.parametrize("change", [
    {"archive_residual": np.full((8, 8, 1), np.nan)},
    {"input_image": np.full((8, 8, 1), np.inf)},
    {"reconstruction": np.zeros((8, 8))},
    {"reconstruction": np.zeros((0, 8, 1))},
    {"residual_threshold": float("nan")},
    {"residual_threshold": float("inf")},
    {"parameter_count": -1},
    {"packet_count": 0.5},
    {"metrics": {"rmse": float("nan")}},
    {"metrics": {"psnr": float("-inf")}},
    {"residual_storage": "sparse", "residual_indices": np.zeros((1, 1), dtype=np.int64),
     "residual_values": np.zeros((1, 1)), "input_image": np.zeros((8, 8, 1))},
    {"residual_storage": "sparse", "residual_indices": np.array([[0.5, 1.0]]), "residual_values": np.zeros((1, 1))},
    {"residual_storage": "sparse", "residual_indices": np.array([[0, 0], [0, 0]]), "residual_values": np.zeros((2, 1))},
    {"residual_storage": "sparse", "residual_indices": np.array([[8, 0]]), "residual_values": np.zeros((1, 1)),
     "input_image": np.zeros((8, 8, 1))},
    {"residual_storage": "sparse", "residual_indices": np.array([[0, 0]]), "residual_values": np.zeros((1, 2))},
])
def test_invalid_closure_returns_failed_report_without_decoding(factory, change: dict[str, Any]) -> None:
    model = factory()
    for name, value in change.items():
        setattr(model, name, value)
    report = model.verify()
    assert report["passed"] is False
    assert report["errors"]
    with pytest.raises(ValueError, match="validation failed"):
        model.to_bytes()


@pytest.mark.parametrize("change", [
    {"core_atoms": np.zeros((1, 2, 2)), "packet_specs": [{"kind": "constant", "params": []}]},
    {"core_atoms": np.zeros((1, 8, 8)), "core_coefficients": np.zeros((1, 2)),
     "packet_specs": [{"kind": "constant", "params": []}]},
    {"singular_directions": np.zeros((1, 2, 2, 1))},
    {"singular_coefficients": np.array([float("nan")])},
    {"search_seed_ids": np.array([1, 1]), "search_seed_masks": np.zeros((2, 8, 8))},
    {"packet_specs": [{"kind": "unknown", "params": []}]},
    {"packet_specs": [{"kind": "dct", "params": [0]}]},
])
def test_invalid_packet_components_are_rejected(change: dict[str, Any]) -> None:
    model = basic_model()
    for name, value in change.items():
        setattr(model, name, value)
    assert model.verify()["passed"] is False


def change_archive(payload: bytes, *, metadata: dict[str, Any] | None = None,
                   array: tuple[str, np.ndarray] | None = None) -> bytes:
    output = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(payload)) as source, zipfile.ZipFile(output, "w") as destination:
        manifest = json.loads(source.read("manifest.json"))
        if metadata:
            manifest.update(metadata)
        replacements = {}
        if array:
            name, value = array
            record = manifest["arrays"][name]
            value_payload = _array_payload(value)
            record.update(shape=list(value.shape), dtype=str(value.dtype), sha256=_sha256(value_payload), nbytes=value.nbytes)
            replacements[record["path"]] = value_payload
        destination.writestr("manifest.json", json.dumps(manifest))
        for item in source.infolist():
            if item.filename != "manifest.json":
                destination.writestr(item, replacements.get(item.filename, source.read(item.filename)))
    return output.getvalue()


@pytest.mark.parametrize("factory,loader", [(basic_model, AMSpdModel.from_bytes), (basic_tiled_model, TiledAMSpdModel.from_bytes)])
@pytest.mark.parametrize("metadata", [
    {"arrays": []},
    {"metrics": []},
    {"schema_version": 1.5},
    {"parameter_count": 0.5},
    {"residual_threshold": "invalid"},
])
def test_malformed_archive_metadata_raises_value_error(factory, loader, metadata) -> None:
    with pytest.raises(ValueError):
        loader(change_archive(factory().to_bytes(), metadata=metadata))


@pytest.mark.parametrize("factory,loader", [(basic_model, AMSpdModel.from_bytes), (basic_tiled_model, TiledAMSpdModel.from_bytes)])
def test_fractional_sparse_archive_indices_are_not_silently_truncated(factory, loader) -> None:
    model = factory()
    model.residual_storage = "sparse"
    model.archive_residual = None
    model.residual_indices = np.array([[0, 0]], dtype=np.int64)
    model.residual_values = np.zeros((1, 1))
    payload = change_archive(model.to_bytes(), array=("residual_indices", np.array([[0.5, 0.0]])))
    with pytest.raises(ValueError, match="integer"):
        loader(payload)


@pytest.mark.parametrize("loader", [AMSpdModel.from_bytes, TiledAMSpdModel.from_bytes])
def test_non_archive_payload_has_clear_value_error(loader) -> None:
    with pytest.raises(ValueError, match="invalid"):
        loader(b"This is not a model archive.")


@pytest.mark.parametrize("factory,loader", [(basic_model, AMSpdModel.from_bytes), (basic_tiled_model, TiledAMSpdModel.from_bytes)])
def test_infinite_psnr_is_valid_for_perfect_reconstruction(factory, loader) -> None:
    model = factory()
    model.metrics = {"rmse": 0.0, "psnr": float("inf")}
    loaded = loader(model.to_bytes())
    assert loaded.verify()["passed"] is True
    assert loaded.metrics["psnr"] == float("inf")


@pytest.mark.parametrize("field,value", [("tile_size", 8.5), ("tile_size", True), ("overlap", 0.5), ("workers", 1.5)])
def test_tiled_configuration_requires_integer_sizes_and_workers(field: str, value: Any) -> None:
    with pytest.raises(ValueError):
        TiledConfig(**{field: value})


def small_config() -> AMSpdConfig:
    return AMSpdConfig(method="core", packet_budget=2, singular_budget=1, tree_depth=1,
                       max_rank=1, max_actions=1, max_regions=2, max_candidates_per_iteration=20)


@pytest.mark.parametrize("change", [
    {"random_state": {}},
    {"next_seed_id": -1},
    {"selected_seed_ids": [999999]},
    {"quadtree_leaves": [[0, 0, 100, 100]]},
    {"candidate_specs": [{"kind": "mask", "params": [999999], "depth": 0, "complexity": 1.0}]},
])
def test_exact_continuation_state_is_validated(change: dict[str, Any]) -> None:
    model = reconstruct(synthetic_geometry(12), small_config()).to_model(include_input=True)
    assert model.verify()["passed"] is True
    model.search_state.update(change)
    assert model.verify()["passed"] is False


@pytest.mark.filterwarnings("ignore:divide by zero encountered in scalar divide:RuntimeWarning")
def test_constant_tiled_image_can_be_saved_with_infinite_psnr() -> None:
    result = tiled_reconstruct(np.zeros((8, 8, 1)), small_config(), TiledConfig(tile_size=8, overlap=0))
    loaded = TiledAMSpdModel.from_bytes(result.to_model().to_bytes())
    np.testing.assert_array_equal(loaded.decode("exact"), np.zeros((8, 8, 1)))
    assert loaded.metrics["psnr"] == float("inf")


def test_malformed_embedded_packet_metadata_returns_failed_report() -> None:
    model = basic_tiled_model()
    tile = basic_model()
    tile.packet_specs = None
    model.tile_models = [tile]
    assert model.verify()["passed"] is False


def test_tiled_resume_requires_top_level_source_or_residual() -> None:
    model = basic_tiled_model()
    tile = reconstruct(synthetic_geometry(12), small_config()).to_model(include_input=True)
    model.tile_models = [tile]
    model.residual_storage = "none"
    model.archive_residual = None
    assert model.supports_resume is False


def test_generic_loader_reports_non_archive_payload(tmp_path) -> None:
    path = tmp_path / "invalid.amspd"
    path.write_bytes(b"not an archive")
    with pytest.raises(ValueError, match="invalid"):
        load_model_archive(path)
