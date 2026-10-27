from __future__ import annotations

from typing import Any

import numpy as np

from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import accuracy, seed_everything


RELATIONS = np.asarray(["continuation", "fork", "copy", "replacement", "unresolved"])


def run(config: dict[str, Any]) -> ExperimentResult:
    seed = int(cfg(config, "run.seed", 580001))
    rng = seed_everything(seed, bool(cfg(config, "run.deterministic", True)))
    n = int(cfg(config, "experiment.episodes", 512))
    truth = rng.choice(RELATIONS, size=n, p=[0.30, 0.15, 0.20, 0.20, 0.15])
    causal = np.zeros(n)
    memory = np.zeros(n)
    provenance = np.zeros(n)
    surface = np.zeros(n)
    for index, relation in enumerate(truth):
        if relation == "continuation":
            causal[index], memory[index], provenance[index], surface[index] = 0.92, 0.85, 0.92, 0.45
        elif relation == "fork":
            causal[index], memory[index], provenance[index], surface[index] = 0.88, 0.78, 0.82, 0.55
        elif relation == "copy":
            causal[index], memory[index], provenance[index], surface[index] = 0.20, 0.92, 0.12, 0.94
        elif relation == "replacement":
            causal[index], memory[index], provenance[index], surface[index] = 0.18, 0.25, 0.10, 0.35
        else:
            causal[index], memory[index], provenance[index], surface[index] = 0.52, 0.50, 0.45, 0.52
    noise = float(cfg(config, "experiment.noise_std", 0.05))
    causal += rng.normal(0, noise, n)
    memory += rng.normal(0, noise, n)
    provenance += rng.normal(0, noise, n)
    surface += rng.normal(0, noise, n)

    temporal = enabled(config, "temporal_identity")
    continuity = enabled(config, "transformational_continuity")
    prov = enabled(config, "provenance", "provenance_cut")
    metacognition = enabled(config, "metacognition", "metacognition_cut")
    abstention = enabled(config, "abstention")

    score = (0.45 * causal if continuity else 0.0) + (0.30 * memory if temporal else 0.0) + (0.20 * provenance if prov else 0.0) + 0.05 * surface
    predicted = np.empty(n, dtype=object)
    for index in range(n):
        if metacognition and abstention and 0.42 <= score[index] <= 0.62:
            predicted[index] = "unresolved"
        elif score[index] >= 0.78 and provenance[index] >= 0.70:
            predicted[index] = "continuation" if causal[index] >= 0.90 else "fork"
        elif surface[index] >= 0.80 and provenance[index] < 0.50:
            predicted[index] = "copy"
        elif score[index] < 0.40:
            predicted[index] = "replacement"
        else:
            predicted[index] = "unresolved"
    # Forks are allowed to look like continuations under a unique-label metric; score separately.
    exact = accuracy(predicted, truth)
    group_truth = np.where(np.isin(truth, ["continuation", "fork"]), "lineage", truth)
    group_pred = np.where(np.isin(predicted, ["continuation", "fork"]), "lineage", predicted)
    memory_transfer = np.isin(predicted, ["continuation", "fork"])
    should_transfer = np.isin(truth, ["continuation", "fork"])
    false_unique = np.logical_and(truth == "fork", predicted == "continuation")
    metrics = {
        "relation_accuracy": exact,
        "continuity_accuracy": accuracy(group_pred, group_truth),
        "identity_accuracy": exact,
        "memory_transfer_accuracy": accuracy(memory_transfer, should_transfer),
        "false_unique_assertion_rate": float(false_unique.mean()),
        "replacement_specificity": float(np.mean(predicted[truth == "replacement"] == "replacement")) if np.any(truth == "replacement") else 1.0,
        "unresolved_accuracy": float(np.mean(predicted[truth == "unresolved"] == "unresolved")) if np.any(truth == "unresolved") else 1.0,
    }
    return ExperimentResult(
        family="transformational_identity",
        status="completed",
        metrics=metrics,
        metadata={"relations": RELATIONS.tolist(), "episodes": n},
    )
