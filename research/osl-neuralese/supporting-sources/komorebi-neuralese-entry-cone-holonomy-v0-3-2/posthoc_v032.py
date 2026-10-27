#!/usr/bin/env python3
"""Derive the human-scale v0.3.2 summary and figures from the frozen result.

This module is post hoc. It does not load checkpoints, execute learned endpoints,
or alter the prospectively frozen v0.3.1/v0.3.2 materials.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any


AUTHOR = "Komorebi P."
VERSION = "0.3.2"
EXPECTED_RESULT_SHA256 = (
    "134135524c0b7017c4611ce385b3853fc33d8d883d1716e60f3f6aa1c9ffba5c"
)
ROOT = Path(__file__).resolve().parent
RESULT_PATH = ROOT / "results" / "V032_ENTRY_CONE_HOLONOMY_RESULTS.json"
SUMMARY_PATH = ROOT / "results" / "V032_POSTHOC_SUMMARY.json"
RELATION_CSV_PATH = ROOT / "results" / "V032_RELATION_PROFILE.csv"
RELATION_BY_CHECKPOINT_CSV_PATH = (
    ROOT / "results" / "V032_RELATION_PROFILE_BY_CHECKPOINT.csv"
)
MATCHED_CSV_PATH = ROOT / "results" / "V032_MATCHED_CLASSIFICATIONS.csv"
FIGURE_DIR = ROOT / "figures"
ANALYSIS_RECORD_PATH = ROOT / "V032_ANALYSIS_COMPLETE.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def _finite_float(value: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"non-finite JSON float: {value}")
    return parsed


def strict_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_no_duplicate_object,
        parse_float=_finite_float,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant: {value}")
        ),
    )


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def relation_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for episode in result["relations"]["episodes"]:
        for relation_object in episode["relations"]:
            relation = relation_object["primitive"]["relation"]
            for repeat in relation_object["repeats"]:
                eligible = repeat["eligible_case_audit"]
                audit = repeat["audit"]
                rows.append(
                    {
                        "author": AUTHOR,
                        "version": VERSION,
                        "checkpoint_seed": episode["checkpoint_seed"],
                        "episode_index": episode["episode_index"],
                        "episode_half": (
                            "first" if episode["episode_index"] < 4 else "second"
                        ),
                        "relation": relation,
                        "repeat_count": repeat["repeat_count"],
                        "inserted_token_budget": repeat["inserted_token_budget"],
                        "failure_case_count": eligible["failure_case_count"],
                        "reveal_case_count": eligible["reveal_case_count"],
                        "strict_error_count": audit["strict_error_count"],
                        "minimum_target_margin": eligible["minimum_target_margin"],
                        "minimum_angular_clearance": eligible[
                            "minimum_angular_clearance"
                        ],
                        "maximum_loop_angle_radians": repeat[
                            "loop_vs_baseline_maximum_positive_ray_angle"
                        ],
                    }
                )
    return rows


def aggregate_relation_rows(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["relation"],
            row["repeat_count"],
            row["inserted_token_budget"],
        )
        grouped[key].append(row)

    output: list[dict[str, Any]] = []
    for (relation, repeat_count, budget), group in sorted(grouped.items()):
        failure_strata = {
            (row["checkpoint_seed"], row["episode_half"])
            for row in group
            if row["failure_case_count"] > 0
        }
        output.append(
            {
                "author": AUTHOR,
                "version": VERSION,
                "relation": relation,
                "repeat_count": repeat_count,
                "inserted_token_budget": budget,
                "episode_count": len(group),
                "episodes_with_failure": sum(
                    row["failure_case_count"] > 0 for row in group
                ),
                "checkpoint_half_strata_with_failure": len(failure_strata),
                "failure_case_count": sum(
                    row["failure_case_count"] for row in group
                ),
                "reveal_case_count": sum(row["reveal_case_count"] for row in group),
                "strict_error_count": sum(row["strict_error_count"] for row in group),
                "minimum_target_margin": min(
                    row["minimum_target_margin"] for row in group
                ),
                "minimum_angular_clearance": min(
                    row["minimum_angular_clearance"] for row in group
                ),
                "maximum_loop_angle_radians": max(
                    row["maximum_loop_angle_radians"] for row in group
                ),
            }
        )
    return output


def aggregate_relation_rows_by_checkpoint(
    rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["checkpoint_seed"],
            row["relation"],
            row["repeat_count"],
            row["inserted_token_budget"],
        )
        grouped[key].append(row)
    output = []
    for (checkpoint_seed, relation, repeat_count, budget), group in sorted(
        grouped.items()
    ):
        output.append(
            {
                "author": AUTHOR,
                "version": VERSION,
                "checkpoint_seed": checkpoint_seed,
                "relation": relation,
                "repeat_count": repeat_count,
                "inserted_token_budget": budget,
                "episode_count": len(group),
                "episodes_with_failure": sum(
                    row["failure_case_count"] > 0 for row in group
                ),
                "failure_case_count": sum(
                    row["failure_case_count"] for row in group
                ),
                "reveal_case_count": sum(row["reveal_case_count"] for row in group),
                "strict_error_count": sum(row["strict_error_count"] for row in group),
                "minimum_target_margin": min(
                    row["minimum_target_margin"] for row in group
                ),
                "minimum_angular_clearance": min(
                    row["minimum_angular_clearance"] for row in group
                ),
                "maximum_loop_angle_radians": max(
                    row["maximum_loop_angle_radians"] for row in group
                ),
            }
        )
    return output


def first_exit_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[int, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[
            (row["checkpoint_seed"], row["episode_index"], row["relation"])
        ].append(row)
    output: list[dict[str, Any]] = []
    for (checkpoint_seed, episode_index, relation), group in sorted(grouped.items()):
        exits = sorted(
            (row for row in group if row["failure_case_count"] > 0),
            key=lambda row: row["inserted_token_budget"],
        )
        if exits:
            first = exits[0]
            output.append(
                {
                    "checkpoint_seed": checkpoint_seed,
                    "episode_index": episode_index,
                    "episode_half": first["episode_half"],
                    "relation": relation,
                    "first_exit_repeat_count": first["repeat_count"],
                    "first_exit_inserted_token_budget": first[
                        "inserted_token_budget"
                    ],
                    "failure_case_count_at_first_exit": first[
                        "failure_case_count"
                    ],
                    "reveal_case_count_at_first_exit": first["reveal_case_count"],
                    "minimum_angular_clearance_at_first_exit": first[
                        "minimum_angular_clearance"
                    ],
                }
            )
    return output


def spectrum_summary(result: dict[str, Any]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    caveat = None
    for episode in result["relations"]["episodes"]:
        for relation_object in episode["relations"]:
            primitive = relation_object["primitive"]
            spectrum = primitive["eigenspectrum"]
            scalar = primitive["nearest_positive_scalar_identity"]
            caveat = spectrum["caveat"]
            records.append(
                {
                    "relation": primitive["relation"],
                    "raw_spectral_radius": spectrum["spectral_radius"],
                    "dominant_to_second_modulus_ratio": spectrum[
                        "dominant_to_second_modulus_ratio"
                    ],
                    "projective_asymptotic_classification": spectrum[
                        "projective_asymptotic_classification"
                    ],
                    "eigenvector_condition_number": spectrum[
                        "eigenvector_condition_number"
                    ],
                    "henrici_departure_from_normality": spectrum[
                        "henrici_departure_from_normality"
                    ],
                    "normalized_normal_commutator": spectrum[
                        "normalized_normal_commutator"
                    ],
                    "relative_residual_to_positive_scalar_identity": scalar[
                        "relative_frobenius_residual"
                    ],
                }
            )

    aggregates = []
    for relation in ("f2", "r4", "frfr", "rfrf"):
        group = [record for record in records if record["relation"] == relation]
        classifications: dict[str, int] = defaultdict(int)
        for record in group:
            classifications[record["projective_asymptotic_classification"]] += 1
        aggregates.append(
            {
                "relation": relation,
                "episode_primitive_count": len(group),
                "raw_spectral_radius_range": [
                    min(record["raw_spectral_radius"] for record in group),
                    max(record["raw_spectral_radius"] for record in group),
                ],
                "dominant_to_second_modulus_ratio_range": [
                    min(record["dominant_to_second_modulus_ratio"] for record in group),
                    max(record["dominant_to_second_modulus_ratio"] for record in group),
                ],
                "projective_asymptotic_classification_counts": dict(classifications),
                "eigenvector_condition_number_range": [
                    min(record["eigenvector_condition_number"] for record in group),
                    max(record["eigenvector_condition_number"] for record in group),
                ],
                "henrici_departure_from_normality_range": [
                    min(record["henrici_departure_from_normality"] for record in group),
                    max(record["henrici_departure_from_normality"] for record in group),
                ],
                "normalized_normal_commutator_range": [
                    min(record["normalized_normal_commutator"] for record in group),
                    max(record["normalized_normal_commutator"] for record in group),
                ],
                "relative_residual_to_positive_scalar_identity_range": [
                    min(
                        record["relative_residual_to_positive_scalar_identity"]
                        for record in group
                    ),
                    max(
                        record["relative_residual_to_positive_scalar_identity"]
                        for record in group
                    ),
                ],
            }
        )
    return {
        "episode_primitive_count": len(records),
        "by_relation": aggregates,
        "frfr_rfrf_characteristic_polynomial_global_max_abs_difference": max(
            episode["frfr_rfrf_characteristic_polynomial_max_abs_difference"]
            for episode in result["relations"]["episodes"]
        ),
        "frfr_rfrf_frobenius_scaled_characteristic_polynomial_global_max_abs_difference": max(
            episode[
                "frfr_rfrf_common_frobenius_scaled_characteristic_polynomial_max_abs_difference"
            ]
            for episode in result["relations"]["episodes"]
        ),
        "caveat": caveat,
    }


def matched_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for cell in result["matched_controls"]["checkpoint_cells"]:
        flags = cell["raw_flags"]
        reference = cell["reference"]
        identity = cell["identity_control"]
        nonidentity = {
            condition_id.rsplit(":", 1)[-1]: metrics
            for condition_id, metrics in cell["nonidentity_controls"].items()
        }
        require(set(nonidentity) == {"R2", "FR", "FR3"}, "control endpoints drifted")
        rows.append(
            {
                "author": AUTHOR,
                "version": VERSION,
                "checkpoint_seed": cell["checkpoint_seed"],
                "relation": cell["relation"],
                "budget": cell["budget"],
                "direct_reference_identity_hard_difference_count": cell[
                    "direct_reference_vs_identity_decision_difference_count"
                ],
                "reference_severity": reference["severity"],
                "identity_severity": identity["severity"],
                "R2_severity": nonidentity["R2"]["severity"],
                "FR_severity": nonidentity["FR"]["severity"],
                "FR3_severity": nonidentity["FR3"]["severity"],
                **flags,
            }
        )
    return rows


def make_summary(result: dict[str, Any]) -> dict[str, Any]:
    require(result["author"] == AUTHOR, "unexpected result author")
    require(result["version"] == VERSION, "unexpected result version")
    require(
        result["status"] == "REGISTERED_EXECUTION_COMPLETE",
        "registered execution is not complete",
    )
    require(all(result["integrity_gates"].values()), "an integrity gate failed")

    rows = relation_rows(result)
    aggregates = aggregate_relation_rows(rows)
    first_exits = first_exit_rows(rows)
    relation_exit_counts = {
        relation: sum(
            row["failure_case_count"] > 0
            for row in rows
            if row["relation"] == relation
        )
        for relation in ("f2", "r4", "frfr", "rfrf")
    }
    exit_events = result["relations"]["exit_event_index"]
    delayed_reveal_configuration_count = sum(
        any(event["first_reveal_histogram"][str(depth)] > 0 for depth in range(1, 9))
        for event in exit_events
    )
    depth_zero_reveal_configuration_count = sum(
        event["first_reveal_histogram"]["0"] > 0 for event in exit_events
    )
    all_onsets_persist = True
    trajectory_groups: dict[tuple[int, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        trajectory_groups[
            (row["checkpoint_seed"], row["episode_index"], row["relation"])
        ].append(row)
    for trajectory in trajectory_groups.values():
        ordered = sorted(trajectory, key=lambda row: row["inserted_token_budget"])
        seen_exit = False
        for row in ordered:
            if row["failure_case_count"] > 0:
                seen_exit = True
            elif seen_exit:
                all_onsets_persist = False
    final_by_relation = []
    for relation in ("f2", "r4", "frfr", "rfrf"):
        candidates = [row for row in aggregates if row["relation"] == relation]
        final_by_relation.append(max(candidates, key=lambda row: row["inserted_token_budget"]))

    first_global_by_relation = []
    for relation in ("f2", "r4", "frfr", "rfrf"):
        candidates = [
            row
            for row in aggregates
            if row["relation"] == relation and row["failure_case_count"] > 0
        ]
        first_global_by_relation.append(
            min(candidates, key=lambda row: row["inserted_token_budget"])
            if candidates
            else {"relation": relation, "observed_exit": False}
        )

    decoy_matches = defaultdict(lambda: {"true_decoy": 0, "declared_q": 0})
    for episode in result["entry"]["decoys"]:
        for route in episode["routes"]:
            decoy_matches[route["route"]]["true_decoy"] += route[
                "true_decoy_target_match_count"
            ]
            decoy_matches[route["route"]]["declared_q"] += route[
                "declared_q_target_match_count"
            ]

    matched = result["matched_controls"]
    control_matching = [
        condition["matching"]
        for condition in matched["condition_index"]
        if condition["role"] == "control"
    ]
    require(len(control_matching) == 48, "matched control count drifted")
    matching_audit = {
        "control_count": len(control_matching),
        "exact_generator_count_matches": sum(
            match["exact_generator_counts"] for match in control_matching
        ),
        "exact_directed_bigram_count_matches": sum(
            match["exact_directed_bigram_counts"] for match in control_matching
        ),
        "exact_run_second_moment_matches": sum(
            match["exact_run_second_moment"] for match in control_matching
        ),
        "exact_all_three_feature_matches": sum(
            match["exact_generator_counts"]
            and match["exact_directed_bigram_counts"]
            and match["exact_run_second_moment"]
            for match in control_matching
        ),
        "interpretation": (
            "These are globally selected best-score exact-length controls, not "
            "fully feature-matched or exchangeable controls."
        ),
    }
    entry = result["entry"]
    cone = result["finite_observed_cones"]
    relation_design = result["relations"]["design"]
    primary_decision_equivalents = (
        entry["design"]["total_decision_count"]
        + cone["design"]["logical_decision_count"]
        + relation_design["logical_decision_count"]
        + matched["design"]["logical_path_decision_count"]
    )
    require(primary_decision_equivalents == 109_035_136, "decision total drifted")

    summary = {
        "schema": "komorebi.neuralese.entry_cone_holonomy.posthoc_summary.v1",
        "version": VERSION,
        "author": AUTHOR,
        "analysis_class": "posthoc_deterministic_derivation_from_registered_result",
        "source": {
            "path": str(RESULT_PATH.relative_to(ROOT)),
            "sha256": sha256(RESULT_PATH),
            "scientific_class": result["scientific_class"],
            "scientific_design_version": result["scientific_design_version"],
            "correction_runner_version": result["correction_runner_version"],
            "status": result["status"],
        },
        "execution": result["execution"],
        "integrity_gates": result["integrity_gates"],
        "diagnostic_predicates": result["diagnostic_predicates"],
        "preregistered_composites": result["preregistered_composites"],
        "decision_accounting": {
            "entry": entry["design"]["total_decision_count"],
            "finite_observed_cones": cone["design"]["logical_decision_count"],
            "relations": relation_design["logical_decision_count"],
            "matched_paths": matched["design"]["logical_path_decision_count"],
            "primary_total_decision_equivalents": primary_decision_equivalents,
            "matched_direct_pair_comparisons_reused_not_added_to_primary_total": matched[
                "design"
            ]["direct_identity_pair_decision_comparison_count"],
        },
        "entry": {
            "schemes": entry["aggregate"]["schemes"],
            "comparisons": entry["aggregate"]["comparisons"],
            "wrong_semantic_decoy_target_matches": dict(decoy_matches),
            "interpretation": (
                "The eight native-anchor errors are confined to suffix depth zero. "
                "Both incoming recurrent routes repair all eight without a hard "
                "regression through H=8. Wrong-semantic decoys follow their actual "
                "incoming state rather than the declared label."
            ),
        },
        "finite_observed_cones": {
            "history_state_count": cone["design"]["history_state_count"],
            "logical_decision_count": cone["design"]["logical_decision_count"],
            "global_minimum_target_margin": min(
                cell["minimum_target_margin"]
                for episode in cone["episodes"]
                for cell in episode["cells"]
            ),
            "global_minimum_angular_clearance_radians": cone["aggregate"][
                "global_minimum_angular_clearance"
            ],
            "global_minimum_angular_clearance_degrees": math.degrees(
                cone["aggregate"]["global_minimum_angular_clearance"]
            ),
            "global_weakest_facet": cone["aggregate"]["global_weakest_facet"],
            "interpretation": (
                "Every enumerated recurrent state from histories of length 1 through "
                "8 remained hard-correct under every suffix through H=8, with a "
                "strictly positive finite angular buffer. This is not an ambient or "
                "infinite-horizon invariant-cone certificate."
            ),
        },
        "relations": {
            "exit_configuration_count": len(exit_events),
            "exit_configuration_count_by_relation": relation_exit_counts,
            "episode_relation_trajectories_with_exit": len(first_exits),
            "episodes_with_any_exit": len(
                {
                    (row["checkpoint_seed"], row["episode_index"])
                    for row in first_exits
                }
            ),
            "all_first_exits_persist_through_registered_maximum": all_onsets_persist,
            "exit_configurations_with_delayed_reveal": delayed_reveal_configuration_count,
            "exit_configurations_also_with_depth_zero_reveal": depth_zero_reveal_configuration_count,
            "first_exit_by_episode_relation": first_exits,
            "first_global_exit_by_relation": first_global_by_relation,
            "maximum_budget_summary_by_relation": final_by_relation,
            "H2_qualifying_relation_repeat_cells": result["relations"]["aggregate"][
                "H2_qualifying_relation_repeat_cells"
            ],
            "fresh_exit_configuration_count": result["relations"]["aggregate"][
                "fresh_exit_configuration_count"
            ],
            "maximum_stepwise_grouped_ray_discrepancy": result["relations"][
                "aggregate"
            ]["maximum_generator_vs_grouped_positive_ray_angle"],
            "maximum_loop_vs_baseline_ray_angle_radians": max(
                row["maximum_loop_angle_radians"] for row in rows
            ),
            "primitive_spectra": spectrum_summary(result),
            "interpretation": (
                "Repeated semantically identity words produce fresh finite-cone exits "
                "and delayed hard reveals. F2 is the only relation with exits in all "
                "four checkpoint-by-episode-half strata; repeat 27 (54 inserted "
                "tokens) is the earliest such common cell. The grouped and stepwise "
                "ray computations agree to numerical precision, so the observed "
                "angular drift is not a product-grouping artifact."
            ),
        },
        "matched_controls": {
            "design": matched["design"],
            "feature_matching_audit": matching_audit,
            "severity_semantics": (
                "Lexicographic descending in failure-case count, reveal-case count, "
                "and negative minimum target margin. Strict-error count and angular "
                "clearance are reported diagnostics but are not severity components."
            ),
            "classification_validity": matched["classification_validity"],
            "classification_cells": matched["classification_cells"],
            "checkpoint_cells": matched_rows(result),
            "interpretation": (
                "The finite deterministic panel shows several cells where the relator "
                "reference dominates its identity or all nonidentity controls, and an "
                "F2/B64 identity-path hard-signature difference. It shows no cell in "
                "which one nonidentity control exceeds the reference in both "
                "checkpoints. Cross-endpoint contrasts cannot isolate path mechanism "
                "from endpoint or decoder-facet difficulty."
            ),
        },
        "central_factorization": {
            "entry_initialization_defect": "present_but_finitely_repaired",
            "observed_recurrent_state_H8_cone": "strictly_safe_with_positive_buffer",
            "long_identity_loop_holonomy": "present_with_delayed_hard_reveals",
            "matched_control_specificity": "finite_relation_sensitive_pattern_not_population_inference",
            "conclusion": (
                "The registered failure is not exhausted by the entry anchor and is "
                "not merely radial blow-up. It includes projective/angular identity-"
                "loop holonomy that produces registered hard-decision exits along "
                "paths beyond the certified H=8 finite assay."
            ),
        },
        "claim_boundary": result["claim_boundary"],
        "recommended_next_block": {
            "title": "Independent Holonomy Replication, Then Quotient Repair",
            "phase_A_confirmatory_replication": {
                "primary_target": (
                    "Prospectively test whether delayed identity-loop exits generalize "
                    "across many independently trained models and genuinely held-out "
                    "task families before optimizing against this diagnostic."
                ),
                "design_requirements": [
                    "independently trained checkpoints as statistical units",
                    "held-out task families rather than coordinate-fresh episodes",
                    "blinded randomized matched-word banks with model-level inference",
                    "preregistered first-exit survival curves beyond B64 and H8",
                    "spectral predictions and tolerances fixed before endpoint inspection",
                ],
            },
            "phase_B_mechanism_intervention": {
                "primary_target": (
                    "Repair F2 identity-loop angular holonomy on a declared causal or "
                    "observable subspace while contracting transverse directions, then "
                    "replay the unchanged diagnostic on held-out models."
                ),
                "why_F2_first": (
                    "F2 is the sole relation with registered exits across all four "
                    "checkpoint-by-episode-half strata by 54 inserted tokens."
                ),
                "required_ablations": [
                    "quotient-level relation constraint only",
                    "transverse contraction only",
                    "combined relation constraint and contraction",
                    "capacity- and training-compute-matched baseline",
                ],
                "success_requires": [
                    "preserve entry repair and H=8 finite-cone clearance",
                    "remove or materially delay identity-loop exits on held-out models",
                    "improve arbitrary held-out identity words, not only trained relators",
                    "retain D4 task accuracy and causal intervention behavior",
                    "show that any metric does not merely hide delayed-observable directions",
                ],
            },
        },
    }
    return summary


def write_csvs(
    relation_aggregates: list[dict[str, Any]],
    relation_checkpoint_aggregates: list[dict[str, Any]],
    matched: list[dict[str, Any]],
) -> None:
    with RELATION_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(relation_aggregates[0]))
        writer.writeheader()
        writer.writerows(relation_aggregates)
    with RELATION_BY_CHECKPOINT_CSV_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(relation_checkpoint_aggregates[0])
        )
        writer.writeheader()
        writer.writerows(relation_checkpoint_aggregates)
    flattened = []
    for row in matched:
        flattened.append(
            {
                **{k: v for k, v in row.items() if not isinstance(v, list)},
                "reference_severity": json.dumps(row["reference_severity"]),
                "identity_severity": json.dumps(row["identity_severity"]),
                "R2_severity": json.dumps(row["R2_severity"]),
                "FR_severity": json.dumps(row["FR_severity"]),
                "FR3_severity": json.dumps(row["FR3_severity"]),
            }
        )
    with MATCHED_CSV_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(flattened[0]))
        writer.writeheader()
        writer.writerows(flattened)


def render_figures(
    relation_aggregates: list[dict[str, Any]], result: dict[str, Any]
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    colors = {
        "f2": "#3B82F6",
        "r4": "#F59E0B",
        "frfr": "#10B981",
        "rfrf": "#8B5CF6",
    }
    labels = {"f2": r"$F^2$", "r4": r"$R^4$", "frfr": "FRFR", "rfrf": "RFRF"}

    fig, axes = plt.subplots(2, 1, figsize=(9.2, 7.2), sharex=True)
    for relation in ("f2", "r4", "frfr", "rfrf"):
        series = sorted(
            (row for row in relation_aggregates if row["relation"] == relation),
            key=lambda row: row["inserted_token_budget"],
        )
        x = [row["inserted_token_budget"] for row in series]
        axes[0].plot(
            x,
            [row["episodes_with_failure"] for row in series],
            marker="o",
            markersize=3.2,
            linewidth=1.8,
            color=colors[relation],
            label=labels[relation],
        )
        axes[1].plot(
            x,
            [row["minimum_angular_clearance"] for row in series],
            marker="o",
            markersize=3.2,
            linewidth=1.8,
            color=colors[relation],
            label=labels[relation],
        )
    axes[0].set_ylabel("Episodes with a hard exit\n(out of 16)")
    axes[0].set_ylim(-0.35, 16.35)
    axes[0].axvline(54, color="#334155", linestyle="--", linewidth=1.1)
    axes[0].text(
        29.0,
        15.1,
        r"H2: $F^2$ exits occur somewhere in all 4 registered strata (B54–64)",
        fontsize=8.6,
    )
    axes[0].legend(ncol=4, frameon=False, loc="upper left")
    axes[0].grid(axis="y", alpha=0.2)
    axes[1].axhline(0, color="#111827", linewidth=1.1)
    axes[1].set_ylabel("Worst angular clearance (rad)")
    axes[1].set_xlabel("Inserted-token budget")
    axes[1].grid(alpha=0.2)
    fig.suptitle("Registered identity-loop exits are delayed and relation-sensitive", fontsize=14)
    fig.text(
        0.5,
        0.012,
        "Finite deterministic assay: 2 checkpoints × 8 episodes; suffix horizon H=8",
        ha="center",
        fontsize=9,
        color="#475569",
    )
    fig.tight_layout(rect=(0, 0.035, 1, 0.96))
    fig.savefig(
        FIGURE_DIR / "V032_RELATION_EXIT_PROFILE.png",
        dpi=180,
        metadata={"Author": AUTHOR, "Title": "V032 relation exit profile"},
    )
    plt.close(fig)

    relations = ["f2", "r4", "frfr", "rfrf"]
    budgets = [16, 32, 64]
    classification = result["matched_controls"]["classification_cells"]
    cell_sets = {
        key: {(item["relation"], item["budget"]) for item in values}
        for key, values in classification.items()
    }
    values = np.zeros((len(relations), len(budgets)), dtype=int)
    annotations = []
    for i, relation in enumerate(relations):
        row_annotations = []
        for j, budget in enumerate(budgets):
            active = [key for key in ("X1", "X2", "X3") if (relation, budget) in cell_sets[key]]
            values[i, j] = len(active)
            row_annotations.append("\n".join(active) if active else "—")
        annotations.append(row_annotations)
    fig, ax = plt.subplots(figsize=(7.7, 5.0))
    image = ax.imshow(values, cmap="Blues", vmin=0, vmax=3, aspect="auto")
    for i in range(len(relations)):
        for j in range(len(budgets)):
            ax.text(
                j,
                i,
                annotations[i][j],
                ha="center",
                va="center",
                color="white" if values[i, j] >= 2 else "#0F172A",
                fontsize=10,
                fontweight="semibold",
            )
    ax.set_xticks(range(len(budgets)), [str(value) for value in budgets])
    ax.set_yticks(range(len(relations)), [labels[value] for value in relations])
    ax.set_xlabel("Inserted-token budget")
    ax.set_ylabel("Identity relator reference")
    ax.set_title("Registered matched-panel classification cells")
    for edge in np.arange(-0.5, len(budgets), 1):
        ax.axvline(edge, color="white", linewidth=1.5)
    for edge in np.arange(-0.5, len(relations), 1):
        ax.axhline(edge, color="white", linewidth=1.5)
    fig.text(
        0.5,
        0.01,
        "X0 is false (no replicated nonidentity-control excess); X4 is therefore false.\n"
        "Finite deterministic bank; cross-endpoint controls do not identify mechanism.",
        ha="center",
        fontsize=8.7,
        color="#475569",
    )
    fig.colorbar(image, ax=ax, label="Number of active X1–X3 classifications", shrink=0.78)
    fig.tight_layout(rect=(0, 0.085, 1, 1))
    fig.savefig(
        FIGURE_DIR / "V032_MATCHED_CLASSIFICATIONS.png",
        dpi=180,
        metadata={"Author": AUTHOR, "Title": "V032 matched classifications"},
    )
    plt.close(fig)

    raw_relation_rows = relation_rows(result)
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4), sharex=True, sharey=True)
    for checkpoint_seed, axis in enumerate(axes):
        for relation in relations:
            grouped = defaultdict(int)
            for row in raw_relation_rows:
                if row["checkpoint_seed"] == checkpoint_seed and row["relation"] == relation:
                    grouped[row["inserted_token_budget"]] += int(
                        row["failure_case_count"] > 0
                    )
            x = sorted(grouped)
            axis.plot(
                x,
                [grouped[value] for value in x],
                marker="o",
                markersize=3.2,
                linewidth=1.8,
                color=colors[relation],
                label=labels[relation],
            )
        axis.axvspan(54, 64, color="#CBD5E1", alpha=0.28, zorder=-2)
        axis.set_title(f"Checkpoint seed {checkpoint_seed}")
        axis.set_xlabel("Inserted-token budget")
        axis.set_ylim(-0.2, 8.2)
        axis.grid(axis="y", alpha=0.2)
    axes[0].set_ylabel("Episodes with a hard exit (out of 8)")
    axes[0].legend(ncol=2, frameon=False, loc="upper left")
    fig.suptitle("Identity-loop exits differ sharply between checkpoints", fontsize=14)
    fig.text(
        0.5,
        0.012,
        "Shading marks the F² all-strata band (B54–B64); it does not mean every episode exits.",
        ha="center",
        fontsize=8.8,
        color="#475569",
    )
    fig.tight_layout(rect=(0, 0.045, 1, 0.95))
    fig.savefig(
        FIGURE_DIR / "V032_RELATION_EXIT_BY_CHECKPOINT.png",
        dpi=180,
        metadata={"Author": AUTHOR, "Title": "V032 relation exits by checkpoint"},
    )
    plt.close(fig)

    matched = matched_rows(result)
    row_keys = [(relation, budget) for relation in relations for budget in budgets]
    control_keys = ["identity", "R2", "FR", "FR3"]
    severity_keys = {
        "identity": "identity_severity",
        "R2": "R2_severity",
        "FR": "FR_severity",
        "FR3": "FR3_severity",
    }

    def comparison_code(reference: list[float], control: list[float]) -> tuple[int, str]:
        for index, component in enumerate(("F", "R", "M")):
            if reference[index] > control[index]:
                return 3 - index, f"Ref:{component}"
            if reference[index] < control[index]:
                return -(3 - index), f"Ctl:{component}"
        return 0, "Equal"

    from matplotlib.colors import BoundaryNorm, ListedColormap

    cmap = ListedColormap(
        ["#7F1D1D", "#DC2626", "#FCA5A5", "#F8FAFC", "#93C5FD", "#2563EB", "#1E3A8A"]
    )
    norm = BoundaryNorm([-3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 8.0), sharey=True)
    for checkpoint_seed, axis in enumerate(axes):
        matrix = np.zeros((len(row_keys), len(control_keys)), dtype=int)
        annotations: list[list[str]] = []
        for i, (relation, budget) in enumerate(row_keys):
            cell = next(
                row
                for row in matched
                if row["checkpoint_seed"] == checkpoint_seed
                and row["relation"] == relation
                and row["budget"] == budget
            )
            line = []
            for j, control in enumerate(control_keys):
                code, annotation = comparison_code(
                    cell["reference_severity"], cell[severity_keys[control]]
                )
                matrix[i, j] = code
                line.append(annotation)
            annotations.append(line)
        axis.imshow(matrix, cmap=cmap, norm=norm, aspect="auto")
        for i in range(len(row_keys)):
            for j in range(len(control_keys)):
                axis.text(
                    j,
                    i,
                    annotations[i][j],
                    ha="center",
                    va="center",
                    fontsize=7.8,
                    color="white" if abs(matrix[i, j]) >= 2 else "#0F172A",
                )
        axis.set_xticks(range(len(control_keys)), ["Identity", "R²", "FR", "FR³"])
        axis.set_title(f"Checkpoint seed {checkpoint_seed}")
        for edge in np.arange(-0.5, len(control_keys), 1):
            axis.axvline(edge, color="white", linewidth=1.1)
        for edge in np.arange(-0.5, len(row_keys), 1):
            axis.axhline(edge, color="white", linewidth=1.1)
    axes[0].set_yticks(
        range(len(row_keys)),
        [f"{labels[relation]} · B{budget}" for relation, budget in row_keys],
    )
    fig.suptitle("Registered lexicographic severity: reference versus each control", fontsize=14)
    fig.text(
        0.5,
        0.014,
        "Ref/Ctl = more severe side; F = failing-case count, R = reveal count, M = −minimum-margin tie-break.\n"
        "Strict-error count is not part of severity. R²/FR/FR³ cross semantic endpoints.",
        ha="center",
        fontsize=8.7,
        color="#475569",
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.95))
    fig.savefig(
        FIGURE_DIR / "V032_MATCHED_LEX_COMPARISON.png",
        dpi=180,
        metadata={"Author": AUTHOR, "Title": "V032 matched lexicographic comparison"},
    )
    plt.close(fig)

    by_seed = {
        seed: [
            next(
                cell
                for cell in result["matched_controls"]["checkpoint_cells"]
                if cell["checkpoint_seed"] == seed
                and cell["relation"] == relation
                and cell["budget"] == budget
            )
            for relation, budget in row_keys
        ]
        for seed in (0, 1)
    }
    x = np.arange(len(row_keys))
    fig, ax = plt.subplots(figsize=(11.2, 4.7))
    width = 0.38
    for seed, offset, color in ((0, -width / 2, "#3B82F6"), (1, width / 2, "#F97316")):
        values = [
            100
            * cell["direct_reference_vs_identity_decision_difference_count"]
            / cell["reference"]["decision_count"]
            for cell in by_seed[seed]
        ]
        bars = ax.bar(x + offset, values, width, label=f"Checkpoint {seed}", color=color)
        for bar, cell in zip(bars, by_seed[seed]):
            count = cell["direct_reference_vs_identity_decision_difference_count"]
            if count:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.035,
                    str(count),
                    rotation=90,
                    ha="center",
                    va="bottom",
                    fontsize=7.2,
                )
    ax.set_xticks(
        x,
        [f"{labels[relation]}\nB{budget}" for relation, budget in row_keys],
    )
    ax.set_ylabel("Reference/identity hard disagreements (%)")
    ax.set_title("Only F²/B64 hard-disagrees in both checkpoint aggregates")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.2)
    fig.text(
        0.5,
        0.008,
        "Labels are raw disagreement counts of 261,632 decisions per checkpoint cell. "
        "FRFR/RFRF share reversed aliases at each budget.",
        ha="center",
        fontsize=8.6,
        color="#475569",
    )
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(
        FIGURE_DIR / "V032_IDENTITY_PATH_DISAGREEMENTS.png",
        dpi=180,
        metadata={"Author": AUTHOR, "Title": "V032 identity path disagreements"},
    )
    plt.close(fig)


def main() -> int:
    require(sha256(RESULT_PATH) == EXPECTED_RESULT_SHA256, "result digest mismatch")
    result = strict_json(RESULT_PATH)
    summary = make_summary(result)
    raw_rows = relation_rows(result)
    relation_aggregates = aggregate_relation_rows(raw_rows)
    relation_checkpoint_aggregates = aggregate_relation_rows_by_checkpoint(raw_rows)
    matched = matched_rows(result)
    atomic_json(SUMMARY_PATH, summary)
    write_csvs(relation_aggregates, relation_checkpoint_aggregates, matched)
    render_figures(relation_aggregates, result)
    generated = [
        SUMMARY_PATH,
        RELATION_CSV_PATH,
        RELATION_BY_CHECKPOINT_CSV_PATH,
        MATCHED_CSV_PATH,
        FIGURE_DIR / "V032_RELATION_EXIT_PROFILE.png",
        FIGURE_DIR / "V032_RELATION_EXIT_BY_CHECKPOINT.png",
        FIGURE_DIR / "V032_MATCHED_CLASSIFICATIONS.png",
        FIGURE_DIR / "V032_MATCHED_LEX_COMPARISON.png",
        FIGURE_DIR / "V032_IDENTITY_PATH_DISAGREEMENTS.png",
    ]
    analysis_record = {
        "schema": "komorebi.neuralese.entry_cone_holonomy.analysis_complete.v1",
        "version": VERSION,
        "author": AUTHOR,
        "status": "POSTHOC_ANALYSIS_COMPLETE",
        "analysis_class": "deterministic_posthoc_derivation",
        "registered_result": {
            "path": str(RESULT_PATH.relative_to(ROOT)),
            "sha256": sha256(RESULT_PATH),
        },
        "artifacts": {
            str(path.relative_to(ROOT)): {
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
            }
            for path in generated
        },
        "scientific_mutation": "none",
        "checkpoint_deserialization": "not_performed",
        "learned_endpoint_execution": "not_performed",
    }
    atomic_json(ANALYSIS_RECORD_PATH, analysis_record)
    print(f"SUMMARY={SUMMARY_PATH}")
    print(f"SUMMARY_SHA256={sha256(SUMMARY_PATH)}")
    print(f"RELATION_ROWS={len(relation_aggregates)}")
    print(f"MATCHED_CHECKPOINT_CELLS={len(matched)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
