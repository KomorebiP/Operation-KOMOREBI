from __future__ import annotations

import io
import json
import zipfile
from pathlib import Path

import numpy as np

from am_spd import AMSpdConfig, AMSpdModel, reconstruct, resume_model
from am_spd.atlas import synthetic_geometry
from am_spd.cli import main
from am_spd.io import save_image


def config(packet_budget: int, method: str = "core") -> AMSpdConfig:
    return AMSpdConfig(
        method=method,
        packet_budget=packet_budget,
        singular_budget=2,
        tree_depth=1,
        max_rank=1,
        reopen_fractions=(0.2,),
        max_actions=1,
        max_regions=4,
        max_candidates_per_iteration=36,
        residual_refresh=3,
        quadtree_refine_every=2,
        random_seed=1729,
    )


def test_exact_resume_matches_uninterrupted_search(tmp_path: Path) -> None:
    image = synthetic_geometry(12)
    partial = reconstruct(image, config(4))
    model_path = partial.save_model(
        tmp_path / "partial.amspd",
        residual_storage="sparse",
        include_input=True,
        include_atoms=True,
    )
    model = AMSpdModel.load(model_path)

    assert model.schema_version == 2
    assert model.supports_resume is True
    assert model.resume_state_quality == "exact"

    resumed = resume_model(model, config(6), target_packet_budget=6)
    uninterrupted = reconstruct(image, config(6))

    assert resumed.packet_count == uninterrupted.packet_count == 6
    assert resumed.run_metadata["resume_state_quality"] == "exact"
    np.testing.assert_array_equal(resumed.reconstruction, uninterrupted.reconstruction)
    np.testing.assert_array_equal(resumed.archive_residual, uninterrupted.archive_residual)
    assert [spec.key for spec in resumed.core_result.active_specs] == [
        spec.key for spec in uninterrupted.core_result.active_specs
    ]


def test_exact_frontier_without_stored_input_is_classified_separately() -> None:
    image = synthetic_geometry(12)
    partial = reconstruct(image, config(4))
    model = partial.to_model(residual_storage="dense", include_input=False, include_atoms=True)
    assert model.supports_resume is True
    assert model.resume_state_quality == "frontier-exact"
    resumed = resume_model(model, config(6), target_packet_budget=6)
    uninterrupted = reconstruct(image, config(6))
    assert [spec.key for spec in resumed.core_result.active_specs] == [
        spec.key for spec in uninterrupted.core_result.active_specs
    ]
    np.testing.assert_array_equal(resumed.reconstruction, uninterrupted.reconstruction)


def _downgrade_to_schema_one(model: AMSpdModel) -> AMSpdModel:
    source = io.BytesIO(model.to_bytes())
    destination = io.BytesIO()
    with zipfile.ZipFile(source, "r") as archive, zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_DEFLATED
    ) as output:
        manifest = json.loads(archive.read("manifest.json"))
        manifest["schema_version"] = 1
        manifest.pop("search_state", None)
        arrays = manifest.get("arrays", {})
        omitted = {
            arrays.get("search_seed_masks", {}).get("path"),
            arrays.get("search_seed_ids", {}).get("path"),
        }
        arrays.pop("search_seed_masks", None)
        arrays.pop("search_seed_ids", None)
        output.writestr("manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
        for item in archive.infolist():
            if item.filename == "manifest.json" or item.filename in omitted:
                continue
            output.writestr(item, archive.read(item.filename))
    return AMSpdModel.from_bytes(destination.getvalue())


def test_schema_one_model_resumes_as_deterministic_warm_start() -> None:
    image = synthetic_geometry(12)
    partial = reconstruct(image, config(4))
    schema_two = partial.to_model(residual_storage="dense", include_input=True, include_atoms=True)
    schema_one = _downgrade_to_schema_one(schema_two)

    assert schema_one.schema_version == 1
    assert schema_one.supports_resume is True
    assert schema_one.resume_state_quality == "warm"

    first = resume_model(schema_one, config(6), target_packet_budget=6)
    second = resume_model(schema_one, config(6), target_packet_budget=6)
    assert first.packet_count == second.packet_count == 6
    np.testing.assert_array_equal(first.reconstruction, second.reconstruction)
    assert first.run_metadata["resume_state_quality"] == "warm"


def test_cli_resume_increases_packet_budget(tmp_path: Path, capsys) -> None:
    image = synthetic_geometry(12)
    input_path = save_image(tmp_path / "input.png", image)
    partial_path = tmp_path / "partial.amspd"
    resumed_path = tmp_path / "resumed.amspd"

    common = [
        "--method",
        "core",
        "--packet-budget",
        "4",
        "--singular-budget",
        "2",
        "--tree-depth",
        "1",
        "--max-rank",
        "1",
        "--max-actions",
        "1",
        "--max-regions",
        "4",
        "--max-candidates",
        "36",
        "--residual-refresh",
        "3",
        "--quadtree-refine-every",
        "2",
        "--seed",
        "1729",
        "--include-input",
    ]
    assert main(["decompose", str(input_path), str(partial_path), *common]) == 0
    capsys.readouterr()

    assert main(
        [
            "resume",
            str(partial_path),
            str(resumed_path),
            "--target-packet-budget",
            "6",
            "--method",
            "core",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source_resume_state_quality"] == "exact"
    assert payload["result"]["packet_count"] == 6

    resumed = AMSpdModel.load(resumed_path)
    assert resumed.packet_count == 6
    assert resumed.supports_resume is True
    assert resumed.input_image is not None
    assert resumed.resume_state_quality == "exact"
