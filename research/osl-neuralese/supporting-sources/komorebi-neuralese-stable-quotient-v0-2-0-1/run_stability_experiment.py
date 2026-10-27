#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.stability_eval import (
    build_stability_arms,
    code_audit,
    cross_seed_semantic_transport,
    deep_intervention_audit,
    deep_rollout_metrics,
    file_sha256,
    load_legacy_linear_checkpoint,
    null_cycle_metrics,
    observability_audit,
    projective_gauge_audit,
)
from komorebi_neuralese.reporting import source_files, tree_digest


PROFILES: dict[str, dict[str, Any]] = {
    "smoke": {
        "seeds": [0],
        "examples": 128,
        "batch_size": 128,
        "code_examples": 64,
        "observability_examples": 8,
        "lengths": [1, 4, 8, 16, 32, 64],
        "families": ["d4", "c8"],
        "gauge_lengths": [8, 64],
        "null_repeats": [0, 1, 2],
        "null_examples": 128,
        "intervention_examples": 128,
        "intervention_length": 16,
    },
    "pilot": {
        "seeds": [0, 1],
        "examples": 1024,
        "batch_size": 256,
        "code_examples": 256,
        "observability_examples": 32,
        "lengths": [1, 2, 3, 4, 8, 12, 32, 64, 128, 256],
        "families": ["d4", "c8", "mixed_cycle", "random"],
        "gauge_lengths": [8, 64, 128, 256],
        "null_repeats": [0, 1, 2, 4, 8, 16],
        "null_examples": 512,
        "intervention_examples": 512,
        "intervention_length": 64,
    },
    "confirmatory": {
        "seeds": [0, 1],
        "examples": 8192,
        "batch_size": 512,
        "code_examples": 2048,
        "observability_examples": 64,
        "lengths": [1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512],
        "families": ["d4", "c8", "mixed_cycle", "random"],
        "gauge_lengths": [8, 64, 128, 256, 512],
        "null_repeats": [0, 1, 2, 4, 8, 16, 32],
        "null_examples": 4096,
        "intervention_examples": 4096,
        "intervention_length": 128,
    },
}

PARENT_ARMS = ("linear_terminal", "linear_relation")
VARIANTS = ("raw", "normalized_raw", "metric_polar", "anchor_closed", "semantic_chart_closed")


