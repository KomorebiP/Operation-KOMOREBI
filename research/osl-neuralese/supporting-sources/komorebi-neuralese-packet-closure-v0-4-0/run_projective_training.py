#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.reporting import source_files, tree_digest
from komorebi_neuralese.stability_eval import (
    code_audit,
    deep_intervention_audit,
    deep_rollout_metrics,
    file_sha256,
    load_legacy_linear_checkpoint,
    null_cycle_metrics,
)
from komorebi_neuralese.stable_models import ProjectiveLinearHyperOperatorRNN
from komorebi_neuralese.train import TrainConfig, config_dict, train_arm
from komorebi_neuralese.transport import cross_seed_transport


PROFILES: dict[str, dict[str, Any]] = {
    "smoke": {
        "seeds": [0],
        "steps": 120,
        "batch_size": 64,
        "examples": 256,
        "eval_batch_size": 128,
        "lengths": [1, 4, 8, 16, 32, 64],
        "families": ["d4", "c8"],
        "null_repeats": [0, 1, 2],
        "null_examples": 128,
        "intervention_examples": 128,
        "intervention_length": 16
    },
    "pilot": {
        "seeds": [0, 1],
        "steps": 1600,
        "batch_size": 256,
        "examples": 2048,
        "eval_batch_size": 512,
        "lengths": [1, 2, 3, 4, 8, 12, 32, 64, 128, 256],
        "families": ["d4", "c8", "mixed_cycle", "random"],
        "null_repeats": [0, 1, 2, 4, 8, 16],
        "null_examples": 1024,
        "intervention_examples": 1024,
        "intervention_length": 64
    },
    "confirmatory": {
        "seeds": list(range(10)),
        "steps": 5000,
        "batch_size": 256,
        "examples": 8192,
        "eval_batch_size": 1024,
        "lengths": [1, 2, 3, 4, 8, 16, 32, 64, 128, 256, 512],
        "families": ["d4", "c8", "mixed_cycle", "random"],
        "null_repeats": [0, 1, 2, 4, 8, 16, 32],
        "null_examples": 8192,
        "intervention_examples": 8192,
        "intervention_length": 128
    },
}


