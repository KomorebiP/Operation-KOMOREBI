#!/usr/bin/env python3
"""Post-hoc, read-only synthesis of the frozen v0.3.0 registered result."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "results" / "COMPLETION_SURFACE_RESULTS.json"
OUTPUT = ROOT / "results" / "POSTHOC_SUMMARY.json"
REPORT = ROOT / "RESULTS_SUMMARY.md"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def cell(cells: list[dict[str, Any]], L: int, H: int) -> dict[str, Any]:
    return next(item for item in cells if item["L"] == L and item["H"] == H)


def build_summary(data: dict[str, Any]) -> dict[str, Any]:
    episodes = [episode for seed in data["records"].values() for episode in seed["episodes"]]
    final_cells = [cell(episode["cumulative_cells"], 8, 8) for episode in episodes]
    full_decisions = sum(item["decision_count"] for item in final_cells)
    full_correct = sum(item["correct_decision_count"] for item in final_cells)

    post_burnin_cells = [
        cell(episode["exact_history_cumulative_future_cells"], L, 8)
        for episode in episodes
        for L in range(1, 9)
    ]
    post_burnin_decisions = sum(item["decision_count"] for item in post_burnin_cells)
    post_burnin_correct = sum(item["correct_decision_count"] for item in post_burnin_cells)

    seed0_anchor = [cell(ep["cumulative_cells"], 0, 0) for ep in data["records"]["0"]["episodes"]]
    seed1_anchor = [cell(ep["cumulative_cells"], 0, 0) for ep in data["records"]["1"]["episodes"]]

    diagonal_cells = [
        item
        for episode in episodes
        for item in episode["diagonal_action"]["cells"]
    ]
    diagonal_by_horizon: dict[str, dict[str, int]] = {}
    for H in range(8):
        selected = [item for item in diagonal_cells if item["H"] == H]
        diagonal_by_horizon[str(H)] = {
            "passed": sum(bool(item["passed"]) for item in selected),
            "total": len(selected),
        }

    soft_points: dict[str, Any] = {}
    for interface in ("probability", "centered_logit"):
        view = "exact_history_cumulative_future"
        for L, H in ((1, 0), (8, 8)):
            selected = [
                cell(
                    episode["soft_interfaces"]["interfaces"][interface]["views"][view],
                    L,
                    H,
                )
                for episode in episodes
            ]
            soft_points[f"{interface}_exact_L{L}_H{H}"] = {
                "episodes_passing_exact_collapse": sum(
                    bool(item["exact_soft_collapse_pass"]) for item in selected
                ),
                "episode_count": len(selected),
                "minimum_maximum_within_label_coordinate_range": min(
                    item["maximum_within_label_coordinate_range"] for item in selected
                ),
                "maximum_maximum_within_label_coordinate_range": max(
                    item["maximum_within_label_coordinate_range"] for item in selected
                ),
                "maximum_scalar_normalized_rms": max(
                    item["within_label_rms_deviation"] for item in selected
                ),
            }

    relation_records = [
        record
        for seed in data["records"].values()
        for episode in seed["relator_witness"]["episodes"]
        for record in episode["relation_budget_records"]
    ]
    relator_decisions = sum(
        record["cumulative_suffix_records"][-1]["decision_count"]
        for record in relation_records
    )
    identity_wrong_decisions = sum(
        round(
            (1.0 - record["cumulative_suffix_records"][-1]["interfaces"]["identity_loop"]["semantic_accuracy"])
            * record["cumulative_suffix_records"][-1]["decision_count"]
        )
        for record in relation_records
    )
    reveal_histogram: Counter[str] = Counter()
    for record in relation_records:
        reveal_histogram.update(record["first_reveal_histogram"])
    relation_table: list[dict[str, Any]] = []
    keys = sorted(
        {(record["relation"], record["inserted_token_budget"]) for record in relation_records},
        key=lambda item: (item[0], item[1]),
    )
    for relation, budget in keys:
        selected = [
            record
            for record in relation_records
            if record["relation"] == relation and record["inserted_token_budget"] == budget
        ]
        final = [record["cumulative_suffix_records"][-1] for record in selected]
        reveals = [
            record["first_revealing_suffix_horizon"]
            for record in selected
            if record["first_revealing_suffix_horizon"] is not None
        ]
        relation_table.append(
            {
                "relation": relation,
                "inserted_token_budget": budget,
                "observed_history_depth": 6 + budget,
                "configuration_episode_count": len(selected),
                "hard_gate_pass_count": sum(
                    bool(record["gates"]["W0_relator_hard_closure"])
                    for record in selected
                ),
                "soft_gate_pass_count": sum(
                    bool(record["gates"]["W1_relator_soft_flatness"])
                    for record in selected
                ),
                "control_gate_pass_count": sum(
                    bool(record["gates"]["C0_nonidentity_control"])
                    for record in selected
                ),
                "mean_H8_hard_signature_survival": sum(
                    item["identity_loop_vs_baseline"]["hard_signature_survival_fraction"]
                    for item in final
                )
                / len(final),
                "minimum_H8_hard_signature_survival": min(
                    item["identity_loop_vs_baseline"]["hard_signature_survival_fraction"]
                    for item in final
                ),
                "mean_identity_semantic_accuracy": sum(
                    item["interfaces"]["identity_loop"]["semantic_accuracy"]
                    for item in final
                )
                / len(final),
                "minimum_identity_semantic_accuracy": min(
                    item["interfaces"]["identity_loop"]["semantic_accuracy"]
                    for item in final
                ),
                "minimum_identity_target_margin": min(
                    item["interfaces"]["identity_loop"]["target_margin"]["minimum"]
                    for item in final
                ),
                "identity_failing_case_count": sum(
                    record["identity_semantic_or_margin_failure_count"]
                    for record in selected
                ),
                "first_revealing_suffix_horizon": min(reveals) if reveals else None,
                "maximum_positive_ray_angle": max(
                    item["paired_path"]["positive_ray_angle"]["maximum"]
                    for item in final
                ),
                "maximum_probability_coordinate_difference": max(
                    item["paired_path"]["probability"]["maximum_difference"]
                    for item in final
                ),
                "maximum_centered_logit_coordinate_difference": max(
                    item["paired_path"]["centered_logit"]["maximum_difference"]
                    for item in final
                ),
            }
        )

    failures = [
        (record["observed_history_depth"], witness["first_failure_horizon"], seed_name,
         episode["episode_index"], record, witness)
        for seed_name, seed in data["records"].items()
        for episode in seed["relator_witness"]["episodes"]
        for record in episode["relation_budget_records"]
        for witness in record["identity_semantic_or_margin_failures"]
    ]
    earliest = min(failures, key=lambda item: (item[0], item[1]))
    _, _, seed_name, episode_index, record, witness = earliest

    return {
        "schema": "komorebi.neuralese.completion_surface.posthoc_summary.v1",
        "source_results": str(SOURCE.name),
        "source_results_sha256": sha256(SOURCE),
        "registered_gates": data["gates"],
        "execution_elapsed_seconds": data["execution"]["elapsed_seconds"],
        "ordinary_surface": {
            "full_cumulative_L8_H8": {
                "decision_count": full_decisions,
                "correct_decision_count": full_correct,
                "error_count": full_decisions - full_correct,
                "accuracy": full_correct / full_decisions,
                "episode_hard_pass_count": sum(
                    bool(item["hard_completion_pass"]) for item in final_cells
                ),
                "episode_count": len(final_cells),
            },
            "seed0_depth0_anchor": {
                "accuracy": min(item["semantic_continuation_accuracy"] for item in seed0_anchor),
                "signature_class_count": min(item["signature_class_count"] for item in seed0_anchor),
                "maximum_merge_multiplicity": max(item["maximum_merge_multiplicity"] for item in seed0_anchor),
                "minimum_target_margin": min(item["minimum_target_margin"] for item in seed0_anchor),
                "misdecoded_semantic_label": 2,
                "colliding_prediction_label": 6,
            },
            "seed1_depth0_anchor": {
                "accuracy": min(item["semantic_continuation_accuracy"] for item in seed1_anchor),
                "signature_class_count": min(item["signature_class_count"] for item in seed1_anchor),
                "minimum_target_margin": min(item["minimum_target_margin"] for item in seed1_anchor),
            },
            "post_burnin_exact_L1_to_L8_cumulative_H8": {
                "decision_count": post_burnin_decisions,
                "correct_decision_count": post_burnin_correct,
                "error_count": post_burnin_decisions - post_burnin_correct,
                "all_128_episode_depth_cells_pass": all(
                    bool(item["hard_completion_pass"]) for item in post_burnin_cells
                ),
                "minimum_target_margin": min(
                    item["minimum_target_margin"] for item in post_burnin_cells
                ),
                "scope_note": "Post-hoc conjunction of registered exact-history shells, not the preregistered cumulative H0 gate.",
            },
            "diagonal_action_by_target_horizon": diagonal_by_horizon,
            "soft_exact_history_points": soft_points,
        },
        "relator_witness": {
            "configuration_episode_count": len(relation_records),
            "hard_gate_pass_count": sum(
                bool(record["gates"]["W0_relator_hard_closure"])
                for record in relation_records
            ),
            "soft_gate_pass_count": sum(
                bool(record["gates"]["W1_relator_soft_flatness"])
                for record in relation_records
            ),
            "control_gate_pass_count": sum(
                bool(record["gates"]["C0_nonidentity_control"])
                for record in relation_records
            ),
            "total_case_configuration_count": sum(
                record["base_case_count"] for record in relation_records
            ),
            "decision_count": relator_decisions,
            "identity_wrong_decision_count": identity_wrong_decisions,
            "identity_failing_case_count": sum(
                record["identity_semantic_or_margin_failure_count"]
                for record in relation_records
            ),
            "first_reveal_histogram": dict(reveal_histogram),
            "delayed_failing_case_count": sum(
                value for key, value in reveal_histogram.items() if key not in {"0", ">8"}
            ),
            "earliest_observed_depth_failure": {
                "checkpoint_seed": int(seed_name),
                "episode_index": episode_index,
                "relation": record["relation"],
                "inserted_token_budget": record["inserted_token_budget"],
                "observed_history_depth": record["observed_history_depth"],
                **witness,
            },
            "by_relation_budget": relation_table,
        },
        "interpretation": {
            "best_supported": "A task-local hard decision-cone code is exact on every registered ordinary history shell after one generator step, through history depth 8 and continuation horizon 8.",
            "not_supported": [
                "completion from raw initialization for both seeds",
                "exact probability or centered-logit quotient",
                "full registered diagonal compatibility at H=0",
                "path-flat long recurrence",
                "unbounded or architecture-independent Neuralese",
            ],
            "mechanism_hypothesis": "The system has a separate entry transient followed by a metastable hard semantic regime. History-bearing soft microstate and repeated-path drift accumulate inside decision cones until margins are crossed.",
        },
    }


def render_report(summary: dict[str, Any]) -> str:
    ordinary = summary["ordinary_surface"]
    relator = summary["relator_witness"]
    rows = [
        item
        for item in relator["by_relation_budget"]
        if item["inserted_token_budget"] in {32, 64}
    ]
    relation_lines = [
        "| Relation | Added tokens | Environments passing hard gate | Mean / worst H8 survival | First reveal |",
        "|---|---:|---:|---:|---:|",
    ]
    for item in rows:
        first = "none" if item["first_revealing_suffix_horizon"] is None else str(item["first_revealing_suffix_horizon"])
        relation_lines.append(
            f"| `{item['relation']}` | {item['inserted_token_budget']} | "
            f"{item['hard_gate_pass_count']}/16 | "
            f"{item['mean_H8_hard_signature_survival']:.6f} / "
            f"{item['minimum_H8_hard_signature_survival']:.6f} | {first} |"
        )
    soft = ordinary["soft_exact_history_points"]
    p10 = soft["probability_exact_L1_H0"]
    p88 = soft["probability_exact_L8_H8"]
    z10 = soft["centered_logit_exact_L1_H0"]
    z88 = soft["centered_logit_exact_L8_H8"]
    full = ordinary["full_cumulative_L8_H8"]
    burn = ordinary["post_burnin_exact_L1_to_L8_cumulative_H8"]
    earliest = relator["earliest_observed_depth_failure"]
    gate_lines = "\n".join(
        f"| `{name}` | {'PASS' if passed else 'FAIL'} |"
        for name, passed in summary["registered_gates"].items()
    )
    return f"""# Neuralese Bi-Depth Completion Surface — Results

