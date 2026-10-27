#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import audit_algebra
from komorebi_neuralese.evaluate import EvaluationConfig, full_evaluation
from komorebi_neuralese.models import RecurrentOperatorModel, build_model
from komorebi_neuralese.reporting import (
    aggregate_arms,
    arm_summary,
    render_markdown_report,
    source_files,
    tree_digest,
    write_json,
    write_summary_csv,
)
from komorebi_neuralese.train import TrainConfig, config_dict, train_arm
from komorebi_neuralese.transport import cross_seed_transport


ARM_DEFINITIONS = {
    "linear_terminal": {"model": "linear_hyper", "regime": "terminal", "lr": 1e-3, "clip": 1.0},
    "linear_relation": {"model": "linear_hyper", "regime": "relation", "lr": 1e-3, "clip": 1.0},
    "gru_terminal": {"model": "gru", "regime": "terminal", "lr": 2e-3, "clip": 5.0},
    "gru_intermediate": {"model": "gru", "regime": "intermediate", "lr": 2e-3, "clip": 5.0},
    "one_shot_terminal": {"model": "one_shot", "regime": "terminal", "lr": 2e-3, "clip": 5.0},
    "token_only_terminal": {"model": "token_only", "regime": "terminal", "lr": 2e-3, "clip": 5.0},
}

PROFILES = {
    "smoke": {
        "seeds": [0],
        "steps": {name: 120 for name in ARM_DEFINITIONS},
        "batch_size": 64,
        "examples_per_length": 256,
        "intervention_examples": 256,
        "eval_batch_size": 128,
    },
    "pilot": {
        "seeds": [0, 1],
        "steps": {
            "linear_terminal": 1600,
            "linear_relation": 1600,
            "gru_terminal": 2200,
            "gru_intermediate": 1800,
            "one_shot_terminal": 2200,
            "token_only_terminal": 1200,
        },
        "batch_size": 256,
        "examples_per_length": 2048,
        "intervention_examples": 2048,
        "eval_batch_size": 512,
    },
    "confirmatory": {
        "seeds": list(range(10)),
        "steps": {
            "linear_terminal": 5000,
            "linear_relation": 5000,
            "gru_terminal": 6000,
            "gru_intermediate": 5000,
            "one_shot_terminal": 6000,
            "token_only_terminal": 3000,
        },
        "batch_size": 256,
        "examples_per_length": 8192,
        "intervention_examples": 8192,
        "eval_batch_size": 1024,
    },
}


def parse_int_list(value: str | None, default: list[int]) -> list[int]:
    if value is None:
        return list(default)
    values = [int(item.strip()) for item in value.split(",") if item.strip()]
    if not values:
        raise ValueError("seed list is empty")
    return values


def parse_name_list(value: str | None, default: list[str]) -> list[str]:
    if value is None:
        return list(default)
    values = [item.strip() for item in value.split(",") if item.strip()]
    unknown = sorted(set(values) - set(ARM_DEFINITIONS))
    if unknown:
        raise ValueError(f"unknown arms: {unknown}")
    return values


def environment_record(device: torch.device, threads: int) -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "device": str(device),
        "torch_threads": threads,
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda,
    }


def extract_mean(aggregate: dict[str, Any], arm: str, metric: str) -> float:
    return float(aggregate[arm][metric]["mean"])


