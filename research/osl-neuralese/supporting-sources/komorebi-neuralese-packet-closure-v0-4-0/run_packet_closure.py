#!/usr/bin/env python3
"""Run the prospective v0.4 ambient packet-closure training block.

The runner enforces three phase boundaries:

1. train the complete registered paired arm panel using construction-side data only;
2. serialize and hash every successful checkpoint, then write a seal; and
3. only after that seal exists, materialize the horizon-eight audit bank and
   evaluate the frozen checkpoints.

Scientific gate failures are retained as results. A completed run exits zero
when capability or mechanism hypotheses fail, while infrastructure or assay-
integrity failures are recorded and return a nonzero status.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import itertools
import json
import math
import os
import platform
import statistics
import sys
import time
import traceback
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

if __name__ == "__main__" and not (
    sys.flags.ignore_environment
    and sys.flags.safe_path
    and sys.flags.dont_write_bytecode
):
    raise SystemExit(
        "Run the sealed experiment with: python -E -P -B run_packet_closure.py"
    )
sys.dont_write_bytecode = True

import numpy as np
import torch


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
_unsafe_preimport_paths = [
    path
    for path in (
        [ROOT / "__pycache__", SRC]
        + list(ROOT.glob("*.py"))
        + list(ROOT.glob("*.pyc"))
        + list(ROOT.glob("*.pyo"))
        + list(SRC.rglob("*"))
    )
    if path.exists()
    and (
        path.is_symlink()
        or path.name == "__pycache__"
        or path.suffix.lower() in {".pyc", ".pyo"}
    )
]
if _unsafe_preimport_paths:
    raise SystemExit(
        "symlinks and local bytecode/cache artifacts are forbidden before source-sealed execution: "
        + ", ".join(
            path.relative_to(ROOT).as_posix()
            for path in _unsafe_preimport_paths[:8]
        )
    )
# Always prepend the sealed local source, even if an untrusted duplicate path
# already appears later in PYTHONPATH.
sys.path.insert(0, str(SRC))

from komorebi_neuralese.algebra import D4_RELATIONS, N_STATES, canonical_maps
from komorebi_neuralese.ambient_eval import (
    episode_bank_receipts,
    episode_contract,
    file_sha256,
    json_ready,
)
from komorebi_neuralese.data import EpisodeBatch, EpisodeGenerator
from komorebi_neuralese.evaluate import intervention_metrics
from komorebi_neuralese.packet_closure_eval import (
    evaluate_ambient_complement_causality,
    evaluate_hard_polar_geometry,
    evaluate_heldout_packet,
    evaluate_null_loop_retention,
    evaluate_sampled_switched_gain,
    evaluate_structured_deep_accuracy,
    freeze_heldout_bank,
    sample_switch_words,
)
from komorebi_neuralese.packet_closure_train import (
    PRIMARY_PACKET_CLOSURE_ARMS,
    PacketClosureLossWeights,
    PacketClosureTrainConfig,
    build_packet_closure_model,
    construction_checkpoint_metadata,
    make_v04_construction_bank,
    make_v04_suffix_plan,
    state_dict_digest,
    terminal_firewall_policy_digest,
    train_packet_closure_arm,
)
from komorebi_neuralese.reporting import source_files, tree_digest
from komorebi_neuralese.stability_training import (
    feshbach_block_diagnostics,
    feshbach_return_diagnostics,
    g_orthogonal_anchor_projector,
    metric_condition_diagnostics,
)


VERSION = "0.4.0"
SCHEMA_PREFIX = "komorebi.neuralese.packet_closure"
ARM_NAMES = tuple(PRIMARY_PACKET_CLOSURE_ARMS)
EXPECTED_ARM_NAMES = (
    "euclidean_supervised",
    "euclidean_cr",
    "polar_supervised",
    "polar_cr",
)
if ARM_NAMES != EXPECTED_ARM_NAMES:
    raise RuntimeError("live primary packet-closure arm registry changed")

PRIMARY_ARM = "polar_cr"
POLAR_ARMS = ("polar_supervised", "polar_cr")
TWO_BY_TWO_CELLS = {
    (0, 0): "euclidean_supervised",
    (0, 1): "euclidean_cr",
    (1, 0): "polar_supervised",
    (1, 1): "polar_cr",
}
CANONICAL_PILOT_RUNTIME = {
    "python_version": "3.12.13",
    "python_implementation": "CPython",
    "platform": "Linux-6.18.35-x86_64-with-glibc2.39",
    "machine": "x86_64",
    "numpy": "2.3.5",
    "torch": "2.14.0+cu130",
    "numpy_config_sha256": "d458c673e553c8556cf4904a3955b48e93356e7d85da83d2b28b03f28d237c4d",
    "torch_config_sha256": "5b898757e61d71ed0eecefe8d61f4e041f6caeaea1f3eb85f686a83a4fa53b9d",
}


def runtime_receipt() -> dict[str, str]:
    """Fingerprint the numerical runtime that defines the official pilot."""

    numpy_stream = io.StringIO()
    with contextlib.redirect_stdout(numpy_stream):
        np.show_config()
    return {
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "numpy_config_sha256": hashlib.sha256(
            numpy_stream.getvalue().encode("utf-8")
        ).hexdigest(),
        "torch_config_sha256": hashlib.sha256(
            torch.__config__.show().encode("utf-8")
        ).hexdigest(),
    }


def frozen_training_profile(*, steps: int, batch_size: int, warmup_steps: int) -> dict[str, Any]:
    """Return every training choice that must match the preregistration."""

    return {
        "model_classes": {
            "euclidean_supervised": "ProjectiveLinearTableOperatorRNN",
            "euclidean_cr": "ProjectiveLinearTableOperatorRNN",
            "polar_supervised": "PolarIsometricTableOperatorRNN",
            "polar_cr": "PolarIsometricTableOperatorRNN",
        },
        "arm_names": list(ARM_NAMES),
        "steps": int(steps),
        "batch_size": int(batch_size),
        "train_max_length": 4,
        "hidden_dim": 12,
        "learning_rate": 2e-3,
        "metric_learning_rate_scale": 0.10,
        "weight_decay": 1e-6,
        "grad_clip": 5.0,
        "warmup_steps": int(warmup_steps),
        "auxiliary_max_depth": 4,
        "stability_return_depths": [2, 4, 8],
        "auxiliary_contexts": 1,
        "construction_words_per_step": 4,
        "required_margin": 0.10,
        "margin_temperature": 0.05,
        "switched_gain_target": 2.0,
        "episode_seed_base": 40_000,
        "checkpoints": 11,
        "loss_weights": asdict(
            PacketClosureLossWeights(
                conformal=0.0,
                switched_gain=0.0,
            )
        ),
    }


PROFILES: dict[str, dict[str, Any]] = {
    "smoke": {
        "seeds": [53],
        "training": frozen_training_profile(steps=20, batch_size=32, warmup_steps=5),
        "eval_examples": 32,
        "eval_batch_size": 32,
        "packet_examples": 16,
        "packet_prefixes": [0, 64, 128, 256],
        "deep_depths": [32, 64],
        "null_examples": 8,
        "null_repeats": [1, 2],
        "switched_word_length": 4,
        "switched_word_count": 16,
        "switched_contexts": 2,
        "feshbach_contexts": 4,
        "intervention_examples": 32,
        "intervention_length": 8,
        "intervention_state_split": 4,
        "intervention_operator_step_zero_indexed": 3,
        "ambient_examples": 32,
        "ambient_length": 8,
        "eval_seed_base": 510_000,
    },
    "screen": {
        "seeds": [71],
        "training": frozen_training_profile(steps=1600, batch_size=128, warmup_steps=200),
        "eval_examples": 128,
        "eval_batch_size": 128,
        "packet_examples": 64,
        "packet_prefixes": [0, 64, 128, 256],
        "deep_depths": [64, 128, 256],
        "null_examples": 32,
        "null_repeats": [1, 4, 8, 16],
        "switched_word_length": 8,
        "switched_word_count": 64,
        "switched_contexts": 8,
        "feshbach_contexts": 16,
        "intervention_examples": 128,
        "intervention_length": 32,
        "intervention_state_split": 16,
        "intervention_operator_step_zero_indexed": 3,
        "ambient_examples": 128,
        "ambient_length": 32,
        "eval_seed_base": 520_000,
    },
    "pilot": {
        "seeds": [101, 211, 307],
        # Freeze the exact completed seed-71 corrected-screen workload.  An
        # attempted larger-budget calibration produced no completed result and
        # therefore did not inform this choice.
        "training": frozen_training_profile(steps=1600, batch_size=128, warmup_steps=200),
        "eval_examples": 512,
        "eval_batch_size": 256,
        "packet_examples": 128,
        "packet_prefixes": [0, 64, 128, 256],
        "deep_depths": [128, 256, 512],
        "null_examples": 64,
        "null_repeats": [1, 2, 4, 8, 16, 32],
        "switched_word_length": 8,
        "switched_word_count": 256,
        "switched_contexts": 16,
        "feshbach_contexts": 32,
        "intervention_examples": 512,
        "intervention_length": 64,
        "intervention_state_split": 32,
        "intervention_operator_step_zero_indexed": 3,
        "ambient_examples": 512,
        "ambient_length": 64,
        "eval_seed_base": 530_000,
    },
}

CONTRACT_FILENAME = "PACKET_CLOSURE_PREREGISTRATION.json"
FROZEN_GATE_THRESHOLDS: dict[str, Any] = {
    "packet_membership_minimum": 0.90,
    "packet_margin_p10_strict_minimum": 0.0,
    "null_loop_membership_minimum": 0.90,
    "switched_projective_gain_interval": [0.999, 1.001],
    "switched_defined_fraction": 1.0,
    "switched_word_accuracy_minimum": 0.95,
    "hard_polar_orthogonality_tolerance": 1e-5,
    "hard_polar_determinant_tolerance": 1e-5,
    "hard_polar_projective_log_gain_tolerance": 1e-3,
    "raw_prepolar_relative_singular_warning_floor": 1e-4,
    "d4_accuracy_by_depth": {"128": 0.98, "256": 0.90, "512": 0.75},
    "causal_patch_accuracy_minimum": 0.90,
    "causal_control_accuracy_maximum": 0.40,
    "causal_native_accuracy_minimum": 0.90,
    "causal_counterfactual_distinct_fraction": 1.0,
    "causal_defined_fraction": 1.0,
    "state_control_geometry_tolerance": 1e-5,
    "operator_control_chord_tolerance": 1e-4,
    "operator_control_orthogonality_tolerance": 1e-4,
    "operator_control_separation_strict_minimum": 1e-5,
    "ambient_native_accuracy_minimum": 0.75,
    "ambient_accuracy_drop_minimum": 0.05,
    "ambient_specificity_margin_minimum": 0.05,
    "ambient_ideal_geometry_tolerance": 1e-8,
    "ambient_applied_geometry_tolerance": 1e-6,
    "ambient_applied_rank_tolerance": 1e-5,
    "objective_margin_positive_seed_minimum": 2,
    "objective_mean_margin_difference_strict_minimum": 0.0,
    "objective_mean_membership_difference_minimum": 0.0,
    "objective_mean_null_closure_difference_minimum": 0.0,
}
FROZEN_REGISTERED_DESIGN: dict[str, Any] = {
    "author": "Komorebi P.",
    "study_status": "prospective_developmental_fresh_seed_paired_2x2",
    "arm_names": list(ARM_NAMES),
    "primary_arm": PRIMARY_ARM,
    "polar_arms": list(POLAR_ARMS),
    "cell_mapping": {
        "raw_supervised": "euclidean_supervised",
        "raw_cr": "euclidean_cr",
        "polar_supervised": "polar_supervised",
        "polar_cr": "polar_cr",
    },
    "hidden_dimension": 12,
    "anchor_plane_rank": 8,
    "ambient_complement_rank": 4,
    "execution_device": "cpu",
    "torch_intraop_threads": 1,
    "deterministic_algorithms": True,
    "official_pilot_output": "results/packet_closure_pilot",
    "pilot_replay_requires_explicit_flag": True,
    "pilot_replay_study_status": "non_evidentiary_pilot_replay",
    "canonical_pilot_runtime": CANONICAL_PILOT_RUNTIME,
    "reserved_terminal_action_groups": ["identity", "r2"],
    "heldout_continuation_count": 171,
    "heldout_includes_empty_continuation": True,
    "cr_return_only_path_depths": [2, 4, 8],
    "cr_return_only_word_count": 6,
    "evaluation_families": ["d4", "c8", "mixed_cycle"],
    "state_controls": [
        "unit_sphere_recipient_angle_matched_random_tangent",
        "wrong_reachable_same_prefix_state",
    ],
    "operator_controls": [
        "relative_conjugacy_matched_orthogonal",
        (
            "independent_context_balanced_slot_with_exact_original_and_alternate_"
            "table_collision_exclusion"
        ),
    ],
    "state_intervention_position": "profile.intervention_state_split",
    "operator_intervention_position_zero_indexed": 3,
    "gate_thresholds": FROZEN_GATE_THRESHOLDS,
}


def contract_source_files(root: Path = ROOT) -> list[Path]:
    """Return the non-self-referential source set sealed by the contract."""

    return [
        path
        for path in source_files(root)
        if path.as_posix() != CONTRACT_FILENAME
    ]


def contract_source_digest(root: Path = ROOT) -> str:
    return tree_digest(root, contract_source_files(root))


def contract_requirements(source_digest: str) -> dict[str, Any]:
    """Return the exact machine-checked core of the v0.4 contract."""

    return {
        "schema": f"{SCHEMA_PREFIX}.contract.v1",
        "version": VERSION,
        "author": "Komorebi P.",
        "status": "frozen_before_pilot",
        "study_status": "prospective_developmental_fresh_seed_paired_2x2",
        "implementation_source_digest": str(source_digest),
        "profiles": PROFILES,
        "registered_design": FROZEN_REGISTERED_DESIGN,
    }


def validate_contract(
    contract: Mapping[str, Any],
    profile: str,
    config: Mapping[str, Any],
    source_digest: str,
) -> dict[str, Any]:
    """Fail closed unless every frozen implementation field agrees exactly."""

    requirements = contract_requirements(source_digest)
    if not isinstance(contract, Mapping):
        return {
            "top_level_schema_valid": False,
            "schema_valid": False,
            "version_valid": False,
            "author_valid": False,
            "status_valid": False,
            "study_status_valid": False,
            "source_digest_valid": False,
            "profiles_valid": False,
            "profile_valid": False,
            "registered_design_valid": False,
            "valid": False,
        }
    checks = {
        "top_level_schema_valid": set(contract) == set(requirements),
        "schema_valid": contract.get("schema") == requirements["schema"],
        "version_valid": contract.get("version") == requirements["version"],
        "author_valid": contract.get("author") == requirements["author"],
        "status_valid": contract.get("status") == requirements["status"],
        "study_status_valid": (
            contract.get("study_status") == requirements["study_status"]
        ),
        "source_digest_valid": (
            contract.get("implementation_source_digest")
            == requirements["implementation_source_digest"]
        ),
        "profiles_valid": strict_json_equal(
            contract.get("profiles"), requirements["profiles"]
        ),
        "profile_valid": strict_json_equal(
            contract.get("profiles", {}).get(profile), dict(config)
        ),
        "registered_design_valid": (
            strict_json_equal(
                contract.get("registered_design"), requirements["registered_design"]
            )
        ),
    }
    return {**checks, "valid": all(checks.values())}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, value: Any) -> None:
    """Atomically write strict JSON, replacing non-finite diagnostics by null."""

    payload = json_ready(value)
    rendered = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(rendered, encoding="utf-8")
    os.replace(temporary, path)


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def _strict_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject duplicate object keys in preregistration JSON."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def derive_seed(base: int, *parts: object) -> int:
    encoded = json.dumps([int(base), *parts], sort_keys=True, separators=(",", ":")).encode("utf-8")
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "little") % (2**31 - 1)


def tensor_digest(tensor: torch.Tensor) -> str:
    local = tensor.detach().to(device="cpu").contiguous()
    digest = hashlib.sha256()
    digest.update(str(local.dtype).encode("ascii"))
    digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
    digest.update(local.numpy().tobytes())
    return digest.hexdigest()


def metric_for(model: torch.nn.Module) -> torch.Tensor:
    candidate = getattr(model, "invariant_metric", None)
    if candidate is None:
        hidden_dim = int(getattr(model, "hidden_dim"))
        reference = next(model.parameters())
        return torch.eye(hidden_dim, dtype=reference.dtype, device=reference.device)
    metric = candidate() if callable(candidate) else candidate
    if not isinstance(metric, torch.Tensor):
        raise TypeError("model invariant_metric did not resolve to a tensor")
    return metric


def numeric_summary(values: torch.Tensor | Iterable[float]) -> dict[str, Any]:
    if isinstance(values, torch.Tensor):
        tensor = values.detach().to(device="cpu", dtype=torch.float64).reshape(-1)
    else:
        tensor = torch.tensor(tuple(values), dtype=torch.float64)
    finite = tensor[torch.isfinite(tensor)]
    if not finite.numel():
        return {
            "count": int(tensor.numel()),
            "finite_count": 0,
            "minimum": None,
            "p10": None,
            "median": None,
            "mean": None,
            "p90": None,
            "maximum": None,
        }
    return {
        "count": int(tensor.numel()),
        "finite_count": int(finite.numel()),
        "minimum": float(finite.min()),
        "p10": float(torch.quantile(finite, 0.10)),
        "median": float(torch.median(finite)),
        "mean": float(finite.mean()),
        "p90": float(torch.quantile(finite, 0.90)),
        "maximum": float(finite.max()),
    }


def config_payload(config: PacketClosureTrainConfig) -> dict[str, Any]:
    return asdict(config)


def training_config_for(
    profile_config: Mapping[str, Any],
    *,
    seed: int,
    device: torch.device,
) -> PacketClosureTrainConfig:
    frozen = dict(profile_config["training"])
    if tuple(frozen["arm_names"]) != ARM_NAMES:
        raise ValueError("frozen arm_names do not match the live arm registry")
    expected_model_classes = {
        "euclidean_supervised": "ProjectiveLinearTableOperatorRNN",
        "euclidean_cr": "ProjectiveLinearTableOperatorRNN",
        "polar_supervised": "PolarIsometricTableOperatorRNN",
        "polar_cr": "PolarIsometricTableOperatorRNN",
    }
    if frozen["model_classes"] != expected_model_classes:
        raise ValueError("frozen model_classes do not match the primary raw/polar panel")
    weights = PacketClosureLossWeights(**frozen["loss_weights"])
    return PacketClosureTrainConfig(
        seed=int(seed),
        steps=int(frozen["steps"]),
        batch_size=int(frozen["batch_size"]),
        train_max_length=int(frozen["train_max_length"]),
        hidden_dim=int(frozen["hidden_dim"]),
        learning_rate=float(frozen["learning_rate"]),
        metric_learning_rate_scale=float(frozen["metric_learning_rate_scale"]),
        weight_decay=float(frozen["weight_decay"]),
        grad_clip=float(frozen["grad_clip"]),
        warmup_steps=int(frozen["warmup_steps"]),
        auxiliary_max_depth=int(frozen["auxiliary_max_depth"]),
        stability_return_depths=tuple(
            int(value) for value in frozen["stability_return_depths"]
        ),
        auxiliary_contexts=int(frozen["auxiliary_contexts"]),
        construction_words_per_step=int(frozen["construction_words_per_step"]),
        required_margin=float(frozen["required_margin"]),
        margin_temperature=float(frozen["margin_temperature"]),
        switched_gain_target=float(frozen["switched_gain_target"]),
        episode_seed_base=int(frozen["episode_seed_base"]),
        checkpoints=int(frozen["checkpoints"]),
        device=str(device),
        weights=weights,
    )


def load_contract(profile: str, config: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    path = ROOT / CONTRACT_FILENAME
    if not path.exists():
        return {}, {
            "available": False,
            "valid": False,
            "path": path.name,
            "reason": "missing preregistration contract",
        }
    contract = json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON constant: {value}")
        ),
        object_pairs_hook=_strict_json_object,
    )
    validation = validate_contract(
        contract,
        profile,
        config,
        contract_source_digest(ROOT),
    )
    return contract, {
        "available": True,
        "path": path.name,
        "sha256": file_sha256(path),
        **validation,
    }


def make_eval_banks(config: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Materialize all behavioral banks after the checkpoint seal."""

    base = int(config["eval_seed_base"])
    packet_batches = {
        str(prefix): EpisodeGenerator(derive_seed(base, "packet", prefix)).sample(
            int(config["packet_examples"]), int(prefix), family="d4"
        )
        for prefix in config["packet_prefixes"]
    }
    deep_batches: dict[str, dict[str, EpisodeBatch]] = {}
    for depth in config["deep_depths"]:
        deep_batches[str(depth)] = {
            family: EpisodeGenerator(derive_seed(base, "deep", family, depth)).sample(
                int(config["eval_examples"]), int(depth), family=family
            )
            for family in ("d4", "c8", "mixed_cycle")
        }
    null_batch = EpisodeGenerator(derive_seed(base, "null")).sample(
        int(config["null_examples"]), 0, family="d4"
    )
    switched_batch = EpisodeGenerator(derive_seed(base, "switched")).sample(
        int(config["switched_contexts"]), 0, family="d4"
    )
    feshbach_batch = EpisodeGenerator(derive_seed(base, "feshbach")).sample(
        int(config["feshbach_contexts"]), 0, family="d4"
    )
    ambient_batches = {
        family: EpisodeGenerator(derive_seed(base, "ambient", family)).sample(
            int(config["ambient_examples"]), int(config["ambient_length"]), family=family
        )
        for family in ("d4", "c8", "mixed_cycle")
    }
    intervention_batch = EpisodeGenerator(derive_seed(base, "intervention")).sample(
        int(config["intervention_examples"]),
        int(config["intervention_length"]),
        family="d4",
    )
    intervention_operator_control_batch = EpisodeGenerator(
        derive_seed(base, "intervention_operator_control")
    ).sample(
        int(config["intervention_examples"]),
        int(config["intervention_length"]),
        family="d4",
    )
    banks = {
        "packet": packet_batches,
        "deep": deep_batches,
        "null": null_batch,
        "switched": switched_batch,
        "feshbach": feshbach_batch,
        "ambient": ambient_batches,
        "intervention": intervention_batch,
        "intervention_operator_control": intervention_operator_control_batch,
    }
    receipts: dict[str, Any] = {
        "packet": {key: episode_bank_receipts(value) for key, value in packet_batches.items()},
        "deep": {
            depth: {family: episode_bank_receipts(batch) for family, batch in families.items()}
            for depth, families in deep_batches.items()
        },
        "null": episode_bank_receipts(null_batch),
        "switched": episode_bank_receipts(switched_batch),
        "feshbach": episode_bank_receipts(feshbach_batch),
        "ambient": {
            family: episode_bank_receipts(batch) for family, batch in ambient_batches.items()
        },
        "intervention": episode_bank_receipts(intervention_batch),
        "intervention_operator_control": episode_bank_receipts(
            intervention_operator_control_batch
        ),
    }
    contracts = {
        "packet": {key: episode_contract(value) for key, value in packet_batches.items()},
        "deep": {
            depth: {family: episode_contract(batch) for family, batch in families.items()}
            for depth, families in deep_batches.items()
        },
        "null": episode_contract(null_batch),
        "switched": episode_contract(switched_batch),
        "feshbach": episode_contract(feshbach_batch),
        "ambient": {
            family: episode_contract(batch) for family, batch in ambient_batches.items()
        },
        "intervention": episode_contract(intervention_batch),
        "intervention_operator_control": episode_contract(
            intervention_operator_control_batch
        ),
    }
    receipts["contracts"] = contracts
    return banks, receipts


def validate_eval_episode_contracts(
    eval_bank: Mapping[str, Any],
    config: Mapping[str, Any],
) -> bool:
    """Match every evaluation contract to the registered grid and algebra family."""

    contracts = eval_bank.get("episode_receipts", {}).get("contracts", {})
    if not isinstance(contracts, Mapping):
        return False

    required_truths = (
        "intermediates_exact",
        "target_exact",
        "canonical_visible_slots_exact",
        "tables_exact_one_hot_maps",
        "tables_finite",
        "maps_are_permutations",
        "phi_is_permutation",
        "visible_slots_are_permutations",
        "canonical_family_realization_exact",
        "shapes_exact",
        "values_in_range",
    )

    def exact(row: Any, *, family: str, contexts: int, length: int) -> bool:
        return bool(
            isinstance(row, Mapping)
            and row.get("family") == family
            and type(row.get("contexts")) is int
            and row.get("contexts") == int(contexts)
            and type(row.get("length")) is int
            and row.get("length") == int(length)
            and all(row.get(key) is True for key in required_truths)
        )

    packet = contracts.get("packet")
    expected_prefixes = {str(int(value)) for value in config["packet_prefixes"]}
    if not isinstance(packet, Mapping) or set(packet) != expected_prefixes:
        return False
    if any(
        not exact(
            packet[str(prefix)],
            family="d4",
            contexts=int(config["packet_examples"]),
            length=int(prefix),
        )
        for prefix in config["packet_prefixes"]
    ):
        return False

    deep = contracts.get("deep")
    expected_depths = {str(int(value)) for value in config["deep_depths"]}
    fixed_families = {"d4", "c8", "mixed_cycle"}
    if not isinstance(deep, Mapping) or set(deep) != expected_depths:
        return False
    for depth in config["deep_depths"]:
        rows = deep.get(str(depth))
        if not isinstance(rows, Mapping) or set(rows) != fixed_families:
            return False
        if any(
            not exact(
                rows[family],
                family=family,
                contexts=int(config["eval_examples"]),
                length=int(depth),
            )
            for family in fixed_families
        ):
            return False

    ambient = contracts.get("ambient")
    if not isinstance(ambient, Mapping) or set(ambient) != fixed_families:
        return False
    if any(
        not exact(
            ambient[family],
            family=family,
            contexts=int(config["ambient_examples"]),
            length=int(config["ambient_length"]),
        )
        for family in fixed_families
    ):
        return False

    singleton_specs = {
        "null": ("d4", int(config["null_examples"]), 0),
        "switched": ("d4", int(config["switched_contexts"]), 0),
        "feshbach": ("d4", int(config["feshbach_contexts"]), 0),
        "intervention": (
            "d4",
            int(config["intervention_examples"]),
            int(config["intervention_length"]),
        ),
        "intervention_operator_control": (
            "d4",
            int(config["intervention_examples"]),
            int(config["intervention_length"]),
        ),
    }
    expected_top_level = {"packet", "deep", "ambient", *singleton_specs}
    if set(contracts) != expected_top_level:
        return False
    return all(
        exact(contracts[name], family=family, contexts=contexts, length=length)
        for name, (family, contexts, length) in singleton_specs.items()
    )


