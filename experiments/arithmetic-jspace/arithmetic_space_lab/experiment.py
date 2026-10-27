from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

from . import __version__
from .audit import AuditFailure, audit_dataset
from .core import seeded_rng, stable_hash
from .generate import canonical_json, generate, sha256_file
from .config import load_config
from .geometry import probe_checkpoint
from .paired_stats import paired_exact_group
from .tiny_model import ModelConfig
from .train_data import (
    apply_control_plan,
    deranged_control_plan,
    examples_fingerprint,
    load_sft_examples,
)
from .trainer import (
    TrainConfig,
    evaluate_generation,
    evaluate_loss,
    load_model_checkpoint,
    model_state_hash,
    resolve_device,
    runtime_information,
    train_arm,
    validate_lengths,
)
from .byte_tokenizer import ByteTokenizer


PACKAGE_ROOT = Path(__file__).resolve().parent.parent
RUN_SENTINEL = ".arithmetic_jspace_run"
RUN_SENTINEL_CONTENT = "arithmetic-jspace-owned-run-v1\n"


def _atomic_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _prepare_run(output: Path, resolved: dict[str, Any]) -> None:
    output = output.resolve()
    if output.exists() and any(output.iterdir()):
        sentinel = output / RUN_SENTINEL
        if not sentinel.is_file() or sentinel.read_text(encoding="utf-8") != RUN_SENTINEL_CONTENT:
            raise ValueError(f"refusing to use a non-owned nonempty run directory: {output}")
        existing_path = output / "resolved_experiment.json"
        if not existing_path.is_file():
            raise ValueError(f"owned run is missing resolved_experiment.json: {output}")
        existing = _load_json(existing_path)
        if canonical_json(existing) != canonical_json(resolved):
            raise ValueError(
                "existing run configuration differs; choose a different -Output or matching seed/profile"
            )
        return
    output.mkdir(parents=True, exist_ok=True)
    (output / RUN_SENTINEL).write_text(RUN_SENTINEL_CONTENT, encoding="utf-8", newline="\n")
    _atomic_json(resolved, output / "resolved_experiment.json")


def _data_stage(resolved: dict[str, Any], output: Path) -> tuple[Path, dict[str, Any]]:
    config_path = PACKAGE_ROOT / resolved["data_config"]
    data_config = load_config(config_path)
    data_config["seed"] = int(resolved["seed"])
    data_root = output / "data"
    reused = False
    if (data_root / "manifest.json").is_file():
        try:
            report = audit_dataset(data_root)
            saved = _load_json(data_root / "resolved_config.json")
            if canonical_json(saved) != canonical_json(data_config):
                raise ValueError("existing generated data configuration differs")
            reused = True
        except (AuditFailure, OSError, ValueError):
            report = {}
    else:
        report = {}
    if not reused:
        generate(data_config, data_root, overwrite=data_root.exists())
        report = audit_dataset(data_root)
    if report.get("status") != "PASS":
        raise RuntimeError("generated data did not pass its audit")
    print(
        f"DATA_STAGE=PASS DATA_REUSED={reused} CANONICAL_RECORDS={report['canonical_records']}",
        flush=True,
    )
    return data_root, report


