#!/usr/bin/env python3
"""Resume an interrupted frozen primary run in deterministic bounded shards.

This is orchestration-only code and is deliberately outside the scientific
code whitelist used by the sealed protocol.  Every training cell resets its
own NumPy and Torch seeds in the original runner, so completed cells can be
validated and skipped without changing any later cell's computation.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
for value in (str(ROOT), str(SRC)):
    if value not in sys.path:
        sys.path.insert(0, value)

import run_experiment as runner
from komorebi_neuralese.hard_operator import ExactTableOracle
from komorebi_neuralese.models import build_model
from komorebi_neuralese.reporting import code_files, protocol_digest, tree_digest
from komorebi_neuralese.splits import audit_coordinate_splits
from komorebi_neuralese.train import config_dict, train_arm
from komorebi_neuralese.transport import cross_seed_transport
from komorebi_neuralese.version import VERSION


class RecoveryError(RuntimeError):
    """Fail-closed recovery validation error."""


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RecoveryError(f"expected JSON object: {path}")
    return value


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary, path)


def _atomic_checkpoint(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    torch.save(value, temporary)
    os.replace(temporary, path)


def _safe_checkpoint(path: Path) -> dict[str, Any]:
    try:
        value = torch.load(path, map_location="cpu", weights_only=True)
    except Exception as error:
        raise RecoveryError(f"cannot safely load checkpoint {path}: {error}") from error
    if not isinstance(value, dict) or not isinstance(value.get("state_dict"), dict):
        raise RecoveryError(f"invalid checkpoint payload: {path}")
    return value


def _append_event(output_dir: Path, event: dict[str, Any]) -> None:
    path = output_dir / "RECOVERY_EVENTS.json"
    events: list[dict[str, Any]] = []
    if path.exists():
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, list):
            raise RecoveryError("RECOVERY_EVENTS.json must be a list")
        events = value
    events.append(event)
    _atomic_json(path, events)


def _validate_base(actual: dict[str, Any], expected: dict[str, Any], label: str) -> None:
    for key, value in expected.items():
        if actual.get(key) != value:
            raise RecoveryError(
                f"{label} {key!r} mismatch: expected {value!r}, observed {actual.get(key)!r}"
            )


def _expected_initial_digest(
    protocol: dict[str, Any], arm: dict[str, Any], seed: int, device: torch.device
) -> tuple[dict[str, Any], str]:
    torch.manual_seed(seed)
    np.random.seed(seed)
    config = runner._train_config(protocol, arm, seed, device)
    model = build_model(
        str(arm["model_name"]),
        operator_init_std=config.operator_init_std,
        orthogonal_parameterization=config.orthogonal_parameterization,
    )
    return config_dict(config), runner._tensor_state_digest(model)


def _validate_cell(
    *,
    output_dir: Path,
    protocol: dict[str, Any],
    receipt_base: dict[str, Any],
    arm_name: str,
    arm: dict[str, Any],
    seed: int,
    device: torch.device,
) -> dict[str, Any] | None:
    record_path = output_dir / "arms" / arm_name / f"seed_{seed}.json"
    checkpoint_path = output_dir / "checkpoints" / arm_name / f"seed_{seed}.pt"
    if record_path.exists() != checkpoint_path.exists():
        raise RecoveryError(
            f"cell {arm_name}/{seed} has only one of record and checkpoint"
        )
    if not record_path.exists():
        return None
    record = _read_json(record_path)
    checkpoint = _safe_checkpoint(checkpoint_path)
    expected_config, expected_initial_digest = _expected_initial_digest(
        protocol, arm, seed, device
    )
    _validate_base(record, receipt_base, f"record {arm_name}/{seed}")
    _validate_base(checkpoint, receipt_base, f"checkpoint {arm_name}/{seed}")
    for value, label in ((record, "record"), (checkpoint, "checkpoint")):
        if value.get("arm") != arm_name or value.get("seed") != seed:
            raise RecoveryError(f"{label} identity mismatch for {arm_name}/{seed}")
        if value.get("config") != expected_config:
            raise RecoveryError(f"{label} config mismatch for {arm_name}/{seed}")
    if record.get("initial_tensor_digest") != expected_initial_digest:
        raise RecoveryError(f"initial tensor digest mismatch for {arm_name}/{seed}")
    if not isinstance(record.get("metrics"), dict) or not isinstance(
        record.get("training"), dict
    ):
        raise RecoveryError(f"incomplete scientific record for {arm_name}/{seed}")
    audit = record["training"].get("sampling_audit")
    if not isinstance(audit, dict):
        raise RecoveryError(f"missing sampling audit for {arm_name}/{seed}")
    if not audit.get("fail_closed") or int(audit.get("split_violations") or 0) != 0:
        raise RecoveryError(f"failed sampling audit for {arm_name}/{seed}")
    # Strict load catches missing, unexpected, or shape-incompatible tensors.
    model = build_model(
        str(arm["model_name"]),
        operator_init_std=float(expected_config["operator_init_std"]),
        orthogonal_parameterization=str(expected_config["orthogonal_parameterization"]),
    )
    model.load_state_dict(checkpoint["state_dict"], strict=True)
    return record


def _load_model(
    output_dir: Path,
    arm_name: str,
    arm: dict[str, Any],
    seed: int,
    device: torch.device,
) -> torch.nn.Module:
    checkpoint = _safe_checkpoint(
        output_dir / "checkpoints" / arm_name / f"seed_{seed}.pt"
    )
    config = checkpoint["config"]
    model = build_model(
        str(arm["model_name"]),
        operator_init_std=float(config["operator_init_std"]),
        orthogonal_parameterization=str(config["orthogonal_parameterization"]),
    )
    model.load_state_dict(checkpoint["state_dict"], strict=True)
    return model.to(device)


def _training_sampling_audit(records: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    audits = [
        record["training"]["sampling_audit"]
        for arm_records in records.values()
        for record in arm_records
    ]
    supports: dict[str, dict[str, Any]] = {}
    for audit in audits:
        for support in audit.get("conditioning_supports", []):
            digest = str(support["digest"])
            previous = supports.setdefault(digest, support)
            if previous != support:
                raise RecoveryError(f"inconsistent conditioning support {digest}")
    methods = sorted(
        {str(method) for audit in audits for method in audit.get("sampling_methods", [])}
    )
    backends = sorted(
        {
            str(audit["conditioned_sampler_backend"])
            for audit in audits
            if audit.get("conditioned_sampler_backend") is not None
        }
    )
    result = {
        "cells": len(audits),
        "word_product_scopes": sorted(
            {str(audit["word_product_scope"]) for audit in audits}
        ),
        "sampling_methods": methods,
        "conditioned_sampler_backends": backends,
        "actual_counter_semantics": (
            "candidate/rejected totals count sampler draws actually executed; "
            "direct-conditioned draws have zero fictional rejections"
        ),
        "conditioning_supports": sorted(
            supports.values(), key=lambda item: (int(item["length"]), str(item["digest"]))
        ),
        "direct_conditioning_receipts_complete": (
            "direct_conditioned_uniform" not in methods or bool(supports)
        ),
        "conditioned_sampler_backend_frozen": backends == ["cached_exact_v1"],
        "all_fail_closed": all(bool(audit["fail_closed"]) for audit in audits),
        "total_accepted_examples": sum(int(audit["accepted_examples"]) for audit in audits),
        "total_candidate_examples": sum(int(audit["candidate_examples"]) for audit in audits),
        "total_rejected_examples": sum(int(audit["rejected_examples"]) for audit in audits),
        "total_split_violations": sum(int(audit["split_violations"] or 0) for audit in audits),
    }
    result["counter_arithmetic_exact"] = (
        result["total_candidate_examples"] - result["total_accepted_examples"]
        == result["total_rejected_examples"]
    )
    if not (
        result["all_fail_closed"]
        and result["total_split_violations"] == 0
        and result["counter_arithmetic_exact"]
        and result["direct_conditioning_receipts_complete"]
        and result["conditioned_sampler_backend_frozen"]
    ):
        raise RecoveryError(f"training sampling audit failed: {result}")
    return result


def _finalize(
    *,
    output_dir: Path,
    protocol: dict[str, Any],
    receipt_base: dict[str, Any],
    records: dict[str, list[dict[str, Any]]],
    transport_records: list[dict[str, Any]],
    oracle_record: dict[str, Any] | None,
    split_audit: dict[str, Any],
    device: torch.device,
    threads: int,
) -> None:
    expected_pairs = {
        (arm, seed) for arm in protocol["arms"] for seed in protocol["seeds"]
    }
    observed_pairs = {
        (record["arm"], record["seed"])
        for values in records.values()
        for record in values
    }
    grid = {
        "expected_cells": len(expected_pairs),
        "observed_cells": len(observed_pairs),
        "missing_cells": [list(value) for value in sorted(expected_pairs - observed_pairs)],
        "unexpected_cells": [list(value) for value in sorted(observed_pairs - expected_pairs)],
        "complete": observed_pairs == expected_pairs,
    }
    if not grid["complete"]:
        raise RecoveryError(f"cannot finalize incomplete grid: {grid}")
    aggregate = runner._aggregate_all(records, transport_records)
    gates = runner._evaluate_gates(protocol, aggregate)
    all_gates_passed = bool(gates) and len(gates) == len(protocol.get("gates", [])) and all(
        gate["passed"] for gate in gates.values()
    )
    _atomic_json(output_dir / "AGGREGATE.json", aggregate)
    _atomic_json(
        output_dir / "GATES.json",
        {"all_gates_passed": all_gates_passed, "gates": gates},
    )
    _atomic_json(output_dir / "GRID_AUDIT.json", grid)
    _atomic_json(output_dir / "COORDINATE_SPLIT_AUDIT.json", split_audit)
    runner._write_csv(output_dir / "summary.csv", records)
    (output_dir / "REPORT.md").write_text(
        runner._report(protocol, aggregate, gates, grid, oracle_record), encoding="utf-8"
    )
    plots = runner._plots(output_dir, protocol, aggregate)
    sampling = _training_sampling_audit(records)
    receipt = {
        **receipt_base,
        "status": "complete",
        "scientific_gate_status": "not_applicable"
        if not gates
        else ("pass" if all_gates_passed else "fail"),
        "grid_complete": True,
        "all_gates_passed": all_gates_passed if gates else None,
        "arms": list(protocol["arms"]),
        "seeds": list(protocol["seeds"]),
        "transport_records": len(transport_records),
        "exact_oracle_passed": (
            oracle_record["integrity"]["passed"] if oracle_record is not None else None
        ),
        "training_sampling_audit": sampling,
        "plots": plots,
        "environment": runner._environment(device, threads),
    }
    _atomic_json(output_dir / "RECEIPT.json", receipt)
    running = output_dir / "RUNNING.json"
    if running.exists():
        running.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resume an interrupted frozen primary in bounded deterministic shards"
    )
    parser.add_argument("--protocol", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", choices=("cpu", "cuda", "auto"), default="cpu")
    parser.add_argument("--threads", type=int, default=min(4, os.cpu_count() or 1))
    parser.add_argument(
        "--max-new-cells",
        type=int,
        default=8,
        help="maximum missing arm/seed cells to commit in this invocation",
    )
    parser.add_argument(
        "--max-new-transports",
        type=int,
        default=6,
        help="maximum missing transport pairs to commit after the grid is complete",
    )
    args = parser.parse_args()
    if args.max_new_cells < 0 or args.max_new_transports < 0:
        parser.error("bounded work counts must be nonnegative")
    protocol_path = args.protocol.resolve()
    output_dir = args.output_dir.resolve()
    protocol = runner._read_protocol(protocol_path)
    device = runner._device(args.device)
    torch.set_num_threads(args.threads)
    torch.use_deterministic_algorithms(True)
    np.random.seed(0)
    torch.manual_seed(0)

    if not output_dir.is_dir() or not (output_dir / "RUNNING.json").is_file():
        raise RecoveryError("output must be an interrupted run containing RUNNING.json")
    copied_protocol = output_dir / "PROTOCOL.json"
    if copied_protocol.read_bytes() != protocol_path.read_bytes():
        raise RecoveryError("output PROTOCOL.json is not byte-identical to requested protocol")
    code_digest = tree_digest(ROOT, code_files(ROOT))
    frozen_protocol_digest = protocol_digest(protocol_path)
    if protocol.get("expected_code_digest") not in (None, code_digest):
        raise RecoveryError("scientific code digest differs from the sealed protocol")
    split_object = audit_coordinate_splits()
    split_audit = asdict(split_object)
    split_audit["passed"] = split_object.passed
    if not split_audit["passed"] or protocol.get("expected_coordinate_split_digest") not in (
        None,
        split_audit["digest"],
    ):
        raise RecoveryError("coordinate split audit failed or differs from protocol")
    receipt_base = {
        "package_version": VERSION,
        "protocol_id": protocol["protocol_id"],
        "analysis_status": protocol["analysis_status"],
        "code_digest": code_digest,
        "protocol_digest": frozen_protocol_digest,
        "coordinate_split_digest": split_audit["digest"],
    }
    _validate_base(_read_json(output_dir / "RUNNING.json"), receipt_base, "RUNNING")
    if (output_dir / "FAILED.json").exists() or (output_dir / "RECEIPT.json").exists():
        raise RecoveryError("refusing recovery when FAILED.json or RECEIPT.json exists")

    invocation = {
        "started_utc": _utc(),
        "pid": os.getpid(),
        "max_new_cells": args.max_new_cells,
        "max_new_transports": args.max_new_transports,
        "reason": "execution_supervisor_interrupted_original_runner_without_FAILED_record",
    }
    _append_event(output_dir, {**invocation, "event": "resume_started"})
    records: dict[str, list[dict[str, Any]]] = {
        name: [] for name in protocol["arms"]
    }
    new_cells = 0
    try:
        oracle_record: dict[str, Any] | None = None
        oracle_path = output_dir / "EXACT_ORACLE.json"
        if protocol.get("oracle", {}).get("enabled", False):
            if not oracle_path.exists():
                raise RecoveryError("original run did not commit its required exact oracle")
            oracle_record = _read_json(oracle_path)
            _validate_base(oracle_record, receipt_base, "exact oracle")
            if not oracle_record.get("integrity", {}).get("passed"):
                raise RecoveryError("exact oracle integrity did not pass")

        for arm_name, arm in protocol["arms"].items():
            print(f"arm={arm_name}", flush=True)
            for seed in protocol["seeds"]:
                existing = _validate_cell(
                    output_dir=output_dir,
                    protocol=protocol,
                    receipt_base=receipt_base,
                    arm_name=arm_name,
                    arm=arm,
                    seed=int(seed),
                    device=device,
                )
                if existing is not None:
                    records[arm_name].append(existing)
                    print(f"  seed={seed} validated/skipped", flush=True)
                    continue
                if new_cells >= args.max_new_cells:
                    print("bounded cell limit reached", flush=True)
                    _append_event(
                        output_dir,
                        {
                            **invocation,
                            "event": "resume_paused",
                            "finished_utc": _utc(),
                            "new_cells": new_cells,
                            "validated_cells": sum(map(len, records.values())),
                        },
                    )
                    return 0
                print(f"  seed={seed} training", flush=True)
                torch.manual_seed(seed)
                np.random.seed(seed)
                config = runner._train_config(protocol, arm, seed, device)
                model = build_model(
                    str(arm["model_name"]),
                    operator_init_std=config.operator_init_std,
                    orthogonal_parameterization=config.orthogonal_parameterization,
                )
                initialization_digest = runner._tensor_state_digest(model)
                trained = train_arm(model, config)
                evaluation_seed = int(protocol["evaluation"].get("seed_base", 500_000)) + 1000 * seed
                print(f"  seed={seed} evaluating", flush=True)
                metrics = runner._evaluate_model(trained.model, protocol, evaluation_seed, device)
                record = {
                    **receipt_base,
                    "arm": arm_name,
                    "seed": seed,
                    "initial_tensor_digest": initialization_digest,
                    "model_spec": trained.model.model_spec()
                    if callable(getattr(trained.model, "model_spec", None))
                    else {"model_name": config.model_name},
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
                checkpoint = {
                    **receipt_base,
                    "arm": arm_name,
                    "seed": seed,
                    "config": config_dict(config),
                    "state_dict": trained.model.state_dict(),
                }
                _atomic_checkpoint(
                    output_dir / "checkpoints" / arm_name / f"seed_{seed}.pt",
                    checkpoint,
                )
                _atomic_json(
                    output_dir / "arms" / arm_name / f"seed_{seed}.json", record
                )
                records[arm_name].append(record)
                new_cells += 1

        transport_config = protocol.get("transport", {})
        transport_records: list[dict[str, Any]] = []
        new_transports = 0
        if transport_config.get("enabled", False):
            pairs = [tuple(int(value) for value in pair) for pair in transport_config["seed_pairs"]]
            for arm_name in transport_config["arms"]:
                arm = protocol["arms"][arm_name]
                for pair_index, (source_seed, target_seed) in enumerate(pairs, start=1):
                    path = output_dir / "transport" / f"{arm_name}_{source_seed}_to_{target_seed}.json"
                    if path.exists():
                        item = _read_json(path)
                        _validate_base(item, receipt_base, f"transport {source_seed}->{target_seed}")
                        if item.get("arm") != arm_name or item.get("source_seed") != source_seed or item.get("target_seed") != target_seed:
                            raise RecoveryError(f"transport identity mismatch: {path}")
                        transport_records.append(item)
                        continue
                    if new_transports >= args.max_new_transports:
                        _append_event(
                            output_dir,
                            {
                                **invocation,
                                "event": "resume_paused",
                                "finished_utc": _utc(),
                                "new_cells": new_cells,
                                "new_transports": new_transports,
                                "validated_cells": sum(map(len, records.values())),
                            },
                        )
                        return 0
                    print(f"transport {arm_name} {source_seed}->{target_seed}", flush=True)
                    source = _load_model(output_dir, arm_name, arm, source_seed, device)
                    target = _load_model(output_dir, arm_name, arm, target_seed, device)
                    metrics, transport = cross_seed_transport(
                        source,
                        target,
                        seed=int(transport_config.get("seed_base", 9_000_000)) + pair_index,
                        anchor_examples=int(transport_config["anchor_examples"]),
                        test_examples=int(transport_config["test_examples"]),
                        batch_size=int(transport_config["batch_size"]),
                        device=device,
                        anchor_coordinate_split="train",
                        test_coordinate_split=str(protocol["evaluation"]["coordinate_split"]),
                    )
                    item = {
                        **receipt_base,
                        "arm": arm_name,
                        "source_seed": source_seed,
                        "target_seed": target_seed,
                        "metrics": metrics,
                        "transport": transport.to_serializable(),
                    }
                    _atomic_json(path, item)
                    transport_records.append(item)
                    new_transports += 1

        _finalize(
            output_dir=output_dir,
            protocol=protocol,
            receipt_base=receipt_base,
            records=records,
            transport_records=transport_records,
            oracle_record=oracle_record,
            split_audit=split_audit,
            device=device,
            threads=args.threads,
        )
        _append_event(
            output_dir,
            {
                **invocation,
                "event": "recovery_complete",
                "finished_utc": _utc(),
                "new_cells": new_cells,
                "new_transports": new_transports,
                "validated_cells": sum(map(len, records.values())),
            },
        )
        print("recovery complete", flush=True)
        return 0
    except Exception as error:
        _atomic_json(
            output_dir / "RECOVERY_FAILED.json",
            {
                **receipt_base,
                "status": "recovery_failed",
                "error": repr(error),
                "traceback": traceback.format_exc(),
                "utc": _utc(),
            },
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