def independent_cross_context_bank_contract(
    primary: EpisodeBatch,
    control: EpisodeBatch,
    *,
    operator_step: int,
) -> dict[str, Any]:
    """Audit the model-independent noncollision rule used by the control."""

    examples = int(primary.start.shape[0])
    if int(control.start.shape[0]) != examples:
        raise ValueError("cross-context banks must have equal row counts")
    if not 0 <= int(operator_step) < int(primary.op_slots.shape[1]):
        raise ValueError("operator intervention step is outside the primary bank")
    rows = torch.arange(examples)
    original_slots = primary.op_slots[:, int(operator_step)]
    alternate_slots = 1 - original_slots
    original_tables = primary.maps[rows, original_slots]
    alternate_tables = primary.maps[rows, alternate_slots]
    original_collisions = (control.maps == original_tables[:, None, :]).all(dim=-1)
    alternate_collisions = (control.maps == alternate_tables[:, None, :]).all(dim=-1)
    excluded = original_collisions | alternate_collisions
    base_choices = rows % int(control.maps.shape[1])
    base_original_collision = original_collisions[rows, base_choices]
    base_alternate_collision = alternate_collisions[rows, base_choices]
    selected_choices = torch.where(
        excluded[rows, base_choices], 1 - base_choices, base_choices
    )
    selected_original_collision = original_collisions[rows, selected_choices]
    selected_alternate_collision = alternate_collisions[rows, selected_choices]
    if bool((selected_original_collision | selected_alternate_collision).any()):
        raise RuntimeError(
            "independent cross-context control has no slot outside both "
            "primary operator tables"
        )
    return {
        "selection_policy": (
            "balanced_slot_by_bank_row_then_flip_only_on_exact_original_or_"
            "alternate_visible_table_collision"
        ),
        "examples": examples,
        "operator_step_zero_indexed": int(operator_step),
        "base_original_table_collision_count": int(base_original_collision.sum()),
        "base_alternate_table_collision_count": int(base_alternate_collision.sum()),
        "selected_original_table_collision_count": int(
            selected_original_collision.sum()
        ),
        "selected_alternate_table_collision_count": int(
            selected_alternate_collision.sum()
        ),
        "selected_slot_counts": [
            int((selected_choices == slot).sum())
            for slot in range(int(control.maps.shape[1]))
        ],
    }


def validate_cross_context_control_contract(
    record: Any,
    config: Mapping[str, Any],
) -> bool:
    """Fail closed on malformed or colliding independent-control receipts."""

    if not isinstance(record, Mapping):
        return False
    if set(record) != {
        "selection_policy",
        "examples",
        "operator_step_zero_indexed",
        "base_original_table_collision_count",
        "base_alternate_table_collision_count",
        "selected_original_table_collision_count",
        "selected_alternate_table_collision_count",
        "selected_slot_counts",
    }:
        return False
    examples = record.get("examples")
    step = record.get("operator_step_zero_indexed")
    base_original_collisions = record.get("base_original_table_collision_count")
    base_alternate_collisions = record.get("base_alternate_table_collision_count")
    selected_original_collisions = record.get(
        "selected_original_table_collision_count"
    )
    selected_alternate_collisions = record.get(
        "selected_alternate_table_collision_count"
    )
    slot_counts = record.get("selected_slot_counts")
    if not (
        record.get("selection_policy")
        == (
            "balanced_slot_by_bank_row_then_flip_only_on_exact_original_or_"
            "alternate_visible_table_collision"
        )
        and type(examples) is int
        and examples == int(config["intervention_examples"])
        and type(step) is int
        and step == int(config["intervention_operator_step_zero_indexed"])
        and type(base_original_collisions) is int
        and 0 <= base_original_collisions <= examples
        and type(base_alternate_collisions) is int
        and 0 <= base_alternate_collisions <= examples
        and base_original_collisions + base_alternate_collisions <= examples
        and type(selected_original_collisions) is int
        and selected_original_collisions == 0
        and type(selected_alternate_collisions) is int
        and selected_alternate_collisions == 0
        and isinstance(slot_counts, list)
        and len(slot_counts) == 2
        and all(type(value) is int and value >= 0 for value in slot_counts)
    ):
        return False
    return sum(slot_counts) == examples


def _canonical_codes(model: torch.nn.Module, batch: EpisodeBatch) -> torch.Tensor:
    device = next(model.parameters()).device
    working = batch.to(device)
    trace = model.run(working.tables, working.op_slots, working.start)
    if trace.operator_codes is None or trace.operator_codes.ndim != 4:
        raise ValueError("exact Feshbach audit requires square matrix operator codes")
    rows = torch.arange(working.start.shape[0], device=device)
    return torch.stack(
        tuple(
            trace.operator_codes[rows, working.canonical_to_slot[:, action]]
            for action in range(working.canonical_to_slot.shape[1])
        ),
        dim=1,
    )


def _operator_word_product(codes: torch.Tensor, word: Sequence[int]) -> torch.Tensor:
    batch, _, dimension, _ = codes.shape
    product = torch.eye(dimension, dtype=codes.dtype, device=codes.device).expand(batch, -1, -1)
    for action in word:
        product = codes[:, int(action)] @ product
    return product


def exact_feshbach_audit(model: torch.nn.Module, batch: EpisodeBatch) -> dict[str, Any]:
    """Evaluate an exact rank-8/rank-4 anchor split without a soft-null claim."""

    model.eval()
    device = next(model.parameters()).device
    with torch.inference_mode():
        metric = metric_for(model)
        states = torch.arange(N_STATES, device=device)
        anchors = model.initial_hidden(states)
        plane = g_orthogonal_anchor_projector(anchors, metric)
        raw_codes = _canonical_codes(model, batch)
        chart = torch.linalg.cholesky(metric).transpose(-1, -2)
        inverse_chart = torch.linalg.inv(chart)
        whitened = chart @ raw_codes @ inverse_chart
        projective_scale = torch.linalg.matrix_norm(
            whitened, ord="fro", dim=(-2, -1)
        ) / math.sqrt(raw_codes.shape[-1])
        codes = raw_codes / projective_scale.clamp_min(1e-12)[..., None, None]
        blocks = feshbach_block_diagnostics(codes, plane, metric)

        # U_g D_v V_h is evaluated on every generator pair and every middle
        # word through length three.  This is an exact P/Q decomposition, not
        # a statement that Q is an observational nullspace.
        middle_words = tuple(
            word
            for length in range(0, 4)
            for word in itertools.product(range(codes.shape[1]), repeat=length)
        )
        return_rows: list[torch.Tensor] = []
        submultiplicative_rows: list[torch.Tensor] = []
        energy_rows: list[torch.Tensor] = []
        for g, h, word in itertools.product(range(codes.shape[1]), range(codes.shape[1]), middle_words):
            middle = _operator_word_product(codes, word)
            returned = feshbach_return_diagnostics(
                codes[:, g], middle, codes[:, h], plane, metric
            )
            return_rows.append(returned.full_product_fraction)
            submultiplicative_rows.append(returned.submultiplicative_fraction)
            energy_rows.append(returned.return_energy)

        conditioning = metric_condition_diagnostics(metric)
        return_fraction = torch.stack(return_rows, dim=1)
        submultiplicative = torch.stack(submultiplicative_rows, dim=1)
        return_energy = torch.stack(energy_rows, dim=1)
        return {
            "exact_anchor_plane": {
                "ambient_dimension": plane.ambient_dimension,
                "anchor_count": plane.anchor_count,
                "retained_rank": plane.rank,
                "nuisance_rank": plane.ambient_dimension - plane.rank,
                "effective_trace": float(plane.effective_trace),
                "complement_effective_trace": float(plane.complement_effective_trace),
                "idempotence_error": float(plane.idempotence_error),
                "metric_self_adjoint_error": float(plane.metric_self_adjoint_error),
            },
            "metric": {
                "positive_definite": bool(conditioning.positive_definite),
                "condition_number": float(conditioning.condition_number),
                "determinant": float(conditioning.determinant),
                "eigenvalues": conditioning.eigenvalues.detach().cpu().tolist(),
            },
            "generator_blocks": {
                "projective_scale": numeric_summary(projective_scale),
                "p_to_p_fraction": numeric_summary(blocks.p_to_p_fraction),
                "p_to_q_fraction": numeric_summary(blocks.p_to_q_fraction),
                "q_to_p_fraction": numeric_summary(blocks.q_to_p_fraction),
                "q_to_q_fraction": numeric_summary(blocks.q_to_q_fraction),
                "total_energy": numeric_summary(blocks.total_energy),
            },
            "delayed_return": {
                "middle_word_maximum_length": 3,
                "middle_word_count": len(middle_words),
                "generator_pair_count": int(codes.shape[1] ** 2),
                "full_product_fraction": numeric_summary(return_fraction),
                "submultiplicative_fraction": numeric_summary(submultiplicative),
                "return_energy": numeric_summary(return_energy),
            },
        }


def evaluate_model(
    model: torch.nn.Module,
    config: Mapping[str, Any],
    banks: Mapping[str, Any],
    audit_plan: Any,
    switched_words: Sequence[Sequence[int]],
    *,
    arm: str,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    transitions = torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long)
    packet = {
        prefix: evaluate_heldout_packet(
            model,
            batch,
            audit_plan,
            transitions,
            boundary_tolerance=0.0,
            max_suffixes=None,
        ).to_dict()
        for prefix, batch in banks["packet"].items()
    }
    deep = {
        depth: evaluate_structured_deep_accuracy(model, batches).to_dict()
        for depth, batches in banks["deep"].items()
    }
    null_loop = evaluate_null_loop_retention(
        model,
        banks["null"],
        audit_plan,
        transitions,
        D4_RELATIONS,
        repeats=config["null_repeats"],
        boundary_tolerance=0.0,
        max_suffixes=None,
    ).to_dict()
    switched = evaluate_sampled_switched_gain(
        model,
        banks["switched"],
        switched_words,
        transitions,
        episode_limit=int(config["switched_contexts"]),
        max_words=None,
    ).to_dict()
    feshbach = exact_feshbach_audit(model, banks["feshbach"])
    family_transitions = {
        family: torch.from_numpy(canonical_maps(family)).to(dtype=torch.long)
        for family in ("d4", "c8", "mixed_cycle")
    }
    if arm in POLAR_ARMS:
        polar_geometry = {
            "available": True,
            **evaluate_hard_polar_geometry(
                model,
                banks["ambient"],
                {family: switched_words for family in banks["ambient"]},
                family_transitions,
                switched_episode_limit=int(config["switched_contexts"]),
                max_switched_words=None,
                orthogonality_tolerance=FROZEN_GATE_THRESHOLDS[
                    "hard_polar_orthogonality_tolerance"
                ],
                determinant_magnitude_tolerance=FROZEN_GATE_THRESHOLDS[
                    "hard_polar_determinant_tolerance"
                ],
                projective_log_gain_tolerance=FROZEN_GATE_THRESHOLDS[
                    "hard_polar_projective_log_gain_tolerance"
                ],
                raw_relative_singular_floor=FROZEN_GATE_THRESHOLDS[
                    "raw_prepolar_relative_singular_warning_floor"
                ],
            ).to_dict(),
        }
    else:
        polar_geometry = {
            "available": False,
            "reason": "raw operator arm; hard-polar geometry assay is not applicable",
        }
    ambient_causality = {
        family: evaluate_ambient_complement_causality(
            model,
            batch,
            random_seed=derive_seed(
                int(config["eval_seed_base"]), "ambient_random_control", family
            ),
            random_energy_match_tolerance=FROZEN_GATE_THRESHOLDS[
                "ambient_applied_geometry_tolerance"
            ],
            applied_rank_tolerance=FROZEN_GATE_THRESHOLDS[
                "ambient_applied_rank_tolerance"
            ],
            minimum_accuracy_drop=FROZEN_GATE_THRESHOLDS[
                "ambient_accuracy_drop_minimum"
            ],
            specificity_margin=FROZEN_GATE_THRESHOLDS[
                "ambient_specificity_margin_minimum"
            ],
            native_accuracy_floor=FROZEN_GATE_THRESHOLDS[
                "ambient_native_accuracy_minimum"
            ],
        ).to_dict()
        for family, batch in banks["ambient"].items()
    }
    length = int(config["intervention_length"])
    causal = intervention_metrics(
        model,
        int(config["intervention_examples"]),
        int(config["eval_batch_size"]),
        derive_seed(int(config["eval_seed_base"]), "intervention"),
        device,
        length=length,
        split=int(config["intervention_state_split"]),
        operator_step=int(config["intervention_operator_step_zero_indexed"]),
        episode_batch=banks["intervention"],
        operator_control_batch=banks["intervention_operator_control"],
        control_seed=derive_seed(
            int(config["eval_seed_base"]), "intervention_controls"
        ),
    )
    return {
        "heldout_packet_by_prefix": packet,
        "structured_deep_by_depth": deep,
        "null_loop_retention": null_loop,
        "switched_gain": switched,
        "exact_feshbach": feshbach,
        "hard_polar_geometry": polar_geometry,
        "ambient_complement_causality": ambient_causality,
        "causal_interventions": causal,
        "evaluation_seed": seed,
    }


def _finite(value: Any) -> float | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value)):
        return float(value)
    return None


def strict_json_equal(actual: Any, expected: Any) -> bool:
    """Compare JSON-shaped values without Python's bool/int/float coercions."""

    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return set(actual) == set(expected) and all(
            strict_json_equal(actual[key], expected[key]) for key in expected
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            strict_json_equal(left, right)
            for left, right in zip(actual, expected)
        )
    return bool(actual == expected)


def _strict_fraction(
    value: Any,
    *,
    denominator: int | None = None,
    allow_none: bool = False,
) -> bool:
    """Validate a serialized fraction and, when known, its integer count origin."""

    if value is None:
        return allow_none
    if type(value) is not float or not math.isfinite(value) or not 0.0 <= value <= 1.0:
        return False
    if denominator is None:
        return True
    if type(denominator) is not int or denominator <= 0:
        return False
    scaled = value * denominator
    return abs(scaled - round(scaled)) <= 1e-9


def _strict_nonnegative_finite(value: Any) -> bool:
    return type(value) is float and math.isfinite(value) and value >= 0.0


def _strict_numeric_summary(
    summary: Any,
    *,
    expected_count: int,
    require_all_finite: bool = False,
) -> bool:
    """Validate the exact schema and internal ordering of a numeric summary."""

    expected_keys = {
        "count",
        "finite_count",
        "minimum",
        "p10",
        "median",
        "mean",
        "p90",
        "maximum",
    }
    if not isinstance(summary, Mapping) or set(summary) != expected_keys:
        return False
    count = summary.get("count")
    finite_count = summary.get("finite_count")
    if (
        type(count) is not int
        or type(finite_count) is not int
        or count != expected_count
        or not 0 <= finite_count <= count
        or (require_all_finite and finite_count != count)
    ):
        return False
    statistic_keys = ("minimum", "p10", "median", "mean", "p90", "maximum")
    if finite_count == 0:
        return all(summary.get(key) is None for key in statistic_keys)
    values = [summary.get(key) for key in statistic_keys]
    if any(type(value) is not float or not math.isfinite(value) for value in values):
        return False
    minimum, p10, median, mean, p90, maximum = (float(value) for value in values)
    # torch.median returns the lower middle order statistic for an even count,
    # whereas quantile interpolates; p10 may therefore exceed that median at n=2.
    return (
        minimum <= p10 <= p90 <= maximum
        and minimum <= median <= maximum
        and minimum <= mean <= maximum
    )


def _complete_summary_value(summary: Any, key: str) -> float | None:
    """Return a summary statistic only when its entire registered bank is finite."""

    if not isinstance(summary, Mapping):
        return None
    count = summary.get("count")
    finite_count = summary.get("finite_count")
    if (
        type(count) is not int
        or type(finite_count) is not int
        or count <= 0
        or finite_count != count
    ):
        return None
    return _finite(summary.get(key))


def _packet_endpoint_scalars(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, float | None]:
    """Extract packet membership and margin independently over the frozen grid."""

    rows = evaluation.get("heldout_packet_by_prefix")
    expected_prefixes = {str(value) for value in config["packet_prefixes"]}
    if not isinstance(rows, Mapping) or set(rows) != expected_prefixes:
        return {"packet_membership": None, "packet_margin_p10": None}
    memberships: list[float] = []
    margins: list[float] = []
    membership_valid = True
    margin_valid = True
    examples = int(config["packet_examples"])
    for prefix in sorted(expected_prefixes, key=int):
        row = rows.get(prefix)
        if not isinstance(row, Mapping):
            return {"packet_membership": None, "packet_margin_p10": None}
        membership = row.get("strict_membership_fraction")
        if _strict_fraction(membership, denominator=examples):
            memberships.append(float(membership))
        else:
            membership_valid = False
        margin = _complete_summary_value(row.get("suffix_minimum_margin"), "p10")
        if margin is None:
            margin_valid = False
        else:
            margins.append(float(margin))
        groups = row.get("relation_groups")
        if not isinstance(groups, list) or len(groups) != 2:
            return {"packet_membership": None, "packet_margin_p10": None}
        for group in groups:
            if not isinstance(group, Mapping):
                return {"packet_membership": None, "packet_margin_p10": None}
            membership = group.get("membership_fraction")
            if _strict_fraction(membership, denominator=examples):
                memberships.append(float(membership))
            else:
                membership_valid = False
            margin = _complete_summary_value(group.get("minimum_margin"), "p10")
            if margin is None:
                margin_valid = False
            else:
                margins.append(float(margin))
    return {
        "packet_membership": min(memberships) if membership_valid and memberships else None,
        "packet_margin_p10": min(margins) if margin_valid and margins else None,
    }


def _null_endpoint_scalars(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, float | None]:
    """Extract null endpoints, treating zero-baseline conditional rates correctly."""

    result = evaluation.get("null_loop_retention")
    if not isinstance(result, Mapping):
        return {
            "null_closure": None,
            "null_baseline_membership": None,
            "null_conditional_retention": None,
            "null_post_membership": None,
        }
    baseline = result.get("baseline")
    relations = result.get("relations")
    if (
        not isinstance(baseline, Mapping)
        or not isinstance(relations, Mapping)
        or set(relations) != set(D4_RELATIONS)
    ):
        return {
            "null_closure": None,
            "null_baseline_membership": None,
            "null_conditional_retention": None,
            "null_post_membership": None,
        }
    examples = int(config["null_examples"])
    baseline_membership = baseline.get("strict_membership_fraction")
    if not _strict_fraction(baseline_membership, denominator=examples):
        return {
            "null_closure": None,
            "null_baseline_membership": None,
            "null_conditional_retention": None,
            "null_post_membership": None,
        }
    baseline_value = float(baseline_membership)
    baseline_members = round(baseline_value * examples)
    expected_repeats = {str(value) for value in config["null_repeats"]}
    conditional_values: list[float] = []
    post_values: list[float] = []
    conditional_valid = True
    post_valid = True
    for relation in relations.values():
        by_repeat = relation.get("by_repeat") if isinstance(relation, Mapping) else None
        if not isinstance(by_repeat, Mapping) or set(by_repeat) != expected_repeats:
            return {
                "null_closure": None,
                "null_baseline_membership": baseline_value,
                "null_conditional_retention": None,
                "null_post_membership": None,
            }
        for repeat in sorted(expected_repeats, key=int):
            row = by_repeat.get(repeat)
            if not isinstance(row, Mapping):
                conditional_valid = False
                post_valid = False
                continue
            post = row.get("strict_membership_fraction")
            if _strict_fraction(post, denominator=examples):
                post_values.append(float(post))
            else:
                post_valid = False
            conditional = row.get("conditional_retention_fraction")
            if baseline_members == 0:
                if conditional is not None:
                    conditional_valid = False
            elif _strict_fraction(conditional, denominator=baseline_members):
                conditional_values.append(float(conditional))
            else:
                conditional_valid = False
    conditional_minimum = (
        min(conditional_values)
        if baseline_members > 0 and conditional_valid and conditional_values
        else None
    )
    post_minimum = min(post_values) if post_valid and post_values else None
    closure_values: list[float] = [baseline_value]
    if baseline_members > 0:
        if conditional_minimum is None:
            return {
                "null_closure": None,
                "null_baseline_membership": baseline_value,
                "null_conditional_retention": None,
                "null_post_membership": post_minimum,
            }
        closure_values.append(conditional_minimum)
    elif not conditional_valid:
        return {
            "null_closure": None,
            "null_baseline_membership": baseline_value,
            "null_conditional_retention": None,
            "null_post_membership": post_minimum,
        }
    if post_minimum is None:
        return {
            "null_closure": None,
            "null_baseline_membership": baseline_value,
            "null_conditional_retention": conditional_minimum,
            "null_post_membership": None,
        }
    closure_values.append(post_minimum)
    return {
        "null_closure": min(closure_values),
        "null_baseline_membership": baseline_value,
        "null_conditional_retention": conditional_minimum,
        "null_post_membership": post_minimum,
    }


