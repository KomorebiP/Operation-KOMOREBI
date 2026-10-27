"""Falsification-first adjudication of Micro OSL behavioral results.

The statuses in this module describe preregistered behavioral gates only.  A
PASS is not automatically promoted to a claim about latent symbols, causal
mediation, or independently discovered operators.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping, Sequence

from .utils import ensure_dir, load_json, save_json


DEFAULT_BEHAVIORAL_THRESHOLDS: dict[str, Any] = {
    "required_splits": ["lexical", "heldout_pair", "heldout_triple", "renaming"],
    "minimum_split_accuracy": 0.55,
    "minimum_margin_over_control": 0.02,
    "balance": {
        "required": True,
        "splits": ["lexical", "heldout_pair", "heldout_triple", "renaming"],
        "minimum_world_macro_accuracy": 0.55,
        "minimum_query_macro_accuracy": 0.55,
        "minimum_world_accuracy": 0.50,
        "minimum_query_accuracy": 0.40,
        "minimum_margin_over_control": 0.0,
    },
    "renaming": {
        "required": True,
        "minimum_pair_completeness": 1.0,
        "minimum_prediction_consistency": 0.80,
        "minimum_pair_joint_correctness": 0.55,
        "maximum_robustness_gap": 0.10,
        "require_gold_consistency": True,
    },
    "learned_binding_h2": {
        "required": True,
        "minimum_triplet_completeness": 1.0,
        "minimum_correct_minus_scrambled_accuracy": 0.10,
        "minimum_correct_vs_scrambled_prediction_change": 0.25,
        "minimum_correct_only_success_rate": 0.10,
        "require_triplet_gold_consistency": True,
    },
    "counterfactual": {
        "required": True,
        "minimum_affected_joint_accuracy": 0.50,
        "minimum_unaffected_joint_accuracy": 0.50,
        "minimum_change_sensitivity": 0.75,
        "minimum_invariance_specificity": 0.75,
        "minimum_pair_level_completeness": 0.50,
        "minimum_pair_level_specificity": 0.75,
    },
}


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any] | None) -> dict[str, Any]:
    result = deepcopy(dict(base))
    for key, value in dict(override or {}).items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _normalize_threshold_overrides(
    thresholds: Mapping[str, Any] | None,
) -> Mapping[str, Any] | None:
    if thresholds is None:
        return None
    normalized = deepcopy(dict(thresholds))
    balance = normalized.get("balance")
    if isinstance(balance, Mapping):
        balance = dict(balance)
        aliases = {
            "minimum_world_balanced_accuracy": "minimum_world_macro_accuracy",
            "minimum_query_balanced_accuracy": "minimum_query_macro_accuracy",
            "minimum_min_cell_accuracy": "minimum_query_accuracy",
        }
        for old, new in aliases.items():
            if old in balance and new not in balance:
                balance[new] = balance[old]
        normalized["balance"] = balance
    return normalized


def _threshold_for(value: Any, key: str) -> float:
    if isinstance(value, Mapping):
        selected = value.get(key, value.get("default", 0.0))
    else:
        selected = value
    return float(selected)


def _behavior(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(payload.get("behavior"), Mapping):
        return payload["behavior"]
    if isinstance(payload.get("by_split"), Mapping):
        return payload["by_split"]
    return payload


def _controls(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    models = payload.get("models", payload)
    if not isinstance(models, Mapping):
        return {}
    return {
        str(name): value
        for name, value in models.items()
        if isinstance(value, Mapping)
    }


def _nested_float(payload: Mapping[str, Any], path: Sequence[str]) -> float | None:
    current: Any = payload
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            return None
        current = current[key]
    if isinstance(current, bool):
        return None
    try:
        return float(current)
    except (TypeError, ValueError):
        return None


def _strongest_control(
    controls: Mapping[str, Mapping[str, Any]], path: Sequence[str]
) -> tuple[str | None, float | None]:
    candidates: list[tuple[str, float]] = []
    for name, payload in controls.items():
        value = _nested_float(_behavior(payload), path)
        if value is not None:
            candidates.append((name, value))
    if not candidates:
        return None, None
    return sorted(candidates, key=lambda item: (-item[1], item[0]))[0]


def _aggregate_status(statuses: Sequence[str]) -> str:
    if any(status == "FAIL" for status in statuses):
        return "FAIL"
    if not statuses or any(status == "INCOMPLETE" for status in statuses):
        return "INCOMPLETE"
    return "PASS"


def _minimum_check(value: float | None, threshold: float) -> dict[str, Any]:
    status = "INCOMPLETE" if value is None else ("PASS" if value >= threshold else "FAIL")
    return {
        "value": value,
        "criterion": ">=",
        "threshold": threshold,
        "passed": bool(value is not None and value >= threshold),
        "status": status,
    }


def _maximum_check(value: float | None, threshold: float) -> dict[str, Any]:
    status = "INCOMPLETE" if value is None else ("PASS" if value <= threshold else "FAIL")
    return {
        "value": value,
        "criterion": "<=",
        "threshold": threshold,
        "passed": bool(value is not None and value <= threshold),
        "status": status,
    }


def _split_advantage_gate(
    answer_behavior: Mapping[str, Any],
    controls: Mapping[str, Mapping[str, Any]],
    settings: Mapping[str, Any],
) -> dict[str, Any]:
    details: dict[str, Any] = {}
    statuses: list[str] = []
    for split in [str(value) for value in settings.get("required_splits", [])]:
        answer = _nested_float(answer_behavior, ("splits", split, "accuracy"))
        control_name, control = _strongest_control(controls, ("splits", split, "accuracy"))
        minimum = _threshold_for(settings.get("minimum_split_accuracy", 0.0), split)
        margin_minimum = _threshold_for(settings.get("minimum_margin_over_control", 0.0), split)
        margin = answer - control if answer is not None and control is not None else None
        if answer is None or control is None:
            status = "INCOMPLETE"
        else:
            status = "PASS" if answer >= minimum and margin >= margin_minimum else "FAIL"
        statuses.append(status)
        details[split] = {
            "status": status,
            "answer_only_accuracy": answer,
            "minimum_accuracy": minimum,
            "strongest_control": {"name": control_name, "accuracy": control},
            "margin_over_strongest_control": margin,
            "minimum_margin": margin_minimum,
        }
    return {
        "status": _aggregate_status(statuses),
        "policy": "Each endpoint is compared with the highest eligible frozen-control score on that endpoint.",
        "splits": details,
    }


def _balanced_gate(
    answer_behavior: Mapping[str, Any],
    controls: Mapping[str, Mapping[str, Any]],
    settings: Mapping[str, Any],
) -> dict[str, Any]:
    if not bool(settings.get("required", True)):
        return {"status": "PASS", "required": False, "reason": "disabled by configuration"}
    endpoint_thresholds = {
        "world_macro_accuracy": float(
            settings.get(
                "minimum_world_macro_accuracy",
                settings.get("minimum_world_balanced_accuracy", 0.0),
            )
        ),
        "query_macro_accuracy": float(
            settings.get(
                "minimum_query_macro_accuracy",
                settings.get("minimum_query_balanced_accuracy", 0.0),
            )
        ),
        "minimum_world_accuracy": float(settings.get("minimum_world_accuracy", 0.0)),
        "minimum_query_accuracy": float(
            settings.get("minimum_query_accuracy", settings.get("minimum_min_cell_accuracy", 0.0))
        ),
    }
    minimum_margin = float(settings.get("minimum_margin_over_control", 0.0))
    split_details: dict[str, Any] = {}
    split_statuses: list[str] = []
    for split in [str(value) for value in settings.get("splits", [])]:
        checks: dict[str, Any] = {}
        endpoint_statuses: list[str] = []
        for endpoint, minimum in endpoint_thresholds.items():
            path = ("balanced", "splits", split, endpoint)
            answer = _nested_float(answer_behavior, path)
            control_name, control = _strongest_control(controls, path)
            margin = answer - control if answer is not None and control is not None else None
            if answer is None or control is None:
                status = "INCOMPLETE"
            else:
                status = "PASS" if answer >= minimum and margin >= minimum_margin else "FAIL"
            endpoint_statuses.append(status)
            checks[endpoint] = {
                "status": status,
                "answer_only": answer,
                "minimum": minimum,
                "strongest_control": {"name": control_name, "value": control},
                "margin_over_strongest_control": margin,
                "minimum_margin": minimum_margin,
            }
        split_status = _aggregate_status(endpoint_statuses)
        split_statuses.append(split_status)
        split_details[split] = {"status": split_status, "endpoints": checks}
    return {
        "status": _aggregate_status(split_statuses),
        "required": True,
        "cell_definition": "world::question_id",
        "splits": split_details,
    }


def _renaming_gate(answer_only: Mapping[str, Any], settings: Mapping[str, Any]) -> dict[str, Any]:
    if not bool(settings.get("required", True)):
        return {"status": "PASS", "required": False, "reason": "disabled by configuration"}
    behavior = _behavior(answer_only)
    metrics = answer_only.get("renaming", behavior.get("renaming", {}))
    if not isinstance(metrics, Mapping) or int(metrics.get("pair_groups", 0) or 0) < 1:
        return {
            "status": "INCOMPLETE",
            "required": True,
            "reason": "no eligible metadata.pair_id canonical/renamed pairs",
        }
    checks = {
        "pair_completeness": _minimum_check(
            _nested_float(metrics, ("pair_completeness",)),
            float(settings.get("minimum_pair_completeness", 1.0)),
        ),
        "prediction_consistency": _minimum_check(
            _nested_float(metrics, ("prediction_consistency",)),
            float(settings.get("minimum_prediction_consistency", 0.0)),
        ),
        "pair_joint_correctness": _minimum_check(
            _nested_float(metrics, ("pair_joint_correctness",)),
            float(settings.get("minimum_pair_joint_correctness", 0.0)),
        ),
        "robustness_gap": _maximum_check(
            _nested_float(metrics, ("robustness_gap",)),
            float(settings.get("maximum_robustness_gap", 1.0)),
        ),
    }
    if bool(settings.get("require_gold_consistency", True)):
        checks["gold_consistency"] = _minimum_check(
            _nested_float(metrics, ("gold_consistency",)), 1.0
        )
    status = _aggregate_status([str(check["status"]) for check in checks.values()])
    return {
        "status": status,
        "required": True,
        "pair_groups": int(metrics.get("pair_groups", 0)),
        "canonical_accuracy": _nested_float(metrics, ("canonical_accuracy",)),
        "renamed_accuracy": _nested_float(metrics, ("renamed_accuracy",)),
        "checks": checks,
    }


def adjudicate_learned_binding(
    renaming_metrics: Mapping[str, Any],
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Adjudicate H2: behavior depends on episode-local calibration mappings.

    The matched scrambled calibration is an input-level causal control.  PASS
    means correct calibration mattered under the configured behavioral
    thresholds; it does not identify a particular latent mechanism.
    """

    settings = _deep_merge(
        dict(DEFAULT_BEHAVIORAL_THRESHOLDS["learned_binding_h2"]), thresholds
    )
    if not bool(settings.get("required", True)):
        return {"status": "PASS", "required": False, "reason": "disabled by configuration"}
    declared_groups = int(renaming_metrics.get("declared_groups", 0) or 0)
    triplet_groups = int(renaming_metrics.get("triplet_groups", 0) or 0)
    if declared_groups < 1 or triplet_groups < 1:
        return {
            "status": "INCOMPLETE",
            "required": True,
            "hypothesis": "H2_learned_episode_binding",
            "reason": "no complete canonical/renamed/scrambled triplets",
            "declared_groups": declared_groups,
            "triplet_groups": triplet_groups,
        }
    checks = {
        "triplet_completeness": _minimum_check(
            _nested_float(renaming_metrics, ("triplet_completeness",)),
            float(settings.get("minimum_triplet_completeness", 1.0)),
        ),
        "correct_minus_scrambled_accuracy": _minimum_check(
            _nested_float(renaming_metrics, ("correct_minus_scrambled_accuracy",)),
            float(settings.get("minimum_correct_minus_scrambled_accuracy", 0.0)),
        ),
        "correct_vs_scrambled_prediction_change": _minimum_check(
            _nested_float(
                renaming_metrics, ("correct_vs_scrambled_prediction_change",)
            ),
            float(settings.get("minimum_correct_vs_scrambled_prediction_change", 0.0)),
        ),
        "correct_only_success_rate": _minimum_check(
            _nested_float(renaming_metrics, ("correct_only_success_rate",)),
            float(settings.get("minimum_correct_only_success_rate", 0.0)),
        ),
    }
    if bool(settings.get("require_triplet_gold_consistency", True)):
        checks["triplet_gold_consistency"] = _minimum_check(
            _nested_float(renaming_metrics, ("triplet_gold_consistency",)), 1.0
        )
    status = _aggregate_status([str(check["status"]) for check in checks.values()])
    return {
        "status": status,
        "required": True,
        "hypothesis": "H2_learned_episode_binding",
        "declared_groups": declared_groups,
        "triplet_groups": triplet_groups,
        "correct_calibration_accuracy": _nested_float(
            renaming_metrics, ("correct_calibration_accuracy",)
        ),
        "scrambled_accuracy": _nested_float(renaming_metrics, ("scrambled_accuracy",)),
        "checks": checks,
        "pass_meaning": (
            "Correct episode calibration improved matched behavior beyond the configured thresholds."
        ),
        "latent_mechanism_claim": False,
    }


