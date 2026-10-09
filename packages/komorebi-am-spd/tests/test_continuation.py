from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np

from am_spd import AMSpdConfig, AMSpdModel, reconstruct, resume_model
from am_spd.atlas import synthetic_geometry


def core_config(packet_budget: int) -> AMSpdConfig:
    return AMSpdConfig(
        method="core",
        packet_budget=packet_budget,
        singular_budget=1,
        tree_depth=1,
        max_rank=1,
        max_actions=1,
        max_regions=3,
        max_candidates_per_iteration=40,
        tolerance=0.0,
    )


def test_schema_two_exact_resume_matches_uninterrupted_run(tmp_path: Path) -> None:
    image = synthetic_geometry(12)
    initial = reconstruct(image, core_config(4))
    model_path = initial.save_model(
        tmp_path / "checkpoint.amspd",
        residual_storage="dense",
        include_input=True,
        include_atoms=True,
    )
    model = AMSpdModel.load(model_path)

    assert model.schema_version == 2
    assert model.supports_resume is True
    assert model.resume_state_quality == "exact"

    resumed = resume_model(model, target_packet_budget=6)
    uninterrupted = reconstruct(image, core_config(6))

    assert resumed.run_metadata["resume_state_quality"] == "exact"
    assert resumed.packet_count == uninterrupted.packet_count
    assert [spec.key for spec in resumed.core_result.active_specs] == [
        spec.key for spec in uninterrupted.core_result.active_specs
    ]
    np.testing.assert_allclose(resumed.reconstruction, uninterrupted.reconstruction, atol=0.0, rtol=0.0)
    assert resumed.exact_identity_error <= 1e-12


def test_model_resume_convenience_can_change_downstream_method(tmp_path: Path) -> None:
    image = synthetic_geometry(12)
    initial = reconstruct(image, core_config(3))
    model = AMSpdModel.load(
        initial.save_model(tmp_path / "checkpoint.amspd", residual_storage="sparse", include_input=True)
    )
    resumed = model.resume(2, method="spd", config=replace(core_config(3), method="spd", singular_budget=1))

    assert resumed.config.method == "spd"
    assert resumed.packet_count >= initial.packet_count
    assert resumed.singular_result is not None
    assert resumed.exact_identity_error <= 1e-12


def test_schema_one_model_uses_deterministic_warm_resume(tmp_path: Path) -> None:
    import json
    import zipfile

    image = synthetic_geometry(12)
    initial = reconstruct(image, core_config(3))
    current_path = initial.save_model(
        tmp_path / "schema-two.amspd",
        residual_storage="dense",
        include_input=True,
        include_atoms=True,
    )
    legacy_path = tmp_path / "schema-one.amspd"
    with zipfile.ZipFile(current_path, "r") as source, zipfile.ZipFile(legacy_path, "w") as destination:
        manifest = json.loads(source.read("manifest.json"))
        manifest["schema_version"] = 1
        manifest.pop("search_state", None)
        arrays = manifest.get("arrays", {})
        arrays.pop("search_seed_masks", None)
        arrays.pop("search_seed_ids", None)
        destination.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        for item in source.infolist():
            if item.filename == "manifest.json" or item.filename in {
                "arrays/search_seed_masks.npy",
                "arrays/search_seed_ids.npy",
            }:
                continue
            destination.writestr(item, source.read(item.filename))

    legacy = AMSpdModel.load(legacy_path)
    assert legacy.schema_version == 1
    assert legacy.supports_resume is True
    assert legacy.resume_state_quality == "warm"
    resumed = legacy.resume(1, method="core")
    assert resumed.packet_count >= initial.packet_count
    assert resumed.exact_identity_error <= 1e-12