def _scalar_metrics_unchecked(evaluation: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, float | None]:
    final_depth = str(max(config["deep_depths"]))
    packet_scalars = _packet_endpoint_scalars(evaluation, config)
    null_scalars = _null_endpoint_scalars(evaluation, config)
    deep = evaluation["structured_deep_by_depth"][final_depth]
    deep_finite_fractions = [
        deep["per_family"][family].get("finite_fraction")
        for family in ("d4", "c8", "mixed_cycle")
    ]
    all_deep_outputs_finite = all_finite(deep_finite_fractions) and all(
        float(value) == 1.0 for value in deep_finite_fractions
    )
    d4_accuracy = (
        deep["per_family"]["d4"]["accuracy"]
        if _finite(deep["per_family"]["d4"].get("finite_fraction")) == 1.0
        else None
    )
    cross_family_values = [
        deep["per_family"][family]["accuracy"]
        for family in ("c8", "mixed_cycle")
    ]
    cross_family_minimum = (
        min(float(value) for value in cross_family_values)
        if all_finite(cross_family_values)
        and all(
            _finite(deep["per_family"][family].get("finite_fraction")) == 1.0
            for family in ("c8", "mixed_cycle")
        )
        else None
    )
    switched = evaluation["switched_gain"]
    causal = evaluation["causal_interventions"]
    feshbach = evaluation["exact_feshbach"]
    polar_geometry = evaluation.get("hard_polar_geometry", {})
    ambient = evaluation.get("ambient_complement_causality", {})
    ambient_rows = list(ambient.values())
    ambient_q_drops = [
        float(row["performance_drops"]["midpoint_q_ablation"])
        for row in ambient_rows
    ]
    ambient_specific_drops = [
        float(row["performance_drops"]["q_specific_excess_over_random"])
        for row in ambient_rows
    ]
    ambient_native_accuracies = [
        float(row["conditions"]["native"]["accuracy"])
        for row in ambient_rows
    ]
    ambient_support = [
        bool(row["attribution"]["supports_specific_ambient_attribution"])
        for row in ambient_rows
    ]
    polar_aggregate = polar_geometry.get("aggregate", {})
    state_patch = _finite(causal.get("state_patch_transition_accuracy"))
    random_state_patch = _finite(
        causal.get("random_state_patch_transition_accuracy")
    )
    angle_state_control = _finite(
        causal.get("angle_matched_state_control_transition_accuracy")
    )
    reachable_state_control = _finite(
        causal.get("reachable_state_control_transition_accuracy")
    )
    operator_patch = _finite(causal.get("operator_patch_transition_accuracy"))
    random_operator_patch = _finite(
        causal.get("random_operator_patch_transition_accuracy")
    )
    conjugacy_operator_control = _finite(
        causal.get("relative_conjugacy_operator_control_transition_accuracy")
    )
    cross_context_operator_control = _finite(
        causal.get("cross_context_operator_control_transition_accuracy")
    )
    state_margin_values = [state_patch, angle_state_control, reachable_state_control]
    operator_margin_values = [
        operator_patch,
        conjugacy_operator_control,
        cross_context_operator_control,
    ]
    return {
        "packet_membership": packet_scalars["packet_membership"],
        "packet_margin_p10": packet_scalars["packet_margin_p10"],
        "structured_minimum_accuracy": (
            _finite(deep["minimum_family_accuracy"])
            if all_deep_outputs_finite
            else None
        ),
        "d4_accuracy": _finite(d4_accuracy),
        "cross_family_minimum_accuracy": _finite(cross_family_minimum),
        "null_closure": null_scalars["null_closure"],
        "null_baseline_membership": null_scalars["null_baseline_membership"],
        "null_conditional_retention": null_scalars["null_conditional_retention"],
        "null_post_membership": null_scalars["null_post_membership"],
        "switched_max_gain": _finite(switched["projective_gain"]["maximum"]),
        "switched_defined_fraction": _finite(switched["defined_fraction"]),
        "switched_word_accuracy": _finite(switched["word_accuracy"]),
        "metric_condition": _finite(feshbach["metric"]["condition_number"]),
        "feshbach_return_fraction": _finite(
            feshbach["delayed_return"]["full_product_fraction"]["mean"]
        ),
        "causal_native_accuracy": _finite(causal.get("native_original_accuracy")),
        "state_counterfactual_target_distinct_fraction": _finite(
            causal.get("state_counterfactual_target_distinct_fraction")
        ),
        "operator_counterfactual_target_distinct_fraction": _finite(
            causal.get("operator_counterfactual_target_distinct_fraction")
        ),
        "state_transition_eligibility_fraction": (
            float(causal["state_transition_eligible_examples"] / causal["examples"])
            if (
                type(causal.get("state_transition_eligible_examples")) is int
                and type(causal.get("examples")) is int
                and causal["examples"] > 0
            )
            else None
        ),
        "operator_transition_eligibility_fraction": (
            float(causal["operator_transition_eligible_examples"] / causal["examples"])
            if (
                type(causal.get("operator_transition_eligible_examples")) is int
                and type(causal.get("examples")) is int
                and causal["examples"] > 0
            )
            else None
        ),
        "state_conditions_defined_minimum": finite_min(
            [
                causal.get("native_original_defined_fraction"),
                causal.get("state_patch_defined_fraction"),
                causal.get("angle_matched_state_control_defined_fraction"),
                causal.get("reachable_state_control_defined_fraction"),
            ]
        ),
        "operator_conditions_defined_minimum": finite_min(
            [
                causal.get("native_original_defined_fraction"),
                causal.get("operator_patch_defined_fraction"),
                causal.get("relative_conjugacy_operator_control_defined_fraction"),
                causal.get("cross_context_operator_control_defined_fraction"),
            ]
        ),
        "state_patch": state_patch,
        "random_state_patch": random_state_patch,
        "angle_matched_state_control": angle_state_control,
        "reachable_state_control": reachable_state_control,
        "operator_patch": operator_patch,
        "random_operator_patch": random_operator_patch,
        "relative_conjugacy_operator_control": conjugacy_operator_control,
        "cross_context_operator_control": cross_context_operator_control,
        "state_patch_margin": (
            float(state_patch - max(angle_state_control, reachable_state_control))
            if all_finite(state_margin_values)
            else None
        ),
        "operator_patch_margin": (
            float(
                operator_patch
                - max(conjugacy_operator_control, cross_context_operator_control)
            )
            if all_finite(operator_margin_values)
            else None
        ),
        "hard_isometry_maximum_defect": _finite(
            polar_aggregate.get("maximum_frobenius_orthogonality_defect")
        ),
        "raw_prepolar_relative_singular_minimum": _finite(
            polar_aggregate.get("raw_relative_minimum_singular_value", {}).get("minimum")
        ),
        "ambient_q_ablation_drop": (
            statistics.fmean(ambient_q_drops)
            if all_finite(ambient_q_drops)
            else None
        ),
        "ambient_q_specific_excess_drop": (
            statistics.fmean(ambient_specific_drops)
            if all_finite(ambient_specific_drops)
            else None
        ),
        "ambient_native_minimum_accuracy": (
            min(ambient_native_accuracies)
            if all_finite(ambient_native_accuracies)
            else None
        ),
        "ambient_specific_support_fraction": (
            sum(ambient_support) / len(ambient_support) if ambient_support else None
        ),
    }


def scalar_metrics(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, float | None]:
    """Extract scalar endpoints without letting malformed evidence abort adjudication."""

    try:
        return _scalar_metrics_unchecked(evaluation, config)
    except (
        AttributeError,
        IndexError,
        KeyError,
        TypeError,
        ValueError,
        ZeroDivisionError,
    ):
        return {}