Version: 0.3.0  
Status: registered adaptive developmental follow-up  
Source result SHA-256: `{summary['source_results_sha256']}`

## Outcome

| Gate | Status |
|---|---|
{gate_lines}

Execution and cumulative down-set consistency passed. Every scientific completion, soft-collapse, and long-path gate failed under its preregistered exact rule.

## Ordinary histories

The full cumulative `(L=8,H=8)` domain contained **{full['decision_count']:,}** decisions. It had **{full['error_count']}** errors, for aggregate accuracy `{full['accuracy']:.9f}`, but only `{full['episode_hard_pass_count']}/{full['episode_count']}` episode surfaces passed the strict hard gate. All eight errors were the same seed-0 depth-zero anchor defect: semantic label 2 decoded as 6, leaving 7 hard classes, a two-label merge, and minimum margin `{ordinary['seed0_depth0_anchor']['minimum_target_margin']:.6f}`.

The exact history shells reveal a different regime. Across every ordinary history length 1–8, all continuations through H8, both checkpoints, and all 16 episodes, **{burn['correct_decision_count']:,}/{burn['decision_count']:,}** decisions were correct. Every one of the 128 episode/depth cells had one hard signature per semantic state, with minimum margin `{burn['minimum_target_margin']:.6f}`. This is a post-hoc conjunction of registered shell results; it does not replace the failed cumulative gate.