def development_gates(aggregate: dict[str, Any], transport: dict[str, Any] | None) -> dict[str, Any]:
    gates: dict[str, Any] = {}

    def ge(name: str, observed: float, threshold: float) -> None:
        gates[name] = {
            "observed": observed,
            "criterion": f">= {threshold}",
            "passed": bool(observed >= threshold),
        }

    def le(name: str, observed: float, threshold: float) -> None:
        gates[name] = {
            "observed": observed,
            "criterion": f"<= {threshold}",
            "passed": bool(observed <= threshold),
        }

    if "linear_terminal" in aggregate:
        ge("linear_terminal_d4_id", extract_mean(aggregate, "linear_terminal", "d4_id_mean"), 0.95)
        ge("linear_terminal_d4_long", extract_mean(aggregate, "linear_terminal", "d4_long_mean"), 0.70)
        ge("linear_terminal_c8_id", extract_mean(aggregate, "linear_terminal", "c8_id_mean"), 0.80)
        ge("linear_terminal_state_patch", extract_mean(aggregate, "linear_terminal", "state_patch_accuracy"), 0.90)
        ge("linear_terminal_operator_patch", extract_mean(aggregate, "linear_terminal", "operator_patch_accuracy"), 0.90)
        le(
            "linear_terminal_random_state_control",
            extract_mean(aggregate, "linear_terminal", "random_state_patch_accuracy"),
            0.40,
        )
        le(
            "linear_terminal_zero_state_lesion",
            extract_mean(aggregate, "linear_terminal", "zero_state_lesion_original_accuracy"),
            0.40,
        )
        le(
            "linear_terminal_random_operator_control",
            extract_mean(aggregate, "linear_terminal", "random_operator_patch_accuracy"),
            0.40,
        )
        state_margin = extract_mean(aggregate, "linear_terminal", "state_patch_accuracy") - extract_mean(
            aggregate, "linear_terminal", "random_state_patch_accuracy"
        )
        operator_margin = extract_mean(aggregate, "linear_terminal", "operator_patch_accuracy") - extract_mean(
            aggregate, "linear_terminal", "random_operator_patch_accuracy"
        )
        ge("linear_terminal_state_patch_margin", state_margin, 0.50)
        ge("linear_terminal_operator_patch_margin", operator_margin, 0.50)
    if "token_only_terminal" in aggregate:
        le("token_only_d4_id", extract_mean(aggregate, "token_only_terminal", "d4_id_mean"), 0.30)
    if "linear_terminal" in aggregate and "gru_terminal" in aggregate:
        advantage = extract_mean(aggregate, "linear_terminal", "d4_long_mean") - extract_mean(
            aggregate, "gru_terminal", "d4_long_mean"
        )
        ge("linear_over_gru_long_advantage", advantage, 0.10)
    if transport is not None:
        ge("cross_seed_transport_patch", float(transport["aligned_state_patch_accuracy"]), 0.70)
        le("cross_seed_random_map_control", float(transport["random_map_state_patch_accuracy"]), 0.40)
    return gates