def aggregate_records(records: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for arm in ARM_NAMES:
        rows: list[dict[str, float | None]] = []
        for seed in config["seeds"]:
            record = records.get(str(seed), {}).get(arm, {})
            if "evaluation" in record:
                rows.append(scalar_metrics(record["evaluation"], config))
        metrics: dict[str, Any] = {}
        for key in sorted({name for row in rows for name in row}):
            values = [row[key] for row in rows if row[key] is not None]
            metrics[key] = {
                "mean": statistics.fmean(values) if values else None,
                "minimum": min(values) if values else None,
                "maximum": max(values) if values else None,
                "n": len(values),
            }
        output[arm] = {"replicates": len(rows), "metrics": metrics}
    return output


def _paired_contrast_summary(values: Sequence[float]) -> dict[str, Any]:
    rows = tuple(float(value) for value in values)
    if not rows:
        raise ValueError("paired contrast requires at least one replicate")
    sample_sd = statistics.stdev(rows) if len(rows) > 1 else None
    return {
        "estimate": statistics.fmean(rows),
        "replicate_estimates": list(rows),
        "sample_standard_deviation": sample_sd,
        "standard_error": sample_sd / math.sqrt(len(rows)) if sample_sd is not None else None,
        "n": len(rows),
    }


def paired_2x2_analysis(records: Mapping[str, Any], config: Mapping[str, Any]) -> dict[str, Any]:
    """Compute paired raw/polar by supervised/CR contrasts for every seed."""

    metric_names = (
        "packet_membership",
        "packet_margin_p10",
        "d4_accuracy",
        "cross_family_minimum_accuracy",
        "structured_minimum_accuracy",
        "null_closure",
        "switched_max_gain",
        "switched_word_accuracy",
        "feshbach_return_fraction",
        "ambient_q_ablation_drop",
        "ambient_q_specific_excess_drop",
    )
    by_seed: dict[int, dict[tuple[int, int], dict[str, float | None]]] = {}
    for seed in config["seeds"]:
        cells: dict[tuple[int, int], dict[str, float | None]] = {}
        for cell, arm in TWO_BY_TWO_CELLS.items():
            record = records.get(str(seed), {}).get(arm, {})
            if "evaluation" not in record:
                return {"available": False, "reason": f"missing evaluation for {arm} seed {seed}"}
            cells[cell] = scalar_metrics(record["evaluation"], config)
        by_seed[int(seed)] = cells

    summaries: dict[str, Any] = {}
    unavailable_metrics: dict[str, str] = {}
    for metric in metric_names:
        cell_values: dict[tuple[int, int], list[float]] = {cell: [] for cell in TWO_BY_TWO_CELLS}
        contrasts = {
            "polar_architecture_main_effect": [],
            "closure_objective_main_effect": [],
            "closure_given_raw": [],
            "closure_given_polar": [],
            "polar_given_supervised": [],
            "interaction_difference_in_differences": [],
        }
        metric_error: str | None = None
        for seed in config["seeds"]:
            values: dict[tuple[int, int], float] = {}
            for cell in TWO_BY_TWO_CELLS:
                value = by_seed[int(seed)][cell].get(metric)
                if value is None or not math.isfinite(float(value)):
                    metric_error = (
                        f"non-finite {metric} for "
                        f"{TWO_BY_TWO_CELLS[cell]} seed {seed}"
                    )
                    break
                values[cell] = float(value)
                cell_values[cell].append(float(value))
            if metric_error is not None:
                break
            raw_supervised = values[(0, 0)]
            raw_closure = values[(0, 1)]
            polar_supervised = values[(1, 0)]
            polar_closure = values[(1, 1)]
            contrasts["polar_architecture_main_effect"].append(
                ((polar_supervised + polar_closure) - (raw_supervised + raw_closure)) / 2.0
            )
            contrasts["closure_objective_main_effect"].append(
                ((raw_closure + polar_closure) - (raw_supervised + polar_supervised)) / 2.0
            )
            contrasts["closure_given_raw"].append(raw_closure - raw_supervised)
            contrasts["closure_given_polar"].append(polar_closure - polar_supervised)
            contrasts["polar_given_supervised"].append(polar_supervised - raw_supervised)
            contrasts["interaction_difference_in_differences"].append(
                polar_closure - polar_supervised - raw_closure + raw_supervised
            )
        if metric_error is not None:
            unavailable_metrics[metric] = metric_error
            summaries[metric] = {
                "available": False,
                "reason": metric_error,
            }
            continue
        summaries[metric] = {
            "available": True,
            "cell_means": {
                TWO_BY_TWO_CELLS[cell]: statistics.fmean(values)
                for cell, values in cell_values.items()
            },
            "contrasts": {
                name: _paired_contrast_summary(values)
                for name, values in contrasts.items()
            },
        }
    return {
        "available": any(row.get("available") is True for row in summaries.values()),
        "all_metrics_available": not unavailable_metrics,
        "unavailable_metrics": unavailable_metrics,
        "replicate_count": len(config["seeds"]),
        "cell_mapping": {
            "raw_supervised": TWO_BY_TWO_CELLS[(0, 0)],
            "raw_cr": TWO_BY_TWO_CELLS[(0, 1)],
            "polar_supervised": TWO_BY_TWO_CELLS[(1, 0)],
            "polar_cr": TWO_BY_TWO_CELLS[(1, 1)],
        },
        "factor_semantics": {
            "architecture": "raw Euclidean-normalized linear operator versus hard O(12) polar retraction",
            "objective": (
                "matched supervision versus demonstration-aligned composition plus "
                "finite-path complement return (CR)"
            ),
            "interaction": "difference in the CR effect between polar and raw architectures",
        },
        "metrics": summaries,
    }


def _gate(observed: Any, criterion: str, passed: bool | None) -> dict[str, Any]:
    return {
        "observed": observed,
        "criterion": criterion,
        "status": "NOT_EVALUABLE" if passed is None else ("PASS" if passed else "FAIL"),
    }


def validate_switch_bank(
    profile: str,
    config: Mapping[str, Any],
    switch_bank: Mapping[str, Any],
) -> bool:
    """Validate the complete registered switched-word bank declaration."""

    try:
        raw_word_length = switch_bank["word_length"]
        raw_word_count = switch_bank["word_count"]
        raw_contexts = switch_bank["contexts"]
        raw_exhaustive = switch_bank["exhaustive"]
        raw_words = switch_bank["words"]
    except (KeyError, TypeError):
        return False
    if (
        type(raw_word_length) is not int
        or type(raw_word_count) is not int
        or type(raw_contexts) is not int
        or type(raw_exhaustive) is not bool
        or not isinstance(raw_words, list)
    ):
        return False
    word_length = raw_word_length
    word_count = raw_word_count
    contexts = raw_contexts
    exhaustive = raw_exhaustive
    normalized_words: list[tuple[int, ...]] = []
    for word in raw_words:
        if (
            not isinstance(word, (list, tuple))
            or len(word) != word_length
            or any(type(action) is not int or action not in (0, 1) for action in word)
        ):
            return False
        normalized_words.append(tuple(word))
    if (
        word_length <= 0
        or word_count <= 0
        or contexts <= 0
        or
        word_length != int(config["switched_word_length"])
        or word_count != int(config["switched_word_count"])
        or contexts != int(config["switched_contexts"])
        or len(normalized_words) != word_count
        or len(set(normalized_words)) != word_count
        or word_count > 2**word_length
        or exhaustive != (word_count == 2**word_length)
    ):
        return False
    if exhaustive and set(normalized_words) != set(
        itertools.product(range(2), repeat=word_length)
    ):
        return False
    if profile == "pilot":
        return word_length == 8 and word_count == 256 and exhaustive
    return True


def validate_ambient_control_rows(
    rows: Sequence[Mapping[str, Any]],
    expected_runs: int,
    expected_seeds: Sequence[int] | None = None,
) -> bool:
    """Validate ideal construction and actually applied ambient-control geometry."""

    if len(rows) != int(expected_runs) * 3:
        return False
    keys: list[tuple[int, str, str]] = []
    ideal_errors = (
        "projector_idempotence_error",
        "projector_metric_self_adjoint_error",
        "ideal_random_projector_idempotence_error",
        "ideal_random_projector_metric_self_adjoint_error",
        "ideal_energy_match_maximum_absolute_error",
    )
    applied_errors = (
        "applied_anchor_projector_idempotence_error",
        "applied_anchor_projector_metric_self_adjoint_error",
        "applied_complement_projector_idempotence_error",
        "applied_complement_projector_metric_self_adjoint_error",
        "random_projector_idempotence_error",
        "random_projector_metric_self_adjoint_error",
        "energy_match_maximum_absolute_error",
    )
    for row in rows:
        seed = row.get("seed")
        arm = row.get("arm")
        family = row.get("family")
        if type(seed) is not int or arm not in ARM_NAMES or family not in {
            "d4",
            "c8",
            "mixed_cycle",
        }:
            return False
        keys.append((seed, str(arm), str(family)))
        if (
            row.get("anchor_rank") != 8
            or row.get("complement_rank") != 4
            or row.get("applied_anchor_rank") != 8
            or row.get("applied_complement_rank") != 4
        ):
            return False
        if (
            row.get("random_projector_rank") != 4
            or row.get("applied_random_projector_minimum_rank") != 4
            or row.get("applied_random_projector_maximum_rank") != 4
            or row.get("applied_rank_tolerance")
            != FROZEN_GATE_THRESHOLDS["ambient_applied_rank_tolerance"]
            or row.get("reported_energy_match_tolerance")
            != FROZEN_GATE_THRESHOLDS["ambient_applied_geometry_tolerance"]
        ):
            return False
        for key in ideal_errors:
            value = row.get(key)
            if (
                value is None
                or not math.isfinite(float(value))
                or float(value) < 0.0
                or float(value)
                > FROZEN_GATE_THRESHOLDS["ambient_ideal_geometry_tolerance"]
            ):
                return False
        for key in applied_errors:
            value = row.get(key)
            if (
                value is None
                or not math.isfinite(float(value))
                or float(value) < 0.0
                or float(value)
                > FROZEN_GATE_THRESHOLDS["ambient_applied_geometry_tolerance"]
            ):
                return False
        if row.get("status") not in {
            "CAUSAL_ROLLOUT_UNDEFINED",
            "NATIVE_ACCURACY_BELOW_ATTRIBUTION_FLOOR",
            "NO_MEANINGFUL_Q_PERFORMANCE_DROP",
            "Q_DROP_NOT_SPECIFIC_TO_ANCHOR_COMPLEMENT",
            "SUPPORTED_SPECIFIC_Q_PERFORMANCE_DROP",
        }:
            return False
    if len(set(keys)) != len(keys):
        return False
    if expected_seeds is not None:
        expected_keys = {
            (int(seed), arm, family)
            for seed in expected_seeds
            for arm in ARM_NAMES
            for family in ("d4", "c8", "mixed_cycle")
        }
        if set(keys) != expected_keys:
            return False
    return True


def all_finite(values: Sequence[Any]) -> bool:
    """Return true only for a nonempty sequence of finite numeric values."""

    if not values:
        return False
    try:
        return all(math.isfinite(float(value)) for value in values)
    except (TypeError, ValueError, OverflowError):
        return False


def finite_min(values: Sequence[Any]) -> float:
    """Fail closed with NaN when a registered grid contains invalid values."""

    if not all_finite(values):
        return math.nan
    return min(float(value) for value in values)


def validate_primary_closure_grid(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> dict[str, Any]:
    """Require every registered packet prefix, relation group, and loop cell."""

    expected_prefixes = {str(int(value)) for value in config["packet_prefixes"]}
    packet_rows = evaluation.get("heldout_packet_by_prefix", {})
    packet_prefixes_exact = (
        isinstance(packet_rows, Mapping) and set(packet_rows) == expected_prefixes
    )

    canonical = canonical_maps("d4")
    identity_signature = tuple(range(N_STATES))
    r2_signature = tuple(int(value) for value in canonical[0][canonical[0]])
    expected_signatures = {identity_signature, r2_signature}
    group_coverage_exact = bool(packet_prefixes_exact)
    margin_finiteness_exact = bool(packet_prefixes_exact)
    if packet_prefixes_exact:
        for row in packet_rows.values():
            groups = row.get("relation_groups") if isinstance(row, Mapping) else None
            if not isinstance(groups, list) or len(groups) != 2:
                group_coverage_exact = False
                break
            if _complete_summary_value(
                row.get("suffix_minimum_margin"), "p10"
            ) is None:
                margin_finiteness_exact = False
            try:
                raw_signatures = [group["signature"] for group in groups]
                raw_suffix_counts = [group["suffix_count"] for group in groups]
            except (KeyError, TypeError):
                group_coverage_exact = False
                break
            if any(
                not isinstance(signature, list)
                or len(signature) != N_STATES
                or any(type(value) is not int for value in signature)
                for signature in raw_signatures
            ) or any(type(value) is not int for value in raw_suffix_counts):
                group_coverage_exact = False
                break
            signatures = {tuple(signature) for signature in raw_signatures}
            suffix_counts = list(raw_suffix_counts)
            if any(
                _complete_summary_value(group.get("minimum_margin"), "p10")
                is None
                for group in groups
            ):
                margin_finiteness_exact = False
            if (
                signatures != expected_signatures
                or any(value <= 0 for value in suffix_counts)
                or sum(suffix_counts)
                != FROZEN_REGISTERED_DESIGN["heldout_continuation_count"]
            ):
                group_coverage_exact = False
                break

    null = evaluation.get("null_loop_retention", {})
    relations = null.get("relations", {}) if isinstance(null, Mapping) else {}
    expected_relations = set(D4_RELATIONS)
    expected_repeats = {str(int(value)) for value in config["null_repeats"]}
    raw_repeats = null.get("repeats", []) if isinstance(null, Mapping) else []
    null_relation_coverage_exact = (
        isinstance(relations, Mapping)
        and set(relations) == expected_relations
        and isinstance(raw_repeats, list)
        and all(type(value) is int for value in raw_repeats)
        and [int(value) for value in raw_repeats]
        == [int(value) for value in config["null_repeats"]]
    )
    if null_relation_coverage_exact:
        for name, relation in relations.items():
            if (
                not isinstance(relation, Mapping)
                or not strict_json_equal(
                    relation.get("word"), list(D4_RELATIONS[name])
                )
                or set(relation.get("by_repeat", {})) != expected_repeats
            ):
                null_relation_coverage_exact = False
                break

    deep = evaluation.get("structured_deep_by_depth", {})
    expected_depths = {str(int(value)) for value in config["deep_depths"]}
    expected_families = {"d4", "c8", "mixed_cycle"}
    deep_grid_exact = isinstance(deep, Mapping) and set(deep) == expected_depths
    if deep_grid_exact:
        for depth in config["deep_depths"]:
            depth_row = deep.get(str(depth))
            families = (
                depth_row.get("per_family", {})
                if isinstance(depth_row, Mapping)
                else {}
            )
            if not isinstance(families, Mapping) or set(families) != expected_families:
                deep_grid_exact = False
                break
            for family in expected_families:
                family_row = families.get(family)
                if (
                    not isinstance(family_row, Mapping)
                    or type(family_row.get("examples")) is not int
                    or family_row.get("examples") != int(config["eval_examples"])
                    or type(family_row.get("depth")) is not int
                    or family_row.get("depth") != int(depth)
                    or "accuracy" not in family_row
                    or "finite_fraction" not in family_row
                ):
                    deep_grid_exact = False
                    break
            if not deep_grid_exact:
                break

    return {
        "packet_prefixes_exact": packet_prefixes_exact,
        "relation_group_coverage_exact": group_coverage_exact,
        "packet_margin_finiteness_exact": margin_finiteness_exact,
        "null_relation_repeat_coverage_exact": null_relation_coverage_exact,
        "structured_deep_grid_exact": deep_grid_exact,
        "expected_packet_prefixes": sorted(expected_prefixes, key=int),
        "expected_relation_group_count": 2,
        "expected_null_relations": sorted(expected_relations),
        "expected_null_repeats": sorted(expected_repeats, key=int),
        "valid": bool(
            packet_prefixes_exact
            and group_coverage_exact
            and null_relation_coverage_exact
            and deep_grid_exact
        ),
    }


def validate_packet_result_contract(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> bool:
    """Validate every packet row against the exact frozen bank and count schema."""

    packet = evaluation.get("heldout_packet_by_prefix")
    expected_prefixes = {str(int(value)) for value in config["packet_prefixes"]}
    if not isinstance(packet, Mapping) or set(packet) != expected_prefixes:
        return False
    transitions = torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long)
    bank = freeze_heldout_bank(
        make_v04_suffix_plan(max_depth=8), transitions, max_suffixes=None
    )
    bank_dict = bank.to_dict()
    signature_counts = {
        signature: bank.relation_signatures.count(signature)
        for signature in set(bank.relation_signatures)
    }
    examples = int(config["packet_examples"])
    suffixes = len(bank.words)
    row_keys = {
        "bank",
        "examples",
        "boundary_tolerance",
        "strict_membership_fraction",
        "word_weighted_membership_fraction",
        "macro_relation_group_membership_fraction",
        "suffix_accuracy",
        "finite_margin_fraction",
        "minimum_margin",
        "suffix_minimum_margin",
        "relation_groups",
    }
    group_keys = {
        "signature",
        "suffix_count",
        "membership_fraction",
        "word_weighted_membership_fraction",
        "minimum_margin",
    }
    for prefix in config["packet_prefixes"]:
        row = packet.get(str(prefix))
        if not isinstance(row, Mapping) or set(row) != row_keys:
            return False
        if (
            not strict_json_equal(row.get("bank"), bank_dict)
            or type(row.get("examples")) is not int
            or row.get("examples") != examples
            or type(row.get("boundary_tolerance")) is not float
            or row.get("boundary_tolerance") != 0.0
        ):
            return False
        for key, denominator in (
            ("strict_membership_fraction", examples),
            ("word_weighted_membership_fraction", examples * suffixes),
            ("suffix_accuracy", examples * suffixes),
            ("finite_margin_fraction", examples * suffixes),
        ):
            if not _strict_fraction(row.get(key), denominator=denominator):
                return False
        if not _strict_fraction(row.get("macro_relation_group_membership_fraction")):
            return False
        if not _strict_numeric_summary(
            row.get("minimum_margin"), expected_count=examples
        ) or not _strict_numeric_summary(
            row.get("suffix_minimum_margin"),
            expected_count=examples * suffixes,
        ):
            return False
        suffix_summary = row["suffix_minimum_margin"]
        if round(float(row["finite_margin_fraction"]) * examples * suffixes) != int(
            suffix_summary["finite_count"]
        ):
            return False
        groups = row.get("relation_groups")
        if not isinstance(groups, list) or len(groups) != len(signature_counts):
            return False
        observed: dict[tuple[int, ...], Mapping[str, Any]] = {}
        for group in groups:
            if not isinstance(group, Mapping) or set(group) != group_keys:
                return False
            signature = group.get("signature")
            if (
                not isinstance(signature, list)
                or len(signature) != N_STATES
                or any(type(value) is not int for value in signature)
            ):
                return False
            normalized = tuple(signature)
            if normalized in observed:
                return False
            observed[normalized] = group
        if set(observed) != set(signature_counts):
            return False
        group_membership_counts: list[int] = []
        group_word_counts: list[int] = []
        for signature, count in signature_counts.items():
            group = observed[signature]
            if type(group.get("suffix_count")) is not int or group.get("suffix_count") != count:
                return False
            if not _strict_fraction(
                group.get("membership_fraction"), denominator=examples
            ) or not _strict_fraction(
                group.get("word_weighted_membership_fraction"),
                denominator=examples * count,
            ):
                return False
            if not _strict_numeric_summary(
                group.get("minimum_margin"), expected_count=examples
            ):
                return False
            group_members = round(
                float(group["membership_fraction"]) * examples
            )
            group_words = round(
                float(group["word_weighted_membership_fraction"])
                * examples
                * count
            )
            if (
                float(group["membership_fraction"])
                > float(group["word_weighted_membership_fraction"])
                or group_members > int(group["minimum_margin"]["finite_count"])
            ):
                return False
            group_membership_counts.append(group_members)
            group_word_counts.append(group_words)
        macro = sum(
            float(group["membership_fraction"]) for group in observed.values()
        ) / len(observed)
        if not math.isclose(
            float(row["macro_relation_group_membership_fraction"]),
            macro,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            return False
        overall_members = round(
            float(row["strict_membership_fraction"]) * examples
        )
        overall_words = round(
            float(row["word_weighted_membership_fraction"])
            * examples
            * suffixes
        )
        if (
            not (
                max(0, sum(group_membership_counts) - examples)
                <= overall_members
                <= min(group_membership_counts)
            )
            or overall_words != sum(group_word_counts)
            or float(row["strict_membership_fraction"])
            > float(row["word_weighted_membership_fraction"])
            or float(row["word_weighted_membership_fraction"])
            > float(row["suffix_accuracy"])
            or float(row["word_weighted_membership_fraction"])
            > float(row["finite_margin_fraction"])
            or overall_members > int(row["minimum_margin"]["finite_count"])
        ):
            return False
    return True


def validate_deep_result_contract(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> bool:
    """Validate depth/family accuracies and their exact aggregate arithmetic."""

    deep = evaluation.get("structured_deep_by_depth")
    expected_depths = {str(int(value)) for value in config["deep_depths"]}
    families = {"d4", "c8", "mixed_cycle"}
    if not isinstance(deep, Mapping) or set(deep) != expected_depths:
        return False
    examples = int(config["eval_examples"])
    row_keys = {
        "per_family",
        "pooled_accuracy",
        "macro_family_accuracy",
        "minimum_family_accuracy",
        "total_examples",
    }
    family_keys = {"accuracy", "finite_fraction", "examples", "depth"}
    for depth in config["deep_depths"]:
        row = deep.get(str(depth))
        if not isinstance(row, Mapping) or set(row) != row_keys:
            return False
        per_family = row.get("per_family")
        if not isinstance(per_family, Mapping) or set(per_family) != families:
            return False
        accuracies: list[float] = []
        correct_total = 0
        for family in sorted(families):
            family_row = per_family.get(family)
            if not isinstance(family_row, Mapping) or set(family_row) != family_keys:
                return False
            if (
                type(family_row.get("examples")) is not int
                or family_row.get("examples") != examples
                or type(family_row.get("depth")) is not int
                or family_row.get("depth") != int(depth)
                or not _strict_fraction(
                    family_row.get("accuracy"), denominator=examples
                )
                or not _strict_fraction(
                    family_row.get("finite_fraction"), denominator=examples
                )
                or float(family_row["accuracy"])
                > float(family_row["finite_fraction"])
            ):
                return False
            accuracies.append(float(family_row["accuracy"]))
            correct_total += round(float(family_row["accuracy"]) * examples)
        total = examples * len(families)
        if type(row.get("total_examples")) is not int or row.get("total_examples") != total:
            return False
        for key in ("pooled_accuracy", "macro_family_accuracy", "minimum_family_accuracy"):
            if not _strict_fraction(row.get(key)):
                return False
        expected_values = {
            "pooled_accuracy": correct_total / total,
            "macro_family_accuracy": statistics.fmean(accuracies),
            "minimum_family_accuracy": min(accuracies),
        }
        if any(
            not math.isclose(
                float(row[key]), expected,
                rel_tol=0.0,
                abs_tol=1e-12,
            )
            for key, expected in expected_values.items()
        ):
            return False
    return True


def _validate_switched_payload_contract(
    switched: Any,
    config: Mapping[str, Any],
    *,
    family: str,
    episodes: int,
) -> bool:
    """Validate one family-specific switched result and gain/log-gain linkage."""

    expected_keys = {
        "bank",
        "episodes",
        "defined_fraction",
        "word_accuracy",
        "log_projective_gain",
        "projective_gain",
        "mixed_minus_constant_log_gain",
        "mixed_enhancement_fraction",
    }
    if not isinstance(switched, Mapping) or set(switched) != expected_keys:
        return False
    words = sample_switch_words(
        num_actions=2,
        word_length=int(config["switched_word_length"]),
        count=int(config["switched_word_count"]),
        seed=derive_seed(int(config["eval_seed_base"]), "switch_words"),
        include_constant_words=True,
    )
    transitions = torch.from_numpy(canonical_maps(family)).to(dtype=torch.long)
    encoded = json.dumps(
        {
            "transitions": transitions.tolist(),
            "words": [list(word) for word in words],
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    expected_bank = {
        "word_count": len(words),
        "word_length": int(config["switched_word_length"]),
        "fingerprint": hashlib.sha256(encoded).hexdigest(),
        "constant_word_count": 2,
        "mixed_word_count": len(words) - 2,
    }
    if (
        not strict_json_equal(switched.get("bank"), expected_bank)
        or type(switched.get("episodes")) is not int
        or switched.get("episodes") != episodes
        or not _strict_fraction(
            switched.get("defined_fraction"),
            denominator=episodes * len(words),
        )
    ):
        return False
    defined_count = round(
        float(switched["defined_fraction"]) * episodes * len(words)
    )
    word_accuracy = switched.get("word_accuracy")
    if (word_accuracy is None) != (defined_count == 0):
        return False
    if defined_count > 0 and not _strict_fraction(
        word_accuracy, denominator=defined_count
    ):
        return False
    log_summary = switched.get("log_projective_gain")
    gain_summary = switched.get("projective_gain")
    if not _strict_numeric_summary(
        log_summary, expected_count=defined_count, require_all_finite=True
    ) or not _strict_numeric_summary(
        gain_summary, expected_count=defined_count, require_all_finite=True
    ):
        return False
    if defined_count > 0:
        maximum_log = math.log(torch.finfo(torch.float64).max)
        expected_minimum = math.exp(
            min(float(log_summary["minimum"]), maximum_log)
        )
        expected_maximum = math.exp(
            min(float(log_summary["maximum"]), maximum_log)
        )
        expected_median = math.exp(
            min(float(log_summary["median"]), maximum_log)
        )
        if not math.isclose(
            float(gain_summary["minimum"]),
            expected_minimum,
            rel_tol=1e-12,
            abs_tol=0.0,
        ) or not math.isclose(
            float(gain_summary["maximum"]),
            expected_maximum,
            rel_tol=1e-12,
            abs_tol=0.0,
        ) or not math.isclose(
            float(gain_summary["median"]),
            expected_median,
            rel_tol=1e-12,
            abs_tol=0.0,
        ):
            return False
    enhancement = switched.get("mixed_minus_constant_log_gain")
    if not isinstance(enhancement, Mapping):
        return False
    enhancement_count = enhancement.get("count")
    if (
        type(enhancement_count) is not int
        or not 0 <= enhancement_count <= episodes
        or enhancement_count > defined_count // 2
        or enhancement_count
        < max(
            0,
            episodes
            - ((episodes * len(words) - defined_count) // 2),
        )
        or not _strict_numeric_summary(
            enhancement,
            expected_count=enhancement_count,
            require_all_finite=True,
        )
    ):
        return False
    enhancement_fraction = switched.get("mixed_enhancement_fraction")
    if (enhancement_fraction is None) != (enhancement_count == 0):
        return False
    if enhancement_count > 0 and not _strict_fraction(
        enhancement_fraction, denominator=enhancement_count
    ):
        return False
    if enhancement_count > 0:
        log_range = float(log_summary["maximum"]) - float(log_summary["minimum"])
        if (
            float(enhancement["minimum"]) < -log_range - 1e-12
            or float(enhancement["maximum"]) > log_range + 1e-12
        ):
            return False
        positive_fraction = float(enhancement_fraction)
        if (
            (positive_fraction == 0.0 and float(enhancement["maximum"]) > 0.0)
            or (positive_fraction == 1.0 and float(enhancement["minimum"]) <= 0.0)
            or (
                0.0 < positive_fraction < 1.0
                and not (
                    float(enhancement["minimum"]) <= 0.0
                    and float(enhancement["maximum"]) > 0.0
                )
            )
        ):
            return False
    return True


def validate_switched_result_contract(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> bool:
    """Validate the registered D4 exhaustive switched result."""

    return _validate_switched_payload_contract(
        evaluation.get("switched_gain"),
        config,
        family="d4",
        episodes=int(config["switched_contexts"]),
    )


def validate_null_result_contract(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> bool:
    """Validate null-loop retention counts, conditional denominators, and crossings."""

    null = evaluation.get("null_loop_retention")
    if not isinstance(null, Mapping) or set(null) != {
        "bank", "repeats", "baseline", "relations"
    }:
        return False
    transitions = torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long)
    bank = freeze_heldout_bank(
        make_v04_suffix_plan(max_depth=8), transitions, max_suffixes=None
    )
    if not strict_json_equal(null.get("bank"), bank.to_dict()):
        return False
    expected_repeats = [int(value) for value in config["null_repeats"]]
    if not strict_json_equal(null.get("repeats"), expected_repeats):
        return False
    baseline = null.get("baseline")
    baseline_config = dict(config)
    baseline_config["packet_prefixes"] = [0]
    baseline_config["packet_examples"] = int(config["null_examples"])
    if not validate_packet_result_contract(
        {"heldout_packet_by_prefix": {"0": baseline}}, baseline_config
    ):
        return False
    examples = int(config["null_examples"])
    suffixes = len(bank.words)
    baseline_members = round(
        float(baseline["strict_membership_fraction"]) * examples
    )
    baseline_word_members = round(
        float(baseline["word_weighted_membership_fraction"])
        * examples
        * suffixes
    )
    relations = null.get("relations")
    if not isinstance(relations, Mapping) or set(relations) != set(D4_RELATIONS):
        return False
    relation_keys = {"word", "by_repeat", "first_sampled_crossing"}
    repeat_keys = {
        "strict_membership_fraction",
        "conditional_retention_fraction",
        "conditional_word_retention_fraction",
        "current_label_accuracy",
        "finite_logit_fraction",
        "minimum_margin",
        "positive_baseline_margin_ratio",
        "macro_relation_group_membership_fraction",
    }
    for name, expected_word in D4_RELATIONS.items():
        relation = relations.get(name)
        if (
            not isinstance(relation, Mapping)
            or set(relation) != relation_keys
            or not strict_json_equal(relation.get("word"), list(expected_word))
        ):
            return False
        by_repeat = relation.get("by_repeat")
        expected_keys = {str(value) for value in expected_repeats}
        if not isinstance(by_repeat, Mapping) or set(by_repeat) != expected_keys:
            return False
        retained_by_repeat: dict[int, int] = {}
        for repeat in expected_repeats:
            row = by_repeat.get(str(repeat))
            if not isinstance(row, Mapping) or set(row) != repeat_keys:
                return False
            if not _strict_fraction(
                row.get("strict_membership_fraction"), denominator=examples
            ) or not _strict_fraction(
                row.get("current_label_accuracy"), denominator=examples
            ) or not _strict_fraction(
                row.get("finite_logit_fraction"), denominator=examples
            ) or not _strict_fraction(
                row.get("macro_relation_group_membership_fraction")
            ):
                return False
            post_members = round(
                float(row["strict_membership_fraction"]) * examples
            )
            conditional = row.get("conditional_retention_fraction")
            if (conditional is None) != (baseline_members == 0):
                return False
            if baseline_members > 0:
                if not _strict_fraction(
                    conditional, denominator=baseline_members
                ):
                    return False
                retained = round(float(conditional) * baseline_members)
                if not (
                    max(0, baseline_members + post_members - examples)
                    <= retained
                    <= min(baseline_members, post_members)
                ):
                    return False
                retained_by_repeat[repeat] = retained
            else:
                retained_by_repeat[repeat] = 0
            conditional_word = row.get("conditional_word_retention_fraction")
            if (conditional_word is None) != (baseline_word_members == 0):
                return False
            if baseline_word_members > 0 and not _strict_fraction(
                conditional_word, denominator=baseline_word_members
            ):
                return False
            if baseline_word_members > 0:
                retained_words = round(
                    float(conditional_word) * baseline_word_members
                )
                retained = retained_by_repeat[repeat]
                if not (
                    retained * suffixes
                    <= retained_words
                    <= baseline_word_members - (baseline_members - retained)
                ):
                    return False
            if (
                float(row["current_label_accuracy"])
                > float(row["finite_logit_fraction"])
                or float(row["strict_membership_fraction"])
                > float(row["macro_relation_group_membership_fraction"])
                or not _strict_numeric_summary(
                    row.get("minimum_margin"), expected_count=examples
                )
                or row["minimum_margin"]["finite_count"] < post_members
                or not _strict_numeric_summary(
                    row.get("positive_baseline_margin_ratio"),
                    expected_count=baseline_members,
                )
            ):
                return False
        crossing = relation.get("first_sampled_crossing")
        if not isinstance(crossing, Mapping) or set(crossing) != {
            "never_fraction_among_baseline_members", "observed"
        }:
            return False
        observed = crossing.get("observed")
        if (
            not isinstance(observed, list)
            or len(observed) > baseline_members
            or any(
                type(value) is not int or value not in expected_repeats
                for value in observed
            )
        ):
            return False
        never = crossing.get("never_fraction_among_baseline_members")
        if (never is None) != (baseline_members == 0):
            return False
        if baseline_members > 0:
            if not _strict_fraction(never, denominator=baseline_members):
                return False
            expected_never = (baseline_members - len(observed)) / baseline_members
            if not math.isclose(
                float(never), expected_never, rel_tol=0.0, abs_tol=1e-12
            ):
                return False
            first_repeat = expected_repeats[0]
            if sum(value == first_repeat for value in observed) != (
                baseline_members - retained_by_repeat[first_repeat]
            ):
                return False
            for repeat in expected_repeats[1:]:
                currently_lost = baseline_members - retained_by_repeat[repeat]
                if (
                    sum(value <= repeat for value in observed) < currently_lost
                    or sum(value == repeat for value in observed) > currently_lost
                ):
                    return False
    return True


def validate_ambient_result_contract(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> bool:
    """Validate ambient-causal primitives, arithmetic, thresholds, and statuses."""

    ambient = evaluation.get("ambient_complement_causality")
    families = {"d4", "c8", "mixed_cycle"}
    if not isinstance(ambient, Mapping) or set(ambient) != families:
        return False
    examples = int(config["ambient_examples"])
    steps = int(config["ambient_length"])
    top_keys = {
        "geometry",
        "conditions",
        "performance_drops",
        "native_conditioned_transitions",
        "q_energy_fraction",
        "matched_random_control",
        "attribution",
    }
    condition_names = {
        "native",
        "p_confined",
        "midpoint_q_ablated",
        "matched_random_rank_control",
    }
    condition_keys = {
        "accuracy",
        "finite_fraction",
        "defined_fraction",
        "state_valid_fraction",
        "agreement_with_native",
    }
    geometry_keys = {
        "steps",
        "midpoint",
        "anchor_rank",
        "complement_rank",
        "ambient_dimension",
        "projector_idempotence_error",
        "projector_metric_self_adjoint_error",
        "applied_rank_tolerance",
        "applied_anchor_rank",
        "applied_complement_rank",
        "applied_anchor_projector_idempotence_error",
        "applied_anchor_projector_metric_self_adjoint_error",
        "applied_complement_projector_idempotence_error",
        "applied_complement_projector_metric_self_adjoint_error",
    }
    drop_keys = {
        "p_confined",
        "midpoint_q_ablation",
        "matched_random_rank_control",
        "q_specific_excess_over_random",
    }
    transition_keys = {
        "native_correct_count",
        "native_error_count",
        "p_confined_break_fraction",
        "p_confined_correction_fraction",
        "q_ablation_break_fraction",
        "q_ablation_correction_fraction",
        "matched_random_break_fraction",
        "matched_random_correction_fraction",
    }
    attribution_keys = {
        "status",
        "supports_specific_ambient_attribution",
        "minimum_accuracy_drop",
        "specificity_margin",
        "native_accuracy_floor",
        "native_accuracy_eligible",
        "random_energy_match_tolerance",
    }
    matched_keys = {
        "rank",
        "applied_minimum_effective_rank",
        "applied_maximum_effective_rank",
        "seed",
        "state_conditioned",
        "removed_energy_fraction",
        "q_removed_energy_fraction",
        "q_energy_match_mean_absolute_error",
        "q_energy_match_maximum_absolute_error",
        "maximum_idempotence_error",
        "maximum_metric_self_adjoint_error",
        "ideal_construction",
    }
    ideal_keys = {
        "removed_energy_fraction",
        "q_energy_match_mean_absolute_error",
        "q_energy_match_maximum_absolute_error",
        "maximum_idempotence_error",
        "maximum_metric_self_adjoint_error",
    }
    for family in sorted(families):
        row = ambient.get(family)
        if not isinstance(row, Mapping) or set(row) != top_keys:
            return False
        geometry = row.get("geometry")
        if not isinstance(geometry, Mapping) or set(geometry) != geometry_keys:
            return False
        exact_geometry = {
            "steps": steps,
            "midpoint": steps // 2,
            "anchor_rank": 8,
            "complement_rank": 4,
            "ambient_dimension": 12,
            "applied_rank_tolerance": FROZEN_GATE_THRESHOLDS[
                "ambient_applied_rank_tolerance"
            ],
            "applied_anchor_rank": 8,
            "applied_complement_rank": 4,
        }
        if any(
            not strict_json_equal(geometry.get(key), expected)
            for key, expected in exact_geometry.items()
        ):
            return False
        for key in geometry_keys - set(exact_geometry):
            if not _strict_nonnegative_finite(geometry.get(key)):
                return False
        conditions = row.get("conditions")
        if not isinstance(conditions, Mapping) or set(conditions) != condition_names:
            return False
        for name, condition in conditions.items():
            if not isinstance(condition, Mapping) or set(condition) != condition_keys:
                return False
            if any(
                not _strict_fraction(condition.get(key), denominator=examples)
                for key in (
                    "accuracy",
                    "finite_fraction",
                    "defined_fraction",
                    "agreement_with_native",
                )
            ) or not _strict_fraction(condition.get("state_valid_fraction")):
                return False
            if (
                float(condition["accuracy"]) > float(condition["defined_fraction"])
                or float(condition["defined_fraction"])
                > float(condition["finite_fraction"])
            ):
                return False
        if conditions["native"]["agreement_with_native"] != 1.0:
            return False
        drops = row.get("performance_drops")
        if not isinstance(drops, Mapping) or set(drops) != drop_keys:
            return False
        if any(type(drops.get(key)) is not float or not math.isfinite(drops[key]) for key in drop_keys):
            return False
        native_accuracy = float(conditions["native"]["accuracy"])
        expected_drops = {
            "p_confined": native_accuracy - float(conditions["p_confined"]["accuracy"]),
            "midpoint_q_ablation": native_accuracy
            - float(conditions["midpoint_q_ablated"]["accuracy"]),
            "matched_random_rank_control": native_accuracy
            - float(conditions["matched_random_rank_control"]["accuracy"]),
        }
        expected_drops["q_specific_excess_over_random"] = (
            expected_drops["midpoint_q_ablation"]
            - expected_drops["matched_random_rank_control"]
        )
        if any(
            not math.isclose(float(drops[key]), value, rel_tol=0.0, abs_tol=1e-12)
            for key, value in expected_drops.items()
        ):
            return False
        transitions = row.get("native_conditioned_transitions")
        if not isinstance(transitions, Mapping) or set(transitions) != transition_keys:
            return False
        native_correct = transitions.get("native_correct_count")
        native_error = transitions.get("native_error_count")
        expected_correct = round(native_accuracy * examples)
        expected_defined = round(
            float(conditions["native"]["defined_fraction"]) * examples
        )
        if (
            type(native_correct) is not int
            or type(native_error) is not int
            or native_correct != expected_correct
            or native_error != expected_defined - expected_correct
        ):
            return False
        for name in ("p_confined", "q_ablation", "matched_random"):
            if not _strict_fraction(
                transitions.get(f"{name}_break_fraction"),
                denominator=native_correct,
                allow_none=native_correct == 0,
            ) or not _strict_fraction(
                transitions.get(f"{name}_correction_fraction"),
                denominator=native_error,
                allow_none=native_error == 0,
            ):
                return False
            if (transitions.get(f"{name}_break_fraction") is None) != (native_correct == 0):
                return False
            if (transitions.get(f"{name}_correction_fraction") is None) != (native_error == 0):
                return False
        native_undefined = examples - native_correct - native_error
        condition_mapping = {
            "p_confined": "p_confined",
            "q_ablation": "midpoint_q_ablated",
            "matched_random": "matched_random_rank_control",
        }
        for transition_name, condition_name in condition_mapping.items():
            breaks = (
                round(
                    float(transitions[f"{transition_name}_break_fraction"])
                    * native_correct
                )
                if native_correct > 0
                else 0
            )
            corrections = (
                round(
                    float(transitions[f"{transition_name}_correction_fraction"])
                    * native_error
                )
                if native_error > 0
                else 0
            )
            guaranteed_correct = native_correct - breaks + corrections
            condition = conditions[condition_name]
            condition_correct = round(float(condition["accuracy"]) * examples)
            condition_defined = round(
                float(condition["defined_fraction"]) * examples
            )
            agreement = round(
                float(condition["agreement_with_native"]) * examples
            )
            if not (
                guaranteed_correct
                <= condition_correct
                <= guaranteed_correct + native_undefined
                and condition_defined >= guaranteed_correct
                and native_correct - breaks
                <= agreement
                <= native_correct - breaks + (native_error - corrections)
            ):
                return False
        energies = row.get("q_energy_fraction")
        if not isinstance(energies, Mapping) or set(energies) != {
            "initial", "midpoint", "final", "all_native_states"
        }:
            return False
        for name, count in (
            ("initial", examples),
            ("midpoint", examples),
            ("final", examples),
            ("all_native_states", examples * (steps + 1)),
        ):
            energy_summary = energies.get(name)
            if (
                not _strict_numeric_summary(
                    energy_summary,
                    expected_count=count,
                    require_all_finite=True,
                )
                or float(energy_summary["minimum"]) < 0.0
                or float(energy_summary["maximum"])
                > 1.0
                + float(FROZEN_GATE_THRESHOLDS["ambient_applied_geometry_tolerance"])
            ):
                return False
        matched = row.get("matched_random_control")
        if not isinstance(matched, Mapping) or set(matched) != matched_keys:
            return False
        if (
            type(matched.get("rank")) is not int
            or matched.get("rank") != 4
            or type(matched.get("applied_minimum_effective_rank")) is not int
            or matched.get("applied_minimum_effective_rank") != 4
            or type(matched.get("applied_maximum_effective_rank")) is not int
            or matched.get("applied_maximum_effective_rank") != 4
            or type(matched.get("seed")) is not int
            or matched.get("seed")
            != derive_seed(int(config["eval_seed_base"]), "ambient_random_control", family)
            or matched.get("state_conditioned") is not True
        ):
            return False
        for key in ("removed_energy_fraction", "q_removed_energy_fraction"):
            energy_summary = matched.get(key)
            if (
                not _strict_numeric_summary(
                    energy_summary,
                    expected_count=examples,
                    require_all_finite=True,
                )
                or float(energy_summary["minimum"]) < 0.0
                or float(energy_summary["maximum"])
                > 1.0
                + float(FROZEN_GATE_THRESHOLDS["ambient_applied_geometry_tolerance"])
            ):
                return False
        for key in (
            "q_energy_match_mean_absolute_error",
            "q_energy_match_maximum_absolute_error",
            "maximum_idempotence_error",
            "maximum_metric_self_adjoint_error",
        ):
            if not _strict_nonnegative_finite(matched.get(key)):
                return False
        if float(matched["q_energy_match_mean_absolute_error"]) > float(
            matched["q_energy_match_maximum_absolute_error"]
        ) or abs(
            float(matched["removed_energy_fraction"]["mean"])
            - float(matched["q_removed_energy_fraction"]["mean"])
        ) > float(matched["q_energy_match_mean_absolute_error"]) + 1e-12:
            return False
        ideal = matched.get("ideal_construction")
        if not isinstance(ideal, Mapping) or set(ideal) != ideal_keys:
            return False
        if not _strict_numeric_summary(
            ideal.get("removed_energy_fraction"),
            expected_count=examples,
            require_all_finite=True,
        ) or any(
            not _strict_nonnegative_finite(ideal.get(key))
            for key in ideal_keys - {"removed_energy_fraction"}
        ) or float(ideal["removed_energy_fraction"]["minimum"]) < 0.0 or float(
            ideal["removed_energy_fraction"]["maximum"]
        ) > 1.0 + float(
            FROZEN_GATE_THRESHOLDS["ambient_applied_geometry_tolerance"]
        ):
            return False
        if float(ideal["q_energy_match_mean_absolute_error"]) > float(
            ideal["q_energy_match_maximum_absolute_error"]
        ) or abs(
            float(ideal["removed_energy_fraction"]["mean"])
            - float(energies["midpoint"]["mean"])
        ) > float(ideal["q_energy_match_mean_absolute_error"]) + 1e-12:
            return False
        attribution = row.get("attribution")
        if not isinstance(attribution, Mapping) or set(attribution) != attribution_keys:
            return False
        expected_thresholds = {
            "minimum_accuracy_drop": FROZEN_GATE_THRESHOLDS[
                "ambient_accuracy_drop_minimum"
            ],
            "specificity_margin": FROZEN_GATE_THRESHOLDS[
                "ambient_specificity_margin_minimum"
            ],
            "native_accuracy_floor": FROZEN_GATE_THRESHOLDS[
                "ambient_native_accuracy_minimum"
            ],
            "random_energy_match_tolerance": FROZEN_GATE_THRESHOLDS[
                "ambient_applied_geometry_tolerance"
            ],
        }
        if any(
            not strict_json_equal(attribution.get(key), value)
            for key, value in expected_thresholds.items()
        ):
            return False
        eligible = native_accuracy >= float(expected_thresholds["native_accuracy_floor"])
        if attribution.get("native_accuracy_eligible") is not eligible:
            return False
        finite_defined = all(
            condition["finite_fraction"] == 1.0
            and condition["defined_fraction"] == 1.0
            for condition in conditions.values()
        )
        if float(matched["q_energy_match_maximum_absolute_error"]) > float(
            expected_thresholds["random_energy_match_tolerance"]
        ):
            expected_status = "RANDOM_CONTROL_ENERGY_MATCH_FAILED"
        elif not finite_defined:
            expected_status = "CAUSAL_ROLLOUT_UNDEFINED"
        elif not eligible:
            expected_status = "NATIVE_ACCURACY_BELOW_ATTRIBUTION_FLOOR"
        elif float(drops["midpoint_q_ablation"]) < float(
            expected_thresholds["minimum_accuracy_drop"]
        ):
            expected_status = "NO_MEANINGFUL_Q_PERFORMANCE_DROP"
        elif float(drops["q_specific_excess_over_random"]) < float(
            expected_thresholds["specificity_margin"]
        ):
            expected_status = "Q_DROP_NOT_SPECIFIC_TO_ANCHOR_COMPLEMENT"
        else:
            expected_status = "SUPPORTED_SPECIFIC_Q_PERFORMANCE_DROP"
        expected_support = expected_status == "SUPPORTED_SPECIFIC_Q_PERFORMANCE_DROP"
        if (
            attribution.get("status") != expected_status
            or attribution.get("supports_specific_ambient_attribution") is not expected_support
        ):
            return False
    return True


def validate_causal_result_contract(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
    arm: str,
    cross_context_contract: Any,
) -> bool:
    """Validate causal counts, conditional denominators, controls, and geometry."""

    causal = evaluation.get("causal_interventions")
    if not isinstance(causal, Mapping):
        return False
    conditions = (
        "state_patch",
        "random_state_patch",
        "angle_matched_state_control",
        "reachable_state_control",
        "random_absolute_state",
        "zero_state_lesion_original",
        "operator_patch",
        "random_operator_patch",
        "relative_conjugacy_operator_control",
        "cross_context_operator_control",
        "native_original",
    )
    state_transitions = (
        "state_patch",
        "random_state_patch",
        "angle_matched_state_control",
        "reachable_state_control",
    )
    operator_transitions = (
        "operator_patch",
        "random_operator_patch",
        "relative_conjugacy_operator_control",
        "cross_context_operator_control",
    )
    expected_keys = {
        "available",
        "examples",
        "length",
        "state_split",
        "operator_step",
        "episode_bank_supplied",
        "operator_control_bank_supplied",
        "control_seed",
        "state_counterfactual_target_distinct_fraction",
        "operator_counterfactual_target_distinct_fraction",
        "state_transition_eligible_examples",
        "operator_transition_eligible_examples",
        "state_control_geometry",
        "operator_control_geometry",
        *(f"{name}_accuracy" for name in conditions),
        *(f"{name}_defined_fraction" for name in conditions),
        *(f"{name}_transition_accuracy" for name in state_transitions),
        *(f"{name}_transition_accuracy" for name in operator_transitions),
    }
    if set(causal) != expected_keys:
        return False
    examples = int(config["intervention_examples"])
    fixed = {
        "available": True,
        "examples": examples,
        "length": int(config["intervention_length"]),
        "state_split": int(config["intervention_state_split"]),
        "operator_step": int(config["intervention_operator_step_zero_indexed"]),
        "episode_bank_supplied": True,
        "operator_control_bank_supplied": True,
        "control_seed": derive_seed(
            int(config["eval_seed_base"]), "intervention_controls"
        ),
    }
    if any(not strict_json_equal(causal.get(key), value) for key, value in fixed.items()):
        return False
    polar = arm in POLAR_ARMS
    for name in conditions:
        accuracy = causal.get(f"{name}_accuracy")
        defined = causal.get(f"{name}_defined_fraction")
        if name == "relative_conjugacy_operator_control" and not polar:
            if accuracy is not None or defined is not None:
                return False
            continue
        if (
            not _strict_fraction(accuracy, denominator=examples)
            or not _strict_fraction(defined, denominator=examples)
            or float(accuracy) > float(defined)
        ):
            return False
    for key in (
        "state_counterfactual_target_distinct_fraction",
        "operator_counterfactual_target_distinct_fraction",
    ):
        if not _strict_fraction(causal.get(key), denominator=examples):
            return False
    native_count = round(float(causal["native_original_accuracy"]) * examples)
    for kind, transition_names in (
        ("state", state_transitions),
        ("operator", operator_transitions),
    ):
        eligible = causal.get(f"{kind}_transition_eligible_examples")
        distinct = round(
            float(causal[f"{kind}_counterfactual_target_distinct_fraction"])
            * examples
        )
        if (
            type(eligible) is not int
            or not 0 <= eligible <= examples
            or eligible > min(native_count, distinct)
            or eligible < max(0, native_count + distinct - examples)
        ):
            return False
        for name in transition_names:
            value = causal.get(f"{name}_transition_accuracy")
            if name == "relative_conjugacy_operator_control" and not polar:
                if value is not None:
                    return False
                continue
            if (value is None) != (eligible == 0):
                return False
            if eligible > 0 and not _strict_fraction(value, denominator=eligible):
                return False
            if eligible > 0:
                overall_successes = round(
                    float(causal[f"{name}_accuracy"]) * examples
                )
                transition_successes = round(float(value) * eligible)
                if not (
                    max(0, overall_successes - (examples - eligible))
                    <= transition_successes
                    <= min(overall_successes, eligible)
                ):
                    return False
    state_geometry = causal.get("state_control_geometry")
    state_geometry_keys = {
        "control",
        "defined_fraction",
        "maximum_norm_error",
        "maximum_cosine_error",
        "minimum_target_sine",
    }
    if (
        not isinstance(state_geometry, Mapping)
        or set(state_geometry) != state_geometry_keys
        or state_geometry.get("control")
        != "unit_sphere_recipient_angle_matched_random_tangent"
        or not _strict_fraction(state_geometry.get("defined_fraction"))
        or not _strict_nonnegative_finite(state_geometry.get("maximum_norm_error"))
        or not _strict_nonnegative_finite(state_geometry.get("maximum_cosine_error"))
        or not _strict_fraction(state_geometry.get("minimum_target_sine"))
        or float(state_geometry["minimum_target_sine"])
        <= float(FROZEN_GATE_THRESHOLDS["state_control_geometry_tolerance"])
    ):
        return False
    operator_geometry = causal.get("operator_control_geometry")
    operator_geometry_keys = {
        "control",
        "cross_context_control",
        "available",
        "defined_fraction",
        "maximum_chord_distance_error",
        "maximum_orthogonality_defect",
        "determinant_component_match_fraction",
        "minimum_separation_from_alternate",
        "cross_context_defined_fraction",
        "minimum_cross_context_separation_from_original",
        "minimum_cross_context_separation_from_alternate",
        "cross_context_base_original_table_collision_count",
        "cross_context_base_alternate_table_collision_count",
        "cross_context_selected_original_table_collision_count",
        "cross_context_selected_alternate_table_collision_count",
    }
    if (
        not isinstance(operator_geometry, Mapping)
        or set(operator_geometry) != operator_geometry_keys
        or operator_geometry.get("control") != "relative_conjugacy_matched_orthogonal"
        or operator_geometry.get("cross_context_control")
        != (
            "independent_context_balanced_slot_with_exact_original_and_alternate_"
            "table_collision_exclusion"
        )
        or operator_geometry.get("available") is not polar
    ):
        return False
    base_original_collisions = operator_geometry.get(
        "cross_context_base_original_table_collision_count"
    )
    base_alternate_collisions = operator_geometry.get(
        "cross_context_base_alternate_table_collision_count"
    )
    selected_original_collisions = operator_geometry.get(
        "cross_context_selected_original_table_collision_count"
    )
    selected_alternate_collisions = operator_geometry.get(
        "cross_context_selected_alternate_table_collision_count"
    )
    if (
        type(base_original_collisions) is not int
        or not 0 <= base_original_collisions <= examples
        or type(base_alternate_collisions) is not int
        or not 0 <= base_alternate_collisions <= examples
        or base_original_collisions + base_alternate_collisions > examples
        or type(selected_original_collisions) is not int
        or selected_original_collisions != 0
        or type(selected_alternate_collisions) is not int
        or selected_alternate_collisions != 0
    ):
        return False
    operator_fraction_keys = {
        "defined_fraction",
        "determinant_component_match_fraction",
        "cross_context_defined_fraction",
    }
    operator_nonnegative_keys = {
        "maximum_chord_distance_error",
        "maximum_orthogonality_defect",
        "minimum_separation_from_alternate",
        "minimum_cross_context_separation_from_original",
        "minimum_cross_context_separation_from_alternate",
    }
    if polar:
        if any(
            not _strict_fraction(operator_geometry.get(key))
            for key in operator_fraction_keys
        ) or any(
            not _strict_nonnegative_finite(operator_geometry.get(key))
            for key in operator_nonnegative_keys
        ):
            return False
        if (
            not isinstance(cross_context_contract, Mapping)
            or type(
                cross_context_contract.get("base_original_table_collision_count")
            ) is not int
            or type(
                cross_context_contract.get("base_alternate_table_collision_count")
            ) is not int
            or base_original_collisions
            != cross_context_contract.get("base_original_table_collision_count")
            or base_alternate_collisions
            != cross_context_contract.get("base_alternate_table_collision_count")
            or selected_original_collisions
            != cross_context_contract.get("selected_original_table_collision_count")
            or selected_alternate_collisions
            != cross_context_contract.get("selected_alternate_table_collision_count")
        ):
            return False
    elif any(
        operator_geometry.get(key) is not None
        for key in operator_fraction_keys | operator_nonnegative_keys
    ) or any(
        value != 0
        for value in (
            base_original_collisions,
            base_alternate_collisions,
            selected_original_collisions,
            selected_alternate_collisions,
        )
    ):
        return False
    return True


def _summary_is_nonnegative(summary: Mapping[str, Any]) -> bool:
    """Return whether every finite value represented by a summary is nonnegative."""

    return (
        type(summary.get("finite_count")) is int
        and (
            summary["finite_count"] == 0
            or (
                type(summary.get("minimum")) is float
                and summary["minimum"] >= 0.0
            )
        )
    )


def _pooled_summary_matches_children(
    pooled: Any,
    children: Sequence[Mapping[str, Any]],
    *,
    expected_count: int,
    require_all_finite: bool,
) -> bool:
    """Check the pooled count, extrema, and finite-value mean from child summaries."""

    if not _strict_numeric_summary(
        pooled,
        expected_count=expected_count,
        require_all_finite=require_all_finite,
    ):
        return False
    finite_count = sum(int(child["finite_count"]) for child in children)
    if int(pooled["finite_count"]) != finite_count:
        return False
    if finite_count == 0:
        return True
    nonempty = [child for child in children if int(child["finite_count"]) > 0]
    expected_minimum = min(float(child["minimum"]) for child in nonempty)
    expected_maximum = max(float(child["maximum"]) for child in nonempty)
    expected_mean = sum(
        float(child["mean"]) * int(child["finite_count"])
        for child in nonempty
    ) / finite_count
    return all(
        math.isclose(
            float(pooled[key]),
            expected,
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
        for key, expected in (
            ("minimum", expected_minimum),
            ("maximum", expected_maximum),
            ("mean", expected_mean),
        )
    )


def validate_feshbach_result_contract(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
) -> bool:
    """Validate the complete exact P/Q Feshbach diagnostic payload."""

    result = evaluation.get("exact_feshbach")
    if not isinstance(result, Mapping) or set(result) != {
        "exact_anchor_plane", "metric", "generator_blocks", "delayed_return"
    }:
        return False

    plane = result.get("exact_anchor_plane")
    plane_keys = {
        "ambient_dimension",
        "anchor_count",
        "retained_rank",
        "nuisance_rank",
        "effective_trace",
        "complement_effective_trace",
        "idempotence_error",
        "metric_self_adjoint_error",
    }
    if not isinstance(plane, Mapping) or set(plane) != plane_keys:
        return False
    exact_plane = {
        "ambient_dimension": 12,
        "anchor_count": N_STATES,
        "retained_rank": N_STATES,
        "nuisance_rank": 12 - N_STATES,
    }
    if any(
        not strict_json_equal(plane.get(key), expected)
        for key, expected in exact_plane.items()
    ):
        return False
    for key in (
        "effective_trace",
        "complement_effective_trace",
        "idempotence_error",
        "metric_self_adjoint_error",
    ):
        if not _strict_nonnegative_finite(plane.get(key)):
            return False
    if (
        not math.isclose(
            float(plane["effective_trace"]),
            float(plane["retained_rank"]),
            rel_tol=0.0,
            abs_tol=1e-4,
        )
        or not math.isclose(
            float(plane["complement_effective_trace"]),
            float(plane["nuisance_rank"]),
            rel_tol=0.0,
            abs_tol=1e-4,
        )
        or int(plane["retained_rank"]) + int(plane["nuisance_rank"])
        != int(plane["ambient_dimension"])
    ):
        return False

    metric = result.get("metric")
    if not isinstance(metric, Mapping) or set(metric) != {
        "positive_definite", "condition_number", "determinant", "eigenvalues"
    }:
        return False
    eigenvalues = metric.get("eigenvalues")
    if (
        metric.get("positive_definite") is not True
        or type(metric.get("condition_number")) is not float
        or not math.isfinite(metric["condition_number"])
        or metric["condition_number"] < 1.0
        or type(metric.get("determinant")) is not float
        or not math.isfinite(metric["determinant"])
        or metric["determinant"] <= 0.0
        or not isinstance(eigenvalues, list)
        or len(eigenvalues) != int(plane["ambient_dimension"])
        or any(
            type(value) is not float or not math.isfinite(value) or value <= 0.0
            for value in eigenvalues
        )
        or any(left > right for left, right in zip(eigenvalues, eigenvalues[1:]))
    ):
        return False
    expected_condition = float(eigenvalues[-1]) / float(eigenvalues[0])
    expected_determinant = math.prod(float(value) for value in eigenvalues)
    if not math.isclose(
        float(metric["condition_number"]),
        expected_condition,
        rel_tol=1e-4,
        abs_tol=1e-8,
    ) or not math.isclose(
        float(metric["determinant"]),
        expected_determinant,
        rel_tol=1e-4,
        abs_tol=1e-8,
    ):
        return False

    generator_blocks = result.get("generator_blocks")
    block_keys = {
        "projective_scale",
        "p_to_p_fraction",
        "p_to_q_fraction",
        "q_to_p_fraction",
        "q_to_q_fraction",
        "total_energy",
    }
    block_count = int(config["feshbach_contexts"]) * 2
    if not isinstance(generator_blocks, Mapping) or set(generator_blocks) != block_keys:
        return False
    for key in block_keys:
        summary = generator_blocks.get(key)
        if (
            not _strict_numeric_summary(
                summary, expected_count=block_count, require_all_finite=True
            )
            or not _summary_is_nonnegative(summary)
        ):
            return False
    if (
        float(generator_blocks["projective_scale"]["minimum"]) <= 0.0
        or float(generator_blocks["total_energy"]["minimum"]) <= 0.0
    ):
        return False
    fraction_keys = (
        "p_to_p_fraction", "p_to_q_fraction", "q_to_p_fraction", "q_to_q_fraction"
    )
    if any(
        float(generator_blocks[key]["maximum"]) > 1.0 + 1e-4
        for key in fraction_keys
    ) or not math.isclose(
        sum(float(generator_blocks[key]["mean"]) for key in fraction_keys),
        1.0,
        rel_tol=0.0,
        abs_tol=1e-4,
    ):
        return False

    delayed = result.get("delayed_return")
    delayed_keys = {
        "middle_word_maximum_length",
        "middle_word_count",
        "generator_pair_count",
        "full_product_fraction",
        "submultiplicative_fraction",
        "return_energy",
    }
    if not isinstance(delayed, Mapping) or set(delayed) != delayed_keys:
        return False
    for key, expected in (
        ("middle_word_maximum_length", 3),
        ("middle_word_count", 15),
        ("generator_pair_count", 4),
    ):
        if not strict_json_equal(delayed.get(key), expected):
            return False
    delayed_count = int(config["feshbach_contexts"]) * 4 * 15
    for key in ("full_product_fraction", "submultiplicative_fraction", "return_energy"):
        summary = delayed.get(key)
        if (
            not _strict_numeric_summary(
                summary, expected_count=delayed_count, require_all_finite=True
            )
            or not _summary_is_nonnegative(summary)
        ):
            return False
    return float(delayed["submultiplicative_fraction"]["maximum"]) <= 1.0 + 1e-4


def validate_hard_polar_result_contract(
    evaluation: Mapping[str, Any],
    config: Mapping[str, Any],
    arm: str,
) -> bool:
    """Validate hard-polar geometry, pooled arithmetic, and switched controls."""

    geometry = evaluation.get("hard_polar_geometry")
    raw_payload = {
        "available": False,
        "reason": "raw operator arm; hard-polar geometry assay is not applicable",
    }
    if arm not in POLAR_ARMS:
        return strict_json_equal(geometry, raw_payload)
    top_keys = {
        "available",
        "per_batch",
        "aggregate",
        "switched_sanity",
        "thresholds",
        "hard_isometry_pass",
        "projective_switched_gain_sanity_pass",
        "raw_prepolar_well_conditioned_pass",
    }
    if (
        not isinstance(geometry, Mapping)
        or set(geometry) != top_keys
        or geometry.get("available") is not True
    ):
        return False

    families = {"d4", "c8", "mixed_cycle"}
    per_batch = geometry.get("per_batch")
    per_batch_keys = {
        "examples",
        "operators_per_example",
        "ambient_dimension",
        "frobenius_orthogonality_defect",
        "spectral_orthogonality_defect",
        "absolute_determinant",
        "absolute_determinant_magnitude_defect",
        "determinant_components",
        "raw_relative_minimum_singular_value",
        "raw_below_relative_singular_floor_fraction",
        "postpolar_relative_minimum_singular_value",
    }
    summary_keys = (
        "frobenius_orthogonality_defect",
        "spectral_orthogonality_defect",
        "absolute_determinant",
        "absolute_determinant_magnitude_defect",
        "raw_relative_minimum_singular_value",
        "postpolar_relative_minimum_singular_value",
    )
    examples = int(config["ambient_examples"])
    matrices_per_family = examples * 2
    if not isinstance(per_batch, Mapping) or set(per_batch) != families:
        return False
    for family in sorted(families):
        row = per_batch.get(family)
        if not isinstance(row, Mapping) or set(row) != per_batch_keys:
            return False
        if any(
            not strict_json_equal(row.get(key), expected)
            for key, expected in (
                ("examples", examples),
                ("operators_per_example", 2),
                ("ambient_dimension", 12),
            )
        ):
            return False
        for key in summary_keys:
            summary = row.get(key)
            if (
                not _strict_numeric_summary(
                    summary,
                    expected_count=matrices_per_family,
                    require_all_finite=key != "raw_relative_minimum_singular_value",
                )
                or not _summary_is_nonnegative(summary)
            ):
                return False
        for key in (
            "raw_relative_minimum_singular_value",
            "postpolar_relative_minimum_singular_value",
        ):
            maximum = row[key]["maximum"]
            if maximum is not None and float(maximum) > 1.0 + 1e-12:
                return False
        components = row.get("determinant_components")
        if (
            not isinstance(components, Mapping)
            or set(components) != {"positive", "negative", "zero"}
            or any(type(value) is not int or value < 0 for value in components.values())
            or sum(components.values()) != matrices_per_family
        ):
            return False
        below = row.get("raw_below_relative_singular_floor_fraction")
        if not _strict_fraction(below, denominator=matrices_per_family):
            return False
        below_count = round(float(below) * matrices_per_family)
        if below_count < matrices_per_family - int(
            row["raw_relative_minimum_singular_value"]["finite_count"]
        ):
            return False

    thresholds = geometry.get("thresholds")
    expected_thresholds = {
        "orthogonality_tolerance": FROZEN_GATE_THRESHOLDS[
            "hard_polar_orthogonality_tolerance"
        ],
        "determinant_magnitude_tolerance": FROZEN_GATE_THRESHOLDS[
            "hard_polar_determinant_tolerance"
        ],
        "projective_log_gain_tolerance": FROZEN_GATE_THRESHOLDS[
            "hard_polar_projective_log_gain_tolerance"
        ],
        "raw_relative_singular_floor": FROZEN_GATE_THRESHOLDS[
            "raw_prepolar_relative_singular_warning_floor"
        ],
    }
    if not strict_json_equal(thresholds, expected_thresholds):
        return False

    switched = geometry.get("switched_sanity")
    switched_episodes = min(examples, int(config["switched_contexts"]))
    if not isinstance(switched, Mapping) or set(switched) != families:
        return False
    for family in sorted(families):
        if not _validate_switched_payload_contract(
            switched.get(family),
            config,
            family=family,
            episodes=switched_episodes,
        ):
            return False

    aggregate = geometry.get("aggregate")
    aggregate_keys = {
        "batch_count",
        "operator_matrix_count",
        "all_finite",
        "maximum_frobenius_orthogonality_defect",
        "maximum_spectral_orthogonality_defect",
        "absolute_determinant",
        "maximum_absolute_determinant_magnitude_defect",
        "determinant_components",
        "raw_relative_minimum_singular_value",
        "raw_below_relative_singular_floor_fraction",
        "postpolar_relative_minimum_singular_value",
        "switched_defined_fraction",
        "maximum_absolute_switched_log_gain",
    }
    total_matrices = matrices_per_family * len(families)
    if not isinstance(aggregate, Mapping) or set(aggregate) != aggregate_keys:
        return False
    if (
        not strict_json_equal(aggregate.get("batch_count"), len(families))
        or not strict_json_equal(aggregate.get("operator_matrix_count"), total_matrices)
    ):
        return False
    child_summaries = {
        key: [per_batch[family][key] for family in sorted(families)]
        for key in summary_keys
    }
    for key in (
        "absolute_determinant",
        "raw_relative_minimum_singular_value",
        "postpolar_relative_minimum_singular_value",
    ):
        if (
            not _pooled_summary_matches_children(
                aggregate.get(key),
                child_summaries[key],
                expected_count=total_matrices,
                require_all_finite=key != "raw_relative_minimum_singular_value",
            )
            or not _summary_is_nonnegative(aggregate[key])
        ):
            return False
    expected_all_finite = all(
        int(per_batch[family][key]["finite_count"]) == matrices_per_family
        for family in families
        for key in (
            "frobenius_orthogonality_defect",
            "spectral_orthogonality_defect",
            "absolute_determinant",
            "postpolar_relative_minimum_singular_value",
        )
    )
    if aggregate.get("all_finite") is not expected_all_finite:
        return False
    for aggregate_key, child_key in (
        ("maximum_frobenius_orthogonality_defect", "frobenius_orthogonality_defect"),
        ("maximum_spectral_orthogonality_defect", "spectral_orthogonality_defect"),
        (
            "maximum_absolute_determinant_magnitude_defect",
            "absolute_determinant_magnitude_defect",
        ),
    ):
        value = aggregate.get(aggregate_key)
        if (
            not _strict_nonnegative_finite(value)
            or not math.isclose(
                float(value),
                max(float(summary["maximum"]) for summary in child_summaries[child_key]),
                rel_tol=1e-12,
                abs_tol=1e-12,
            )
        ):
            return False
    components = aggregate.get("determinant_components")
    if (
        not isinstance(components, Mapping)
        or set(components) != {"positive", "negative", "zero"}
        or any(type(value) is not int or value < 0 for value in components.values())
        or sum(components.values()) != total_matrices
        or any(
            components[key]
            != sum(per_batch[family]["determinant_components"][key] for family in families)
            for key in components
        )
    ):
        return False
    raw_below = aggregate.get("raw_below_relative_singular_floor_fraction")
    expected_raw_below_count = sum(
        round(
            float(per_batch[family]["raw_below_relative_singular_floor_fraction"])
            * matrices_per_family
        )
        for family in families
    )
    if (
        not _strict_fraction(raw_below, denominator=total_matrices)
        or round(float(raw_below) * total_matrices) != expected_raw_below_count
    ):
        return False

    words = int(config["switched_word_count"])
    total_switched = switched_episodes * words * len(families)
    defined_counts = {
        family: round(
            float(switched[family]["defined_fraction"]) * switched_episodes * words
        )
        for family in families
    }
    switched_defined = aggregate.get("switched_defined_fraction")
    if (
        not _strict_fraction(switched_defined, denominator=total_switched)
        or round(float(switched_defined) * total_switched) != sum(defined_counts.values())
    ):
        return False
    log_extrema = [
        abs(float(switched[family]["log_projective_gain"][key]))
        for family in families
        if defined_counts[family] > 0
        for key in ("minimum", "maximum")
    ]
    expected_maximum_log = max(log_extrema) if log_extrema else None
    maximum_log = aggregate.get("maximum_absolute_switched_log_gain")
    if (maximum_log is None) != (expected_maximum_log is None):
        return False
    if expected_maximum_log is not None and (
        not _strict_nonnegative_finite(maximum_log)
        or not math.isclose(
            float(maximum_log), expected_maximum_log, rel_tol=1e-12, abs_tol=1e-12
        )
    ):
        return False

    expected_hard_pass = bool(
        expected_all_finite
        and float(aggregate["maximum_frobenius_orthogonality_defect"])
        <= float(thresholds["orthogonality_tolerance"])
        and float(aggregate["maximum_spectral_orthogonality_defect"])
        <= float(thresholds["orthogonality_tolerance"])
        and float(aggregate["maximum_absolute_determinant_magnitude_defect"])
        <= float(thresholds["determinant_magnitude_tolerance"])
    )
    expected_switched_pass = bool(
        float(switched_defined) == 1.0
        and maximum_log is not None
        and float(maximum_log) <= float(thresholds["projective_log_gain_tolerance"])
    )
    raw_minimum = aggregate["raw_relative_minimum_singular_value"]["minimum"]
    expected_raw_pass = bool(
        raw_minimum is not None
        and float(raw_minimum) >= float(thresholds["raw_relative_singular_floor"])
    )
    return (
        geometry.get("hard_isometry_pass") is expected_hard_pass
        and geometry.get("projective_switched_gain_sanity_pass")
        is expected_switched_pass
        and geometry.get("raw_prepolar_well_conditioned_pass") is expected_raw_pass
    )


def adjudicate(
    profile: str,
    config: Mapping[str, Any],
    contract_status: Mapping[str, Any],
    records: Mapping[str, Any],
    aggregate: Mapping[str, Any],
    paired_analysis: Mapping[str, Any],
    checkpoint_seal: Mapping[str, Any],
    eval_bank: Mapping[str, Any],
    phase_times: Mapping[str, str],
    run_mode: str = "official",
    source_integrity: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    successful_training = sum(
        "checkpoint" in records.get(str(seed), {}).get(arm, {})
        for seed in config["seeds"]
        for arm in ARM_NAMES
    )
    successful_evaluation = sum(
        "evaluation" in records.get(str(seed), {}).get(arm, {})
        for seed in config["seeds"]
        for arm in ARM_NAMES
    )
    verified_reloads = sum(
        records.get(str(seed), {}).get(arm, {}).get("checkpoint_reload_verified") is True
        for seed in config["seeds"]
        for arm in ARM_NAMES
    )
    expected_runs = len(config["seeds"]) * len(ARM_NAMES)
    strict_files = bool(checkpoint_seal.get("strict_checkpoint_firewall"))
    execution = {
        "E01_preregistration_profile_match": _gate(
            contract_status,
            (
                "contract schema, version, author, status, source digest, all profiles, "
                "selected profile, and registered design exactly match the implementation"
            ),
            bool(contract_status.get("valid")),
        ),
        "E02_all_training_runs_completed": _gate(
            successful_training, f"== {expected_runs}", successful_training == expected_runs
        ),
        "E03_all_evaluations_completed": _gate(
            successful_evaluation, f"== {expected_runs}", successful_evaluation == expected_runs
        ),
        "E04_checkpoint_seal_complete": _gate(
            len(checkpoint_seal.get("checkpoints", [])),
            f"== {expected_runs} checkpoint receipts",
            len(checkpoint_seal.get("checkpoints", [])) == expected_runs,
        ),
        "E05_frozen_checkpoint_reload": _gate(
            verified_reloads,
            f"== {expected_runs} hash-verified disk reloads",
            verified_reloads == expected_runs,
        ),
        "E06_source_and_contract_immutable": _gate(
            source_integrity,
            (
                "source-tree and preregistration-contract hashes equal their startup "
                "values before checkpoint sealing and after evaluation"
            ),
            bool(source_integrity and source_integrity.get("valid") is True),
        ),
    }

    init_stream_checks: list[bool] = []
    construction_digests: set[str] = set()
    construction_record_checks: list[bool] = []
    ranks: list[tuple[Any, Any]] = []
    terminal_firewall_rows: list[dict[str, Any]] = []
    polar_geometry_rows: list[dict[str, Any]] = []
    ambient_control_rows: list[dict[str, Any]] = []
    closure_coverage_rows: list[dict[str, Any]] = []
    packet_contract_rows: list[dict[str, Any]] = []
    deep_contract_rows: list[dict[str, Any]] = []
    ambient_contract_rows: list[dict[str, Any]] = []
    causal_contract_rows: list[dict[str, Any]] = []
    switched_contract_rows: list[dict[str, Any]] = []
    null_contract_rows: list[dict[str, Any]] = []
    feshbach_contract_rows: list[dict[str, Any]] = []
    hard_polar_contract_rows: list[dict[str, Any]] = []
    for seed in config["seeds"]:
        complete = [records.get(str(seed), {}).get(arm, {}) for arm in ARM_NAMES]
        initial = {row.get("training", {}).get("initial_state_digest") for row in complete}
        shared_initial = {
            row.get("training", {}).get("shared_initialization_digest") for row in complete
        }
        streams = {row.get("training", {}).get("episode_stream_digest") for row in complete}
        proposal_streams = {
            row.get("training", {}).get("terminal_proposal_stream_digest") for row in complete
        }
        init_stream_checks.append(
            len(initial) == 1
            and None not in initial
            and len(shared_initial) == 1
            and None not in shared_initial
            and len(streams) == 1
            and None not in streams
            and len(proposal_streams) == 1
            and None not in proposal_streams
        )
        for arm, row in zip(ARM_NAMES, complete):
            digest = row.get("training", {}).get("construction_digest")
            if digest is not None:
                construction_digests.add(str(digest))
            training = row.get("training", {})
            construction_record_checks.append(
                type(training.get("construction_word_count")) is int
                and training.get("construction_word_count")
                == len(make_v04_construction_bank(
                    int(config["training"]["auxiliary_max_depth"])
                ).construction)
                and isinstance(digest, str)
            )
            if training:
                terminal_firewall_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "policy_digest": training.get("terminal_firewall_policy_digest"),
                        "proposal_stream_digest": training.get("terminal_proposal_stream_digest"),
                        "proposal_count": training.get("terminal_proposal_count"),
                        "accepted": training.get("terminal_candidates_accepted"),
                        "rejected": training.get("terminal_candidates_rejected"),
                        "identity_rejections": training.get("terminal_identity_rejections"),
                        "r2_rejections": training.get("terminal_r2_rejections"),
                    }
                )
            feshbach = row.get("evaluation", {}).get("exact_feshbach", {}).get("exact_anchor_plane")
            if isinstance(feshbach, Mapping):
                ranks.append(
                    (feshbach.get("retained_rank"), feshbach.get("nuisance_rank"))
                )
            geometry = row.get("evaluation", {}).get("hard_polar_geometry", {})
            if "evaluation" in row:
                evaluation = row["evaluation"]
                closure_coverage_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        **validate_primary_closure_grid(evaluation, config),
                    }
                )
                packet_contract_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "valid": validate_packet_result_contract(evaluation, config),
                    }
                )
                deep_contract_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "valid": validate_deep_result_contract(evaluation, config),
                    }
                )
                ambient_contract_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "valid": validate_ambient_result_contract(evaluation, config),
                    }
                )
                causal_contract_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "valid": validate_causal_result_contract(
                            evaluation,
                            config,
                            arm,
                            eval_bank.get("cross_context_operator_control"),
                        ),
                    }
                )
                switched_contract_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "valid": validate_switched_result_contract(
                            evaluation, config
                        ),
                    }
                )
                null_contract_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "valid": validate_null_result_contract(evaluation, config),
                    }
                )
                feshbach_contract_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "valid": validate_feshbach_result_contract(evaluation, config),
                    }
                )
                hard_polar_contract_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "valid": validate_hard_polar_result_contract(
                            evaluation, config, arm
                        ),
                    }
                )
            if (
                arm in POLAR_ARMS
                and geometry.get("available") is True
                and "evaluation" in row
                and validate_hard_polar_result_contract(
                    row["evaluation"], config, arm
                )
            ):
                polar_geometry_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "hard_isometry_pass": geometry.get("hard_isometry_pass"),
                        "projective_switched_gain_sanity_pass": geometry.get(
                            "projective_switched_gain_sanity_pass"
                        ),
                        "raw_prepolar_well_conditioned_pass": geometry.get(
                            "raw_prepolar_well_conditioned_pass"
                        ),
                        "maximum_frobenius_orthogonality_defect": geometry.get(
                            "aggregate", {}
                        ).get("maximum_frobenius_orthogonality_defect"),
                        "raw_relative_minimum_singular_value": geometry.get(
                            "aggregate", {}
                        ).get("raw_relative_minimum_singular_value", {}).get("minimum"),
                    }
                )
            for family, ambient in row.get("evaluation", {}).get(
                "ambient_complement_causality", {}
            ).items():
                ambient_control_rows.append(
                    {
                        "seed": int(seed),
                        "arm": arm,
                        "family": family,
                        "anchor_rank": ambient.get("geometry", {}).get("anchor_rank"),
                        "complement_rank": ambient.get("geometry", {}).get("complement_rank"),
                        "projector_idempotence_error": ambient.get("geometry", {}).get(
                            "projector_idempotence_error"
                        ),
                        "projector_metric_self_adjoint_error": ambient.get(
                            "geometry", {}
                        ).get("projector_metric_self_adjoint_error"),
                        "applied_anchor_rank": ambient.get("geometry", {}).get(
                            "applied_anchor_rank"
                        ),
                        "applied_complement_rank": ambient.get("geometry", {}).get(
                            "applied_complement_rank"
                        ),
                        "applied_rank_tolerance": ambient.get("geometry", {}).get(
                            "applied_rank_tolerance"
                        ),
                        "applied_anchor_projector_idempotence_error": ambient.get(
                            "geometry", {}
                        ).get("applied_anchor_projector_idempotence_error"),
                        "applied_anchor_projector_metric_self_adjoint_error": ambient.get(
                            "geometry", {}
                        ).get("applied_anchor_projector_metric_self_adjoint_error"),
                        "applied_complement_projector_idempotence_error": ambient.get(
                            "geometry", {}
                        ).get("applied_complement_projector_idempotence_error"),
                        "applied_complement_projector_metric_self_adjoint_error": ambient.get(
                            "geometry", {}
                        ).get("applied_complement_projector_metric_self_adjoint_error"),
                        "random_projector_rank": ambient.get(
                            "matched_random_control", {}
                        ).get("rank"),
                        "applied_random_projector_minimum_rank": ambient.get(
                            "matched_random_control", {}
                        ).get("applied_minimum_effective_rank"),
                        "applied_random_projector_maximum_rank": ambient.get(
                            "matched_random_control", {}
                        ).get("applied_maximum_effective_rank"),
                        "random_projector_idempotence_error": ambient.get(
                            "matched_random_control", {}
                        ).get("maximum_idempotence_error"),
                        "random_projector_metric_self_adjoint_error": ambient.get(
                            "matched_random_control", {}
                        ).get("maximum_metric_self_adjoint_error"),
                        "energy_match_maximum_absolute_error": ambient.get(
                            "matched_random_control", {}
                        ).get("q_energy_match_maximum_absolute_error"),
                        "ideal_random_projector_idempotence_error": ambient.get(
                            "matched_random_control", {}
                        ).get("ideal_construction", {}).get(
                            "maximum_idempotence_error"
                        ),
                        "ideal_random_projector_metric_self_adjoint_error": ambient.get(
                            "matched_random_control", {}
                        ).get("ideal_construction", {}).get(
                            "maximum_metric_self_adjoint_error"
                        ),
                        "ideal_energy_match_maximum_absolute_error": ambient.get(
                            "matched_random_control", {}
                        ).get("ideal_construction", {}).get(
                            "q_energy_match_maximum_absolute_error"
                        ),
                        "reported_energy_match_tolerance": ambient.get(
                            "attribution", {}
                        ).get("random_energy_match_tolerance"),
                        "status": ambient.get("attribution", {}).get("status"),
                    }
                )
    expected_construction_bank = make_v04_construction_bank(
        int(config["training"]["auxiliary_max_depth"])
    )
    expected_construction = construction_checkpoint_metadata(
        expected_construction_bank
    )
    construction_firewall_exact = bool(
        strict_json_equal(
            checkpoint_seal.get("construction"), expected_construction
        )
        and type(checkpoint_seal.get("construction_word_count")) is int
        and checkpoint_seal.get("construction_word_count")
        == len(expected_construction_bank.construction)
        and construction_digests == {expected_construction["construction_digest"]}
        and len(construction_record_checks) == expected_runs
        and all(construction_record_checks)
    )
    expected_heldout = freeze_heldout_bank(
        make_v04_suffix_plan(max_depth=8),
        torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long),
        max_suffixes=None,
    )
    heldout_bank_exact = bool(
        strict_json_equal(eval_bank.get("heldout_bank"), expected_heldout.to_dict())
        and strict_json_equal(
            eval_bank.get("heldout_words"),
            [list(word) for word in expected_heldout.words],
        )
        and strict_json_equal(
            eval_bank.get("heldout_relation_signatures"),
            [list(value) for value in expected_heldout.relation_signatures],
        )
    )
    heldout_metadata = eval_bank.get("heldout_bank")
    heldout_metadata = heldout_metadata if isinstance(heldout_metadata, Mapping) else {}
    seal_before_eval = phase_times["checkpoint_sealed"] < phase_times["evaluation_bank_materialized"]
    assay = {
        "A01_paired_initialization_and_stream": _gate(
            init_stream_checks,
            (
                "identical full/shared initialization, accepted episode-stream, and "
                "terminal-proposal-stream digests within every seed"
            ),
            all(init_stream_checks) and len(init_stream_checks) == len(config["seeds"]),
        ),
        "A02_construction_bank_shared": _gate(
            {
                "digests": sorted(construction_digests),
                "seal_construction": checkpoint_seal.get("construction"),
                "word_count": checkpoint_seal.get("construction_word_count"),
                "canonical_match": construction_firewall_exact,
            },
            (
                "every checkpoint and the seal match the exact canonical 20-word "
                "nonempty horizon-4 construction set, whose induced actions exclude "
                "identity and r2"
            ),
            construction_firewall_exact,
        ),
        "A03_checkpoint_audit_firewall": _gate(
            strict_files,
            "no heldout/evaluation bank content in any checkpoint",
            strict_files,
        ),
        "A04_reserved_terminal_action_holdout": _gate(
            {
                "heldout_words": heldout_metadata.get("word_count"),
                "heldout_groups": heldout_metadata.get("relation_group_count"),
                "split_verified": heldout_metadata.get("split_verified"),
                "fingerprint": heldout_metadata.get("fingerprint"),
                "canonical_match": heldout_bank_exact,
            },
            (
                "171 exhaustive horizon-8 continuations (including empty) in two reserved "
                "terminal-action groups; "
                "endpoint split verified"
            ),
            heldout_bank_exact
            and type(heldout_metadata.get("word_count")) is int
            and heldout_metadata.get("word_count")
            == FROZEN_REGISTERED_DESIGN["heldout_continuation_count"]
            and type(heldout_metadata.get("relation_group_count")) is int
            and heldout_metadata.get("relation_group_count") == 2
            and heldout_metadata.get("split_verified") is True,
        ),
        "A05_checkpoint_before_evaluation_bank": _gate(
            phase_times,
            "checkpoint seal timestamp precedes evaluation-bank materialization",
            seal_before_eval,
        ),
        "A06_exact_episode_contracts": _gate(
            eval_bank.get("episode_receipts", {}).get("contracts"),
            (
                "every registered bank has the exact family, contexts, depth, tensor "
                "geometry, one-hot maps, canonical conjugated action, targets, "
                "intermediates, and slot mapping"
            ),
            validate_eval_episode_contracts(eval_bank, config),
        ),
        "A07_nonvacuous_exact_feshbach_split": _gate(
            ranks,
            "retained rank == 8 and nuisance rank == 4 for every evaluated checkpoint",
            len(ranks) == expected_runs
            and all(
                type(value[0]) is int
                and type(value[1]) is int
                and value == (8, 4)
                for value in ranks
            ),
        ),
        "A08_switched_bank_contract": _gate(
            {
                "word_length": eval_bank["switch_bank"]["word_length"],
                "word_count": eval_bank["switch_bank"]["word_count"],
                "exhaustive": eval_bank["switch_bank"]["exhaustive"],
                "contexts": config["switched_contexts"],
            },
            (
                "exactly all 256 length-8 words for pilot; declared deterministic bank "
                "with configured contexts otherwise"
            ),
            validate_switch_bank(profile, config, eval_bank["switch_bank"]),
        ),
        "A09_terminal_endpoint_group_firewall": _gate(
            terminal_firewall_rows,
            (
                "every run uses the frozen identity/r2 endpoint-rejection policy; accepted "
                "count equals steps*batch and proposal/rejection counts close exactly"
            ),
            (
                len(terminal_firewall_rows) == expected_runs
                and all(
                    row["policy_digest"] == terminal_firewall_policy_digest()
                    and all(
                        type(row[name]) is int
                        for name in (
                            "proposal_count",
                            "accepted",
                            "rejected",
                            "identity_rejections",
                            "r2_rejections",
                        )
                    )
                    and all(
                        row[name] >= 0
                        for name in (
                            "proposal_count",
                            "accepted",
                            "rejected",
                            "identity_rejections",
                            "r2_rejections",
                        )
                    )
                    and row["proposal_count"] >= row["accepted"]
                    and row["accepted"]
                    == int(config["training"]["steps"])
                    * int(config["training"]["batch_size"])
                    and row["proposal_count"] == row["accepted"] + row["rejected"]
                    and row["rejected"]
                    == row["identity_rejections"] + row["r2_rejections"]
                    and isinstance(row["proposal_stream_digest"], str)
                    and len(row["proposal_stream_digest"]) == 64
                    and all(
                        character in "0123456789abcdef"
                        for character in row["proposal_stream_digest"]
                    )
                    for row in terminal_firewall_rows
                )
            ),
        ),
        "A10_hard_polar_isometry": _gate(
            polar_geometry_rows,
            (
                "both polar arms pass exact O(12) matrix and finite-bank projective-gain "
                "implementation checks for every seed"
            ),
            (
                len(polar_geometry_rows) == len(config["seeds"]) * len(POLAR_ARMS)
                and all(
                    row["hard_isometry_pass"] is True
                    and row["projective_switched_gain_sanity_pass"] is True
                    for row in polar_geometry_rows
                )
            ),
        ),
        "A11_raw_prepolar_singular_diagnostic": _gate(
            polar_geometry_rows,
            (
                "raw pre-polar relative singular values are recorded for both polar arms; "
                "conditioning below 1e-4 is a warning, not a closure failure"
            ),
            (
                len(polar_geometry_rows) == len(config["seeds"]) * len(POLAR_ARMS)
                and all(
                    "raw_relative_minimum_singular_value" in row
                    and "raw_prepolar_well_conditioned_pass" in row
                    and all_finite([row["raw_relative_minimum_singular_value"]])
                    and float(row["raw_relative_minimum_singular_value"]) >= 0.0
                    and type(row["raw_prepolar_well_conditioned_pass"]) is bool
                    for row in polar_geometry_rows
                )
            ),
        ),
        "A12_ambient_control_geometry": _gate(
            ambient_control_rows,
            (
                "all ambient assays have ideal rank-8/4 construction within 1e-8; "
                "the float32-cast P/Q and random controls retain ranks 8/4 and match "
                "the actually removed Q energy within 1e-6"
            ),
            validate_ambient_control_rows(
                ambient_control_rows,
                expected_runs,
                expected_seeds=config["seeds"],
            ),
        ),
        "A13_complete_primary_closure_grid": _gate(
            closure_coverage_rows,
            (
                "every seed x arm evaluation contains exactly all registered packet "
                "prefixes, both reserved relation groups, every D4 null relation x "
                "repeat cell, and the complete depth x family grid with registered "
                "example counts"
            ),
            (
                len(closure_coverage_rows) == expected_runs
                and all(row["valid"] is True for row in closure_coverage_rows)
            ),
        ),
        "A14_cross_context_operator_control_bank": _gate(
            eval_bank.get("cross_context_operator_control"),
            (
                "independent operator-control slots are balanced by frozen row and "
                "flipped only to exclude exact collisions with either the original or "
                "alternate visible table; both selected collision counts are zero"
            ),
            validate_cross_context_control_contract(
                eval_bank.get("cross_context_operator_control"), config
            ),
        ),
        "A15_packet_result_contract": _gate(
            packet_contract_rows,
            (
                "every seed x arm packet result binds the exact held-out bank, "
                "registered context count, zero boundary, canonical 86/85 relation-group "
                "cardinalities, fraction denominators, and complete numeric summaries"
            ),
            len(packet_contract_rows) == expected_runs
            and all(row["valid"] is True for row in packet_contract_rows),
        ),
        "A16_deep_result_contract": _gate(
            deep_contract_rows,
            (
                "every seed x arm depth x family result has registered counts, fractions "
                "in [0,1], accuracy no greater than finite fraction, and exact pooled, "
                "macro, and minimum arithmetic"
            ),
            len(deep_contract_rows) == expected_runs
            and all(row["valid"] is True for row in deep_contract_rows),
        ),
        "A17_ambient_result_contract": _gate(
            ambient_contract_rows,
            (
                "every seed x arm ambient result has the exact family/condition schema, "
                "registered geometry and thresholds, bounded count-derived fractions, "
                "recomputed performance drops, and coherent attribution status"
            ),
            len(ambient_contract_rows) == expected_runs
            and all(row["valid"] is True for row in ambient_contract_rows),
        ),
        "A18_causal_result_contract": _gate(
            causal_contract_rows,
            (
                "every seed x arm causal result has registered banks and intervention "
                "positions, bounded count-derived fractions, valid eligible denominators, "
                "coherent conditional transitions, and architecture-appropriate controls"
            ),
            len(causal_contract_rows) == expected_runs
            and all(row["valid"] is True for row in causal_contract_rows),
        ),
        "A19_switched_result_contract": _gate(
            switched_contract_rows,
            (
                "every seed x arm switched result binds the exact word bank and "
                "fingerprint, registered contexts, defined denominator, behavioral "
                "accuracy, numeric summaries, and gain/log-gain extrema"
            ),
            len(switched_contract_rows) == expected_runs
            and all(row["valid"] is True for row in switched_contract_rows),
        ),
        "A20_null_result_contract": _gate(
            null_contract_rows,
            (
                "every seed x arm null-loop result binds the exact packet bank and "
                "repeat grid, with valid baseline, conditional denominators, retained "
                "intersection bounds, margin summaries, and first-crossing arithmetic"
            ),
            len(null_contract_rows) == expected_runs
            and all(row["valid"] is True for row in null_contract_rows),
        ),
        "A21_feshbach_result_contract": _gate(
            feshbach_contract_rows,
            (
                "every seed x arm exact Feshbach result has the full rank, metric, "
                "generator-block, and delayed-return schemas with registered counts, "
                "finite nonnegative summaries, and coherent spectral diagnostics"
            ),
            len(feshbach_contract_rows) == expected_runs
            and all(row["valid"] is True for row in feshbach_contract_rows),
        ),
        "A22_hard_polar_result_contract": _gate(
            hard_polar_contract_rows,
            (
                "every seed x arm hard-polar result has its architecture-appropriate "
                "exact schema; polar arms reconcile family and pooled geometry, use "
                "family-specific switched banks, and derive every pass flag"
            ),
            len(hard_polar_contract_rows) == expected_runs
            and all(row["valid"] is True for row in hard_polar_contract_rows),
        ),
    }

    pilot = profile == "pilot" and run_mode == "official"
    primary_rows = [
        scalar_metrics(records[str(seed)][PRIMARY_ARM]["evaluation"], config)
        for seed in config["seeds"]
        if "evaluation" in records.get(str(seed), {}).get(PRIMARY_ARM, {})
    ]
    primary_evaluations = [
        records[str(seed)][PRIMARY_ARM]["evaluation"]
        for seed in config["seeds"]
        if "evaluation" in records.get(str(seed), {}).get(PRIMARY_ARM, {})
    ]

    def all_values(name: str) -> list[float]:
        return [
            float(row[name])
            for row in primary_rows
            if row.get(name) is not None
        ]

    def pilot_test(name: str, predicate: Any) -> bool | None:
        values = all_values(name)
        if not pilot:
            return None
        if len(values) != len(config["seeds"]):
            return False
        if not all_finite(values):
            return False
        return bool(predicate(values))

    def closure_grid_metrics(evaluation: Mapping[str, Any]) -> dict[str, float]:
        """Gate-aligned minima over all prefixes, groups, loops, and repeats."""

        packet = _packet_endpoint_scalars(evaluation, config)
        null = _null_endpoint_scalars(evaluation, config)
        return {
            "packet_membership": (
                float(packet["packet_membership"])
                if packet["packet_membership"] is not None
                else math.nan
            ),
            "packet_margin_p10": (
                float(packet["packet_margin_p10"])
                if packet["packet_margin_p10"] is not None
                else math.nan
            ),
            "null_closure": (
                float(null["null_closure"])
                if null["null_closure"] is not None
                else math.nan
            ),
        }

    # Primary gates and paired packet/null estimands use the per-seed minimum
    # over the entire frozen audit grid.
    primary_grid_rows = [
        closure_grid_metrics(evaluation) for evaluation in primary_evaluations
    ]
    packet_membership = [row["packet_membership"] for row in primary_grid_rows]
    packet_margin = [row["packet_margin_p10"] for row in primary_grid_rows]
    null_closure = [row["null_closure"] for row in primary_grid_rows]
    switched_gain = all_values("switched_max_gain")
    switched_defined = all_values("switched_defined_fraction")
    switched_accuracy = all_values("switched_word_accuracy")
    mechanism = {
        "M01_heldout_packet_membership": _gate(
            packet_membership,
            ">= 0.90 at every audited prefix and in both reserved groups per polar_cr pilot seed",
            (
                all_finite(packet_membership)
                and min(packet_membership)
                >= FROZEN_GATE_THRESHOLDS["packet_membership_minimum"]
                if pilot and len(packet_membership) == len(config["seeds"])
                else None
            ),
        ),
        "M02_heldout_margin_p10": _gate(
            packet_margin,
            "> 0 at every audited prefix and in both reserved groups per polar_cr pilot seed",
            (
                all_finite(packet_margin)
                and min(packet_margin)
                > FROZEN_GATE_THRESHOLDS["packet_margin_p10_strict_minimum"]
                if pilot and len(packet_margin) == len(config["seeds"])
                else None
            ),
        ),
        "M03_null_loop_packet_retention": _gate(
            null_closure,
            (
                ">= 0.90 for null-bank baseline membership, conditional retention, "
                "and post-loop membership for every relation and repeat through 32 "
                "per polar_cr pilot seed"
            ),
            (
                all_finite(null_closure)
                and min(null_closure)
                >= FROZEN_GATE_THRESHOLDS["null_loop_membership_minimum"]
                if pilot and len(null_closure) == len(config["seeds"])
                else None
            ),
        ),
        "M04_switched_projective_gain": _gate(
            switched_gain,
            "hard-polar exhaustive length-8 maximum gain lies in [0.999, 1.001] per pilot seed",
            pilot_test(
                "switched_max_gain",
                lambda v: (
                    min(v)
                    >= FROZEN_GATE_THRESHOLDS["switched_projective_gain_interval"][0]
                    and max(v)
                    <= FROZEN_GATE_THRESHOLDS["switched_projective_gain_interval"][1]
                ),
            ),
        ),
        "M05_switched_domain_defined": _gate(
            switched_defined,
            "defined fraction == 1 per polar_cr pilot seed",
            pilot_test(
                "switched_defined_fraction",
                lambda v: min(v)
                == FROZEN_GATE_THRESHOLDS["switched_defined_fraction"],
            ),
        ),
        "M06_switched_word_accuracy": _gate(
            switched_accuracy,
            "exhaustive length-8 switched-word behavioral accuracy >= 0.95 per polar_cr pilot seed",
            pilot_test(
                "switched_word_accuracy",
                lambda v: min(v)
                >= FROZEN_GATE_THRESHOLDS["switched_word_accuracy_minimum"],
            ),
        ),
    }

    depth_thresholds = {
        int(depth): float(value)
        for depth, value in FROZEN_GATE_THRESHOLDS["d4_accuracy_by_depth"].items()
    }
    d4_observed: dict[str, dict[str, list[float]]] = {}
    transfer_observed: dict[str, dict[str, dict[str, list[float]]]] = {}
    d4_pass = True
    transfer_pass = True
    deep_evaluable = (
        pilot
        and len(primary_rows) == len(config["seeds"])
        and len(primary_evaluations) == len(config["seeds"])
        and all(
            validate_deep_result_contract(evaluation, config)
            for evaluation in primary_evaluations
        )
    )
    if deep_evaluable:
        for depth in config["deep_depths"]:
            d4_values = [
                float(
                    records[str(seed)][PRIMARY_ARM]["evaluation"]["structured_deep_by_depth"]
                    [str(depth)]["per_family"]["d4"]["accuracy"]
                )
                for seed in config["seeds"]
            ]
            d4_finite = [
                float(
                    records[str(seed)][PRIMARY_ARM]["evaluation"]
                    ["structured_deep_by_depth"][str(depth)]["per_family"]["d4"]
                    ["finite_fraction"]
                )
                for seed in config["seeds"]
            ]
            transfer_values = {
                family: [
                    float(
                        records[str(seed)][PRIMARY_ARM]["evaluation"]
                        ["structured_deep_by_depth"][str(depth)]["per_family"][family]
                        ["accuracy"]
                    )
                    for seed in config["seeds"]
                ]
                for family in ("c8", "mixed_cycle")
            }
            transfer_finite = {
                family: [
                    float(
                        records[str(seed)][PRIMARY_ARM]["evaluation"]
                        ["structured_deep_by_depth"][str(depth)]["per_family"][family]
                        ["finite_fraction"]
                    )
                    for seed in config["seeds"]
                ]
                for family in ("c8", "mixed_cycle")
            }
            d4_observed[str(depth)] = {
                "accuracy": d4_values,
                "finite_fraction": d4_finite,
            }
            transfer_observed[str(depth)] = {
                family: {
                    "accuracy": transfer_values[family],
                    "finite_fraction": transfer_finite[family],
                }
                for family in ("c8", "mixed_cycle")
            }
            threshold = depth_thresholds[int(depth)]
            d4_pass = (
                d4_pass
                and all_finite(d4_values)
                and all_finite(d4_finite)
                and min(d4_finite) == 1.0
                and min(d4_values) >= threshold
            )
            transfer_pass = transfer_pass and all(
                all_finite(transfer_values[family])
                and all_finite(transfer_finite[family])
                and min(transfer_finite[family]) == 1.0
                and min(transfer_values[family]) >= threshold
                for family in ("c8", "mixed_cycle")
            )
    capability = {
        "C01_primary_d4_depth_curve": _gate(
            d4_observed,
            (
                "polar_cr per-seed D4 outputs are fully finite and accuracy >= "
                "0.98@128, 0.90@256, 0.75@512"
            ),
            d4_pass if deep_evaluable else None,
        )
    }
    secondary_transfer = {
        "S01_zero_shot_cross_family_depth_curve": _gate(
            transfer_observed,
            (
                "descriptive secondary: polar_cr per-seed C8 and mixed-cycle outputs "
                "are fully finite and accuracy >= 0.98@128, 0.90@256, 0.75@512"
            ),
            transfer_pass if deep_evaluable else None,
        )
    }

    supervised_grid_rows = [
        closure_grid_metrics(records[str(seed)]["polar_supervised"]["evaluation"])
        for seed in config["seeds"]
        if "evaluation"
        in records.get(str(seed), {}).get("polar_supervised", {})
    ]
    objective_cells_complete = (
        pilot
        and len(primary_grid_rows)
        == len(supervised_grid_rows)
        == len(config["seeds"])
    )
    objective_differences: dict[str, list[float]] = {
        metric: [
            primary[metric] - supervised[metric]
            for primary, supervised in zip(primary_grid_rows, supervised_grid_rows)
        ]
        if len(primary_grid_rows) == len(supervised_grid_rows)
        else []
        for metric in ("packet_membership", "packet_margin_p10", "null_closure")
    }
    margin_differences = objective_differences["packet_margin_p10"]
    membership_differences = objective_differences["packet_membership"]
    null_differences = objective_differences["null_closure"]
    margin_evaluable = objective_cells_complete and all_finite(margin_differences)
    membership_evaluable = (
        objective_cells_complete and all_finite(membership_differences)
    )
    null_evaluable = objective_cells_complete and all_finite(null_differences)
    objective_effect = {
        "O01_cr_grid_margin_benefit": _gate(
            {
                "paired_differences": margin_differences,
                "mean_difference": (
                    statistics.fmean(margin_differences)
                    if margin_differences
                    else None
                ),
                "positive_seed_count": sum(value > 0 for value in margin_differences),
            },
            (
                "paired polar_cr minus polar_supervised grid-min margin has positive mean "
                "and is positive in at least two of three pilot seeds"
            ),
            (
                statistics.fmean(margin_differences)
                > FROZEN_GATE_THRESHOLDS[
                    "objective_mean_margin_difference_strict_minimum"
                ]
                and sum(value > 0 for value in margin_differences)
                >= FROZEN_GATE_THRESHOLDS[
                    "objective_margin_positive_seed_minimum"
                ]
                if margin_evaluable
                else None
            ),
        ),
        "O02_cr_grid_membership_nonnegative_direction": _gate(
            {
                "paired_differences": membership_differences,
                "mean_difference": (
                    statistics.fmean(membership_differences)
                    if membership_differences
                    else None
                ),
            },
            (
                "mean paired polar_cr minus polar_supervised grid-min "
                "packet-membership difference is nonnegative"
            ),
            (
                statistics.fmean(membership_differences)
                >= FROZEN_GATE_THRESHOLDS[
                    "objective_mean_membership_difference_minimum"
                ]
                if membership_evaluable
                else None
            ),
        ),
        "O03_cr_null_closure_nonnegative_direction": _gate(
            {
                "paired_differences": null_differences,
                "mean_difference": (
                    statistics.fmean(null_differences)
                    if null_differences
                    else None
                ),
            },
            (
                "developmental direction check: mean paired polar_cr minus "
                "polar_supervised difference in worst baseline/conditional/post-loop "
                "null closure is nonnegative"
            ),
            (
                statistics.fmean(null_differences)
                >= FROZEN_GATE_THRESHOLDS[
                    "objective_mean_null_closure_difference_minimum"
                ]
                if null_evaluable
                else None
            ),
        ),
    }

    state_patch = all_values("state_patch")
    angle_state_control = all_values("angle_matched_state_control")
    reachable_state_control = all_values("reachable_state_control")
    operator_patch = all_values("operator_patch")
    conjugacy_operator_control = all_values("relative_conjugacy_operator_control")
    cross_context_operator_control = all_values("cross_context_operator_control")
    causal_native_accuracy = all_values("causal_native_accuracy")
    state_distinct_fraction = all_values(
        "state_counterfactual_target_distinct_fraction"
    )
    operator_distinct_fraction = all_values(
        "operator_counterfactual_target_distinct_fraction"
    )
    state_eligibility_fraction = all_values("state_transition_eligibility_fraction")
    operator_eligibility_fraction = all_values(
        "operator_transition_eligibility_fraction"
    )
    state_defined_fraction = all_values("state_conditions_defined_minimum")
    operator_defined_fraction = all_values("operator_conditions_defined_minimum")
    state_geometry = [
        evaluation["causal_interventions"].get("state_control_geometry", {})
        for evaluation in primary_evaluations
    ]
    operator_geometry = [
        evaluation["causal_interventions"].get("operator_control_geometry", {})
        for evaluation in primary_evaluations
    ]
    state_geometry_valid = (
        len(state_geometry) == len(config["seeds"])
        and all(
            row.get("defined_fraction") == 1.0
            and float(row.get("maximum_norm_error", math.inf))
            <= FROZEN_GATE_THRESHOLDS["state_control_geometry_tolerance"]
            and float(row.get("maximum_cosine_error", math.inf))
            <= FROZEN_GATE_THRESHOLDS["state_control_geometry_tolerance"]
            and float(row.get("minimum_target_sine", -math.inf))
            > FROZEN_GATE_THRESHOLDS["state_control_geometry_tolerance"]
            for row in state_geometry
        )
    )
    operator_geometry_valid = (
        len(operator_geometry) == len(config["seeds"])
        and all(
            row.get("available") is True
            and row.get("defined_fraction") == 1.0
            and float(row.get("maximum_chord_distance_error", math.inf))
            <= FROZEN_GATE_THRESHOLDS["operator_control_chord_tolerance"]
            and float(row.get("maximum_orthogonality_defect", math.inf))
            <= FROZEN_GATE_THRESHOLDS["operator_control_orthogonality_tolerance"]
            and row.get("determinant_component_match_fraction") == 1.0
            and float(row.get("minimum_separation_from_alternate", -math.inf))
            > FROZEN_GATE_THRESHOLDS[
                "operator_control_separation_strict_minimum"
            ]
            and row.get("cross_context_defined_fraction") == 1.0
            and row.get("cross_context_selected_original_table_collision_count")
            == 0
            and row.get("cross_context_selected_alternate_table_collision_count")
            == 0
            and float(
                row.get("minimum_cross_context_separation_from_original", -math.inf)
            )
            > FROZEN_GATE_THRESHOLDS[
                "operator_control_separation_strict_minimum"
            ]
            and float(
                row.get("minimum_cross_context_separation_from_alternate", -math.inf)
            )
            > FROZEN_GATE_THRESHOLDS[
                "operator_control_separation_strict_minimum"
            ]
            for row in operator_geometry
        )
    )
    attribution = {
        "T01_complete_paired_2x2": _gate(
            {
                "expected_cells": expected_runs,
                "completed_cells": successful_evaluation,
                "contrast_analysis_available": bool(paired_analysis.get("available")),
            },
            "all four paired raw/polar x supervised/CR cells available",
            successful_evaluation == expected_runs,
        ),
        "T02_causal_state_patch_specificity": _gate(
            {
                "native_original": causal_native_accuracy,
                "counterfactual_target_distinct_fraction": state_distinct_fraction,
                "transition_eligibility_fraction": state_eligibility_fraction,
                "minimum_defined_fraction": state_defined_fraction,
                "patch": state_patch,
                "angle_matched_control": angle_state_control,
                "reachable_wrong_control": reachable_state_control,
                "geometry": state_geometry,
            },
            (
                "on natively correct cases with distinct targets, polar_cr state patch "
                ">= 0.90; native accuracy and eligibility >= 0.90; all relevant outputs "
                "finite; angle-matched and reachable-wrong controls <= 0.40; geometry "
                "receipts valid per pilot seed"
            ),
            (
                len(state_patch)
                == len(angle_state_control)
                == len(reachable_state_control)
                == len(causal_native_accuracy)
                == len(state_distinct_fraction)
                == len(state_eligibility_fraction)
                == len(state_defined_fraction)
                == len(config["seeds"])
                and all_finite(state_patch)
                and all_finite(angle_state_control)
                and all_finite(reachable_state_control)
                and all_finite(causal_native_accuracy)
                and all_finite(state_distinct_fraction)
                and all_finite(state_eligibility_fraction)
                and all_finite(state_defined_fraction)
                and min(causal_native_accuracy)
                >= FROZEN_GATE_THRESHOLDS["causal_native_accuracy_minimum"]
                and min(state_distinct_fraction)
                == FROZEN_GATE_THRESHOLDS[
                    "causal_counterfactual_distinct_fraction"
                ]
                and min(state_eligibility_fraction)
                >= FROZEN_GATE_THRESHOLDS["causal_native_accuracy_minimum"]
                and min(state_defined_fraction)
                == FROZEN_GATE_THRESHOLDS["causal_defined_fraction"]
                and min(state_patch)
                >= FROZEN_GATE_THRESHOLDS["causal_patch_accuracy_minimum"]
                and max(angle_state_control)
                <= FROZEN_GATE_THRESHOLDS["causal_control_accuracy_maximum"]
                and max(reachable_state_control)
                <= FROZEN_GATE_THRESHOLDS["causal_control_accuracy_maximum"]
                and state_geometry_valid
                if pilot
                else None
            ),
        ),
        "T03_causal_operator_patch_specificity": _gate(
            {
                "native_original": causal_native_accuracy,
                "counterfactual_target_distinct_fraction": operator_distinct_fraction,
                "transition_eligibility_fraction": operator_eligibility_fraction,
                "minimum_defined_fraction": operator_defined_fraction,
                "patch": operator_patch,
                "relative_conjugacy_control": conjugacy_operator_control,
                "cross_context_control": cross_context_operator_control,
                "geometry": operator_geometry,
            },
            (
                "on natively correct cases with distinct targets, polar_cr operator patch "
                ">= 0.90; native accuracy and eligibility >= 0.90; all relevant outputs "
                "finite; operator-geometry and cross-context controls <= 0.40; geometry "
                "receipts valid per pilot seed"
            ),
            (
                len(operator_patch)
                == len(conjugacy_operator_control)
                == len(cross_context_operator_control)
                == len(causal_native_accuracy)
                == len(operator_distinct_fraction)
                == len(operator_eligibility_fraction)
                == len(operator_defined_fraction)
                == len(config["seeds"])
                and all_finite(operator_patch)
                and all_finite(conjugacy_operator_control)
                and all_finite(cross_context_operator_control)
                and all_finite(causal_native_accuracy)
                and all_finite(operator_distinct_fraction)
                and all_finite(operator_eligibility_fraction)
                and all_finite(operator_defined_fraction)
                and min(causal_native_accuracy)
                >= FROZEN_GATE_THRESHOLDS["causal_native_accuracy_minimum"]
                and min(operator_distinct_fraction)
                == FROZEN_GATE_THRESHOLDS[
                    "causal_counterfactual_distinct_fraction"
                ]
                and min(operator_eligibility_fraction)
                >= FROZEN_GATE_THRESHOLDS["causal_native_accuracy_minimum"]
                and min(operator_defined_fraction)
                == FROZEN_GATE_THRESHOLDS["causal_defined_fraction"]
                and min(operator_patch)
                >= FROZEN_GATE_THRESHOLDS["causal_patch_accuracy_minimum"]
                and max(conjugacy_operator_control)
                <= FROZEN_GATE_THRESHOLDS["causal_control_accuracy_maximum"]
                and max(cross_context_operator_control)
                <= FROZEN_GATE_THRESHOLDS["causal_control_accuracy_maximum"]
                and operator_geometry_valid
                if pilot
                else None
            ),
        ),
    }

    ambient_statuses = [
        {
            "seed": int(seed),
            "family": family,
            "status": row["attribution"]["status"],
            "supports_specific_ambient_attribution": row["attribution"].get(
                "supports_specific_ambient_attribution"
            ),
            "native_accuracy": row.get("conditions", {}).get("native", {}).get(
                "accuracy"
            ),
            "condition_finite_fractions": {
                name: condition.get("finite_fraction")
                for name, condition in row.get("conditions", {}).items()
            },
            "condition_defined_fractions": {
                name: condition.get("defined_fraction")
                for name, condition in row.get("conditions", {}).items()
            },
            "q_ablation_drop": row.get("performance_drops", {}).get(
                "midpoint_q_ablation"
            ),
            "q_specific_excess_drop": row["performance_drops"][
                "q_specific_excess_over_random"
            ],
        }
        for seed in config["seeds"]
        for family, row in records.get(str(seed), {})
        .get(PRIMARY_ARM, {})
        .get("evaluation", {})
        .get("ambient_complement_causality", {})
        .items()
    ]
    ambient_attribution = {
        "D01_specific_ambient_complement_use": _gate(
            ambient_statuses,
            (
                "descriptive only: every polar_cr family has fully finite/defined causal "
                "rollouts, native accuracy >= 0.75, Q drop >= 0.05, and Q-specific "
                "excess over the energy/rank-matched random control >= 0.05; failure "
                "does not invalidate closure"
            ),
            (
                all(
                    row["status"] == "SUPPORTED_SPECIFIC_Q_PERFORMANCE_DROP"
                    and row["supports_specific_ambient_attribution"] is True
                    and _finite(row["native_accuracy"]) is not None
                    and float(row["native_accuracy"])
                    >= FROZEN_GATE_THRESHOLDS[
                        "ambient_native_accuracy_minimum"
                    ]
                    and _finite(row["q_ablation_drop"]) is not None
                    and float(row["q_ablation_drop"])
                    >= FROZEN_GATE_THRESHOLDS[
                        "ambient_accuracy_drop_minimum"
                    ]
                    and _finite(row["q_specific_excess_drop"]) is not None
                    and float(row["q_specific_excess_drop"])
                    >= FROZEN_GATE_THRESHOLDS[
                        "ambient_specificity_margin_minimum"
                    ]
                    and set(row["condition_finite_fractions"])
                    == {
                        "native",
                        "p_confined",
                        "midpoint_q_ablated",
                        "matched_random_rank_control",
                    }
                    and all(
                        _finite(value) == 1.0
                        for value in row["condition_finite_fractions"].values()
                    )
                    and set(row["condition_defined_fractions"])
                    == {
                        "native",
                        "p_confined",
                        "midpoint_q_ablated",
                        "matched_random_rank_control",
                    }
                    and all(
                        _finite(value) == 1.0
                        for value in row["condition_defined_fractions"].values()
                    )
                    for row in ambient_statuses
                )
                if pilot and len(ambient_statuses) == len(config["seeds"]) * 3
                else None
            ),
        )
    }

    def group_status(group: Mapping[str, Mapping[str, Any]]) -> str:
        statuses = {item["status"] for item in group.values()}
        if "FAIL" in statuses:
            return "FAIL"
        if statuses == {"PASS"}:
            return "PASS"
        return "NOT_EVALUATED"

    execution_status = group_status(execution)
    assay_status = group_status(assay)
    mechanism_status = group_status(mechanism)
    capability_status = group_status(capability)
    attribution_status = group_status(attribution)
    secondary_transfer_status = group_status(secondary_transfer)
    ambient_attribution_status = group_status(ambient_attribution)
    objective_effect_status = group_status(objective_effect)
    primary_scientific_statuses = (
        mechanism_status,
        capability_status,
        attribution_status,
    )
    if not pilot or execution_status != "PASS" or assay_status != "PASS":
        full_claim = "NOT_EVALUATED"
    elif all(status == "PASS" for status in primary_scientific_statuses):
        full_claim = "PASS"
    else:
        full_claim = "FAIL"
    return {
        "study_status": (
            "prospective_developmental_fresh_seed_paired_2x2"
            if profile == "pilot" and run_mode == "official"
            else "non_evidentiary_pilot_replay"
            if run_mode == "replay"
            else "developmental_implementation_screen"
            if profile == "screen"
            else "engineering_smoke"
        ),
        "run_mode": run_mode,
        "scientific_failures_are_retained": True,
        "execution_status": execution_status,
        "assay_status": assay_status,
        "mechanism_status": mechanism_status,
        "capability_status": capability_status,
        "attribution_status": attribution_status,
        "secondary_transfer_status": secondary_transfer_status,
        "ambient_attribution_status": ambient_attribution_status,
        "objective_effect_status": objective_effect_status,
        "full_developmental_claim": full_claim,
        "execution_gates": execution,
        "assay_gates": assay,
        "mechanism_gates": mechanism,
        "capability_gates": capability,
        "attribution_gates": attribution,
        "secondary_transfer_gates": secondary_transfer,
        "ambient_attribution_gates": ambient_attribution,
        "objective_effect_gates": objective_effect,
    }


