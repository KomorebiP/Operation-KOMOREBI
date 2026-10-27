from __future__ import annotations

import math
from typing import Any

from .tasks import QUERY_TYPES


def _gate(name: str, value: Any, passed: bool, threshold: Any = None) -> dict[str, Any]:
    return {"name": name, "value": value, "threshold": threshold, "passed": bool(passed)}


def _valid_probability(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
        and 0.0 <= float(value) <= 1.0
    )


def adjudicate(
    config: dict[str, Any],
    engineering: dict[str, Any],
    evaluation: dict[str, Any],
) -> dict[str, Any]:
    engineering_gates = [
        _gate(key, engineering.get(key), engineering.get(key) is True, True)
        for key in (
            "local_model_loaded",
            "single_token_targets",
            "answer_token_boundary",
            "backbone_frozen",
            "optimizer_excludes_backbone",
            "finite_loss",
            "nonzero_finite_gradient",
            "nonzero_finite_parameter_delta",
            "nonzero_finite_state",
            "artifacts_complete",
        )
    ]
    engineering_pass = all(item["passed"] for item in engineering_gates)

    scientific_enabled = bool(config["gates"]["scientific_enabled"])
    scientific_gates: list[dict[str, Any]] = []
    if scientific_enabled:
        iid = evaluation.get("iid", {})
        ood = evaluation.get("ood", {})
        expected_modes = {"recurrent", "zero", "shuffle", "no_feedback"}
        structure_pass = (
            isinstance(iid, dict)
            and expected_modes.issubset(iid)
            and isinstance(ood, dict)
            and expected_modes.issubset(ood)
            and all(isinstance(iid.get(mode), dict) for mode in expected_modes)
            and all(isinstance(ood.get(mode), dict) for mode in expected_modes)
        )
        scientific_gates.append(
            _gate("evaluation_modes_complete", structure_pass, structure_pass, True)
        )
        query_keys: set[str] = set()
        baseline_keys: set[str] = set()
        query_structure_pass = False
        probability_values: list[Any] = []
        if structure_pass:
            recurrent = iid["recurrent"]
            query_accuracy = recurrent.get("accuracy_by_query", {})
            majority_baseline = recurrent.get("majority_baseline_by_query", {})
            if isinstance(query_accuracy, dict) and isinstance(majority_baseline, dict):
                query_keys = set(query_accuracy)
                baseline_keys = set(majority_baseline)
                query_structure_pass = query_keys == set(QUERY_TYPES) and baseline_keys == set(
                    QUERY_TYPES
                )
            probability_values.extend(
                iid[mode].get("accuracy") for mode in expected_modes
            )
            probability_values.extend(
                ood[mode].get("accuracy") for mode in expected_modes
            )
            if query_structure_pass:
                probability_values.extend(query_accuracy.values())
                probability_values.extend(majority_baseline.values())
        metrics_valid = (
            structure_pass
            and query_structure_pass
            and bool(probability_values)
            and all(_valid_probability(value) for value in probability_values)
        )
        scientific_gates.extend(
            [
                _gate(
                    "query_families_complete",
                    sorted(query_keys),
                    query_structure_pass,
                    sorted(QUERY_TYPES),
                ),
                _gate(
                    "probability_metrics_valid",
                    metrics_valid,
                    metrics_valid,
                    True,
                ),
                _gate("engineering_prerequisite", engineering_pass, engineering_pass, True),
                _gate(
                    "canonical_scientific_profile",
                    engineering.get("canonical_scientific_profile"),
                    engineering.get("canonical_scientific_profile") is True,
                    True,
                ),
            ]
        )
        if metrics_valid:
            recurrent = iid["recurrent"]
            zero = iid["zero"]
            shuffled = iid["shuffle"]
            no_feedback = iid["no_feedback"]
            threshold = config["gates"]
            scientific_gates.extend(
                [
                    _gate(
                        "recurrent_iid_accuracy",
                        recurrent["accuracy"],
                        recurrent["accuracy"] >= threshold["recurrent_iid_min"],
                        threshold["recurrent_iid_min"],
                    ),
                    _gate(
                        "recurrent_minus_zero",
                        recurrent["accuracy"] - zero["accuracy"],
                        recurrent["accuracy"] - zero["accuracy"]
                        >= threshold["zero_gap_min"],
                        threshold["zero_gap_min"],
                    ),
                    _gate(
                        "recurrent_minus_shuffle",
                        recurrent["accuracy"] - shuffled["accuracy"],
                        recurrent["accuracy"] - shuffled["accuracy"]
                        >= threshold["shuffle_gap_min"],
                        threshold["shuffle_gap_min"],
                    ),
                    _gate(
                        "recurrent_minus_no_feedback",
                        recurrent["accuracy"] - no_feedback["accuracy"],
                        recurrent["accuracy"] - no_feedback["accuracy"]
                        >= threshold["feedback_gap_min"],
                        threshold["feedback_gap_min"],
                    ),
                    _gate(
                        "recurrent_ood_accuracy",
                        ood["recurrent"]["accuracy"],
                        ood["recurrent"]["accuracy"] >= threshold["ood_min"],
                        threshold["ood_min"],
                    ),
                ]
            )
            for query_type in QUERY_TYPES:
                accuracy = recurrent["accuracy_by_query"][query_type]
                majority = recurrent["majority_baseline_by_query"][query_type]
                scientific_gates.extend(
                    [
                        _gate(
                            f"recurrent_{query_type}_accuracy",
                            accuracy,
                            accuracy >= threshold["per_query_min"],
                            threshold["per_query_min"],
                        ),
                        _gate(
                            f"recurrent_{query_type}_above_empirical_majority",
                            accuracy - majority,
                            accuracy > majority,
                            0.0,
                        ),
                    ]
                )
    scientific_pass = (
        engineering_pass
        and scientific_enabled
        and bool(scientific_gates)
        and all(item["passed"] for item in scientific_gates)
    )
    return {
        "schema": "komorebi.neuralese.g1.gates.v1",
        "engineering": {"passed": engineering_pass, "gates": engineering_gates},
        "scientific": {
            "evaluated": scientific_enabled,
            "passed": scientific_pass,
            "gates": scientific_gates,
        },
        "claim": (
            "G1_SINGLE_SEED_PILOT_PASS"
            if scientific_pass
            else "G1_ENGINEERING_PASS"
            if engineering_pass
            else "G1_NOT_ESTABLISHED"
        ),
        "replication_established": False,
    }