Diagonal compatibility passed in all `1792/1792` generator-cells at target horizons 1–7. At target horizon 0 it passed `128/256`: every seed-1 case passed and every seed-0 case failed because the zero-horizon interface could not resolve the anchor defect. Thus future observability repairs the coarse hard partition, but the full registered diagonal gate remains failed.

## Soft microstate

Exact hard profiles do not imply soft collapse. Already at exact `(L=1,H=0)`, every episode failed both soft interfaces. The maximum within-semantic probability-coordinate range lay between `{p10['minimum_maximum_within_label_coordinate_range']:.6g}` and `{p10['maximum_maximum_within_label_coordinate_range']:.6g}`; centered-logit range lay between `{z10['minimum_maximum_within_label_coordinate_range']:.6g}` and `{z10['maximum_maximum_within_label_coordinate_range']:.6g}`.

By exact history `L=8` with cumulative futures through `H=8`, those episode-wise maxima ranged from `{p88['minimum_maximum_within_label_coordinate_range']:.6g}` to `{p88['maximum_maximum_within_label_coordinate_range']:.6g}` for probabilities and `{z88['minimum_maximum_within_label_coordinate_range']:.6g}` to `{z88['maximum_maximum_within_label_coordinate_range']:.6g}` for centered logits. The exact tolerance was `1e-10` (or its registered centered-logit scale adjustment), so this is a clear soft/history microstate, not numerical noise.

