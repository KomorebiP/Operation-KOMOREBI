from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np


def _first(metrics: Mapping[str, Any], names: tuple[str, ...], default: float = 0.0) -> float:
    for name in names:
        value = metrics.get(name)
        if isinstance(value, (int, float, np.generic)):
            return float(np.clip(value, 0.0, 1.0))
    return default


def functional_profile(metrics: Mapping[str, Any]) -> dict[str, Any]:
    profile = {
        "global_access": _first(
            metrics,
            (
                "jspace_ablation_drop",
                "workspace_decodability",
                "jspace_task_score",
                "flexible_task_accuracy",
                "task_accuracy",
            ),
        ),
        "self_model": _first(
            metrics,
            ("self_world_accuracy", "continuity_accuracy", "identity_accuracy"),
        ),
        "autobiographical_provenance": _first(
            metrics,
            ("provenance_accuracy", "ownership_accuracy"),
        ),
        "planner_coupling": _first(
            metrics,
            (
                "planner_cut_drop",
                "plan_accuracy",
                "planner_binding_rate",
                "planner_bound_accuracy",
                "task_accuracy",
            ),
        ),
        "feedback_recurrence": _first(
            metrics,
            ("recurrence_reopen_rate", "feedback_reopen_rate"),
        ),
        "metacognition": _first(
            metrics,
            ("metacognitive_accuracy", "calibration_accuracy", "adaptive_probe_accuracy"),
        ),
        "transformational_continuity": _first(
            metrics,
            ("continuity_accuracy", "relation_accuracy"),
        ),
        "distributed_integration": _first(
            metrics,
            (
                "broadcast_ablation_drop",
                "structural_closure",
                "shared_workspace_closure",
                "synergy_task_accuracy",
            ),
        ),
        "endogenous_formation": _first(
            metrics,
            ("route_accuracy", "formation_accuracy", "emergence_rate"),
        ),
        "fuzzy_structure": _first(
            metrics,
            ("causal_membership_calibration", "fuzzy_task_accuracy"),
        ),
    }
    values = np.asarray(list(profile.values()), dtype=float)
    geometric = float(np.exp(np.mean(np.log(np.clip(values, 1e-9, 1.0)))))
    return {
        "axes": profile,
        "functional_closure_composite": geometric,
        "interpretation": (
            "This is a configurable functional-indicator vector and engineering composite. "
            "It is not a probability of consciousness, subjective experience, sentience, or moral status."
        ),
    }
