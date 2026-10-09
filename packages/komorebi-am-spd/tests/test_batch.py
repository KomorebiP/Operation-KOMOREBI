from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from am_spd import AMSpdConfig, TiledConfig, load_model_archive, run_batch
from am_spd.io import save_image


def config() -> AMSpdConfig:
    return AMSpdConfig(
        method="core",
        packet_budget=2,
        singular_budget=1,
        tree_depth=1,
        max_rank=1,
        max_actions=1,
        max_regions=3,
        max_candidates_per_iteration=20,
        tolerance=0.0,
    )


def test_batch_processes_single_and_tiled_images(tmp_path: Path) -> None:
    inputs = tmp_path / "inputs"
    nested = inputs / "nested"
    nested.mkdir(parents=True)
    save_image(inputs / "small.png", np.linspace(0.0, 1.0, 10 * 10).reshape(10, 10, 1))
    save_image(nested / "large.png", np.linspace(0.0, 1.0, 18 * 18 * 3).reshape(18, 18, 3))

    output = tmp_path / "output"
    result = run_batch(
        inputs,
        output,
        config(),
        workers=2,
        save_models=True,
        include_input_in_models=True,
        tile_config=TiledConfig(tile_size=12, overlap=4),
        tiled_above=12,
        save_tile_models=True,
    )

    assert result.passed is True
    assert {record.mode for record in result.records} == {"single", "tiled"}
    assert all(record.status == "completed" for record in result.records)
    assert (output / "batch.json").exists()
    assert (output / "batch.csv").exists()
    assert json.loads((output / "batch.json").read_text())["counts"]["completed"] == 2
    for record in result.records:
        assert record.exact_identity_error is not None and record.exact_identity_error <= 1e-12
        assert record.model is not None
        assert load_model_archive(record.model).verify()["passed"] is True


def test_batch_skip_existing_is_resumable(tmp_path: Path) -> None:
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    save_image(inputs / "one.png", np.ones((8, 8, 1)) * 0.5)
    output = tmp_path / "output"
    first = run_batch(inputs, output, config())
    second = run_batch(inputs, output, config(), skip_existing=True)
    assert first.records[0].status == "completed"
    assert second.records[0].status == "skipped"
    assert second.records[0].run_fingerprint == first.records[0].run_fingerprint

    save_image(inputs / "one.png", np.ones((8, 8, 1)) * 0.25)
    changed = run_batch(inputs, output, config(), skip_existing=True)
    assert changed.records[0].status == "completed"
    assert changed.records[0].input_sha256 != first.records[0].input_sha256

    from dataclasses import replace

    changed_config = run_batch(inputs, output, replace(config(), packet_budget=3), skip_existing=True)
    assert changed_config.records[0].status == "completed"
    assert changed_config.run_fingerprint != changed.run_fingerprint


def test_batch_skip_reprocesses_changed_input(tmp_path: Path) -> None:
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    source = inputs / "one.png"
    save_image(source, np.linspace(0.0, 1.0, 8 * 8).reshape(8, 8, 1))
    output = tmp_path / "output"
    first = run_batch(inputs, output, config())
    first_digest = first.records[0].input_sha256

    save_image(source, np.linspace(1.0, 0.0, 8 * 8).reshape(8, 8, 1))
    second = run_batch(inputs, output, config(), skip_existing=True)
    assert second.records[0].status == "completed"
    assert second.records[0].input_sha256 != first_digest