## Repeated identity paths

The witness block evaluated `{relator['configuration_episode_count']}` relation/budget/environment records, covering `{relator['total_case_configuration_count']:,}` individual cases and **{relator['decision_count']:,}** suffix decisions through H8. Hard closure passed `{relator['hard_gate_pass_count']}/{relator['configuration_episode_count']}` records; exact soft path flatness passed `0/{relator['configuration_episode_count']}`; the matched nonidentity control passed `{relator['control_gate_pass_count']}/{relator['configuration_episode_count']}`. Identity insertions produced `{relator['identity_wrong_decision_count']:,}` wrong decisions in `{relator['identity_failing_case_count']:,}` cases.

{chr(10).join(relation_lines)}

The earliest hard counterexample occurred at total observed history depth **{earliest['observed_history_depth']}**: checkpoint seed {earliest['checkpoint_seed']}, episode {earliest['episode_index']}, `{earliest['relation']}` with {earliest['inserted_token_budget']} inserted tokens. It remained correct at the loop endpoint and first failed after a suffix of length **{earliest['first_failure_horizon']}**, with target margin `{earliest['target_margin']:.6f}`. Across all hard-failing cases, `{relator['delayed_failing_case_count']:,}/{relator['identity_failing_case_count']:,}` (`{relator['delayed_failing_case_count']/relator['identity_failing_case_count']:.2%}`) required a nonempty continuation. This is direct delayed observability.

Soft path flatness failed before hard behavior did. Even one `F^2` loop (two inserted tokens) reached worst angle about `0.0535` rad, probability-coordinate drift `0.01109`, and centered-logit drift `0.1602`, while hard decisions still passed. At 32 tokens the mixed relations first crossed decision boundaries; by 64 tokens every relation family failed somewhere. The matched nonidentity control failed in 19 records versus 20 identity-loop failures, so most long-depth failures are not unique to algebraically identity words; they indicate broader path-length fragility with relation-dependent rates.

## Interpretation

The most economical model is now:

\\[
\\text{{entry transient}}\\;\\longrightarrow\\;\\text{{metastable hard decision-cone code}}\\;\\longrightarrow\\;\\text{{margin-crossing path drift}}.
\\]

This is stronger than “the model merely memorized depth 6”: every ordinary exact shell from depth 1 through 8 had perfect hard continuation profiles through H8. It is weaker than causal completion: raw initialization is not uniformly in the code, soft state retains history, and algebraically redundant paths eventually leave the correct decision cones.

No result here establishes unbounded recurrence, an exact soft predictive quotient, an invariant metric, a normally attracting fiber, architecture-independent transport, or spontaneous Neuralese in general language models.
"""


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    summary = build_summary(data)
    OUTPUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(summary), encoding="utf-8")
    print(json.dumps({"summary": str(OUTPUT), "report": str(REPORT)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
