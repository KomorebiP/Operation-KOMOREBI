from __future__ import annotations

from typing import Any

import numpy as np

from rrct_lab.experiments.common import cfg, enabled
from rrct_lab.results import ExperimentResult
from rrct_lab.utils import accuracy, seed_everything


def run(config: dict[str, Any]) -> ExperimentResult:
    seed = int(cfg(config, "run.seed", 580001))
    rng = seed_everything(seed, bool(cfg(config, "run.deterministic", True)))
    n = int(cfg(config, "experiment.episodes", 512))
    classes = int(cfg(config, "experiment.action_dim", 4))
    self_state = rng.integers(0, classes, size=n)
    world_state = rng.integers(0, classes, size=n)
    task_target = (self_state + world_state) % classes
    workspace = enabled(config, "workspace", "workspace_cut")
    self_model = enabled(config, "self_model", "self_model_cut")
    boundary = enabled(config, "causal_boundary", "causal_boundary_cut")
    memory = enabled(config, "autobiographical_memory", "memory_cut")
    provenance = enabled(config, "provenance", "provenance_cut")
    planner = enabled(config, "planner_binding", "planner_binding_cut")
    recurrence = enabled(config, "recurrence", "recurrence_cut") and not bool(
        cfg(config, "interventions.feedback_cut", False)
    )
    metacognition = enabled(config, "metacognition", "metacognition_cut")
    temporal = enabled(config, "temporal_identity")
    transform = enabled(config, "transformational_continuity")

    if workspace and planner:
        task_prediction = task_target.copy()
    elif planner:
        task_prediction = world_state.copy()
    else:
        task_prediction = np.zeros(n, dtype=int)

    if boundary and self_model:
        self_world_prediction = np.ones(n, dtype=int)
        flip = rng.random(n) < float(cfg(config, "experiment.noise_std", 0.05))
        self_world_prediction[flip] = 0
    else:
        self_world_prediction = rng.integers(0, 2, size=n)
    self_world_target = np.ones(n, dtype=int)

    provenance_type = rng.choice(
        np.asarray([0, 1, 2, 3]),
        size=n,
        p=np.asarray([0.40, 0.25, 0.20, 0.15]),
    )
    should_write = provenance_type <= 1
    if memory and provenance and self_model:
        write_prediction = should_write.copy()
    elif memory and self_model:
        write_prediction = provenance_type != 3
    else:
        write_prediction = rng.random(n) < 0.5
    false_write = np.logical_and(write_prediction, np.logical_not(should_write))
    ownership_accuracy = float(np.mean(write_prediction == should_write))

    surprise = rng.random(n) < float(cfg(config, "experiment.surprise_probability", 0.20))
    reopen = surprise & recurrence & metacognition
    expected_reopen = surprise

    transformed = rng.random(n) < float(cfg(config, "experiment.transform_probability", 0.35))
    if temporal and transform and memory:
        continuity_prediction = np.ones(n, dtype=int)
    elif temporal:
        continuity_prediction = np.logical_not(transformed).astype(int)
    else:
        continuity_prediction = rng.integers(0, 2, size=n)
    continuity_target = np.ones(n, dtype=int)

    task_accuracy = accuracy(task_prediction, task_target)
    metrics = {
        "task_accuracy": task_accuracy,
        "self_world_accuracy": accuracy(self_world_prediction, self_world_target),
        "ownership_accuracy": ownership_accuracy,
        "provenance_accuracy": ownership_accuracy,
        "false_autobiographical_write_rate": float(false_write.mean()),
        "planner_binding_rate": 1.0 if planner else 0.0,
        "recurrence_reopen_rate": (
            float(np.mean(reopen[surprise])) if np.any(surprise) else 1.0
        ),
        "metacognitive_accuracy": (
            float(np.mean(reopen == expected_reopen)) if metacognition else 0.0
        ),
        "continuity_accuracy": accuracy(continuity_prediction, continuity_target),
        "workspace_decodability": 1.0 if workspace else 1.0 / classes,
        "routine_task_accuracy": 1.0,
        "ablation_drop": 1.0 - task_accuracy if not workspace else 0.0,
    }
    rows = []
    if bool(cfg(config, "run.save_rows", True)):
        for index in range(min(n, 2000)):
            rows.append(
                {
                    "episode": index,
                    "self_state": int(self_state[index]),
                    "world_state": int(world_state[index]),
                    "target": int(task_target[index]),
                    "prediction": int(task_prediction[index]),
                    "provenance_type": int(provenance_type[index]),
                    "write": bool(write_prediction[index]),
                    "surprise": bool(surprise[index]),
                    "reopen": bool(reopen[index]),
                    "transformed": bool(transformed[index]),
                }
            )
    return ExperimentResult(
        family="single_agent_closure",
        status="completed",
        metrics=metrics,
        rows=rows,
        metadata={
            "classes": classes,
            "episodes": n,
            "interpretation_boundary": "Functional synthetic closure test; not consciousness evidence.",
        },
    )