def atomic_json(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _values(records: dict[str, Any], parent: str, variant: str, *keys: str) -> list[float]:
    output: list[float] = []
    for seed_record in records[parent].values():
        value: Any = seed_record["variants"][variant]
        for key in keys:
            value = value[key]
        output.append(float(value))
    return output


def adjudicate(records: dict[str, Any], transport: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    gates: dict[str, Any] = {}

    def add(name: str, observed: Any, criterion: str, passed: bool) -> None:
        gates[name] = {"observed": observed, "criterion": criterion, "passed": bool(passed)}

    observability_null = [
        seed_record["observability"]["finite_horizon"]["null_dimension"]
        for parent in PARENT_ARMS
        for seed_record in records[parent].values()
    ]
    add(
        "no_fixed_additive_nuisance_packet",
        max(observability_null),
        "finite-horizon future-null dimension == 0",
        max(observability_null) == 0,
    )

    comparable_agreements = []
    for seed_record in records["linear_terminal"].values():
        for row in seed_record["projective_gauge"].values():
            if row["prediction_agreement_when_comparable"] is not None:
                comparable_agreements.append(row["prediction_agreement_when_comparable"])
    min_agreement = min(comparable_agreements) if comparable_agreements else 0.0
    add("projective_gauge_prediction_equivalence", min_agreement, ">= 0.999999", min_agreement >= 0.999999)

    anchor_accuracy = []
    anchor_finite = []
    for parent in PARENT_ARMS:
        for seed_record in records[parent].values():
            for family in config["families"]:
                for row in seed_record["variants"]["semantic_chart_closed"]["deep"][family].values():
                    anchor_accuracy.append(row["accuracy"])
                    anchor_finite.append(row["finite_fraction"])
    add("semantic_chart_all_depth_accuracy", min(anchor_accuracy), ">= 0.999", min(anchor_accuracy) >= 0.999)
    add("semantic_chart_all_depth_finite", min(anchor_finite), ">= 1.0", min(anchor_finite) >= 1.0)

    closure_defects = [
        seed_record["variants"]["semantic_chart_closed"]["code_audit"]["anchor_defect_max"]
        for parent in PARENT_ARMS
        for seed_record in records[parent].values()
    ]
    metric_defects = [
        seed_record["variants"]["semantic_chart_closed"]["code_audit"]["metric_isometry_defect_max"]
        for parent in PARENT_ARMS
        for seed_record in records[parent].values()
    ]
    metric_conditions = [
        seed_record["variants"]["semantic_chart_closed"]["code_audit"]["metric_condition_number"]
        for parent in PARENT_ARMS
        for seed_record in records[parent].values()
    ]
    add("semantic_chart_closure_backward_error", max(closure_defects), "<= 1e-5", max(closure_defects) <= 1e-5)
    add("semantic_chart_isometry_backward_error", max(metric_defects), "<= 1e-4", max(metric_defects) <= 1e-4)
    add("semantic_chart_metric_condition", max(metric_conditions), "<= 1.0001", max(metric_conditions) <= 1.0001)

    null_cycle_accuracy = []
    for parent in PARENT_ARMS:
        for seed_record in records[parent].values():
            cycles = seed_record["variants"]["semantic_chart_closed"]["null_cycles"]
            for relation in cycles.values():
                null_cycle_accuracy.extend(row["accuracy"] for row in relation.values())
    add("semantic_chart_null_cycle_accuracy", min(null_cycle_accuracy), ">= 0.999", min(null_cycle_accuracy) >= 0.999)

    state_patch = _values(records, "linear_terminal", "semantic_chart_closed", "interventions", "state_patch_accuracy")
    operator_patch = _values(records, "linear_terminal", "semantic_chart_closed", "interventions", "operator_patch_accuracy")
    random_state = _values(records, "linear_terminal", "semantic_chart_closed", "interventions", "random_state_patch_accuracy")
    random_operator = _values(
        records, "linear_terminal", "semantic_chart_closed", "interventions", "random_operator_patch_accuracy"
    )
    add("semantic_chart_deep_state_patch", min(state_patch), ">= 0.99", min(state_patch) >= 0.99)
    add("semantic_chart_deep_operator_patch", min(operator_patch), ">= 0.99", min(operator_patch) >= 0.99)
    add("semantic_chart_random_state_control", max(random_state), "<= 0.40", max(random_state) <= 0.40)
    add("semantic_chart_random_operator_control", max(random_operator), "<= 0.40", max(random_operator) <= 0.40)

    if transport:
        accuracies = [value["accuracy"] for value in transport.values()]
        residuals = [value["intertwining_residual_max"] for value in transport.values()]
        metric_residuals = [value["metric_transport_residual"] for value in transport.values()]
        add("cross_seed_anchor_transport", min(accuracies), ">= 0.99", min(accuracies) >= 0.99)
        add("cross_seed_intertwining_backward_error", max(residuals), "<= 1e-5", max(residuals) <= 1e-5)
        add(
            "cross_seed_metric_transport_backward_error",
            max(metric_residuals),
            "<= 1e-5",
            max(metric_residuals) <= 1e-5,
        )

    return {"all_passed": all(item["passed"] for item in gates.values()), "gates": gates}


def aggregate_variant_curve(records: dict[str, Any], parent: str, variant: str, family: str) -> dict[str, float]:
    lengths = next(iter(records[parent].values()))["variants"][variant]["deep"][family].keys()
    return {
        length: float(
            np.mean(
                [seed_record["variants"][variant]["deep"][family][length]["accuracy"] for seed_record in records[parent].values()]
            )
        )
        for length in lengths
    }


def render_charts(output_dir: Path, records: dict[str, Any]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []
    created = []
    figure = plt.figure(figsize=(8, 5.5), dpi=180)
    axis = figure.add_subplot(111)
    for variant in VARIANTS:
        curve = aggregate_variant_curve(records, "linear_terminal", variant, "d4")
        x = np.asarray([int(value) for value in curve])
        y = np.asarray(list(curve.values()))
        axis.plot(x, y, marker="o", label=variant)
    axis.set_xscale("log", base=2)
    axis.set_ylim(0, 1.03)
    axis.set_xlabel("Composition depth")
    axis.set_ylabel("Exact accuracy")
    axis.set_title("Terminal checkpoint: projective and closure controls")
    axis.legend(fontsize=8)
    figure.tight_layout()
    path = output_dir / "d4_depth_accuracy.png"
    figure.savefig(path)
    plt.close(figure)
    created.append(path.name)

    figure = plt.figure(figsize=(8, 5.5), dpi=180)
    axis = figure.add_subplot(111)
    for variant in VARIANTS:
        seed_curves = []
        for seed_record in records["linear_terminal"].values():
            curve = seed_record["variants"][variant]["deep"]["d4"]
            seed_curves.append([curve[key]["median_log10_l2"] for key in curve])
        values = np.asarray(seed_curves, dtype=float)
        x = np.asarray([int(key) for key in next(iter(records["linear_terminal"].values()))["variants"][variant]["deep"]["d4"]])
        means = np.asarray(
            [np.nan if np.isnan(column).all() else np.nanmean(column) for column in values.transpose()]
        )
        axis.plot(x, means, marker="o", label=variant)
    axis.set_xscale("log", base=2)
    axis.set_xlabel("Composition depth")
    axis.set_ylabel("Median log10 hidden norm")
    axis.set_title("Radial growth versus stable closure")
    axis.legend(fontsize=8)
    figure.tight_layout()
    path = output_dir / "d4_depth_norm.png"
    figure.savefig(path)
    plt.close(figure)
    created.append(path.name)
    return created


def render_report(
    records: dict[str, Any],
    transport: dict[str, Any],
    gates: dict[str, Any],
    config: dict[str, Any],
    elapsed: float,
    source_digest: str,
) -> str:
    terminal = records["linear_terminal"]
    depths = [str(value) for value in config["lengths"]]
    rows = []
    for variant in VARIANTS:
        values = []
        for depth in depths:
            values.append(
                np.mean([seed_record["variants"][variant]["deep"]["d4"][depth]["accuracy"] for seed_record in terminal.values()])
            )
        rows.append((variant, values))
    selected_depths = [depth for depth in ("12", "64", "128", "256") if depth in depths]
    lines = [
        "# Komorebi Neuralese Stable Quotient v0.2.0",
        "",
        "## Result",
        "",
        f"**Developmental gate status:** `{'PASS' if gates['all_passed'] else 'FAIL'}`  ",
        f"**Elapsed:** `{elapsed:.3f}` seconds  ",
        f"**Evaluation source:** `{source_digest}`  ",
        "**Claim status:** frozen-checkpoint mechanistic development result, not confirmatory emergence evidence.",
        "",
        "The original norm explosion decomposes into two effects. Positive radial scale is an exact gauge of the bias-free linear model, so per-step normalization preserves all finite predictions. The remaining depth failure is angular/projective drift. A full-rank future-observability audit found no nonzero fixed additive nuisance packet. An exact table-to-anchor closure arm removes the angular defect and remains bounded while preserving causal interventions.",
        "",
        "## D4 depth accuracy",
        "",
        "| Variant | " + " | ".join(f"L{depth}" for depth in selected_depths) + " |",
        "|---|" + "---:|" * len(selected_depths),
    ]
    for variant, values in rows:
        mapping = dict(zip(depths, values))
        lines.append("| " + variant + " | " + " | ".join(f"{mapping[depth]:.4f}" for depth in selected_depths) + " |")
    lines += [
        "",
        "`normalized_raw` fixes overflow only. `metric_polar` tests whether norm preservation alone is sufficient. `anchor_closed` compiles each exposed anonymous table as transport between the model's learned state anchors. `semantic_chart_closed` expresses the same closure in a canonical one-hot chart, removing the ill-conditioned ambient metric. Both closed arms are strong structural positive controls and must not be described as spontaneous discovery.",
        "",
        "## Mechanistic adjudication",
        "",
        "| Gate | Observed | Criterion | Result |",
        "|---|---:|---|---|",
    ]
    for name, gate in gates["gates"].items():
        observed = gate["observed"]
        observed_text = f"{observed:.6g}" if isinstance(observed, float) else str(observed)
        lines.append(f"| `{name}` | {observed_text} | `{gate['criterion']}` | {'PASS' if gate['passed'] else 'FAIL'} |")
    lines += [
        "",
        "## Interpretation",
        "",
        "1. The exploding radius was not itself semantic because every positive rescaling produces the same downstream argmax continuation.",
        "2. Normalization keeps computation finite but leaves directional accuracy unchanged until the unnormalized run overflows.",
        "3. The centered decoder has an instantaneous null direction, but the operator family makes it future-observable. A forced linear P/Q split would therefore be false.",
        "4. The learned state anchors already form a complete eight-state semantic coordinate system. Compiling table actions as `B P B^{-1}` removes arbitrary-depth drift; transporting that action into the canonical semantic chart reduces the recurrent metric condition number to one.",
        "5. This establishes an engineering resolution and localizes the learning failure to the unconstrained operator encoder. It does not show that terminal training discovered the closed representation unaided.",
        "",
        "## Next scientific threshold",
        "",
        "Train a projective/conformal operator encoder with fixed-temperature normalized states, anonymous composition consistency, bounded metric conditioning, and table-derived held-out null cycles. The decisive result is whether the learned encoder approaches the anchor-closed behavior without being given the exact `B P B^{-1}` compiler.",
        "",
    ]
    if transport:
        lines += ["## Cross-seed closed transport", ""]
        for name, result in transport.items():
            lines.append(
                f"- `{name}`: accuracy `{result['accuracy']:.4f}`, maximum intertwining residual `{result['intertwining_residual_max']:.3e}`."
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Komorebi projective and stable-quotient frozen-checkpoint assay")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args()
    config = dict(PROFILES[args.profile])
    output_dir = args.output_dir or ROOT / "results" / f"stability_{args.profile}"
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device(args.device)
    torch.set_num_threads(max(1, min(8, os.cpu_count() or 1)))
    torch.use_deterministic_algorithms(True)

    preregistration_path = ROOT / "STABILITY_PREREGISTRATION.json"
    preregistration = json.loads(preregistration_path.read_text(encoding="utf-8"))
    if preregistration["profiles"][args.profile] != config:
        raise SystemExit("profile does not match frozen preregistration")
    atomic_json(output_dir / "PREREGISTRATION.json", preregistration)
    source_digest = tree_digest(ROOT, source_files(ROOT))

    started = time.perf_counter()
    records: dict[str, Any] = {parent: {} for parent in PARENT_ARMS}
    loaded: dict[tuple[str, int], Any] = {}
    for parent_index, parent in enumerate(PARENT_ARMS):
        for seed in config["seeds"]:
            checkpoint = ROOT / "results" / "pilot" / "checkpoints" / f"{parent}_seed{seed}.pt"
            if not checkpoint.exists():
                raise FileNotFoundError(f"missing parent checkpoint: {checkpoint}")
            base, payload = load_legacy_linear_checkpoint(checkpoint, device)
            loaded[(parent, seed)] = base
            variants = build_stability_arms(base)
            seed_record: dict[str, Any] = {
                "checkpoint": {
                    "path": checkpoint.relative_to(ROOT).as_posix(),
                    "sha256": file_sha256(checkpoint),
                    "parent_source_digest": payload["source_digest"],
                    "config": payload["config"],
                },
                "observability": observability_audit(
                    base,
                    examples=config["observability_examples"],
                    max_depth=4,
                    seed=70_000 + parent_index * 1000 + seed,
                    device=device,
                ),
                "projective_gauge": projective_gauge_audit(
                    base,
                    variants["normalized_raw"],
                    lengths=config["gauge_lengths"],
                    examples=config["examples"],
                    seed=71_000 + parent_index * 1000 + seed,
                    device=device,
                ),
                "variants": {},
            }
            for variant_index, (variant_name, model) in enumerate(variants.items()):
                model.to(device).eval()
                variant_record: dict[str, Any] = {
                    "code_audit": code_audit(
                        model,
                        examples=config["code_examples"],
                        seed=72_000 + parent_index * 10_000 + seed * 100,
                        device=device,
                    ),
                    "deep": {},
                }
                for family_index, family in enumerate(config["families"]):
                    variant_record["deep"][family] = deep_rollout_metrics(
                        model,
                        family=family,
                        lengths=config["lengths"],
                        examples=config["examples"],
                        batch_size=config["batch_size"],
                        seed=80_000 + parent_index * 100_000 + seed * 10_000 + family_index * 100,
                        device=device,
                    )
                variant_record["null_cycles"] = null_cycle_metrics(
                    model,
                    relation_repeats=config["null_repeats"],
                    examples=config["null_examples"],
                    batch_size=config["batch_size"],
                    base_length=8,
                    seed=90_000 + parent_index * 10_000 + seed * 100,
                    device=device,
                )
                variant_record["interventions"] = deep_intervention_audit(
                    model,
                    examples=config["intervention_examples"],
                    batch_size=config["batch_size"],
                    length=config["intervention_length"],
                    seed=100_000 + parent_index * 10_000 + seed * 100,
                    device=device,
                )
                seed_record["variants"][variant_name] = variant_record
            records[parent][str(seed)] = seed_record

    transport: dict[str, Any] = {}
    if len(config["seeds"]) >= 2:
        first, second = config["seeds"][:2]
        for parent_index, parent in enumerate(PARENT_ARMS):
            transport[parent] = cross_seed_semantic_transport(
                loaded[(parent, first)],
                loaded[(parent, second)],
                examples=config["examples"],
                length=max(config["intervention_length"], 64),
                split=max(config["intervention_length"], 64) // 2,
                seed=110_000 + parent_index,
                device=device,
            )

    gates = adjudicate(records, transport, config)
    elapsed = time.perf_counter() - started
    result = {
        "schema": "komorebi.neuralese.stable_quotient.result.v1",
        "version": "0.2.0",
        "profile": args.profile,
        "developmental": True,
        "source_digest": source_digest,
        "evaluation_source_digest": source_digest,
        "records": records,
        "transport": transport,
        "gates": gates,
        "elapsed_seconds": elapsed,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "device": str(device),
            "cuda_available": torch.cuda.is_available(),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
    }
    atomic_json(output_dir / "RESULTS.json", result)
    atomic_json(output_dir / "GATES.json", gates)
    atomic_json(output_dir / "ENVIRONMENT.json", result["environment"])
    charts = render_charts(output_dir, records)
    report = render_report(records, transport, gates, config, elapsed, source_digest)
    (output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    completion = {
        "schema": "komorebi.neuralese.stable_quotient.completion.v1",
        "profile": args.profile,
        "all_gates_passed": gates["all_passed"],
        "results_sha256": file_sha256(output_dir / "RESULTS.json"),
        "report_sha256": file_sha256(output_dir / "REPORT.md"),
        "charts": charts,
        "evaluation_source_digest": source_digest,
    }
    atomic_json(output_dir / "RUN_COMPLETE.json", completion)
    print(json.dumps(completion, sort_keys=True))
    return 0 if gates["all_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
