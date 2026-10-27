#!/usr/bin/env python3
"""Sealed developmental runner for the v0.6 Invariant Observable Kernel block."""

from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import platform
from types import SimpleNamespace
import sys
import time
from typing import Any, Iterable, Mapping, Sequence

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
from komorebi_neuralese.evaluate import intervention_metrics
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
    numeric_summary,
)
from komorebi_neuralese.flatness_training import relation_cell_bank
from komorebi_neuralese.invariant_kernel_eval import (
    DEFAULT_SUFFIX_LENGTHS,
    adversarial_assay_controls,
    audit_centered_quotient_paths,
    audit_centered_quotient_structure,
    audit_centered_quotient_suffixes,
    audit_kernel_structure,
    build_suffix_word_bank,
    centered_null_intervention_audit,
    extract_model_geometry,
    fiber_intervention_audit,
    gauge_covariance_audit,
    path_defect_audit,
    path_products,
    suffix_leakage_audit,
)
from komorebi_neuralese.invariant_kernel_models import (
    LearnedFrameBlockIsometricOperatorRNN,
)
from komorebi_neuralese.invariant_kernel_training import (
    PRIMARY_INVARIANT_KERNEL_ARMS,
    V06_PLAN_VERSION,
    InvariantKernelTrainConfig,
    LearnedIntertwinerPolarRNN,
    build_invariant_kernel_model,
    invariant_kernel_checkpoint_metadata,
    invariant_kernel_training_contract,
    train_paired_invariant_kernel_panel,
)
from komorebi_neuralese.packet_closure_train import state_dict_digest


VERSION = "0.6.0"
SCHEMA = "komorebi.neuralese.invariant_kernel.result.v1"
PREREGISTRATION = ROOT / "INVARIANT_KERNEL_PREREGISTRATION.json"
CANONICAL_PILOT_DIR = ROOT / "results" / "invariant_kernel_pilot"
RECORD_DIR_NAME = "records"
CHART_NAME = "invariant_kernel_summary.png"

PROFILE_CONFIG: Mapping[str, Mapping[str, Any]] = {
    "smoke": {
        "seeds": (73,),
        "steps": 40,
        "batch_size": 32,
        "auxiliary_contexts": 8,
        "auxiliary_delay_steps": 0,
        "auxiliary_ramp_end_step": 40,
        "geometry_contexts": 8,
        "diamonds_per_length": 2,
        "diamond_lengths": (8, 9),
        "diamond_suffix_lengths": (4, 8),
        "loops_per_stratum": 1,
        "loop_repeats": (1, 8, 32),
        "loop_suffix_lengths": (0, 8, 32),
        "deep_depths": (128,),
        "deep_examples": 32,
        "causal_examples": 32,
    },
    "screen": {
        "seeds": (947,),
        "steps": 3200,
        "batch_size": 128,
        "auxiliary_contexts": 8,
        "auxiliary_delay_steps": 800,
        "auxiliary_ramp_end_step": 1600,
        "geometry_contexts": 256,
        "diamonds_per_length": 16,
        "diamond_lengths": (8, 9, 16, 17, 24, 25, 32, 33),
        "diamond_suffix_lengths": (4, 8, 16, 32, 64),
        "loops_per_stratum": 8,
        "loop_repeats": (1, 2, 4, 8, 16, 32),
        "loop_suffix_lengths": (0, 4, 8, 16, 32, 64),
        "deep_depths": (128, 256, 512),
        "deep_examples": 256,
        "causal_examples": 128,
    },
    "pilot": {
        "seeds": (1009, 1217, 1429, 1693, 1879),
        "steps": 3200,
        "batch_size": 128,
        "auxiliary_contexts": 8,
        "auxiliary_delay_steps": 800,
        "auxiliary_ramp_end_step": 1600,
        "geometry_contexts": 1024,
        "diamonds_per_length": 64,
        "diamond_lengths": (8, 9, 16, 17, 24, 25, 32, 33),
        "diamond_suffix_lengths": (4, 8, 16, 32, 64),
        "loops_per_stratum": 32,
        "loop_repeats": (1, 2, 4, 8, 16, 32),
        "loop_suffix_lengths": (0, 4, 8, 16, 32, 64),
        "deep_depths": (128, 256, 512),
        "deep_examples": 1024,
        "causal_examples": 512,
    },
}

ALGEBRAIC_SUFFIX_LENGTHS = (0, 1, 2, 4, 8, 16, 32, 64)
INTERVENTION_SUFFIX_LENGTHS = (0, 4, 16, 64)
INTERVENTION_MAGNITUDES = (0.25, 0.5, 1.0)


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
    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except (TypeError, ValueError):
        return False


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def derive_seed(base: int, *tags: object) -> int:
    payload = json.dumps([int(base), *tags], separators=(",", ":")).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:4], "little") & 0x7FFFFFFF


def _profile_as_registered(profile: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "seeds": list(profile["seeds"]),
        "steps": profile["steps"],
        "batch_size": profile["batch_size"],
        "auxiliary_contexts": profile["auxiliary_contexts"],
        "auxiliary_delay_steps": profile["auxiliary_delay_steps"],
        "auxiliary_ramp_end_step": profile["auxiliary_ramp_end_step"],
        "geometry_contexts": profile["geometry_contexts"],
        "diamonds_per_length": profile["diamonds_per_length"],
        "diamond_lengths": list(profile["diamond_lengths"]),
        "diamond_suffix_lengths": list(profile["diamond_suffix_lengths"]),
        "loops_per_repeat_suffix_stratum": profile["loops_per_stratum"],
        "loop_repeats": list(profile["loop_repeats"]),
        "loop_suffix_lengths": list(profile["loop_suffix_lengths"]),
        "deep_depths": list(profile["deep_depths"]),
        "deep_examples_per_depth": profile["deep_examples"],
        "causal_examples": profile["causal_examples"],
    }


def validate_preregistration() -> dict[str, Any]:
    if not PREREGISTRATION.is_file():
        raise FileNotFoundError("missing INVARIANT_KERNEL_PREREGISTRATION.json")
    registered = json.loads(PREREGISTRATION.read_text(encoding="utf-8"))
    if registered.get("schema") != "komorebi.invariant_observable_kernel.preregistration.v1":
        raise RuntimeError("invariant-kernel preregistration schema mismatch")
    if registered.get("version") != VERSION or registered.get("author") != "Komorebi P.":
        raise RuntimeError("invariant-kernel preregistration identity mismatch")
    if registered.get("training_plan_version") != V06_PLAN_VERSION:
        raise RuntimeError("invariant-kernel training-plan version mismatch")
    arms = registered.get("arms")
    if not isinstance(arms, list) or [row.get("name") for row in arms] != list(
        PRIMARY_INVARIANT_KERNEL_ARMS
    ):
        raise RuntimeError("executable arm order differs from preregistration")
    if registered.get("primary_arm") != "learned_intertwiner":
        raise RuntimeError("primary arm differs from preregistration")
    if registered.get("positive_control_arm") != "hard_kernel_semantic_flat":
        raise RuntimeError("positive control differs from preregistration")
    profiles = registered.get("profiles")
    expected_profiles = {
        name: _profile_as_registered(profile)
        for name, profile in PROFILE_CONFIG.items()
    }
    if not strict_json_equal(profiles, expected_profiles):
        raise RuntimeError("executable profiles differ from preregistration")
    intervention = registered.get("intervention_contract", {})
    if (
        intervention.get("suffix_lengths") != list(INTERVENTION_SUFFIX_LENGTHS)
        or intervention.get("algebraic_suffix_lengths")
        != list(ALGEBRAIC_SUFFIX_LENGTHS)
        or intervention.get("relative_perturbation_magnitudes")
        != list(INTERVENTION_MAGNITUDES)
    ):
        raise RuntimeError("intervention grid differs from preregistration")
    numerical = registered.get("numerical_contract", {})
    if (
        numerical.get("training_and_native_behavior_dtype") != "float32"
        or numerical.get("geometry_policy")
        != "promote_executed_float32_tensors_to_float64_without_reexecution"
        or numerical.get("native_margin_tau") != NATIVE_MARGIN_TAU
        or numerical.get("rank_relative_threshold") != 1e-6
        or numerical.get("rank_ambiguity_band") != [1e-7, 1e-5]
        or numerical.get("threshold_equality") != "fails"
        or numerical.get("integer_minimum_count_equality") != "passes"
        or numerical.get("nonfinite") != "fails_closed"
        or numerical.get("deterministic_algorithms") is not True
        or numerical.get("cpu_threads") != 1
    ):
        raise RuntimeError("numerical contract differs from executable policy")
    return registered


def source_digest() -> tuple[str, list[str]]:
    suffixes = {".py", ".md", ".json", ".toml", ".ps1", ".txt"}
    excluded = {"MANIFEST.json", "SHA256SUMS.txt"}
    files = sorted(
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in suffixes
        and "results" not in path.relative_to(ROOT).parts
        and path.name not in excluded
        and "__pycache__" not in path.parts
        and ".pytest_cache" not in path.parts
        and ".git" not in path.parts
        and ".venv" not in path.parts
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


def assert_clean_output(path: Path) -> None:
    if path.exists() and (not path.is_dir() or any(path.iterdir())):
        raise FileExistsError(f"refusing to overwrite nonempty output directory: {path}")
    path.mkdir(parents=True, exist_ok=True)


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
        tensor = getattr(batch, name).detach().cpu().contiguous()
        digest.update(name.encode("ascii") + b"\0")
        digest.update(str(tensor.dtype).encode("ascii") + b"\0")
        digest.update(json.dumps(list(tensor.shape), separators=(",", ":")).encode("ascii"))
        digest.update(tensor.numpy().tobytes())
    digest.update(batch.family.encode("ascii"))
    return digest.hexdigest()


def _words_digest(words: Mapping[int, torch.Tensor]) -> str:
    digest = hashlib.sha256(b"v0.6-suffix-word-bank")
    for length in sorted(words):
        tensor = words[length].detach().cpu().contiguous()
        digest.update(int(length).to_bytes(4, "little"))
        digest.update(tensor.numpy().tobytes())
    return digest.hexdigest()


def train_config(profile: Mapping[str, Any], seed: int, device: str) -> InvariantKernelTrainConfig:
    return InvariantKernelTrainConfig(
        seed=int(seed),
        steps=int(profile["steps"]),
        batch_size=int(profile["batch_size"]),
        auxiliary_contexts=int(profile["auxiliary_contexts"]),
        auxiliary_delay_steps=int(profile["auxiliary_delay_steps"]),
        auxiliary_ramp_end_step=int(profile["auxiliary_ramp_end_step"]),
        device=device,
    )


def _json_safe_tree(value: Any) -> bool:
    if value is None or isinstance(value, (str, bool, int)):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, torch.Tensor):
        return value.layout == torch.strided
    if isinstance(value, (list, tuple)):
        return all(_json_safe_tree(item) for item in value)
    if isinstance(value, Mapping):
        return all(isinstance(key, str) and _json_safe_tree(item) for key, item in value.items())
    return False


def checkpoint_payload(
    trained: Any,
    *,
    source_sha256: str,
    preregistration_sha256: str,
) -> dict[str, Any]:
    metadata = invariant_kernel_checkpoint_metadata(trained)
    payload = {
        "schema": "komorebi.neuralese.invariant_kernel.checkpoint.v1",
        "version": VERSION,
        "arm": trained.arm.name,
        "seed": trained.config.seed,
        "config": asdict(trained.config),
        "model_class": type(trained.model).__name__,
        "state_dict": trained.model.state_dict(),
        "initial_state_digest": trained.initial_state_digest,
        "final_state_digest": trained.final_state_digest,
        "training_metadata": metadata,
        "source_digest": source_sha256,
        "preregistration_sha256": preregistration_sha256,
    }
    if not _json_safe_tree(payload):
        raise TypeError("checkpoint payload contains a weights-only-unsafe value")
    return payload


def build_evaluation_banks(
    output_dir: Path,
    profile: Mapping[str, Any],
    *,
    source_sha256: str,
    preregistration_sha256: str,
) -> tuple[FlatnessAuditBank, dict[int, dict[str, Any]], dict[str, Any]]:
    audit_config = FlatnessAuditConfig(
        seed=derive_seed(606_013, "v0.6", "behavioral-path-bank"),
        diamonds_per_length=int(profile["diamonds_per_length"]),
        loops_per_stratum=int(profile["loops_per_stratum"]),
        diamond_lengths=tuple(int(value) for value in profile["diamond_lengths"]),
        diamond_suffix_lengths=tuple(
            int(value) for value in profile["diamond_suffix_lengths"]
        ),
        loop_repeats=tuple(int(value) for value in profile["loop_repeats"]),
        loop_suffix_lengths=tuple(int(value) for value in profile["loop_suffix_lengths"]),
    )
    audit_bank = build_flatness_audit_bank(audit_config)
    banks: dict[int, dict[str, Any]] = {}
    receipts: dict[str, Any] = {}
    for raw_seed in profile["seeds"]:
        seed = int(raw_seed)
        geometry_seed = derive_seed(seed, "v0.6", "geometry")
        main_seed = derive_seed(seed, "v0.6", "causal-main")
        control_seed = derive_seed(seed, "v0.6", "causal-cross-context")
        geometry = EpisodeGenerator(geometry_seed).sample(
            int(profile["geometry_contexts"]), 0, family="d4"
        )
        main = EpisodeGenerator(main_seed).sample(
            int(profile["causal_examples"]), 64, family="d4"
        )
        control = EpisodeGenerator(control_seed).sample(
            int(profile["causal_examples"]), 64, family="d4"
        )
        suffix_seed = derive_seed(seed, "v0.6", "algebraic-suffixes")
        suffix_words = build_suffix_word_bank(
            operator_count=2,
            samples_per_length=8,
            seed=suffix_seed,
            lengths=ALGEBRAIC_SUFFIX_LENGTHS,
        )
        null_batches: dict[int, EpisodeBatch] = {}
        null_receipts: dict[str, Any] = {}
        for length in INTERVENTION_SUFFIX_LENGTHS:
            null_seed = derive_seed(seed, "v0.6", "null-intervention", int(length))
            batch = EpisodeGenerator(null_seed).sample(
                int(profile["causal_examples"]), int(length), family="d4"
            )
            null_batches[int(length)] = batch
            null_receipts[str(length)] = {
                "seed": null_seed,
                "digest": batch_digest(batch),
                "examples": int(profile["causal_examples"]),
            }
        banks[seed] = {
            "geometry": geometry,
            "causal_main": main,
            "causal_control": control,
            "suffix_words": suffix_words,
            "null_batches": null_batches,
        }
        receipts[str(seed)] = {
            "geometry": {
                "seed": geometry_seed,
                "digest": batch_digest(geometry),
                "contexts": int(profile["geometry_contexts"]),
            },
            "causal_main": {
                "seed": main_seed,
                "digest": batch_digest(main),
                "examples": int(profile["causal_examples"]),
                "length": 64,
            },
            "causal_control": {
                "seed": control_seed,
                "digest": batch_digest(control),
                "examples": int(profile["causal_examples"]),
                "length": 64,
            },
            "suffix_words": {
                "seed": suffix_seed,
                "digest": _words_digest(suffix_words),
                "lengths": list(ALGEBRAIC_SUFFIX_LENGTHS),
                "samples_per_length": 8,
            },
            "null_interventions": null_receipts,
            "deep_seeds": {
                family: {
                    str(depth): derive_seed(seed, "v0.6", "deep", family, int(depth))
                    for depth in (profile["deep_depths"] if family == "d4" else (128,))
                }
                for family in ("d4", "c8", "mixed_cycle")
            },
        }
    receipt = {
        "schema": "komorebi.neuralese.invariant_kernel.eval_bank.v1",
        "version": VERSION,
        "source_digest": source_sha256,
        "preregistration_sha256": preregistration_sha256,
        "behavioral_bank": audit_bank.to_dict(include_cases=True),
        "per_seed": receipts,
    }
    receipt["fingerprint"] = hashlib.sha256(canonical_json_bytes(receipt)).hexdigest()
    write_json(output_dir / "EVAL_BANK.json", receipt)
    return audit_bank, banks, receipt


