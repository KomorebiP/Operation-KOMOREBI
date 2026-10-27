#!/usr/bin/env python3
"""Sealed runner for Komorebi Neuralese Flat Packet Connection v0.5.0."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import sys
import time
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from komorebi_neuralese.data import EpisodeBatch, EpisodeGenerator
from komorebi_neuralese.flatness_eval import (
    NATIVE_MARGIN_TAU,
    FlatnessAuditBank,
    FlatnessAuditConfig,
    build_flatness_audit_bank,
    evaluate_control_suite,
    evaluate_deep_accuracy,
    evaluate_loop_cases,
    evaluate_path_cases,
    hard_orthogonality_residual,
)
from komorebi_neuralese.flatness_training import (
    PRIMARY_FLATNESS_ARMS,
    FlatnessTrainConfig,
    build_flatness_model,
    state_dict_digest,
    train_paired_flatness_panel,
)

# The inherited intervention evaluator is reused unchanged; it implements the
# hardened state/operator replacement controls from v0.4.
from run_packet_closure import intervention_metrics


VERSION = "0.5.0"
SCHEMA = "komorebi.flat_packet_connection.result.v1"
PREREGISTRATION = ROOT / "FLAT_CONNECTION_PREREGISTRATION.json"
CONTRACT = ROOT / "FLAT_CONNECTION_CONTRACT.json"

PROFILE_CONFIG: Mapping[str, Mapping[str, Any]] = {
    "smoke": {
        "seeds": (59,),
        "steps": 20,
        "batch_size": 32,
        "diamonds_per_length": 2,
        "loops_per_stratum": 1,
        "diamond_lengths": (8, 9),
        "diamond_suffix_lengths": (4, 8),
        "loop_repeats": (1, 8, 32),
        "loop_suffix_lengths": (0, 8, 32),
        "deep_depths": (128,),
        "deep_examples": 32,
        "causal_examples": 32,
    },
    "screen": {
        "seeds": (137,),
        "steps": 1600,
        "batch_size": 128,
        "diamonds_per_length": 16,
        "loops_per_stratum": 8,
        "diamond_lengths": (8, 9, 16, 17, 24, 25, 32, 33),
        "diamond_suffix_lengths": (4, 8, 16, 32, 64),
        "loop_repeats": (1, 2, 4, 8, 16, 32),
        "loop_suffix_lengths": (0, 4, 8, 16, 32, 64),
        "deep_depths": (128, 256, 512),
        "deep_examples": 256,
        "causal_examples": 128,
    },
    "pilot": {
        "seeds": (401, 503, 607, 709, 811),
        "steps": 2400,
        "batch_size": 128,
        "diamonds_per_length": 64,
        "loops_per_stratum": 32,
        "diamond_lengths": (8, 9, 16, 17, 24, 25, 32, 33),
        "diamond_suffix_lengths": (4, 8, 16, 32, 64),
        "loop_repeats": (1, 2, 4, 8, 16, 32),
        "loop_suffix_lengths": (0, 4, 8, 16, 32, 64),
        "deep_depths": (128, 256, 512),
        "deep_examples": 1024,
        "causal_examples": 512,
    },
}

FROZEN_THRESHOLDS: Mapping[str, float] = {
    "deep_128_pooled": 0.99,
    "deep_128_worst": 0.97,
    "deep_256_pooled": 0.97,
    "deep_256_worst": 0.92,
    "deep_512_pooled": 0.90,
    "deep_512_worst": 0.85,
    "diamond_joint_pooled": 0.98,
    "diamond_joint_worst": 0.95,
    "loop_joint_pooled": 0.98,
    "loop_joint_worst": 0.95,
    "equivalent_agreement_pooled": 0.99,
    "equivalent_agreement_worst": 0.97,
    "inequivalent_sensitivity_pooled": 0.95,
    "inequivalent_sensitivity_worst": 0.90,
    "loop_8_degradation_max": 0.03,
    "loop_32_degradation_max": 0.05,
    "robust_packet_pooled": 0.95,
    "robust_packet_worst": 0.90,
    "packet_defect_median": 0.005,
    "packet_defect_p95": 0.025,
    "full_defect_median": 0.02,
    "full_defect_p95": 0.08,
    "relative_defect_reduction": 0.50,
    "packet_vs_cr_absolute_margin": 0.10,
    "causal_patch_min": 0.95,
    "causal_control_max": 0.20,
    "causal_margin_min": 0.70,
    "boundary_rate_max": 0.005,
    "hard_polar_orthogonality_max": 1e-5,
}

REGISTERED_DESIGN_FIELDS = (
    "profile_name",
    "arms",
    "pilot_profile",
    "thresholds",
    "numerical_contract",
    "preregistration_sha256",
)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_json_bytes(value))


def strict_json_equal(left: Any, right: Any) -> bool:
    """Compare JSON-domain values without numeric coercion or NaN equality."""

    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except (TypeError, ValueError):
        return False


def validate_preregistration() -> dict[str, Any]:
    """Require the executable pilot contract to match the human-readable seal."""

    if not PREREGISTRATION.is_file():
        raise FileNotFoundError("missing FLAT_CONNECTION_PREREGISTRATION.json")
    registered = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if registered.get("schema") != "komorebi.flat_packet_connection.preregistration.v2":
        raise RuntimeError("flat-connection preregistration schema mismatch")
    if registered.get("version") != VERSION:
        raise RuntimeError("flat-connection preregistration version mismatch")
    if registered.get("arms") != list(PRIMARY_FLATNESS_ARMS):
        raise RuntimeError("executable arm order differs from preregistration")
    if registered.get("primary_arm") != "polar_packet_flat":
        raise RuntimeError("executable primary arm differs from preregistration")
    if not strict_json_equal(registered.get("thresholds"), dict(FROZEN_THRESHOLDS)):
        raise RuntimeError("executable thresholds differ from preregistration")
    pilot = registered.get("pilot")
    expected_pilot = {
        "seeds": list(PROFILE_CONFIG["pilot"]["seeds"]),
        "steps": PROFILE_CONFIG["pilot"]["steps"],
        "batch_size": PROFILE_CONFIG["pilot"]["batch_size"],
        "diamond_examples_per_length": PROFILE_CONFIG["pilot"][
            "diamonds_per_length"
        ],
        "loop_examples_per_repeat_suffix_stratum": PROFILE_CONFIG["pilot"][
            "loops_per_stratum"
        ],
        "deep_examples_per_depth_per_seed": PROFILE_CONFIG["pilot"][
            "deep_examples"
        ],
        "causal_examples_per_seed": PROFILE_CONFIG["pilot"]["causal_examples"],
    }
    if not strict_json_equal(pilot, expected_pilot):
        raise RuntimeError("executable pilot profile differs from preregistration")
    numerical = registered.get("numerical_contract", {})
    if (
        numerical.get("behavior_dtype") != "float32"
        or numerical.get("normalized_margin_tau") != NATIVE_MARGIN_TAU
        or numerical.get("threshold_equality") != "fails"
        or numerical.get("zero_norm") != "fails_closed"
    ):
        raise RuntimeError("executable numerical contract differs from preregistration")
    return registered


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def derive_seed(base: int, *tags: object) -> int:
    payload = json.dumps([int(base), *tags], separators=(",", ":")).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "little") & 0x7FFFFFFF


def source_digest() -> tuple[str, list[str]]:
    suffixes = {".py", ".md", ".json", ".toml", ".ps1", ".txt"}
    excluded = {
        "MANIFEST.json",
        "SHA256SUMS.txt",
        CONTRACT.name,
    }
    files = sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in suffixes
        and "results" not in path.relative_to(ROOT).parts
        and path.name not in excluded
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
        and ".venv" not in path.parts
        and ".git" not in path.parts
    )
    digest = hashlib.sha256()
    names: list[str] = []
    for path in files:
        relative = path.relative_to(ROOT).as_posix()
        names.append(relative)
        digest.update(relative.encode("utf-8") + b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest(), names


def runtime_receipt() -> dict[str, Any]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "torch": torch.__version__,
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "device": "cpu",
        "torch_threads": torch.get_num_threads(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "python_flags": {
            "ignore_environment": bool(sys.flags.ignore_environment),
            "isolated": bool(sys.flags.isolated),
            "safe_path": bool(sys.flags.safe_path),
            "dont_write_bytecode": bool(sys.dont_write_bytecode),
        },
    }


def batch_digest(batch: EpisodeBatch) -> str:
    digest = hashlib.sha256()
    for name in (
        "tables",
        "maps",
        "op_slots",
        "canonical_ops",
        "start",
        "target",
        "intermediates",
        "canonical_to_slot",
        "phi",
    ):
        tensor = getattr(batch, name).detach().to(device="cpu").contiguous()
        digest.update(name.encode("ascii") + b"\0")
        digest.update(str(tensor.dtype).encode("ascii") + b"\0")
        digest.update(json.dumps(list(tensor.shape), separators=(",", ":")).encode("ascii"))
        digest.update(tensor.numpy().tobytes())
    digest.update(batch.family.encode("ascii"))
    return digest.hexdigest()


def assert_clean_output(path: Path) -> None:
    if path.exists() and any(path.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)


def train_config(profile: Mapping[str, Any], seed: int, device: str) -> FlatnessTrainConfig:
    return FlatnessTrainConfig(
        seed=seed,
        steps=int(profile["steps"]),
        batch_size=int(profile["batch_size"]),
        device=device,
    )


def checkpoint_payload(result: Any, source_sha256: str) -> dict[str, Any]:
    return {
        "schema": "komorebi.flat_packet_connection.checkpoint.v1",
        "version": VERSION,
        "arm": result.arm.name,
        "config": asdict(result.config),
        "model_class": type(result.model).__name__,
        "state_dict": result.model.state_dict(),
        "initial_state_digest": result.initial_state_digest,
        "final_state_digest": result.final_state_digest,
        "episode_stream_digest": result.episode_stream_digest,
        "terminal_proposal_stream_digest": result.terminal_proposal_stream_digest,
        "relation_schedule_digest": result.relation_schedule_digest,
        "source_digest": source_sha256,
    }


def train_and_seal(
    output_dir: Path,
    profile: Mapping[str, Any],
    *,
    device: str,
    source_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir()
    training: dict[str, Any] = {}
    checkpoint_rows: list[dict[str, Any]] = []
    for seed in profile["seeds"]:
        config = train_config(profile, int(seed), device)
        panel = train_paired_flatness_panel(config)
        training[str(seed)] = {}
        for arm in PRIMARY_FLATNESS_ARMS:
            result = panel[arm]
            filename = f"{arm}_seed{seed}.pt"
            checkpoint_path = checkpoint_dir / filename
            torch.save(checkpoint_payload(result, source_sha256), checkpoint_path)
            checkpoint_rows.append(
                {
                    "path": f"checkpoints/{filename}",
                    "sha256": sha256_file(checkpoint_path),
                    "arm": arm,
                    "seed": int(seed),
                    "state_digest": result.final_state_digest,
                }
            )
            training[str(seed)][arm] = {
                "config": asdict(config),
                "trajectory": result.trajectory,
                "elapsed_seconds": result.elapsed_seconds,
                "final_loss": result.final_loss,
                "parameter_count": result.parameter_count,
                "initial_state_digest": result.initial_state_digest,
                "final_state_digest": result.final_state_digest,
                "episode_stream_digest": result.episode_stream_digest,
                "terminal_proposal_stream_digest": result.terminal_proposal_stream_digest,
                "relation_schedule_digest": result.relation_schedule_digest,
                "terminal_proposal_count": result.terminal_proposal_count,
                "terminal_candidates_accepted": result.terminal_candidates_accepted,
                "terminal_candidates_rejected": result.terminal_candidates_rejected,
            }
        del panel
    checkpoint_rows.sort(key=lambda row: (row["seed"], row["arm"]))
    seal_payload = {
        "schema": "komorebi.flat_packet_connection.checkpoint_seal.v1",
        "version": VERSION,
        "source_digest": source_sha256,
        "count": len(checkpoint_rows),
        "checkpoints": checkpoint_rows,
    }
    seal_payload["seal_sha256"] = hashlib.sha256(
        canonical_json_bytes(seal_payload)
    ).hexdigest()
    write_json(output_dir / "CHECKPOINT_SEAL.json", seal_payload)
    return training, seal_payload


def validate_checkpoint_seal(
    output_dir: Path,
    seal: Mapping[str, Any],
    profile: Mapping[str, Any],
    *,
    expected_source_digest: str,
) -> dict[tuple[int, str], Mapping[str, Any]]:
    """Validate the complete sealed checkpoint panel before any model is used."""

    if set(seal) != {
        "schema",
        "version",
        "source_digest",
        "count",
        "checkpoints",
        "seal_sha256",
    }:
        raise RuntimeError("checkpoint seal has an unexpected schema surface")
    if (
        seal.get("schema")
        != "komorebi.flat_packet_connection.checkpoint_seal.v1"
        or seal.get("version") != VERSION
        or seal.get("source_digest") != expected_source_digest
    ):
        raise RuntimeError("checkpoint seal identity mismatch")
    unhashed = dict(seal)
    observed_seal_sha = unhashed.pop("seal_sha256", None)
    expected_seal_sha = hashlib.sha256(canonical_json_bytes(unhashed)).hexdigest()
    if observed_seal_sha != expected_seal_sha:
        raise RuntimeError("checkpoint seal self-hash mismatch")
    rows = seal.get("checkpoints")
    if not isinstance(rows, list) or seal.get("count") != len(rows):
        raise RuntimeError("checkpoint seal count mismatch")
    expected_keys = {
        (int(seed), arm)
        for seed in profile["seeds"]
        for arm in PRIMARY_FLATNESS_ARMS
    }
    indexed: dict[tuple[int, str], Mapping[str, Any]] = {}
    observed_order: list[tuple[int, str]] = []
    expected_paths: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {
            "path",
            "sha256",
            "arm",
            "seed",
            "state_digest",
        }:
            raise RuntimeError("checkpoint seal row has an unexpected schema")
        arm = row.get("arm")
        seed = row.get("seed")
        if type(seed) is not int or arm not in PRIMARY_FLATNESS_ARMS:
            raise RuntimeError("checkpoint seal row has an invalid arm or seed")
        key = (seed, str(arm))
        if key in indexed:
            raise RuntimeError("checkpoint seal contains a duplicate arm/seed row")
        relative = f"checkpoints/{arm}_seed{seed}.pt"
        if row.get("path") != relative:
            raise RuntimeError("checkpoint seal path does not match its arm and seed")
        for digest_name in ("sha256", "state_digest"):
            digest = row.get(digest_name)
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise RuntimeError(f"checkpoint seal has an invalid {digest_name}")
        path = output_dir / relative
        if not path.is_file() or sha256_file(path) != row["sha256"]:
            raise RuntimeError(f"sealed checkpoint bytes do not match: {relative}")
        indexed[key] = row
        observed_order.append(key)
        expected_paths.add(relative)
    if set(indexed) != expected_keys or len(rows) != len(expected_keys):
        raise RuntimeError("checkpoint seal does not cover the exact arm/seed panel")
    if observed_order != sorted(observed_order):
        raise RuntimeError("checkpoint seal rows are not in canonical arm/seed order")
    actual_paths = {
        path.relative_to(output_dir).as_posix()
        for path in (output_dir / "checkpoints").glob("*.pt")
        if path.is_file()
    }
    if actual_paths != expected_paths:
        raise RuntimeError("checkpoint directory differs from the sealed file set")
    return indexed


def load_sealed_model(
    output_dir: Path,
    arm: str,
    seed: int,
    profile: Mapping[str, Any],
    *,
    device: str,
    expected_source_digest: str,
    seal_row: Mapping[str, Any],
) -> Any:
    path = output_dir / "checkpoints" / f"{arm}_seed{seed}.pt"
    payload = torch.load(path, map_location=device, weights_only=False)
    if set(payload) != {
        "schema",
        "version",
        "arm",
        "config",
        "model_class",
        "state_dict",
        "initial_state_digest",
        "final_state_digest",
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "source_digest",
    }:
        raise RuntimeError("checkpoint payload has an unexpected schema surface")
    if (
        payload.get("schema")
        != "komorebi.flat_packet_connection.checkpoint.v1"
        or payload.get("version") != VERSION
    ):
        raise RuntimeError("checkpoint schema or version mismatch")
    if payload.get("source_digest") != expected_source_digest:
        raise RuntimeError("checkpoint source digest does not match the frozen runner")
    if payload.get("arm") != arm:
        raise RuntimeError("checkpoint arm label mismatch")
    config = train_config(profile, seed, device)
    if not strict_json_equal(payload.get("config"), asdict(config)):
        raise RuntimeError("checkpoint training configuration mismatch")
    model = build_flatness_model(config, arm).to(device)
    if payload.get("model_class") != type(model).__name__:
        raise RuntimeError("checkpoint model class mismatch")
    if state_dict_digest(model) != payload.get("initial_state_digest"):
        raise RuntimeError("checkpoint initial-state digest mismatch")
    model.load_state_dict(payload["state_dict"], strict=True)
    if state_dict_digest(model) != payload.get("final_state_digest"):
        raise RuntimeError("checkpoint tensor digest mismatch after reload")
    if (
        seal_row.get("path") != f"checkpoints/{arm}_seed{seed}.pt"
        or seal_row.get("state_digest") != payload.get("final_state_digest")
        or seal_row.get("sha256") != sha256_file(path)
    ):
        raise RuntimeError("checkpoint payload disagrees with its seal row")
    model.eval()
    return model


def build_postseal_banks(
    output_dir: Path,
    profile: Mapping[str, Any],
) -> tuple[FlatnessAuditBank, dict[int, tuple[EpisodeBatch, EpisodeBatch]], dict[str, Any]]:
    audit_config = FlatnessAuditConfig(
        seed=derive_seed(91_337, "v0.5", "flatness-audit"),
        diamonds_per_length=int(profile["diamonds_per_length"]),
        loops_per_stratum=int(profile["loops_per_stratum"]),
        diamond_lengths=tuple(int(value) for value in profile["diamond_lengths"]),
        diamond_suffix_lengths=tuple(
            int(value) for value in profile["diamond_suffix_lengths"]
        ),
        loop_repeats=tuple(int(value) for value in profile["loop_repeats"]),
        loop_suffix_lengths=tuple(
            int(value) for value in profile["loop_suffix_lengths"]
        ),
    )
    audit_bank = build_flatness_audit_bank(audit_config)
    causal_banks: dict[int, tuple[EpisodeBatch, EpisodeBatch]] = {}
    causal_receipts: dict[str, Any] = {}
    for seed in profile["seeds"]:
        count = int(profile["causal_examples"])
        length = 64
        episode_seed = derive_seed(int(seed), "causal-main")
        control_seed = derive_seed(int(seed), "causal-operator-control")
        main = EpisodeGenerator(episode_seed).sample(count, length, family="d4")
        control = EpisodeGenerator(control_seed).sample(count, length, family="d4")
        causal_banks[int(seed)] = (main, control)
        causal_receipts[str(seed)] = {
            "main_seed": episode_seed,
            "main_digest": batch_digest(main),
            "operator_control_seed": control_seed,
            "operator_control_digest": batch_digest(control),
            "examples": count,
            "length": length,
        }
    receipt = {
        "schema": "komorebi.flat_packet_connection.eval_bank.v1",
        "audit_bank": audit_bank.to_dict(include_cases=True),
        "causal_banks": causal_receipts,
        "deep_banks": {
            str(seed): {
                family: {
                    str(depth): derive_seed(int(seed), "deep", family, int(depth))
                    for depth in (
                        profile["deep_depths"]
                        if family == "d4"
                        else (128,)
                    )
                }
                for family in ("d4", "c8", "mixed_cycle")
            }
            for seed in profile["seeds"]
        },
    }
    receipt["fingerprint"] = hashlib.sha256(canonical_json_bytes(receipt)).hexdigest()
    write_json(output_dir / "EVAL_BANK.json", receipt)
    return audit_bank, causal_banks, receipt


def validate_eval_bank_receipt(
    output_dir: Path,
    audit_bank: FlatnessAuditBank,
    causal_banks: Mapping[int, tuple[EpisodeBatch, EpisodeBatch]],
    receipt: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> None:
    """Verify that every post-seal bank is exactly committed by its receipt."""

    if receipt.get("schema") != "komorebi.flat_packet_connection.eval_bank.v1":
        raise RuntimeError("evaluation-bank receipt schema mismatch")
    unhashed = dict(receipt)
    observed = unhashed.pop("fingerprint", None)
    if observed != hashlib.sha256(canonical_json_bytes(unhashed)).hexdigest():
        raise RuntimeError("evaluation-bank receipt fingerprint mismatch")
    if not strict_json_equal(
        receipt.get("audit_bank"), audit_bank.to_dict(include_cases=True)
    ):
        raise RuntimeError("evaluation-bank audit cases disagree with receipt")
    expected_seed_keys = {str(int(seed)) for seed in profile["seeds"]}
    causal_receipts = receipt.get("causal_banks")
    if not isinstance(causal_receipts, Mapping) or set(causal_receipts) != expected_seed_keys:
        raise RuntimeError("evaluation-bank causal seed grid mismatch")
    for seed in profile["seeds"]:
        key = str(int(seed))
        main, control = causal_banks[int(seed)]
        row = causal_receipts[key]
        if (
            row.get("main_seed") != derive_seed(int(seed), "causal-main")
            or row.get("operator_control_seed")
            != derive_seed(int(seed), "causal-operator-control")
            or row.get("main_digest") != batch_digest(main)
            or row.get("operator_control_digest") != batch_digest(control)
            or row.get("examples") != int(profile["causal_examples"])
            or row.get("length") != 64
        ):
            raise RuntimeError("evaluation-bank causal receipt mismatch")
    expected_deep = {
        str(int(seed)): {
            family: {
                str(int(depth)): derive_seed(int(seed), "deep", family, int(depth))
                for depth in (
                    profile["deep_depths"] if family == "d4" else (128,)
                )
            }
            for family in ("d4", "c8", "mixed_cycle")
        }
        for seed in profile["seeds"]
    }
    if not strict_json_equal(receipt.get("deep_banks"), expected_deep):
        raise RuntimeError("evaluation-bank deep seed grid mismatch")
    stored = json.loads((output_dir / "EVAL_BANK.json").read_text(encoding="utf-8"))
    if not strict_json_equal(stored, receipt):
        raise RuntimeError("stored evaluation-bank receipt changed after sealing")


def evaluate_one_model(
    model: Any,
    audit_bank: FlatnessAuditBank,
    causal_banks: tuple[EpisodeBatch, EpisodeBatch],
    profile: Mapping[str, Any],
    *,
    seed: int,
    device: str,
) -> dict[str, Any]:
    diamonds = evaluate_path_cases(
        model,
        audit_bank.diamonds,
        seed=derive_seed(seed, "diamonds"),
        equivalent=True,
        device=device,
    )
    inequivalent = evaluate_path_cases(
        model,
        audit_bank.inequivalent,
        seed=derive_seed(seed, "inequivalent"),
        equivalent=False,
        device=device,
    )
    loops = evaluate_loop_cases(
        model,
        audit_bank.loops,
        seed=derive_seed(seed, "loops"),
        device=device,
    )
    deep: dict[str, Any] = {}
    for family in ("d4", "c8", "mixed_cycle"):
        depths = profile["deep_depths"] if family == "d4" else (128,)
        deep[family] = {
            str(depth): evaluate_deep_accuracy(
                model,
                seed=derive_seed(seed, "deep", family, int(depth)),
                depth=int(depth),
                examples=int(profile["deep_examples"]),
                family=family,
                device=device,
            )
            for depth in depths
        }
    main_batch, operator_control_batch = causal_banks
    causal = intervention_metrics(
        model,
        int(profile["causal_examples"]),
        min(128, int(profile["causal_examples"])),
        derive_seed(seed, "causal-main"),
        torch.device(device),
        length=64,
        split=32,
        operator_step=3,
        episode_batch=main_batch,
        operator_control_batch=operator_control_batch,
        control_seed=derive_seed(seed, "causal-controls"),
    )
    return {
        "diamonds": diamonds,
        "inequivalent": inequivalent,
        "loops": loops,
        "deep": deep,
        "causal_interventions": causal,
        "hard_polar_geometry": hard_orthogonality_residual(
            model,
            seed=derive_seed(seed, "hard-polar-geometry"),
        ),
    }


def evaluate_panel(
    output_dir: Path,
    audit_bank: FlatnessAuditBank,
    causal_banks: Mapping[int, tuple[EpisodeBatch, EpisodeBatch]],
    profile: Mapping[str, Any],
    *,
    device: str,
    source_sha256: str,
    checkpoint_seal: Mapping[str, Any],
) -> dict[str, Any]:
    seal_rows = validate_checkpoint_seal(
        output_dir,
        checkpoint_seal,
        profile,
        expected_source_digest=source_sha256,
    )
    records: dict[str, Any] = {}
    for seed in profile["seeds"]:
        records[str(seed)] = {}
        for arm in PRIMARY_FLATNESS_ARMS:
            model = load_sealed_model(
                output_dir,
                arm,
                int(seed),
                profile,
                device=device,
                expected_source_digest=source_sha256,
                seal_row=seal_rows[(int(seed), arm)],
            )
            records[str(seed)][arm] = evaluate_one_model(
                model,
                audit_bank,
                causal_banks[int(seed)],
                profile,
                seed=int(seed),
                device=device,
            )
            del model
    return records


def _rate_summary(rows: Sequence[Mapping[str, Any]], numerator: str, denominator: str) -> dict[str, Any]:
    numerators = [int(row[numerator]) for row in rows]
    denominators = [int(row[denominator]) for row in rows]
    rates = [value / total for value, total in zip(numerators, denominators, strict=True)]
    return {
        "numerator": sum(numerators),
        "denominator": sum(denominators),
        "pooled": sum(numerators) / sum(denominators),
        "mean_seed": sum(rates) / len(rates),
        "worst_seed": min(rates),
        "per_seed": rates,
    }


def _value_summary(values: Sequence[Any]) -> dict[str, Any]:
    normalized: list[float | None] = []
    finite: list[float] = []
    for value in values:
        try:
            converted = float(value)
        except (TypeError, ValueError, OverflowError):
            converted = math.nan
        if math.isfinite(converted):
            finite.append(converted)
            normalized.append(converted)
        else:
            normalized.append(None)
    if len(finite) != len(values) or not finite:
        return {
            "count": len(values),
            "finite_count": len(finite),
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
            "per_seed": normalized,
        }
    ordered = sorted(finite)
    return {
        "count": len(finite),
        "finite_count": len(finite),
        "mean": sum(finite) / len(finite),
        "median": ordered[(len(ordered) - 1) // 2],
        "minimum": min(finite),
        "maximum": max(finite),
        "per_seed": finite,
    }


def aggregate_records(
    records: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    aggregate: dict[str, Any] = {}
    seed_keys = [str(seed) for seed in profile["seeds"]]
    for arm in PRIMARY_FLATNESS_ARMS:
        rows = [records[seed][arm] for seed in seed_keys]
        deep: dict[str, Any] = {}
        for depth in profile["deep_depths"]:
            deep_rows = [row["deep"]["d4"][str(depth)] for row in rows]
            deep[str(depth)] = {
                "ordinary": _rate_summary(deep_rows, "ordinary_correct", "total"),
                "robust": _rate_summary(deep_rows, "robust_correct", "total"),
                "boundary": _rate_summary(deep_rows, "boundary", "total"),
            }
        diamond_rows = [row["diamonds"] for row in rows]
        negative_rows = [row["inequivalent"] for row in rows]
        loop_rows = [row["loops"] for row in rows]
        causal_rows = [row["causal_interventions"] for row in rows]
        geometry_rows = [row["hard_polar_geometry"] for row in rows]
        aggregate[arm] = {
            "deep_d4": deep,
            "diamonds": {
                "joint": _rate_summary(diamond_rows, "joint_correct", "total"),
                "joint_robust": _rate_summary(diamond_rows, "joint_robust", "total"),
                "agreement": _rate_summary(
                    diamond_rows, "prediction_agreement", "total"
                ),
                "boundary": _rate_summary(
                    diamond_rows, "boundary", "decision_total"
                ),
                "full_defect_seed_medians": _value_summary(
                    [row["full_holonomy_defect"]["median"] for row in diamond_rows]
                ),
                "full_defect_seed_p95": _value_summary(
                    [row["full_holonomy_defect"]["p95"] for row in diamond_rows]
                ),
                "packet_defect_seed_medians": _value_summary(
                    [row["packet_quotient_defect"]["median"] for row in diamond_rows]
                ),
                "packet_defect_seed_p95": _value_summary(
                    [row["packet_quotient_defect"]["p95"] for row in diamond_rows]
                ),
            },
            "inequivalent": {
                "sensitivity": _rate_summary(
                    negative_rows, "joint_correct", "total"
                ),
                "prediction_agreement": _rate_summary(
                    negative_rows, "prediction_agreement", "total"
                ),
            },
            "loops": {
                "joint": _rate_summary(loop_rows, "joint_correct", "total"),
                "joint_robust": _rate_summary(
                    loop_rows, "joint_robust", "total"
                ),
                "agreement": _rate_summary(loop_rows, "agreement", "total"),
                "boundary": _rate_summary(
                    loop_rows, "boundary", "decision_total"
                ),
                "degradation": _value_summary(
                    [row["accuracy_degradation"] for row in loop_rows]
                ),
            },
            "causal": {
                key: _value_summary([row[key] for row in causal_rows])
                for key in (
                    "native_original_accuracy",
                    "state_patch_accuracy",
                    "angle_matched_state_control_accuracy",
                    "random_state_patch_accuracy",
                    "reachable_state_control_accuracy",
                    "operator_patch_accuracy",
                    "random_operator_patch_accuracy",
                    "cross_context_operator_control_accuracy",
                )
                if all(isinstance(row.get(key), (int, float)) for row in causal_rows)
            },
            "maximum_orthogonality_residual": max(
                row["orthogonality_residual"]["maximum"] for row in geometry_rows
            ),
            "zero_shot_128": {
                family: _rate_summary(
                    [row["deep"][family]["128"] for row in rows],
                    "ordinary_correct",
                    "total",
                )
                for family in ("c8", "mixed_cycle")
            },
        }
    return aggregate


def _finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
    )


def _hex_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _complete_numeric_summary(value: Any, expected_count: int) -> bool:
    if not isinstance(value, Mapping):
        return False
    if value.get("count") != expected_count or value.get("finite_count") != expected_count:
        return False
    return all(
        _finite_number(value.get(key))
        for key in ("minimum", "median", "p95", "maximum", "mean")
    )


def _valid_native_decision(value: Any, expected_total: int) -> bool:
    if not isinstance(value, Mapping) or value.get("total") != expected_total:
        return False
    counts = [value.get(key) for key in ("ordinary_correct", "robust_correct", "boundary")]
    if any(type(count) is not int or not 0 <= count <= expected_total for count in counts):
        return False
    ordinary, robust, boundary = (int(count) for count in counts)
    if robust > ordinary:
        return False
    expected_rates = {
        "ordinary_accuracy": ordinary / expected_total,
        "robust_accuracy": robust / expected_total,
        "boundary_rate": boundary / expected_total,
    }
    if any(value.get(key) != expected for key, expected in expected_rates.items()):
        return False
    minimum_margin = value.get("minimum_margin")
    return (
        value.get("margin_tau") == NATIVE_MARGIN_TAU
        and _hex_digest(value.get("logits_sha256"))
        and _finite_number(minimum_margin)
    )


def validate_execution_integrity(
    records: Mapping[str, Any],
    aggregate: Mapping[str, Any],
    controls: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    """Fail closed on incomplete grids, undefined geometry, or stale aggregates."""

    expected_seeds = [str(int(seed)) for seed in profile["seeds"]]
    expected_arms = set(PRIMARY_FLATNESS_ARMS)
    expected_paths = int(profile["diamonds_per_length"]) * len(
        profile["diamond_lengths"]
    )
    expected_loops = (
        int(profile["loops_per_stratum"])
        * len(profile["loop_repeats"])
        * len(profile["loop_suffix_lengths"])
    )
    expected_strata = {
        f"repeats_{int(repeats)}_suffix_{int(suffix)}"
        for repeats in profile["loop_repeats"]
        for suffix in profile["loop_suffix_lengths"]
    }
    checks = {
        "record_grid_exact": True,
        "registered_counts_exact": True,
        "all_claim_geometry_defined": True,
        "native_decisions_well_formed": True,
        "causal_grid_exact": True,
        "control_grid_exact": True,
        "aggregate_recomputed_exact": True,
    }
    if set(records) != set(expected_seeds):
        checks["record_grid_exact"] = False
    for seed in expected_seeds:
        seed_rows = records.get(seed)
        if not isinstance(seed_rows, Mapping) or set(seed_rows) != expected_arms:
            checks["record_grid_exact"] = False
            continue
        for arm in PRIMARY_FLATNESS_ARMS:
            row = seed_rows.get(arm)
            if not isinstance(row, Mapping) or set(row) != {
                "diamonds",
                "inequivalent",
                "loops",
                "deep",
                "causal_interventions",
                "hard_polar_geometry",
            }:
                checks["record_grid_exact"] = False
                continue
            for path_name, equivalent in (("diamonds", True), ("inequivalent", False)):
                path = row.get(path_name)
                if (
                    not isinstance(path, Mapping)
                    or path.get("total") != expected_paths
                    or path.get("decision_total") != 2 * expected_paths
                    or path.get("equivalent") is not equivalent
                    or not _hex_digest(path.get("native_logits_digest"))
                ):
                    checks["registered_counts_exact"] = False
                    continue
                for summary_name in (
                    "full_holonomy_defect",
                    "anchor_restriction_defect",
                    "packet_quotient_defect",
                ):
                    if not _complete_numeric_summary(
                        path.get(summary_name), expected_paths
                    ):
                        checks["all_claim_geometry_defined"] = False
                if not all(
                    type(path.get(key)) is int
                    and 0 <= int(path[key]) <= expected_paths
                    for key in (
                        "joint_correct",
                        "joint_robust",
                        "prediction_agreement",
                        "target_distinct",
                    )
                ):
                    checks["registered_counts_exact"] = False

            loops = row.get("loops")
            if (
                not isinstance(loops, Mapping)
                or loops.get("total") != expected_loops
                or loops.get("decision_total") != 2 * expected_loops
                or not isinstance(loops.get("strata"), Mapping)
                or set(loops["strata"]) != expected_strata
            ):
                checks["registered_counts_exact"] = False
            else:
                for stratum in loops["strata"].values():
                    if (
                        not isinstance(stratum, Mapping)
                        or stratum.get("total") != int(profile["loops_per_stratum"])
                        or not _hex_digest(stratum.get("loop_logits_sha256"))
                        or not _hex_digest(stratum.get("baseline_logits_sha256"))
                    ):
                        checks["registered_counts_exact"] = False

            deep = row.get("deep")
            expected_deep = {
                "d4": {str(int(depth)) for depth in profile["deep_depths"]},
                "c8": {"128"},
                "mixed_cycle": {"128"},
            }
            if not isinstance(deep, Mapping) or set(deep) != set(expected_deep):
                checks["registered_counts_exact"] = False
            else:
                for family, depths in expected_deep.items():
                    family_rows = deep.get(family)
                    if not isinstance(family_rows, Mapping) or set(family_rows) != depths:
                        checks["registered_counts_exact"] = False
                        continue
                    for depth in depths:
                        decision = family_rows[depth]
                        if (
                            not _valid_native_decision(
                                decision, int(profile["deep_examples"])
                            )
                            or decision.get("family") != family
                            or decision.get("depth") != int(depth)
                        ):
                            checks["native_decisions_well_formed"] = False

            causal = row.get("causal_interventions")
            required_causal = (
                "native_original_accuracy",
                "state_patch_accuracy",
                "operator_patch_accuracy",
                "relative_conjugacy_operator_control_accuracy",
                "state_transition_eligible_examples",
                "operator_transition_eligible_examples",
            )
            if (
                not isinstance(causal, Mapping)
                or causal.get("available") is not True
                or causal.get("examples") != int(profile["causal_examples"])
                or causal.get("length") != 64
                or causal.get("episode_bank_supplied") is not True
                or causal.get("operator_control_bank_supplied") is not True
                or any(causal.get(key) is None for key in required_causal)
            ):
                checks["causal_grid_exact"] = False

            geometry = row.get("hard_polar_geometry")
            if not isinstance(geometry, Mapping) or any(
                not _complete_numeric_summary(geometry.get(name), 64)
                for name in (
                    "orthogonality_residual",
                    "determinant_magnitude_error",
                )
            ):
                checks["all_claim_geometry_defined"] = False

    control_gates = controls.get("gates") if isinstance(controls, Mapping) else None
    if (
        not isinstance(control_gates, Mapping)
        or not control_gates
        or any(type(value) is not bool for value in control_gates.values())
        or controls.get("assay_valid") != all(control_gates.values())
    ):
        checks["control_grid_exact"] = False
    try:
        recomputed = aggregate_records(records, profile)
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        checks["aggregate_recomputed_exact"] = False
    else:
        if not strict_json_equal(aggregate, recomputed):
            checks["aggregate_recomputed_exact"] = False
    return {"valid": all(checks.values()), "checks": checks}


def _loop_repeat_degradation(
    records: Mapping[str, Any],
    seeds: Sequence[int],
    arm: str,
    repeats: int,
) -> dict[str, Any]:
    per_seed: list[float] = []
    strata: list[dict[str, Any]] = []
    for seed in seeds:
        rows = records[str(seed)][arm]["loops"]["strata"]
        selected = [
            row
            for row in rows.values()
            if int(row["repeats"]) == repeats
        ]
        if not selected:
            return {
                "pooled": None,
                "maximum_stratum": None,
                "per_seed": [],
                "strata": [],
            }
        loop_correct = sum(int(row["loop_correct"]) for row in selected)
        baseline_correct = sum(int(row["baseline_correct"]) for row in selected)
        total = sum(int(row["total"]) for row in selected)
        per_seed.append((baseline_correct - loop_correct) / total)
        strata.extend(
            {
                "seed": int(seed),
                "suffix_length": int(row["suffix_length"]),
                "degradation": float(row["accuracy_degradation"]),
            }
            for row in selected
        )
    return {
        "pooled": sum(row["degradation"] for row in strata) / len(strata),
        "maximum_stratum": max(row["degradation"] for row in strata),
        "per_seed": per_seed,
        "strata": sorted(strata, key=lambda row: (row["seed"], row["suffix_length"])),
    }


def _causal_gate(records: Mapping[str, Any], seeds: Sequence[int], arm: str) -> dict[str, Any]:
    patch_keys = (
        "state_patch_accuracy",
        "operator_patch_accuracy",
        "state_patch_transition_accuracy",
        "operator_patch_transition_accuracy",
    )
    control_keys = (
        "angle_matched_state_control_accuracy",
        "random_state_patch_accuracy",
        "reachable_state_control_accuracy",
        "random_operator_patch_accuracy",
        "relative_conjugacy_operator_control_accuracy",
        "cross_context_operator_control_accuracy",
        "angle_matched_state_control_transition_accuracy",
        "random_state_patch_transition_accuracy",
        "reachable_state_control_transition_accuracy",
        "random_operator_patch_transition_accuracy",
        "relative_conjugacy_operator_control_transition_accuracy",
        "cross_context_operator_control_transition_accuracy",
    )
    rows = [records[str(seed)][arm]["causal_interventions"] for seed in seeds]
    patches = [row.get(key) for row in rows for key in patch_keys]
    controls = [row.get(key) for row in rows for key in control_keys]
    native = [row.get("native_original_accuracy") for row in rows]
    defined_keys = (
        "native_original_defined_fraction",
        "state_patch_defined_fraction",
        "operator_patch_defined_fraction",
        "angle_matched_state_control_defined_fraction",
        "random_state_patch_defined_fraction",
        "reachable_state_control_defined_fraction",
        "random_operator_patch_defined_fraction",
        "relative_conjugacy_operator_control_defined_fraction",
        "cross_context_operator_control_defined_fraction",
    )
    coverage: list[Any] = [
        row.get(key) for row in rows for key in defined_keys
    ]
    for row in rows:
        examples = row.get("examples")
        if type(examples) is int and examples > 0:
            coverage.extend(
                (
                    row.get("state_counterfactual_target_distinct_fraction"),
                    row.get("operator_counterfactual_target_distinct_fraction"),
                    row.get("state_transition_eligible_examples") / examples
                    if type(row.get("state_transition_eligible_examples")) is int
                    else None,
                    row.get("operator_transition_eligible_examples") / examples
                    if type(row.get("operator_transition_eligible_examples")) is int
                    else None,
                )
            )
        else:
            coverage.extend((None, None, None, None))
    if not all(_finite_number(value) for value in patches + controls + native + coverage):
        return {
            "minimum_patch": None,
            "maximum_control": None,
            "minimum_margin": None,
            "minimum_native": None,
            "minimum_coverage": None,
            "pass": False,
        }
    patches = [float(value) for value in patches]
    controls = [float(value) for value in controls]
    native = [float(value) for value in native]
    coverage = [float(value) for value in coverage]
    minimum_patch = min(patches)
    maximum_control = max(controls)
    return {
        "minimum_patch": minimum_patch,
        "maximum_control": maximum_control,
        "minimum_margin": minimum_patch - maximum_control,
        "minimum_native": min(native),
        "minimum_coverage": min(coverage),
        "pass": bool(
            minimum_patch >= FROZEN_THRESHOLDS["causal_patch_min"]
            and maximum_control <= FROZEN_THRESHOLDS["causal_control_max"]
            and minimum_patch - maximum_control
            >= FROZEN_THRESHOLDS["causal_margin_min"]
            and min(native) >= FROZEN_THRESHOLDS["causal_patch_min"]
            and min(coverage) >= FROZEN_THRESHOLDS["causal_patch_min"]
        ),
    }


def adjudicate(
    records: Mapping[str, Any],
    aggregate: Mapping[str, Any],
    controls: Mapping[str, Any],
    profile_name: str,
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    seeds = tuple(int(seed) for seed in profile["seeds"])
    primary = aggregate["polar_packet_flat"]
    exact_arm = aggregate["polar_exact_flat"]
    supervised = aggregate["polar_supervised"]
    legacy_cr = aggregate["polar_cr_v04"]
    integrity = validate_execution_integrity(records, aggregate, controls, profile)
    checks: dict[str, dict[str, Any]] = {}

    def add(name: str, observed: Any, threshold: Any, passed: bool) -> None:
        checks[name] = {
            "observed": observed,
            "threshold": threshold,
            "pass": bool(passed),
        }

    for depth in (128, 256, 512):
        if str(depth) not in primary["deep_d4"]:
            continue
        row = primary["deep_d4"][str(depth)]["ordinary"]
        robust_row = primary["deep_d4"][str(depth)]["robust"]
        pooled_threshold = FROZEN_THRESHOLDS[f"deep_{depth}_pooled"]
        worst_threshold = FROZEN_THRESHOLDS[f"deep_{depth}_worst"]
        add(
            f"deep_{depth}",
            {
                "ordinary_pooled": row["pooled"],
                "ordinary_worst_seed": row["worst_seed"],
                "robust_pooled": robust_row["pooled"],
                "robust_worst_seed": robust_row["worst_seed"],
            },
            {"pooled_min": pooled_threshold, "worst_seed_min": worst_threshold},
            row["pooled"] >= pooled_threshold
            and row["worst_seed"] >= worst_threshold
            and robust_row["pooled"] >= pooled_threshold
            and robust_row["worst_seed"] >= worst_threshold,
        )
    diamond = primary["diamonds"]
    add(
        "diamond_joint_correct",
        {
            "pooled": diamond["joint"]["pooled"],
            "worst_seed": diamond["joint"]["worst_seed"],
        },
        {
            "pooled_min": FROZEN_THRESHOLDS["diamond_joint_pooled"],
            "worst_seed_min": FROZEN_THRESHOLDS["diamond_joint_worst"],
        },
        diamond["joint"]["pooled"]
        >= FROZEN_THRESHOLDS["diamond_joint_pooled"]
        and diamond["joint"]["worst_seed"]
        >= FROZEN_THRESHOLDS["diamond_joint_worst"],
    )
    add(
        "equivalent_path_agreement",
        {
            "pooled": diamond["agreement"]["pooled"],
            "worst_seed": diamond["agreement"]["worst_seed"],
        },
        {
            "pooled_min": FROZEN_THRESHOLDS["equivalent_agreement_pooled"],
            "worst_seed_min": FROZEN_THRESHOLDS["equivalent_agreement_worst"],
        },
        diamond["agreement"]["pooled"]
        >= FROZEN_THRESHOLDS["equivalent_agreement_pooled"]
        and diamond["agreement"]["worst_seed"]
        >= FROZEN_THRESHOLDS["equivalent_agreement_worst"],
    )
    loop = primary["loops"]
    loop_robust = loop["joint_robust"]
    add(
        "loop_plus_suffix_joint_correct",
        {
            "ordinary_pooled": loop["joint"]["pooled"],
            "ordinary_worst_seed": loop["joint"]["worst_seed"],
            "robust_pooled": loop_robust["pooled"],
            "robust_worst_seed": loop_robust["worst_seed"],
        },
        {
            "pooled_min": FROZEN_THRESHOLDS["loop_joint_pooled"],
            "worst_seed_min": FROZEN_THRESHOLDS["loop_joint_worst"],
        },
        loop["joint"]["pooled"] >= FROZEN_THRESHOLDS["loop_joint_pooled"]
        and loop["joint"]["worst_seed"]
        >= FROZEN_THRESHOLDS["loop_joint_worst"]
        and loop_robust["pooled"] >= FROZEN_THRESHOLDS["loop_joint_pooled"]
        and loop_robust["worst_seed"] >= FROZEN_THRESHOLDS["loop_joint_worst"],
    )
    negative = primary["inequivalent"]["sensitivity"]
    add(
        "matched_inequivalent_sensitivity",
        {"pooled": negative["pooled"], "worst_seed": negative["worst_seed"]},
        {
            "pooled_min": FROZEN_THRESHOLDS["inequivalent_sensitivity_pooled"],
            "worst_seed_min": FROZEN_THRESHOLDS[
                "inequivalent_sensitivity_worst"
            ],
        },
        negative["pooled"]
        >= FROZEN_THRESHOLDS["inequivalent_sensitivity_pooled"]
        and negative["worst_seed"]
        >= FROZEN_THRESHOLDS["inequivalent_sensitivity_worst"],
    )
    robust = diamond["joint_robust"]
    add(
        "robust_packet_membership",
        {"pooled": robust["pooled"], "worst_seed": robust["worst_seed"]},
        {
            "pooled_min": FROZEN_THRESHOLDS["robust_packet_pooled"],
            "worst_seed_min": FROZEN_THRESHOLDS["robust_packet_worst"],
        },
        robust["pooled"] >= FROZEN_THRESHOLDS["robust_packet_pooled"]
        and robust["worst_seed"] >= FROZEN_THRESHOLDS["robust_packet_worst"],
    )
    boundary_rows = {
        "diamonds": diamond["boundary"]["pooled"],
        "loops": loop["boundary"]["pooled"],
        **{
            f"deep_{depth}": primary["deep_d4"][str(depth)]["boundary"]["pooled"]
            for depth in profile["deep_depths"]
        },
    }
    add(
        "native_boundary_rate",
        boundary_rows,
        {"maximum": FROZEN_THRESHOLDS["boundary_rate_max"]},
        max(boundary_rows.values()) <= FROZEN_THRESHOLDS["boundary_rate_max"],
    )
    for repeats, threshold_key in (
        (8, "loop_8_degradation_max"),
        (32, "loop_32_degradation_max"),
    ):
        degradation = _loop_repeat_degradation(
            records, seeds, "polar_packet_flat", repeats
        )
        add(
            f"loop_{repeats}_degradation",
            degradation,
            {"maximum": FROZEN_THRESHOLDS[threshold_key]},
            degradation["maximum_stratum"] is not None
            and degradation["maximum_stratum"] <= FROZEN_THRESHOLDS[threshold_key],
        )
    packet_median = diamond["packet_defect_seed_medians"]["maximum"]
    packet_p95 = diamond["packet_defect_seed_p95"]["maximum"]
    add(
        "packet_quotient_defect",
        {"worst_seed_median": packet_median, "worst_seed_p95": packet_p95},
        {
            "median_max": FROZEN_THRESHOLDS["packet_defect_median"],
            "p95_max": FROZEN_THRESHOLDS["packet_defect_p95"],
        },
        packet_median is not None
        and packet_p95 is not None
        and packet_median <= FROZEN_THRESHOLDS["packet_defect_median"]
        and packet_p95 <= FROZEN_THRESHOLDS["packet_defect_p95"],
    )
    exact_median = exact_arm["diamonds"]["full_defect_seed_medians"]["maximum"]
    exact_p95 = exact_arm["diamonds"]["full_defect_seed_p95"]["maximum"]
    add(
        "exact_arm_full_flatness_secondary",
        {"worst_seed_median": exact_median, "worst_seed_p95": exact_p95},
        {
            "median_max": FROZEN_THRESHOLDS["full_defect_median"],
            "p95_max": FROZEN_THRESHOLDS["full_defect_p95"],
        },
        exact_median is not None
        and exact_p95 is not None
        and exact_median <= FROZEN_THRESHOLDS["full_defect_median"]
        and exact_p95 <= FROZEN_THRESHOLDS["full_defect_p95"],
    )
    supervised_defects = [
        records[str(seed)]["polar_supervised"]["diamonds"][
            "packet_quotient_defect"
        ]["median"]
        for seed in seeds
    ]
    primary_defects = [
        records[str(seed)]["polar_packet_flat"]["diamonds"][
            "packet_quotient_defect"
        ]["median"]
        for seed in seeds
    ]
    reductions = [
        1.0 - primary_value / baseline
        if baseline is not None and baseline > 0.0 and primary_value is not None
        else 0.0
        for baseline, primary_value in zip(
            supervised_defects, primary_defects, strict=True
        )
    ]
    required_seed_count = 4 if len(seeds) == 5 else len(seeds)
    add(
        "packet_defect_relative_reduction",
        {"per_seed": reductions, "passing_seeds": sum(value >= 0.5 for value in reductions)},
        {
            "minimum_reduction": FROZEN_THRESHOLDS["relative_defect_reduction"],
            "minimum_passing_seeds": required_seed_count,
        },
        sum(
            value >= FROZEN_THRESHOLDS["relative_defect_reduction"]
            for value in reductions
        )
        >= required_seed_count,
    )
    if "512" in primary["deep_d4"]:
        depth_differences = [
            records[str(seed)]["polar_packet_flat"]["deep"]["d4"]["512"][
                "robust_accuracy"
            ]
            - records[str(seed)]["polar_cr_v04"]["deep"]["d4"]["512"][
                "robust_accuracy"
            ]
            for seed in seeds
        ]
        loop_differences = [
            records[str(seed)]["polar_packet_flat"]["loops"]["joint_robust_rate"]
            - records[str(seed)]["polar_cr_v04"]["loops"]["joint_robust_rate"]
            for seed in seeds
        ]
        add(
            "primary_beats_legacy_cr",
            {
                "depth_512_mean_difference": sum(depth_differences) / len(seeds),
                "loop_mean_difference": sum(loop_differences) / len(seeds),
                "positive_depth_seeds": sum(value > 0.0 for value in depth_differences),
                "positive_loop_seeds": sum(value > 0.0 for value in loop_differences),
            },
            {
                "mean_margin": FROZEN_THRESHOLDS["packet_vs_cr_absolute_margin"],
                "positive_seed_count": required_seed_count,
            },
            sum(depth_differences) / len(seeds)
            >= FROZEN_THRESHOLDS["packet_vs_cr_absolute_margin"]
            and sum(loop_differences) / len(seeds)
            >= FROZEN_THRESHOLDS["packet_vs_cr_absolute_margin"]
            and sum(value > 0.0 for value in depth_differences)
            >= required_seed_count
            and sum(value > 0.0 for value in loop_differences)
            >= required_seed_count,
        )
        shuffled_depth_differences = [
            records[str(seed)]["polar_packet_flat"]["deep"]["d4"]["512"][
                "robust_accuracy"
            ]
            - records[str(seed)]["polar_shuffled_packet"]["deep"]["d4"]["512"][
                "robust_accuracy"
            ]
            for seed in seeds
        ]
        shuffled_loop_differences = [
            records[str(seed)]["polar_packet_flat"]["loops"]["joint_robust_rate"]
            - records[str(seed)]["polar_shuffled_packet"]["loops"]["joint_robust_rate"]
            for seed in seeds
        ]
        shuffled_defect_improvements = [
            records[str(seed)]["polar_shuffled_packet"]["diamonds"][
                "packet_quotient_defect"
            ]["median"]
            - records[str(seed)]["polar_packet_flat"]["diamonds"][
                "packet_quotient_defect"
            ]["median"]
            for seed in seeds
        ]
        add(
            "true_relation_beats_shuffled_control",
            {
                "depth_512_differences": shuffled_depth_differences,
                "loop_differences": shuffled_loop_differences,
                "packet_defect_improvements": shuffled_defect_improvements,
            },
            {"strictly_positive_in_seeds": required_seed_count},
            all(
                sum(value > 0.0 for value in values) >= required_seed_count
                and sum(values) / len(values) > 0.0
                for values in (
                    shuffled_depth_differences,
                    shuffled_loop_differences,
                    shuffled_defect_improvements,
                )
            ),
        )
    causal = _causal_gate(records, seeds, "polar_packet_flat")
    add("causal_semantics_preserved", causal, "frozen causal thresholds", causal["pass"])
    orthogonality = primary["maximum_orthogonality_residual"]
    add(
        "hard_polar_isometry",
        orthogonality,
        {"maximum": FROZEN_THRESHOLDS["hard_polar_orthogonality_max"]},
        orthogonality <= FROZEN_THRESHOLDS["hard_polar_orthogonality_max"],
    )

    add(
        "complete_registered_evaluation",
        integrity["checks"],
        "all integrity checks true",
        integrity["valid"],
    )

    assay_valid = bool(controls["assay_valid"])
    scientific_gate_names = [
        name
        for name in checks
        if name != "exact_arm_full_flatness_secondary"
    ]
    scientific_pass = all(checks[name]["pass"] for name in scientific_gate_names)
    if profile_name != "pilot":
        flatness_status = "DEVELOPMENTAL_NOT_ADJUDICATED"
    elif not integrity["valid"] or not assay_valid:
        flatness_status = "NOT_EVALUATED"
    else:
        flatness_status = "PASS" if scientific_pass else "FAIL"
    return {
        "execution_integrity": "PASS" if integrity["valid"] else "FAIL",
        "assay_validity": "PASS" if assay_valid else "FAIL",
        "scientific_flatness": flatness_status,
        "scientific_connection": "NOT_EVALUATED",
        "ambient_necessity": "SEPARATE_CALIBRATION_ONLY",
        "control_gates": controls["gates"],
        "integrity_checks": integrity["checks"],
        "scientific_checks": checks,
        "all_primary_checks_pass": scientific_pass,
    }


def render_chart(output_dir: Path, aggregate: Mapping[str, Any], profile: Mapping[str, Any]) -> str:
    selected = (
        "polar_supervised",
        "polar_cr_v04",
        "polar_exact_flat",
        "polar_packet_flat",
        "polar_hybrid_flat",
        "polar_shuffled_packet",
    )
    labels = [
        "supervised",
        "CR v0.4",
        "exact-flat",
        "packet-flat",
        "hybrid",
        "false equality",
    ]
    colors = ["#777777", "#5b8ff9", "#61d9a8", "#f6bd16", "#7262fd", "#e8684a"]
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    ax = axes[0, 0]
    for arm, label, color in zip(selected, labels, colors, strict=True):
        depths = [int(value) for value in profile["deep_depths"]]
        values = [aggregate[arm]["deep_d4"][str(depth)]["ordinary"]["pooled"] for depth in depths]
        ax.plot(depths, values, marker="o", label=label, color=color)
    ax.set_title("D4 accuracy across recurrent depth")
    ax.set_xlabel("Depth")
    ax.set_ylabel("Native accuracy")
    ax.set_ylim(0.0, 1.02)
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, ncol=2)

    ax = axes[0, 1]
    x = np.arange(len(selected))
    width = 0.36
    diamond = [aggregate[arm]["diamonds"]["joint"]["pooled"] for arm in selected]
    loops = [aggregate[arm]["loops"]["joint"]["pooled"] for arm in selected]
    ax.bar(x - width / 2, diamond, width, label="held-out diamonds")
    ax.bar(x + width / 2, loops, width, label="loop + suffix")
    ax.set_xticks(x, labels, rotation=25, ha="right")
    ax.set_ylim(0.0, 1.02)
    ax.set_title("Behavioral path independence")
    ax.set_ylabel("Joint correctness")
    ax.legend(fontsize=8)

    ax = axes[1, 0]
    full = [max(aggregate[arm]["diamonds"]["full_defect_seed_medians"]["mean"] or 1e-12, 1e-12) for arm in selected]
    packet = [max(aggregate[arm]["diamonds"]["packet_defect_seed_medians"]["mean"] or 1e-12, 1e-12) for arm in selected]
    ax.bar(x - width / 2, full, width, label="full holonomy")
    ax.bar(x + width / 2, packet, width, label="packet quotient")
    ax.set_yscale("log")
    ax.set_xticks(x, labels, rotation=25, ha="right")
    ax.set_title("Held-out geometric defects")
    ax.set_ylabel("Median defect (log scale)")
    ax.legend(fontsize=8)

    ax = axes[1, 1]
    sensitivity = [aggregate[arm]["inequivalent"]["sensitivity"]["pooled"] for arm in selected]
    robust = [aggregate[arm]["diamonds"]["joint_robust"]["pooled"] for arm in selected]
    ax.bar(x - width / 2, sensitivity, width, label="inequivalent sensitivity")
    ax.bar(x + width / 2, robust, width, label="robust equivalent packet")
    ax.set_xticks(x, labels, rotation=25, ha="right")
    ax.set_ylim(0.0, 1.02)
    ax.set_title("Noncollapse and robust semantics")
    ax.set_ylabel("Rate")
    ax.legend(fontsize=8)

    path = output_dir / "flat_connection_summary.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path.name


def _format(value: Any) -> str:
    return "—" if value is None else f"{float(value):.4f}"


def render_report(result: Mapping[str, Any]) -> str:
    aggregate = result["aggregate"]
    status = result["status"]
    lines = [
        "# Flat Packet Connection v0.5.0",
        "",
        "**Author:** Komorebi P.",
        "",
        f"**Run profile:** `{result['profile']}`",
        "",
        "## Outcome",
        "",
        f"- Execution integrity: **{status['execution_integrity']}**",
        f"- Assay validity: **{status['assay_validity']}**",
        f"- Scientific flatness: **{status['scientific_flatness']}**",
        f"- Cross-context learned connection: **{status['scientific_connection']}**",
        f"- Ambient necessity: **{status['ambient_necessity']}**",
        "",
        "The primary question is whether anonymous short relation cells create",
        "path independence on long held-out consequences while preserving causal",
        "operator semantics. Hard polar isometry is fixed in every learned arm.",
        "",
        "## Main results",
        "",
        "| Arm | D4 depth 128 | D4 deepest | Diamonds | Loop + suffix | Full defect | Packet defect | Inequivalent sensitivity |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    deepest = str(max(int(value) for value in result["config"]["deep_depths"]))
    for arm in PRIMARY_FLATNESS_ARMS:
        row = aggregate[arm]
        lines.append(
            "| "
            + " | ".join(
                (
                    f"`{arm}`",
                    _format(row["deep_d4"]["128"]["ordinary"]["pooled"]),
                    _format(row["deep_d4"][deepest]["ordinary"]["pooled"]),
                    _format(row["diamonds"]["joint"]["pooled"]),
                    _format(row["loops"]["joint"]["pooled"]),
                    _format(row["diamonds"]["full_defect_seed_medians"]["mean"]),
                    _format(row["diamonds"]["packet_defect_seed_medians"]["mean"]),
                    _format(row["inequivalent"]["sensitivity"]["pooled"]),
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Assay calibration",
            "",
        ]
    )
    for name, passed in status["control_gates"].items():
        lines.append(f"- `{name}`: **{'PASS' if passed else 'FAIL'}**")
    lines.extend(
        [
            "",
            "The exact compiled oracle must be perfectly correct and flat. The",
            "quotient-curved oracle must remain behaviorally perfect while retaining",
            "nonzero full-space holonomy. Identity collapse and random isometry must",
            "fail semantics. A synthetic suffix-visible residue must pass an immediate",
            "endpoint test and fail the future-continuation test.",
            "",
            "## Frozen scientific checks",
            "",
        ]
    )
    for name, row in status["scientific_checks"].items():
        lines.append(f"- `{name}`: **{'PASS' if row['pass'] else 'FAIL'}**")
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "A pilot pass supports finite-depth, structurally supervised D4 flatness",
            "in this explicit table-conditioned recurrent architecture. It does not",
            "establish spontaneous Neuralese, an infinite-horizon guarantee, a learned",
            "cross-model connection, architecture-independent emergence, awareness, or",
            "consciousness. A valid scientific failure remains a retained result; package",
            "verification is independent of whether the hypothesis succeeds.",
            "",
            "The separate ANC-4 calibration tests when a four-dimensional vertical",
            "fiber is mathematically necessary for delay memory. It is not part of the",
            "flatness adjudication and cannot rescue it.",
        ]
    )
    return "\n".join(lines) + "\n"


def validate_invocation(profile_name: str, output_dir: Path, replay: bool) -> str:
    canonical_pilot = ROOT / "results" / "flat_connection_pilot"
    if profile_name != "pilot":
        if replay:
            raise ValueError("--replay is only meaningful for the pilot profile")
        return "developmental"
    if replay:
        if output_dir.resolve() == canonical_pilot.resolve():
            raise ValueError("pilot replay cannot target the canonical retained directory")
        return "non_evidentiary_pilot_replay"
    if output_dir.resolve() != canonical_pilot.resolve():
        raise ValueError("fresh pilot may target only results/flat_connection_pilot")
    return "fresh_pilot"


def validate_pilot_contract(
    contract: Mapping[str, Any],
    *,
    source_sha256: str,
    preregistration_sha256: str,
    preregistration: Mapping[str, Any],
) -> None:
    """Bind the fresh pilot to its source, preregistration, and full design."""

    required = {
        "schema",
        "version",
        "author",
        "source_digest",
        *REGISTERED_DESIGN_FIELDS,
        "registered_design_sha256",
    }
    expected_profile = {
        key: list(value) if isinstance(value, tuple) else value
        for key, value in PROFILE_CONFIG["pilot"].items()
    }
    design = {
        field: contract.get(field) for field in REGISTERED_DESIGN_FIELDS
    }
    try:
        expected_design_sha256 = hashlib.sha256(
            canonical_json_bytes(design)
        ).hexdigest()
    except (TypeError, ValueError):
        expected_design_sha256 = ""
    if (
        not required.issubset(contract)
        or contract.get("schema") != "komorebi.flat_packet_connection.contract.v1"
        or contract.get("version") != VERSION
        or contract.get("author") != "Komorebi P."
        or contract.get("profile_name") != "pilot"
        or contract.get("source_digest") != source_sha256
        or contract.get("preregistration_sha256") != preregistration_sha256
        or contract.get("arms") != list(PRIMARY_FLATNESS_ARMS)
        or not strict_json_equal(contract.get("pilot_profile"), expected_profile)
        or not strict_json_equal(
            contract.get("thresholds"), dict(FROZEN_THRESHOLDS)
        )
        or not strict_json_equal(
            contract.get("numerical_contract"),
            preregistration.get("numerical_contract"),
        )
        or contract.get("registered_design_sha256") != expected_design_sha256
        or (
            "primary_arm" in contract
            and contract.get("primary_arm") != "polar_packet_flat"
        )
    ):
        raise RuntimeError("pilot contract does not bind the complete frozen design")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=tuple(PROFILE_CONFIG), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args(argv)
    if args.device != "cpu":
        raise ValueError("the frozen v0.5 profiles currently permit CPU only")
    if not sys.flags.ignore_environment or not sys.flags.safe_path or not sys.dont_write_bytecode:
        raise RuntimeError("invoke with python -E -P -B")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        # A hosting runtime may have initialized its interop pool already;
        # intra-op determinism remains explicitly fixed above.
        pass
    profile = dict(PROFILE_CONFIG[args.profile])
    preregistration = validate_preregistration()
    output_dir = args.output_dir.resolve()
    run_mode = validate_invocation(args.profile, output_dir, args.replay)
    assert_clean_output(output_dir)
    started = time.perf_counter()
    source_sha256, source_files = source_digest()
    prereg_sha256 = sha256_file(PREREGISTRATION)
    contract_sha256 = None
    if args.profile == "pilot":
        if not CONTRACT.exists():
            raise FileNotFoundError("pilot requires a frozen FLAT_CONNECTION_CONTRACT.json")
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        validate_pilot_contract(
            contract,
            source_sha256=source_sha256,
            preregistration_sha256=prereg_sha256,
            preregistration=preregistration,
        )
        contract_sha256 = sha256_file(CONTRACT)
    write_json(
        output_dir / "RUN_STARTED.json",
        {
            "schema": "komorebi.flat_packet_connection.run_started.v1",
            "version": VERSION,
            "profile": args.profile,
            "run_mode": run_mode,
            "source_digest": source_sha256,
            "preregistration_sha256": prereg_sha256,
            "contract_sha256": contract_sha256,
            "runtime": runtime_receipt(),
        },
    )
    phase_started = time.perf_counter()
    training, checkpoint_seal = train_and_seal(
        output_dir,
        profile,
        device=args.device,
        source_sha256=source_sha256,
    )
    training_seconds = time.perf_counter() - phase_started
    phase_started = time.perf_counter()
    audit_bank, causal_banks, eval_receipt = build_postseal_banks(output_dir, profile)
    validate_eval_bank_receipt(
        output_dir,
        audit_bank,
        causal_banks,
        eval_receipt,
        profile,
    )
    controls = evaluate_control_suite(
        audit_bank,
        deep_examples=min(256, int(profile["deep_examples"])),
        device=args.device,
    )
    records = evaluate_panel(
        output_dir,
        audit_bank,
        causal_banks,
        profile,
        device=args.device,
        source_sha256=source_sha256,
        checkpoint_seal=checkpoint_seal,
    )
    evaluation_seconds = time.perf_counter() - phase_started
    aggregate = aggregate_records(records, profile)
    status = adjudicate(records, aggregate, controls, args.profile, profile)
    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": args.profile,
        "run_mode": run_mode,
        "config": profile,
        "thresholds": dict(FROZEN_THRESHOLDS),
        "source_digest": source_sha256,
        "source_files": source_files,
        "preregistration_sha256": prereg_sha256,
        "contract_sha256": contract_sha256,
        "checkpoint_seal": checkpoint_seal,
        "evaluation_bank_fingerprint": eval_receipt["fingerprint"],
        "training": training,
        "controls": controls,
        "records": records,
        "aggregate": aggregate,
        "status": status,
        "runtime": runtime_receipt(),
        "phase_seconds": {
            "training": training_seconds,
            "evaluation": evaluation_seconds,
            "total": time.perf_counter() - started,
        },
    }
    chart = render_chart(output_dir, aggregate, profile)
    result["chart"] = {"path": chart, "sha256": sha256_file(output_dir / chart)}
    write_json(output_dir / "RESULTS.json", result)
    write_json(output_dir / "GATES.json", status)
    (output_dir / "REPORT.md").write_text(render_report(result), encoding="utf-8")
    complete = {
        "schema": "komorebi.flat_packet_connection.run_complete.v1",
        "version": VERSION,
        "profile": args.profile,
        "run_mode": run_mode,
        "contract_sha256": contract_sha256,
        "execution_integrity": status["execution_integrity"],
        "assay_validity": status["assay_validity"],
        "scientific_flatness": status["scientific_flatness"],
        "results_sha256": sha256_file(output_dir / "RESULTS.json"),
        "report_sha256": sha256_file(output_dir / "REPORT.md"),
        "chart_sha256": sha256_file(output_dir / chart),
    }
    write_json(output_dir / "RUN_COMPLETE.json", complete)
    print(json.dumps(complete, indent=2, sort_keys=True))
    return (
        0
        if status["execution_integrity"] == "PASS"
        and status["assay_validity"] == "PASS"
        else 2
    )


if __name__ == "__main__":
    raise SystemExit(main())
