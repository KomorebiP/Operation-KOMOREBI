from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import pytest

from am_spd import AMSpdConfig, AMSpdModel, reconstruct
from am_spd.atlas import synthetic_geometry


def config() -> AMSpdConfig:
    return AMSpdConfig(
        method="portfolio",
        packet_budget=4,
        singular_budget=2,
        tree_depth=1,
        max_rank=1,
        reopen_fractions=(0.2,),
        max_actions=1,
        max_regions=4,
        max_candidates_per_iteration=36,
    )


@pytest.mark.parametrize("storage", ["dense", "sparse"])
def test_model_roundtrip_exact_closure(tmp_path: Path, storage: str) -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, config())
    path = result.save_model(tmp_path / "image.amspd", residual_storage=storage, include_input=True)
    model = AMSpdModel.load(path)

    assert model.verify()["passed"] is True
    assert model.selected_method == result.selected_method
    assert model.packet_count == result.packet_count
    assert model.packet_specs
    assert model.portfolio_trials
    np.testing.assert_allclose(model.decode("raw"), result.reconstruction)
    np.testing.assert_allclose(model.decode("exact"), image, atol=1e-12, rtol=0.0)


def test_approximation_only_model_rejects_exact_decode(tmp_path: Path) -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, config())
    model = AMSpdModel.load(result.save_model(tmp_path / "approx.amspd", residual_storage="none"))
    assert model.has_exact_closure is False
    with pytest.raises(ValueError, match="unthresholded exact residual"):
        model.decode("exact")


def test_model_checksum_detects_tampering(tmp_path: Path) -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, config())
    original = result.save_model(tmp_path / "original.amspd", residual_storage="dense")
    tampered = tmp_path / "tampered.amspd"
    with zipfile.ZipFile(original, "r") as source, zipfile.ZipFile(tampered, "w") as destination:
        for item in source.infolist():
            payload = source.read(item.filename)
            if item.filename == "arrays/reconstruction.npy":
                payload = payload[:-1] + bytes([payload[-1] ^ 1])
            destination.writestr(item, payload)
    with pytest.raises(ValueError, match="checksum mismatch"):
        AMSpdModel.load(tampered)


def test_thresholded_sparse_model_is_marked_lossy(tmp_path: Path) -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, config())
    model = AMSpdModel.load(
        result.save_model(
            tmp_path / "thresholded.amspd",
            residual_storage="sparse",
            residual_threshold=1e-3,
        )
    )
    assert model.has_residual_closure is True
    assert model.has_exact_closure is False
    with pytest.raises(ValueError, match="unthresholded exact residual"):
        model.decode("exact")


def test_legacy_archive_conversion_preserves_exact_closure(tmp_path: Path) -> None:
    image = synthetic_geometry(12)
    result = reconstruct(image, config())
    legacy = result.save_archive(tmp_path / "legacy.npz")

    converted = AMSpdModel.from_legacy_archive(legacy, residual_storage="sparse")
    path = converted.save(tmp_path / "converted.amspd")
    loaded = AMSpdModel.load(path)

    assert loaded.verify()["passed"] is True
    assert loaded.provenance["converted_from"] == "am-spd-0.1.x-npz"
    assert loaded.packet_specs == []
    np.testing.assert_allclose(loaded.decode("exact"), image, atol=1e-12, rtol=0.0)
