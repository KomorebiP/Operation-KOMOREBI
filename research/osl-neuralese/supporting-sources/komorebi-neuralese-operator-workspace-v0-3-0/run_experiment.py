#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import shutil
import sys
import traceback
from dataclasses import asdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Iterable

import numpy as np
import torch

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from komorebi_neuralese.closure import (
    ClosureEvaluationConfig,
    deep_accuracy_stability,
    full_closure_evaluation,
)
from komorebi_neuralese.data import EpisodeGenerator
from komorebi_neuralese.hard_operator import (
    ExactTableOracle,
    HardOperatorRNN,
    hard_operator_health_metrics,
)
from komorebi_neuralese.heldout_semantics import (
    split_conditioned_final_action_metrics,
)
from komorebi_neuralese.models import RecurrentOperatorModel, build_model
from komorebi_neuralese.reporting import code_files, protocol_digest, tree_digest, write_json
from komorebi_neuralese.splits import audit_coordinate_splits
from komorebi_neuralese.train import TrainConfig, config_dict, train_arm
from komorebi_neuralese.transport import cross_seed_transport
from komorebi_neuralese.version import VERSION


def _device(name: str) -> torch.device:
    if name == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = torch.device(name)
    if device.type == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")
    return device


def _environment(device: torch.device, threads: int) -> dict[str, Any]:
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


def _tensor_state_digest(model: torch.nn.Module) -> str:
    """Hash only initialized tensor values, excluding class-specific metadata."""
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        if not torch.is_tensor(value):
            continue
        tensor = value.detach().cpu().contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(tensor.dtype).encode("ascii"))
        digest.update(json.dumps(list(tensor.shape), separators=(",", ":")).encode("ascii"))
        digest.update(tensor.numpy().tobytes())
    return digest.hexdigest()


def _read_protocol(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("protocol must be a JSON object")
    required = {"schema_version", "protocol_id", "analysis_status", "package_version", "seeds", "arms", "training", "evaluation"}
    missing = sorted(required - set(value))
    if missing:
        raise ValueError(f"protocol missing required keys: {missing}")
    if value["package_version"] != VERSION:
        raise ValueError(f"protocol package_version must be {VERSION}")
    seeds = value["seeds"]
    if not isinstance(seeds, list) or not seeds or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds):
        raise ValueError("protocol seeds must be a nonempty list of integers")
    if len(seeds) != len(set(seeds)):
        raise ValueError("protocol seeds must be unique")
    if not isinstance(value["arms"], dict) or not value["arms"]:
        raise ValueError("protocol arms must be a nonempty object")
    training = value["training"]
    if not isinstance(training, dict):
        raise ValueError("protocol training must be an object")
    if training.get("word_product_scope") != "contiguous":
        raise ValueError(
            "v0.3 protocols must explicitly freeze training.word_product_scope='contiguous'"
        )
    if training.get("conditioned_sampler_backend") != "cached_exact_v1":
        raise ValueError(
            "v0.3 protocols must explicitly freeze "
            "training.conditioned_sampler_backend='cached_exact_v1'"
        )
    for name, arm in value["arms"].items():
        if not isinstance(name, str) or not isinstance(arm, dict) or "model_name" not in arm:
            raise ValueError("every arm must have a string name and model_name")
        if arm.get("word_product_scope", "contiguous") != "contiguous":
            raise ValueError(
                f"arm {name!r} overrides the required contiguous training split boundary"
            )
        if arm.get("conditioned_sampler_backend", "cached_exact_v1") != "cached_exact_v1":
            raise ValueError(
                f"arm {name!r} overrides the required cached exact conditioned sampler"
            )
    return value


def _numeric_leaves(value: Any, prefix: str = "") -> dict[str, float]:
    leaves: dict[str, float] = {}
    if isinstance(value, dict):
        for key, child in value.items():
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            leaves.update(_numeric_leaves(child, child_prefix))
    elif isinstance(value, (int, float)) and not isinstance(value, bool):
        number = float(value)
        if math.isfinite(number):
            leaves[prefix] = number
    return leaves


def _aggregate_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    flattened = [_numeric_leaves(record["metrics"]) for record in records]
    if not flattened:
        return {}
    keys = sorted(set.intersection(*(set(record) for record in flattened)))
    output: dict[str, Any] = {}
    for key in keys:
        values = [record[key] for record in flattened]
        output[key] = {
            "mean": mean(values),
            "std": pstdev(values) if len(values) > 1 else 0.0,
            "n": len(values),
            "values": values,
        }
    return output


def _aggregate_all(records: dict[str, list[dict[str, Any]]], transport: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "arms": {arm: _aggregate_records(values) for arm, values in records.items()},
        "transport": _aggregate_records(transport),
    }


def _comparison(value: float, operator: str, gate: dict[str, Any]) -> bool:
    if operator == "ge":
        return value >= float(gate["threshold"])
    if operator == "le":
        return value <= float(gate["threshold"])
    if operator == "between":
        return float(gate["lower"]) <= value <= float(gate["upper"])
    raise ValueError(f"unknown gate operator: {operator}")