def _counterfactual_gate(
    answer_only: Mapping[str, Any], settings: Mapping[str, Any]
) -> dict[str, Any]:
    if not bool(settings.get("required", True)):
        return {"status": "PASS", "required": False, "reason": "disabled by configuration"}
    metrics = answer_only.get("counterfactual", {})
    if not isinstance(metrics, Mapping) or int(metrics.get("pair_groups", 0) or 0) < 1:
        return {
            "status": "INCOMPLETE",
            "required": True,
            "reason": "no eligible counterfactual pairs",
        }
    endpoints = {
        "affected_joint_accuracy": "minimum_affected_joint_accuracy",
        "unaffected_joint_accuracy": "minimum_unaffected_joint_accuracy",
        "change_sensitivity": "minimum_change_sensitivity",
        "invariance_specificity": "minimum_invariance_specificity",
        "pair_level_completeness": "minimum_pair_level_completeness",
        "pair_level_specificity": "minimum_pair_level_specificity",
    }
    checks = {
        endpoint: _minimum_check(
            _nested_float(metrics, (endpoint,)), float(settings.get(setting_name, 0.0))
        )
        for endpoint, setting_name in endpoints.items()
    }
    return {
        "status": _aggregate_status([str(check["status"]) for check in checks.values()]),
        "required": True,
        "pair_groups": int(metrics.get("pair_groups", 0)),
        "checks": checks,
    }


