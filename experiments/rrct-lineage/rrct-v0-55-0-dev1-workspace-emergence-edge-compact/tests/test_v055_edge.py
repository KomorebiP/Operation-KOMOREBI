from __future__ import annotations

import pathlib
import sys

import torch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from workspace_edge import (
    CheckpointResult,
    NestedWorkspaceModel,
    classify_emergence,
    onset_statistics,
    train_trajectory,
)


def test_parameter_matching() -> None:
    settings = [(1, 44), (2, 32), (3, 25), (4, 20), (6, 14), (8, 10)]
    counts = [NestedWorkspaceModel(dim, hidden).parameter_count() for dim, hidden in settings]
    assert max(abs(count - 2480) / 2480 for count in counts) <= 0.05


def _row(step: int, flag: bool) -> CheckpointResult:
    return CheckpointResult(
        step=step,
        train_loss=0.0,
        action_accuracy=1.0 if flag else 0.0,
        probe_accuracy=1.0 if flag else 0.0,
        probe_r2=1.0 if flag else 0.0,
        patch_accuracy=1.0 if flag else 0.0,
        cut_accuracy=0.0,
        order_parameter=1.0 if flag else 0.0,
        emergence_margin=0.01 if flag else -0.95,
        emergence=flag,
        local_a_effective_rank=2.0,
        local_b_effective_rank=2.0,
        global_effective_rank=2.0,
        minimum_effective_rank=2.0,
        minimum_second_to_first_ratio=1.0,
        minimum_top2_variance_fraction=1.0,
        mean_latent_norm=1.0,
    )


def test_stable_onset_rejects_transient_hit() -> None:
    stats = onset_statistics([_row(100, False), _row(200, True), _row(300, False), _row(400, True)])
    assert stats["first_hit_step"] == 200
    assert stats["stable_onset_step"] == 400
    assert stats["relapse_count_after_first_hit"] == 1


def test_threshold_logic() -> None:
    assert classify_emergence(0.98, 0.95, 0.95, 0.15)[0]
    assert not classify_emergence(0.979, 1.0, 1.0, 0.0)[0]


def test_short_trajectory_is_deterministic() -> None:
    kwargs = dict(
        dim=2,
        hidden=8,
        base_seed=55123,
        checkpoints=(10, 20),
        batch_size=32,
        eval_cases=64,
        calibration_cases=64,
        patch_cases=32,
    )
    first = train_trajectory(**kwargs)
    second = train_trajectory(**kwargs)
    assert first.checkpoints == second.checkpoints
    assert first.parameter_count == second.parameter_count
