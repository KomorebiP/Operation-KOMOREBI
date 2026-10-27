from __future__ import annotations

from typing import Any

import numpy as np

from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import accuracy, seed_everything


ROUTES = ["local", "flat", "pair_01_23", "pair_02_13", "pair_03_12", "full_overlap"]
COSTS = np.asarray([0.0, 1.0, 2.5, 2.5, 2.5, 4.0])
TASKS = ROUTES.copy()

# Rows are task families; columns are route losses. Each row has one minimal sufficient route,
# while overbuilt routes can sometimes remain accurate at higher cost.
LOSS = np.asarray(
    [
        [0.00, 0.00, 0.00, 0.00, 0.00, 0.00],
        [0.95, 0.00, 0.00, 0.00, 0.00, 0.00],
        [0.95, 0.55, 0.00, 0.72, 0.72, 0.00],
        [0.95, 0.55, 0.72, 0.00, 0.72, 0.00],
        [0.95, 0.55, 0.72, 0.72, 0.00, 0.00],
        [0.95, 0.75, 0.75, 0.75, 0.75, 0.00],
    ]
)


def run(config: dict[str, Any]) -> ExperimentResult:
    seed = int(cfg(config, "run.seed", 580001))
    rng = seed_everything(seed, bool(cfg(config, "run.deterministic", True)))
    n = int(cfg(config, "experiment.episodes", 6000))
    lam = float(cfg(config, "workspace.formation_cost", 0.12))
    temperature = max(1e-6, float(cfg(config, "workspace.temperature", 0.05)))
    workspace_active = enabled(config, "workspace", "workspace_cut")
    dynamic = enabled(config, "dynamic_formation")
    cost_regularized = enabled(config, "cost_regularization")
    hierarchical = enabled(config, "hierarchical_workspace")
    tasks = rng.integers(0, len(TASKS), n)
    route_predictions = np.zeros(n, dtype=int)
    task_success = np.zeros(n, dtype=bool)
    for index, task in enumerate(tasks):
        if not workspace_active:
            route = 0
        elif dynamic:
            objective = LOSS[task] + (lam * COSTS if cost_regularized else 0.0)
            if not hierarchical:
                objective = objective.copy()
                objective[2:] = 1e6
            logits = -objective / temperature
            probabilities = np.exp(logits - logits.max())
            probabilities /= probabilities.sum()
            route = int(rng.choice(len(ROUTES), p=probabilities))
        else:
            route = 5
        route_predictions[index] = route
        task_success[index] = LOSS[task, route] <= 0.05
    minimal = np.asarray([0, 1, 2, 3, 4, 5])[tasks]
    metrics = {
        "task_accuracy": float(task_success.mean()),
        "route_accuracy": accuracy(route_predictions, minimal),
        "formation_accuracy": accuracy(route_predictions, minimal),
        "mean_route_cost": float(COSTS[route_predictions].mean()),
        "mean_minimal_cost": float(COSTS[minimal].mean()),
        "mean_excess_cost": float((COSTS[route_predictions] - COSTS[minimal]).mean()),
        "workspace_dissolution_accuracy": float(np.mean(route_predictions[tasks == 0] == 0)) if np.any(tasks == 0) else 1.0,
        "graph_switch_accuracy": accuracy(route_predictions, minimal),
        "causal_patch_effect": float(np.mean(LOSS[tasks, route_predictions] != LOSS[tasks, rng.permutation(route_predictions)])),
    }
    return ExperimentResult(
        family="formation_routing",
        status="completed",
        metrics=metrics,
        metadata={
            "routes": ROUTES,
            "task_families": TASKS,
            "formation_cost": lam,
            "dynamic_formation": dynamic,
            "workspace_active": workspace_active,
            "hierarchical_workspace": hierarchical,
            "cost_regularization": cost_regularized,
        },
    )