def adjudicate_behavioral_gates(
    answer_only: Mapping[str, Any],
    frozen_controls: Mapping[str, Any],
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compare answer-only behavior with frozen controls under fixed gates."""

    resolved = _deep_merge(
        DEFAULT_BEHAVIORAL_THRESHOLDS, _normalize_threshold_overrides(thresholds)
    )
    answer_behavior = _behavior(answer_only)
    controls = _controls(frozen_controls)
    renaming_metrics = answer_only.get("renaming", answer_behavior.get("renaming", {}))
    if not isinstance(renaming_metrics, Mapping):
        renaming_metrics = {}
    gates = {
        "split_advantage": _split_advantage_gate(answer_behavior, controls, resolved),
        "balanced_robustness": _balanced_gate(
            answer_behavior, controls, dict(resolved.get("balance", {}))
        ),
        "paired_renaming": _renaming_gate(
            answer_only, dict(resolved.get("renaming", {}))
        ),
        "learned_binding_h2": adjudicate_learned_binding(
            renaming_metrics, dict(resolved.get("learned_binding_h2", {}))
        ),
        "counterfactual": _counterfactual_gate(
            answer_only, dict(resolved.get("counterfactual", {}))
        ),
    }
    behavioral_status = _aggregate_status([gate["status"] for gate in gates.values()])
    return {
        "schema": "osl.micro-emergence.evidence-adjudication.v1",
        "arm": "answer_only",
        "architecture": None,
        "status": behavioral_status,
        "behavioral_status": behavioral_status,
        "thresholds": resolved,
        "frozen_controls": sorted(controls),
        "gates": gates,
        "claim_boundary": {
            "pass_meaning": "The answer-only arm passed the configured behavioral gates for this run.",
            "automatic_emergence_claim": False,
            "quotient_scope": "benchmark_only",
            "quotient_note": "Finite-world quotient results describe benchmark structure unless separately fitted to learned representations.",
            "not_adjudicated": [
                "causal mediation by latent representations",
                "independently admitted or newly discovered operators",
                "general symbolic competence outside the registered finite worlds",
            ],
        },
    }


def render_evidence_adjudication_markdown(payload: Mapping[str, Any]) -> str:
    """Render a concise human-readable companion to the JSON adjudication."""

    gates = payload.get("gates", {}) if isinstance(payload.get("gates"), Mapping) else {}
    lines = [
        "# Micro OSL Evidence Adjudication",
        "",
        f"Overall behavioral status: **{payload.get('behavioral_status', 'INCOMPLETE')}**",
        "",
        "A PASS means only that the answer-only arm met the configured behavioral thresholds for this run. It is not, by itself, an emergence or causal-representation claim.",
        "",
        "| Gate | Status |",
        "|---|---:|",
    ]
    for name, gate in gates.items():
        status = gate.get("status", "INCOMPLETE") if isinstance(gate, Mapping) else "INCOMPLETE"
        lines.append(f"| `{name}` | **{status}** |")

    split_gate = gates.get("split_advantage", {}) if isinstance(gates, Mapping) else {}
    split_rows = split_gate.get("splits", {}) if isinstance(split_gate, Mapping) else {}
    if isinstance(split_rows, Mapping) and split_rows:
        lines.extend(
            [
                "",
                "## Answer-only versus strongest frozen control",
                "",
                "| Split | Answer-only | Control | Margin | Status |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for split, row in split_rows.items():
            answer = row.get("answer_only_accuracy")
            control = row.get("strongest_control", {})
            control_value = control.get("accuracy") if isinstance(control, Mapping) else None
            margin = row.get("margin_over_strongest_control")
            answer_text = "NA" if answer is None else f"{float(answer):.4f}"
            control_text = "NA" if control_value is None else f"{float(control_value):.4f}"
            margin_text = "NA" if margin is None else f"{float(margin):+.4f}"
            lines.append(
                f"| `{split}` | {answer_text} | {control_text} | {margin_text} | **{row.get('status', 'INCOMPLETE')}** |"
            )

    lines.extend(
        [
            "",
            "## Scope boundary",
            "",
            "Quotient analysis is labeled **benchmark-only** unless it is separately fitted to learned representations. This adjudication does not test latent causal mediation, independently admitted operators, or competence outside the registered finite worlds.",
            "",
        ]
    )
    return "\n".join(lines)


def _preferred_file(paths: Sequence[Path], root: Path) -> Path | None:
    if not paths:
        return None
    return sorted(paths, key=lambda path: (len(path.relative_to(root).parts), str(path)))[0]


def _answer_only_evaluation(root: Path) -> tuple[Path | None, list[str]]:
    warnings: list[str] = []
    candidates: list[Path] = []
    for evaluation in root.rglob("evaluation_results.json"):
        if evaluation.parent.name.endswith("__answer_only"):
            candidates.append(evaluation)
            continue
        training_summary = evaluation.parent / "training_summary.json"
        if training_summary.is_file():
            try:
                if str(load_json(training_summary).get("arm")) == "answer_only":
                    candidates.append(evaluation)
            except Exception:
                continue
    selected = _preferred_file(candidates, root)
    if len(candidates) > 1:
        warnings.append(
            f"found {len(candidates)} answer-only evaluations; selected {selected.relative_to(root).as_posix() if selected else 'none'}"
        )
    return selected, warnings


def _configured_thresholds(root: Path) -> Mapping[str, Any] | None:
    config_path = root / "resolved_config.json"
    if not config_path.is_file():
        return None
    try:
        config = load_json(config_path)
    except Exception:
        return None
    candidates = [
        config.get("adjudication"),
        config.get("evidence_adjudication"),
        config.get("evaluation", {}).get("adjudication")
        if isinstance(config.get("evaluation"), Mapping)
        else None,
    ]
    return next((value for value in candidates if isinstance(value, Mapping)), None)


def build_evidence_adjudication(
    run_dir: str | Path,
    thresholds: Mapping[str, Any] | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    """Build ``EVIDENCE_ADJUDICATION.json`` and its Markdown companion.

    ``run_dir`` should contain ``baseline_results.json`` and an answer-only
    experiment directory.  Missing inputs produce an explicit INCOMPLETE
    adjudication rather than a silent omission.
    """

    root = Path(run_dir).resolve()
    output = ensure_dir(Path(output_dir).resolve() if output_dir else root)
    answer_path, warnings = _answer_only_evaluation(root)
    baseline_path = _preferred_file(list(root.rglob("baseline_results.json")), root)
    answer_payload = load_json(answer_path) if answer_path is not None else {}
    baseline_payload = load_json(baseline_path) if baseline_path is not None else {}
    configured = thresholds if thresholds is not None else _configured_thresholds(root)
    payload = adjudicate_behavioral_gates(answer_payload, baseline_payload, configured)
    if answer_path is not None and answer_path.parent.name.endswith("__answer_only"):
        payload["architecture"] = answer_path.parent.name[: -len("__answer_only")]
    payload["sources"] = {
        "answer_only_evaluation": answer_path.relative_to(root).as_posix() if answer_path else None,
        "frozen_controls": baseline_path.relative_to(root).as_posix() if baseline_path else None,
    }
    if answer_path is None:
        warnings.append("answer-only evaluation_results.json not found")
    if baseline_path is None:
        warnings.append("baseline_results.json not found")
    payload["warnings"] = warnings

    json_path = output / "EVIDENCE_ADJUDICATION.json"
    markdown_path = output / "EVIDENCE_ADJUDICATION.md"
    save_json(json_path, payload)
    markdown_path.write_text(
        render_evidence_adjudication_markdown(payload), encoding="utf-8", newline="\n"
    )
    return {
        "status": payload["behavioral_status"],
        "json": str(json_path),
        "markdown": str(markdown_path),
        "adjudication": payload,
    }


__all__ = [
    "DEFAULT_BEHAVIORAL_THRESHOLDS",
    "adjudicate_behavioral_gates",
    "adjudicate_learned_binding",
    "build_evidence_adjudication",
    "render_evidence_adjudication_markdown",
]