def plot_results(output_dir: Path, records: dict[str, list[dict[str, Any]]]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []

    created: list[str] = []
    lengths = (1, 2, 3, 4, 6, 8, 10, 12)
    figure = plt.figure(figsize=(8, 6), dpi=180)
    axis = figure.add_subplot(111)
    for arm_name, arm_records in records.items():
        values = [
            np.mean([record["evaluation"]["accuracy"]["d4"][str(length)] for record in arm_records])
            for length in lengths
        ]
        axis.plot(lengths, values, marker="o", label=arm_name)
    axis.axvline(4, linestyle="--", linewidth=1)
    axis.set_xlabel("Composition length")
    axis.set_ylabel("Exact accuracy")
    axis.set_ylim(0.0, 1.03)
    axis.set_title("D4 conjugation generalization")
    axis.legend(fontsize=7)
    figure.tight_layout()
    path = output_dir / "accuracy_by_length.png"
    figure.savefig(path)
    plt.close(figure)
    created.append(path.name)

    causal_arms = [name for name, values in records.items() if values[0]["evaluation"]["interventions"].get("available")]
    if causal_arms:
        labels = []
        state_values = []
        operator_values = []
        random_values = []
        for arm_name in causal_arms:
            labels.append(arm_name)
            state_values.append(
                np.mean([record["evaluation"]["interventions"]["state_patch_accuracy"] for record in records[arm_name]])
            )
            operator_values.append(
                np.mean([record["evaluation"]["interventions"]["operator_patch_accuracy"] for record in records[arm_name]])
            )
            random_values.append(
                np.mean(
                    [record["evaluation"]["interventions"]["random_operator_patch_accuracy"] for record in records[arm_name]]
                )
            )
        x = np.arange(len(labels))
        width = 0.25
        figure = plt.figure(figsize=(9, 6), dpi=180)
        axis = figure.add_subplot(111)
        axis.bar(x - width, state_values, width, label="state patch")
        axis.bar(x, operator_values, width, label="operator patch")
        axis.bar(x + width, random_values, width, label="random operator control")
        axis.set_xticks(x)
        axis.set_xticklabels(labels, rotation=20, ha="right")
        axis.set_ylabel("Exact counterfactual accuracy")
        axis.set_ylim(0.0, 1.03)
        axis.set_title("Causal intervention assay")
        axis.legend(fontsize=8)
        figure.tight_layout()
        path = output_dir / "causal_interventions.png"
        figure.savefig(path)
        plt.close(figure)
        created.append(path.name)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Komorebi Neuralese operator-workspace assay")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--seeds", default=None, help="comma-separated seed override")
    parser.add_argument("--arms", default=None, help="comma-separated arm override")
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--threads", type=int, default=min(4, os.cpu_count() or 1))
    args = parser.parse_args()

    profile = PROFILES[args.profile]
    seeds = parse_int_list(args.seeds, profile["seeds"])
    arms = parse_name_list(args.arms, list(ARM_DEFINITIONS))
    if args.device == "auto":
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(args.device)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    torch.manual_seed(0)
    np.random.seed(0)

    output_dir = args.output_dir or (ROOT / "results" / args.profile)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "arms").mkdir(parents=True, exist_ok=True)
    (output_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    source_digest = tree_digest(ROOT, source_files(ROOT))
    evaluation_config = EvaluationConfig(
        examples_per_length=int(profile["examples_per_length"]),
        intervention_examples=int(profile["intervention_examples"]),
        batch_size=int(profile["eval_batch_size"]),
    )
    preregistration = {
        "schema": "komorebi.neuralese.preregistration.v1",
        "profile": args.profile,
        "source_digest": source_digest,
        "seeds": seeds,
        "arms": arms,
        "train_family": "d4_regular_action_randomly_conjugated_by_S8",
        "train_lengths": [1, 2, 3, 4],
        "heldout_lengths": [6, 8, 10, 12],
        "heldout_operator_families": ["c8", "mixed_cycle", "random"],
        "primary_evidence": [
            "exact terminal accuracy",
            "relation endpoints",
            "equivalent-path convergence",
            "causal state transplant",
            "causal internal operator-code replacement",
            "matched random intervention controls",
            "cross-seed affine transport",
        ],
        "development_gate_thresholds": {
            "linear_terminal_d4_id": 0.95,
            "linear_terminal_d4_long": 0.70,
            "linear_terminal_c8_id": 0.80,
            "linear_terminal_state_patch": 0.90,
            "linear_terminal_operator_patch": 0.90,
            "linear_terminal_random_state_control": 0.40,
            "linear_terminal_zero_state_lesion": 0.40,
            "linear_terminal_random_operator_control": 0.40,
            "linear_terminal_state_patch_margin": 0.50,
            "linear_terminal_operator_patch_margin": 0.50,
            "token_only_d4_id": 0.30,
            "linear_over_gru_long_advantage": 0.10,
            "cross_seed_transport_patch": 0.70,
            "cross_seed_random_map_control": 0.40,
        },
        "threshold_provenance": "developmental thresholds informed by the v0.1.0 scaffold; not outcome-independent confirmation",
        "claim_boundary": "developmental finite-state causal-operator assay; not a confirmatory Neuralese claim",
    }
    write_json(output_dir / "PREREGISTRATION.json", preregistration)
    write_json(output_dir / "ENVIRONMENT.json", environment_record(device, args.threads))
    write_json(output_dir / "ALGEBRA_AUDIT.json", asdict(audit_algebra("d4")))

    records: dict[str, list[dict[str, Any]]] = {arm: [] for arm in arms}
    trained_models: dict[str, dict[int, torch.nn.Module]] = {arm: {} for arm in arms}

    for arm_name in arms:
        definition = ARM_DEFINITIONS[arm_name]
        for seed in seeds:
            # Seed before construction so initialization is independent of arm order and subset selection.
            torch.manual_seed(seed)
            np.random.seed(seed)
            model = build_model(definition["model"], max_length=max(evaluation_config.lengths))
            config = TrainConfig(
                model_name=definition["model"],
                regime=definition["regime"],
                seed=seed,
                steps=int(profile["steps"][arm_name]),
                batch_size=int(profile["batch_size"]),
                train_max_length=4,
                max_eval_length=max(evaluation_config.lengths),
                learning_rate=float(definition["lr"]),
                grad_clip=float(definition["clip"]),
                device=str(device),
            )
            print(f"TRAIN arm={arm_name} seed={seed} steps={config.steps}", flush=True)
            trained = train_arm(model, config)
            print(f"EVAL arm={arm_name} seed={seed}", flush=True)
            evaluation = full_evaluation(
                trained.model,
                evaluation_config,
                seed=50_000 + 100 * seed,
                device=device,
            )
            record = {
                "schema": "komorebi.neuralese.arm_result.v1",
                "arm": arm_name,
                "source_digest": source_digest,
                "config": config_dict(config),
                "training": {
                    "elapsed_seconds": trained.elapsed_seconds,
                    "final_loss": trained.final_loss,
                    "parameter_count": trained.parameter_count,
                    "trajectory": trained.trajectory,
                },
                "evaluation": evaluation,
                "summary": arm_summary({"evaluation": evaluation}),
            }
            records[arm_name].append(record)
            trained_models[arm_name][seed] = trained.model
            write_json(output_dir / "arms" / f"{arm_name}_seed{seed}.json", record)
            torch.save(
                {
                    "arm": arm_name,
                    "source_digest": source_digest,
                    "config": config_dict(config),
                    "state_dict": trained.model.state_dict(),
                },
                output_dir / "checkpoints" / f"{arm_name}_seed{seed}.pt",
            )

    aggregate = aggregate_arms(records)
    transport_metrics = None
    if "linear_terminal" in trained_models and len(seeds) >= 2:
        source_seed, target_seed = seeds[0], seeds[1]
        source_model = trained_models["linear_terminal"][source_seed]
        target_model = trained_models["linear_terminal"][target_seed]
        if isinstance(source_model, RecurrentOperatorModel) and isinstance(target_model, RecurrentOperatorModel):
            print(f"TRANSPORT arm=linear_terminal source={source_seed} target={target_seed}", flush=True)
            transport_metrics, transport = cross_seed_transport(
                source_model,
                target_model,
                seed=80_000,
                anchor_examples=int(profile["intervention_examples"]),
                test_examples=int(profile["intervention_examples"]),
                batch_size=int(profile["eval_batch_size"]),
                device=device,
            )
            transport_metrics.update({"source_seed": source_seed, "target_seed": target_seed})
            write_json(output_dir / "TRANSPORT_RESULT.json", transport_metrics)
            np.savez_compressed(
                output_dir / "TRANSPORT_MAP.npz",
                weight=transport.weight.detach().cpu().numpy(),
                bias=transport.bias.detach().cpu().numpy(),
                source_mean=transport.source_mean.detach().cpu().numpy(),
                target_mean=transport.target_mean.detach().cpu().numpy(),
            )

    gates = development_gates(aggregate, transport_metrics)
    write_json(output_dir / "AGGREGATE_RESULTS.json", aggregate)
    write_json(output_dir / "GATE_RESULTS.json", gates)
    write_summary_csv(output_dir / "SUMMARY.csv", records)

    receipts_path = output_dir / "AUDIT_RECEIPTS.jsonl"
    with receipts_path.open("w", encoding="utf-8") as handle:
        for arm_name, arm_records in records.items():
            for record in arm_records:
                receipt = {
                    "schema": "komorebi.neuralese.audit_receipt.v1",
                    "source_digest": source_digest,
                    "arm": arm_name,
                    "seed": record["config"]["seed"],
                    "summary": record["summary"],
                }
                handle.write(json.dumps(receipt, sort_keys=True) + "\n")
        if transport_metrics is not None:
            handle.write(
                json.dumps(
                    {
                        "schema": "komorebi.neuralese.transport_receipt.v1",
                        "source_digest": source_digest,
                        "metrics": transport_metrics,
                    },
                    sort_keys=True,
                )
                + "\n"
            )

    report = render_markdown_report(args.profile, source_digest, aggregate, gates, transport_metrics)
    (output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    figures = plot_results(output_dir, records)
    completion = {
        "schema": "komorebi.neuralese.run_complete.v1",
        "profile": args.profile,
        "source_digest": source_digest,
        "arm_count": len(arms),
        "seed_count": len(seeds),
        "all_development_gates_passed": all(gate["passed"] for gate in gates.values()),
        "figures": figures,
    }
    write_json(output_dir / "RUN_COMPLETE.json", completion)
    print(json.dumps(completion, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