def render_chart(output_dir: Path, aggregate: Mapping[str, Any]) -> list[str]:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return []
    labels = list(ARM_NAMES)
    metrics = (
        ("packet_membership", "Held-out packet membership", (0.0, 1.03)),
        ("d4_accuracy", "Primary D4 deep accuracy", (0.0, 1.03)),
        ("cross_family_minimum_accuracy", "Secondary cross-family minimum", (0.0, 1.03)),
        ("null_closure", "Null-loop packet closure", (0.0, 1.03)),
    )
    figure, axes = plt.subplots(2, 2, figsize=(13, 8), dpi=180)
    color_by_arm = {
        "euclidean_supervised": "#777777",
        "euclidean_cr": "#d95f02",
        "polar_supervised": "#5f9ea0",
        "polar_cr": "#3288bd",
    }
    colors = [color_by_arm[arm] for arm in labels]
    for axis, (metric, title, limits) in zip(axes.flat, metrics):
        values = [aggregate[arm]["metrics"].get(metric, {}).get("mean") for arm in labels]
        heights = [float(value) if value is not None else 0.0 for value in values]
        axis.bar(range(len(labels)), heights, color=colors)
        axis.set_title(title)
        axis.set_xticks(range(len(labels)), labels, rotation=45, ha="right", fontsize=8)
        if limits is not None:
            axis.set_ylim(*limits)
        axis.grid(axis="y", alpha=0.25)
    figure.suptitle("v0.4 clean packet-closure 2x2 outcomes")
    figure.tight_layout()
    path = output_dir / "packet_closure_2x2.png"
    figure.savefig(path)
    plt.close(figure)
    return [path.name]


