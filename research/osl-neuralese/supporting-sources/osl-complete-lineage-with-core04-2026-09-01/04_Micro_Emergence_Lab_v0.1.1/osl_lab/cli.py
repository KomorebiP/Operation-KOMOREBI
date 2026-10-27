"""Command-line entry point for the completely offline Micro OSL lab."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any, Mapping, Sequence

import numpy as np

from .baselines import run_baselines
from .generator import (
    DatasetConfig,
    EVALUATION_SPLITS,
    SPLITS,
    load_dataset,
    write_dataset,
)
from .manifest import verify_manifest
from .reporting import build_report
from .soft_quotient import (
    exact_partition,
    fit_soft_quotient,
    json_ready,
    temperature_hardening_sweep,
)
from .utils import (
    environment_report,
    load_json,
    resolve_device,
    save_json,
    sha256_file,
    write_jsonl,
)
from .verification import verify_project
from .worlds import (
    WORLDS,
    apply_operator,
    canonical_json,
    enumerate_states,
    query_answers,
    verify_declared_laws,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRESETS = ("smoke", "standard", "confirmatory", "full")
ARMS = (
    "answer_only",
    "role_bind_augmented",
    "role_bind_scrambled",
    "state_supervised",
    "equivalence_regularized",
    "operator_regularized",
    "combined",
)

CENTRAL_ARMS = (
    "answer_only",
    "role_bind_augmented",
    "role_bind_scrambled",
)

INITIALIZATION_CONTRACT_FIELDS = (
    "tokenizer_sha256",
    "answer_classes_sha256",
    "model_parameter_schema_sha256",
    "initial_model_sha256",
)


def _resolved_data_seed(args: argparse.Namespace) -> int:
    value = getattr(args, "data_seed", None)
    return int(args.seed if value is None else value)


def _resolved_model_seed(args: argparse.Namespace) -> int:
    value = getattr(args, "model_seed", None)
    return int(args.seed if value is None else value)


def _count_jsonl(path: Path) -> int:
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def _portable_environment_report() -> dict[str, Any]:
    report = environment_report()
    executable = report.pop("executable", None)
    report.pop("cwd", None)
    if executable:
        report["python_executable_name"] = Path(str(executable)).name
    return report


def _audit_initialization_contracts(
    experiments: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Require matched central arms to share labels, shapes, and exact bytes."""

    relevant = [item for item in experiments if str(item.get("arm")) in CENTRAL_ARMS]
    contracts = {
        str(item["arm"]): dict(item.get("initialization_contract") or {})
        for item in relevant
    }
    duplicate_arms = sorted(
        arm
        for arm in CENTRAL_ARMS
        if sum(str(item.get("arm")) == arm for item in relevant) > 1
    )
    checks: dict[str, Any] = {}
    for field in INITIALIZATION_CONTRACT_FIELDS:
        values = {arm: contract.get(field) for arm, contract in sorted(contracts.items())}
        populated = [value for value in values.values() if value]
        checks[field] = {
            "values": values,
            "status": "PASS"
            if len(populated) == len(values) and len(set(populated)) <= 1
            else "FAIL",
        }
    status = "PASS" if not duplicate_arms and all(
        check["status"] == "PASS" for check in checks.values()
    ) else "FAIL"
    return {
        "status": status,
        "criterion": (
            "central arms must share the exact tokenizer, answer-label ordering, "
            "parameter schema, and initialized model bytes"
        ),
        "arms": {
            arm: contract.get("initial_model_sha256")
            for arm, contract in sorted(contracts.items())
        },
        "checks": checks,
        "duplicate_arms": duplicate_arms,
        "not_run": not relevant,
    }


def _snapshot_reproducibility(output: Path, config_source: Path) -> dict[str, Any]:
    destination = output / "reproducibility"
    destination.mkdir(parents=True, exist_ok=True)
    copied: list[dict[str, Any]] = []
    candidates = [
        (config_source, "config_source.json"),
        (PROJECT_ROOT / "MANIFEST.json", "PACKAGE_MANIFEST.json"),
        (PROJECT_ROOT / "SHA256SUMS.txt", "PACKAGE_SHA256SUMS.txt"),
        (PROJECT_ROOT / "pyproject.toml", "pyproject.toml"),
        (PROJECT_ROOT / "requirements.txt", "requirements.txt"),
        (PROJECT_ROOT / "requirements-minimal.txt", "requirements-minimal.txt"),
        (PROJECT_ROOT / "environment-lock-known-good.txt", "environment-lock-known-good.txt"),
    ]
    for source, name in candidates:
        if not source.is_file():
            continue
        target = destination / name
        shutil.copy2(source, target)
        copied.append(
            {
                "path": f"reproducibility/{name}",
                "size_bytes": target.stat().st_size,
                "sha256": sha256_file(target),
            }
        )
    manifest = {
        "schema": "osl.micro-emergence.reproducibility-bundle.v1",
        "files": copied,
    }
    save_json(destination / "REPRODUCIBILITY_MANIFEST.json", manifest)
    return manifest


