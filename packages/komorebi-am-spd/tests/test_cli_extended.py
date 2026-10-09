from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from am_spd.cli import main
from am_spd.io import save_image

SMALL_OPTIONS = [
    "--method",
    "core",
    "--packet-budget",
    "3",
    "--singular-budget",
    "1",
    "--tree-depth",
    "1",
    "--max-rank",
    "1",
    "--max-actions",
    "1",
    "--max-regions",
    "3",
    "--max-candidates",
    "24",
]


def test_cli_model_lifecycle(tmp_path: Path, capsys) -> None:
    image = np.linspace(0.0, 1.0, 10 * 10 * 3).reshape(10, 10, 3)
    input_path = save_image(tmp_path / "input.png", image)
    model_path = tmp_path / "image.amspd"

    assert main(["decompose", str(input_path), str(model_path), "--include-input", *SMALL_OPTIONS]) == 0
    assert model_path.exists()
    capsys.readouterr()

    exact_path = tmp_path / "exact.npy"
    assert main(["decode", str(model_path), str(exact_path), "--mode", "exact"]) == 0
    recovered = np.load(exact_path, allow_pickle=False)
    np.testing.assert_allclose(recovered, image, atol=1.0 / 255.0, rtol=0.0)
    capsys.readouterr()

    inspect_path = tmp_path / "inspection.json"
    assert main(["inspect", str(model_path), "--packets", "--output", str(inspect_path)]) == 0
    payload = json.loads(inspect_path.read_text())
    assert payload["verification"]["passed"] is True
    assert payload["packets"]


def test_cli_complete_and_small_benchmark(tmp_path: Path, capsys) -> None:
    image = np.linspace(0.0, 1.0, 10 * 10 * 3).reshape(10, 10, 3)
    input_path = save_image(tmp_path / "input.png", image)
    model_path = tmp_path / "complete.amspd"
    assert main(["complete", str(input_path), str(model_path), *SMALL_OPTIONS]) == 0
    complete_payload = json.loads(capsys.readouterr().out)
    assert complete_payload["identity_error"] <= 1e-12

    output_dir = tmp_path / "benchmark"
    assert main(
        [
            "benchmark",
            "--output-dir",
            str(output_dir),
            "--cases",
            "synthetic_geometry",
            "--methods",
            "core",
            "--size",
            "8",
        ]
    ) == 0
    capsys.readouterr()
    assert (output_dir / "benchmark.json").exists()
    assert (output_dir / "benchmark.csv").exists()


def test_cli_lists_paper_cases(capsys) -> None:
    assert main(["reproduce-paper", "--list-cases"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert "synthetic_geometry" in payload["paper_cases"]


def test_cli_converts_legacy_archive(tmp_path: Path, capsys) -> None:
    image = np.linspace(0.0, 1.0, 10 * 10 * 3).reshape(10, 10, 3)
    input_path = save_image(tmp_path / "input.png", image)
    reconstruction_path = tmp_path / "reconstruction.png"
    legacy_path = tmp_path / "legacy.npz"

    assert main(
        [
            "reconstruct",
            str(input_path),
            str(reconstruction_path),
            "--archive",
            str(legacy_path),
            *SMALL_OPTIONS,
        ]
    ) == 0
    capsys.readouterr()

    model_path = tmp_path / "converted.amspd"
    assert main(["convert-archive", str(legacy_path), str(model_path)]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["verification"]["passed"] is True
    assert model_path.exists()

    exact_path = tmp_path / "converted-exact.npy"
    assert main(["decode", str(model_path), str(exact_path), "--mode", "exact"]) == 0
    recovered = np.load(exact_path, allow_pickle=False)
    np.testing.assert_allclose(recovered, image, atol=1.0 / 255.0, rtol=0.0)


def test_cli_resume_and_tiled_lifecycle(tmp_path: Path, capsys) -> None:
    image = np.linspace(0.0, 1.0, 14 * 16 * 3).reshape(14, 16, 3)
    input_path = save_image(tmp_path / "input.png", image)

    checkpoint = tmp_path / "checkpoint.amspd"
    assert main(
        [
            "decompose",
            str(input_path),
            str(checkpoint),
            "--include-input",
            "--method",
            "core",
            "--packet-budget",
            "3",
            "--max-candidates",
            "24",
            "--tolerance",
            "0",
        ]
    ) == 0
    capsys.readouterr()

    resumed = tmp_path / "resumed.amspd"
    assert main(
        [
            "resume",
            str(checkpoint),
            str(resumed),
            "--target-packet-budget",
            "5",
            "--method",
            "core",
            "--include-input",
        ]
    ) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["source_resume_state_quality"] == "exact"
    assert payload["result"]["packet_count"] >= 3

    tiled_model = tmp_path / "image.amspdt"
    preview = tmp_path / "tiled.png"
    assert main(
        [
            "tiled",
            str(input_path),
            str(tiled_model),
            "--preview",
            str(preview),
            "--tile-size",
            "10",
            "--overlap",
            "2",
            "--include-input",
            "--method",
            "core",
            "--packet-budget",
            "2",
            "--max-candidates",
            "20",
        ]
    ) == 0
    tiled_payload = json.loads(capsys.readouterr().out)
    assert tiled_payload["result"]["tile_count"] > 1
    assert tiled_model.exists()

    resumed_tiled = tmp_path / "resumed.amspdt"
    assert main(
        [
            "resume",
            str(tiled_model),
            str(resumed_tiled),
            "--target-packet-budget",
            "3",
            "--method",
            "core",
            "--workers",
            "2",
        ]
    ) == 0
    resumed_payload = json.loads(capsys.readouterr().out)
    assert resumed_payload["source_format"] == "tiled"
    assert resumed_payload["result"]["tile_count"] == tiled_payload["result"]["tile_count"]

    exact = tmp_path / "tiled-exact.npy"
    assert main(["decode", str(tiled_model), str(exact), "--mode", "exact"]) == 0
    capsys.readouterr()
    np.testing.assert_allclose(np.load(exact, allow_pickle=False), image, atol=1.0 / 255.0, rtol=0.0)


def test_cli_tune_and_batch(tmp_path: Path, capsys) -> None:
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    image = np.linspace(0.0, 1.0, 10 * 10 * 3).reshape(10, 10, 3)
    input_path = save_image(inputs / "input.png", image)

    tuning_dir = tmp_path / "tuning"
    assert main(
        [
            "tune",
            str(input_path),
            "--output-dir",
            str(tuning_dir),
            "--methods",
            "core",
            "--packet-budgets",
            "2",
            "3",
            "--singular-budgets",
            "1",
            "--tree-depths",
            "1",
            "--max-ranks",
            "1",
            "--max-candidates",
            "20",
            "--objective",
            "rmse",
            "--save-model",
        ]
    ) == 0
    tune_payload = json.loads(capsys.readouterr().out)
    assert len(tune_payload["records"]) == 2
    assert (tuning_dir / "tuning.csv").exists()
    assert (tuning_dir / "best.amspd").exists()

    batch_dir = tmp_path / "batch"
    assert main(
        [
            "batch",
            str(inputs),
            "--output-dir",
            str(batch_dir),
            "--save-models",
            "--method",
            "core",
            "--packet-budget",
            "2",
            "--singular-budget",
            "1",
            "--tree-depth",
            "1",
            "--max-rank",
            "1",
            "--max-actions",
            "1",
            "--max-regions",
            "3",
            "--max-candidates",
            "20",
        ]
    ) == 0
    batch_payload = json.loads(capsys.readouterr().out)
    assert batch_payload["counts"]["completed"] == 1
    assert (batch_dir / "batch.csv").exists()