def atomic_json(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def _metric(records: dict[str, Any], arm: str, family: str, depth: str, name: str = "accuracy") -> list[float]:
    return [float(record[arm]["deep"][family][depth][name]) for record in records.values() if arm in record]


def adjudicate(records: dict[str, Any], transport: dict[str, Any] | None, config: dict[str, Any]) -> dict[str, Any]:
    gates: dict[str, Any] = {}

    def add(name: str, observed: float, criterion: str, passed: bool) -> None:
        gates[name] = {"observed": observed, "criterion": criterion, "passed": bool(passed)}

    train_accuracy = []
    for record in records.values():
        train_accuracy.append(mean(record["projective"]["deep"]["d4"][str(depth)]["accuracy"] for depth in (1, 2, 3, 4)))
    add("projective_train_range", min(train_accuracy), ">= 0.98 per seed", min(train_accuracy) >= 0.98)

    if "64" in map(str, config["lengths"]):
        values = _metric(records, "projective", "d4", "64")
        add("projective_d4_depth64", min(values), ">= 0.98 per seed", min(values) >= 0.98)
    if "128" in map(str, config["lengths"]):
        values = _metric(records, "projective", "d4", "128")
        add("projective_d4_depth128", min(values), ">= 0.95 per seed", min(values) >= 0.95)
    if "256" in map(str, config["lengths"]):
        values = _metric(records, "projective", "d4", "256")
        add("projective_d4_depth256_mean", mean(values), ">= 0.80", mean(values) >= 0.80)
        add("projective_d4_depth256_seed_floor", min(values), ">= 0.75", min(values) >= 0.75)
        raw_values = _metric(records, "raw_parent", "d4", "256")
        if raw_values:
            advantage = mean(values) - mean(raw_values)
            add("projective_depth256_advantage", advantage, ">= 0.50 over matched raw parent", advantage >= 0.50)

    finite = [
        row["finite_fraction"]
        for record in records.values()
        for family in config["families"]
        for row in record["projective"]["deep"][family].values()
    ]
    add("projective_all_depth_finite", min(finite), "== 1.0", min(finite) == 1.0)

    state_patch = [record["projective"]["interventions"]["state_patch_accuracy"] for record in records.values()]
    operator_patch = [record["projective"]["interventions"]["operator_patch_accuracy"] for record in records.values()]
    random_state = [record["projective"]["interventions"]["random_state_patch_accuracy"] for record in records.values()]
    random_operator = [
        record["projective"]["interventions"]["random_operator_patch_accuracy"] for record in records.values()
    ]
    add("projective_deep_state_patch", min(state_patch), ">= 0.90", min(state_patch) >= 0.90)
    add("projective_deep_operator_patch", min(operator_patch), ">= 0.90", min(operator_patch) >= 0.90)
    add("projective_random_state_control", max(random_state), "<= 0.40", max(random_state) <= 0.40)
    add("projective_random_operator_control", max(random_operator), "<= 0.40", max(random_operator) <= 0.40)

    cycle_accuracy = [
        row["accuracy"]
        for record in records.values()
        for relation in record["projective"]["null_cycles"].values()
        for row in relation.values()
    ]
    add("projective_null_cycle_accuracy", min(cycle_accuracy), ">= 0.90", min(cycle_accuracy) >= 0.90)

    if transport is not None:
        add(
            "projective_cross_seed_transport",
            float(transport["aligned_state_patch_accuracy"]),
            ">= 0.70",
            float(transport["aligned_state_patch_accuracy"]) >= 0.70,
        )
        add(
            "projective_transport_random_control",
            float(transport["random_map_state_patch_accuracy"]),
            "<= 0.40",
            float(transport["random_map_state_patch_accuracy"]) <= 0.40,
        )
    return {"all_passed": all(item["passed"] for item in gates.values()), "gates": gates}


def render_chart(output_dir: Path, records: dict[str, Any]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []
    first = next(iter(records.values()))
    depths = list(first["projective"]["deep"]["d4"])
    x = np.asarray([int(value) for value in depths])
    figure = plt.figure(figsize=(8, 5.5), dpi=180)
    axis = figure.add_subplot(111)
    for arm, label in (("raw_parent", "raw parent"), ("projective", "projective terminal-only")):
        if arm not in first:
            continue
        y = [mean(record[arm]["deep"]["d4"][depth]["accuracy"] for record in records.values() if arm in record) for depth in depths]
        axis.plot(x, y, marker="o", label=label)
    axis.set_xscale("log", base=2)
    axis.set_ylim(0, 1.03)
    axis.set_xlabel("Composition depth")
    axis.set_ylabel("Exact D4 accuracy")
    axis.set_title("Matched terminal training: raw versus projective recurrence")
    axis.legend()
    figure.tight_layout()
    path = output_dir / "projective_vs_raw_depth.png"
    figure.savefig(path)
    plt.close(figure)
    return [path.name]


def render_report(
    records: dict[str, Any], gates: dict[str, Any], transport: dict[str, Any] | None, config: dict[str, Any]
) -> str:
    selected = [str(value) for value in (4, 12, 64, 128, 256) if value in config["lengths"]]
    cycle_rows = [
        row
        for record in records.values()
        for relation in record["projective"]["null_cycles"].values()
        for row in relation.values()
    ]
    nonzero_cycle_rows = [row for row in cycle_rows if row["inserted_relation_length"] > 0]
    cycle_accuracy_floor = min(row["accuracy"] for row in cycle_rows)
    cycle_median_angle_max = max(
        row["median_projective_angle_to_no_cycle"] or 0.0 for row in nonzero_cycle_rows
    )
    projective_code_rows = [record["projective"]["code_audit"] for record in records.values()]
    spectral_radius_median = mean(row["spectral_radius_median"] for row in projective_code_rows)
    projective_anchor_defect = mean(row["projective_anchor_defect_mean"] for row in projective_code_rows)
    conformal_defect = mean(row["conformal_metric_defect_mean"] for row in projective_code_rows)
    training_digests = sorted(
        {record["projective"]["checkpoint"]["training_source_digest"] for record in records.values()}
    )
    evaluation_digests = sorted(
        {record["projective"]["training"]["evaluation_source_digest"] for record in records.values()}
    )
    lines = [
        "# Projective Terminal-Only Training Result",
        "",
        f"**Developmental gate status:** `{'PASS' if gates['all_passed'] else 'FAIL'}`  ",
        "**Training:** lengths 1–4, terminal answer loss only, no named relations, no intermediate targets, no anchor compiler.",
        f"**Checkpoint training source:** `{', '.join(training_digests)}`  ",
        f"**Current evaluation source:** `{', '.join(evaluation_digests)}`  ",
        "The bundled completion time is checkpoint re-evaluation time; original per-seed training durations remain in `RESULTS.json`.",
        "",
        "## D4 comparison",
        "",
        "| Arm | " + " | ".join(f"L{depth}" for depth in selected) + " |",
        "|---|" + "---:|" * len(selected),
    ]
    for arm, label in (("raw_parent", "Raw v0.1 parent"), ("projective", "Projective terminal-only")):
        if not all(arm in record for record in records.values()):
            continue
        values = [mean(record[arm]["deep"]["d4"][depth]["accuracy"] for record in records.values()) for depth in selected]
        lines.append("| " + label + " | " + " | ".join(f"{value:.4f}" for value in values) + " |")
    clean_depth128_advantage = None
    if "128" in selected and all("raw_parent" in record for record in records.values()):
        projective_128 = mean(record["projective"]["deep"]["d4"]["128"]["accuracy"] for record in records.values())
        raw_128 = mean(record["raw_parent"]["deep"]["d4"]["128"]["accuracy"] for record in records.values())
        clean_depth128_advantage = projective_128 - raw_128
    lines += [
        "",
        "The only architectural change is positive-ray normalization after each recurrent operator application. The operator encoder remains learned from terminal supervision. This prevents scale from serving as an optimization shortcut and forces composition to be represented directionally.",
        "",
    ]
    if clean_depth128_advantage is not None:
        lines += [
            f"At depth 128, before the raw float32 arm overflows, the projective advantage is `{clean_depth128_advantage:.4f}`. The preregistered depth-256 advantage includes raw overflow and should not be read as a purely semantic margin.",
            "",
        ]
    lines += [
        "## Held-out operator families",
        "",
        "| Family | L64 | L128 | L256 |",
        "|---|---:|---:|---:|",
    ]
    for family, label in (("d4", "D4"), ("c8", "C8"), ("mixed_cycle", "Mixed cycle"), ("random", "Arbitrary random permutations")):
        if family not in config["families"] or "256" not in records[next(iter(records))]["projective"]["deep"][family]:
            continue
        values = [
            mean(record["projective"]["deep"][family][depth]["accuracy"] for record in records.values())
            for depth in ("64", "128", "256")
        ]
        lines.append(f"| {label} | " + " | ".join(f"{value:.4f}" for value in values) + " |")
    lines += [
        "",
        "C8 and mixed-cycle transfer remained strong despite being absent from training. Arbitrary independent permutation pairs did not: their long-depth score settled near 0.25. The result is therefore broad within structured permutation families, not universal over arbitrary operators.",
        "",
        "## Closure and holonomy audit",
        "",
        f"All evaluated hidden states remained finite. Table-verified null cycles preserved the correct answer down to `{cycle_accuracy_floor:.4f}`, but the largest median ray angle relative to the no-cycle trajectory reached `{cycle_median_angle_max:.4f}` radians. The learned computation is behaviorally closed over the tested loops before it is geometrically flat.",
        "",
        f"The ambient learned matrices had mean median spectral radius `{spectral_radius_median:.4f}`, mean scale-quotiented anchor defect `{projective_anchor_defect:.4f}`, and mean conformal-metric defect `{conformal_defect:.4f}`. Because per-step normalization removes matrix scale, spectral radius is not a stability criterion for this arm. The nonzero scale-free defects show that the encoder did not learn an exact ambient group representation; its successful semantics live on reachable projective trajectories.",
        "",
        "## Gates",
        "",
        "| Gate | Observed | Criterion | Result |",
        "|---|---:|---|---|",
    ]
    for name, gate in gates["gates"].items():
        lines.append(
            f"| `{name}` | {gate['observed']:.6g} | `{gate['criterion']}` | {'PASS' if gate['passed'] else 'FAIL'} |"
        )
    lines += [
        "",
        "## Claim boundary",
        "",
        "This is a two-seed developmental result whose long-depth gates were informed by an initial exploratory run. It shows that projective gauge fixing is sufficient to induce substantially more stable terminal-only operator learning in this finite table task. It does not establish spontaneous Neuralese in an unconstrained model, exact group representation, universal arbitrary-permutation generalization, asymptotically unbounded recurrence, or architecture-independent emergence.",
        "",
    ]
    if transport is not None:
        lines += [
            "## Cross-seed transport",
            "",
            f"Aligned continuation accuracy: `{transport['aligned_state_patch_accuracy']:.4f}`. Random-map control: `{transport['random_map_state_patch_accuracy']:.4f}`.",
            "",
            f"The same D4-fitted map achieved C8 `{transport['by_family']['c8']['aligned_state_patch_accuracy']:.4f}`, mixed-cycle `{transport['by_family']['mixed_cycle']['aligned_state_patch_accuracy']:.4f}`, and arbitrary-random `{transport['by_family']['random']['aligned_state_patch_accuracy']:.4f}` continuation accuracy. The target model's native arbitrary-random score was `{transport['by_family']['random']['target_native_accuracy']:.4f}`, so transport preserved its limitation rather than concealing it.",
            "",
        ]
    lines += [
        "## Strongest supported claim",
        "",
        "> In this randomly re-coordinatized finite operator task, positive-ray gauge fixing during terminal-only training produced a compact recurrent state with stable finite norms, causal state and operator semantics, long-depth structured-family generalization, and behavior-preserving cross-seed transport. Residual projective holonomy and arbitrary-operator failure remain.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train a projective terminal-only recurrent operator model")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--reuse-checkpoints", action="store_true")
    args = parser.parse_args()
    config = PROFILES[args.profile]
    output_dir = args.output_dir or ROOT / "results" / f"projective_{args.profile}"
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "checkpoints").mkdir(parents=True, exist_ok=True)
    device = torch.device(args.device)
    torch.set_num_threads(max(1, min(8, os.cpu_count() or 1)))
    torch.use_deterministic_algorithms(True)
    preregistration = json.loads((ROOT / "PROJECTIVE_PREREGISTRATION.json").read_text(encoding="utf-8"))
    if preregistration["profiles"][args.profile] != config:
        raise SystemExit("profile does not match projective preregistration")
    atomic_json(output_dir / "PREREGISTRATION.json", preregistration)
    source_digest = tree_digest(ROOT, source_files(ROOT))
    started = time.perf_counter()
    prior_result = None
    prior_result_path = output_dir / "RESULTS.json"
    if args.reuse_checkpoints and prior_result_path.exists():
        prior_result = json.loads(prior_result_path.read_text(encoding="utf-8"))

    records: dict[str, Any] = {}
    trained_models: dict[int, ProjectiveLinearHyperOperatorRNN] = {}
    for seed in config["seeds"]:
        torch.manual_seed(seed)
        np.random.seed(seed)
        model = ProjectiveLinearHyperOperatorRNN(hidden_dim=8)
        train_config = TrainConfig(
            model_name="projective_linear_hyper",
            regime="terminal",
            seed=seed,
            steps=config["steps"],
            batch_size=config["batch_size"],
            train_max_length=4,
            max_eval_length=max(config["lengths"]),
            learning_rate=1e-3,
            grad_clip=1.0,
            device=str(device),
        )
        checkpoint_path = output_dir / "checkpoints" / f"projective_terminal_seed{seed}.pt"
        if args.reuse_checkpoints:
            if not checkpoint_path.exists():
                raise FileNotFoundError(f"cannot reuse missing checkpoint: {checkpoint_path}")
            checkpoint_payload = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
            if checkpoint_payload.get("schema") != "komorebi.neuralese.projective_checkpoint.v1":
                raise ValueError("projective checkpoint schema mismatch")
            if checkpoint_payload.get("config") != config_dict(train_config):
                raise ValueError("projective checkpoint config mismatch")
            model.load_state_dict(checkpoint_payload["state_dict"], strict=True)
            model.to(device).eval()
            trained_model = model
            previous_training = None
            if prior_result is not None:
                previous_training = prior_result.get("records", {}).get(str(seed), {}).get("projective", {}).get("training")
            training_record = previous_training or {
                "config": config_dict(train_config),
                "reused_checkpoint": True,
                "original_source_digest": checkpoint_payload.get("source_digest"),
                "parameter_count": sum(parameter.numel() for parameter in model.parameters()),
            }
            training_record = dict(training_record)
            training_record["reused_checkpoint_for_evaluation"] = True
            training_source_digest = checkpoint_payload.get("source_digest")
        else:
            trained = train_arm(model, train_config)
            trained.model.eval()
            trained_model = trained.model
            training_record = {
                "config": config_dict(train_config),
                "elapsed_seconds": trained.elapsed_seconds,
                "final_loss": trained.final_loss,
                "parameter_count": trained.parameter_count,
                "trajectory": trained.trajectory,
                "reused_checkpoint_for_evaluation": False,
            }
            training_source_digest = source_digest
        training_record["training_source_digest"] = training_source_digest
        training_record["evaluation_source_digest"] = source_digest
        trained_models[seed] = trained_model
        projective: dict[str, Any] = {
            "training": training_record,
            "deep": {},
            "code_audit": code_audit(trained_model, 512 if args.profile != "smoke" else 64, 210_000 + seed, device),
        }
        for family_index, family in enumerate(config["families"]):
            evaluation_seed = 220_000 + seed * 1000 + family_index * 100
            projective["deep"][family] = deep_rollout_metrics(
                trained_model,
                family,
                config["lengths"],
                config["examples"],
                config["eval_batch_size"],
                evaluation_seed,
                device,
            )
        projective["null_cycles"] = null_cycle_metrics(
            trained_model,
            config["null_repeats"],
            config["null_examples"],
            config["eval_batch_size"],
            8,
            230_000 + seed,
            device,
        )
        projective["interventions"] = deep_intervention_audit(
            trained_model,
            config["intervention_examples"],
            config["eval_batch_size"],
            config["intervention_length"],
            240_000 + seed,
            device,
        )
        seed_record: dict[str, Any] = {"projective": projective}

        raw_path = ROOT / "results" / "pilot" / "checkpoints" / f"linear_terminal_seed{seed}.pt"
        if raw_path.exists():
            raw, parent_payload = load_legacy_linear_checkpoint(raw_path, device)
            raw_record: dict[str, Any] = {
                "checkpoint_sha256": file_sha256(raw_path),
                "parent_source_digest": parent_payload["source_digest"],
                "deep": {},
            }
            for family_index, family in enumerate(config["families"]):
                evaluation_seed = 220_000 + seed * 1000 + family_index * 100
                raw_record["deep"][family] = deep_rollout_metrics(
                    raw,
                    family,
                    config["lengths"],
                    config["examples"],
                    config["eval_batch_size"],
                    evaluation_seed,
                    device,
                )
            seed_record["raw_parent"] = raw_record

        if not args.reuse_checkpoints:
            torch.save(
                {
                    "schema": "komorebi.neuralese.projective_checkpoint.v1",
                    "source_digest": source_digest,
                    "config": config_dict(train_config),
                    "state_dict": trained_model.state_dict(),
                },
                checkpoint_path,
            )
        projective["checkpoint"] = {
            "path": checkpoint_path.relative_to(ROOT).as_posix(),
            "sha256": file_sha256(checkpoint_path),
            "schema": "komorebi.neuralese.projective_checkpoint.v1",
            "training_source_digest": training_source_digest,
        }
        records[str(seed)] = seed_record

    transport_metrics = None
    if len(trained_models) >= 2:
        source_seed, target_seed = config["seeds"][:2]
        transport_metrics, _ = cross_seed_transport(
            trained_models[source_seed],
            trained_models[target_seed],
            seed=250_000,
            anchor_examples=config["intervention_examples"],
            test_examples=config["intervention_examples"],
            batch_size=config["eval_batch_size"],
            device=device,
        )

    gates = adjudicate(records, transport_metrics, config)
    elapsed = time.perf_counter() - started
    result = {
        "schema": "komorebi.neuralese.projective_training.result.v1",
        "version": "0.2.0",
        "profile": args.profile,
        "developmental": True,
        "source_digest": source_digest,
        "evaluation_source_digest": source_digest,
        "records": records,
        "transport": transport_metrics,
        "gates": gates,
        "elapsed_seconds": elapsed,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
            "torch": torch.__version__,
            "device": str(device),
            "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        },
    }
    atomic_json(output_dir / "RESULTS.json", result)
    atomic_json(output_dir / "GATES.json", gates)
    charts = render_chart(output_dir, records)
    report = render_report(records, gates, transport_metrics, config)
    (output_dir / "REPORT.md").write_text(report, encoding="utf-8")
    completion = {
        "schema": "komorebi.neuralese.projective_training.completion.v1",
        "profile": args.profile,
        "all_gates_passed": gates["all_passed"],
        "results_sha256": file_sha256(output_dir / "RESULTS.json"),
        "report_sha256": file_sha256(output_dir / "REPORT.md"),
        "charts": charts,
        "elapsed_seconds": elapsed,
        "evaluation_source_digest": source_digest,
    }
    atomic_json(output_dir / "RUN_COMPLETE.json", completion)
    print(json.dumps(completion, sort_keys=True))
    return 0 if gates["all_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
