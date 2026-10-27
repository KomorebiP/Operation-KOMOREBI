from __future__ import annotations

import argparse
import atexit
import json
import math
import os
from pathlib import Path
import random
import sys
import time
import traceback
from typing import Any


ROOT = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Komorebi Neuralese G1 experiment")
    parser.add_argument("--model", required=True, help="Local Hugging Face model directory")
    parser.add_argument("--output", required=True, help="Run output directory")
    parser.add_argument("--profile", choices=("wiring", "smoke", "pilot"), default="smoke")
    parser.add_argument("--device", choices=("cuda", "cpu"))
    parser.add_argument("--source-layer", type=int)
    parser.add_argument("--recurrent-steps", type=int)
    parser.add_argument("--training-steps", type=int)
    parser.add_argument("--seed", type=int, help="Registered seed override")
    return parser.parse_args()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _training_records(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict) or not isinstance(value.get("step"), int):
            raise RuntimeError(f"invalid training record at line {line_number}")
        records.append(value)
    if any(left["step"] >= right["step"] for left, right in zip(records, records[1:])):
        raise RuntimeError("training log steps are not strictly increasing")
    return records


def _atomic_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    import os
    import tempfile

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            for record in records:
                handle.write(json.dumps(record, sort_keys=True) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    except BaseException:
        try:
            os.unlink(temporary_name)
        except FileNotFoundError:
            pass
        raise


def main() -> int:
    args = parse_args()
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

    import torch

    from neuralese_g1.config import load_config
    from neuralese_g1.gates import adjudicate
    from neuralese_g1.integrity import (
        acquire_run_lock,
        atomic_json,
        release_run_lock,
        verify_package_manifest,
    )
    from neuralese_g1.model import FrozenRecurrentCausalLM
    from neuralese_g1.results import verify_run_directory
    from neuralese_g1.runtime import (
        atomic_torch_save,
        capture_rng_state,
        environment_report,
        evaluate_split,
        file_inventory_fingerprint,
        load_local_model,
        module_all_finite,
        module_state_hash,
        restore_rng_state,
        seed_everything,
        train_steps,
    )
    from neuralese_g1.tasks import ANSWER_CUE, make_split, split_digest
    from neuralese_g1.token_contract import validate_single_token_targets

    package_verification = verify_package_manifest(ROOT)

    overrides: dict[str, Any] = {}
    if args.seed is not None:
        overrides["seed"] = args.seed
    if args.device is not None:
        overrides["model.device"] = args.device
    if args.source_layer is not None:
        overrides["model.source_layer"] = args.source_layer
    if args.recurrent_steps is not None:
        overrides["workspace.steps"] = args.recurrent_steps
    if args.training_steps is not None:
        overrides["training.steps"] = args.training_steps
    profile_path = ROOT / "configs" / f"{args.profile}.json"
    config = load_config(profile_path, overrides)
    canonical_overrides = (
        {"seed": config["seed"]} if config["profile"] == "pilot" else {}
    )
    canonical_config = load_config(profile_path, canonical_overrides)
    canonical_claim_eligible = config == canonical_config
    device = str(config["model"]["device"])
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA was requested but is unavailable")

    model_path = Path(args.model).resolve()
    output = Path(args.output).resolve()
    if not model_path.is_dir():
        raise FileNotFoundError(f"model directory not found: {model_path}")
    if output == ROOT or ROOT in output.parents:
        raise RuntimeError("run output must be outside the package directory")
    if (
        output == model_path
        or model_path in output.parents
        or output in model_path.parents
    ):
        raise RuntimeError("run output and model directories must not overlap")
    if (output / "run_summary.json").exists():
        raise RuntimeError(
            f"completed output already exists: {output}; select a new directory for replication"
        )
    output.mkdir(parents=True, exist_ok=True)
    run_lock = acquire_run_lock(output / ".g1.lock")
    atexit.register(release_run_lock, run_lock)
    package_manifest_sha256 = str(package_verification["manifest_sha256"])
    started = time.perf_counter()
    seed_everything(int(config["seed"]))

    task = config["task"]
    split_arguments = {
        "seed": int(config["seed"]),
        "states": int(task["states"]),
    }
    train_examples = make_split(
        **split_arguments,
        split="train",
        base_problems=int(task["train_base_problems"]),
        chain_min=int(task["train_chain_min"]),
        chain_max=int(task["train_chain_max"]),
    )
    validation_examples = make_split(
        **split_arguments,
        split="validation",
        base_problems=int(task["validation_base_problems"]),
        chain_min=int(task["train_chain_min"]),
        chain_max=int(task["train_chain_max"]),
    )
    test_examples = make_split(
        **split_arguments,
        split="test_iid",
        base_problems=int(task["test_base_problems"]),
        chain_min=int(task["train_chain_min"]),
        chain_max=int(task["train_chain_max"]),
    )
    ood_examples = make_split(
        **split_arguments,
        split="test_ood_depth",
        base_problems=int(task["ood_base_problems"]),
        chain_min=int(task["ood_chain_min"]),
        chain_max=int(task["ood_chain_max"]),
    )
    random.Random(int(config["seed"]) + 91).shuffle(train_examples)

    split_prompt_sets = {
        "train": {example.compute_prompt for example in train_examples},
        "validation": {example.compute_prompt for example in validation_examples},
        "test_iid": {example.compute_prompt for example in test_examples},
        "test_ood_depth": {example.compute_prompt for example in ood_examples},
    }
    expected_base_counts = {
        "train": int(task["train_base_problems"]),
        "validation": int(task["validation_base_problems"]),
        "test_iid": int(task["test_base_problems"]),
        "test_ood_depth": int(task["ood_base_problems"]),
    }
    for split, prompts in split_prompt_sets.items():
        if len(prompts) != expected_base_counts[split]:
            raise RuntimeError(f"duplicate registered compute problem within {split}")
    split_overlap_counts: dict[str, int] = {}
    split_names = tuple(split_prompt_sets)
    for left_index, left in enumerate(split_names):
        for right in split_names[left_index + 1 :]:
            overlap = len(split_prompt_sets[left] & split_prompt_sets[right])
            split_overlap_counts[f"{left}__{right}"] = overlap
            if overlap:
                raise RuntimeError(f"compute-prompt leakage between {left} and {right}")
    registered_split_digests = {
        "train": split_digest(train_examples),
        "validation": split_digest(validation_examples),
        "test_iid": split_digest(test_examples),
        "test_ood_depth": split_digest(ood_examples),
    }

    model_fingerprint = file_inventory_fingerprint(model_path)
    tokenizer, backbone, dtype = load_local_model(
        model_path,
        device=device,
        dtype_name=str(config["model"]["dtype"]),
        trust_remote_code=bool(config["model"]["trust_remote_code"]),
        attention_implementation=str(config["model"]["attention_implementation"]),
    )
    expected_model = config["model"]
    model_identity = {
        "model_type": str(getattr(backbone.config, "model_type", "")),
        "architecture": backbone.__class__.__name__,
        "hidden_size": int(backbone.config.hidden_size),
        "layers": int(backbone.config.num_hidden_layers),
    }
    expected_identity = {
        "model_type": str(expected_model["expected_model_type"]),
        "architecture": str(expected_model["expected_architecture"]),
        "hidden_size": int(expected_model["expected_hidden_size"]),
        "layers": int(expected_model["expected_layers"]),
    }
    if model_identity != expected_identity:
        raise RuntimeError(
            f"model identity mismatch: expected {expected_identity}, observed {model_identity}"
        )
    all_examples = train_examples + validation_examples + test_examples + ood_examples
    target_tokens = validate_single_token_targets(tokenizer, all_examples)
    answer_token_contract = {
        "schema": "komorebi.neuralese.g1.answer_token_contract.v1",
        "status": "PASS",
        "answer_cue": ANSWER_CUE,
        "target_count": len(target_tokens),
        "prompt_target_pair_count": len(
            {(example.query_prompt, example.target_text) for example in all_examples}
        ),
    }
    maximum_length = int(config["model"]["max_sequence_length"])
    maximum_compute_tokens = max(
        len(tokenizer.encode(example.compute_prompt, add_special_tokens=True))
        for example in all_examples
    )
    maximum_query_tokens = max(
        len(tokenizer.encode(example.query_prompt, add_special_tokens=True))
        for example in all_examples
    )
    if max(maximum_compute_tokens, maximum_query_tokens) > maximum_length:
        raise RuntimeError("registered prompt exceeds model.max_sequence_length")

    model = FrozenRecurrentCausalLM(
        backbone,
        source_layer=int(config["model"]["source_layer"]),
        workspace_width=int(config["workspace"]["width"]),
        recurrent_steps=int(config["workspace"]["steps"]),
        injection_scale=float(config["workspace"]["injection_scale"]),
        state_clip=float(config["workspace"]["state_clip"]),
        dropout=float(config["workspace"]["dropout"]),
    ).to(device)
    workspace_parameters = model.workspace_parameters()
    if not workspace_parameters:
        raise RuntimeError("workspace contains no trainable parameters")
    optimizer = torch.optim.AdamW(
        workspace_parameters,
        lr=float(config["training"]["learning_rate"]),
        weight_decay=float(config["training"]["weight_decay"]),
    )
    scaler = torch.amp.GradScaler(
        "cuda",
        enabled=device == "cuda" and dtype == torch.float16,
        init_scale=float(config["training"]["loss_scale_initial"]),
    )
    workspace_ids = {id(parameter) for parameter in workspace_parameters}
    backbone_ids = {id(parameter) for parameter in model.backbone.parameters()}
    optimizer_ids = {
        id(parameter)
        for group in optimizer.param_groups
        for parameter in group["params"]
    }
    optimizer_excludes_backbone = not bool(optimizer_ids & backbone_ids)
    optimizer_matches_workspace = optimizer_ids == workspace_ids
    if not model.backbone_is_frozen:
        raise RuntimeError("backbone freeze invariant failed")
    if not optimizer_excludes_backbone or not optimizer_matches_workspace:
        raise RuntimeError("optimizer parameter partition invariant failed")
    if not module_all_finite(model.workspace):
        raise RuntimeError("workspace initialization contains a nonfinite value")

    strict_hash = bool(config["model"]["strict_backbone_hash"])
    backbone_hash_before = module_state_hash(model.backbone) if strict_hash else None
    initial_workspace_hash = module_state_hash(model.workspace)
    checkpoint_path = output / "checkpoint.pt"
    training_log_path = output / "training.jsonl"
    start_step = 0
    resumed = False
    checkpoint_latest_record: dict[str, Any] | None = None
    resumed_records: list[dict[str, Any]] = []
    start_overflow_retries = 0
    if checkpoint_path.is_file():
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
        if checkpoint.get("schema") != "komorebi.neuralese.g1.checkpoint.v3":
            raise RuntimeError("checkpoint schema mismatch")
        if checkpoint.get("config_digest") != config["config_digest"]:
            raise RuntimeError("checkpoint config digest mismatch")
        if checkpoint.get("model_fingerprint") != model_fingerprint:
            raise RuntimeError("checkpoint model fingerprint mismatch")
        if checkpoint.get("package_manifest_sha256") != package_manifest_sha256:
            raise RuntimeError("checkpoint package manifest mismatch")
        if checkpoint.get("split_digests") != registered_split_digests:
            raise RuntimeError("checkpoint split digest mismatch")
        model.workspace.load_state_dict(checkpoint["workspace_state"])
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        scaler.load_state_dict(checkpoint["scaler_state"])
        start_step = int(checkpoint["completed_steps"])
        initial_workspace_hash = str(checkpoint["initial_workspace_hash"])
        checkpoint_latest_record = checkpoint.get("latest_record")
        resumed = True
        if start_step > int(config["training"]["steps"]):
            raise RuntimeError("checkpoint step exceeds configured training steps")
        if strict_hash and checkpoint.get("backbone_hash_before") != backbone_hash_before:
            raise RuntimeError("checkpoint backbone hash mismatch")
        existing_records = _training_records(training_log_path)
        if start_step == 0:
            if checkpoint_latest_record is not None:
                raise RuntimeError("step-zero checkpoint contains training telemetry")
            if existing_records:
                _atomic_jsonl(training_log_path, [])
        else:
            if not existing_records:
                raise RuntimeError("checkpoint exists without a training log")
            if existing_records[-1]["step"] < start_step:
                raise RuntimeError("training log ends before the checkpoint")
            retained_records = [
                record for record in existing_records if record["step"] <= start_step
            ]
            if not retained_records or retained_records[-1]["step"] != start_step:
                raise RuntimeError("training log does not contain the checkpoint step")
            if checkpoint_latest_record != retained_records[-1]:
                raise RuntimeError("checkpoint telemetry does not match the training log")
            start_overflow_retries = int(
                checkpoint_latest_record.get("overflow_retries_total", -1)
            )
            if start_overflow_retries < 0:
                raise RuntimeError("checkpoint overflow-retry telemetry is missing")
            if len(retained_records) != len(existing_records):
                _atomic_jsonl(training_log_path, retained_records)
            resumed_records = retained_records
        restore_rng_state(checkpoint["rng_state"])
        if not module_all_finite(model.workspace):
            raise RuntimeError("resumed workspace contains a nonfinite value")
    elif training_log_path.exists():
        raise RuntimeError("training log exists without a recoverable checkpoint")

    resolved_config_path = output / "resolved_config.json"
    if resolved_config_path.is_file():
        if _read_json(resolved_config_path) != config:
            raise RuntimeError("resolved configuration differs from the existing run")
    else:
        atomic_json(resolved_config_path, config)

    preflight = {
        "schema": "komorebi.neuralese.g1.preflight.v1",
        "status": "PASS",
        "profile": config["profile"],
        "seed": config["seed"],
        "config_digest": config["config_digest"],
        "environment": environment_report(device),
        "model": model_fingerprint,
        "model_identity": model_identity,
        "expected_model_identity": expected_identity,
        "model_class": model.backbone.__class__.__name__,
        "resolved_torch_dtype": str(dtype),
        "hidden_size": int(model.backbone.config.hidden_size),
        "physical_layers": len(model.layers),
        "source_layer": model.source_layer,
        "logical_recurrent_steps": model.recurrent_steps,
        "backbone_parameters": sum(parameter.numel() for parameter in model.backbone.parameters()),
        "workspace_parameters": sum(parameter.numel() for parameter in workspace_parameters),
        "backbone_frozen": model.backbone_is_frozen,
        "optimizer_excludes_backbone": optimizer_excludes_backbone,
        "optimizer_matches_workspace": optimizer_matches_workspace,
        "single_token_targets": target_tokens,
        "answer_token_contract": answer_token_contract,
        "maximum_compute_tokens": maximum_compute_tokens,
        "maximum_query_tokens": maximum_query_tokens,
        "split_counts": {
            "train": len(train_examples),
            "validation": len(validation_examples),
            "test_iid": len(test_examples),
            "test_ood_depth": len(ood_examples),
        },
        "split_digests": registered_split_digests,
        "compute_prompt_overlap_counts": split_overlap_counts,
        "strict_backbone_hash": strict_hash,
        "package_manifest_sha256": package_manifest_sha256,
        "gradient_scaler_enabled": scaler.is_enabled(),
        "gradient_scaler_registered_initial_scale": float(
            config["training"]["loss_scale_initial"]
        ),
        "gradient_scaler_start_scale": float(scaler.get_scale()),
        "backbone_hash_before": backbone_hash_before,
        "resumed": resumed,
        "start_step": start_step,
        "canonical_claim_eligible": canonical_claim_eligible,
    }
    atomic_json(output / "preflight.json", preflight)

    latest_record: dict[str, Any] | None = checkpoint_latest_record
    logged_records = list(resumed_records)

    def log_callback(record: dict[str, Any]) -> None:
        nonlocal latest_record
        latest_record = record
        logged_records.append(record)
        _atomic_jsonl(training_log_path, logged_records)
        print(
            f"G1_STEP={record['step']} LOSS={record['loss']:.6f} "
            f"GRAD_NORM={record['gradient_norm']:.6f}",
            flush=True,
        )

    def checkpoint_callback(completed_steps: int) -> None:
        atomic_torch_save(
            checkpoint_path,
            {
                "schema": "komorebi.neuralese.g1.checkpoint.v3",
                "completed_steps": completed_steps,
                "config_digest": config["config_digest"],
                "model_fingerprint": model_fingerprint,
                "package_manifest_sha256": package_manifest_sha256,
                "split_digests": preflight["split_digests"],
                "initial_workspace_hash": initial_workspace_hash,
                "backbone_hash_before": backbone_hash_before,
                "workspace_state": model.workspace.state_dict(),
                "optimizer_state": optimizer.state_dict(),
                "scaler_state": scaler.state_dict(),
                "rng_state": capture_rng_state(),
                "latest_record": latest_record,
            },
        )

    if not resumed:
        checkpoint_callback(0)

    train_steps(
        model,
        tokenizer,
        train_examples,
        config=config,
        optimizer=optimizer,
        scaler=scaler,
        start_step=start_step,
        start_overflow_retries=start_overflow_retries,
        log_callback=log_callback,
        checkpoint_callback=checkpoint_callback,
    )
    records = _training_records(training_log_path)
    if not records:
        raise RuntimeError("training produced no telemetry")
    print("G1_EVALUATION=START", flush=True)
    iid_summary, iid_records = evaluate_split(
        model, tokenizer, test_examples, config=config
    )
    ood_summary, ood_records = evaluate_split(
        model, tokenizer, ood_examples, config=config
    )
    workspace_hash_after = module_state_hash(model.workspace)
    backbone_hash_after = module_state_hash(model.backbone) if strict_hash else None
    evaluation = {
        "schema": "komorebi.neuralese.g1.evaluation.v1",
        "iid": iid_summary,
        "ood": ood_summary,
        "validation_not_used_for_selection": True,
        "claim_ceiling": "G1_SMALL_MODEL_SINGLE_SEED",
    }
    atomic_json(output / "evaluation.json", evaluation)
    _atomic_jsonl(
        output / "predictions.jsonl",
        [dict(record, split="test_iid") for record in iid_records]
        + [dict(record, split="test_ood_depth") for record in ood_records],
    )

    losses = [float(record["loss"]) for record in records]
    gradient_norms = [float(record["gradient_norm"]) for record in records]
    state_norms = [
        float(value)
        for record in records
        for value in record["trace"]["state_mean_norm_by_step"]
    ]
    injection_norms = [
        float(value)
        for record in records
        for value in record["trace"]["injection_mean_norm_by_step"]
    ]
    required_artifacts = (
        "resolved_config.json",
        "preflight.json",
        "training.jsonl",
        "checkpoint.pt",
        "evaluation.json",
        "predictions.jsonl",
    )
    expected_iid_predictions = len(test_examples) * 4
    expected_ood_predictions = len(ood_examples) * 4
    artifact_consistency = (
        len(iid_records) == expected_iid_predictions
        and len(ood_records) == expected_ood_predictions
        and iid_summary["state_derangement"]["answer_compatible_matches"] == 0
        and ood_summary["state_derangement"]["answer_compatible_matches"] == 0
        and iid_summary["state_derangement"]["bijection"] is True
        and ood_summary["state_derangement"]["bijection"] is True
    )
    engineering = {
        "local_model_loaded": True,
        "single_token_targets": bool(target_tokens),
        "answer_token_boundary": answer_token_contract["status"] == "PASS",
        "backbone_frozen": model.backbone_is_frozen
        and all(parameter.grad is None for parameter in model.backbone.parameters())
        and (not strict_hash or backbone_hash_before == backbone_hash_after),
        "optimizer_excludes_backbone": optimizer_excludes_backbone
        and optimizer_matches_workspace,
        "finite_loss": bool(losses) and all(math.isfinite(value) for value in losses),
        "nonzero_finite_gradient": bool(gradient_norms)
        and all(math.isfinite(value) for value in gradient_norms)
        and max(gradient_norms) > 0.0,
        "nonzero_finite_parameter_delta": module_all_finite(model.workspace)
        and workspace_hash_after != initial_workspace_hash,
        "nonzero_finite_state": bool(state_norms)
        and bool(injection_norms)
        and all(math.isfinite(value) for value in state_norms + injection_norms)
        and max(state_norms) > 0.0
        and max(injection_norms) > 0.0,
        "artifacts_complete": artifact_consistency
        and all((output / name).is_file() for name in required_artifacts),
        "canonical_scientific_profile": canonical_claim_eligible,
    }
    gates = adjudicate(config, engineering, evaluation)
    atomic_json(output / "gates.json", gates)
    summary = {
        "schema": "komorebi.neuralese.g1.run_summary.v1",
        "status": gates["claim"],
        "profile": config["profile"],
        "seed": config["seed"],
        "resumed": resumed,
        "training": {
            "logged_records": len(records),
            "first_logged_loss": losses[0],
            "last_logged_loss": losses[-1],
            "maximum_gradient_norm": max(gradient_norms),
            "overflow_retries_total": records[-1]["overflow_retries_total"],
            "workspace_hash_before": initial_workspace_hash,
            "workspace_hash_after": workspace_hash_after,
        },
        "backbone_hash_before": backbone_hash_before,
        "backbone_hash_after": backbone_hash_after,
        "evaluation": {
            "iid_recurrent_accuracy": iid_summary["recurrent"]["accuracy"],
            "iid_zero_accuracy": iid_summary["zero"]["accuracy"],
            "iid_shuffle_accuracy": iid_summary["shuffle"]["accuracy"],
            "iid_no_feedback_accuracy": iid_summary["no_feedback"]["accuracy"],
            "ood_recurrent_accuracy": ood_summary["recurrent"]["accuracy"],
        },
        "gates": gates,
        "elapsed_seconds": time.perf_counter() - started,
        "interpretation_boundary": (
            "This run evaluates a bounded recurrent latent workspace. It does not establish "
            "general Neuralese, OSL grounding, awareness, consciousness, or Astra parity."
        ),
    }
    atomic_json(output / "run_summary.json", summary)
    verification = verify_run_directory(output)
    atomic_json(output / "verification.json", verification)
    print(f"G1_STATUS={gates['claim']}")
    print(f"IID_RECURRENT_ACCURACY={iid_summary['recurrent']['accuracy']:.6f}")
    print(f"IID_ZERO_ACCURACY={iid_summary['zero']['accuracy']:.6f}")
    print(f"IID_SHUFFLE_ACCURACY={iid_summary['shuffle']['accuracy']:.6f}")
    print(f"IID_NO_FEEDBACK_ACCURACY={iid_summary['no_feedback']['accuracy']:.6f}")
    print(f"OOD_RECURRENT_ACCURACY={ood_summary['recurrent']['accuracy']:.6f}")
    print(f"OUTPUT={output}")
    exit_code = 0 if gates["engineering"]["passed"] else 2
    release_run_lock(run_lock)
    atexit.unregister(release_run_lock)
    return exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"G1_STATUS=FAIL: {error}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)