def _control_plan(
    output: Path,
    regime: str,
    base_examples: list[Any],
) -> dict[str, Any]:
    path = output / "controls" / f"{regime}_derangement.json"
    expected = deranged_control_plan(base_examples, ByteTokenizer())
    if path.is_file():
        plan = _load_json(path)
        if canonical_json(plan) != canonical_json(expected):
            raise ValueError(f"existing control plan is stale or modified for regime {regime}")
    else:
        plan = expected
        _atomic_json(plan, path)
    expected_pairs = [base_examples[index].pair_id for index in plan["active_indices"]]
    if set(expected_pairs) != set(plan["assignment"]):
        raise ValueError(f"stale or invalid control plan for regime {regime}")
    if plan["active_rows"] < max(64, len(base_examples) // 5):
        raise ValueError(f"matched control retained too few rows for {regime}")
    return plan


def _fixed_behavior_subset(
    examples: list[Any], count: int, regime: str, split: str
) -> list[Any]:
    del regime  # Selection stays paired across response regimes for the same problems.
    return sorted(
        examples,
        key=lambda item: stable_hash(
            f"heldout-behavior-v1|{split}|{item.pair_id}"
        ),
    )[:count]


def _behavior_stage(
    *,
    output: Path,
    arm_summaries: dict[str, dict[str, Any]],
    arm_context: dict[str, dict[str, Any]],
    model_config: ModelConfig,
    train_config: TrainConfig,
    device: Any,
) -> dict[str, dict[str, Any]]:
    tokenizer = ByteTokenizer()
    reports: dict[str, dict[str, Any]] = {}
    for name, summary in arm_summaries.items():
        context = arm_context[name]
        regime = str(context["regime"])
        checkpoint_step = int(summary["optimizer_steps"])
        checkpoint = output / "arms" / name / f"checkpoint_step_{checkpoint_step:06d}.pt"
        if not checkpoint.is_file():
            raise FileNotFoundError(f"final behavior checkpoint is missing: {checkpoint}")
        checkpoint_sha256 = sha256_file(checkpoint)
        loss_subsets: dict[str, list[Any]] = {}
        generation_subsets: dict[str, list[Any]] = {}
        subset_metadata: dict[str, dict[str, Any]] = {}
        for split, examples in sorted(context["test_splits"].items()):
            loss_count = (
                len(examples)
                if train_config.heldout_loss_samples == 0
                else min(train_config.heldout_loss_samples, len(examples))
            )
            generation_count = min(
                train_config.heldout_generation_samples, len(examples)
            )
            loss_subset = _fixed_behavior_subset(examples, loss_count, regime, split)
            generation_subset = _fixed_behavior_subset(
                examples, generation_count, regime, split
            )
            if not loss_subset or not generation_subset:
                raise ValueError(f"held-out behavior split is empty: {regime}/{split}")
            validate_lengths(
                loss_subset,
                tokenizer,
                model_config.max_seq_len,
                f"{name} held-out {split}",
            )
            longest_completion = max(
                len(tokenizer.encode(item.completion)) + 1 for item in loss_subset
            )
            loss_subsets[split] = loss_subset
            generation_subsets[split] = generation_subset
            subset_metadata[split] = {
                "available_examples": len(examples),
                "loss_evaluated_examples": len(loss_subset),
                "generation_evaluated_examples": len(generation_subset),
                "loss_examples_sha256": examples_fingerprint(
                    loss_subset, regime, split
                ),
                "generation_examples_sha256": examples_fingerprint(
                    generation_subset, regime, split
                ),
                "longest_completion_tokens_including_eos": longest_completion,
            }
        evaluation_configuration_sha256 = stable_hash(
            canonical_json(
                {
                    "schema": "heldout-behavior-v2",
                    "checkpoint_sha256": checkpoint_sha256,
                    "regime": regime,
                    "target_source": "correct_heldout_oracle",
                    "eval_batch_size": train_config.eval_batch_size,
                    "max_new_tokens": train_config.max_new_tokens,
                    "subsets": subset_metadata,
                }
            )
        )
        report_path = output / "behavior" / f"{name}.json"
        model, payload = load_model_checkpoint(checkpoint, model_config, device)
        if int(payload.get("step", -1)) != checkpoint_step:
            raise RuntimeError(f"final checkpoint step mismatch: {checkpoint}")
        if payload.get("fingerprint") != summary.get("fingerprint"):
            raise RuntimeError(f"final checkpoint fingerprint mismatch: {checkpoint}")
        if model_state_hash(model) != summary.get("final_model_hash"):
            raise RuntimeError(f"final checkpoint model hash mismatch: {checkpoint}")
        del payload
        if report_path.is_file():
            report = _load_json(report_path)
            report_splits = report.get("splits")
            if (
                report.get("status") != "PASS"
                or report.get("schema_version") != "2.0"
                or report.get("arm") != name
                or report.get("regime") != regime
                or report.get("checkpoint_step") != checkpoint_step
                or report.get("checkpoint_file_sha256") != checkpoint_sha256
                or report.get("evaluation_configuration_sha256")
                != evaluation_configuration_sha256
                or report.get("target_source") != "correct_heldout_oracle"
                or not isinstance(report_splits, dict)
                or set(report_splits) != set(loss_subsets)
            ):
                raise RuntimeError(f"stale or incomplete behavior report: {report_path}")
            for split, expected_metadata in subset_metadata.items():
                split_report = report_splits[split]
                if (
                    not isinstance(split_report, dict)
                    or any(
                        split_report.get(key) != value
                        for key, value in expected_metadata.items()
                    )
                    or not isinstance(split_report.get("loss"), dict)
                    or not isinstance(split_report.get("generation"), dict)
                    or not {
                        "loss",
                        "token_accuracy",
                        "target_tokens",
                    }.issubset(split_report["loss"])
                    or not {
                        "raw_exact_match",
                        "answer_exact_match",
                        "answer_exact_count",
                        "eos_rate",
                        "examples",
                        "items",
                    }.issubset(split_report["generation"])
                    or split_report["generation"].get("examples")
                    != expected_metadata["generation_evaluated_examples"]
                    or len(split_report["generation"].get("items", []))
                    != expected_metadata["generation_evaluated_examples"]
                    or {
                        item.get("pair_id")
                        for item in split_report["generation"].get("items", [])
                        if isinstance(item, dict)
                    }
                    != {item.pair_id for item in generation_subsets[split]}
                ):
                    raise RuntimeError(
                        f"stale or incomplete behavior split report: {report_path} ({split})"
                    )
            print(f"BEHAVIOR_ARM={name} STATUS=REUSED", flush=True)
        else:
            split_reports: dict[str, dict[str, Any]] = {}
            for split, loss_subset in loss_subsets.items():
                loss = evaluate_loss(
                    model,
                    loss_subset,
                    tokenizer,
                    device,
                    train_config.eval_batch_size,
                )
                generation = evaluate_generation(
                    model,
                    generation_subsets[split],
                    tokenizer,
                    device,
                    train_config.max_new_tokens,
                    batch_size=train_config.eval_batch_size,
                    retain_items=True,
                )
                split_reports[split] = {
                    **subset_metadata[split],
                    "loss": loss,
                    "generation": generation,
                }
                print(
                    f"BEHAVIOR_ARM={name} SPLIT={split} STATUS=PASS "
                    f"ANSWER_EXACT={generation['answer_exact_count']}/{generation['examples']} "
                    f"RATE={generation['answer_exact_match']:.6f}",
                    flush=True,
                )
            report = {
                "status": "PASS",
                "schema_version": "2.0",
                "arm": name,
                "regime": regime,
                "checkpoint_step": checkpoint_step,
                "checkpoint_file_sha256": checkpoint_sha256,
                "evaluation_configuration_sha256": evaluation_configuration_sha256,
                "target_source": "correct_heldout_oracle",
                "splits": split_reports,
            }
            _atomic_json(report, report_path)
        reports[name] = report
        del model
        if device.type == "cuda":
            import torch

            torch.cuda.empty_cache()
    return reports


def _paired_behavior_stage(
    *,
    resolved: dict[str, Any],
    behavior_reports: dict[str, dict[str, Any]],
    output: Path,
    seed: int,
) -> dict[str, Any]:
    data_configuration = load_config(PACKAGE_ROOT / resolved["data_config"])
    required_iid_operations = {
        operation
        for operation, weight in data_configuration["operations"].items()
        if float(weight) > 0
    }
    by_regime: dict[str, dict[str, str]] = {}
    for arm in resolved["arms"]:
        control = str(arm["control"])
        if control in {"correct", "shuffled"}:
            by_regime.setdefault(str(arm["regime"]), {})[control] = str(arm["name"])

    comparisons: dict[str, Any] = {}
    for regime, arms in sorted(by_regime.items()):
        if set(arms) != {"correct", "shuffled"}:
            continue
        correct_report = behavior_reports[arms["correct"]]
        shuffled_report = behavior_reports[arms["shuffled"]]
        split_reports: dict[str, Any] = {}
        for split in sorted(set(correct_report["splits"]) & set(shuffled_report["splits"])):
            correct_items = {
                item["pair_id"]: item
                for item in correct_report["splits"][split]["generation"]["items"]
            }
            shuffled_items = {
                item["pair_id"]: item
                for item in shuffled_report["splits"][split]["generation"]["items"]
            }
            if set(correct_items) != set(shuffled_items):
                raise RuntimeError(f"paired behavior item mismatch for {regime}/{split}")
            pairs = [
                (correct_items[pair_id], shuffled_items[pair_id])
                for pair_id in sorted(correct_items)
            ]
            overall = paired_exact_group(pairs)
            differences = [
                int(bool(correct["answer_exact_match"]))
                - int(bool(shuffled["answer_exact_match"]))
                for correct, shuffled in pairs
            ]
            rng = seeded_rng(seed, "paired-behavior-bootstrap-v1", regime, split)
            replicates = 2000
            bootstrap = sorted(
                sum(differences[rng.randrange(len(differences))] for _ in differences)
                / len(differences)
                for _ in range(replicates)
            )
            overall["paired_bootstrap_replicates"] = replicates
            overall["rate_difference_bootstrap_95_ci"] = [
                bootstrap[int(0.025 * (replicates - 1))],
                bootstrap[int(0.975 * (replicates - 1))],
            ]
            by_operation: dict[str, Any] = {}
            for operation in sorted({correct["operation"] for correct, _ in pairs}):
                by_operation[operation] = paired_exact_group(
                    [pair for pair in pairs if pair[0]["operation"] == operation]
                )
            by_difficulty: dict[str, Any] = {}
            for difficulty in sorted({int(correct["difficulty"]) for correct, _ in pairs}):
                by_difficulty[str(difficulty)] = paired_exact_group(
                    [pair for pair in pairs if int(pair[0]["difficulty"]) == difficulty]
                )
            split_reports[split] = {
                "overall": overall,
                "by_operation": by_operation,
                "by_difficulty": by_difficulty,
            }
            print(
                f"PAIRED_BEHAVIOR REGIME={regime} SPLIT={split} "
                f"CORRECT={overall['correct_exact_count']}/{overall['examples']} "
                f"SHUFFLED={overall['shuffled_exact_count']}/{overall['examples']} "
                f"DELTA={overall['rate_difference']:.6f} "
                f"MCNEMAR_P={overall['mcnemar_exact_two_sided_p']:.6g}",
                flush=True,
            )

        iid = split_reports.get("test_iid", {}).get("overall", {})
        iid_operations = split_reports.get("test_iid", {}).get("by_operation", {})
        competence_pass = bool(
            iid
            and iid.get("correct_exact_rate", 0.0) >= 0.50
            and iid.get("rate_difference", 0.0) >= 0.20
            and iid.get("mcnemar_exact_two_sided_p", 1.0) < 0.05
            and iid.get("rate_difference_bootstrap_95_ci", [0.0])[0] > 0.0
            and set(iid_operations) == required_iid_operations
            and all(value["correct_exact_count"] > 0 for value in iid_operations.values())
        )
        comparisons[regime] = {
            "correct_arm": arms["correct"],
            "shuffled_arm": arms["shuffled"],
            "splits": split_reports,
            "arithmetic_competence_gate": "PASS" if competence_pass else "NOT_REACHED",
            "gate_thresholds": {
                "iid_correct_exact_rate_minimum": 0.50,
                "iid_correct_minus_shuffled_minimum": 0.20,
                "mcnemar_p_maximum": 0.05,
                "bootstrap_ci_lower_must_exceed_zero": True,
                "every_iid_operation_requires_a_correct_item": True,
                "required_iid_operations": sorted(required_iid_operations),
            },
        }
        print(
            f"ARITHMETIC_COMPETENCE_GATE REGIME={regime} "
            f"STATUS={comparisons[regime]['arithmetic_competence_gate']}",
            flush=True,
        )

    report = {
        "status": "PASS",
        "schema_version": "1.0",
        "comparisons": comparisons,
    }
    _atomic_json(report, output / "behavior" / "paired_comparisons.json")
    return report


def run_experiment(
    profile: str,
    output: str | Path,
    seed: int,
    device_name: str,
    resume: bool = True,
) -> dict[str, Any]:
    profile_path = PACKAGE_ROOT / "training_configs" / f"{profile}.json"
    if not profile_path.is_file():
        raise ValueError(f"unknown experiment profile: {profile}")
    resolved = _load_json(profile_path)
    resolved["profile"] = profile
    resolved["seed"] = int(seed)
    resolved["device"] = device_name
    resolved["schema_version"] = "1.0"
    resolved["package_version"] = __version__
    resolved["profile_configuration_sha256"] = sha256_file(profile_path)
    data_config_path = PACKAGE_ROOT / resolved["data_config"]
    resolved["data_configuration_sha256"] = stable_hash(
        canonical_json(load_config(data_config_path))
    )
    manifest_path = PACKAGE_ROOT / "PACKAGE_MANIFEST.sha256"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"package manifest is missing: {manifest_path}")
    resolved["package_manifest_sha256"] = sha256_file(manifest_path)
    output_path = Path(output).resolve()
    try:
        output_path.relative_to(PACKAGE_ROOT.resolve())
    except ValueError:
        pass
    else:
        raise ValueError(
            f"run output must be outside the immutable package directory: {output_path}"
        )
    _prepare_run(output_path, resolved)
    device = resolve_device(device_name)
    runtime = runtime_information(device)
    _atomic_json(runtime, output_path / "runtime.json")
    print(
        f"TRAINING_DEVICE={runtime['device']} TORCH={runtime['torch']} "
        f"GPU={runtime.get('gpu', 'none')}",
        flush=True,
    )
    data_root, data_report = _data_stage(resolved, output_path)
    model_config = ModelConfig.from_dict(resolved["model"])
    train_config = TrainConfig.from_dict(resolved["training"])
    arm_summaries: dict[str, dict[str, Any]] = {}
    arm_context: dict[str, dict[str, Any]] = {}
    base_cache: dict[str, list[Any]] = {}
    validation_cache: dict[str, list[Any]] = {}
    test_cache: dict[str, dict[str, list[Any]]] = {}
    plans: dict[str, dict[str, Any]] = {}
    test_splits = sorted(
        split for split in data_report["counts"] if str(split).startswith("test_")
    )
    if not test_splits:
        raise ValueError("generated data has no held-out test_* split")
    started = time.perf_counter()

    for arm in resolved["arms"]:
        name = str(arm["name"])
        regime = str(arm["regime"])
        if arm["control"] not in {"correct", "shuffled"}:
            raise ValueError(f"unsupported control type for {name}: {arm['control']}")
        if regime not in base_cache:
            base_cache[regime] = load_sft_examples(data_root, regime, "train")
            validation_cache[regime] = load_sft_examples(data_root, regime, "validation")
            test_cache[regime] = {
                split: load_sft_examples(data_root, regime, split)
                for split in test_splits
            }
        base = base_cache[regime]
        if bool(arm.get("matched_control", False)):
            if regime not in plans:
                plans[regime] = _control_plan(output_path, regime, base)
            plan = plans[regime]
            train_examples = apply_control_plan(
                base, plan, shuffled=arm["control"] == "shuffled"
            )
            plan_hash = stable_hash(canonical_json(plan))
        else:
            if arm["control"] != "correct":
                raise ValueError("an unmatched shuffled arm is not permitted")
            train_examples = base
            plan_hash = "none"
        base_fingerprint = examples_fingerprint(base, regime, "train")
        data_fingerprint = stable_hash(
            f"{base_fingerprint}|{plan_hash}|{arm['control']}|{len(train_examples)}"
        )
        arm_output = output_path / "arms" / name
        summary = train_arm(
            arm_name=name,
            stream_key=str(arm["stream_key"]),
            train_examples=train_examples,
            validation_examples=validation_cache[regime],
            model_config=model_config,
            train_config=train_config,
            output=arm_output,
            device=device,
            seed=int(seed),
            data_fingerprint=data_fingerprint,
            resume=resume,
        )
        arm_summaries[name] = summary
        arm_context[name] = {
            "regime": regime,
            "validation": validation_cache[regime],
            "test": test_cache[regime]["test_iid"],
            "test_splits": test_cache[regime],
        }
        if device.type == "cuda":
            import torch

            torch.cuda.empty_cache()

    initial_hashes = {summary["initial_model_hash"] for summary in arm_summaries.values()}
    if len(initial_hashes) != 1:
        raise RuntimeError("experimental arms did not start from identical model weights")
    if any(summary["final_model_hash"] == summary["initial_model_hash"] for summary in arm_summaries.values()):
        raise RuntimeError("at least one trained arm did not change its weights")
    matched_curricula: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for arm in resolved["arms"]:
        if bool(arm.get("matched_control", False)):
            key = (str(arm["regime"]), str(arm["stream_key"]))
            matched_curricula.setdefault(key, []).append(
                arm_summaries[str(arm["name"])]["curriculum"]
            )
    for key, curricula in matched_curricula.items():
        fingerprints = {
            canonical_json(
                [
                    (
                        stage["name"],
                        stage["end_step"],
                        stage["eligible_examples"],
                        stage["eligible_pair_fingerprint"],
                    )
                    for stage in curriculum
                ]
            )
            for curriculum in curricula
        }
        if len(fingerprints) != 1:
            raise RuntimeError(
                f"matched arms did not use identical curriculum pools: {key}"
            )

    behavior_reports = _behavior_stage(
        output=output_path,
        arm_summaries=arm_summaries,
        arm_context=arm_context,
        model_config=model_config,
        train_config=train_config,
        device=device,
    )
    paired_behavior = _paired_behavior_stage(
        resolved=resolved,
        behavior_reports=behavior_reports,
        output=output_path,
        seed=int(seed),
    )

    probe_config = resolved["probe"]
    expected_probe_fingerprint = stable_hash(
        canonical_json(
            {
                "rank": int(probe_config["rank"]),
                "layer": int(probe_config["layer"]),
                "activation_samples": int(probe_config["activation_samples"]),
                "gradient_samples": int(probe_config["gradient_samples"]),
                "jacobian_projections": int(probe_config["jacobian_projections"]),
                "random_controls": int(probe_config["random_controls"]),
                "batch_size": int(probe_config["batch_size"]),
                "ridge": float(probe_config["ridge"]),
                "seed": int(seed),
            }
        )
    )
    geometry_reports: dict[str, dict[str, Any]] = {}
    for name, context in arm_context.items():
        for step in probe_config["checkpoint_steps"]:
            checkpoint = output_path / "arms" / name / f"checkpoint_step_{int(step):06d}.pt"
            if not checkpoint.is_file():
                raise FileNotFoundError(f"probe checkpoint is missing: {checkpoint}")
            report_path = output_path / "geometry" / name / f"step_{int(step):06d}.json"
            if report_path.is_file():
                report = _load_json(report_path)
                if (
                    report.get("status") != "PASS"
                    or report.get("checkpoint_step") != int(step)
                    or report.get("checkpoint_file_sha256") != sha256_file(checkpoint)
                    or report.get("probe_configuration_sha256") != expected_probe_fingerprint
                ):
                    raise RuntimeError(f"stale or incomplete geometry report: {report_path}")
                print(f"GEOMETRY_ARM={name} STEP={step} STATUS=REUSED", flush=True)
            else:
                report = probe_checkpoint(
                    checkpoint=checkpoint,
                    model_config=model_config,
                    discovery_examples=context["validation"],
                    sealed_examples=context["test"],
                    device=device,
                    output=report_path,
                    rank=int(probe_config["rank"]),
                    layer=int(probe_config["layer"]),
                    activation_samples=int(probe_config["activation_samples"]),
                    gradient_samples=int(probe_config["gradient_samples"]),
                    jacobian_projections=int(probe_config["jacobian_projections"]),
                    random_controls=int(probe_config["random_controls"]),
                    batch_size=int(probe_config["batch_size"]),
                    ridge=float(probe_config["ridge"]),
                    seed=int(seed),
                )
                print(
                    f"GEOMETRY_ARM={name} STEP={step} STATUS=PASS "
                    f"J_U_OVERLAP="
                    f"{report['overlaps']['jacobian_update__future_update_crosscov']:.6f}",
                    flush=True,
                )
            geometry_reports[f"{name}:{step}"] = report

    summary = {
        "status": "PASS",
        "experiment_name": resolved["experiment_name"],
        "profile": profile,
        "seed": seed,
        "device": str(device),
        "data_records": data_report["canonical_records"],
        "arms": arm_summaries,
        "heldout_behavior": {
            name: {
                "checkpoint_step": value["checkpoint_step"],
                "target_source": value["target_source"],
                "splits": {
                    split: {
                        "available_examples": split_report["available_examples"],
                        "loss_evaluated_examples": split_report[
                            "loss_evaluated_examples"
                        ],
                        "generation_evaluated_examples": split_report[
                            "generation_evaluated_examples"
                        ],
                        "loss": split_report["loss"],
                        "raw_exact_match": split_report["generation"]["raw_exact_match"],
                        "answer_exact_match": split_report["generation"]["answer_exact_match"],
                        "answer_exact_count": split_report["generation"][
                            "answer_exact_count"
                        ],
                        "eos_rate": split_report["generation"]["eos_rate"],
                    }
                    for split, split_report in value["splits"].items()
                },
            }
            for name, value in behavior_reports.items()
        },
        "paired_behavior": paired_behavior,
        "geometry_reports": {
            key: {
                "checkpoint_step": value["checkpoint_step"],
                "claim_status": value["claim_status"],
                "overlaps": value["overlaps"],
                "candidate_ablation": value["candidate_ablation"],
                "energy_matched_random_ablation_mean": value[
                    "energy_matched_random_ablation_mean"
                ],
            }
            for key, value in geometry_reports.items()
        },
        "scientific_claim": "NOT_ESTABLISHED",
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "result_path": str(output_path),
    }
    _atomic_json(summary, output_path / "experiment_summary.json")
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run arithmetic training and candidate-space probes.")
    parser.add_argument(
        "--profile",
        choices=[
            "smoke",
            "balanced",
            "symbolic_only",
            "deep_symbolic",
            "emergence_longitudinal",
        ],
        required=True,
    )
    parser.add_argument("--output", required=True)
    parser.add_argument("--seed", type=int, default=314159)
    parser.add_argument("--device", choices=["cuda", "cpu", "auto"], default="cuda")
    parser.add_argument("--no-resume", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_experiment(
            args.profile,
            args.output,
            args.seed,
            args.device,
            resume=not args.no_resume,
        )
        print("TRAINING_AND_PROBE_PIPELINE=PASS")
        print("ACTUAL_MODEL_TRAINING=PASS")
        print("JSPACE_CLAIM=NOT_ESTABLISHED")
        print(
            "OPTIMIZER_STEPS="
            + json.dumps(
                {name: arm["optimizer_steps"] for name, arm in result["arms"].items()},
                sort_keys=True,
            )
        )
        print(f"RESULT_PATH={result['result_path']}")
        return 0
    except (AuditFailure, FileNotFoundError, OSError, RuntimeError, ValueError) as error:
        print(f"TRAINING_AND_PROBE_PIPELINE=FAIL: {error}", file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