def validate_evaluation_banks(
    output_dir: Path,
    audit_bank: FlatnessAuditBank,
    banks: Mapping[int, Mapping[str, Any]],
    receipt: Mapping[str, Any],
    profile: Mapping[str, Any],
    *,
    expected_source_digest: str,
    expected_preregistration_sha256: str,
) -> None:
    if receipt.get("schema") != "komorebi.neuralese.invariant_kernel.eval_bank.v1":
        raise RuntimeError("evaluation-bank schema mismatch")
    if (
        receipt.get("version") != VERSION
        or receipt.get("source_digest") != expected_source_digest
        or receipt.get("preregistration_sha256") != expected_preregistration_sha256
    ):
        raise RuntimeError("evaluation-bank identity mismatch")
    unsigned = dict(receipt)
    observed = unsigned.pop("fingerprint", None)
    if observed != hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest():
        raise RuntimeError("evaluation-bank fingerprint mismatch")
    if not strict_json_equal(receipt.get("behavioral_bank"), audit_bank.to_dict(include_cases=True)):
        raise RuntimeError("behavioral evaluation bank changed after sealing")
    if set(banks) != {int(seed) for seed in profile["seeds"]}:
        raise RuntimeError("evaluation bank has the wrong seed grid")
    if set(receipt.get("per_seed", {})) != {str(int(seed)) for seed in profile["seeds"]}:
        raise RuntimeError("evaluation-bank receipt has the wrong seed grid")
    for seed, bank in banks.items():
        row = receipt["per_seed"][str(seed)]
        if (
            row["geometry"]["digest"] != batch_digest(bank["geometry"])
            or row["causal_main"]["digest"] != batch_digest(bank["causal_main"])
            or row["causal_control"]["digest"] != batch_digest(bank["causal_control"])
            or row["suffix_words"]["digest"] != _words_digest(bank["suffix_words"])
        ):
            raise RuntimeError("evaluation-bank tensor digest mismatch")
        for length, batch in bank["null_batches"].items():
            if row["null_interventions"][str(length)]["digest"] != batch_digest(batch):
                raise RuntimeError("null-intervention bank digest mismatch")
    stored = json.loads((output_dir / "EVAL_BANK.json").read_text(encoding="utf-8"))
    if not strict_json_equal(stored, receipt):
        raise RuntimeError("stored evaluation-bank receipt changed after sealing")