def _criterion(gate: dict[str, Any]) -> str:
    operator = gate["operator"]
    if operator == "ge":
        return f">= {gate['threshold']}"
    if operator == "le":
        return f"<= {gate['threshold']}"
    if operator == "between":
        return f"in [{gate['lower']}, {gate['upper']}]"
    if operator == "delta_ge":
        return f"paired mean delta >= {gate['threshold']}"
    return operator


def _evaluate_gates(protocol: dict[str, Any], aggregate: dict[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for gate in protocol.get("gates", []):
        gate_id = str(gate.get("id", ""))
        if not gate_id or gate_id in output:
            raise ValueError("gate ids must be nonempty and unique")
        record: dict[str, Any] = {"criterion": _criterion(gate), "passed": False, "source": gate.get("source", "arm")}
        try:
            source = gate.get("source", "arm")
            metric = str(gate["metric"])
            if source == "transport":
                item = aggregate["transport"][metric]
            elif source == "arm":
                arm = str(gate["arm"])
                item = aggregate["arms"][arm][metric]
                record["arm"] = arm
            else:
                raise ValueError(f"unknown gate source: {source}")
            values = [float(value) for value in item["values"]]
            if not values or any(not math.isfinite(value) for value in values):
                raise ValueError("gate metric is empty or non-finite")
            operator = str(gate["operator"])
            if operator == "delta_ge":
                if source != "arm":
                    raise ValueError("paired delta gates require arm metrics")
                comparator = str(gate["comparator_arm"])
                other_values = [float(value) for value in aggregate["arms"][comparator][metric]["values"]]
                if len(values) != len(other_values):
                    raise ValueError("paired gate arm lengths differ")
                observed_values = [left - right for left, right in zip(values, other_values, strict=True)]
                observed = mean(observed_values)
                passed = observed >= float(gate["threshold"])
                record["comparator_arm"] = comparator
            else:
                observed_values = values
                observed = float(item["mean"])
                passed = _comparison(observed, operator, gate)
            minimum_fraction = gate.get("minimum_seed_fraction")
            seed_fraction = None
            if minimum_fraction is not None:
                if operator == "delta_ge":
                    threshold = float(gate["threshold"])
                    seed_fraction = sum(value >= threshold for value in observed_values) / len(observed_values)
                else:
                    seed_fraction = sum(_comparison(value, operator, gate) for value in observed_values) / len(observed_values)
                passed = passed and seed_fraction >= float(minimum_fraction)
            record.update({"observed": observed, "n": len(observed_values), "values": observed_values, "seed_fraction_passing": seed_fraction, "passed": bool(passed)})
        except (KeyError, TypeError, ValueError) as error:
            record["error"] = str(error)
        output[gate_id] = record
    return output


def _train_config(protocol: dict[str, Any], arm: dict[str, Any], seed: int, device: torch.device) -> TrainConfig:
    merged = {**dict(protocol["training"]), **{key: value for key, value in arm.items() if key != "model_name"}}
    evaluation_depths = [int(value) for value in protocol["evaluation"]["depths"]]
    return TrainConfig(
        model_name=str(arm["model_name"]),
        regime=str(merged.get("regime", "terminal")),
        seed=seed,
        steps=int(merged["steps"]),
        batch_size=int(merged["batch_size"]),
        train_min_length=int(merged.get("train_min_length", 1)),
        train_max_length=int(merged.get("train_max_length", 4)),
        max_eval_length=max(evaluation_depths),
        learning_rate=float(merged.get("learning_rate", 1e-3)),
        operator_init_std=(
            None if merged.get("operator_init_std") is None else float(merged["operator_init_std"])
        ),
        orthogonal_parameterization=str(merged.get("orthogonal_parameterization", "qr")),
        weight_decay=float(merged.get("weight_decay", 1e-6)),
        grad_clip=float(merged.get("grad_clip", 1.0)),
        relation_weight=float(merged.get("relation_weight", 0.15)),
        relation_hidden_weight=float(merged.get("relation_hidden_weight", 0.05)),
        intermediate_weight=float(merged.get("intermediate_weight", 0.50)),
        metric_isometry_weight=float(merged.get("metric_isometry_weight", 0.0)),
        composition_weight=float(merged.get("composition_weight", 0.0)),
        composition_shuffle_targets=bool(merged.get("composition_shuffle_targets", False)),
        composition_min_length=int(merged.get("composition_min_length", 2)),
        composition_max_length=int(merged.get("composition_max_length", 4)),
        word_product_scope=str(merged.get("word_product_scope", "contiguous")),
        conditioned_sampler_backend=str(
            merged.get("conditioned_sampler_backend", "cached_exact_v1")
        ),
        device=str(device),
    )


def _evaluate_model(model: RecurrentOperatorModel, protocol: dict[str, Any], seed: int, device: torch.device) -> dict[str, Any]:
    evaluation = protocol["evaluation"]
    split = str(evaluation["coordinate_split"])
    neighbors = tuple(int(value) for value in evaluation.get("neighbor_offsets", [-1, 0, 1]))
    depths = tuple(int(value) for value in evaluation["depths"])
    closure = full_closure_evaluation(
        model,
        ClosureEvaluationConfig(
            depths=depths,
            neighbor_offsets=neighbors,
            examples=int(evaluation["examples_per_depth"]),
            batch_size=int(evaluation["batch_size"]),
            geometry_examples=int(evaluation["geometry_examples"]),
            composition_examples=int(evaluation["composition_examples"]),
            patch_examples=int(evaluation["patch_examples"]),
            composition_family=str(evaluation.get("composition_family", "random")),
            patch_donor_family=str(evaluation.get("patch_donor_family", "random")),
            patch_recipient_family=str(evaluation.get("patch_recipient_family", "random")),
            patch_prefix_length=int(evaluation.get("patch_prefix_length", 4)),
            patch_suffix_length=int(evaluation.get("patch_suffix_length", 8)),
            coordinate_split=split,
        ),
        seed=seed,
        device=device,
    )
    c8 = deep_accuracy_stability(
        model,
        family="c8",
        depths=depths,
        examples_per_depth=int(evaluation.get("c8_examples_per_depth", evaluation["examples_per_depth"])),
        batch_size=int(evaluation["batch_size"]),
        seed=seed + 100_000,
        device=device,
        coordinate_split=split,
        neighbor_offsets=neighbors,
    )
    random_family = deep_accuracy_stability(
        model,
        family="random",
        depths=tuple(int(value) for value in evaluation.get("random_depths", [8, 32, 64])),
        examples_per_depth=int(evaluation.get("random_examples_per_depth", max(64, int(evaluation["examples_per_depth"]) // 2))),
        batch_size=int(evaluation["batch_size"]),
        seed=seed + 200_000,
        device=device,
        coordinate_split=split,
        neighbor_offsets=(0,),
    )
    output = {
        "closure": closure,
        "c8_deep_stability": c8,
        "random_deep_stability": random_family,
    }
    semantic_holdout_depths = tuple(
        int(value) for value in evaluation.get("semantic_holdout_depths", ())
    )
    if semantic_holdout_depths:
        output["split_conditioned_final_action"] = (
            split_conditioned_final_action_metrics(
                model,
                family=str(evaluation.get("semantic_holdout_family", "random")),
                depths=semantic_holdout_depths,
                examples_per_depth=int(
                    evaluation.get(
                        "semantic_holdout_examples",
                        evaluation["examples_per_depth"],
                    )
                ),
                batch_size=int(
                    evaluation.get("semantic_holdout_batch_size", evaluation["batch_size"])
                ),
                seed=seed + int(evaluation.get("semantic_holdout_seed_offset", 800_000)),
                device=device,
                coordinate_split=split,
                maximum_candidate_multiplier=int(
                    evaluation.get("semantic_holdout_maximum_candidate_multiplier", 100)
                ),
            )
        )
    extended_depths = tuple(int(value) for value in evaluation.get("extended_stability_depths", ()))
    if extended_depths:
        extended_examples = int(evaluation.get("extended_examples_per_depth", 128))
        extended: dict[str, Any] = {}
        for family_index, family in enumerate(
            evaluation.get("extended_stability_families", ["d4", "c8", "random"])
        ):
            extended[str(family)] = deep_accuracy_stability(
                model,
                family=str(family),
                depths=extended_depths,
                examples_per_depth=extended_examples,
                batch_size=int(evaluation["batch_size"]),
                seed=seed + 400_000 + 100_000 * family_index,
                device=device,
                coordinate_split=split,
                neighbor_offsets=(0,),
            )
        output["extended_stability"] = extended
    if isinstance(model, HardOperatorRNN):
        health: dict[str, Any] = {}
        for family_index, family in enumerate(("d4", "c8", "random")):
            health_batch = EpisodeGenerator(
                seed + 300_000 + 10_000 * family_index,
                coordinate_split=split,
            ).sample(
                int(evaluation["geometry_examples"]),
                0,
                family=family,
            ).to(device)
            health[family] = hard_operator_health_metrics(model, health_batch.tables)
        output["hard_operator_health"] = health
    return output


def _exact_oracle_integrity(metrics: dict[str, Any]) -> dict[str, Any]:
    """Turn the structured ceiling into a fail-closed assay check."""

    checks: dict[str, bool] = {}
    for section_name in ("closure", "c8_deep_stability", "random_deep_stability"):
        section = (
            metrics[section_name]["deep_stability"]
            if section_name == "closure"
            else metrics[section_name]
        )
        for depth, record in section["by_depth"].items():
            checks[f"{section_name}.depth_{depth}.accuracy"] = record["endpoint_accuracy"] == 1.0
            checks[f"{section_name}.depth_{depth}.finite"] = record["finite_trajectory_fraction"] == 1.0
            checks[f"{section_name}.depth_{depth}.norm"] = (
                abs(float(record["g_endpoint_ratio_median"]) - 1.0) <= 1e-6
            )
    for family, section in metrics.get("extended_stability", {}).items():
        for depth, record in section["by_depth"].items():
            checks[f"extended.{family}.depth_{depth}.accuracy"] = record["endpoint_accuracy"] == 1.0
            checks[f"extended.{family}.depth_{depth}.finite"] = record["finite_trajectory_fraction"] == 1.0
            checks[f"extended.{family}.depth_{depth}.norm"] = (
                abs(float(record["g_endpoint_ratio_median"]) - 1.0) <= 1e-6
            )
    composition = metrics["closure"]["anonymous_composition"]
    checks["composition.target_split"] = bool(composition["composite_target_split_enforced"])
    checks["composition.substitution"] = composition["true_substitution_accuracy"] == 1.0
    checks["composition.output_agreement"] = composition["true_substitution_output_agreement"] == 1.0
    checks["composition.residual"] = (
        float(composition["metric_operator_closure_residual"]["maximum"]) <= 1e-6
    )
    patch = metrics["closure"]["cross_context_patch"]
    checks["patch.correct"] = patch["cross_context_state_patch_accuracy"] == 1.0
    checks["patch.wrong_control"] = patch["on_manifold_wrong_state_control_accuracy"] == 0.0
    semantic_holdout = metrics.get("split_conditioned_final_action")
    if semantic_holdout is not None:
        checks["split_conditioned_final_action.primitive_split"] = bool(
            semantic_holdout["primitive_split_enforced"]
        )
        checks["split_conditioned_final_action.composite_split"] = bool(
            semantic_holdout["full_composite_split_enforced"]
        )
        receipt = semantic_holdout["acceptance_receipt"]
        checks["split_conditioned_final_action.accepted_only"] = bool(
            receipt["only_accepted_examples_evaluated"]
            and receipt["model_evaluated_rejected_examples"] == 0
            and receipt["all_primitive_maps_in_requested_split"]
            and receipt["all_accepted_full_composites_in_requested_split"]
        )
        for depth, record in semantic_holdout["by_depth"].items():
            depth_receipt = record["acceptance_receipt"]
            checks[f"split_conditioned_final_action.depth_{depth}.accuracy"] = (
                record["endpoint_accuracy"] == 1.0
            )
            checks[f"split_conditioned_final_action.depth_{depth}.finite"] = (
                record["finite_logits_fraction"] == 1.0
            )
            checks[f"split_conditioned_final_action.depth_{depth}.accounting"] = bool(
                depth_receipt["candidate_accounting_exact"]
                and depth_receipt["acceptance_accounting_exact"]
                and depth_receipt["rejection_accounting_exact"]
            )
    return {"passed": all(checks.values()), "checks": checks}


def _summary_value(aggregate: dict[str, Any], arm: str, metric: str) -> float | None:
    try:
        return float(aggregate["arms"][arm][metric]["mean"])
    except (KeyError, TypeError, ValueError):
        return None


def _format(value: float | None) -> str:
    return "—" if value is None or not math.isfinite(value) else f"{value:.4f}"


def _report(
    protocol: dict[str, Any],
    aggregate: dict[str, Any],
    gates: dict[str, Any],
    grid: dict[str, Any],
    oracle_record: dict[str, Any] | None,
) -> str:
    lines = [
        "# V0.3 hard-stable recurrent operator report",
        "",
        f"**Protocol:** `{protocol['protocol_id']}`  ",
        f"**Analysis status:** `{protocol['analysis_status']}`  ",
        f"**Coordinate split:** `{protocol['evaluation']['coordinate_split']}`",
        "",
        "## Arm summary",
        "",
        "| Arm | D4 d8 | D4 d64 | D4 d128 | C8 d64 | D4 norm d2048 | Composition substitution | Sequential/direct | Closure residual | Context patch |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in protocol["arms"]:
        metrics = (
            "closure.deep_stability.by_depth.8.endpoint_accuracy",
            "closure.deep_stability.by_depth.64.endpoint_accuracy",
            "closure.deep_stability.by_depth.128.endpoint_accuracy",
            "c8_deep_stability.by_depth.64.endpoint_accuracy",
            "extended_stability.d4.by_depth.2048.g_endpoint_ratio.median",
            "closure.anonymous_composition.true_substitution_accuracy",
            "closure.anonymous_composition.true_substitution_output_agreement",
            "closure.anonymous_composition.metric_operator_closure_residual.median",
            "closure.cross_context_patch.cross_context_state_patch_accuracy",
        )
        values = [_summary_value(aggregate, arm, metric) for metric in metrics]
        lines.append(f"| {arm} | " + " | ".join(_format(value) for value in values) + " |")
    semantic_depths = tuple(
        sorted(
            {
                int(value)
                for value in protocol["evaluation"].get("semantic_holdout_depths", ())
            }
        )
    )
    if semantic_depths:
        lines.extend(
            [
                "",
                "## Split-conditioned final-action assay",
                "",
                "| Arm | Depth | Endpoint accuracy | Candidate acceptance rate |",
                "|---|---:|---:|---:|",
            ]
        )
        for arm in protocol["arms"]:
            for depth in semantic_depths:
                accuracy = _summary_value(
                    aggregate,
                    arm,
                    f"split_conditioned_final_action.by_depth.{depth}.endpoint_accuracy",
                )
                acceptance = _summary_value(
                    aggregate,
                    arm,
                    "split_conditioned_final_action.by_depth."
                    f"{depth}.acceptance_receipt.acceptance_rate",
                )
                lines.append(
                    f"| {arm} | {depth} | {_format(accuracy)} | {_format(acceptance)} |"
                )
        lines.extend(
            [
                "",
                "Every scored word in this assay has both its primitive maps and its full "
                "composite finite-state action in the requested dev/test hash partition. "
                "This is split-conditioned final-action evaluation; it does not establish "
                "that the abstract group element or word-equivalence class is globally novel.",
            ]
        )
    lines.extend(["", "## Frozen gates", ""])
    if not gates:
        lines.append("No inferential gates were assigned to this development-only protocol.")
    else:
        lines.extend(
            [
                "| Gate | Status | Mean | Mean criterion | Seed pass fraction | Required fraction |",
                "|---|---|---:|---|---:|---:|",
            ]
        )
        for gate_id, gate in gates.items():
            status = "PASS" if gate["passed"] else "FAIL"
            seed_fraction = gate.get("seed_fraction_passing")
            required_fraction = next(
                (
                    item.get("minimum_seed_fraction")
                    for item in protocol.get("gates", [])
                    if item.get("id") == gate_id
                ),
                None,
            )
            lines.append(
                f"| `{gate_id}` | **{status}** | {_format(gate.get('observed'))} | "
                f"{gate['criterion']} | {_format(seed_fraction)} | "
                f"{_format(required_fraction)} |"
            )
    transport = aggregate.get("transport", {})
    if transport:
        lines.extend(["", "## Cross-seed transport", "", "| Metric | Mean |", "|---|---:|"])
        for metric in (
            "by_family.d4.aligned_state_patch_accuracy",
            "by_family.d4.shuffled_pair_state_patch_accuracy",
            "by_family.d4.random_map_state_patch_accuracy",
            "by_family.d4.decode_reembed_state_patch_accuracy",
            "by_family.d4.operator_intertwining_behavior_agreement",
            "by_family.d4.metric_compatibility_normalized_defect",
        ):
            item = transport.get(metric)
            if item is not None:
                lines.append(f"| `{metric}` | {item['mean']:.4f} |")
    lines.extend([
        "",
        "## Completeness and interpretation",
        "",
        f"The exact arm-by-seed grid was {'complete' if grid['complete'] else 'incomplete'} ({grid['observed_cells']}/{grid['expected_cells']} cells).",
        f"The parameter-free exact table oracle {'passed' if oracle_record and oracle_record['integrity']['passed'] else 'was not run or failed'} its fail-closed orientation, closure, and stability checks.",
        "",
        "Training confines every nonempty contiguous subword action to the train map partition. The model receives complete transition tables and an operator-shaped 8×8 latent channel, and an exact table-transpose executor exists. Results therefore test learned table execution, anonymous closure, and coordinate transport under this explicit inductive bias. Exact norm preservation and orthogonality in the hard arm are architectural integrity properties, not learned discoveries. The assay does not establish spontaneous Neuralese, a learned invariant metric, globally novel group elements, language-model generality, or awareness.",
        "",
    ])
    return "\n".join(lines)


def _write_csv(path: Path, records: dict[str, list[dict[str, Any]]]) -> None:
    preferred: tuple[str, ...] = (
        "closure.deep_stability.by_depth.8.endpoint_accuracy",
        "closure.deep_stability.by_depth.32.endpoint_accuracy",
        "closure.deep_stability.by_depth.64.endpoint_accuracy",
        "closure.deep_stability.by_depth.128.endpoint_accuracy",
        "c8_deep_stability.by_depth.64.endpoint_accuracy",
        "extended_stability.d4.by_depth.2048.endpoint_accuracy",
        "extended_stability.d4.by_depth.2048.g_endpoint_ratio.median",
        "closure.anonymous_composition.true_substitution_accuracy",
        "closure.anonymous_composition.true_substitution_output_agreement",
        "closure.anonymous_composition.metric_operator_closure_residual.median",
        "closure.operator_geometry.aggregate.normalized_g_isometry_defect_p95",
        "closure.operator_geometry.aggregate.spectral_radius_p95",
        "closure.operator_geometry.metric.condition_number",
        "closure.cross_context_patch.cross_context_state_patch_accuracy",
        "closure.cross_context_patch.on_manifold_wrong_state_control_accuracy",
        "closure.cross_context_patch.cross_context_patch_margin",
    )
    semantic_depths = sorted(
        {
            int(depth)
            for values in records.values()
            for record in values
            for depth in record["metrics"]
            .get("split_conditioned_final_action", {})
            .get("by_depth", {})
        }
    )
    if semantic_depths:
        preferred += ("split_conditioned_final_action.endpoint_accuracy",)
        for depth in semantic_depths:
            preferred += (
                f"split_conditioned_final_action.by_depth.{depth}.endpoint_accuracy",
                "split_conditioned_final_action.by_depth."
                f"{depth}.acceptance_receipt.acceptance_rate",
            )
    rows: list[dict[str, Any]] = []
    for arm, values in records.items():
        for record in values:
            leaves = _numeric_leaves(record["metrics"])
            row = {"arm": arm, "seed": record["seed"], "parameters": record["training"]["parameter_count"], "elapsed_seconds": record["training"]["elapsed_seconds"]}
            row.update({metric: leaves.get(metric) for metric in preferred})
            rows.append(row)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _plots(output_dir: Path, protocol: dict[str, Any], aggregate: dict[str, Any]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []
    depths = [int(value) for value in protocol["evaluation"]["depths"]]
    created: list[str] = []
    figure, axis = plt.subplots(figsize=(9, 6), dpi=180)
    for arm in protocol["arms"]:
        values = [_summary_value(aggregate, arm, f"closure.deep_stability.by_depth.{depth}.endpoint_accuracy") for depth in depths]
        if all(value is not None for value in values):
            axis.plot(depths, values, marker="o", label=arm)
    axis.set_xscale("log", base=2)
    axis.set_xticks(depths, labels=[str(value) for value in depths])
    axis.set_ylim(0.0, 1.03)
    axis.set_xlabel("Recurrent depth")
    axis.set_ylabel("Exact endpoint accuracy")
    axis.set_title("Held-out-table D4 accuracy")
    axis.legend(fontsize=7)
    figure.tight_layout()
    path = output_dir / "heldout_depth_accuracy.png"
    figure.savefig(path)
    plt.close(figure)
    created.append(path.name)

    figure, axis = plt.subplots(figsize=(10, 6), dpi=180)
    arms = list(protocol["arms"])
    defects = [_summary_value(aggregate, arm, "closure.operator_geometry.aggregate.normalized_g_isometry_defect_p95") or 0.0 for arm in arms]
    axis.bar(np.arange(len(arms)), defects)
    axis.set_xticks(np.arange(len(arms)), labels=arms, rotation=25, ha="right")
    axis.set_ylabel("P95 normalized G-isometry defect")
    axis.set_title("Held-out operator geometry")
    figure.tight_layout()
    path = output_dir / "heldout_operator_geometry.png"
    figure.savefig(path)
    plt.close(figure)
    created.append(path.name)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a frozen v0.3 Komorebi operator-workspace protocol")
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--threads", type=int, default=min(4, os.cpu_count() or 1))
    args = parser.parse_args()
    protocol_path = args.protocol.resolve()
    output_dir = args.output_dir.resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"output directory is not empty: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    protocol = _read_protocol(protocol_path)
    device = _device(args.device)
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    np.random.seed(0)
    torch.manual_seed(0)

    code_digest = tree_digest(ROOT, code_files(ROOT))
    frozen_protocol_digest = protocol_digest(protocol_path)
    expected_code = protocol.get("expected_code_digest")
    if expected_code is not None and expected_code != code_digest:
        raise RuntimeError(f"code digest mismatch: expected {expected_code}, observed {code_digest}")
    split_object = audit_coordinate_splits()
    split_audit = asdict(split_object)
    split_audit["passed"] = split_object.passed
    expected_split = protocol.get("expected_coordinate_split_digest")
    if expected_split is not None and expected_split != split_audit["digest"]:
        raise RuntimeError("coordinate split digest does not match frozen protocol")
    if not split_audit["passed"]:
        raise RuntimeError("coordinate split audit failed")

    shutil.copyfile(protocol_path, output_dir / "PROTOCOL.json")
    receipt_base = {
        "package_version": VERSION,
        "protocol_id": protocol["protocol_id"],
        "analysis_status": protocol["analysis_status"],
        "code_digest": code_digest,
        "protocol_digest": frozen_protocol_digest,
        "coordinate_split_digest": split_audit["digest"],
    }
    write_json(output_dir / "RUNNING.json", {**receipt_base, "status": "running", "environment": _environment(device, args.threads)})
    records: dict[str, list[dict[str, Any]]] = {name: [] for name in protocol["arms"]}
    retained_models: dict[str, dict[int, RecurrentOperatorModel]] = {}
    transport_records: list[dict[str, Any]] = []
    oracle_record: dict[str, Any] | None = None

    try:
        oracle_config = protocol.get("oracle", {})
        if oracle_config.get("enabled", False):
            print("exact structured oracle audit", flush=True)
            oracle = ExactTableOracle().to(device)
            oracle_seed = int(oracle_config.get("seed", 7_700_000))
            oracle_metrics = _evaluate_model(oracle, protocol, oracle_seed, device)
            oracle_integrity = _exact_oracle_integrity(oracle_metrics)
            oracle_record = {
                **receipt_base,
                "role": "exact_structured_ceiling_only",
                "model_spec": oracle.model_spec(),
                "seed": oracle_seed,
                "integrity": oracle_integrity,
                "metrics": oracle_metrics,
            }
            write_json(output_dir / "EXACT_ORACLE.json", oracle_record)
            if not oracle_integrity["passed"]:
                raise RuntimeError("exact structured oracle audit failed")

        transport_arms = set(protocol.get("transport", {}).get("arms", []))
        for arm_index, (arm_name, arm) in enumerate(protocol["arms"].items(), start=1):
            print(f"[{arm_index}/{len(protocol['arms'])}] arm={arm_name}", flush=True)
            if arm_name in transport_arms:
                retained_models[arm_name] = {}
            for seed_index, seed in enumerate(protocol["seeds"], start=1):
                print(f"  [{seed_index}/{len(protocol['seeds'])}] seed={seed} training", flush=True)
                torch.manual_seed(seed)
                np.random.seed(seed)
                config = _train_config(protocol, arm, seed, device)
                model = build_model(
                    str(arm["model_name"]),
                    operator_init_std=config.operator_init_std,
                    orthogonal_parameterization=config.orthogonal_parameterization,
                )
                initialization_digest = _tensor_state_digest(model)
                trained = train_arm(model, config)
                evaluation_seed = int(protocol["evaluation"].get("seed_base", 500_000)) + 1000 * seed
                print(f"  [{seed_index}/{len(protocol['seeds'])}] seed={seed} evaluating", flush=True)
                metrics = _evaluate_model(trained.model, protocol, evaluation_seed, device)
                record = {
                    **receipt_base,
                    "arm": arm_name,
                    "seed": seed,
                    "initial_tensor_digest": initialization_digest,
                    "model_spec": (
                        trained.model.model_spec()
                        if callable(getattr(trained.model, "model_spec", None))
                        else {"model_name": config.model_name}
                    ),
                    "config": config_dict(config),
                    "training": {
                        "parameter_count": trained.parameter_count,
                        "elapsed_seconds": trained.elapsed_seconds,
                        "final_loss": trained.final_loss,
                        "trajectory": trained.trajectory,
                        "sampling_audit": trained.sampling_audit,
                    },
                    "metrics": metrics,
                }
                records[arm_name].append(record)
                arm_dir = output_dir / "arms" / arm_name
                arm_dir.mkdir(parents=True, exist_ok=True)
                write_json(arm_dir / f"seed_{seed}.json", record)
                checkpoint_dir = output_dir / "checkpoints" / arm_name
                checkpoint_dir.mkdir(parents=True, exist_ok=True)
                torch.save({**receipt_base, "arm": arm_name, "seed": seed, "config": config_dict(config), "state_dict": trained.model.state_dict()}, checkpoint_dir / f"seed_{seed}.pt")
                if arm_name in transport_arms:
                    retained_models[arm_name][seed] = trained.model

        transport_config = protocol.get("transport", {})
        if transport_config.get("enabled", False):
            pairs = [tuple(int(value) for value in pair) for pair in transport_config["seed_pairs"]]
            for arm_name in transport_config["arms"]:
                for pair_index, (source_seed, target_seed) in enumerate(pairs, start=1):
                    print(f"transport arm={arm_name} pair={source_seed}->{target_seed} ({pair_index}/{len(pairs)})", flush=True)
                    metrics, transport = cross_seed_transport(
                        retained_models[arm_name][source_seed],
                        retained_models[arm_name][target_seed],
                        seed=int(transport_config.get("seed_base", 9_000_000)) + pair_index,
                        anchor_examples=int(transport_config["anchor_examples"]),
                        test_examples=int(transport_config["test_examples"]),
                        batch_size=int(transport_config["batch_size"]),
                        device=device,
                        anchor_coordinate_split="train",
                        test_coordinate_split=str(protocol["evaluation"]["coordinate_split"]),
                    )
                    transport_record = {**receipt_base, "arm": arm_name, "source_seed": source_seed, "target_seed": target_seed, "metrics": metrics, "transport": transport.to_serializable()}
                    transport_records.append(transport_record)
                    write_json(output_dir / "transport" / f"{arm_name}_{source_seed}_to_{target_seed}.json", transport_record)

        expected_pairs = {(arm, seed) for arm in protocol["arms"] for seed in protocol["seeds"]}
        observed_pairs = {(record["arm"], record["seed"]) for values in records.values() for record in values}
        grid = {
            "expected_cells": len(expected_pairs),
            "observed_cells": len(observed_pairs),
            "missing_cells": [list(value) for value in sorted(expected_pairs - observed_pairs)],
            "unexpected_cells": [list(value) for value in sorted(observed_pairs - expected_pairs)],
            "complete": observed_pairs == expected_pairs,
        }
        aggregate = _aggregate_all(records, transport_records)
        gates = _evaluate_gates(protocol, aggregate)
        all_gates_passed = bool(gates) and len(gates) == len(protocol.get("gates", [])) and all(gate["passed"] for gate in gates.values())
        write_json(output_dir / "AGGREGATE.json", aggregate)
        write_json(output_dir / "GATES.json", {"all_gates_passed": all_gates_passed, "gates": gates})
        write_json(output_dir / "GRID_AUDIT.json", grid)
        write_json(output_dir / "COORDINATE_SPLIT_AUDIT.json", split_audit)
        _write_csv(output_dir / "summary.csv", records)
        (output_dir / "REPORT.md").write_text(
            _report(protocol, aggregate, gates, grid, oracle_record),
            encoding="utf-8",
        )
        plots = _plots(output_dir, protocol, aggregate)
        sampling_audits = [
            record["training"]["sampling_audit"]
            for arm_records in records.values()
            for record in arm_records
        ]
        conditioning_supports: dict[str, dict[str, Any]] = {}
        for audit in sampling_audits:
            for support in audit.get("conditioning_supports", []):
                digest = str(support["digest"])
                previous = conditioning_supports.setdefault(digest, support)
                if previous != support:
                    raise RuntimeError(
                        f"conditioning support digest {digest} has inconsistent metadata"
                    )
        sampling_methods = sorted(
            {
                str(method)
                for audit in sampling_audits
                for method in audit.get("sampling_methods", [])
            }
        )
        conditioned_sampler_backends = sorted(
            {
                str(audit["conditioned_sampler_backend"])
                for audit in sampling_audits
                if audit.get("conditioned_sampler_backend") is not None
            }
        )
        training_sampling_audit = {
            "cells": len(sampling_audits),
            "word_product_scopes": sorted(
                {str(audit["word_product_scope"]) for audit in sampling_audits}
            ),
            "sampling_methods": sampling_methods,
            "conditioned_sampler_backends": conditioned_sampler_backends,
            "actual_counter_semantics": (
                "candidate/rejected totals count sampler draws actually executed; "
                "direct-conditioned draws have zero fictional rejections"
            ),
            "conditioning_supports": sorted(
                conditioning_supports.values(),
                key=lambda item: (int(item["length"]), str(item["digest"])),
            ),
            "direct_conditioning_receipts_complete": (
                "direct_conditioned_uniform" not in sampling_methods
                or bool(conditioning_supports)
            ),
            "conditioned_sampler_backend_frozen": (
                conditioned_sampler_backends == ["cached_exact_v1"]
            ),
            "all_fail_closed": all(bool(audit["fail_closed"]) for audit in sampling_audits),
            "total_accepted_examples": sum(
                int(audit["accepted_examples"]) for audit in sampling_audits
            ),
            "total_candidate_examples": sum(
                int(audit["candidate_examples"]) for audit in sampling_audits
            ),
            "total_rejected_examples": sum(
                int(audit["rejected_examples"]) for audit in sampling_audits
            ),
            "total_split_violations": sum(
                int(audit["split_violations"] or 0) for audit in sampling_audits
            ),
        }
        training_sampling_audit["counter_arithmetic_exact"] = (
            training_sampling_audit["total_candidate_examples"]
            - training_sampling_audit["total_accepted_examples"]
            == training_sampling_audit["total_rejected_examples"]
        )
        if not (
            training_sampling_audit["all_fail_closed"]
            and training_sampling_audit["total_split_violations"] == 0
            and training_sampling_audit["counter_arithmetic_exact"]
            and training_sampling_audit["direct_conditioning_receipts_complete"]
            and training_sampling_audit["conditioned_sampler_backend_frozen"]
        ):
            raise RuntimeError(
                f"training word-product split audit failed: {training_sampling_audit}"
            )
        receipt = {
            **receipt_base,
            "status": "complete",
            "scientific_gate_status": "not_applicable" if not gates else ("pass" if all_gates_passed else "fail"),
            "grid_complete": grid["complete"],
            "all_gates_passed": all_gates_passed if gates else None,
            "arms": list(protocol["arms"]),
            "seeds": list(protocol["seeds"]),
            "transport_records": len(transport_records),
            "exact_oracle_passed": (
                oracle_record["integrity"]["passed"] if oracle_record is not None else None
            ),
            "training_sampling_audit": training_sampling_audit,
            "plots": plots,
            "environment": _environment(device, args.threads),
        }
        write_json(output_dir / "RECEIPT.json", receipt)
        (output_dir / "RUNNING.json").unlink()
        print(json.dumps(receipt, indent=2, sort_keys=True), flush=True)
        return 0
    except Exception as error:
        write_json(output_dir / "FAILED.json", {**receipt_base, "status": "failed", "error": repr(error), "traceback": traceback.format_exc()})
        raise


if __name__ == "__main__":
    raise SystemExit(main())
