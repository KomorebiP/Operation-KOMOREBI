from __future__ import annotations

import dataclasses
import hashlib
import json
from pathlib import Path
import sys

import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workspace_scaling import make_batch, train_and_evaluate  # noqa: E402


def test_preoutcome_freeze_is_unchanged() -> None:
    path = ROOT / "validation/PREOUTCOME_FREEZE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    companion = path.with_suffix(path.suffix + ".sha256")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == companion.read_text().split()[0]
    assert payload["status"] == "FROZEN_BEFORE_HOLDOUT"
    assert payload["holdout_outcomes_inspected"] is False
    assert payload["file_count"] == len(payload["files"]) == 9
    for relative, expected in payload["files"].items():
        source = ROOT / relative
        assert source.is_file()
        assert source.stat().st_size == expected["size_bytes"]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == expected["sha256"]


def test_task_has_exact_nested_circular_composition() -> None:
    batch = make_batch(1024, torch.Generator().manual_seed(54054))
    values = batch["values"]
    reconstructed_u = torch.remainder(values[:, 0] + values[:, 1], 1.0)
    reconstructed_v = torch.remainder(values[:, 2] + values[:, 3], 1.0)
    reconstructed_y = torch.remainder(reconstructed_u + reconstructed_v, 1.0)
    reconstructed_actions = torch.remainder(values + reconstructed_y[:, None], 1.0)
    def circular_error(left: torch.Tensor, right: torch.Tensor) -> torch.Tensor:
        return torch.abs(torch.remainder(left - right + 0.5, 1.0) - 0.5)

    assert float(circular_error(reconstructed_u, batch["u"]).max()) <= 2e-7
    assert float(circular_error(reconstructed_v, batch["v"]).max()) <= 2e-7
    assert float(circular_error(reconstructed_y, batch["y"]).max()) <= 3e-7
    expected_phase = torch.stack(
        (
            torch.cos(2.0 * torch.pi * reconstructed_actions),
            torch.sin(2.0 * torch.pi * reconstructed_actions),
        ),
        dim=-1,
    )
    assert torch.allclose(expected_phase, batch["action_phase"], atol=2e-6, rtol=0.0)


def test_frozen_holdout_recomputes_and_keeps_failed_thresholds() -> None:
    rows = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((ROOT / "holdout_results/points").glob("*.json"))
    ]
    assert len(rows) == 28
    frame = pd.DataFrame(rows)
    summary = json.loads((ROOT / "holdout_results/HOLDOUT_ANALYSIS.json").read_text())
    assert frame["uses_intermediate_workspace_labels_for_training"].eq(False).all()
    assert frame["valence_model_present"].eq(False).all()
    assert frame["self_preservation_reward"].eq(0.0).all()
    assert summary["status"] == "V054_HOLDOUT_ENDPOINTS_NOT_MET"
    assert summary["all_endpoints_met"] is False
    assert sum(bool(value) for value in summary["endpoints"].values()) == 13
    assert summary["endpoints"]["E05_d2_400_near_above"] is False
    assert summary["endpoints"]["E06_d2_800_above"] is False
    assert summary["endpoints"]["E15_above_action"] is False
    d1 = frame[(frame.bottleneck_dim == 1) & (frame.hidden_width == 64)]
    assert d1.emergence.sum() == 0
    assert d1.action_accuracy.mean() <= 0.15


def test_formula_orders_dimension_and_posthoc_boundary() -> None:
    validation = json.loads(
        (ROOT / "holdout_results/SCALING_VALIDATION.json").read_text(encoding="utf-8")
    )
    assert validation["original_formula_holdout"]["auc"] >= 0.89
    thresholds = {
        (entry["dim"], entry["hidden"]): entry
        for entry in validation["posthoc_combined_formula"]["thresholds"]
    }
    assert thresholds[(4, 16)]["steps_p50_single_seed"] < thresholds[(2, 32)]["steps_p50_single_seed"]
    assert thresholds[(4, 8)]["steps_p50_single_seed"] < thresholds[(2, 8)]["steps_p50_single_seed"]
    posthoc = validation["posthoc_d2_h32_s1200"]
    assert posthoc["n"] == 4
    assert posthoc["emergence_rate"] == 1.0
    assert posthoc["mean_action_accuracy"] >= 0.99
    assert posthoc["mean_probe_accuracy"] >= 0.99
    assert posthoc["mean_patch_accuracy"] >= 0.99
    assert posthoc["mean_cut_accuracy"] <= 0.15


def test_representative_frozen_replays_are_exact() -> None:
    names = [
        "d2_h32_s400_seed346151134.json",
        "d4_h16_s400_seed346151134.json",
    ]
    for name in names:
        saved = json.loads(
            (ROOT / "holdout_results/points" / name).read_text(encoding="utf-8")
        )
        replay = dataclasses.asdict(
            train_and_evaluate(
                dim=int(saved["bottleneck_dim"]),
                hidden=int(saved["hidden_width"]),
                steps=int(saved["steps"]),
                seed=int(saved["seed"]),
                eval_cases=4096,
                calibration_cases=2048,
                patch_cases=2048,
            )
        )
        for key, value in replay.items():
            if key == "train_seconds":
                continue
            assert value == saved[key]