def train_and_seal(
    output_dir: Path,
    profile: Mapping[str, Any],
    *,
    device: str,
    source_sha256: str,
    preregistration_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir()
    training: dict[str, Any] = {}
    checkpoint_rows: list[dict[str, Any]] = []
    for raw_seed in profile["seeds"]:
        seed = int(raw_seed)
        config = train_config(profile, seed, device)
        panel = train_paired_invariant_kernel_panel(config)
        training[str(seed)] = {}
        for arm in PRIMARY_INVARIANT_KERNEL_ARMS:
            trained = panel[arm]
            filename = f"{arm}_seed{seed}.pt"
            path = checkpoint_dir / filename
            torch.save(
                checkpoint_payload(
                    trained,
                    source_sha256=source_sha256,
                    preregistration_sha256=preregistration_sha256,
                ),
                path,
            )
            checkpoint_rows.append(
                {
                    "path": f"checkpoints/{filename}",
                    "sha256": sha256_file(path),
                    "arm": arm,
                    "seed": seed,
                    "state_digest": trained.final_state_digest,
                }
            )
            training[str(seed)][arm] = {
                "config": asdict(config),
                "trajectory": trained.trajectory,
                "elapsed_seconds": trained.elapsed_seconds,
                "final_loss": trained.final_loss,
                "parameter_count": trained.parameter_count,
                "trainable_parameter_count": trained.trainable_parameter_count,
                "initial_state_digest": trained.initial_state_digest,
                "core_initial_state_digest": trained.core_initial_state_digest,
                "final_state_digest": trained.final_state_digest,
                "episode_stream_digest": trained.episode_stream_digest,
                "terminal_proposal_stream_digest": trained.terminal_proposal_stream_digest,
                "relation_schedule_digest": trained.relation_schedule_digest,
                "terminal_firewall_policy_digest": trained.terminal_firewall_policy_digest,
                "terminal_proposal_count": trained.terminal_proposal_count,
                "terminal_candidates_accepted": trained.terminal_candidates_accepted,
                "terminal_candidates_rejected": trained.terminal_candidates_rejected,
                "terminal_identity_rejections": trained.terminal_identity_rejections,
                "terminal_r2_rejections": trained.terminal_r2_rejections,
                "construction_digest": trained.construction_digest,
                "ambient_initial_digest": trained.ambient_initial_digest,
                "ambient_final_digest": trained.ambient_final_digest,
            }
        del panel
    checkpoint_rows.sort(key=lambda row: (row["seed"], row["arm"]))
    seal = {
        "schema": "komorebi.neuralese.invariant_kernel.checkpoint_seal.v1",
        "version": VERSION,
        "source_digest": source_sha256,
        "preregistration_sha256": preregistration_sha256,
        "count": len(checkpoint_rows),
        "checkpoints": checkpoint_rows,
    }
    seal["seal_sha256"] = hashlib.sha256(canonical_json_bytes(seal)).hexdigest()
    write_json(output_dir / "CHECKPOINT_SEAL.json", seal)
    return training, seal


def _hex_digest(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def validate_checkpoint_seal(
    output_dir: Path,
    seal: Mapping[str, Any],
    profile: Mapping[str, Any],
    *,
    expected_source_digest: str,
    expected_preregistration_sha256: str,
) -> dict[tuple[int, str], Mapping[str, Any]]:
    expected_surface = {
        "schema",
        "version",
        "source_digest",
        "preregistration_sha256",
        "count",
        "checkpoints",
        "seal_sha256",
    }
    if set(seal) != expected_surface:
        raise RuntimeError("checkpoint seal has an unexpected schema surface")
    if (
        seal.get("schema")
        != "komorebi.neuralese.invariant_kernel.checkpoint_seal.v1"
        or seal.get("version") != VERSION
        or seal.get("source_digest") != expected_source_digest
        or seal.get("preregistration_sha256") != expected_preregistration_sha256
    ):
        raise RuntimeError("checkpoint seal identity mismatch")
    unsigned = dict(seal)
    observed_self_hash = unsigned.pop("seal_sha256", None)
    if observed_self_hash != hashlib.sha256(canonical_json_bytes(unsigned)).hexdigest():
        raise RuntimeError("checkpoint seal self-hash mismatch")
    rows = seal.get("checkpoints")
    if not isinstance(rows, list) or type(seal.get("count")) is not int:
        raise RuntimeError("checkpoint seal count is malformed")
    expected_keys = {
        (int(seed), arm)
        for seed in profile["seeds"]
        for arm in PRIMARY_INVARIANT_KERNEL_ARMS
    }
    indexed: dict[tuple[int, str], Mapping[str, Any]] = {}
    order: list[tuple[int, str]] = []
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
        seed, arm = row.get("seed"), row.get("arm")
        if type(seed) is not int or arm not in PRIMARY_INVARIANT_KERNEL_ARMS:
            raise RuntimeError("checkpoint seal row has an invalid seed or arm")
        key = (seed, str(arm))
        if key in indexed:
            raise RuntimeError("checkpoint seal contains a duplicate seed/arm row")
        relative = f"checkpoints/{arm}_seed{seed}.pt"
        if row.get("path") != relative:
            raise RuntimeError("checkpoint path does not match its seed and arm")
        if not _hex_digest(row.get("sha256")) or not _hex_digest(row.get("state_digest")):
            raise RuntimeError("checkpoint seal contains an invalid digest")
        path = output_dir / relative
        if not path.is_file() or sha256_file(path) != row["sha256"]:
            raise RuntimeError(f"sealed checkpoint bytes do not match: {relative}")
        indexed[key] = row
        order.append(key)
        expected_paths.add(relative)
    if seal["count"] != len(rows) or set(indexed) != expected_keys:
        raise RuntimeError("checkpoint seal does not cover the exact profile grid")
    if order != sorted(order):
        raise RuntimeError("checkpoint seal rows are not in canonical order")
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
    expected_preregistration_sha256: str,
    seal_row: Mapping[str, Any],
) -> torch.nn.Module:
    path = output_dir / "checkpoints" / f"{arm}_seed{seed}.pt"
    payload = torch.load(path, map_location=device, weights_only=True)
    expected_surface = {
        "schema",
        "version",
        "arm",
        "seed",
        "config",
        "model_class",
        "state_dict",
        "initial_state_digest",
        "final_state_digest",
        "training_metadata",
        "source_digest",
        "preregistration_sha256",
    }
    if not isinstance(payload, Mapping) or set(payload) != expected_surface:
        raise RuntimeError("checkpoint payload has an unexpected schema surface")
    if (
        payload.get("schema") != "komorebi.neuralese.invariant_kernel.checkpoint.v1"
        or payload.get("version") != VERSION
        or payload.get("arm") != arm
        or payload.get("seed") != seed
        or payload.get("source_digest") != expected_source_digest
        or payload.get("preregistration_sha256") != expected_preregistration_sha256
    ):
        raise RuntimeError("checkpoint payload identity mismatch")
    config = train_config(profile, seed, device)
    if not strict_json_equal(payload.get("config"), asdict(config)):
        raise RuntimeError("checkpoint training configuration mismatch")
    if not _json_safe_tree(payload):
        raise RuntimeError("checkpoint payload is not weights-only-safe")
    state = payload.get("state_dict")
    if not isinstance(state, Mapping) or not state or not all(
        isinstance(key, str) and isinstance(value, torch.Tensor)
        for key, value in state.items()
    ):
        raise RuntimeError("checkpoint state_dict has an unsafe surface")
    model = build_invariant_kernel_model(config, arm).to(device)
    if payload.get("model_class") != type(model).__name__:
        raise RuntimeError("checkpoint model class mismatch")
    if state_dict_digest(model) != payload.get("initial_state_digest"):
        raise RuntimeError("checkpoint initial-state digest mismatch")
    model.load_state_dict(state, strict=True)
    if state_dict_digest(model) != payload.get("final_state_digest"):
        raise RuntimeError("checkpoint tensor digest mismatch after reload")
    if (
        seal_row.get("path") != f"checkpoints/{arm}_seed{seed}.pt"
        or seal_row.get("state_digest") != payload.get("final_state_digest")
        or seal_row.get("sha256") != sha256_file(path)
    ):
        raise RuntimeError("checkpoint payload disagrees with its seal row")
    metadata = payload.get("training_metadata")
    if not isinstance(metadata, Mapping) or metadata.get("arm", {}).get("name") != arm:
        raise RuntimeError("checkpoint training metadata disagrees with arm")
    model.eval()
    return model


class _BehavioralGeometryView:
    """Compatibility view supplying an effective decoder to the v0.5 path assay."""

    def __init__(self, model: torch.nn.Module, decoder_weight: torch.Tensor) -> None:
        self.model = model
        self.decoder = SimpleNamespace(weight=decoder_weight)

    @property
    def training(self) -> bool:
        return bool(self.model.training)

    def to(self, device: torch.device | str) -> "_BehavioralGeometryView":
        self.model.to(device)
        self.decoder.weight = self.decoder.weight.to(device)
        return self

    def eval(self) -> "_BehavioralGeometryView":
        self.model.eval()
        return self

    def train(self, mode: bool = True) -> "_BehavioralGeometryView":
        self.model.train(mode)
        return self

    def __getattr__(self, name: str) -> Any:
        return getattr(self.model, name)


def _decoder_weight(model: torch.nn.Module) -> torch.Tensor:
    if isinstance(model, LearnedFrameBlockIsometricOperatorRNN):
        return model.effective_decoder_weight()
    decoder = getattr(model, "decoder", None)
    weight = getattr(decoder, "weight", None)
    if not isinstance(weight, torch.Tensor):
        raise TypeError("model does not expose an auditable decoder weight")
    return weight


def _centered_decoder(weight: torch.Tensor) -> torch.Tensor:
    weight64 = weight.detach().to(torch.float64)
    classes = weight64.shape[0]
    centering = torch.eye(classes, dtype=torch.float64) - torch.ones(
        classes, classes, dtype=torch.float64
    ) / float(classes)
    return centering @ weight64


def _word_product(codes: torch.Tensor, word: Sequence[int]) -> torch.Tensor:
    result = torch.eye(codes.shape[-1], dtype=codes.dtype, device=codes.device)
    for action in word:
        result = codes[int(action)] @ result
    return result


def _observer_stack(
    decoder_weight: torch.Tensor,
    codes: torch.Tensor,
    contexts: EpisodeBatch,
) -> torch.Tensor:
    observer = _centered_decoder(decoder_weight).to(codes.device)
    rows: list[torch.Tensor] = []
    for index in range(codes.shape[0]):
        bank = relation_cell_bank(contexts.maps[index])
        if len(bank.normal_forms) != 8:
            raise RuntimeError("registered observer requires eight BFS normal forms")
        for word in bank.normal_forms:
            rows.append(observer @ _word_product(codes[index], word))
    result = torch.cat(rows, dim=0)
    if not bool(torch.isfinite(result).all()) or result.shape[1] != 12:
        raise RuntimeError("future-observer stack is malformed or non-finite")
    return result


def _orthogonal_projector_from_observer(
    observer_stack: torch.Tensor,
    rank: int = 7,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    _, singular, right = torch.linalg.svd(observer_stack, full_matrices=False)
    if singular.numel() != 12 or not bool(torch.isfinite(singular).all()):
        raise RuntimeError("observer singular spectrum is incomplete")
    frame_rows = right[:rank]
    projector = frame_rows.T @ frame_rows
    return projector, frame_rows, singular


def _projector_frame(projector: torch.Tensor, rank: int) -> torch.Tensor:
    values, vectors = torch.linalg.eigh((projector + projector.T) / 2.0)
    order = torch.argsort(values, descending=True)
    return vectors[:, order[:rank]]


def _spectral_rows(value: torch.Tensor) -> list[float]:
    if not bool(torch.isfinite(value).all()):
        return [math.nan] * int(np.prod(value.shape[:-2]))
    return [
        float(item)
        for item in torch.linalg.matrix_norm(value, ord=2, dim=(-2, -1)).reshape(-1)
    ]


def _complete_summary(values: Iterable[float]) -> dict[str, Any]:
    result = numeric_summary(values)
    result["complete"] = result["count"] > 0 and result["finite_count"] == result["count"]
    return result


def _relation_geometry(
    codes: torch.Tensor,
    contexts: EpisodeBatch,
    p: torch.Tensor,
    q: torch.Tensor,
    ambient: torch.Tensor | None,
) -> dict[str, Any]:
    semantic: list[float] = []
    null: list[float] = []
    ambient_values: list[float] = []
    full: list[float] = []
    forward_cross: list[float] = []
    reverse_cross: list[float] = []
    ratios: list[float] = []
    for index in range(codes.shape[0]):
        for left_word, right_word in relation_cell_bank(contexts.maps[index]).cells:
            left = _word_product(codes[index], left_word)
            right = _word_product(codes[index], right_word)
            delta = left - right
            semantic_value = float(torch.linalg.matrix_norm(p @ delta @ p, ord="fro") / math.sqrt(7.0))
            null_value = float(torch.linalg.matrix_norm(q @ delta @ q, ord="fro") / math.sqrt(5.0))
            semantic.append(semantic_value)
            null.append(null_value)
            full.append(float(torch.linalg.matrix_norm(delta, ord="fro") / math.sqrt(12.0)))
            forward_cross.append(float(torch.linalg.matrix_norm(q @ delta @ p, ord=2)))
            reverse_cross.append(float(torch.linalg.matrix_norm(p @ delta @ q, ord=2)))
            if null_value > 1e-12:
                ratios.append(semantic_value / null_value)
            elif semantic_value <= 1e-12:
                ratios.append(0.0)
            else:
                ratios.append(math.inf)
            if ambient is not None:
                ambient_values.append(
                    float(torch.linalg.matrix_norm(ambient @ delta @ ambient, ord="fro") / 2.0)
                )
    return {
        "cases": len(semantic),
        "semantic_defect": _complete_summary(semantic),
        "null_curvature": _complete_summary(null),
        "ambient_curvature": (
            _complete_summary(ambient_values)
            if ambient is not None
            else {"status": "NOT_EVALUATED", "reason": "no registered L/K split"}
        ),
        "full_defect": _complete_summary(full),
        "behavioral_to_null_defect": _complete_summary(forward_cross),
        "null_to_behavioral_defect": _complete_summary(reverse_cross),
        "semantic_to_null_ratio": _complete_summary(ratios),
    }


def _registered_relation_word_groups(
    contexts: EpisodeBatch,
) -> dict[str, tuple[torch.Tensor, torch.Tensor]]:
    """Encode all nine BFS relation cells in fixed-length, batched groups.

    The path-audit API requires equal tensor lengths.  D4 cells differ only by
    powers of the episode's order-two generator, so appending that registered
    identity word preserves each path product while yielding length-three odd
    and length-four even banks.  No L/K interpretation is introduced here.
    """

    collected: dict[str, tuple[list[list[int]], list[list[int]]]] = {
        "odd_length3": ([], []),
        "even_length4": ([], []),
    }
    expected_cases: dict[str, int] = {}
    for context_map in contexts.maps:
        bank = relation_cell_bank(context_map)
        identity_candidates = [
            left
            for left, right in bank.cells
            if len(left) == 2 and len(right) == 0
        ]
        if len(identity_candidates) != 1:
            raise RuntimeError("relation bank does not identify one order-two word")
        identity_word = identity_candidates[0]
        per_context: dict[str, tuple[list[list[int]], list[list[int]]]] = {
            "odd_length3": ([], []),
            "even_length4": ([], []),
        }
        for left, right in bank.cells:
            label = "even_length4" if len(left) % 2 == 0 else "odd_length3"
            target_length = 4 if label == "even_length4" else 3

            def padded(word: Sequence[int]) -> list[int]:
                deficit = target_length - len(word)
                if deficit < 0 or deficit % 2:
                    raise RuntimeError("relation path cannot be identity padded")
                return list(word) + list(identity_word) * (deficit // 2)

            per_context[label][0].append(padded(left))
            per_context[label][1].append(padded(right))
        for label, (left_rows, right_rows) in per_context.items():
            if not left_rows or len(left_rows) != len(right_rows):
                raise RuntimeError("relation path group is empty or misaligned")
            if label in expected_cases and expected_cases[label] != len(left_rows):
                raise RuntimeError("relation path group cardinality changed by context")
            expected_cases[label] = len(left_rows)
            collected[label][0].append(left_rows)
            collected[label][1].append(right_rows)
    return {
        label: (
            torch.tensor(left, dtype=torch.long),
            torch.tensor(right, dtype=torch.long),
        )
        for label, (left, right) in collected.items()
    }


def _two_way_gauge_covariance(
    p: torch.Tensor,
    decoder: torch.Tensor,
    codes: torch.Tensor,
    suffix_words: Mapping[int, torch.Tensor],
    *,
    seed: int,
) -> dict[str, Any]:
    generator = torch.Generator(device="cpu").manual_seed(seed)
    raw = torch.randn(12, 12, generator=generator, dtype=torch.float64)
    gauge, triangular = torch.linalg.qr(raw)
    signs = torch.where(
        torch.sign(torch.diagonal(triangular)) == 0,
        torch.ones(12, dtype=torch.float64),
        torch.sign(torch.diagonal(triangular)),
    )
    gauge = gauge @ torch.diag(signs)
    if float(torch.linalg.det(gauge)) < 0.0:
        gauge[:, -1].neg_()
    q = torch.eye(12, dtype=torch.float64) - p
    transformed_p = gauge @ p @ gauge.T
    transformed_q = gauge @ q @ gauge.T
    transformed_d = decoder @ gauge.T
    transformed_codes = gauge @ codes @ gauge.T
    observer = _centered_decoder(decoder)
    observer_g = _centered_decoder(transformed_d)
    deltas: list[float] = []
    leakage_deltas: list[float] = []
    for length in sorted(suffix_words):
        products = path_products(codes, suffix_words[length])
        products_g = path_products(transformed_codes, suffix_words[length])
        deltas.append(float(torch.linalg.matrix_norm(observer_g @ products_g @ gauge - observer @ products, ord=2).max()))
        original = torch.linalg.matrix_norm(p @ products @ q, ord=2, dim=(-2, -1))
        changed = torch.linalg.matrix_norm(
            transformed_p @ products_g @ transformed_q, ord=2, dim=(-2, -1)
        )
        leakage_deltas.append(float((original - changed).abs().max()))
    values = {
        "gauge_orthogonality_residual": float(torch.linalg.matrix_norm(gauge.T @ gauge - torch.eye(12, dtype=torch.float64), ord=2)),
        "projector_transport_residual": float(torch.linalg.matrix_norm(transformed_p - gauge @ p @ gauge.T, ord=2)),
        "centered_continuation_delta": max(deltas),
        "leakage_scalar_delta": max(leakage_deltas),
    }
    values["all_finite"] = all(math.isfinite(value) for value in values.values())
    values["passed"] = values["all_finite"] and all(
        value <= 5e-5 for key, value in values.items() if key not in {"all_finite", "passed"}
    )
    return values


def evaluate_geometry(
    model: torch.nn.Module,
    geometry_batch: EpisodeBatch,
    suffix_words: Mapping[int, torch.Tensor],
    *,
    seed: int,
) -> tuple[dict[str, Any], torch.Tensor]:
    model.eval()
    with torch.inference_mode():
        executed = model.encode_operators(geometry_batch.tables).detach()
        decoder_native = _decoder_weight(model).detach()
    if executed.dtype != torch.float32 or decoder_native.dtype != torch.float32:
        raise RuntimeError("native v0.6 execution must remain float32")
    extracted = extract_model_geometry(
        model,
        geometry_batch.tables,
        suffix_words,
        required_lengths=ALGEBRAIC_SUFFIX_LENGTHS,
        expected_behavioral_rank=7,
        rank_tolerance=1e-6,
        sigma_behavioral_floor=1e-3,
        sigma_first_null_ceiling=1e-3,
    )
    codes = extracted.operator_codes
    decoder = extracted.decoder_weight
    p = extracted.behavioral_projector
    q = extracted.centered_null_projector
    line = extracted.common_projector
    ambient = extracted.ambient_projector
    three_way = extracted.three_way_registered
    source = extracted.source
    observer_rows = []
    centered_for_observer = _centered_decoder(decoder)
    for length in sorted(suffix_words):
        products = path_products(codes, suffix_words[length])
        observer_rows.append((centered_for_observer @ products).reshape(-1, 12))
    observer_stack = torch.cat(observer_rows, dim=0)
    observed_projector, _, singular = _orthogonal_projector_from_observer(observer_stack)
    p_frame = _projector_frame(p, 7)
    pi = p_frame.T
    centered = _centered_decoder(decoder)
    identity = torch.eye(12, dtype=torch.float64)
    relative = singular / singular[0]
    rank = int((relative > 1e-6).sum())
    rank_ambiguous = bool(((relative >= 1e-7) & (relative <= 1e-5)).any())
    generator_leakage = []
    intertwining = []
    orthogonality = []
    for matrix in codes.reshape(-1, 12, 12):
        generator_leakage.append(
            max(
                float(torch.linalg.matrix_norm(p @ matrix @ q, ord=2)),
                float(torch.linalg.matrix_norm(q @ matrix @ p, ord=2)),
            )
        )
        descended = pi @ matrix @ pi.T
        intertwining.append(
            float(torch.linalg.matrix_norm(pi @ matrix - descended @ pi, ord="fro") / math.sqrt(7.0))
        )
        orthogonality.append(float(torch.linalg.matrix_norm(matrix.T @ matrix - identity, ord="fro")))

    suffix_levels: dict[str, Any] = {}
    all_suffix_leakage: list[float] = []
    for length in sorted(suffix_words):
        products = path_products(codes, suffix_words[length])
        values = [
            max(left, right)
            for left, right in zip(
                _spectral_rows(p @ products @ q),
                _spectral_rows(q @ products @ p),
                strict=True,
            )
        ]
        suffix_levels[str(length)] = _complete_summary(values)
        all_suffix_leakage.extend(values)
    decoder_norm = max(float(torch.linalg.matrix_norm(centered, ord=2)), 1e-8)
    structure = {
        "projector_source": source,
        "three_way_registered": three_way,
        "projector_symmetry_residual": float(torch.linalg.matrix_norm(p - p.T, ord="fro")),
        "projector_idempotence_residual": float(torch.linalg.matrix_norm(p @ p - p, ord="fro")),
        "projector_trace_error": abs(float(torch.trace(p)) - 7.0),
        "centered_readout_leakage": float(torch.linalg.matrix_norm(centered @ q, ord=2) / decoder_norm),
        "centered_readout_completeness": float(torch.linalg.matrix_norm(centered - centered @ p, ord=2) / decoder_norm),
        "operator_orthogonality": _complete_summary(orthogonality),
        "generator_leakage": _complete_summary(generator_leakage),
        "intertwining_residual": _complete_summary(intertwining),
    }
    two_way_structure = audit_centered_quotient_structure(
        p,
        q,
        decoder,
        codes,
        tolerance=5e-5,
        rank_tolerance=1e-6,
    )
    two_way_suffix = audit_centered_quotient_suffixes(
        p,
        q,
        decoder,
        codes,
        suffix_words,
        required_lengths=ALGEBRAIC_SUFFIX_LENGTHS,
        tolerance=0.20,
        rank_tolerance=1e-6,
        sigma_behavioral_floor=1e-3,
        sigma_first_null_ceiling=1e-3,
    )
    two_way_null = centered_null_intervention_audit(
        p,
        q,
        decoder,
        codes,
        suffix_words,
        required_lengths=ALGEBRAIC_SUFFIX_LENGTHS,
        tolerance=0.02,
        rank_tolerance=1e-6,
    )
    relation_word_groups = _registered_relation_word_groups(geometry_batch)
    two_way_paths = {
        label: audit_centered_quotient_paths(
            p,
            q,
            codes,
            left_words,
            right_words,
            tolerance=0.10,
        ).to_dict()
        for label, (left_words, right_words) in relation_word_groups.items()
    }
    observer = {
        "singular_values": [float(value) for value in singular],
        "relative_singular_values": [float(value) for value in relative],
        "rank_at_fixed_1e-6": rank,
        "rank_ambiguous": rank_ambiguous,
        "sigma7_over_sigma1": float(relative[6]),
        "sigma8_over_sigma1": float(relative[7]),
        "principal_angle_projector_distance": float(
            torch.linalg.matrix_norm(p - observed_projector, ord=2)
        ),
    }
    relation = _relation_geometry(codes, geometry_batch, p, q, ambient)
    typed: dict[str, Any]
    if three_way:
        assert line is not None and ambient is not None
        typed_structure = audit_kernel_structure(p, line, ambient, decoder, codes)
        typed_suffix = suffix_leakage_audit(
            p,
            line,
            ambient,
            decoder,
            codes,
            suffix_words,
            required_lengths=ALGEBRAIC_SUFFIX_LENGTHS,
            tolerance=5e-5,
            rank_tolerance=1e-6,
            sigma_behavioral_floor=1e-3,
            sigma_first_null_ceiling=5e-5,
        )
        typed_fiber = fiber_intervention_audit(
            p,
            line,
            ambient,
            decoder,
            codes,
            suffix_words,
            required_lengths=ALGEBRAIC_SUFFIX_LENGTHS,
            tolerance=5e-5,
            rank_tolerance=1e-6,
        )
        typed_paths = {
            label: path_defect_audit(
                p,
                line,
                ambient,
                codes,
                left_words,
                right_words,
                tolerance=0.10,
                curvature_detection_floor=0.10,
            ).to_dict()
            for label, (left_words, right_words) in relation_word_groups.items()
        }
        first_cells = relation_cell_bank(geometry_batch.maps[0]).cells[0]
        left_words = torch.tensor([first_cells[0]], dtype=torch.long)
        right_words = torch.tensor([first_cells[1]], dtype=torch.long)
        generator = torch.Generator(device="cpu").manual_seed(
            derive_seed(seed, "registered-coordinate-gauge")
        )
        raw = torch.randn(12, 12, generator=generator, dtype=torch.float64)
        gauge, _ = torch.linalg.qr(raw)
        typed_gauge = gauge_covariance_audit(
            p,
            line,
            ambient,
            decoder,
            codes[:1],
            suffix_words,
            left_words,
            right_words,
            gauge,
            required_lengths=ALGEBRAIC_SUFFIX_LENGTHS,
            tolerance=5e-5,
        )
        typed = {
            "status": "EVALUATED",
            "structure": typed_structure.to_dict(),
            "suffix": typed_suffix.to_dict(),
            "paths": typed_paths,
            "fiber_intervention": typed_fiber.to_dict(),
            "gauge_covariance": typed_gauge.to_dict(),
        }
    else:
        typed = {
            "status": "NOT_EVALUATED",
            "reason": "the model has no scientifically registered L1/K4 split",
        }
    result = {
        "schema": "komorebi.neuralese.invariant_kernel.geometry.v1",
        "native_tensor_dtype": "float32",
        "geometry_dtype": "float64_from_executed_float32",
        "contexts": int(codes.shape[0]),
        "observer": observer,
        "extraction": extracted.receipt(),
        "structure": structure,
        "two_way_audits": {
            "structure": two_way_structure.to_dict(),
            "suffix": two_way_suffix.to_dict(),
            "paths": two_way_paths,
            "null_intervention": two_way_null.to_dict(),
        },
        "suffix_leakage": {
            "levels": suffix_levels,
            "all": _complete_summary(all_suffix_leakage),
            "length64": suffix_levels["64"],
        },
        "relations": relation,
        "typed_three_way": typed,
        "gauge_covariance": _two_way_gauge_covariance(
            p,
            decoder,
            codes,
            suffix_words,
            seed=derive_seed(seed, "two-way-gauge"),
        ),
    }
    return result, p


def _visible_product(codes: torch.Tensor, slots: torch.Tensor) -> torch.Tensor:
    batch, _, dimension, _ = codes.shape
    result = torch.eye(dimension, dtype=codes.dtype, device=codes.device).expand(
        batch, -1, -1
    ).clone()
    rows = torch.arange(batch, device=codes.device)
    for step_slots in slots.unbind(dim=1):
        result = codes[rows, step_slots] @ result
    return result


def _native_margin(logits: torch.Tensor) -> torch.Tensor:
    predictions = logits.argmax(dim=1)
    rows = torch.arange(logits.shape[0], device=logits.device)
    chosen = logits[rows, predictions]
    alternatives = logits.clone()
    alternatives[rows, predictions] = -torch.inf
    return chosen - alternatives.max(dim=1).values


def evaluate_null_perturbations(
    model: torch.nn.Module,
    p: torch.Tensor,
    null_batches: Mapping[int, EpisodeBatch],
    *,
    seed: int,
) -> dict[str, Any]:
    q64 = torch.eye(12, dtype=torch.float64) - p
    decoder64 = _centered_decoder(_decoder_weight(model))
    generator = torch.Generator(device="cpu").manual_seed(
        derive_seed(seed, "null-random-directions")
    )
    rows_out: list[dict[str, Any]] = []
    total = retained = target_correct = native_target_correct = boundary = 0
    relative_effects: list[float] = []
    for length in INTERVENTION_SUFFIX_LENGTHS:
        batch = null_batches[int(length)]
        model.eval()
        with torch.inference_mode():
            codes_native = model.encode_operators(batch.tables)
            start_hidden = model.initial_hidden(batch.start)
            product_native = _visible_product(codes_native, batch.op_slots)
            final_native = torch.bmm(product_native, start_hidden.unsqueeze(-1)).squeeze(-1)
            logits_native = model.decode_hidden(final_native)
        if not bool(torch.isfinite(logits_native).all()):
            raise RuntimeError("null-perturbation native logits are non-finite")
        native_prediction = logits_native.argmax(dim=1)
        native_correct = native_prediction == batch.target
        native_robust = _native_margin(logits_native) > NATIVE_MARGIN_TAU
        product64 = product_native.to(torch.float64)
        response = decoder64 @ product64 @ q64
        _, _, right = torch.linalg.svd(response, full_matrices=False)
        worst = right[:, 0, :]
        worst = worst @ q64
        worst = worst / torch.linalg.vector_norm(worst, dim=1, keepdim=True).clamp_min(1e-12)
        random = torch.randn(
            start_hidden.shape[0],
            12,
            generator=generator,
            dtype=torch.float64,
        ) @ q64
        random = random / torch.linalg.vector_norm(random, dim=1, keepdim=True).clamp_min(1e-12)
        for direction_name, direction64 in (("seeded_random_null", random), ("worst_measured_null", worst)):
            direction = direction64.to(start_hidden.dtype)
            membership = torch.linalg.vector_norm(direction64 @ p, dim=1)
            probe_norm = torch.linalg.vector_norm(direction64, dim=1)
            if float(probe_norm.min()) <= 0.99 or float(membership.max()) > 5e-5:
                raise RuntimeError("null perturbation failed nonzero membership audit")
            for magnitude in INTERVENTION_MAGNITUDES:
                scale = (
                    float(magnitude)
                    * torch.linalg.vector_norm(start_hidden, dim=1, keepdim=True)
                )
                perturbed = start_hidden + scale * direction
                with torch.inference_mode():
                    final = torch.bmm(product_native, perturbed.unsqueeze(-1)).squeeze(-1)
                    logits = model.decode_hidden(final)
                defined = torch.isfinite(logits).all(dim=1)
                prediction = logits.argmax(dim=1)
                condition_total = int(batch.start.shape[0])
                condition_retained = int((defined & (prediction == native_prediction)).sum())
                condition_target = int((defined & (prediction == batch.target)).sum())
                centered_native = logits_native - logits_native.mean(dim=1, keepdim=True)
                centered_delta = (logits - logits_native) - (logits - logits_native).mean(
                    dim=1, keepdim=True
                )
                effect = torch.linalg.vector_norm(centered_delta.to(torch.float64), dim=1) / torch.linalg.vector_norm(
                    centered_native.to(torch.float64), dim=1
                ).clamp_min(1e-8)
                effects = [float(value) for value in effect]
                relative_effects.extend(effects)
                total += condition_total
                retained += condition_retained
                target_correct += condition_target
                native_target_correct += int(native_correct.sum())
                boundary += int((~native_robust).sum())
                rows_out.append(
                    {
                        "suffix_length": int(length),
                        "direction": direction_name,
                        "relative_magnitude": float(magnitude),
                        "total": condition_total,
                        "defined": int(defined.sum()),
                        "prediction_retained": condition_retained,
                        "prediction_retention": condition_retained / condition_total,
                        "original_target_correct": condition_target,
                        "original_target_accuracy": condition_target / condition_total,
                        "native_target_correct": int(native_correct.sum()),
                        "native_target_accuracy": float(native_correct.float().mean()),
                        "native_boundary": int((~native_robust).sum()),
                        "minimum_probe_norm": float(probe_norm.min()),
                        "maximum_behavioral_membership": float(membership.max()),
                        "relative_centered_logit_effect": _complete_summary(effects),
                    }
                )
    return {
        "schema": "komorebi.neuralese.invariant_kernel.null_perturbation.v1",
        "conditions": rows_out,
        "total": total,
        "prediction_retained": retained,
        "prediction_retention": retained / total,
        "original_target_correct": target_correct,
        "original_target_accuracy": target_correct / total,
        "native_target_correct": native_target_correct,
        "native_target_accuracy": native_target_correct / total,
        "native_boundary": boundary,
        "native_boundary_rate": boundary / total,
        "relative_centered_logit_effect": _complete_summary(relative_effects),
        "all_conditions_complete": all(row["defined"] == row["total"] for row in rows_out),
        "memory_claim_eligible": False,
        "evidence_scope": "synthetic_nonzero_null_invariance_not_learned_memory",
    }


def evaluate_behavior(
    model: torch.nn.Module,
    decoder_weight: torch.Tensor,
    audit_bank: FlatnessAuditBank,
    bank: Mapping[str, Any],
    profile: Mapping[str, Any],
    *,
    seed: int,
    device: str,
) -> dict[str, Any]:
    view = _BehavioralGeometryView(model, decoder_weight)
    diamonds = evaluate_path_cases(
        view,
        audit_bank.diamonds,
        seed=derive_seed(seed, "v0.6", "diamonds"),
        equivalent=True,
        device=device,
    )
    inequivalent = evaluate_path_cases(
        view,
        audit_bank.inequivalent,
        seed=derive_seed(seed, "v0.6", "inequivalent"),
        equivalent=False,
        device=device,
    )
    loops = evaluate_loop_cases(
        model,
        audit_bank.loops,
        seed=derive_seed(seed, "v0.6", "loops"),
        device=device,
    )
    deep: dict[str, Any] = {}
    for family in ("d4", "c8", "mixed_cycle"):
        depths = profile["deep_depths"] if family == "d4" else (128,)
        deep[family] = {
            str(depth): evaluate_deep_accuracy(
                model,
                seed=derive_seed(seed, "v0.6", "deep", family, int(depth)),
                depth=int(depth),
                examples=int(profile["deep_examples"]),
                family=family,
                device=device,
            )
            for depth in depths
        }
    causal = intervention_metrics(
        model,
        int(profile["causal_examples"]),
        min(128, int(profile["causal_examples"])),
        derive_seed(seed, "v0.6", "causal-main"),
        torch.device(device),
        length=64,
        split=32,
        operator_step=3,
        episode_batch=bank["causal_main"],
        operator_control_batch=bank["causal_control"],
        control_seed=derive_seed(seed, "v0.6", "causal-controls"),
    )
    return {
        "diamonds": diamonds,
        "inequivalent": inequivalent,
        "loops": loops,
        "deep": deep,
        "causal_interventions": causal,
        "hard_isometry": hard_orthogonality_residual(
            model,
            seed=derive_seed(seed, "v0.6", "hard-isometry"),
            contexts=min(32, int(profile["geometry_contexts"])),
        ),
    }


def evaluate_panel(
    output_dir: Path,
    audit_bank: FlatnessAuditBank,
    banks: Mapping[int, Mapping[str, Any]],
    profile: Mapping[str, Any],
    *,
    device: str,
    source_sha256: str,
    preregistration_sha256: str,
    checkpoint_seal: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    seal_rows = validate_checkpoint_seal(
        output_dir,
        checkpoint_seal,
        profile,
        expected_source_digest=source_sha256,
        expected_preregistration_sha256=preregistration_sha256,
    )
    record_dir = output_dir / RECORD_DIR_NAME
    record_dir.mkdir()
    records: dict[str, Any] = {}
    index: list[dict[str, Any]] = []
    for raw_seed in profile["seeds"]:
        seed = int(raw_seed)
        records[str(seed)] = {}
        for arm in PRIMARY_INVARIANT_KERNEL_ARMS:
            model = load_sealed_model(
                output_dir,
                arm,
                seed,
                profile,
                device=device,
                expected_source_digest=source_sha256,
                expected_preregistration_sha256=preregistration_sha256,
                seal_row=seal_rows[(seed, arm)],
            )
            geometry, projector = evaluate_geometry(
                model,
                banks[seed]["geometry"],
                banks[seed]["suffix_words"],
                seed=derive_seed(seed, arm, "geometry"),
            )
            behavior = evaluate_behavior(
                model,
                _decoder_weight(model).detach(),
                audit_bank,
                banks[seed],
                profile,
                seed=seed,
                device=device,
            )
            null_perturbation = evaluate_null_perturbations(
                model,
                projector,
                banks[seed]["null_batches"],
                seed=derive_seed(seed, arm, "null-perturbation"),
            )
            record = {
                "schema": "komorebi.neuralese.invariant_kernel.arm_record.v1",
                "version": VERSION,
                "seed": seed,
                "arm": arm,
                "source_digest": source_sha256,
                "preregistration_sha256": preregistration_sha256,
                "checkpoint_sha256": seal_rows[(seed, arm)]["sha256"],
                "checkpoint_state_digest": seal_rows[(seed, arm)]["state_digest"],
                "behavior": behavior,
                "geometry": geometry,
                "null_perturbation": null_perturbation,
            }
            path = record_dir / f"{arm}_seed{seed}.json"
            write_json(path, record)
            row = {
                "path": path.relative_to(output_dir).as_posix(),
                "sha256": sha256_file(path),
                "arm": arm,
                "seed": seed,
            }
            records[str(seed)][arm] = record
            index.append(row)
            del model
    index.sort(key=lambda row: (row["seed"], row["arm"]))
    expected_paths = {
        f"{RECORD_DIR_NAME}/{arm}_seed{seed}.json"
        for seed in profile["seeds"]
        for arm in PRIMARY_INVARIANT_KERNEL_ARMS
    }
    actual_paths = {
        path.relative_to(output_dir).as_posix()
        for path in record_dir.glob("*.json")
        if path.is_file()
    }
    if actual_paths != expected_paths:
        raise RuntimeError("per-arm record directory does not match the exact grid")
    return records, index


def _rate_summary(
    rows: Sequence[Mapping[str, Any]],
    numerator: str,
    denominator: str,
) -> dict[str, Any]:
    numerators = [int(row[numerator]) for row in rows]
    denominators = [int(row[denominator]) for row in rows]
    if not denominators or any(total <= 0 for total in denominators):
        return {
            "numerator": sum(numerators),
            "denominator": sum(denominators),
            "pooled": None,
            "mean_seed": None,
            "worst_seed": None,
            "per_seed": [],
        }
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


def _causal_scalar(row: Mapping[str, Any], key: str) -> float | None:
    value = row.get(key)
    return float(value) if isinstance(value, (int, float)) and math.isfinite(float(value)) else None


def aggregate_records(
    records: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    seed_keys = [str(int(seed)) for seed in profile["seeds"]]
    aggregate: dict[str, Any] = {}
    for arm in PRIMARY_INVARIANT_KERNEL_ARMS:
        arm_rows = [records[seed][arm] for seed in seed_keys]
        behavior_rows = [row["behavior"] for row in arm_rows]
        geometry_rows = [row["geometry"] for row in arm_rows]
        null_rows = [row["null_perturbation"] for row in arm_rows]
        deep: dict[str, Any] = {}
        for depth in profile["deep_depths"]:
            rows = [row["deep"]["d4"][str(depth)] for row in behavior_rows]
            deep[str(depth)] = {
                "ordinary": _rate_summary(rows, "ordinary_correct", "total"),
                "robust": _rate_summary(rows, "robust_correct", "total"),
                "boundary": _rate_summary(rows, "boundary", "total"),
            }
        diamonds = [row["diamonds"] for row in behavior_rows]
        inequivalent = [row["inequivalent"] for row in behavior_rows]
        loops = [row["loops"] for row in behavior_rows]
        causal = [row["causal_interventions"] for row in behavior_rows]
        aggregate[arm] = {
            "deep_d4": deep,
            "diamonds": {
                "joint": _rate_summary(diamonds, "joint_correct", "total"),
                "joint_robust": _rate_summary(diamonds, "joint_robust", "total"),
                "agreement": _rate_summary(diamonds, "prediction_agreement", "total"),
                "boundary": _rate_summary(diamonds, "boundary", "decision_total"),
            },
            "inequivalent": {
                "sensitivity": _rate_summary(inequivalent, "joint_correct", "total"),
                "agreement": _rate_summary(inequivalent, "prediction_agreement", "total"),
            },
            "loops": {
                "joint": _rate_summary(loops, "joint_correct", "total"),
                "joint_robust": _rate_summary(loops, "joint_robust", "total"),
                "agreement": _rate_summary(loops, "agreement", "total"),
                "boundary": _rate_summary(loops, "boundary", "decision_total"),
                "degradation": _value_summary([row["accuracy_degradation"] for row in loops]),
            },
            "zero_shot_128": {
                family: _rate_summary(
                    [row["deep"][family]["128"] for row in behavior_rows],
                    "robust_correct",
                    "total",
                )
                for family in ("c8", "mixed_cycle")
            },
            "geometry": {
                "extraction_valid_fraction": sum(
                    bool(row["extraction"]["extraction_valid"]) for row in geometry_rows
                ) / len(geometry_rows),
                "rank_ambiguous_count": sum(
                    bool(row["observer"]["rank_ambiguous"]) for row in geometry_rows
                ),
                "sigma7_over_sigma1": _value_summary(
                    [row["observer"]["sigma7_over_sigma1"] for row in geometry_rows]
                ),
                "sigma8_over_sigma1": _value_summary(
                    [row["observer"]["sigma8_over_sigma1"] for row in geometry_rows]
                ),
                "principal_angle": _value_summary(
                    [row["observer"]["principal_angle_projector_distance"] for row in geometry_rows]
                ),
                "projector_residual": _value_summary(
                    [
                        max(
                            row["structure"]["projector_symmetry_residual"],
                            row["structure"]["projector_idempotence_residual"],
                            row["structure"]["projector_trace_error"],
                        )
                        for row in geometry_rows
                    ]
                ),
                "centered_readout_leakage": _value_summary(
                    [row["structure"]["centered_readout_leakage"] for row in geometry_rows]
                ),
                "generator_leakage_seed_p95": _value_summary(
                    [row["structure"]["generator_leakage"]["p95"] for row in geometry_rows]
                ),
                "generator_leakage_seed_max": _value_summary(
                    [row["structure"]["generator_leakage"]["maximum"] for row in geometry_rows]
                ),
                "length64_leakage_seed_p95": _value_summary(
                    [row["suffix_leakage"]["length64"]["p95"] for row in geometry_rows]
                ),
                "length64_leakage_seed_max": _value_summary(
                    [row["suffix_leakage"]["length64"]["maximum"] for row in geometry_rows]
                ),
                "intertwining_seed_median": _value_summary(
                    [row["structure"]["intertwining_residual"]["median"] for row in geometry_rows]
                ),
                "intertwining_seed_p95": _value_summary(
                    [row["structure"]["intertwining_residual"]["p95"] for row in geometry_rows]
                ),
                "intertwining_seed_max": _value_summary(
                    [row["structure"]["intertwining_residual"]["maximum"] for row in geometry_rows]
                ),
                "semantic_defect_seed_median": _value_summary(
                    [row["relations"]["semantic_defect"]["median"] for row in geometry_rows]
                ),
                "semantic_defect_seed_p95": _value_summary(
                    [row["relations"]["semantic_defect"]["p95"] for row in geometry_rows]
                ),
                "null_curvature_seed_median": _value_summary(
                    [row["relations"]["null_curvature"]["median"] for row in geometry_rows]
                ),
                "semantic_null_ratio_seed_median": _value_summary(
                    [row["relations"]["semantic_to_null_ratio"]["median"] for row in geometry_rows]
                ),
                "ambient_curvature_seed_median": _value_summary(
                    [
                        row["relations"]["ambient_curvature"].get("median")
                        for row in geometry_rows
                    ]
                ),
                "gauge_pass_fraction": sum(
                    bool(row["gauge_covariance"]["passed"]) for row in geometry_rows
                ) / len(geometry_rows),
            },
            "null_perturbation": {
                "prediction_retention": _rate_summary(
                    null_rows, "prediction_retained", "total"
                ),
                "original_target_accuracy": _rate_summary(
                    null_rows, "original_target_correct", "total"
                ),
                "native_target_accuracy": _rate_summary(
                    null_rows, "native_target_correct", "total"
                ),
                "relative_effect_seed_p95": _value_summary(
                    [row["relative_centered_logit_effect"]["p95"] for row in null_rows]
                ),
                "complete_fraction": sum(bool(row["all_conditions_complete"]) for row in null_rows)
                / len(null_rows),
            },
            "causal": {
                key: _value_summary([_causal_scalar(row, key) for row in causal])
                for key in (
                    "native_original_accuracy",
                    "state_patch_transition_accuracy",
                    "angle_matched_state_control_transition_accuracy",
                    "reachable_state_control_transition_accuracy",
                    "random_state_patch_transition_accuracy",
                    "operator_patch_transition_accuracy",
                    "random_operator_patch_transition_accuracy",
                    "cross_context_operator_control_transition_accuracy",
                    "state_counterfactual_target_distinct_fraction",
                    "operator_counterfactual_target_distinct_fraction",
                )
            },
            "causal_coverage": {
                "state": _value_summary(
                    [row["state_transition_eligible_examples"] / row["examples"] for row in causal]
                ),
                "operator": _value_summary(
                    [row["operator_transition_eligible_examples"] / row["examples"] for row in causal]
                ),
            },
            "maximum_orthogonality_residual": max(
                row["hard_isometry"]["orthogonality_residual"]["maximum"]
                for row in behavior_rows
            ),
        }
    return aggregate


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _complete_numeric(value: Any) -> bool:
    return (
        isinstance(value, Mapping)
        and type(value.get("count")) is int
        and value["count"] > 0
        and value.get("finite_count") == value["count"]
        and all(_finite_number(value.get(name)) for name in ("minimum", "median", "p95", "maximum", "mean"))
    )


def validate_execution_integrity(
    records: Mapping[str, Any],
    record_index: Sequence[Mapping[str, Any]],
    training: Mapping[str, Any],
    controls: Mapping[str, Any],
    profile: Mapping[str, Any],
    *,
    output_dir: Path,
    source_sha256: str,
    preregistration_sha256: str,
    checkpoint_seal: Mapping[str, Any],
    eval_receipt: Mapping[str, Any],
) -> dict[str, Any]:
    seeds = [str(int(seed)) for seed in profile["seeds"]]
    expected_keys = {
        (int(seed), arm)
        for seed in profile["seeds"]
        for arm in PRIMARY_INVARIANT_KERNEL_ARMS
    }
    checks: dict[str, bool] = {}
    checks["record_grid"] = (
        set(records) == set(seeds)
        and all(set(records[seed]) == set(PRIMARY_INVARIANT_KERNEL_ARMS) for seed in seeds)
        and {(int(row.get("seed", -1)), row.get("arm")) for row in record_index} == expected_keys
        and len(record_index) == len(expected_keys)
    )
    record_hashes_valid = True
    for row in record_index:
        path = output_dir / str(row.get("path", ""))
        if (
            set(row) != {"path", "sha256", "arm", "seed"}
            or not path.is_file()
            or not _hex_digest(row.get("sha256"))
            or sha256_file(path) != row.get("sha256")
        ):
            record_hashes_valid = False
    checks["record_hashes"] = record_hashes_valid
    checks["record_identity"] = all(
        row.get("schema") == "komorebi.neuralese.invariant_kernel.arm_record.v1"
        and row.get("version") == VERSION
        and row.get("seed") == int(seed)
        and row.get("arm") == arm
        and row.get("source_digest") == source_sha256
        and row.get("preregistration_sha256") == preregistration_sha256
        for seed in seeds
        for arm, row in records[seed].items()
    ) if checks["record_grid"] else False
    checks["training_grid"] = (
        set(training) == set(seeds)
        and all(set(training[seed]) == set(PRIMARY_INVARIANT_KERNEL_ARMS) for seed in seeds)
    )
    paired_fields = (
        "episode_stream_digest",
        "terminal_proposal_stream_digest",
        "relation_schedule_digest",
        "terminal_firewall_policy_digest",
        "terminal_proposal_count",
        "terminal_candidates_accepted",
        "terminal_candidates_rejected",
        "terminal_identity_rejections",
        "terminal_r2_rejections",
        "construction_digest",
    )
    checks["paired_training_streams"] = checks["training_grid"] and all(
        all(len({training[seed][arm][field] for arm in PRIMARY_INVARIANT_KERNEL_ARMS}) == 1 for field in paired_fields)
        for seed in seeds
    )
    checks["frozen_hard_ambient"] = checks["training_grid"] and all(
        training[seed][arm]["ambient_initial_digest"] is not None
        and training[seed][arm]["ambient_initial_digest"] == training[seed][arm]["ambient_final_digest"]
        for seed in seeds
        for arm in ("hard_kernel_supervised", "hard_kernel_semantic_flat")
    )
    checks["behavioral_decisions_complete"] = checks["record_grid"] and all(
        all(
            row["behavior"]["deep"]["d4"][str(depth)]["total"] == int(profile["deep_examples"])
            and row["behavior"]["deep"]["d4"][str(depth)]["ordinary_correct"]
            <= row["behavior"]["deep"]["d4"][str(depth)]["total"]
            and _hex_digest(row["behavior"]["deep"]["d4"][str(depth)]["logits_sha256"])
            for depth in profile["deep_depths"]
        )
        for seed in seeds
        for row in records[seed].values()
    )
    checks["geometry_complete"] = checks["record_grid"] and all(
        row["geometry"]["native_tensor_dtype"] == "float32"
        and row["geometry"]["geometry_dtype"] == "float64_from_executed_float32"
        and row["geometry"]["contexts"] == int(profile["geometry_contexts"])
        and _complete_numeric(row["geometry"]["structure"]["generator_leakage"])
        and _complete_numeric(row["geometry"]["structure"]["intertwining_residual"])
        and _complete_numeric(row["geometry"]["relations"]["semantic_defect"])
        and _complete_numeric(row["geometry"]["relations"]["null_curvature"])
        and _complete_numeric(row["geometry"]["suffix_leakage"]["length64"])
        and all(
            path.get("all_finite") is True
            for path in row["geometry"]["two_way_audits"]["paths"].values()
        )
        and (
            row["geometry"]["typed_three_way"]["status"] != "EVALUATED"
            or all(
                path.get("all_finite") is True
                for path in row["geometry"]["typed_three_way"]["paths"].values()
            )
        )
        for seed in seeds
        for row in records[seed].values()
    )
    checks["null_interventions_complete"] = checks["record_grid"] and all(
        row["null_perturbation"]["all_conditions_complete"]
        and row["null_perturbation"]["total"]
        == int(profile["causal_examples"])
        * len(INTERVENTION_SUFFIX_LENGTHS)
        * 2
        * len(INTERVENTION_MAGNITUDES)
        and _complete_numeric(row["null_perturbation"]["relative_centered_logit_effect"])
        for seed in seeds
        for row in records[seed].values()
    )
    checks["checkpoint_seal_complete"] = (
        checkpoint_seal.get("count") == len(expected_keys)
        and _hex_digest(checkpoint_seal.get("seal_sha256"))
    )
    checks["evaluation_bank_bound"] = (
        eval_receipt.get("source_digest") == source_sha256
        and eval_receipt.get("preregistration_sha256") == preregistration_sha256
        and _hex_digest(eval_receipt.get("fingerprint"))
    )
    checks["coordinate_covariance_complete"] = checks["record_grid"] and all(
        bool(row["geometry"]["gauge_covariance"]["all_finite"])
        for seed in seeds
        for row in records[seed].values()
    )
    checks["assay_controls_executed"] = (
        isinstance(controls.get("kernel"), Mapping)
        and isinstance(controls.get("behavioral"), Mapping)
        and isinstance(controls.get("assay_valid"), bool)
    )
    return {"valid": all(checks.values()), "checks": checks}


def _strict_less(value: Any, threshold: float) -> bool:
    return _finite_number(value) and float(value) < float(threshold)


def _strict_greater(value: Any, threshold: float) -> bool:
    return _finite_number(value) and float(value) > float(threshold)


def _loop_repeat_degradation(
    records: Mapping[str, Any],
    seeds: Sequence[int],
    arm: str,
    repeats: int,
) -> float | None:
    values: list[float] = []
    prefix = f"repeats_{int(repeats)}_suffix_"
    for seed in seeds:
        strata = records[str(seed)][arm]["behavior"]["loops"]["strata"]
        selected = [
            float(row["accuracy_degradation"])
            for key, row in strata.items()
            if key.startswith(prefix) and _finite_number(row.get("accuracy_degradation"))
        ]
        if not selected:
            return None
        values.append(max(selected))
    return max(values) if values else None


def _native_boundary_observables(
    records: Mapping[str, Any],
    seeds: Sequence[int],
    arm: str,
    profile: Mapping[str, Any],
) -> dict[str, Any]:
    """Collect every native margin-boundary rate used by a claim-bearing assay.

    The intervention receipt repeats the native decision across perturbation
    conditions, so its aggregate boundary rate is included once per seed.  A
    missing or malformed receipt makes the maximum undefined and therefore
    fails closed at adjudication.
    """

    per_seed: dict[str, dict[str, float | None]] = {}
    rates: list[float] = []
    complete = True

    def rate(row: Mapping[str, Any], numerator: str, denominator: str) -> float | None:
        value = row.get(numerator)
        total = row.get(denominator)
        if (
            type(value) is not int
            or type(total) is not int
            or total <= 0
            or value < 0
            or value > total
        ):
            return None
        return value / total

    for seed in seeds:
        record = records.get(str(seed), {}).get(arm, {})
        behavior = record.get("behavior", {})
        observed: dict[str, float | None] = {}
        for depth in profile["deep_depths"]:
            row = behavior.get("deep", {}).get("d4", {}).get(str(depth), {})
            observed[f"deep_{int(depth)}"] = rate(row, "boundary", "total")
        observed["diamonds"] = rate(
            behavior.get("diamonds", {}), "boundary", "decision_total"
        )
        observed["loops"] = rate(
            behavior.get("loops", {}), "boundary", "decision_total"
        )
        observed["null_perturbation"] = rate(
            record.get("null_perturbation", {}), "native_boundary", "total"
        )
        per_seed[str(seed)] = observed
        for value in observed.values():
            if value is None or not math.isfinite(value):
                complete = False
            else:
                rates.append(float(value))
    return {
        "per_seed_receipt_rates": per_seed,
        "maximum": max(rates) if complete and rates else None,
    }


def _relative_reduction(primary: Any, baseline: Any) -> float | None:
    if (
        not _finite_number(primary)
        or not _finite_number(baseline)
        or float(baseline) <= 0.0
    ):
        return None
    return 1.0 - float(primary) / float(baseline)


def _pilot_comparative_observables(
    records: Mapping[str, Any],
    seeds: Sequence[int],
) -> dict[str, Any]:
    """Return paired, seed-level pilot comparisons without applying thresholds."""

    semantic_reductions: list[float | None] = []
    leakage_reductions: list[float | None] = []
    depth_cr_margins: list[float | None] = []
    loop_cr_margins: list[float | None] = []
    depth_exact_gaps: list[float | None] = []
    loop_exact_gaps: list[float | None] = []

    def difference(left: Any, right: Any) -> float | None:
        if not _finite_number(left) or not _finite_number(right):
            return None
        return float(left) - float(right)

    for seed in seeds:
        seed_rows = records.get(str(seed), {})
        learned = seed_rows.get("learned_intertwiner", {})
        baseline = seed_rows.get("polar_cr", {})
        exact = seed_rows.get("polar_exact", {})
        learned_geometry = learned.get("geometry", {})
        baseline_geometry = baseline.get("geometry", {})
        learned_behavior = learned.get("behavior", {})
        baseline_behavior = baseline.get("behavior", {})
        exact_behavior = exact.get("behavior", {})

        semantic_reductions.append(
            _relative_reduction(
                learned_geometry.get("relations", {})
                .get("semantic_defect", {})
                .get("median"),
                baseline_geometry.get("relations", {})
                .get("semantic_defect", {})
                .get("median"),
            )
        )
        leakage_reductions.append(
            _relative_reduction(
                learned_geometry.get("structure", {})
                .get("generator_leakage", {})
                .get("median"),
                baseline_geometry.get("structure", {})
                .get("generator_leakage", {})
                .get("median"),
            )
        )
        learned_depth = (
            learned_behavior.get("deep", {}).get("d4", {}).get("512", {})
            .get("robust_accuracy")
        )
        baseline_depth = (
            baseline_behavior.get("deep", {}).get("d4", {}).get("512", {})
            .get("robust_accuracy")
        )
        exact_depth = (
            exact_behavior.get("deep", {}).get("d4", {}).get("512", {})
            .get("robust_accuracy")
        )
        learned_loop = learned_behavior.get("loops", {}).get("joint_robust_rate")
        baseline_loop = baseline_behavior.get("loops", {}).get("joint_robust_rate")
        exact_loop = exact_behavior.get("loops", {}).get("joint_robust_rate")
        depth_cr_margins.append(difference(learned_depth, baseline_depth))
        loop_cr_margins.append(difference(learned_loop, baseline_loop))
        depth_exact_gaps.append(difference(exact_depth, learned_depth))
        loop_exact_gaps.append(difference(exact_loop, learned_loop))

    def complete_mean(values: Sequence[float | None]) -> float | None:
        if not values or not all(_finite_number(value) for value in values):
            return None
        return sum(float(value) for value in values) / len(values)

    return {
        "semantic_defect_reduction_per_seed": semantic_reductions,
        "generator_leakage_reduction_per_seed": leakage_reductions,
        "depth512_margin_vs_polar_cr_per_seed": depth_cr_margins,
        "depth512_mean_margin_vs_polar_cr": complete_mean(depth_cr_margins),
        "depth512_positive_seed_count": sum(
            _finite_number(value) and float(value) > 0.0 for value in depth_cr_margins
        ),
        "loop_margin_vs_polar_cr_per_seed": loop_cr_margins,
        "loop_mean_margin_vs_polar_cr": complete_mean(loop_cr_margins),
        "loop_positive_seed_count": sum(
            _finite_number(value) and float(value) > 0.0 for value in loop_cr_margins
        ),
        "depth512_gap_vs_polar_exact_per_seed": depth_exact_gaps,
        "depth512_pooled_gap_vs_polar_exact": complete_mean(depth_exact_gaps),
        "loop_gap_vs_polar_exact_per_seed": loop_exact_gaps,
        "loop_pooled_gap_vs_polar_exact": complete_mean(loop_exact_gaps),
    }


def _typed_structural_max(records: Mapping[str, Any], seeds: Sequence[int], arm: str) -> float | None:
    values: list[float] = []
    excluded = {"tolerance", "all_finite", "passed"}
    for seed in seeds:
        typed = records[str(seed)][arm]["geometry"]["typed_three_way"]
        if typed.get("status") != "EVALUATED":
            return None
        structure = typed.get("structure", {})
        for key, value in structure.items():
            if key in excluded or key.endswith("rank") or key.startswith("expected_") or key == "hidden_dimension":
                continue
            if _finite_number(value):
                values.append(float(value))
    return max(values) if values else None


def _causal_observables(aggregate: Mapping[str, Any], arm: str) -> dict[str, Any]:
    row = aggregate[arm]
    causal = row["causal"]
    patch_values = [
        causal["state_patch_transition_accuracy"]["minimum"],
        causal["operator_patch_transition_accuracy"]["minimum"],
    ]
    control_values = [
        causal[name]["maximum"]
        for name in (
            "angle_matched_state_control_transition_accuracy",
            "reachable_state_control_transition_accuracy",
            "random_state_patch_transition_accuracy",
            "random_operator_patch_transition_accuracy",
            "cross_context_operator_control_transition_accuracy",
        )
    ]
    if not all(_finite_number(value) for value in patch_values + control_values):
        return {"patch_min": None, "control_max": None, "margin": None, "coverage_min": None}
    patch_min = min(float(value) for value in patch_values)
    control_max = max(float(value) for value in control_values)
    state_coverage = row["causal_coverage"]["state"]["minimum"]
    operator_coverage = row["causal_coverage"]["operator"]["minimum"]
    coverage = min(float(state_coverage), float(operator_coverage)) if all(
        _finite_number(value) for value in (state_coverage, operator_coverage)
    ) else None
    return {
        "patch_min": patch_min,
        "control_max": control_max,
        "margin": patch_min - control_max,
        "coverage_min": coverage,
    }


def adjudicate(
    records: Mapping[str, Any],
    aggregate: Mapping[str, Any],
    controls: Mapping[str, Any],
    integrity: Mapping[str, Any],
    profile_name: str,
    profile: Mapping[str, Any],
    preregistration: Mapping[str, Any],
) -> dict[str, Any]:
    seeds = tuple(int(seed) for seed in profile["seeds"])
    hard_arm = "hard_kernel_semantic_flat"
    learned_arm = "learned_intertwiner"
    baseline_arm = "polar_cr"
    hard = aggregate[hard_arm]
    learned = aggregate[learned_arm]
    baseline = aggregate[baseline_arm]
    groups: dict[str, dict[str, Any]] = {
        "hard_calibration": {},
        "learned_geometry": {},
        "learned_behavior": {},
        "pilot": {},
        "pilot_comparative": {},
    }

    def add(group: str, name: str, observed: Any, threshold: Any, passed: bool) -> None:
        groups[group][name] = {
            "observed": observed,
            "threshold": threshold,
            "pass": bool(passed),
        }

    if profile_name == "smoke":
        assay_valid = bool(controls.get("assay_valid"))
        return {
            "execution_integrity": "PASS" if integrity.get("valid") else "FAIL",
            "assay_validity": "PASS" if assay_valid else "FAIL",
            "scientific_status": "DEVELOPMENTAL_NOT_ADJUDICATED",
            "pilot_promotion": "NOT_EVALUATED",
            "gate_hierarchy": list(preregistration["status_hierarchy"]),
            "integrity_checks": dict(integrity.get("checks", {})),
            "scientific_checks": groups,
            "claim_boundary": "smoke tests execution and assay integrity only",
        }

    screen = preregistration["screen_thresholds"]
    hard_t = screen["hard_calibration"]
    hard_structural = _typed_structural_max(records, seeds, hard_arm)
    hard_geometry = hard["geometry"]
    hard_depth = hard["deep_d4"].get("512", {}).get("robust", {}).get("pooled")
    hard_loop = hard["loops"]["joint_robust"]["pooled"]
    hard_retention = hard["null_perturbation"]["prediction_retention"]["worst_seed"]
    hard_checks = (
        ("structural_residual", hard_structural, hard_t["structural_residual_max"], "max"),
        ("sigma7", hard_geometry["sigma7_over_sigma1"]["minimum"], hard_t["sigma7_over_sigma1_min"], "min"),
        ("sigma8", hard_geometry["sigma8_over_sigma1"]["maximum"], hard_t["sigma8_over_sigma1_max"], "max"),
        ("semantic_defect_median", hard_geometry["semantic_defect_seed_median"]["maximum"], hard_t["semantic_defect_median_max"], "max"),
        ("semantic_defect_p95", hard_geometry["semantic_defect_seed_p95"]["maximum"], hard_t["semantic_defect_p95_max"], "max"),
        ("ambient_curvature", hard_geometry["ambient_curvature_seed_median"]["minimum"], hard_t["ambient_curvature_median_min"], "min"),
        ("depth512_robust", hard_depth, hard_t["depth512_robust_accuracy_min"], "min"),
        ("loop_joint_robust", hard_loop, hard_t["loop_joint_robust_accuracy_min"], "min"),
        ("null_retention", hard_retention, hard_t["null_prediction_retention_min"], "min"),
    )
    for name, observed, threshold, direction in hard_checks:
        add(
            "hard_calibration",
            name,
            observed,
            {"strict_" + ("maximum" if direction == "max" else "minimum"): threshold},
            _strict_less(observed, threshold) if direction == "max" else _strict_greater(observed, threshold),
        )
    hard_gauge_pass = all(
        records[str(seed)][hard_arm]["geometry"]["typed_three_way"]
        .get("gauge_covariance", {})
        .get("passed")
        is True
        for seed in seeds
    )
    add(
        "hard_calibration",
        "coordinate_gauge_covariance",
        hard_gauge_pass,
        {"exact": True},
        hard_gauge_pass,
    )

    geometry_t = screen["learned_geometry"]
    learned_geometry = learned["geometry"]
    baseline_semantic = baseline["geometry"]["semantic_defect_seed_median"]["mean"]
    learned_semantic = learned_geometry["semantic_defect_seed_median"]["mean"]
    reduction = (
        1.0 - float(learned_semantic) / float(baseline_semantic)
        if _finite_number(learned_semantic) and _finite_number(baseline_semantic) and float(baseline_semantic) > 0.0
        else None
    )
    geometry_checks = (
        ("projector_residual", learned_geometry["projector_residual"]["maximum"], geometry_t["projector_residual_max"], "max"),
        ("sigma7", learned_geometry["sigma7_over_sigma1"]["minimum"], geometry_t["sigma7_over_sigma1_min"], "min"),
        ("sigma8", learned_geometry["sigma8_over_sigma1"]["maximum"], geometry_t["sigma8_over_sigma1_max"], "max"),
        ("principal_angle", learned_geometry["principal_angle"]["maximum"], geometry_t["principal_angle_distance_max"], "max"),
        ("centered_readout_leakage", learned_geometry["centered_readout_leakage"]["maximum"], geometry_t["centered_readout_leakage_max"], "max"),
        ("generator_leakage_p95", learned_geometry["generator_leakage_seed_p95"]["maximum"], geometry_t["generator_leakage_p95_max"], "max"),
        ("generator_leakage_max", learned_geometry["generator_leakage_seed_max"]["maximum"], geometry_t["generator_leakage_max"], "max"),
        ("length64_leakage_p95", learned_geometry["length64_leakage_seed_p95"]["maximum"], geometry_t["length64_leakage_p95_max"], "max"),
        ("length64_leakage_max", learned_geometry["length64_leakage_seed_max"]["maximum"], geometry_t["length64_leakage_max"], "max"),
        ("intertwining_median", learned_geometry["intertwining_seed_median"]["maximum"], geometry_t["intertwining_median_max"], "max"),
        ("intertwining_p95", learned_geometry["intertwining_seed_p95"]["maximum"], geometry_t["intertwining_p95_max"], "max"),
        ("semantic_defect_median", learned_geometry["semantic_defect_seed_median"]["maximum"], geometry_t["semantic_defect_median_max"], "max"),
        ("semantic_defect_p95", learned_geometry["semantic_defect_seed_p95"]["maximum"], geometry_t["semantic_defect_p95_max"], "max"),
        ("semantic_defect_reduction", reduction, geometry_t["semantic_defect_reduction_vs_polar_cr_min"], "min"),
        ("null_curvature", learned_geometry["null_curvature_seed_median"]["minimum"], geometry_t["null_curvature_median_min"], "min"),
        ("semantic_null_ratio", learned_geometry["semantic_null_ratio_seed_median"]["maximum"], geometry_t["semantic_to_null_curvature_ratio_median_max"], "max"),
    )
    add(
        "learned_geometry",
        "extraction_valid",
        learned_geometry["extraction_valid_fraction"],
        {"exact": 1.0},
        learned_geometry["extraction_valid_fraction"] == 1.0,
    )
    add(
        "learned_geometry",
        "rank_unambiguous",
        learned_geometry["rank_ambiguous_count"],
        {"exact": 0},
        learned_geometry["rank_ambiguous_count"] == 0,
    )
    add(
        "learned_geometry",
        "coordinate_gauge_covariance",
        learned_geometry["gauge_pass_fraction"],
        {"exact": 1.0},
        learned_geometry["gauge_pass_fraction"] == 1.0,
    )
    for name, observed, threshold, direction in geometry_checks:
        add(
            "learned_geometry",
            name,
            observed,
            {"strict_" + ("maximum" if direction == "max" else "minimum"): threshold},
            _strict_less(observed, threshold) if direction == "max" else _strict_greater(observed, threshold),
        )

    behavior_t = screen["learned_behavior"]
    learned_depth = learned["deep_d4"].get("512", {}).get("robust", {}).get("pooled")
    baseline_depth = baseline["deep_d4"].get("512", {}).get("robust", {}).get("pooled")
    depth_margin = (
        float(learned_depth) - float(baseline_depth)
        if _finite_number(learned_depth) and _finite_number(baseline_depth)
        else None
    )
    loop_margin = (
        learned["loops"]["joint_robust"]["pooled"] - baseline["loops"]["joint_robust"]["pooled"]
        if _finite_number(learned["loops"]["joint_robust"]["pooled"])
        and _finite_number(baseline["loops"]["joint_robust"]["pooled"])
        else None
    )
    causal = _causal_observables(aggregate, learned_arm)
    behavior_checks = (
        ("depth512_robust", learned_depth, behavior_t["depth512_robust_accuracy_min"], "min"),
        ("depth512_margin_vs_cr", depth_margin, behavior_t["depth512_margin_vs_polar_cr_min"], "min"),
        ("diamond_joint_robust", learned["diamonds"]["joint_robust"]["pooled"], behavior_t["diamond_joint_robust_accuracy_min"], "min"),
        ("loop_joint_robust", learned["loops"]["joint_robust"]["pooled"], behavior_t["loop_joint_robust_accuracy_min"], "min"),
        ("loop_margin_vs_cr", loop_margin, behavior_t["loop_margin_vs_polar_cr_min"], "min"),
        ("repeat32_degradation", _loop_repeat_degradation(records, seeds, learned_arm, 32), behavior_t["repeat32_worst_suffix_degradation_max"], "max"),
        ("causal_patch", causal["patch_min"], behavior_t["causal_patch_accuracy_min"], "min"),
        ("causal_control", causal["control_max"], behavior_t["causal_control_accuracy_max"], "max"),
        ("causal_margin", causal["margin"], behavior_t["causal_margin_min"], "min"),
        ("causal_coverage", causal["coverage_min"], behavior_t["causal_coverage_min"], "min"),
        ("null_prediction_retention", learned["null_perturbation"]["prediction_retention"]["worst_seed"], behavior_t["null_prediction_retention_min"], "min"),
        ("null_centered_logit_effect_p95", learned["null_perturbation"]["relative_effect_seed_p95"]["maximum"], behavior_t["null_centered_logit_relative_effect_p95_max"], "max"),
    )
    for name, observed, threshold, direction in behavior_checks:
        add(
            "learned_behavior",
            name,
            observed,
            {"strict_" + ("maximum" if direction == "max" else "minimum"): threshold},
            _strict_less(observed, threshold) if direction == "max" else _strict_greater(observed, threshold),
        )

    if profile_name == "pilot":
        pilot = preregistration["pilot_thresholds"]
        boundary = _native_boundary_observables(
            records, seeds, learned_arm, profile
        )
        pilot_checks = (
            ("depth128_pooled", learned["deep_d4"]["128"]["robust"]["pooled"], pilot["depth128_robust_pooled_min"], "min"),
            ("depth128_worst", learned["deep_d4"]["128"]["robust"]["worst_seed"], pilot["depth128_robust_worst_seed_min"], "min"),
            ("depth256_pooled", learned["deep_d4"]["256"]["robust"]["pooled"], pilot["depth256_robust_pooled_min"], "min"),
            ("depth256_worst", learned["deep_d4"]["256"]["robust"]["worst_seed"], pilot["depth256_robust_worst_seed_min"], "min"),
            ("depth512_pooled", learned["deep_d4"]["512"]["robust"]["pooled"], pilot["depth512_robust_pooled_min"], "min"),
            ("depth512_worst", learned["deep_d4"]["512"]["robust"]["worst_seed"], pilot["depth512_robust_worst_seed_min"], "min"),
            ("diamond_pooled", learned["diamonds"]["joint_robust"]["pooled"], pilot["diamond_joint_pooled_min"], "min"),
            ("diamond_worst", learned["diamonds"]["joint_robust"]["worst_seed"], pilot["diamond_joint_worst_seed_min"], "min"),
            ("loop_pooled", learned["loops"]["joint_robust"]["pooled"], pilot["loop_joint_pooled_min"], "min"),
            ("loop_worst", learned["loops"]["joint_robust"]["worst_seed"], pilot["loop_joint_worst_seed_min"], "min"),
            ("equivalent_agreement_pooled", learned["diamonds"]["agreement"]["pooled"], pilot["equivalent_agreement_pooled_min"], "min"),
            ("equivalent_agreement_worst", learned["diamonds"]["agreement"]["worst_seed"], pilot["equivalent_agreement_worst_seed_min"], "min"),
            ("inequivalent_pooled", learned["inequivalent"]["sensitivity"]["pooled"], pilot["inequivalent_sensitivity_pooled_min"], "min"),
            ("inequivalent_worst", learned["inequivalent"]["sensitivity"]["worst_seed"], pilot["inequivalent_sensitivity_worst_seed_min"], "min"),
            ("repeat8_degradation", _loop_repeat_degradation(records, seeds, learned_arm, 8), pilot["repeat8_degradation_max"], "max"),
            ("repeat32_degradation", _loop_repeat_degradation(records, seeds, learned_arm, 32), pilot["repeat32_degradation_max"], "max"),
            ("native_boundary_rate", boundary["maximum"], pilot["native_boundary_rate_max"], "max"),
            ("semantic_defect_median", learned_geometry["semantic_defect_seed_median"]["maximum"], pilot["semantic_defect_worst_seed_median_max"], "max"),
            ("semantic_defect_p95", learned_geometry["semantic_defect_seed_p95"]["maximum"], pilot["semantic_defect_worst_seed_p95_max"], "max"),
            ("sigma7", learned_geometry["sigma7_over_sigma1"]["minimum"], pilot["sigma7_over_sigma1_min"], "min"),
            ("sigma8", learned_geometry["sigma8_over_sigma1"]["maximum"], pilot["sigma8_over_sigma1_max"], "max"),
            ("principal_angle", learned_geometry["principal_angle"]["maximum"], pilot["principal_angle_distance_max"], "max"),
            ("readout_leakage", learned_geometry["centered_readout_leakage"]["maximum"], pilot["centered_readout_leakage_max"], "max"),
            ("generator_p95", learned_geometry["generator_leakage_seed_p95"]["maximum"], pilot["generator_leakage_p95_max"], "max"),
            ("generator_max", learned_geometry["generator_leakage_seed_max"]["maximum"], pilot["generator_leakage_max"], "max"),
            ("length64_p95", learned_geometry["length64_leakage_seed_p95"]["maximum"], pilot["length64_leakage_p95_max"], "max"),
            ("length64_max", learned_geometry["length64_leakage_seed_max"]["maximum"], pilot["length64_leakage_max"], "max"),
            ("intertwining_median", learned_geometry["intertwining_seed_median"]["maximum"], pilot["intertwining_median_max"], "max"),
            ("intertwining_p95", learned_geometry["intertwining_seed_p95"]["maximum"], pilot["intertwining_p95_max"], "max"),
            ("intertwining_max", learned_geometry["intertwining_seed_max"]["maximum"], pilot["intertwining_max"], "max"),
            ("null_curvature", learned_geometry["null_curvature_seed_median"]["minimum"], pilot["null_curvature_median_min"], "min"),
            ("semantic_null_ratio", learned_geometry["semantic_null_ratio_seed_median"]["maximum"], pilot["semantic_to_null_curvature_ratio_median_max"], "max"),
            ("causal_patch", causal["patch_min"], pilot["causal_patch_accuracy_min"], "min"),
            ("causal_native_accuracy", learned["causal"]["native_original_accuracy"]["minimum"], pilot["causal_native_accuracy_min"], "min"),
            ("causal_control", causal["control_max"], pilot["causal_control_accuracy_max"], "max"),
            ("causal_margin", causal["margin"], pilot["causal_margin_min"], "min"),
            ("causal_coverage", causal["coverage_min"], pilot["causal_coverage_min"], "min"),
            ("null_retention_pooled", learned["null_perturbation"]["prediction_retention"]["pooled"], pilot["null_retention_pooled_min"], "min"),
            ("null_retention_worst", learned["null_perturbation"]["prediction_retention"]["worst_seed"], pilot["null_retention_worst_seed_min"], "min"),
            ("null_effect_p95", learned["null_perturbation"]["relative_effect_seed_p95"]["maximum"], pilot["null_centered_logit_effect_p95_max"], "max"),
        )
        for name, observed, threshold, direction in pilot_checks:
            add(
                "pilot",
                name,
                observed,
                {"strict_" + ("maximum" if direction == "max" else "minimum"): threshold},
                _strict_less(observed, threshold) if direction == "max" else _strict_greater(observed, threshold),
            )

        # Preserve the full receipt-level boundary surface rather than only the
        # maximum that determines the gate.
        groups["pilot"]["native_boundary_rate"]["observed"] = boundary

        comparative_t = pilot["comparative"]
        comparative = _pilot_comparative_observables(records, seeds)
        semantic_reductions = comparative["semantic_defect_reduction_per_seed"]
        leakage_reductions = comparative["generator_leakage_reduction_per_seed"]
        paired_reduction_count = sum(
            _strict_greater(semantic, comparative_t["semantic_defect_reduction_vs_polar_cr_min"])
            and _strict_greater(leakage, comparative_t["generator_leakage_reduction_vs_polar_cr_min"])
            for semantic, leakage in zip(
                semantic_reductions, leakage_reductions, strict=True
            )
        )
        add(
            "pilot_comparative",
            "paired_geometry_reduction_seed_count",
            {
                "semantic_defect_reduction_per_seed": semantic_reductions,
                "generator_leakage_reduction_per_seed": leakage_reductions,
                "passing_seed_count": paired_reduction_count,
            },
            {
                "semantic_defect_strict_minimum": comparative_t["semantic_defect_reduction_vs_polar_cr_min"],
                "generator_leakage_strict_minimum": comparative_t["generator_leakage_reduction_vs_polar_cr_min"],
                "integer_minimum_count": comparative_t["reduction_seed_count_min"],
            },
            paired_reduction_count >= comparative_t["reduction_seed_count_min"],
        )
        comparative_checks = (
            (
                "depth512_mean_margin_vs_polar_cr",
                comparative["depth512_mean_margin_vs_polar_cr"],
                comparative_t["depth512_mean_margin_vs_polar_cr_min"],
                "min",
            ),
            (
                "loop_mean_margin_vs_polar_cr",
                comparative["loop_mean_margin_vs_polar_cr"],
                comparative_t["loop_mean_margin_vs_polar_cr_min"],
                "min",
            ),
            (
                "depth512_pooled_gap_vs_polar_exact",
                comparative["depth512_pooled_gap_vs_polar_exact"],
                comparative_t["depth512_noninferiority_vs_polar_exact_max_gap"],
                "max",
            ),
            (
                "loop_pooled_gap_vs_polar_exact",
                comparative["loop_pooled_gap_vs_polar_exact"],
                comparative_t["loop_noninferiority_vs_polar_exact_max_gap"],
                "max",
            ),
        )
        for name, observed, threshold, direction in comparative_checks:
            add(
                "pilot_comparative",
                name,
                observed,
                {"strict_" + ("maximum" if direction == "max" else "minimum"): threshold},
                _strict_less(observed, threshold)
                if direction == "max"
                else _strict_greater(observed, threshold),
            )
        for name, observed, threshold in (
            (
                "depth512_positive_seed_count",
                comparative["depth512_positive_seed_count"],
                comparative_t["depth512_positive_seed_count_min"],
            ),
            (
                "loop_positive_seed_count",
                comparative["loop_positive_seed_count"],
                comparative_t["loop_positive_seed_count_min"],
            ),
        ):
            add(
                "pilot_comparative",
                name,
                {
                    "count": observed,
                    "per_seed": comparative[
                        "depth512_margin_vs_polar_cr_per_seed"
                        if name.startswith("depth512")
                        else "loop_margin_vs_polar_cr_per_seed"
                    ],
                },
                {"integer_minimum_count": threshold},
                type(observed) is int and observed >= threshold,
            )

    assay_valid = bool(controls.get("assay_valid"))
    hard_pass = all(row["pass"] for row in groups["hard_calibration"].values())
    curved_gate_names = {"null_curvature", "semantic_null_ratio"}
    geometry_pass = all(
        row["pass"]
        for name, row in groups["learned_geometry"].items()
        if name not in curved_gate_names
    )
    behavior_pass = all(row["pass"] for row in groups["learned_behavior"].values())
    pilot_pass = profile_name != "pilot" or all(
        row["pass"]
        for name, row in groups["pilot"].items()
        if name not in curved_gate_names
    ) and all(row["pass"] for row in groups["pilot_comparative"].values())
    curved = all(
        groups["learned_geometry"].get(name, {}).get("pass", False)
        for name in curved_gate_names
    )
    if profile_name == "pilot":
        curved = curved and all(
            groups["pilot"].get(name, {}).get("pass", False)
            for name in curved_gate_names
        )
    if not integrity.get("valid") or not assay_valid:
        scientific = "NOT_EVALUATED"
    elif not hard_pass:
        scientific = "CALIBRATION_FAILURE"
    elif not geometry_pass:
        scientific = "COMPILED_KERNEL_ONLY"
    elif not behavior_pass or not pilot_pass:
        scientific = "GEOMETRY_WITHOUT_COMPUTATIONAL_CLOSURE"
    elif not curved:
        scientific = "INVARIANT_KERNEL_WITHOUT_CURVED_AMBIENT"
    else:
        scientific = "PASS_CURVED_INVARIANT_QUOTIENT"
    promotion = (
        "PROMOTE_TO_FIVE_SEED_PILOT"
        if profile_name == "screen" and scientific == "PASS_CURVED_INVARIANT_QUOTIENT"
        else "DO_NOT_PROMOTE"
        if profile_name == "screen"
        else "NOT_APPLICABLE"
    )
    return {
        "execution_integrity": "PASS" if integrity.get("valid") else "FAIL",
        "assay_validity": "PASS" if assay_valid else "FAIL",
        "scientific_status": scientific,
        "pilot_promotion": promotion,
        "gate_hierarchy": list(preregistration["status_hierarchy"]),
        "integrity_checks": dict(integrity.get("checks", {})),
        "scientific_checks": groups,
        "claim_boundary": (
            "explicitly pressured invariant quotient only; no spontaneous Neuralese, "
            "useful ambient memory, awareness, or consciousness claim"
        ),
    }


def render_chart(
    output_dir: Path,
    aggregate: Mapping[str, Any],
    profile: Mapping[str, Any],
) -> str:
    arms = tuple(PRIMARY_INVARIANT_KERNEL_ARMS)
    labels = (
        "polar supervised",
        "polar CR",
        "polar exact",
        "learned intertwiner",
        "hard supervised",
        "hard semantic-flat",
    )
    colors = ("#777777", "#5b8ff9", "#61d9a8", "#e8684a", "#7262fd", "#f6bd16")
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    depths = [int(value) for value in profile["deep_depths"]]
    for arm, label, color in zip(arms, labels, colors, strict=True):
        values = [aggregate[arm]["deep_d4"][str(depth)]["robust"]["pooled"] for depth in depths]
        axes[0, 0].plot(depths, values, marker="o", label=label, color=color)
    axes[0, 0].set_title("Robust D4 accuracy across recurrent depth")
    axes[0, 0].set_xlabel("Depth")
    axes[0, 0].set_ylabel("Robust accuracy")
    axes[0, 0].set_ylim(0.0, 1.02)
    axes[0, 0].grid(alpha=0.25)
    axes[0, 0].legend(fontsize=7, ncol=2)

    x = np.arange(len(arms))
    width = 0.36
    diamonds = [aggregate[arm]["diamonds"]["joint_robust"]["pooled"] for arm in arms]
    loops = [aggregate[arm]["loops"]["joint_robust"]["pooled"] for arm in arms]
    axes[0, 1].bar(x - width / 2, diamonds, width, label="diamonds")
    axes[0, 1].bar(x + width / 2, loops, width, label="loops")
    axes[0, 1].set_xticks(x, labels, rotation=25, ha="right")
    axes[0, 1].set_ylim(0.0, 1.02)
    axes[0, 1].set_title("Held-out path behavior")
    axes[0, 1].set_ylabel("Joint robust accuracy")
    axes[0, 1].legend(fontsize=8)

    sigma8 = [
        max(float(aggregate[arm]["geometry"]["sigma8_over_sigma1"]["mean"] or 0.0), 1e-12)
        for arm in arms
    ]
    leakage = [
        max(float(aggregate[arm]["geometry"]["generator_leakage_seed_max"]["mean"] or 0.0), 1e-12)
        for arm in arms
    ]
    axes[1, 0].bar(x - width / 2, sigma8, width, label=r"$\sigma_8/\sigma_1$")
    axes[1, 0].bar(x + width / 2, leakage, width, label="generator leakage")
    axes[1, 0].set_yscale("log")
    axes[1, 0].set_xticks(x, labels, rotation=25, ha="right")
    axes[1, 0].set_title("Observable-kernel diagnostics")
    axes[1, 0].set_ylabel("Value (log scale)")
    axes[1, 0].legend(fontsize=8)

    semantic = [
        max(float(aggregate[arm]["geometry"]["semantic_defect_seed_median"]["mean"] or 0.0), 1e-12)
        for arm in arms
    ]
    null = [
        max(float(aggregate[arm]["geometry"]["null_curvature_seed_median"]["mean"] or 0.0), 1e-12)
        for arm in arms
    ]
    axes[1, 1].bar(x - width / 2, semantic, width, label="semantic defect")
    axes[1, 1].bar(x + width / 2, null, width, label="null curvature")
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_xticks(x, labels, rotation=25, ha="right")
    axes[1, 1].set_title("Horizontal flatness versus vertical curvature")
    axes[1, 1].set_ylabel("Median normalized defect")
    axes[1, 1].legend(fontsize=8)
    path = output_dir / CHART_NAME
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path.name


def _format(value: Any) -> str:
    return "—" if not _finite_number(value) else f"{float(value):.4f}"


def render_report(result: Mapping[str, Any]) -> str:
    aggregate = result["aggregate"]
    status = result["gates"]["status"]
    deepest = str(max(int(value) for value in result["config"]["deep_depths"]))
    lines = [
        "# Invariant Observable Kernel v0.6.0",
        "",
        "**Author:** Komorebi P.",
        "",
        f"**Run profile:** `{result['profile']}`",
        "",
        "## Outcome",
        "",
        f"- Execution integrity: **{status['execution_integrity']}**",
        f"- Assay validity: **{status['assay_validity']}**",
        f"- Scientific status: **{status['scientific_status']}**",
        f"- Pilot promotion: **{status['pilot_promotion']}**",
        "",
        "The block tests whether a fixed rank-seven centered-behavior quotient",
        "can remain causally closed while a five-dimensional null fiber carries",
        "behaviorally inert dynamics. A typed one-plus-four split is reported only",
        "for the hard architecture that registers it before training.",
        "",
        "## Main results",
        "",
        "| Arm | Deepest D4 | Diamonds | Loops | sigma8/sigma1 | Generator leak | Semantic defect | Null curvature | Null retention |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in PRIMARY_INVARIANT_KERNEL_ARMS:
        row = aggregate[arm]
        values = (
            f"`{arm}`",
            _format(row["deep_d4"][deepest]["robust"]["pooled"]),
            _format(row["diamonds"]["joint_robust"]["pooled"]),
            _format(row["loops"]["joint_robust"]["pooled"]),
            _format(row["geometry"]["sigma8_over_sigma1"]["mean"]),
            _format(row["geometry"]["generator_leakage_seed_max"]["mean"]),
            _format(row["geometry"]["semantic_defect_seed_median"]["mean"]),
            _format(row["geometry"]["null_curvature_seed_median"]["mean"]),
            _format(row["null_perturbation"]["prediction_retention"]["pooled"]),
        )
        lines.append("| " + " | ".join(values) + " |")
    lines.extend(["", "## Gate hierarchy", ""])
    for group_name, group in status["scientific_checks"].items():
        if not group:
            continue
        lines.extend([f"### {group_name.replace('_', ' ').title()}", ""])
        for name, row in group.items():
            lines.append(f"- `{name}`: **{'PASS' if row['pass'] else 'FAIL'}**")
        lines.append("")
    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "The hard-kernel arms are compiled sufficiency controls. Their fixed",
            "ambient encoder is dormant under the task objective and is not evidence",
            "of useful memory. The learned-intertwiner arm receives explicit chart,",
            "readout, intertwining, and semantic-relation pressure. A positive result",
            "therefore supports an explicitly induced quotient, not spontaneous",
            "Neuralese. No awareness or consciousness claim is tested.",
            "",
            "All geometry was computed in float64 after promoting the exact executed",
            "float32 matrices. Scientific failure does not invalidate a run whose",
            "execution and assay integrity pass.",
        ]
    )
    return "\n".join(lines) + "\n"


def validate_invocation(profile_name: str, output_dir: Path, replay: bool) -> str:
    if profile_name != "pilot":
        if replay:
            raise ValueError("--replay is only meaningful for the pilot profile")
        return "developmental"
    if replay:
        if output_dir.resolve() == CANONICAL_PILOT_DIR.resolve():
            raise ValueError("pilot replay cannot target the canonical retained directory")
        return "non_evidentiary_pilot_replay"
    if output_dir.resolve() != CANONICAL_PILOT_DIR.resolve():
        raise ValueError("fresh pilot may target only results/invariant_kernel_pilot")
    return "fresh_pilot"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=tuple(PROFILE_CONFIG), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--replay", action="store_true")
    args = parser.parse_args(argv)
    if args.device != "cpu":
        raise ValueError("sealed v0.6 profiles currently permit CPU only")
    if not sys.flags.ignore_environment or not sys.flags.safe_path or not sys.dont_write_bytecode:
        raise RuntimeError("invoke with python -E -P -B")
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    try:
        torch.set_num_interop_threads(1)
    except RuntimeError:
        pass

    preregistration = validate_preregistration()
    profile = dict(PROFILE_CONFIG[args.profile])
    output_dir = args.output_dir.resolve()
    run_mode = validate_invocation(args.profile, output_dir, args.replay)
    assert_clean_output(output_dir)
    started = time.perf_counter()
    source_sha256, source_files = source_digest()
    preregistration_sha256 = sha256_file(PREREGISTRATION)
    write_json(
        output_dir / "RUN_STARTED.json",
        {
            "schema": "komorebi.neuralese.invariant_kernel.run_started.v1",
            "version": VERSION,
            "profile": args.profile,
            "run_mode": run_mode,
            "source_digest": source_sha256,
            "preregistration_sha256": preregistration_sha256,
            "runtime": runtime_receipt(),
        },
    )
    phase = time.perf_counter()
    audit_bank, banks, eval_receipt = build_evaluation_banks(
        output_dir,
        profile,
        source_sha256=source_sha256,
        preregistration_sha256=preregistration_sha256,
    )
    validate_evaluation_banks(
        output_dir,
        audit_bank,
        banks,
        eval_receipt,
        profile,
        expected_source_digest=source_sha256,
        expected_preregistration_sha256=preregistration_sha256,
    )
    bank_seconds = time.perf_counter() - phase

    phase = time.perf_counter()
    kernel_controls = adversarial_assay_controls()
    behavioral_controls = evaluate_control_suite(
        audit_bank,
        deep_examples=min(256, int(profile["deep_examples"])),
        device=args.device,
    )
    controls = {
        "schema": "komorebi.neuralese.invariant_kernel.controls.v1",
        "kernel": kernel_controls,
        "behavioral": behavioral_controls,
        "assay_valid": bool(kernel_controls.get("assay_valid"))
        and bool(behavioral_controls.get("assay_valid")),
    }
    write_json(output_dir / "CONTROLS.json", controls)
    controls_seconds = time.perf_counter() - phase

    phase = time.perf_counter()
    training, checkpoint_seal = train_and_seal(
        output_dir,
        profile,
        device=args.device,
        source_sha256=source_sha256,
        preregistration_sha256=preregistration_sha256,
    )
    training_seconds = time.perf_counter() - phase
    phase = time.perf_counter()
    records, record_index = evaluate_panel(
        output_dir,
        audit_bank,
        banks,
        profile,
        device=args.device,
        source_sha256=source_sha256,
        preregistration_sha256=preregistration_sha256,
        checkpoint_seal=checkpoint_seal,
    )
    evaluation_seconds = time.perf_counter() - phase
    aggregate = aggregate_records(records, profile)
    aggregate_sha256 = hashlib.sha256(canonical_json_bytes(aggregate)).hexdigest()
    integrity = validate_execution_integrity(
        records,
        record_index,
        training,
        controls,
        profile,
        output_dir=output_dir,
        source_sha256=source_sha256,
        preregistration_sha256=preregistration_sha256,
        checkpoint_seal=checkpoint_seal,
        eval_receipt=eval_receipt,
    )
    status = adjudicate(
        records,
        aggregate,
        controls,
        integrity,
        args.profile,
        profile,
        preregistration,
    )
    gates = {
        "schema": "komorebi.neuralese.invariant_kernel.gates.v1",
        "version": VERSION,
        "profile": args.profile,
        "run_mode": run_mode,
        "source_digest": source_sha256,
        "preregistration_sha256": preregistration_sha256,
        "status": status,
    }
    chart = render_chart(output_dir, aggregate, profile)
    result = {
        "schema": SCHEMA,
        "version": VERSION,
        "profile": args.profile,
        "run_mode": run_mode,
        "config": _profile_as_registered(profile),
        "source_digest": source_sha256,
        "source_files": source_files,
        "preregistration_sha256": preregistration_sha256,
        "training_contract": invariant_kernel_training_contract(
            train_config(profile, int(profile["seeds"][0]), args.device)
        ),
        "checkpoint_seal": checkpoint_seal,
        "evaluation_bank_fingerprint": eval_receipt["fingerprint"],
        "record_index": record_index,
        "records": records,
        "training": training,
        "controls": controls,
        "aggregate": aggregate,
        "aggregate_sha256": aggregate_sha256,
        "gates": gates,
        "runtime": runtime_receipt(),
        "phase_seconds": {
            "evaluation_bank": bank_seconds,
            "controls": controls_seconds,
            "training": training_seconds,
            "evaluation": evaluation_seconds,
            "total": time.perf_counter() - started,
        },
        "chart": {"path": chart, "sha256": sha256_file(output_dir / chart)},
    }
    write_json(output_dir / "RESULTS.json", result)
    write_json(output_dir / "GATES.json", gates)
    (output_dir / "REPORT.md").write_text(render_report(result), encoding="utf-8")
    complete = {
        "schema": "komorebi.neuralese.invariant_kernel.run_complete.v1",
        "version": VERSION,
        "profile": args.profile,
        "run_mode": run_mode,
        "source_digest": source_sha256,
        "preregistration_sha256": preregistration_sha256,
        "checkpoint_seal_sha256": sha256_file(output_dir / "CHECKPOINT_SEAL.json"),
        "evaluation_bank_fingerprint": eval_receipt["fingerprint"],
        "record_hashes": record_index,
        "aggregate_sha256": aggregate_sha256,
        "execution_integrity": status["execution_integrity"],
        "assay_validity": status["assay_validity"],
        "scientific_status": status["scientific_status"],
        "pilot_promotion": status["pilot_promotion"],
        "results_sha256": sha256_file(output_dir / "RESULTS.json"),
        "gates_sha256": sha256_file(output_dir / "GATES.json"),
        "controls_sha256": sha256_file(output_dir / "CONTROLS.json"),
        "report_sha256": sha256_file(output_dir / "REPORT.md"),
        "chart_sha256": sha256_file(output_dir / chart),
    }
    # RUN_COMPLETE is deliberately the last filesystem mutation.
    write_json(output_dir / "RUN_COMPLETE.json", complete)
    print(json.dumps(complete, indent=2, sort_keys=True))
    return 0 if status["execution_integrity"] == "PASS" and status["assay_validity"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