def _config_path(preset: str) -> Path:
    return PROJECT_ROOT / "configs" / f"{preset}.json"


def _load_config(path: str | None, preset: str | None) -> dict[str, Any]:
    source = Path(path).resolve() if path else _config_path(preset or "standard")
    config = load_json(source)
    config["_source"] = str(source)
    return config


def _output_dir(value: str | None, command: str) -> Path:
    target = Path(value).resolve() if value else (PROJECT_ROOT / "results" / command).resolve()
    target.mkdir(parents=True, exist_ok=True)
    return target


def _dataset_dir(args: argparse.Namespace) -> Path:
    value = getattr(args, "data_dir", None) or getattr(args, "output_dir", None)
    return Path(value).resolve() if value else (PROJECT_ROOT / "results" / "data").resolve()


def _dataset_config(config: Mapping[str, Any], seed: int | None) -> DatasetConfig:
    payload = deepcopy(dict(config.get("dataset", {})))
    if seed is not None:
        payload["seed"] = int(seed)
    return DatasetConfig.from_dict(payload)


def _evaluation_records(dataset: Mapping[str, Sequence[Mapping[str, Any]]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for split in EVALUATION_SPLITS:
        records.extend(dict(item) for item in dataset.get(split, []))
    return records


def _training_config(
    config: Mapping[str, Any], arm: str, seed: int, architecture: str = "transformer"
) -> dict[str, Any]:
    if architecture != "transformer":
        raise ValueError("v0.1 supports the from-scratch transformer architecture only")
    payload = deepcopy(dict(config.get("training", {})))
    payload.pop("arms", None)
    payload.pop("architectures", None)
    payload.pop("default_arm", None)
    payload["arm"] = arm
    payload["seed"] = int(seed)
    if "mixed_precision" in payload:
        payload["amp"] = bool(payload.pop("mixed_precision"))
    model = dict(payload.get("model", {}))
    if "max_length" in model:
        payload["max_length"] = int(model["max_length"])
    weights = dict(payload.get("loss_weights", {}))
    if "operator" in weights:
        combined = float(weights.pop("operator"))
        weights.setdefault("operator_alignment", combined / 2.0)
        weights.setdefault("operator_laws", combined / 2.0)
    payload["loss_weights"] = weights
    return payload


def command_doctor(args: argparse.Namespace) -> bool:
    output = _output_dir(args.output_dir, "doctor")
    report = _portable_environment_report()
    report["schema"] = "osl.micro-emergence.doctor.v1"
    report["requested_device"] = args.device
    report["offline_contract"] = {
        "external_dataset_required": False,
        "pretrained_checkpoint_required": False,
        "network_required_for_run": False,
    }
    base_ready = all(
        bool(report["modules"].get(name, {}).get("installed")) for name in ("numpy", "sklearn")
    )
    try:
        report["resolved_device"] = resolve_device(args.device)
        device_ready = True
    except Exception as exc:
        report["device_error"] = f"{type(exc).__name__}: {exc}"
        device_ready = False
    report["neural_ready"] = bool(report["modules"].get("torch", {}).get("installed"))
    report["report_ready"] = bool(
        report["modules"].get("matplotlib", {}).get("installed")
    )
    report["base_ready"] = base_ready
    report["neural_required"] = bool(args.require_neural or args.device == "cuda")
    neural_ok = report["neural_ready"] or not report["neural_required"]
    reports_ok = report["report_ready"] or not args.require_neural
    report["full_runtime_ready"] = bool(base_ready and report["neural_ready"] and report["report_ready"])
    report["status"] = (
        "PASS" if base_ready and device_ready and neural_ok and reports_ok else "FAIL"
    )
    save_json(output / "environment_report.json", report)
    print(json.dumps({key: report.get(key) for key in ("status", "resolved_device", "neural_ready")}, sort_keys=True))
    return report["status"] == "PASS"


def command_generate(args: argparse.Namespace) -> dict[str, Any]:
    config = _load_config(args.config, args.preset)
    output = _output_dir(args.output_dir, "generate")
    existing = output / "manifest.json"
    if existing.exists() and not args.force:
        raise FileExistsError(f"dataset already exists at {output}; pass --force to regenerate it")
    manifest = write_dataset(output, _dataset_config(config, _resolved_data_seed(args)))
    save_json(output / "dataset_manifest.json", manifest)
    print(f"generated {sum(item['records'] for item in manifest['files'].values())} records")
    return manifest


def command_validate(args: argparse.Namespace) -> dict[str, Any]:
    from .validation import validate_dataset

    source = _dataset_dir(args)
    output = _output_dir(args.output_dir, "validate")
    result = validate_dataset(source)
    payload = result.to_dict()
    save_json(output / "validation_report.json", payload)
    print(json.dumps({"status": "PASS" if result.ok else "FAIL", "source": source.name}, sort_keys=True))
    if not result.ok:
        raise RuntimeError("dataset validation failed; inspect validation_report.json")
    return payload


def command_baselines(args: argparse.Namespace) -> dict[str, Any]:
    config = _load_config(args.config, args.preset)
    source = _dataset_dir(args)
    output = _output_dir(args.output_dir, "baselines")
    dataset = load_dataset(source)
    train = dataset.get("train", [])
    evaluation = _evaluation_records(dataset)
    baseline_config = dict(config.get("baselines", {}))
    tfidf_config = {
        "max_features": int(baseline_config.get("tfidf_max_features", 100_000)),
        "seed": _resolved_data_seed(args),
    }
    result = run_baselines(
        train,
        evaluation,
        include_tfidf=bool(baseline_config.get("tfidf", True)),
        tfidf_config=tfidf_config,
    )
    result["train_records"] = len(train)
    result["evaluation_records"] = len(evaluation)
    save_json(output / "baseline_results.json", result)
    print(f"completed baselines on {len(evaluation)} evaluation records")
    return result


def command_train(args: argparse.Namespace) -> dict[str, Any]:
    from .training import train_from_jsonl_files, train_from_jsonl_replacement

    config = _load_config(args.config, args.preset)
    source = _dataset_dir(args)
    output = _output_dir(args.output_dir, "train")
    if (output / "training_summary.json").exists() and not args.force:
        raise FileExistsError(f"training output already exists at {output}; pass --force or resume")
    training = dict(config.get("training", {}))
    arm = args.arm or str(training.get("default_arm", "answer_only"))
    architecture = args.architecture or str((training.get("architectures") or ["transformer"])[0])
    training_paths = [source / "train.jsonl"]
    augmentation_names = {
        "role_bind_augmented": "renaming_train.jsonl",
        "role_bind_scrambled": "renaming_scrambled_train.jsonl",
    }
    if arm in augmentation_names:
        augmentation = source / augmentation_names[arm]
        if not augmentation.is_file():
            raise FileNotFoundError(
                f"{arm} requires {augmentation.name} in the dataset directory"
            )
        training_paths.append(augmentation)
    tokenizer_paths = [source / "train.jsonl"]
    for name in ("renaming_train.jsonl", "renaming_scrambled_train.jsonl"):
        candidate = source / name
        if candidate.is_file():
            tokenizer_paths.append(candidate)
    validation_path = source / "iid_validation.jsonl"
    if not validation_path.is_file():
        legacy = source / "iid.jsonl"
        if legacy.is_file():
            validation_path = legacy
        else:
            raise FileNotFoundError("iid_validation.jsonl is required for checkpoint selection")
    model_seed = _resolved_model_seed(args)
    training_config = _training_config(config, arm, model_seed, architecture)
    if arm in augmentation_names:
        result = train_from_jsonl_replacement(
            training_paths[0],
            training_paths[1],
            validation_path,
            output,
            training_config,
            resume=args.resume,
            device=args.device,
            tokenizer_paths=tokenizer_paths,
        )
    else:
        result = train_from_jsonl_files(
            training_paths,
            validation_path,
            output,
            training_config,
            resume=args.resume,
            device=args.device,
            tokenizer_paths=tokenizer_paths,
        )
    checkpoint_path = Path(result["checkpoint"]).resolve()
    last_checkpoint_path = Path(result["last_checkpoint"]).resolve()
    result["model_seed"] = int(result.get("model_seed", model_seed))
    if args.resume is not None:
        result["resume_requested_model_seed"] = model_seed
    result["training_sources"] = [
        {
            "path": path.name,
            "records": _count_jsonl(path),
            "sha256": sha256_file(path),
        }
        for path in training_paths
    ]
    result["tokenizer_sources"] = [
        {
            "path": path.name,
            "records": _count_jsonl(path),
            "sha256": sha256_file(path),
        }
        for path in tokenizer_paths
    ]
    result["validation_source"] = {
        "path": validation_path.name,
        "records": _count_jsonl(validation_path),
        "sha256": sha256_file(validation_path),
    }
    result["architecture"] = architecture
    result["checkpoint_sha256"] = sha256_file(checkpoint_path)
    result["last_checkpoint_sha256"] = sha256_file(last_checkpoint_path)
    result["checkpoint"] = checkpoint_path.name
    result["last_checkpoint"] = last_checkpoint_path.name
    save_json(output / "training_summary.json", result)
    result["_checkpoint_path"] = str(checkpoint_path)
    result["_last_checkpoint_path"] = str(last_checkpoint_path)
    print(f"trained {architecture}/{arm}; checkpoint: {checkpoint_path.name}")
    return result


def _evaluate_checkpoint(
    checkpoint: str | Path,
    source: Path,
    output: Path,
    config: Mapping[str, Any],
    device: str,
    seed: int,
) -> dict[str, Any]:
    from .training import evaluate_checkpoint
    from .metrics import bootstrap_accuracy_interval

    records = _evaluation_records(load_dataset(source))
    if not records:
        raise ValueError(f"no evaluation records found in {source}")
    batch_size = int(dict(config.get("evaluation", {})).get("batch_size", 128))
    with tempfile.TemporaryDirectory(prefix="osl-evaluation-") as temporary:
        combined = Path(temporary) / "all_evaluation.jsonl"
        write_jsonl(combined, records)
        result = evaluate_checkpoint(
            checkpoint,
            combined,
            output_path=output / "evaluation_results.json",
            batch_size=batch_size,
            device=device,
        )
    result["checkpoint"] = Path(checkpoint).name
    evaluation_config = dict(config.get("evaluation", {}))
    bootstrap_samples = int(evaluation_config.get("bootstrap_samples", 0))
    if bootstrap_samples > 0:
        predictions = list(result.get("predictions", []))
        result["bootstrap_accuracy"] = bootstrap_accuracy_interval(
            [record.get("answer", "") for record in records],
            predictions,
            samples=bootstrap_samples,
            seed=seed,
        )
        split_intervals: dict[str, Any] = {}
        for split in sorted({str(record.get("split", "unspecified")) for record in records}):
            indices = [index for index, record in enumerate(records) if str(record.get("split")) == split]
            split_intervals[split] = bootstrap_accuracy_interval(
                [records[index].get("answer", "") for index in indices],
                [predictions[index] for index in indices],
                samples=bootstrap_samples,
                seed=seed,
            )
        result["bootstrap_accuracy_by_split"] = split_intervals
    if not bool(evaluation_config.get("save_predictions", True)):
        result.pop("record_ids", None)
        result.pop("predictions", None)
        result.pop("state_predictions", None)
    save_json(output / "evaluation_results.json", result)
    return result


def command_evaluate(args: argparse.Namespace) -> dict[str, Any]:
    if not args.checkpoint:
        raise ValueError("--checkpoint is required for evaluate")
    config = _load_config(args.config, args.preset)
    source = _dataset_dir(args)
    output = _output_dir(args.output_dir, "evaluate")
    result = _evaluate_checkpoint(
        args.checkpoint,
        source,
        output,
        config,
        args.device,
        _resolved_model_seed(args),
    )
    print(f"evaluated {result['n']} records")
    return result


def _world_system(world: str) -> tuple[dict[str, np.ndarray], list[str]]:
    states = list(enumerate_states(world))
    index = {canonical_json(state): position for position, state in enumerate(states)}
    transitions: dict[str, np.ndarray] = {}
    for operator in WORLDS[world].operators:
        matrix = np.zeros((len(states), len(states)), dtype=float)
        for row, state in enumerate(states):
            destination = apply_operator(world, state, operator)
            matrix[row, index[canonical_json(destination)]] = 1.0
        transitions[operator] = matrix
    observations = [canonical_json(query_answers(world, state)) for state in states]
    return transitions, observations


def command_quotient(args: argparse.Namespace) -> dict[str, Any]:
    config = _load_config(args.config, args.preset)
    output = _output_dir(args.output_dir, "quotient")
    settings = dict(config.get("quotient", {}))
    if not bool(settings.get("enabled", True)):
        result = {
            "schema": "osl.micro-emergence.quotient-analysis.v1",
            "status": "SKIPPED",
            "scope": "ground_truth_finite_worlds",
            "reason": "disabled by the selected configuration",
            "note": "The quotient benchmark is invariant across model seeds and is not repeated in the confirmatory matrix.",
            "worlds": {},
        }
        save_json(output / "soft_quotient_results.json", result)
        print("skipped quotient analysis because it is disabled in this configuration")
        return result
    candidates = [int(value) for value in settings.get("candidate_dimensions", [2, 4, 8])]
    temperatures = [float(value) for value in settings.get("temperatures", [1.0, 0.25])]
    iterations = int(settings.get("max_iterations", 100))
    feature_depth = int(settings.get("feature_depth", 2))
    worlds: dict[str, Any] = {}
    for world in sorted(WORLDS):
        transitions, observations = _world_system(world)
        exact = exact_partition(transitions, observations)
        exact_summary = {
            "labels": exact["labels"],
            "symbol_count": exact["symbol_count"],
            "iterations": exact["iterations"],
            "analysis": exact["analysis"],
        }
        soft: dict[str, Any] = {}
        for dimension in candidates:
            if 1 <= dimension <= len(observations):
                fitted = fit_soft_quotient(
                    transitions,
                    observations,
                    dimension,
                    temperature=1.0,
                    feature_depth=feature_depth,
                    seed=_resolved_data_seed(args),
                    kmeans_iterations=iterations,
                )
                sweep = temperature_hardening_sweep(
                    transitions,
                    observations,
                    dimension,
                    temperatures,
                    feature_depth=feature_depth,
                    seed=_resolved_data_seed(args),
                )
                labels = np.asarray(fitted["hard_labels"], dtype=int)
                soft[str(dimension)] = {
                    "fit": {
                        "membership": fitted["membership"],
                        "hard_labels": labels,
                        "cluster_counts": np.bincount(labels, minlength=dimension),
                        "temperature": fitted["temperature"],
                        "feature_depth": fitted["feature_depth"],
                        "analysis": fitted["analysis"],
                        "hard_analysis": fitted["hard_analysis"],
                    },
                    "temperature_sweep": sweep,
                }
        worlds[world] = {
            "concrete_state_count": len(observations),
            "exact": exact_summary,
            "soft_candidates": soft,
        }
    result = {
        "schema": "osl.micro-emergence.quotient-analysis.v1",
        "scope": "ground_truth_finite_worlds",
        "note": "This certifies benchmark structure, not learned latent symbols.",
        "declared_laws": verify_declared_laws(),
        "worlds": worlds,
    }
    ready = json_ready(result)
    save_json(output / "soft_quotient_results.json", ready)
    print(f"completed exact and soft quotient analyses for {len(worlds)} worlds")
    return ready


def command_report(args: argparse.Namespace) -> dict[str, Any]:
    config = _load_config(args.config, args.preset)
    output = _output_dir(args.output_dir, "report")
    make_figures = bool(dict(config.get("report", {})).get("make_figures", True))
    result = build_report(output, output / "reports", make_figures=make_figures)
    print("report: reports/FINAL_REPORT.md")
    return result


def command_verify(args: argparse.Namespace) -> dict[str, Any]:
    output = _output_dir(args.output_dir, "verify")
    project = verify_project(PROJECT_ROOT, check_manifest=(PROJECT_ROOT / "MANIFEST.json").exists())
    checks: dict[str, Any] = {"project": project}
    source = _dataset_dir(args)
    if (source / "manifest.json").exists():
        from .validation import validate_dataset

        data_report = validate_dataset(source)
        checks["dataset"] = data_report.to_dict()
    checkpoint_entries: list[dict[str, Any]] = []
    for summary_path in sorted((source / "experiments").glob("*/training_summary.json")):
        summary = load_json(summary_path)
        for field, hash_field in (
            ("checkpoint", "checkpoint_sha256"),
            ("last_checkpoint", "last_checkpoint_sha256"),
        ):
            declared = summary.get(field)
            if not declared:
                continue
            candidate = Path(str(declared))
            if not candidate.is_absolute():
                candidate = summary_path.parent / candidate
            elif not candidate.is_file():
                candidate = summary_path.parent / candidate.name
            expected_hash = summary.get(hash_field)
            observed_hash = sha256_file(candidate) if candidate.is_file() else None
            checkpoint_entries.append(
                {
                    "experiment": summary_path.parent.name,
                    "kind": field,
                    "path": f"experiments/{summary_path.parent.name}/{candidate.name}",
                    "exists": candidate.is_file(),
                    "expected_sha256": expected_hash,
                    "observed_sha256": observed_hash,
                    "status": "PASS"
                    if candidate.is_file() and expected_hash == observed_hash
                    else "FAIL",
                }
            )
    if checkpoint_entries:
        checks["checkpoints"] = {
            "status": "PASS"
            if all(item["status"] == "PASS" for item in checkpoint_entries)
            else "FAIL",
            "checked": len(checkpoint_entries),
            "entries": checkpoint_entries,
        }
    if args.checkpoint:
        checkpoint = Path(args.checkpoint).resolve()
        checks["checkpoint"] = {
            "status": "PASS" if checkpoint.is_file() else "FAIL",
            "path": checkpoint.name,
        }
    status = "PASS"
    if project.get("status") != "PASS":
        status = "FAIL"
    if "dataset" in checks and not bool(checks["dataset"].get("ok")):
        status = "FAIL"
    if checks.get("checkpoint", {}).get("status") == "FAIL":
        status = "FAIL"
    if checks.get("checkpoints", {}).get("status") == "FAIL":
        status = "FAIL"
    result = {"schema": "osl.micro-emergence.verification.v1", "status": status, "checks": checks}
    save_json(output / "verification_report.json", result)
    print(json.dumps({"status": status, "output": output.name}, sort_keys=True))
    if status != "PASS":
        raise RuntimeError("verification failed; inspect verification_report.json")
    return result


def command_run_all(args: argparse.Namespace) -> dict[str, Any]:
    from . import __version__

    config = _load_config(args.config, args.preset)
    output = _output_dir(args.output_dir, f"run_{args.preset or config.get('preset', 'standard')}")
    protected_artifacts = (
        output / "run_metadata.json",
        output / "manifest.json",
        output / "experiment_matrix.json",
        output / "resolved_config.json",
    )
    if not args.force and any(path.exists() for path in protected_artifacts):
        raise FileExistsError(
            f"run output already contains protected artifacts at {output}; "
            "choose a new directory or pass --force explicitly"
        )
    data_seed = _resolved_data_seed(args)
    model_seed = _resolved_model_seed(args)
    resolved_config = {key: value for key, value in config.items() if not key.startswith("_")}
    resolved_config["seed"] = int(args.seed)
    resolved_config["data_seed"] = data_seed
    resolved_config["model_seed"] = model_seed
    resolved_config.setdefault("dataset", {})["seed"] = data_seed
    resolved_config.setdefault("training", {})["seed"] = model_seed
    resolved_config.setdefault("runtime", {})["selected_device"] = args.device
    save_json(output / "resolved_config.json", resolved_config)
    save_json(output / "environment_report.json", _portable_environment_report())
    config_source = Path(config["_source"])
    package_manifest = PROJECT_ROOT / "MANIFEST.json"
    reproducibility = _snapshot_reproducibility(output, config_source)
    metadata = {
        "schema": "osl.micro-emergence.run-metadata.v2",
        "package_version": __version__,
        "config_source": "reproducibility/config_source.json",
        "config_sha256": sha256_file(config_source),
        "package_manifest_sha256": sha256_file(package_manifest)
        if package_manifest.exists()
        else None,
        "reproducibility_manifest": reproducibility,
        "seed": int(args.seed),
        "data_seed": data_seed,
        "model_seed": model_seed,
        "requested_device": args.device,
        "completed": False,
        "status": "RUNNING",
    }
    save_json(output / "run_metadata.json", metadata)
    child = argparse.Namespace(**vars(args))
    child.output_dir = str(output)
    child.data_dir = str(output)
    command_generate(child)
    command_validate(child)
    command_baselines(child)
    experiments: list[dict[str, Any]] = []
    if not args.skip_neural:
        training = dict(config.get("training", {}))
        arms = [str(value) for value in training.get("arms", [training.get("default_arm", "answer_only")])]
        architectures = [str(value) for value in training.get("architectures", ["transformer"])]
        for architecture in architectures:
            for arm in arms:
                experiment_dir = output / "experiments" / f"{architecture}__{arm}"
                experiment_args = argparse.Namespace(**vars(args))
                experiment_args.config = config["_source"]
                experiment_args.data_dir = str(output)
                experiment_args.output_dir = str(experiment_dir)
                experiment_args.arm = arm
                experiment_args.architecture = architecture
                experiment_args.resume = None
                training_result = command_train(experiment_args)
                evaluation_settings = dict(config.get("evaluation", {}))
                checkpoint_policy = str(evaluation_settings.get("checkpoint", "best")).lower()
                if checkpoint_policy not in {"best", "last"}:
                    raise ValueError("evaluation.checkpoint must be 'best' or 'last'")
                selected_checkpoint = (
                    training_result["_last_checkpoint_path"]
                    if checkpoint_policy == "last"
                    else training_result["_checkpoint_path"]
                )
                evaluation_result = _evaluate_checkpoint(
                    selected_checkpoint,
                    output,
                    experiment_dir,
                    config,
                    args.device,
                    model_seed,
                )
                experiments.append(
                    {
                        "architecture": architecture,
                        "arm": arm,
                        "checkpoint": f"experiments/{experiment_dir.name}/{Path(selected_checkpoint).name}",
                        "checkpoint_policy": checkpoint_policy,
                        "best_validation_accuracy": training_result["best_validation_accuracy"],
                        "best_validation_score": training_result["best_validation_score"],
                        "selection_metric": training_result["selection_metric"],
                        "initial_model_sha256": training_result.get("initial_model_sha256"),
                        "initialization_contract": training_result.get(
                            "initialization_contract"
                        ),
                        "evaluation_accuracy": evaluation_result["behavior"]["overall"]["accuracy"],
                    }
                )
    command_quotient(child)
    initialization_audit = _audit_initialization_contracts(experiments)
    if len(initialization_audit["arms"]) > 1 and initialization_audit["status"] != "PASS":
        raise RuntimeError(
            "central arms do not share an identical tokenizer, answer ontology, "
            "parameter schema, and initialized model state"
        )
    run_summary = {
        "schema": "osl.micro-emergence.run-matrix.v2",
        "preset": config.get("preset", args.preset),
        "data_seed": data_seed,
        "model_seed": model_seed,
        "skip_neural": bool(args.skip_neural),
        "initialization_audit": initialization_audit,
        "experiments": experiments,
    }
    save_json(output / "experiment_matrix.json", run_summary)
    child.checkpoint = None
    command_verify(child)
    command_report(child)
    metadata["completed"] = True
    metadata["status"] = "COMPLETED"
    save_json(output / "run_metadata.json", metadata)
    print("run-all completed")
    return run_summary


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config")
    parser.add_argument("--preset", choices=PRESETS)
    parser.add_argument("--output-dir", "--run-dir", dest="output_dir")
    parser.add_argument("--data-dir")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--data-seed", type=int)
    parser.add_argument("--model-seed", type=int)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--checkpoint")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m osl_lab.cli",
        description="Offline falsification-first Micro OSL emergence laboratory",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    doctor = subparsers.add_parser("doctor")
    _add_common(doctor)
    doctor.add_argument("--require-neural", action="store_true")
    for name in ("generate", "validate", "baselines", "evaluate", "quotient", "report", "verify"):
        child = subparsers.add_parser(name)
        _add_common(child)
    train = subparsers.add_parser("train")
    _add_common(train)
    train.add_argument("--arm", choices=ARMS)
    train.add_argument("--architecture", default="transformer")
    train.add_argument("--resume")
    run_all = subparsers.add_parser("run-all")
    _add_common(run_all)
    run_all.add_argument("--skip-neural", action="store_true")
    return parser


COMMANDS = {
    "doctor": command_doctor,
    "generate": command_generate,
    "validate": command_validate,
    "baselines": command_baselines,
    "train": command_train,
    "evaluate": command_evaluate,
    "quotient": command_quotient,
    "report": command_report,
    "verify": command_verify,
    "run-all": command_run_all,
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = COMMANDS[args.command](args)
        return 0 if result is not False else 1
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