def _format(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def render_report(result: Mapping[str, Any]) -> str:
    gates = result["gates"]
    aggregate = result["aggregate"]
    paired = result["paired_2x2_analysis"]
    config = result["config"]
    lines = [
        "# Packet-closure training block",
        "",
        "- Author: `Komorebi P.`",
        f"- Profile: `{result['profile']}`",
        f"- Study: `{gates['study_status']}`",
        f"- Execution: `{gates['execution_status']}`",
        f"- Assay: `{gates['assay_status']}`",
        f"- Mechanism: `{gates['mechanism_status']}`",
        f"- Primary D4 capability: `{gates['capability_status']}`",
        f"- Causal attribution: `{gates['attribution_status']}`",
        f"- Secondary cross-family transfer: `{gates['secondary_transfer_status']}`",
        f"- Descriptive ambient-Q attribution: `{gates['ambient_attribution_status']}`",
        f"- Descriptive hard-polar-stratum CR-objective effect: `{gates['objective_effect_status']}`",
        f"- Full developmental claim: `{gates['full_developmental_claim']}`",
        "",
        (
            "Scientific failures are retained. The clean paired 2x2 crosses raw Euclidean-normalized "
            "operators with hard O(12)-polar operators and matched supervised versus demonstration-"
            "aligned composition plus finite-path complement-return (CR) objectives. All cells share "
            "initialization and both accepted and proposal episode streams."
        ),
        "",
        "## Arm outcomes",
        "",
        (
            "Packet membership, continuation margin, and null closure are worst-cell "
            "estimands over every registered prefix, relation group, null relation, and "
            f"repeat through {max(config['null_repeats'])}; deep metrics use depth "
            f"{max(config['deep_depths'])}."
        ),
        "Causal patch/control entries are conditional transition accuracies among same-bank cases with a correct native answer and a distinct counterfactual target. Relative-conjugacy control is inapplicable to raw arms and is shown as unavailable.",
        "",
        "| Arm | Packet | Margin p10 | D4 deep | Xfer min | Null closure | Switch gain/acc | Hard defect | Raw smin | State patch / angle / reachable | Operator patch / conjugacy / cross-context |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARM_NAMES:
        metrics = aggregate[arm]["metrics"]
        get = lambda name, field="mean": metrics.get(name, {}).get(field)
        lines.append(
            f"| `{arm}` | {_format(get('packet_membership'))} | {_format(get('packet_margin_p10'))} | "
            f"{_format(get('d4_accuracy'))} | {_format(get('cross_family_minimum_accuracy'))} | "
            f"{_format(get('null_closure'))} | {_format(get('switched_max_gain'))}/"
            f"{_format(get('switched_word_accuracy'))} | {_format(get('hard_isometry_maximum_defect'))} | "
            f"{_format(get('raw_prepolar_relative_singular_minimum'))} | "
            f"{_format(get('state_patch'))}/{_format(get('angle_matched_state_control'))}/"
            f"{_format(get('reachable_state_control'))} | "
            f"{_format(get('operator_patch'))}/"
            f"{_format(get('relative_conjugacy_operator_control'))}/"
            f"{_format(get('cross_context_operator_control'))} |"
        )
    lines += [
        "",
        "## Paired 2x2 contrasts",
        "",
        "Positive values mean the named first condition has the larger metric; desirability depends on the metric. The interaction is the difference in the CR effect between polar and raw architectures.",
        "",
        "| Metric | Polar main | CR main | CR given raw | CR given polar | Polar given supervised | Interaction |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    if paired.get("available"):
        for metric, summary in paired["metrics"].items():
            if not summary.get("available", True):
                lines.append(
                    f"| `{metric}` | — | — | — | — | — | {summary.get('reason', 'unavailable')} |"
                )
                continue
            contrasts = summary["contrasts"]
            lines.append(
                f"| `{metric}` | {_format(contrasts['polar_architecture_main_effect']['estimate'])} | "
                f"{_format(contrasts['closure_objective_main_effect']['estimate'])} | "
                f"{_format(contrasts['closure_given_raw']['estimate'])} | "
                f"{_format(contrasts['closure_given_polar']['estimate'])} | "
                f"{_format(contrasts['polar_given_supervised']['estimate'])} | "
                f"{_format(contrasts['interaction_difference_in_differences']['estimate'])} |"
            )
    else:
        lines.append(
            f"| unavailable | — | — | — | — | — | {_format(paired.get('reason'))} |"
        )
    for title, key in (
        ("Execution gates", "execution_gates"),
        ("Assay gates", "assay_gates"),
        ("Mechanism gates", "mechanism_gates"),
        ("Primary D4 capability gates", "capability_gates"),
        ("Causal attribution gates", "attribution_gates"),
        ("Secondary cross-family transfer gates", "secondary_transfer_gates"),
        ("Descriptive ambient-Q attribution gates", "ambient_attribution_gates"),
        ("Descriptive hard-polar-stratum CR-objective effect gates", "objective_effect_gates"),
    ):
        lines += ["", f"## {title}", "", "| Gate | Status | Criterion |", "|---|---|---|"]
        for name, gate in gates[key].items():
            lines.append(f"| `{name}` | {gate['status']} | {gate['criterion']} |")
    lines += [
        "",
        "## Audit boundary",
        "",
        "The terminal sampler rejects every loss-bearing D4 word whose complete induced action is identity or r². The horizon-8 evaluation bank was materialized only after all available checkpoints were serialized and hashed. It contains the empty continuation plus all 170 nonempty words through length eight in those two reserved endpoint-action groups. The empty continuation makes current-prefix decoding part of packet membership. Checkpoints contain only the horizon-4 construction words plus aggregate terminal-firewall counts and digests, never rejected or evaluation words.",
        "",
        "The Feshbach and causal ambient audits use an ideal rank-eight anchor plane and rank-four complement, then separately audit the float32 projectors actually applied. Q energy alone is not evidence of use: the descriptive attribution requires finite, defined rollouts and a performance loss under Q ablation beyond a rank- and removed-energy-matched random control within the registered applied tolerance. A negative ambient-Q result does not invalidate packet closure.",
        "",
        "Hard polar isometry is an architectural implementation assay, not evidence that stability was learned. Raw pre-polar singular conditioning is retained as a warning diagnostic and is not a closure gate.",
        "",
        "## Claim boundary",
        "",
        "A successful primary pilot would establish finite-depth packet preservation, tolerance-bounded hard-polar switched control on the registered finite bank, D4 depth extrapolation, and causal state/operator execution in this explicit table-conditioned architecture. Cross-family zero-shot transfer and ambient-Q use are reported separately and cannot be hidden inside the primary closure claim. The experiment would not establish spontaneous Neuralese, an infinite quotient, universal stability, architecture-independent emergence, awareness, or consciousness.",
        "",
    ]
    return "\n".join(lines)


def checkpoint_has_forbidden_audit_content(payload: Mapping[str, Any]) -> bool:
    forbidden = ("heldout", "held_out", "eval_bank", "evaluation_bank", "audit_words")

    def visit(value: Any) -> bool:
        if isinstance(value, Mapping):
            for key, child in value.items():
                lowered = str(key).lower()
                if any(token in lowered for token in forbidden):
                    return True
                if visit(child):
                    return True
        elif isinstance(value, (list, tuple)):
            return any(visit(child) for child in value)
        return False

    return visit(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Train and audit the v0.4 clean packet-closure 2x2")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="smoke")
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--device", default="cpu")
    parser.add_argument(
        "--replay",
        action="store_true",
        help="replay the sealed pilot without labeling it as fresh evidence",
    )
    args = parser.parse_args()
    if args.device != "cpu":
        raise SystemExit(
            "v0.4 registered profiles are sealed to deterministic CPU execution"
        )
    if args.replay and args.profile != "pilot":
        raise SystemExit("--replay is defined only for the sealed pilot profile")
    run_mode = (
        "replay"
        if args.replay
        else "official"
        if args.profile == "pilot"
        else "development"
    )
    config = dict(PROFILES[args.profile])
    output_dir = args.output_dir or ROOT / "results" / f"packet_closure_{args.profile}"
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir
    output_dir = output_dir.resolve()
    try:
        in_tree_relative = output_dir.relative_to(ROOT.resolve())
    except ValueError:
        in_tree_relative = None
    if (
        in_tree_relative is not None
        and (not in_tree_relative.parts or in_tree_relative.parts[0] != "results")
    ):
        raise SystemExit(
            "in-package outputs are permitted only beneath results/ so they cannot alter the source seal"
        )
    canonical_pilot = (ROOT / "results" / "packet_closure_pilot").resolve()
    if args.profile == "pilot":
        if run_mode == "official" and output_dir != canonical_pilot:
            raise SystemExit(
                "the official pilot may write only to results/packet_closure_pilot; "
                "use --replay for any other output"
            )
        if run_mode == "replay" and output_dir == canonical_pilot:
            raise SystemExit(
                "a pilot replay cannot target the canonical official directory"
            )
    device = torch.device(args.device)
    # These workloads are dominated by many tiny 12x12 factorizations.  A
    # single intra-op thread is substantially faster and avoids BLAS launch
    # overhead while preserving deterministic registered execution.
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    live_runtime = runtime_receipt()
    canonical_runtime_match = live_runtime == CANONICAL_PILOT_RUNTIME
    if args.profile == "pilot" and run_mode == "official" and not canonical_runtime_match:
        raise SystemExit(
            "official pilot runtime does not match the frozen Python/PyTorch/NumPy/BLAS platform receipt"
        )
    source_digest = tree_digest(ROOT, source_files(ROOT))
    contract, contract_status = load_contract(args.profile, config)
    if args.profile == "pilot" and not contract_status.get("valid", False):
        raise SystemExit(
            "pilot contract is missing or invalid; no pilot seed was consumed"
        )
    if run_mode == "replay":
        canonical_completion_path = canonical_pilot / "RUN_COMPLETE.json"
        if not canonical_completion_path.is_file():
            raise SystemExit(
                "pilot replay is blocked until the canonical official run is complete"
            )
        canonical_completion = json.loads(
            canonical_completion_path.read_text(encoding="utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON constant: {value}")
            ),
        )
        if not (
            canonical_completion.get("profile") == "pilot"
            and canonical_completion.get("run_mode") == "official"
            and canonical_completion.get("completed") is True
            and canonical_completion.get("execution_status") == "PASS"
            and canonical_completion.get("assay_status") == "PASS"
            and canonical_completion.get("source_digest") == source_digest
            and canonical_completion.get("contract_sha256")
            == contract_status.get("sha256")
        ):
            raise SystemExit(
                "canonical pilot completion is invalid or belongs to another source seal"
            )

    # Claim a fresh output directory only after every preflight check.  Refuse
    # even an empty existing directory so concurrent or repeated official
    # invocations cannot share a partially written target.
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    try:
        output_dir.mkdir(exist_ok=False)
    except FileExistsError as error:
        raise SystemExit(
            f"refusing to write into an existing output directory: {output_dir}"
        ) from error
    checkpoint_dir = output_dir / "checkpoints"
    checkpoint_dir.mkdir(exist_ok=False)
    if contract:
        atomic_json(output_dir / "PREREGISTRATION.json", contract)
    contract_sha256 = contract_status.get("sha256")

    phase_times = {"started": utc_now()}
    started = time.perf_counter()
    records: dict[str, Any] = {str(seed): {} for seed in config["seeds"]}
    checkpoint_receipts: list[dict[str, Any]] = []
    checkpoint_payloads: dict[tuple[int, str], dict[str, Any]] = {}
    registered_construction_bank = make_v04_construction_bank(
        int(config["training"]["auxiliary_max_depth"])
    )
    registered_construction = construction_checkpoint_metadata(
        registered_construction_bank
    )
    construction_words = registered_construction_bank.construction

    # Phase 1: only training-side construction data is exposed through the
    # trainer.  Individual failures are caught so the remaining paired cells
    # and failure trace survive into the final artifact.
    for seed in config["seeds"]:
        train_config = training_config_for(config, seed=int(seed), device=device)
        for arm in ARM_NAMES:
            print(f"[train] seed={seed} arm={arm}", flush=True)
            try:
                trained = train_packet_closure_arm(arm, train_config)
                safe_construction = {
                    "plan_version": trained.plan_version,
                    "construction_digest": trained.construction_digest,
                    "construction_words": [list(word) for word in trained.construction_words],
                }
                if safe_construction != registered_construction:
                    raise RuntimeError(
                        "trainer construction bank differs from the registered firewall"
                    )
                payload = {
                    "schema": f"{SCHEMA_PREFIX}.checkpoint.v1",
                    "version": VERSION,
                    "arm": arm,
                    "arm_spec": asdict(trained.arm),
                    "train_config": config_payload(train_config),
                    "source_digest": source_digest,
                    "contract_sha256": contract_sha256,
                    "state_dict": trained.model.state_dict(),
                    "construction": safe_construction,
                    "terminal_firewall": {
                        "policy_digest": trained.terminal_firewall_policy_digest,
                        "proposal_stream_digest": trained.terminal_proposal_stream_digest,
                        "proposal_count": trained.terminal_proposal_count,
                        "accepted_count": trained.terminal_candidates_accepted,
                        "rejected_count": trained.terminal_candidates_rejected,
                        "identity_rejections": trained.terminal_identity_rejections,
                        "r2_rejections": trained.terminal_r2_rejections,
                    },
                    "provenance": {
                        "initial_state_digest": trained.initial_state_digest,
                        "shared_initialization_digest": trained.shared_initialization_digest,
                        "final_state_digest": trained.final_state_digest,
                        "episode_stream_digest": trained.episode_stream_digest,
                    },
                }
                if checkpoint_has_forbidden_audit_content(payload):
                    raise RuntimeError("checkpoint payload violates the held-out audit firewall")
                path = checkpoint_dir / f"{arm}_seed{seed}.pt"
                torch.save(payload, path)
                receipt = {
                    "arm": arm,
                    "seed": int(seed),
                    "path": path.relative_to(output_dir).as_posix(),
                    "sha256": file_sha256(path),
                    "state_dict_digest": trained.final_state_digest,
                    "construction_digest": trained.construction_digest,
                    "terminal_firewall_policy_digest": trained.terminal_firewall_policy_digest,
                    "terminal_proposal_stream_digest": trained.terminal_proposal_stream_digest,
                    "sealed_at": utc_now(),
                }
                checkpoint_receipts.append(receipt)
                checkpoint_payloads[(int(seed), arm)] = payload
                records[str(seed)][arm] = {
                    "training": {
                        "status": "COMPLETED",
                        "elapsed_seconds": trained.elapsed_seconds,
                        "final_loss": trained.final_loss,
                        "parameter_count": trained.parameter_count,
                        "trainable_parameter_count": trained.trainable_parameter_count,
                        "initial_state_digest": trained.initial_state_digest,
                        "shared_initialization_digest": trained.shared_initialization_digest,
                        "final_state_digest": trained.final_state_digest,
                        "episode_stream_digest": trained.episode_stream_digest,
                        "terminal_proposal_stream_digest": trained.terminal_proposal_stream_digest,
                        "terminal_firewall_policy_digest": trained.terminal_firewall_policy_digest,
                        "terminal_proposal_count": trained.terminal_proposal_count,
                        "terminal_candidates_accepted": trained.terminal_candidates_accepted,
                        "terminal_candidates_rejected": trained.terminal_candidates_rejected,
                        "terminal_identity_rejections": trained.terminal_identity_rejections,
                        "terminal_r2_rejections": trained.terminal_r2_rejections,
                        "construction_digest": trained.construction_digest,
                        "construction_word_count": len(trained.construction_words),
                        "trajectory": trained.trajectory,
                    },
                    "checkpoint": receipt,
                }
                print(
                    f"[train-complete] seed={seed} arm={arm} "
                    f"loss={trained.final_loss:.6g} seconds={trained.elapsed_seconds:.3f}",
                    flush=True,
                )
            except Exception as error:
                records[str(seed)][arm] = {
                    "training": {
                        "status": "FAILED",
                        "error_type": type(error).__name__,
                        "error": str(error),
                        "traceback": traceback.format_exc(),
                    }
                }
                print(
                    f"[train-failed] seed={seed} arm={arm} {type(error).__name__}: {error}",
                    flush=True,
                )

    phase_times["training_finished"] = utc_now()
    preseal_source_digest = tree_digest(ROOT, source_files(ROOT))
    contract_path = ROOT / CONTRACT_FILENAME
    preseal_contract_sha256 = (
        file_sha256(contract_path) if contract_path.is_file() else None
    )
    source_integrity_at_seal = {
        "startup_source_digest": source_digest,
        "preseal_source_digest": preseal_source_digest,
        "startup_contract_sha256": contract_sha256,
        "preseal_contract_sha256": preseal_contract_sha256,
        "valid": (
            preseal_source_digest == source_digest
            and preseal_contract_sha256 == contract_sha256
        ),
    }
    strict_firewall = all(
        not checkpoint_has_forbidden_audit_content(payload)
        for payload in checkpoint_payloads.values()
    )
    seal = {
        "schema": f"{SCHEMA_PREFIX}.checkpoint_seal.v1",
        "version": VERSION,
        "profile": args.profile,
        "source_digest": source_digest,
        "contract_sha256": contract_sha256,
        "sealed_at": utc_now(),
        "construction_word_count": len(construction_words),
        "construction": registered_construction,
        "strict_checkpoint_firewall": strict_firewall,
        "source_integrity_at_seal": source_integrity_at_seal,
        "checkpoints": checkpoint_receipts,
    }
    atomic_json(output_dir / "CHECKPOINT_SEAL.json", seal)
    checkpoint_seal_sha256 = file_sha256(output_dir / "CHECKPOINT_SEAL.json")
    phase_times["checkpoint_sealed"] = utc_now()

    # Phase 2: materialize evaluation-only words *after* the checkpoint seal.
    audit_plan = make_v04_suffix_plan(max_depth=8)
    transitions = torch.from_numpy(canonical_maps("d4")).to(dtype=torch.long)
    frozen_heldout = freeze_heldout_bank(audit_plan, transitions, max_suffixes=None)
    switched_words = sample_switch_words(
        num_actions=2,
        word_length=int(config["switched_word_length"]),
        count=int(config["switched_word_count"]),
        seed=derive_seed(int(config["eval_seed_base"]), "switch_words"),
        include_constant_words=True,
    )
    banks, bank_receipts = make_eval_banks(config)
    cross_context_contract = independent_cross_context_bank_contract(
        banks["intervention"],
        banks["intervention_operator_control"],
        operator_step=int(config["intervention_operator_step_zero_indexed"]),
    )
    eval_bank_record = {
        "schema": f"{SCHEMA_PREFIX}.evaluation_bank.v1",
        "version": VERSION,
        "profile": args.profile,
        "source_digest": source_digest,
        "contract_sha256": contract_sha256,
        "checkpoint_seal_sha256": checkpoint_seal_sha256,
        "materialized_at": utc_now(),
        "heldout_bank": frozen_heldout.to_dict(),
        "heldout_words": [list(word) for word in frozen_heldout.words],
        "heldout_relation_signatures": [list(value) for value in frozen_heldout.relation_signatures],
        "switch_bank": {
            "word_length": int(config["switched_word_length"]),
            "word_count": len(switched_words),
            "contexts": int(config["switched_contexts"]),
            "exhaustive": len(switched_words) == 2 ** int(config["switched_word_length"]),
            "words": [list(word) for word in switched_words],
        },
        "cross_context_operator_control": cross_context_contract,
        "episode_receipts": bank_receipts,
    }
    atomic_json(output_dir / "EVAL_BANK.json", eval_bank_record)
    evaluation_bank_sha256 = file_sha256(output_dir / "EVAL_BANK.json")
    phase_times["evaluation_bank_materialized"] = utc_now()

    # Phase 3: reconstruct from sealed payloads and evaluate frozen state.
    for seed in config["seeds"]:
        train_config = training_config_for(config, seed=int(seed), device=device)
        for arm in ARM_NAMES:
            if (int(seed), arm) not in checkpoint_payloads:
                continue
            print(f"[evaluate] seed={seed} arm={arm}", flush=True)
            try:
                receipt = records[str(seed)][arm]["checkpoint"]
                checkpoint_path = output_dir / receipt["path"]
                if file_sha256(checkpoint_path) != receipt["sha256"]:
                    raise RuntimeError("checkpoint hash changed after the seal")
                payload = torch.load(
                    checkpoint_path,
                    map_location="cpu",
                    weights_only=True,
                )
                if payload.get("schema") != f"{SCHEMA_PREFIX}.checkpoint.v1":
                    raise RuntimeError("checkpoint schema mismatch after reload")
                if payload.get("version") != VERSION or payload.get("arm") != arm:
                    raise RuntimeError("checkpoint version/arm mismatch after reload")
                if payload.get("source_digest") != source_digest:
                    raise RuntimeError("checkpoint source digest mismatch after reload")
                if payload.get("contract_sha256") != contract_sha256:
                    raise RuntimeError("checkpoint contract hash mismatch after reload")
                model = build_packet_closure_model(train_config, arm)
                model.load_state_dict(payload["state_dict"], strict=True)
                model.to(device).eval()
                if state_dict_digest(model) != payload["provenance"]["final_state_digest"]:
                    raise RuntimeError("reloaded state_dict digest differs from sealed checkpoint")
                records[str(seed)][arm]["checkpoint_reload_verified"] = True
                evaluation = evaluate_model(
                    model,
                    config,
                    banks,
                    audit_plan,
                    switched_words,
                    arm=arm,
                    seed=int(seed),
                    device=device,
                )
                records[str(seed)][arm]["evaluation"] = evaluation
                records[str(seed)][arm]["evaluation_provenance"] = {
                    "checkpoint_sha256": receipt["sha256"],
                    "evaluation_bank_sha256": evaluation_bank_sha256,
                    "source_digest": source_digest,
                    "contract_sha256": contract_sha256,
                }
                records[str(seed)][arm]["evaluation_status"] = "COMPLETED"
                print(f"[evaluate-complete] seed={seed} arm={arm}", flush=True)
            except Exception as error:
                records[str(seed)][arm]["evaluation_status"] = "FAILED"
                records[str(seed)][arm]["evaluation_error"] = {
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "traceback": traceback.format_exc(),
                }
                print(
                    f"[evaluate-failed] seed={seed} arm={arm} {type(error).__name__}: {error}",
                    flush=True,
                )

    phase_times["evaluation_finished"] = utc_now()
    final_source_digest = tree_digest(ROOT, source_files(ROOT))
    final_contract_sha256 = (
        file_sha256(contract_path) if contract_path.is_file() else None
    )
    source_integrity = {
        **source_integrity_at_seal,
        "final_source_digest": final_source_digest,
        "final_contract_sha256": final_contract_sha256,
        "valid": bool(
            source_integrity_at_seal["valid"]
            and final_source_digest == source_digest
            and final_contract_sha256 == contract_sha256
        ),
    }
    aggregate = aggregate_records(records, config)
    paired_analysis = paired_2x2_analysis(records, config)
    gates = adjudicate(
        args.profile,
        config,
        contract_status,
        records,
        aggregate,
        paired_analysis,
        seal,
        eval_bank_record,
        phase_times,
        run_mode=run_mode,
        source_integrity=source_integrity,
    )
    elapsed = time.perf_counter() - started
    result = {
        "schema": f"{SCHEMA_PREFIX}.result.v1",
        "version": VERSION,
        "profile": args.profile,
        "run_mode": run_mode,
        "developmental": True,
        "pilot_seed_policy": {
            "seeds": [101, 211, 307],
            "status": (
                "consumed_by_this_run"
                if args.profile == "pilot" and run_mode == "official"
                else "replayed_registered_seeds"
                if args.profile == "pilot"
                else "untouched"
            ),
        },
        "source_digest": source_digest,
        "contract_sha256": contract_sha256,
        "checkpoint_seal_sha256": checkpoint_seal_sha256,
        "evaluation_bank_sha256": evaluation_bank_sha256,
        "runtime": {
            "live": live_runtime,
            "canonical_pilot": CANONICAL_PILOT_RUNTIME,
            "canonical_match": canonical_runtime_match,
        },
        "source_integrity": source_integrity,
        "config": config,
        "phase_times": phase_times,
        "checkpoint_seal": seal,
        "evaluation_bank": {
            "path": "EVAL_BANK.json",
            "heldout_bank": eval_bank_record["heldout_bank"],
            "switch_bank": {
                key: value for key, value in eval_bank_record["switch_bank"].items() if key != "words"
            },
        },
        "records": records,
        "aggregate": aggregate,
        "paired_2x2_analysis": paired_analysis,
        "gates": gates,
        "elapsed_seconds": elapsed,
    }
    atomic_json(output_dir / "RESULTS.json", result)
    atomic_json(output_dir / "GATES.json", gates)
    environment = {
        "schema": f"{SCHEMA_PREFIX}.environment.v1",
        "version": VERSION,
        "profile": args.profile,
        "run_mode": run_mode,
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "device": str(device),
        "torch_threads": torch.get_num_threads(),
        "deterministic_algorithms": torch.are_deterministic_algorithms_enabled(),
        "runtime_receipt": live_runtime,
        "canonical_pilot_runtime": CANONICAL_PILOT_RUNTIME,
        "canonical_runtime_match": canonical_runtime_match,
        "source_integrity_valid": source_integrity["valid"],
        "source_digest": source_digest,
        "contract_sha256": contract_sha256,
        "evaluation_bank_sha256": evaluation_bank_sha256,
    }
    atomic_json(output_dir / "ENVIRONMENT.json", environment)
    charts = render_chart(output_dir, aggregate)
    atomic_text(output_dir / "REPORT.md", render_report(result))
    completion = {
        "schema": f"{SCHEMA_PREFIX}.completion.v1",
        "version": VERSION,
        "profile": args.profile,
        "run_mode": run_mode,
        "source_digest": source_digest,
        "contract_sha256": contract_sha256,
        "canonical_runtime_match": canonical_runtime_match,
        "source_integrity_valid": source_integrity["valid"],
        "completed": (
            gates["execution_status"] == "PASS"
            and gates["assay_status"] == "PASS"
        ),
        "scientific_gate_failure_retained": any(
            gates[name] == "FAIL"
            for name in (
                "mechanism_status",
                "capability_status",
                "attribution_status",
                "secondary_transfer_status",
                "ambient_attribution_status",
                "objective_effect_status",
            )
        ),
        "execution_status": gates["execution_status"],
        "assay_status": gates["assay_status"],
        "mechanism_status": gates["mechanism_status"],
        "capability_status": gates["capability_status"],
        "attribution_status": gates["attribution_status"],
        "secondary_transfer_status": gates["secondary_transfer_status"],
        "ambient_attribution_status": gates["ambient_attribution_status"],
        "objective_effect_status": gates["objective_effect_status"],
        "full_developmental_claim": gates["full_developmental_claim"],
        "results_sha256": file_sha256(output_dir / "RESULTS.json"),
        "gates_sha256": file_sha256(output_dir / "GATES.json"),
        "report_sha256": file_sha256(output_dir / "REPORT.md"),
        "environment_sha256": file_sha256(output_dir / "ENVIRONMENT.json"),
        "checkpoint_seal_sha256": checkpoint_seal_sha256,
        "evaluation_bank_sha256": evaluation_bank_sha256,
        "charts": charts,
        "elapsed_seconds": elapsed,
        "finished_at": utc_now(),
    }
    atomic_json(output_dir / "RUN_COMPLETE.json", completion)
    print(json.dumps(json_ready(completion), sort_keys=True, allow_nan=False))
    # Scientific failures are data. Execution or assay-integrity failures are errors.
    return 0 if completion["completed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
