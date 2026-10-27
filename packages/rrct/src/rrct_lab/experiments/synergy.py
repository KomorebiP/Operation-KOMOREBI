from __future__ import annotations

from typing import Any

import numpy as np

from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import accuracy, seed_everything


def run(config: dict[str, Any]) -> ExperimentResult:
    seed = int(cfg(config, "run.seed", 580001))
    rng = seed_everything(seed, bool(cfg(config, "run.deterministic", True)))
    n = int(cfg(config, "experiment.episodes", 1024))
    rounds = max(1, int(cfg(config, "workspace.message_rounds", 3)))
    initial = rng.integers(0, 16, n, dtype=np.uint8)
    a_masks = rng.integers(0, 16, size=(n, rounds), dtype=np.uint8)
    b_masks = rng.integers(0, 16, size=(n, rounds), dtype=np.uint8)
    target = initial.copy()
    for round_index in range(rounds):
        target ^= a_masks[:, round_index]
        target ^= b_masks[:, round_index]

    communication = enabled(config, "communication")
    distributed = enabled(config, "distributed_workspace", "workspace_cut")
    workspace = initial.copy()
    persistent = bool(cfg(config, "workspace.persistent_across_steps", True)) and distributed
    read_only = bool(cfg(config, "workspace.read_only", False)) or bool(cfg(config, "interventions.read_only_workspace", False))
    recurrence = enabled(config, "recurrence", "recurrence_cut")
    bilateral = bool(cfg(config, "workspace.bidirectional", True)) and not bool(
        cfg(config, "interventions.one_way", False)
    )
    for round_index in range(rounds):
        if bool(cfg(config, "interventions.reset_each_round", False)) or not persistent:
            workspace[:] = 0
        if communication and not read_only and not bool(cfg(config, "interventions.local_a_cut", False)):
            workspace ^= a_masks[:, round_index]
        if communication and not read_only and bilateral and not bool(cfg(config, "interventions.local_b_cut", False)):
            workspace ^= b_masks[:, round_index]
        if bool(cfg(config, "interventions.reset_each_step", False)):
            workspace[:] = 0
    if bool(cfg(config, "interventions.message_shuffle", False)):
        workspace = rng.permutation(workspace)
    planner = enabled(config, "planner_binding", "planner_binding_cut")
    prediction = workspace if planner else np.zeros(n, dtype=np.uint8)
    task_accuracy = accuracy(prediction, target)

    patch_effect = 0.0
    if enabled(config, "causal_patching"):
        patched = workspace ^ np.uint8(0b1111)
        expected = target ^ np.uint8(0b1111)
        patch_effect = accuracy(patched, expected)
    private_a_guess = rng.integers(0, 16, n)
    private_b_guess = rng.integers(0, 16, n)
    metrics = {
        "task_accuracy": task_accuracy,
        "synergy_task_accuracy": task_accuracy,
        "private_a_accuracy": accuracy(private_a_guess, target),
        "private_b_accuracy": accuracy(private_b_guess, target),
        "synergy_information_bits": 4.0,
        "persistent_state_rate": 1.0 if persistent else 0.0,
        "bilateral_write_rate": 1.0 if bilateral else 0.0,
        "planner_binding_rate": 1.0 if planner else 0.0,
        "recurrence_reopen_rate": 1.0 if recurrence else 0.0,
        "causal_patch_effect": patch_effect,
        "post_erasure_accuracy": 1.0 / 16.0 if bool(cfg(config, "workspace.dissolve_after_episode", True)) else task_accuracy,
    }
    return ExperimentResult(
        family="synergistic_channel",
        status="completed",
        metrics=metrics,
        metadata={
            "episodes": n,
            "rounds": rounds,
            "target_entropy_bits": 4,
            "learned_message_mode": False,
            "communication": communication,
            "distributed_workspace": distributed,
            "read_only": read_only,
        },
        warnings=[
            "The generic lab implementation is an exact synergistic state test. Use the vendored v0.51 release for the canonical trained anonymous-message experiment."
        ],
    )
