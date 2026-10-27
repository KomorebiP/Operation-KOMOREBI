#!/usr/bin/env python3
"""Prospective fresh-bank semantic-retraction factorial for sealed v0.4 models.

This NumPy-only runner tests one frozen selector by section factorial.  The
production bank is unavailable until after the design commit, and the learned
path stays locked until protocol, preflight, bank, and armed receipts agree.
"""

from __future__ import annotations

import argparse
import base64
from collections import OrderedDict
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import io
import itertools
import json
import math
import os
from pathlib import Path
import pickle
import platform
import shutil
import stat
import sys
import time
from typing import Any, Iterable, Mapping, Sequence
import zipfile

import numpy as np


AUTHOR = "Komorebi P."
VERSION = "0.3.0"
EXPECTED_NUMPY_VERSION = "2.3.5"
RESULT_SCHEMA = "komorebi.neuralese.semantic_retraction_factorial_result.v1"
PROTOCOL_SCHEMA = "komorebi.neuralese.semantic_retraction_factorial_protocol.v1"
FROZEN_STATUS = "FROZEN_PROSPECTIVE_FRESH_BANK_FACTORIAL"

ARMS = (
    "euclidean_supervised",
    "euclidean_cr",
    "polar_supervised",
    "polar_cr",
)
SEEDS = (101, 211, 307)
N_STATES = 8
HIDDEN_DIM = 12
CALIBRATION_CONTEXTS = 64
EVALUATION_CONTEXTS = 64
CALIBRATION_PREFIXES = 8
EVALUATION_PREFIXES = 8
PREFIX_LENGTH = 64
SUFFIX_MAX_LENGTH = 6
INTERVENTIONS = (
    "native",
    "oracle_anchor",
    "oracle_prototype",
    "decoder_anchor",
    "decoder_prototype",
    "anchor_nearest_anchor",
    "anchor_nearest_prototype",
    "prototype_nearest_anchor",
    "prototype_nearest_prototype",
    "anchor_projection",
    "wrong_anchor_control",
    "wrong_prototype_control",
)
PROTOTYPE_STATE_CONDITIONS = frozenset(
    {
        "oracle_prototype",
        "decoder_prototype",
        "anchor_nearest_prototype",
        "prototype_nearest_prototype",
        "wrong_prototype_control",
    }
)
NORMALIZATION_EPS = np.float32(1e-8)
PROJECTOR_RESIDUAL_TOLERANCE = 1e-5
PROJECTOR_RANK_GAP_FACTOR = 100.0
RAY_NORM_STRICT_MINIMUM = 1e-12
PRIMARY_GATE_CONTRACT = {
    "primary_arm": "polar_cr",
    "horizons": [5, 6],
    "selector_accuracy_minimum": 0.99,
    "selector_worst_context_minimum": 0.98,
    "conditional_accuracy_minimum": 0.995,
    "unconditional_accuracy_minimum": 0.99,
    "oracle_accuracy_minimum": 0.995,
    "all_words_correct_coverage_minimum": 0.99,
    "worst_context_accuracy_minimum": 0.95,
    "damage_given_native_correct_maximum": 0.005,
    "oracle_accuracy_gap_maximum": 0.01,
    "native_error_rate_for_reduction_gate": 0.01,
    "net_native_error_reduction_minimum": 0.50,
    "reduction_gate_requires_all_required_strata_evaluable": True,
    "prototype_section_decoding_minimum": 1.0,
    "one_step_commutation_minimum": 0.99,
    "one_step_worst_context_minimum": 0.95,
    "reset_idempotence_hidden_tolerance": 1e-6,
    "defined_ray_norm_strict_minimum": RAY_NORM_STRICT_MINIMUM,
    "wrong_prototype_counterfactual_minimum": 0.95,
    "wrong_prototype_factual_leakage_maximum": 0.05,
    "arm_aggregation": "3_of_3_checkpoint_AND",
    "cohort_aggregation": "4_of_4_arm_AND",
}
CLAIM_BOUNDARY_CONTRACT = {
    "domain": "finite_D4_decision_repair",
    "maximum_suffix_length": 6,
    "checkpoint_cohort": "sealed_existing_v0.4_four_arm_three_seed_panel",
    "prospective_dimension": "fresh_cases_only_not_model_discovery",
    "independent_checkpoint_replication": False,
    "architecture_independent_evidence": False,
    "unrestricted_language_or_task_claim": False,
    "global_additive_quotient_claim": False,
    "exact_hidden_state_equivalence_claim": False,
    "universal_neuralese_claim": False,
    "backend_equivalence_claim": False,
}
EXPECTED_ARCHIVE_SHA256 = "4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d"
EXPECTED_SEAL_SHA256 = "78f8fad00b8a50edc6286b43edcc0c7433f25d9a5e39fd05c00a0f77d11d73d4"
PARENT_RELEASE_SHA256 = "dc380967c8ee0aa5bd039fe9d9765b21d22ce534044e4df304962fb691cbf4e6"
V02_SPEND_RECEIPT_SHA256 = "65b399852d338569e4775bbbe7177a94094619d8acd70f8c72017e79843f9c01"

HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "PROTOCOL.json"
FREEZE_RECEIPT_PATH = HERE / "FROZEN_PROTOCOL.sha256"
BANK_SEAL_PATH = HERE / "FRESH_BANK_SEAL.json"
ARMED_RECEIPT_PATH = HERE / "ARMED_RECEIPT.json"
ARMED_RECEIPT_HASH_PATH = HERE / "ARMED_RECEIPT.sha256"
PREFLIGHT_PATH = HERE.parent / "preflight" / "PREFLIGHT.json"
SYNTHETIC_TESTS_PATH = HERE.parent / "preflight" / "SYNTHETIC_TESTS.json"
SCIENTIFIC_BOUNDARIES_PATH = HERE.parent / "reports" / "SCIENTIFIC_BOUNDARIES.md"
SPENT_BANK_REGISTRY_PATH = HERE.parent / "lineage" / "SPENT_BANK_REGISTRY.json"
PARENT_RELEASE_PATH = HERE.parent / "lineage" / "immutable" / "Komorebi_Neuralese_Semantic_Retraction_v0.2.0_ABORTED_PRIMARY_WITH_POSTHOC_CROSSCHECK.zip"
STATE_DIRECTORY = HERE / "state"
SPEND_PATH = STATE_DIRECTORY / "EVALUATION_BANK_SPENT.json"
RESULTS_DIRECTORY = HERE / "results"
DEFAULT_BUNDLE = RESULTS_DIRECTORY / "RESULTS.bundle"
RESULT_RESERVATION_NAME = "RESULT.json.reserved"
COMMIT_RESERVATION_NAME = "COMMIT.json.reserved"
RESULT_COMMIT_NAME = "COMMIT.json"
HARDLINK_CANARY_NAME = ".publication_canary"
MAX_RESULT_BYTES = 1024 * 1024 * 1024
COMMIT_RESERVATION_BYTES = 64 * 1024
MIN_FREE_BYTES_BEFORE_SPEND = 2 * 1024 * 1024 * 1024
SPEND_STATUS = "SPENT_BEFORE_ANY_FRESH_BANK_CHECKPOINT_EVALUATION"
OUTPUT_LIFECYCLE_CONTRACT = {
    "result_format": "single_canonical_json",
    "result_filename": "RESULT.json",
    "terminal_commit_filename": RESULT_COMMIT_NAME,
    "terminal_commit_status": "VERIFIED_RESULT_COMMITTED",
    "stage_verify_before_terminal_commit": True,
    "physical_result_reservation_bytes": MAX_RESULT_BYTES,
    "physical_commit_reservation_bytes": COMMIT_RESERVATION_BYTES,
    "minimum_free_bytes_before_reservation": MIN_FREE_BYTES_BEFORE_SPEND,
    "same_directory_hardlink_publication_canary_before_spend": True,
}

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))


@dataclass(frozen=True)
class StorageType:
    name: str


@dataclass(frozen=True)
class StorageRef:
    key: str
    dtype: str
    count: int


@dataclass(frozen=True)
class TensorDescriptor:
    storage: StorageRef
    offset: int
    size: tuple[int, ...]
    stride: tuple[int, ...]
    requires_grad: bool


@dataclass(frozen=True)
class ResultReservation:
    bundle: Path
    result_path: Path
    commit_path: Path
    result_device: int
    result_inode: int
    commit_device: int
    commit_inode: int
    free_bytes_before: int
    hardlink_publication_canary_completed: bool


@dataclass(frozen=True)
class PreparedCheckpoint:
    arm: str
    seed: int
    arrays: Mapping[str, np.ndarray]
    checkpoint_receipt: Mapping[str, object]


def _rebuild_tensor_descriptor(
    storage: StorageRef,
    offset: int,
    size: tuple[int, ...],
    stride: tuple[int, ...],
    requires_grad: bool,
    backward_hooks: object,
    *unused: object,
) -> TensorDescriptor:
    del backward_hooks, unused
    return TensorDescriptor(
        storage=storage,
        offset=int(offset),
        size=tuple(int(value) for value in size),
        stride=tuple(int(value) for value in stride),
        requires_grad=bool(requires_grad),
    )


class RestrictedTorchUnpickler(pickle.Unpickler):
    """Decode only inert tensor descriptors and primitive containers."""

    _storage_dtypes = {
        "FloatStorage": "<f4",
        "DoubleStorage": "<f8",
        "LongStorage": "<i8",
        "IntStorage": "<i4",
        "BoolStorage": "?",
        "HalfStorage": "<f2",
    }

    def find_class(self, module: str, name: str) -> object:
        if (module, name) == ("collections", "OrderedDict"):
            return OrderedDict
        if (module, name) in {
            ("torch._utils", "_rebuild_tensor_v2"),
            ("torch._utils", "_rebuild_tensor"),
        }:
            return _rebuild_tensor_descriptor
        if module == "torch" and name in self._storage_dtypes:
            return StorageType(name)
        raise pickle.UnpicklingError(f"blocked checkpoint global: {module}.{name}")

    def persistent_load(self, persistent_id: object) -> StorageRef:
        if not (
            isinstance(persistent_id, tuple)
            and len(persistent_id) == 5
            and persistent_id[0] == "storage"
            and isinstance(persistent_id[1], StorageType)
        ):
            raise pickle.UnpicklingError("blocked checkpoint persistent ID")
        storage_type = persistent_id[1]
        return StorageRef(
            key=str(persistent_id[2]),
            dtype=self._storage_dtypes[storage_type.name],
            count=int(persistent_id[4]),
        )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_json_digest(value: object) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256_bytes(encoded)


def json_ready(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def load_checkpoint_restricted(path: Path) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Read a weights-only state dict without importing or executing torch."""

    with zipfile.ZipFile(path) as archive:
        data_names = [name for name in archive.namelist() if name.endswith("/data.pkl")]
        if len(data_names) != 1:
            raise ValueError(f"checkpoint must contain exactly one data.pkl: {path}")
        data_name = data_names[0]
        prefix = data_name[: -len("data.pkl")]
        payload = RestrictedTorchUnpickler(io.BytesIO(archive.read(data_name))).load()
        if not isinstance(payload, dict) or not isinstance(payload.get("state_dict"), dict):
            raise ValueError(f"checkpoint has no state_dict mapping: {path}")

        arrays: dict[str, np.ndarray] = {}
        for name, descriptor in payload["state_dict"].items():
            if not isinstance(name, str) or not isinstance(descriptor, TensorDescriptor):
                raise ValueError(f"invalid tensor descriptor in {path}")
            if len(descriptor.size) != len(descriptor.stride):
                raise ValueError(f"size/stride mismatch for {name}")
            if any(value < 0 for value in descriptor.size + descriptor.stride):
                raise ValueError(f"negative tensor geometry for {name}")
            dtype = np.dtype(descriptor.storage.dtype)
            raw = archive.read(prefix + "data/" + descriptor.storage.key)
            if len(raw) != descriptor.storage.count * dtype.itemsize:
                raise ValueError(f"storage length mismatch for {name}")
            if descriptor.size:
                maximum_index = descriptor.offset + sum(
                    (size - 1) * stride
                    for size, stride in zip(descriptor.size, descriptor.stride)
                    if size
                )
                if maximum_index >= descriptor.storage.count:
                    raise ValueError(f"tensor view escapes storage for {name}")
            arrays[name] = np.ndarray(
                descriptor.size,
                dtype=dtype,
                buffer=raw,
                offset=descriptor.offset * dtype.itemsize,
                strides=tuple(value * dtype.itemsize for value in descriptor.stride),
            ).copy()
    return payload, arrays


def canonical_d4_maps() -> np.ndarray:
    rotation = np.array(
        [4 * (index // 4) + ((index % 4 + 1) % 4) for index in range(N_STATES)],
        dtype=np.int64,
    )
    reflection = np.array(
        [4 * (1 - index // 4) + ((-(index % 4)) % 4) for index in range(N_STATES)],
        dtype=np.int64,
    )
    return np.stack((rotation, reflection), axis=0)


def tensor_receipt(array: np.ndarray) -> dict[str, object]:
    local = np.ascontiguousarray(array)
    return {
        "shape": list(local.shape),
        "dtype": str(local.dtype),
        "sha256": sha256_bytes(local.tobytes(order="C")),
    }


def words_upto(maximum_length: int = SUFFIX_MAX_LENGTH) -> tuple[tuple[int, ...], ...]:
    return tuple(
        word
        for length in range(maximum_length + 1)
        for word in itertools.product(range(2), repeat=length)
    )


def canonical_word_slots(canonical_to_slot: np.ndarray, word: Sequence[int]) -> np.ndarray:
    if not word:
        return np.empty((canonical_to_slot.shape[0], 0), dtype=np.int64)
    canonical = np.broadcast_to(np.asarray(word, dtype=np.int64), (canonical_to_slot.shape[0], len(word)))
    return np.take_along_axis(canonical_to_slot, canonical, axis=1)


def apply_visible_word(
    maps: np.ndarray,
    canonical_to_slot: np.ndarray,
    starts: np.ndarray,
    word: Sequence[int],
) -> np.ndarray:
    current = np.asarray(starts, dtype=np.int64).copy()
    contexts = maps.shape[0]
    if current.ndim != 2 or current.shape[0] != contexts:
        raise ValueError("start array must have shape (context, cases)")
    rows = np.arange(contexts)
    for canonical_operator in word:
        slots = canonical_to_slot[:, int(canonical_operator)]
        selected_maps = maps[rows, slots]
        current = np.take_along_axis(selected_maps, current, axis=1)
    return current


def validate_identity_prefixes(
    bank: Mapping[str, np.ndarray],
    words: Mapping[str, Sequence[int]],
    *,
    expected_count: int,
) -> dict[str, object]:
    contexts = int(bank["maps"].shape[0])
    if len(words) != expected_count:
        raise RuntimeError("fresh prefix count drifted")
    starts = np.broadcast_to(
        np.arange(N_STATES, dtype=np.int64), (contexts, N_STATES)
    )
    output: dict[str, object] = {}
    for name, word in words.items():
        if len(word) != PREFIX_LENGTH:
            raise RuntimeError(f"fresh prefix has wrong length: {name}")
        endpoint = apply_visible_word(bank["maps"], bank["canonical_to_slot"], starts, word)
        identity = bool(np.array_equal(endpoint, starts))
        output[name] = {"length": len(word), "identity_on_all_context_states": identity}
        if not identity:
            raise RuntimeError(f"fresh prefix is not semantically null: {name}")
    return output


def load_fresh_bank_arrays(
    bank_source: Path | bytes,
) -> tuple[
    dict[str, np.ndarray],
    dict[str, np.ndarray],
    OrderedDict[str, tuple[int, ...]],
    OrderedDict[str, tuple[int, ...]],
    dict[str, Any],
]:
    """Materialize the already-verified canonical fresh-bank document."""

    if isinstance(bank_source, bytes):
        document = json.loads(bank_source.decode("utf-8"))
    else:
        document = json.loads(bank_source.read_text(encoding="utf-8"))
    if document.get("schema") != "komorebi.neuralese.semantic_retraction.fresh_bank.v1":
        raise ValueError("fresh-bank schema mismatch")
    if document.get("version") != VERSION:
        raise ValueError("fresh-bank version mismatch")
    if document.get("status") != "SEALED_FRESH_BANK_UNSPENT":
        raise ValueError("fresh bank is not in the frozen unspent state")
    splits = document.get("payload", {}).get("splits", {})

    def materialize_contexts(split_name: str) -> dict[str, np.ndarray]:
        records = splits[split_name]["context_bank"]["contexts"]
        if len(records) != (
            CALIBRATION_CONTEXTS if split_name == "calibration" else EVALUATION_CONTEXTS
        ):
            raise ValueError(f"fresh {split_name} context count mismatch")
        bank = {
            "tables": np.ascontiguousarray(
                [record["tables"] for record in records], dtype=np.float32
            ),
            "maps": np.ascontiguousarray(
                [record["maps"] for record in records], dtype=np.int64
            ),
            "phi": np.ascontiguousarray(
                [record["phi"] for record in records], dtype=np.int64
            ),
            "canonical_to_slot": np.ascontiguousarray(
                [record["canonical_to_slot"] for record in records], dtype=np.int64
            ),
        }
        expected_shapes = {
            "tables": (len(records), 2, N_STATES, N_STATES),
            "maps": (len(records), 2, N_STATES),
            "phi": (len(records), N_STATES),
            "canonical_to_slot": (len(records), 2),
        }
        for name, expected in expected_shapes.items():
            if bank[name].shape != expected:
                raise ValueError(f"fresh {split_name} bank tensor shape mismatch: {name}")
        return bank

    def materialize_words(split_name: str) -> OrderedDict[str, tuple[int, ...]]:
        records = splits[split_name]["identity_path_bank"]["paths"]
        if len(records) != (
            CALIBRATION_PREFIXES if split_name == "calibration" else EVALUATION_PREFIXES
        ):
            raise ValueError(f"fresh {split_name} path count mismatch")
        return OrderedDict(
            (
                f"{split_name}_{int(record['index']):02d}",
                tuple(int(value) for value in record["word"]),
            )
            for record in records
        )

    calibration_bank = materialize_contexts("calibration")
    evaluation_bank = materialize_contexts("evaluation")
    calibration_words = materialize_words("calibration")
    evaluation_words = materialize_words("evaluation")
    validate_identity_prefixes(
        calibration_bank,
        calibration_words,
        expected_count=CALIBRATION_PREFIXES,
    )
    validate_identity_prefixes(
        evaluation_bank,
        evaluation_words,
        expected_count=EVALUATION_PREFIXES,
    )
    return (
        calibration_bank,
        evaluation_bank,
        calibration_words,
        evaluation_words,
        document,
    )


def load_protocol(path: Path = PROTOCOL_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("protocol must be a JSON object")
    return value


def expected_work_counts() -> dict[str, int]:
    suffixes = len(words_upto())
    calibration_split_states = CALIBRATION_CONTEXTS * N_STATES * CALIBRATION_PREFIXES
    evaluation_split_states = EVALUATION_CONTEXTS * N_STATES * EVALUATION_PREFIXES
    suffix_endpoints = (
        evaluation_split_states * suffixes * len(INTERVENTIONS)
        + EVALUATION_CONTEXTS * N_STATES * suffixes
    )
    prefix_matvecs = (
        calibration_split_states + evaluation_split_states
    ) * PREFIX_LENGTH
    suffix_tree_edges = suffixes - 1
    suffix_matvecs = (
        evaluation_split_states * len(INTERVENTIONS) * suffix_tree_edges
    )
    clean_matvecs = EVALUATION_CONTEXTS * N_STATES * suffix_tree_edges
    section_audit_matvecs = 4 * EVALUATION_CONTEXTS * N_STATES
    total_matvecs = prefix_matvecs + suffix_matvecs + clean_matvecs + section_audit_matvecs
    return {
        "calibration_split_states_per_checkpoint": calibration_split_states,
        "evaluation_split_states_per_checkpoint": evaluation_split_states,
        "suffix_endpoint_evaluations_per_checkpoint": suffix_endpoints,
        "float32_recurrent_matvecs_per_checkpoint": total_matvecs,
        "checkpoint_count": len(ARMS) * len(SEEDS),
        "total_suffix_endpoint_evaluations": suffix_endpoints * len(ARMS) * len(SEEDS),
        "total_float32_recurrent_matvecs": total_matvecs * len(ARMS) * len(SEEDS),
    }


def protocol_unlock_state(
    protocol: Mapping[str, Any],
    *,
    protocol_bytes: bytes | None,
    freeze_receipt_path: Path = FREEZE_RECEIPT_PATH,
) -> dict[str, object]:
    """Report the actual fail-closed state; status alone never unlocks a run."""

    status_frozen = protocol.get("status") == FROZEN_STATUS
    receipt_present = freeze_receipt_path.is_file()
    observed_sha256 = sha256_bytes(protocol_bytes) if protocol_bytes is not None else None
    receipted_sha256: str | None = None
    receipt_matches = False
    if receipt_present:
        tokens = freeze_receipt_path.read_text(encoding="utf-8").strip().split()
        if tokens:
            receipted_sha256 = tokens[0]
            receipt_matches = observed_sha256 is not None and receipted_sha256 == observed_sha256
    return {
        "status_frozen": status_frozen,
        "receipt_check_performed": protocol_bytes is not None,
        "receipt_present": receipt_present,
        "receipt_matches": receipt_matches,
        "observed_protocol_sha256": observed_sha256,
        "receipted_protocol_sha256": receipted_sha256,
        "learned_execution_unlocked": status_frozen and receipt_matches,
    }


def validate_protocol_design(
    protocol: Mapping[str, Any],
    *,
    protocol_bytes: bytes | None = None,
    freeze_receipt_path: Path = FREEZE_RECEIPT_PATH,
) -> dict[str, object]:
    if protocol.get("schema") != PROTOCOL_SCHEMA or protocol.get("version") != VERSION:
        raise ValueError("protocol schema or version mismatch")
    if protocol.get("runtime_contract", {}).get("numpy_version") != EXPECTED_NUMPY_VERSION:
        raise ValueError("protocol NumPy version mismatch")
    if tuple(protocol["source_panel"]["arms"]) != ARMS:
        raise ValueError("protocol arm order mismatch")
    if tuple(int(value) for value in protocol["source_panel"]["seeds"]) != SEEDS:
        raise ValueError("protocol seed set mismatch")
    if protocol["source_panel"]["archive_sha256"] != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("protocol archive digest mismatch")
    if protocol["source_panel"]["checkpoint_seal_sha256"] != EXPECTED_SEAL_SHA256:
        raise ValueError("protocol checkpoint-seal digest mismatch")
    if protocol["lineage"]["parent_release_sha256"] != PARENT_RELEASE_SHA256:
        raise ValueError("protocol parent-release digest mismatch")
    if protocol["lineage"]["v0.2_spend_receipt_sha256"] != V02_SPEND_RECEIPT_SHA256:
        raise ValueError("protocol v0.2 spend digest mismatch")
    bank_design = protocol["fresh_bank_design"]
    required_bank_design = {
        "calibration_contexts": CALIBRATION_CONTEXTS,
        "evaluation_contexts": EVALUATION_CONTEXTS,
        "calibration_prefixes": CALIBRATION_PREFIXES,
        "evaluation_prefixes": EVALUATION_PREFIXES,
        "prefix_length": PREFIX_LENGTH,
    }
    for field, expected in required_bank_design.items():
        if int(bank_design[field]) != expected:
            raise ValueError(f"protocol fresh-bank design mismatch: {field}")
    if bank_design.get("entropy_available_before_design_commit") is not False:
        raise ValueError("production entropy must be unavailable before design commit")
    if bank_design.get("calibration_evaluation_disjoint") is not True:
        raise ValueError("protocol must require disjoint calibration/evaluation banks")
    if bank_design.get("prior_bank_exclusion_required") is not True:
        raise ValueError("protocol must require prior-bank exclusion")
    if tuple(protocol["interventions"]) != INTERVENTIONS:
        raise ValueError("protocol intervention order mismatch")
    if int(protocol["continuations"]["maximum_length"]) != SUFFIX_MAX_LENGTH:
        raise ValueError("protocol suffix horizon mismatch")
    if int(protocol["continuations"]["word_count"]) != len(words_upto()):
        raise ValueError("protocol suffix word count mismatch")
    factorial = protocol.get("factorial", {})
    required_core = {
        "oracle_anchor": ["oracle", "anchor"],
        "oracle_prototype": ["oracle", "prototype"],
        "decoder_anchor": ["decoder", "anchor"],
        "decoder_prototype": ["decoder", "prototype"],
    }
    if factorial.get("core_cells") != required_core:
        raise ValueError("protocol core selector-by-section mapping mismatch")
    if factorial.get("decoder_label_computed_once_and_reused") is not True:
        raise ValueError("protocol must reuse the exact decoder label tensor")
    if protocol.get("primary_gate_contract") != PRIMARY_GATE_CONTRACT:
        raise ValueError("protocol primary gate contract mismatch")
    if protocol.get("claim_boundary") != CLAIM_BOUNDARY_CONTRACT:
        raise ValueError("protocol claim-boundary contract mismatch")
    if protocol.get("output_lifecycle") != OUTPUT_LIFECYCLE_CONTRACT:
        raise ValueError("protocol output-lifecycle contract mismatch")
    boundaries = protocol.get("scientific_boundaries", {})
    boundaries_path = require_regular_file(
        SCIENTIFIC_BOUNDARIES_PATH,
        label="scientific-boundaries memo",
    )
    if boundaries.get("sha256") != sha256_file(boundaries_path):
        raise ValueError("protocol scientific-boundaries digest mismatch")
    work = expected_work_counts()
    for name, expected in work.items():
        if int(protocol["bounded_work"][name]) != expected:
            raise ValueError(f"protocol work count mismatch: {name}")
    if protocol["status"] not in {
        "DRAFT_DO_NOT_EVALUATE_LEARNED_CHECKPOINTS",
        FROZEN_STATUS,
    }:
        raise ValueError("unrecognized protocol status")
    firewall = protocol.get("execution_firewall", {})
    if firewall.get("requires_frozen_status_and_receipt") is not True:
        raise ValueError("protocol firewall must require frozen status and exact receipt")
    if (
        firewall.get("runtime_check_before_spend") is not True
        or firewall.get("all_checkpoint_parameters_verified_before_spend") is not True
        or firewall.get("output_capacity_reserved_before_spend") is not True
        or firewall.get("spend_precedes_fresh_bank_checkpoint_evaluation") is not True
    ):
        raise ValueError("protocol pre-spend firewall contract mismatch")
    implementation = protocol.get("implementation_receipts", {})
    implementation_paths = {
        "factorial_runner_sha256": Path(__file__).resolve(),
        "factorial_test_sha256": (HERE / "test_factorial_probe.py").resolve(),
        "fresh_bank_implementation_sha256": (HERE / "fresh_bank.py").resolve(),
        "fresh_bank_test_sha256": (HERE / "test_fresh_bank.py").resolve(),
        "lifecycle_test_sha256": (HERE / "test_lifecycle.py").resolve(),
        "projector_test_sha256": (
            HERE.parent / "preflight" / "test_projector_semantics.py"
        ).resolve(),
        "spent_registry_builder_sha256": (
            HERE.parent / "lineage" / "build_spent_registry.py"
        ).resolve(),
    }
    observed_implementation: dict[str, str] = {}
    for field, path in implementation_paths.items():
        expected = implementation.get(field)
        observed = sha256_file(path)
        if expected != observed:
            raise ValueError(f"protocol implementation digest mismatch: {field}")
        observed_implementation[field] = observed
    preflight = protocol.get("preflight", {})
    if preflight.get("evaluation_bank_generated_or_opened") is not False:
        raise ValueError("protocol preflight must be bank-free")
    if not PREFLIGHT_PATH.is_file():
        raise FileNotFoundError("parameter-only preflight receipt is absent")
    observed_preflight_sha256 = sha256_file(PREFLIGHT_PATH)
    if preflight.get("sha256") != observed_preflight_sha256:
        raise ValueError("protocol preflight digest mismatch")
    synthetic_tests = protocol.get("synthetic_tests", {})
    if not SYNTHETIC_TESTS_PATH.is_file():
        raise FileNotFoundError("synthetic-test receipt is absent")
    observed_synthetic_tests_sha256 = sha256_file(SYNTHETIC_TESTS_PATH)
    if synthetic_tests.get("sha256") != observed_synthetic_tests_sha256:
        raise ValueError("protocol synthetic-test digest mismatch")
    synthetic_document = json.loads(SYNTHETIC_TESTS_PATH.read_text(encoding="utf-8"))
    if (
        synthetic_document.get("schema")
        != "komorebi.neuralese.semantic_retraction.synthetic_tests.v1"
        or synthetic_document.get("version") != VERSION
        or synthetic_document.get("status") != "PASS"
        or synthetic_document.get("production_bank_generated_or_opened") is not False
        or synthetic_document.get("learned_checkpoint_opened") is not False
    ):
        raise ValueError("synthetic-test receipt is not a passing isolated receipt")
    unlock = protocol_unlock_state(
        protocol,
        protocol_bytes=protocol_bytes,
        freeze_receipt_path=freeze_receipt_path,
    )
    return {
        "valid": True,
        "status": protocol["status"],
        "suffix_word_count": len(words_upto()),
        "fresh_prefix_length": PREFIX_LENGTH,
        "bounded_work": work,
        "implementation_receipts": observed_implementation,
        "preflight_sha256": observed_preflight_sha256,
        "synthetic_tests_sha256": observed_synthetic_tests_sha256,
        "learned_execution_unlocked": unlock["learned_execution_unlocked"],
        "unlock_state": unlock,
    }


def assert_learned_execution_unlocked() -> tuple[dict[str, Any], str]:
    protocol_bytes = PROTOCOL_PATH.read_bytes()
    protocol = json.loads(protocol_bytes.decode("utf-8"))
    if canonical_json_bytes(protocol) != protocol_bytes:
        raise RuntimeError("learned execution is locked: protocol JSON is not canonical")
    design = validate_protocol_design(protocol, protocol_bytes=protocol_bytes)
    unlock = design["unlock_state"]
    if not unlock["status_frozen"]:
        raise RuntimeError("learned execution is locked: protocol status is not frozen")
    if not unlock["receipt_present"]:
        raise RuntimeError("learned execution is locked: FROZEN_PROTOCOL.sha256 is absent")
    if not unlock["receipt_matches"]:
        raise RuntimeError("learned execution is locked: protocol receipt mismatch")
    return protocol, str(unlock["observed_protocol_sha256"])


def validate_state_dict(arrays: Mapping[str, np.ndarray]) -> dict[str, object]:
    expected_shapes = {
        "metric_log_diagonal": (HIDDEN_DIM,),
        "metric_strict_lower": (HIDDEN_DIM * (HIDDEN_DIM - 1) // 2,),
        "state_embedding.weight": (N_STATES, HIDDEN_DIM),
        "operator_encoder.weight": (HIDDEN_DIM * HIDDEN_DIM, N_STATES * N_STATES),
        "decoder.weight": (N_STATES, HIDDEN_DIM),
    }
    if set(arrays) != set(expected_shapes):
        raise ValueError("checkpoint state-dict key set mismatch")
    for name, shape in expected_shapes.items():
        array = arrays[name]
        if array.shape != shape:
            raise ValueError(f"checkpoint tensor shape mismatch: {name}")
        if array.dtype != np.dtype("<f4"):
            raise ValueError(f"checkpoint tensor dtype is not float32: {name}")
        if not bool(np.isfinite(array).all()):
            raise ValueError(f"checkpoint tensor is nonfinite: {name}")
    metric_zero = bool(
        np.count_nonzero(arrays["metric_log_diagonal"]) == 0
        and np.count_nonzero(arrays["metric_strict_lower"]) == 0
    )
    if not metric_zero:
        raise ValueError("sealed v0.4 sensitivity requires the frozen identity metric")
    return {
        "exact_keys": True,
        "exact_shapes": True,
        "all_float32": True,
        "all_finite": True,
        "metric_is_exact_identity": True,
        "tensor_receipts": {name: tensor_receipt(value) for name, value in arrays.items()},
    }


def state_dict_digest_numpy(arrays: Mapping[str, np.ndarray]) -> str:
    """Reproduce the sealed torch state-dict digest from inert NumPy arrays."""

    digest = hashlib.sha256()
    for name in sorted(arrays):
        local = np.ascontiguousarray(arrays[name])
        dtype_name = {
            np.dtype("<f4"): "torch.float32",
            np.dtype("<f8"): "torch.float64",
            np.dtype("<i8"): "torch.int64",
            np.dtype("<i4"): "torch.int32",
            np.dtype("?"): "torch.bool",
            np.dtype("<f2"): "torch.float16",
        }.get(local.dtype)
        if dtype_name is None:
            raise TypeError(f"unsupported state-dict dtype for digest: {local.dtype}")
        digest.update(name.encode("utf-8"))
        digest.update(dtype_name.encode("ascii"))
        digest.update(json.dumps(list(local.shape), separators=(",", ":")).encode("ascii"))
        digest.update(local.tobytes(order="C"))
    return digest.hexdigest()


def normalize32(hidden: np.ndarray) -> np.ndarray:
    """Source-style positive Euclidean ray normalization in float32."""

    value = np.asarray(hidden, dtype=np.float32)
    finite_input = np.isfinite(value).all(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore", over="ignore"):
        squared = np.sum(value * value, axis=-1, dtype=np.float32)
        floor = np.float32(NORMALIZATION_EPS * NORMALIZATION_EPS)
        radius = np.sqrt(np.maximum(squared, floor)).astype(np.float32, copy=False)
        normalized = np.asarray(value / radius[..., None], dtype=np.float32)
    arithmetic_failure = finite_input & (
        ~np.isfinite(squared)
        | ~np.isfinite(radius)
        | ~np.isfinite(normalized).all(axis=-1)
    )
    if bool(arithmetic_failure.any()):
        raise FloatingPointError(
            "float32 normalization overflowed or became nonfinite from finite input"
        )
    return normalized


def normalized_anchors32(arrays: Mapping[str, np.ndarray]) -> np.ndarray:
    anchors = normalize32(arrays["state_embedding.weight"])
    if not bool(np.isfinite(anchors).all()):
        raise FloatingPointError("checkpoint contains an undefined anchor")
    return anchors


def construct_anchor_projector32(
    anchors32: np.ndarray,
) -> tuple[np.ndarray, dict[str, object]]:
    """Construct the anchor projector with explicit float32 rank semantics.

    The sealed cohort has the exact Euclidean recurrence metric.  The matrix
    applied to states is cast to float32 once.  Every audit, including rank,
    inspects the exact float64 embedding of those applied float32 bytes.
    """

    anchors_native = np.ascontiguousarray(anchors32, dtype=np.float32)
    if anchors_native.shape != (N_STATES, HIDDEN_DIM):
        raise ValueError("anchor projector received the wrong shape")
    basis = anchors_native.astype(np.float64).T
    left, anchor_singular, _ = np.linalg.svd(basis, full_matrices=False)
    anchor_tau = float(
        max(basis.shape) * np.finfo(np.float64).eps * anchor_singular[0]
    )
    anchor_rank = int(np.count_nonzero(anchor_singular > anchor_tau))
    if anchor_rank != N_STATES:
        raise RuntimeError("anchor chart is not full rank before projector construction")
    orthonormal = left[:, :N_STATES]
    projector64 = orthonormal @ orthonormal.T
    projector32 = np.ascontiguousarray(projector64, dtype=np.float32)
    applied = projector32.astype(np.float64)
    singular = np.linalg.svd(applied, compute_uv=False)
    rank_tolerance = float(
        max(applied.shape) * np.finfo(np.float32).eps * singular[0]
    )
    effective_rank = int(np.count_nonzero(singular > rank_tolerance))
    idempotence = float(np.max(np.abs(applied @ applied - applied)))
    self_adjointness = float(np.max(np.abs(applied.T - applied)))
    preservation = float(np.max(np.abs(applied @ basis - basis)))
    trace_error = abs(float(np.trace(applied)) - N_STATES)
    criteria = {
        "effective_rank_equals_eight": effective_rank == N_STATES,
        "sigma8_at_least_100_tau": bool(
            singular[N_STATES - 1] >= PROJECTOR_RANK_GAP_FACTOR * rank_tolerance
        ),
        "sigma9_at_most_tau": bool(singular[N_STATES] <= rank_tolerance),
        "trace_error_at_most_1e_minus_5": trace_error
        <= PROJECTOR_RESIDUAL_TOLERANCE,
        "idempotence_at_most_1e_minus_5": idempotence
        <= PROJECTOR_RESIDUAL_TOLERANCE,
        "self_adjointness_at_most_1e_minus_5": self_adjointness
        <= PROJECTOR_RESIDUAL_TOLERANCE,
        "anchor_preservation_at_most_1e_minus_5": preservation
        <= PROJECTOR_RESIDUAL_TOLERANCE,
    }
    return projector32, {
        "construction": "QQ^T from thin SVD of float64 anchor embedding; cast once to float32",
        "rank_definition": "count singular values of widened applied float32 matrix above 12*eps32*sigma1",
        "rank_tolerance": rank_tolerance,
        "effective_rank": effective_rank,
        "anchor_rank": anchor_rank,
        "anchor_rank_tolerance": anchor_tau,
        "singular_values": singular.tolist(),
        "sigma8": float(singular[N_STATES - 1]),
        "sigma9": float(singular[N_STATES]),
        "trace": float(np.trace(applied)),
        "trace_error": trace_error,
        "maximum_absolute_idempotence_residual": idempotence,
        "maximum_absolute_self_adjointness_residual": self_adjointness,
        "maximum_absolute_anchor_preservation_residual": preservation,
        "residual_tolerance": PROJECTOR_RESIDUAL_TOLERANCE,
        "rank_gap_factor": PROJECTOR_RANK_GAP_FACTOR,
        "criteria": criteria,
        "pass": all(criteria.values()),
        "tensor": tensor_receipt(projector32),
    }


def projector_failure_receipt(error: Exception) -> dict[str, object]:
    return {
        "construction": "unavailable",
        "rank_definition": "count singular values of widened applied float32 matrix above 12*eps32*sigma1",
        "criteria": {},
        "pass": False,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "isolated_behavioral_effect": "anchor_projection condition unavailable; core factorial remains evaluable",
        "tensor": None,
    }


def encode_operators32(
    arrays: Mapping[str, np.ndarray],
    tables: np.ndarray,
    *,
    polar: bool,
) -> tuple[np.ndarray, dict[str, object]]:
    """Bias-free float32 encoder plus independent NumPy polar factor."""

    features = np.ascontiguousarray(tables.reshape(-1, N_STATES * N_STATES), dtype=np.float32)
    weight = np.ascontiguousarray(arrays["operator_encoder.weight"], dtype=np.float32)
    raw = np.matmul(features, weight.T).reshape(
        tables.shape[0], tables.shape[1], HIDDEN_DIM, HIDDEN_DIM
    )
    raw = np.ascontiguousarray(raw, dtype=np.float32)
    singular_values = np.empty(raw.shape[:2] + (HIDDEN_DIM,), dtype=np.float32)
    if not polar:
        operators = raw.copy()
        singular_values[...] = np.asarray(
            np.linalg.svd(raw, compute_uv=False), dtype=np.float32
        )
    else:
        operators = np.empty_like(raw)
        for index in np.ndindex(raw.shape[:2]):
            left, singular, right_transpose = np.linalg.svd(raw[index], full_matrices=False)
            singular_values[index] = np.asarray(singular, dtype=np.float32)
            operators[index] = np.asarray(left @ right_transpose, dtype=np.float32)
    if operators.dtype != np.float32 or not bool(np.isfinite(operators).all()):
        raise FloatingPointError("operator construction left the finite float32 path")
    identity = np.eye(HIDDEN_DIM, dtype=np.float64)
    defects = np.linalg.norm(
        operators.astype(np.float64).transpose(0, 1, 3, 2)
        @ operators.astype(np.float64)
        - identity,
        axis=(-2, -1),
    )
    largest = singular_values[..., 0].astype(np.float64)
    smallest = singular_values[..., -1].astype(np.float64)
    relative_smallest = np.divide(
        smallest,
        largest,
        out=np.full_like(smallest, np.nan),
        where=largest > 0.0,
    )
    return operators, {
        "polar_retraction": polar,
        "raw_tensor": tensor_receipt(raw),
        "recurrent_tensor": tensor_receipt(operators),
        "maximum_orthogonality_defect_frobenius": (
            float(defects.max()) if polar else None
        ),
        "raw_operator_singular_values": {
            "tensor": tensor_receipt(singular_values),
            "largest": numeric_summary(largest),
            "smallest": numeric_summary(smallest),
            "smallest_over_largest": numeric_summary(relative_smallest),
            "absolute_smallest_at_most_1e-6": int((smallest <= 1e-6).sum()),
            "relative_smallest_at_most_1e-6": int((relative_smallest <= 1e-6).sum()),
        },
        "arithmetic": "numpy_float32",
        "backend_equivalence_claim": False,
    }


def step_context_states32(
    hidden: np.ndarray,
    operators: np.ndarray,
    slots: np.ndarray,
) -> np.ndarray:
    """Advance an array shaped (context, ..., hidden) by one selected code."""

    value = np.asarray(hidden, dtype=np.float32)
    if value.shape[0] != operators.shape[0] or value.shape[-1] != HIDDEN_DIM:
        raise ValueError("hidden state axes do not match context operators")
    selected = operators[np.arange(operators.shape[0]), np.asarray(slots, dtype=np.int64)]
    flattened = value.reshape(value.shape[0], -1, HIDDEN_DIM)
    proposal = np.matmul(selected[:, None, :, :], flattened[..., None]).squeeze(-1)
    proposal = proposal.reshape(value.shape)
    return normalize32(proposal)


def decode32(hidden: np.ndarray, decoder: np.ndarray) -> np.ndarray:
    value = np.asarray(hidden, dtype=np.float32)
    result = np.matmul(value, np.asarray(decoder, dtype=np.float32).T)
    return np.asarray(result, dtype=np.float32)


def finite_argmax(values: np.ndarray, *, label: str) -> tuple[np.ndarray, np.ndarray]:
    """Apply the frozen tie break only to rows with wholly finite scores."""

    scores = np.asarray(values)
    finite = np.isfinite(scores).all(axis=-1)
    if not bool(finite.all()):
        raise FloatingPointError(
            f"{label} has {int((~finite).sum())} nonfinite score rows; selector undefined"
        )
    return np.argmax(scores, axis=-1), finite


def nearest_anchor_labels64(
    hidden: np.ndarray,
    anchors: np.ndarray,
    *,
    label: str,
) -> tuple[np.ndarray, np.ndarray]:
    """Select by oriented cosine; finite sub-threshold rays are undefined."""

    value = np.asarray(hidden, dtype=np.float64)
    section = np.asarray(anchors, dtype=np.float64)
    if not bool(np.isfinite(value).all()) or not bool(np.isfinite(section).all()):
        raise FloatingPointError(f"{label} contains nonfinite input")
    value_norm = np.linalg.norm(value, axis=-1)
    section_norm = np.linalg.norm(section, axis=-1)
    if not bool(np.isfinite(value_norm).all()) or not bool(
        np.isfinite(section_norm).all()
    ):
        raise FloatingPointError(f"{label} contains nonfinite ray norm")
    section_defined = bool(
        np.all(section_norm > RAY_NORM_STRICT_MINIMUM)
    )
    defined = (value_norm > RAY_NORM_STRICT_MINIMUM) & section_defined
    selected = np.zeros(value.shape[:-1], dtype=np.int64)
    if bool(defined.any()):
        defined_scores = np.matmul(value[defined], section.T)
        defined_scores /= (
            value_norm[defined, None] * section_norm[None, :]
        )
        if not bool(np.isfinite(defined_scores).all()):
            raise FloatingPointError(f"{label} contains nonfinite cosine scores")
        selected[defined] = np.argmax(defined_scores, axis=-1)
    return selected, np.asarray(defined, dtype=bool)


def rollout_word32(
    initial: np.ndarray,
    operators: np.ndarray,
    canonical_to_slot: np.ndarray,
    word: Sequence[int],
) -> np.ndarray:
    hidden = normalize32(initial)
    for operator in word:
        hidden = step_context_states32(
            hidden,
            operators,
            canonical_to_slot[:, int(operator)],
        )
    return hidden


def rollout_suffix_tree32(
    initial: np.ndarray,
    operators: np.ndarray,
    canonical_to_slot: np.ndarray,
    decoder: np.ndarray,
    suffixes: Sequence[tuple[int, ...]],
) -> tuple[np.ndarray, np.ndarray]:
    """Evaluate all suffixes while sharing their exact recurrent prefixes."""

    index = {word: position for position, word in enumerate(suffixes)}
    if suffixes[0] != () or len(index) != len(suffixes):
        raise ValueError("suffix set must start with the unique empty word")
    contexts, states = initial.shape[:2]
    hidden = np.empty((len(suffixes), contexts, states, HIDDEN_DIM), dtype=np.float32)
    logits = np.empty((len(suffixes), contexts, states, N_STATES), dtype=np.float32)
    hidden[0] = normalize32(initial)
    logits[0] = decode32(hidden[0], decoder)
    for position, word in enumerate(suffixes[1:], start=1):
        parent = word[:-1]
        if parent not in index or index[parent] >= position:
            raise ValueError("suffixes are not in prefix-tree order")
        hidden[position] = step_context_states32(
            hidden[index[parent]],
            operators,
            canonical_to_slot[:, word[-1]],
        )
        logits[position] = decode32(hidden[position], decoder)
    return hidden, logits


def rollout_intervention32(
    name: str,
    initial: np.ndarray,
    operators: np.ndarray,
    canonical_to_slot: np.ndarray,
    decoder: np.ndarray,
    suffixes: Sequence[tuple[int, ...]],
    *,
    prototype_usable: bool,
    projector_available: bool,
) -> tuple[np.ndarray, np.ndarray, bool]:
    """Skip recurrent math for globally undefined diagnostic conditions."""

    intentionally_undefined = (
        name in PROTOTYPE_STATE_CONDITIONS and not prototype_usable
    ) or (name == "anchor_projection" and not projector_available)
    if intentionally_undefined:
        contexts, states = initial.shape[:2]
        hidden = np.full(
            (len(suffixes), contexts, states, HIDDEN_DIM),
            np.nan,
            dtype=np.float32,
        )
        logits = np.full(
            (len(suffixes), contexts, states, N_STATES),
            np.nan,
            dtype=np.float32,
        )
        return hidden, logits, True
    hidden, logits = rollout_suffix_tree32(
        initial,
        operators,
        canonical_to_slot,
        decoder,
        suffixes,
    )
    return hidden, logits, False


def split_states_for_words32(
    anchors: np.ndarray,
    operators: np.ndarray,
    canonical_to_slot: np.ndarray,
    words: Mapping[str, Sequence[int]],
) -> dict[str, np.ndarray]:
    initial = np.broadcast_to(
        anchors[None, :, :],
        (operators.shape[0], N_STATES, HIDDEN_DIM),
    ).copy()
    return {
        name: rollout_word32(initial, operators, canonical_to_slot, word)
        for name, word in words.items()
    }


def fit_calibration_prototypes(
    split_states: Mapping[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, object]]:
    """Fit one balanced section using only the disjoint calibration split."""

    names = tuple(split_states)
    if len(names) != CALIBRATION_PREFIXES:
        raise RuntimeError("calibration prefix count drifted")
    samples = np.concatenate([split_states[name] for name in names], axis=0)
    expected = (CALIBRATION_CONTEXTS * CALIBRATION_PREFIXES, N_STATES, HIDDEN_DIM)
    if samples.shape != expected:
        raise RuntimeError("calibration prototype contribution count drifted")
    resultant = samples.astype(np.float64).sum(axis=0)
    lengths = np.linalg.norm(resultant, axis=-1)
    defined = (
        np.isfinite(resultant).all(axis=-1)
        & np.isfinite(lengths)
        & (lengths > RAY_NORM_STRICT_MINIMUM)
    )
    prototypes = np.full((N_STATES, HIDDEN_DIM), np.nan, dtype=np.float32)
    prototypes[defined] = np.asarray(
        resultant[defined] / lengths[defined, None],
        dtype=np.float32,
    )
    return prototypes, {
        "role": "held_out_calibration_section",
        "usable": bool(defined.all()),
        "defined_states": exact_fraction(defined),
        "calibration_prefixes": list(names),
        "calibration_contexts": CALIBRATION_CONTEXTS,
        "contributions_per_state": int(samples.shape[0]),
        "balanced_over_context_prefix_and_visible_state": True,
        "accumulation": "fixed prefix order then context order, float64 sum, one float32 cast",
        "resultant_length": numeric_summary(lengths),
        "tensor": tensor_receipt(prototypes),
    }


def wrong_visible_labels(phi: np.ndarray) -> np.ndarray:
    inverse_phi = np.argsort(phi, axis=1)
    visible = np.broadcast_to(np.arange(N_STATES, dtype=np.int64), (phi.shape[0], N_STATES))
    canonical = np.take_along_axis(inverse_phi, visible, axis=1)
    wrong_canonical = canonical_d4_maps()[0, canonical]
    wrong = np.take_along_axis(phi, wrong_canonical, axis=1)
    if bool(np.any(wrong == visible)):
        raise RuntimeError("wrong-anchor control collided with the factual label")
    return wrong


def construct_interventions32(
    native: np.ndarray,
    anchors: np.ndarray,
    decoder: np.ndarray,
    prototypes: np.ndarray,
    projector: np.ndarray | None,
    phi: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, object], dict[str, np.ndarray]]:
    """Build the frozen selector by section matrix from one native cut tensor."""

    true = np.broadcast_to(
        np.arange(N_STATES, dtype=np.int64), native.shape[:2]
    )
    decoded, decoded_finite = finite_argmax(
        decode32(native, decoder),
        label="native decoder selector",
    )
    native_cut_ray_defined = hidden_rays_defined64(native)
    anchor_nearest, anchor_nearest_defined = nearest_anchor_labels64(
        native,
        anchors,
        label="native nearest-anchor selector",
    )
    prototype_usable = bool(
        np.isfinite(prototypes).all()
        and np.all(
            np.linalg.norm(prototypes.astype(np.float64), axis=-1)
            > RAY_NORM_STRICT_MINIMUM
        )
    )
    if prototype_usable:
        prototype_nearest, prototype_nearest_defined = nearest_anchor_labels64(
            native,
            prototypes,
            label="native nearest-prototype selector",
        )
    else:
        prototype_nearest = np.zeros(native.shape[:2], dtype=np.int64)
        prototype_nearest_defined = np.zeros(native.shape[:2], dtype=bool)
    wrong = wrong_visible_labels(phi)
    projected = (
        normalize32(np.matmul(native, np.asarray(projector, dtype=np.float32).T))
        if projector is not None
        else np.full_like(native, np.nan, dtype=np.float32)
    )
    states = {
        "native": native.copy(),
        "oracle_anchor": anchors[true],
        "oracle_prototype": prototypes[true],
        "decoder_anchor": anchors[decoded],
        "decoder_prototype": prototypes[decoded],
        "anchor_nearest_anchor": anchors[anchor_nearest],
        "anchor_nearest_prototype": prototypes[anchor_nearest],
        "prototype_nearest_anchor": anchors[prototype_nearest],
        "prototype_nearest_prototype": prototypes[prototype_nearest],
        "anchor_projection": projected,
        "wrong_anchor_control": anchors[wrong],
        "wrong_prototype_control": prototypes[wrong],
    }
    for name in ("anchor_nearest_anchor", "anchor_nearest_prototype"):
        states[name] = np.where(
            anchor_nearest_defined[..., None],
            states[name],
            np.float32(0.0),
        )
    for name in ("prototype_nearest_anchor", "prototype_nearest_prototype"):
        states[name] = np.where(
            prototype_nearest_defined[..., None],
            states[name],
            np.float32(0.0),
        )
    if tuple(states) != INTERVENTIONS:
        raise RuntimeError("intervention order drifted")
    correct_selection = native_cut_ray_defined & (decoded == true)
    if not np.array_equal(
        states["decoder_anchor"][correct_selection],
        states["oracle_anchor"][correct_selection],
    ):
        raise RuntimeError("decoder/oracle anchor branches disagree under correct selection")
    if prototype_usable and not np.array_equal(
        states["decoder_prototype"][correct_selection],
        states["oracle_prototype"][correct_selection],
    ):
        raise RuntimeError(
            "decoder/oracle prototype branches disagree under correct selection"
        )
    anchor_reselected, anchor_reselected_finite = finite_argmax(
        decode32(states["decoder_anchor"], decoder),
        label="decoder-anchor idempotence selector",
    )
    if prototype_usable:
        prototype_reselected, prototype_reselected_finite = finite_argmax(
            decode32(states["decoder_prototype"], decoder),
            label="decoder-prototype idempotence selector",
        )
    else:
        prototype_reselected = np.zeros(native.shape[:2], dtype=np.int64)
        prototype_reselected_finite = np.zeros(native.shape[:2], dtype=bool)
    anchor_twice = anchors[anchor_reselected]
    prototype_twice = prototypes[prototype_reselected]
    anchor_idempotence_residual = float(
        np.max(np.abs(anchor_twice.astype(np.float64) - states["decoder_anchor"]))
    )
    prototype_idempotence_residual = (
        float(
            np.max(
                np.abs(
                    prototype_twice.astype(np.float64)
                    - states["decoder_prototype"].astype(np.float64)
                )
            )
        )
        if prototype_usable
        else None
    )
    audit = {
        "decoder_scores_finite": exact_fraction(decoded_finite),
        "native_cut_hidden_rays_defined": exact_fraction(
            native_cut_ray_defined
        ),
        "native_cut_hidden_rays_defined_evidence": packed_bool_evidence(
            native_cut_ray_defined
        ),
        "anchor_nearest_scores_defined": exact_fraction(anchor_nearest_defined),
        "prototype_nearest_scores_defined": exact_fraction(
            prototype_nearest_defined
        ),
        "prototype_section_usable": prototype_usable,
        "decoder": exact_fraction(correct_selection),
        "decoder_worst_context": worst_context_fraction(
            correct_selection,
            context_axis=0,
        ),
        "decoder_correct_evidence": packed_bool_evidence(correct_selection),
        "anchor_nearest": exact_fraction(
            anchor_nearest_defined & (anchor_nearest == true)
        ),
        "anchor_nearest_worst_context": worst_context_fraction(
            anchor_nearest_defined & (anchor_nearest == true),
            context_axis=0,
        ),
        "prototype_nearest": exact_fraction(
            prototype_nearest_defined & (prototype_nearest == true)
        ),
        "prototype_nearest_worst_context": worst_context_fraction(
            prototype_nearest_defined & (prototype_nearest == true),
            context_axis=0,
        ),
        "wrong_anchor_is_distinct": bool(np.all(wrong != true)),
        "shared_decoder_selected_labels_tensor": tensor_receipt(
            decoded.astype(np.int64)
        ),
        "decoder_label_tensor_reused_for_both_sections": True,
        "anchor_nearest_selected_labels_tensor": tensor_receipt(
            anchor_nearest.astype(np.int64)
        ),
        "prototype_nearest_selected_labels_tensor": tensor_receipt(
            prototype_nearest.astype(np.int64)
        ),
        "wrong_labels_tensor": tensor_receipt(wrong.astype(np.int64)),
        "oracle_decoder_reset_exact_match_on_correct_selection": True,
        "anchor_projection_available": projector is not None,
        "decoder_anchor_reset_idempotence": {
            "second_selector_finite": exact_fraction(anchor_reselected_finite),
            "selected_label_unchanged": exact_fraction(
                anchor_reselected == decoded
            ),
            "maximum_hidden_discrepancy": anchor_idempotence_residual,
        },
        "decoder_prototype_reset_idempotence": {
            "second_selector_finite": exact_fraction(prototype_reselected_finite),
            "selected_label_unchanged": exact_fraction(
                prototype_reselected == decoded
            ),
            "selected_label_unchanged_evidence": packed_bool_evidence(
                prototype_reselected == decoded
            ),
            "maximum_hidden_discrepancy": prototype_idempotence_residual,
        },
    }
    labels = {
        "true": true,
        "decoder": decoded,
        "decoder_defined": native_cut_ray_defined,
        "anchor_nearest": anchor_nearest,
        "anchor_nearest_defined": anchor_nearest_defined,
        "prototype_nearest": prototype_nearest,
        "prototype_nearest_defined": prototype_nearest_defined,
        "wrong": wrong,
    }
    return states, audit, labels


def autonomous_section_audit(
    section: np.ndarray,
    decoder: np.ndarray,
    operators: np.ndarray,
    bank: Mapping[str, np.ndarray],
    *,
    section_name: str,
) -> dict[str, object]:
    """Audit a fixed visible-state section and its decoder retraction."""

    contexts = int(bank["maps"].shape[0])
    labels = np.arange(N_STATES, dtype=np.int64)
    section_defined = bool(
        section.shape == (N_STATES, HIDDEN_DIM)
        and np.isfinite(section).all()
        and np.all(
            np.linalg.norm(section.astype(np.float64), axis=-1)
            > RAY_NORM_STRICT_MINIMUM
        )
    )
    if not section_defined:
        failed_labels = np.zeros(N_STATES, dtype=bool)
        failed_context_states = np.zeros((contexts, N_STATES), dtype=bool)
        per_generator = {
            str(operator): {
                "self_decoder_scores_finite": exact_fraction(failed_context_states),
                "stepped_hidden_rays_defined": exact_fraction(
                    failed_context_states
                ),
                "nearest_section_scores_defined": exact_fraction(
                    failed_context_states
                ),
                "self_decoded_section": exact_fraction(failed_context_states),
                "nearest_section": exact_fraction(failed_context_states),
                "self_decoded_section_worst_context": worst_context_fraction(
                    failed_context_states,
                    context_axis=0,
                ),
                "nearest_section_worst_context": worst_context_fraction(
                    failed_context_states,
                    context_axis=0,
                ),
                "self_decoded_section_evidence": packed_bool_evidence(
                    failed_context_states
                ),
                "stepped_hidden_rays_defined_evidence": packed_bool_evidence(
                    failed_context_states
                ),
            }
            for operator in range(2)
        }
        return {
            "section_name": section_name,
            "section_defined": False,
            "tie_break": "lowest_visible_state_index",
            "section_consistency": {
                "self_decoder_scores_finite": exact_fraction(failed_labels),
                "nearest_section_scores_defined": exact_fraction(failed_labels),
                "self_decoded_section": exact_fraction(failed_labels),
                "nearest_section": exact_fraction(failed_labels),
            },
            "reset_idempotence": {
                "self_decoded_section": exact_fraction(failed_labels),
                "nearest_section": exact_fraction(failed_labels),
            },
            "one_step_semantic_commutation": {
                "self_decoded_section": exact_fraction(
                    np.zeros((2, contexts, N_STATES), dtype=bool)
                ),
                "nearest_section": exact_fraction(
                    np.zeros((2, contexts, N_STATES), dtype=bool)
                ),
                "per_generator": per_generator,
            },
            "section_tensor": tensor_receipt(section),
            "section_consistency_evidence": packed_bool_evidence(failed_labels),
            "self_labels": None,
            "nearest_labels": None,
        }
    self_on_section, self_section_finite = finite_argmax(
        decode32(section, decoder),
        label=f"{section_name} self-decoder section",
    )
    nearest_on_section, nearest_section_defined = nearest_anchor_labels64(
        section,
        section,
        label=f"{section_name} nearest-section audit",
    )
    self_twice = self_on_section[self_on_section]
    nearest_twice = nearest_on_section[nearest_on_section]

    initial = np.broadcast_to(
        section[None, :, :],
        (contexts, N_STATES, HIDDEN_DIM),
    ).copy()
    true_starts = np.broadcast_to(labels, (contexts, N_STATES))
    self_commutation: list[np.ndarray] = []
    nearest_commutation: list[np.ndarray] = []
    per_generator: dict[str, object] = {}
    for operator in range(2):
        stepped = step_context_states32(
            initial,
            operators,
            bank["canonical_to_slot"][:, operator],
        )
        target = apply_visible_word(
            bank["maps"],
            bank["canonical_to_slot"],
            true_starts,
            (operator,),
        )
        self_selected, self_finite = finite_argmax(
            decode32(stepped, decoder),
            label=f"generator-{operator} self-decoder commutation",
        )
        stepped_ray_defined = hidden_rays_defined64(stepped)
        nearest_selected, nearest_defined = nearest_anchor_labels64(
            stepped,
            section,
            label=f"generator-{operator} nearest-{section_name} commutation",
        )
        self_ok = stepped_ray_defined & (self_selected == target)
        nearest_ok = nearest_defined & (nearest_selected == target)
        self_commutation.append(self_ok)
        nearest_commutation.append(nearest_ok)
        per_generator[str(operator)] = {
            "self_decoder_scores_finite": exact_fraction(self_finite),
            "stepped_hidden_rays_defined": exact_fraction(
                stepped_ray_defined
            ),
            "nearest_section_scores_defined": exact_fraction(nearest_defined),
            "self_decoded_section": exact_fraction(self_ok),
            "nearest_section": exact_fraction(nearest_ok),
            "self_decoded_section_worst_context": worst_context_fraction(
                self_ok,
                context_axis=0,
            ),
            "nearest_section_worst_context": worst_context_fraction(
                nearest_ok,
                context_axis=0,
            ),
            "self_decoded_section_evidence": packed_bool_evidence(self_ok),
            "stepped_hidden_rays_defined_evidence": packed_bool_evidence(
                stepped_ray_defined
            ),
        }
    return {
        "section_name": section_name,
        "section_defined": True,
        "tie_break": "lowest_visible_state_index",
        "section_consistency": {
            "self_decoder_scores_finite": exact_fraction(self_section_finite),
            "nearest_section_scores_defined": exact_fraction(nearest_section_defined),
            "self_decoded_section": exact_fraction(self_on_section == labels),
            "nearest_section": exact_fraction(nearest_on_section == labels),
        },
        "reset_idempotence": {
            "self_decoded_section": exact_fraction(self_twice == self_on_section),
            "nearest_section": exact_fraction(nearest_twice == nearest_on_section),
        },
        "one_step_semantic_commutation": {
            "self_decoded_section": exact_fraction(np.stack(self_commutation, axis=0)),
            "nearest_section": exact_fraction(np.stack(nearest_commutation, axis=0)),
            "per_generator": per_generator,
        },
        "section_tensor": tensor_receipt(section),
        "section_consistency_evidence": packed_bool_evidence(
            self_on_section == labels
        ),
        "self_labels": tensor_receipt(self_on_section.astype(np.int64)),
        "nearest_labels": tensor_receipt(nearest_on_section.astype(np.int64)),
    }


def exact_fraction(mask: np.ndarray) -> dict[str, object]:
    value = np.asarray(mask, dtype=bool)
    numerator = int(value.sum())
    denominator = int(value.size)
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator if denominator else None,
    }


def worst_context_fraction(
    mask: np.ndarray,
    *,
    context_axis: int,
) -> dict[str, object]:
    """Return the least successful context as an exact count fraction."""

    value = np.asarray(mask, dtype=bool)
    moved = np.moveaxis(value, context_axis, 0)
    if moved.shape[0] <= 0:
        raise ValueError("worst-context fraction requires at least one context")
    flattened = moved.reshape(moved.shape[0], -1)
    denominator = int(flattened.shape[1])
    if denominator <= 0:
        raise ValueError("worst-context fraction requires at least one audit case")
    per_context = flattened.sum(axis=1, dtype=np.int64)
    context_index = int(np.argmin(per_context))
    numerator = int(per_context[context_index])
    return {
        "numerator": numerator,
        "denominator": denominator,
        "value": numerator / denominator,
        "context_index": context_index,
    }


def packed_bool_evidence(mask: np.ndarray) -> dict[str, object]:
    """Store a compact, independently decodable copy of a Boolean tensor."""

    value = np.ascontiguousarray(np.asarray(mask, dtype=np.bool_))
    packed = np.packbits(value.reshape(-1), bitorder="little").tobytes()
    return {
        "schema": "komorebi.neuralese.packed_bool.v1",
        "shape": list(value.shape),
        "bit_count": int(value.size),
        "encoding": "numpy.packbits-little/base64",
        "packed_sha256": sha256_bytes(packed),
        "packed_base64": base64.b64encode(packed).decode("ascii"),
    }


def unpack_bool_evidence(receipt: Mapping[str, Any]) -> np.ndarray:
    """Decode and authenticate a packed Boolean evidence tensor."""

    if (
        receipt.get("schema") != "komorebi.neuralese.packed_bool.v1"
        or receipt.get("encoding") != "numpy.packbits-little/base64"
    ):
        raise ValueError("packed Boolean evidence schema/encoding mismatch")
    shape_value = receipt.get("shape")
    if (
        not isinstance(shape_value, list)
        or not shape_value
        or not all(isinstance(item, int) and not isinstance(item, bool) and item >= 0 for item in shape_value)
    ):
        raise ValueError("packed Boolean evidence has an invalid shape")
    shape = tuple(int(item) for item in shape_value)
    bit_count = math.prod(shape)
    if int(receipt.get("bit_count", -1)) != bit_count:
        raise ValueError("packed Boolean evidence bit count mismatch")
    encoded = receipt.get("packed_base64")
    if not isinstance(encoded, str):
        raise ValueError("packed Boolean evidence payload is absent")
    try:
        packed = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError) as error:
        raise ValueError("packed Boolean evidence is not canonical base64") from error
    if base64.b64encode(packed).decode("ascii") != encoded:
        raise ValueError("packed Boolean evidence base64 is not canonical")
    if len(packed) != (bit_count + 7) // 8:
        raise ValueError("packed Boolean evidence byte count mismatch")
    if sha256_bytes(packed) != receipt.get("packed_sha256"):
        raise ValueError("packed Boolean evidence digest mismatch")
    unpacked = np.unpackbits(
        np.frombuffer(packed, dtype=np.uint8),
        bitorder="little",
        count=bit_count,
    ).astype(np.bool_, copy=False)
    return unpacked.reshape(shape)


def numeric_summary(values: Iterable[float] | np.ndarray) -> dict[str, object]:
    array = np.asarray(values, dtype=np.float64)
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return {
            "count": 0,
            "undefined": int(array.size),
            "minimum": None,
            "p10": None,
            "median": None,
            "p90": None,
            "p95": None,
            "maximum": None,
        }
    return {
        "count": int(finite.size),
        "undefined": int(array.size - finite.size),
        "minimum": float(finite.min()),
        "p10": float(np.quantile(finite, 0.10)),
        "median": float(np.median(finite)),
        "p90": float(np.quantile(finite, 0.90)),
        "p95": float(np.quantile(finite, 0.95, method="higher")),
        "maximum": float(finite.max()),
    }


def softmax64(logits: np.ndarray) -> np.ndarray:
    value = np.asarray(logits, dtype=np.float64)
    with np.errstate(invalid="ignore", over="ignore", divide="ignore"):
        shifted = value - np.max(value, axis=-1, keepdims=True)
        exponential = np.exp(shifted)
        return exponential / exponential.sum(axis=-1, keepdims=True)


def oriented_angles64(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    first = np.asarray(left, dtype=np.float64)
    second = np.asarray(right, dtype=np.float64)
    first_norm = np.linalg.norm(first, axis=-1)
    second_norm = np.linalg.norm(second, axis=-1)
    defined = (
        np.isfinite(first).all(axis=-1)
        & np.isfinite(second).all(axis=-1)
        & np.isfinite(first_norm)
        & np.isfinite(second_norm)
        & (first_norm > RAY_NORM_STRICT_MINIMUM)
        & (second_norm > RAY_NORM_STRICT_MINIMUM)
    )
    output = np.full(first_norm.shape, np.nan, dtype=np.float64)
    cosine = np.sum(first * second, axis=-1)
    cosine[defined] /= first_norm[defined] * second_norm[defined]
    output[defined] = np.arccos(np.clip(cosine[defined], -1.0, 1.0))
    return output


def hidden_rays_defined64(hidden: np.ndarray) -> np.ndarray:
    value = np.asarray(hidden, dtype=np.float64)
    norm = np.linalg.norm(value, axis=-1)
    return (
        np.isfinite(value).all(axis=-1)
        & np.isfinite(norm)
        & (norm > RAY_NORM_STRICT_MINIMUM)
    )


def correct_class_margin64(logits: np.ndarray, targets: np.ndarray) -> np.ndarray:
    value = np.asarray(logits, dtype=np.float64)
    labels = np.asarray(targets, dtype=np.int64)
    target_value = np.take_along_axis(value, labels[..., None], axis=-1)[..., 0]
    competitors = value.copy()
    np.put_along_axis(competitors, labels[..., None], -np.inf, axis=-1)
    return target_value - np.max(competitors, axis=-1)


def maximum_over_suffix(
    values: np.ndarray,
    *,
    undefined_fill: float | None = None,
) -> np.ndarray:
    value = np.asarray(values, dtype=np.float64)
    finite = np.isfinite(value)
    if undefined_fill is not None:
        return np.max(np.where(finite, value, float(undefined_fill)), axis=0)
    result = np.full(value.shape[1:], np.nan, dtype=np.float64)
    any_finite = finite.any(axis=0)
    safe = np.where(finite, value, -np.inf)
    result[any_finite] = np.max(safe, axis=0)[any_finite]
    return result


def paired_task_counts(
    clean_correct: np.ndarray,
    condition_correct: np.ndarray,
) -> dict[str, int]:
    clean = np.asarray(clean_correct, dtype=bool)
    condition = np.asarray(condition_correct, dtype=bool)
    return {
        "both_correct": int((clean & condition).sum()),
        "clean_only": int((clean & ~condition).sum()),
        "condition_only": int((~clean & condition).sum()),
        "both_wrong": int((~clean & ~condition).sum()),
    }


def correct_from_rollout(
    hidden: np.ndarray,
    logits: np.ndarray,
    targets: np.ndarray,
) -> np.ndarray:
    endpoint_valid = hidden_rays_defined64(hidden) & np.isfinite(logits).all(axis=-1)
    return endpoint_valid & (np.argmax(logits, axis=-1) == targets)


def assert_finite_rollout(
    hidden: np.ndarray,
    logits: np.ndarray,
    *,
    label: str,
) -> None:
    """Treat nonfinite computation in a defined branch as procedural failure."""

    if not bool(np.isfinite(hidden).all()):
        raise FloatingPointError(f"unexpected nonfinite hidden rollout: {label}")
    if not bool(np.isfinite(logits).all()):
        raise FloatingPointError(f"unexpected nonfinite logit rollout: {label}")


def factorial_contrast_summary(
    correct: Mapping[str, np.ndarray],
    suffixes: Sequence[tuple[int, ...]],
) -> dict[str, object]:
    """Report matched selector/section effects from the exact same cases."""

    comparisons = {
        "decoder_prototype_minus_decoder_anchor": (
            "decoder_prototype",
            "decoder_anchor",
        ),
        "oracle_prototype_minus_oracle_anchor": (
            "oracle_prototype",
            "oracle_anchor",
        ),
        "decoder_prototype_minus_native": ("decoder_prototype", "native"),
        "oracle_prototype_minus_decoder_prototype": (
            "oracle_prototype",
            "decoder_prototype",
        ),
    }
    strata = {
        "all_H0_to_H6": list(range(len(suffixes))),
        **{
            f"H{length}": [
                index for index, word in enumerate(suffixes) if len(word) == length
            ]
            for length in PRIMARY_GATE_CONTRACT["horizons"]
        },
    }
    output: dict[str, object] = {}
    for contrast_name, (left_name, right_name) in comparisons.items():
        per_stratum: dict[str, object] = {}
        for stratum_name, indices in strata.items():
            left = np.asarray(correct[left_name][indices], dtype=bool)
            right = np.asarray(correct[right_name][indices], dtype=bool)
            left_only = int((left & ~right).sum())
            right_only = int((~left & right).sum())
            denominator = int(left.size)
            per_stratum[stratum_name] = {
                "left": left_name,
                "right": right_name,
                "both_correct": int((left & right).sum()),
                "left_only_correct": left_only,
                "right_only_correct": right_only,
                "both_wrong": int((~left & ~right).sum()),
                "difference_numerator": left_only - right_only,
                "denominator": denominator,
                "accuracy_difference": (left_only - right_only) / denominator,
            }
        output[contrast_name] = per_stratum

    interaction: dict[str, object] = {}
    for stratum_name, indices in strata.items():
        arrays = {
            name: np.asarray(correct[name][indices], dtype=np.int8)
            for name in (
                "decoder_prototype",
                "decoder_anchor",
                "oracle_prototype",
                "oracle_anchor",
            )
        }
        values = (
            arrays["decoder_prototype"]
            - arrays["decoder_anchor"]
            - arrays["oracle_prototype"]
            + arrays["oracle_anchor"]
        )
        denominator = int(values.size)
        numerator = int(values.astype(np.int64).sum())
        interaction[stratum_name] = {
            "record_kind": "signed_factorial_interaction",
            "signed_numerator": numerator,
            "denominator": denominator,
            "signed_value": numerator / denominator,
            "formula": "(decoder_prototype-decoder_anchor)-(oracle_prototype-oracle_anchor)",
        }
    output["selector_by_section_interaction"] = interaction
    return output


def selector_localization_summary(
    decoder_correct: np.ndarray,
    oracle_correct: np.ndarray,
    selector_correct: np.ndarray,
    suffixes: Sequence[tuple[int, ...]],
) -> dict[str, object]:
    """Locate every autonomous-versus-oracle loss at selector-error cuts."""

    strata = {
        "all_H0_to_H6": list(range(len(suffixes))),
        **{
            f"H{length}": [
                index for index, word in enumerate(suffixes) if len(word) == length
            ]
            for length in PRIMARY_GATE_CONTRACT["horizons"]
        },
    }
    output: dict[str, object] = {}
    for name, indices in strata.items():
        decoder = np.asarray(decoder_correct[indices], dtype=bool)
        oracle = np.asarray(oracle_correct[indices], dtype=bool)
        selected = np.broadcast_to(
            np.asarray(selector_correct, dtype=bool)[None, :, :],
            decoder.shape,
        )
        excess = oracle & ~decoder
        excess_count = int(excess.sum())
        localized = int((excess & ~selected).sum())
        output[name] = {
            "oracle_correct_decoder_wrong": excess_count,
            "those_at_selector_error_cuts": localized,
            "fraction_localized": (
                localized / excess_count if excess_count else None
            ),
            "any_excess_error_on_selector_correct_cut": bool(
                np.any(excess & selected)
            ),
            "decoder_errors_at_selector_error_cuts": int(
                (~decoder & ~selected).sum()
            ),
        }
    return output


def evaluate_condition(
    hidden: np.ndarray,
    logits: np.ndarray,
    clean_hidden: np.ndarray,
    clean_logits: np.ndarray,
    native_hidden: np.ndarray,
    native_logits: np.ndarray,
    targets: np.ndarray,
    suffixes: Sequence[tuple[int, ...]],
    *,
    wrong_targets: np.ndarray | None = None,
    selector_correct: np.ndarray | None = None,
) -> dict[str, object]:
    logits_finite = np.isfinite(logits).all(axis=-1)
    hidden_ray_defined = hidden_rays_defined64(hidden)
    endpoint_valid = logits_finite & hidden_ray_defined
    clean_logits_finite = np.isfinite(clean_logits).all(axis=-1)
    clean_hidden_ray_defined = hidden_rays_defined64(clean_hidden)
    clean_endpoint_valid = clean_logits_finite & clean_hidden_ray_defined
    prediction = np.argmax(logits, axis=-1)
    clean_prediction = np.argmax(clean_logits, axis=-1)
    native_logits_finite = np.isfinite(native_logits).all(axis=-1)
    native_hidden_ray_defined = hidden_rays_defined64(native_hidden)
    native_endpoint_valid = native_logits_finite & native_hidden_ray_defined
    native_prediction = np.argmax(native_logits, axis=-1)
    correct = endpoint_valid & (prediction == targets)
    clean_correct = clean_endpoint_valid & (clean_prediction == targets)
    agreement = endpoint_valid & clean_endpoint_valid & (prediction == clean_prediction)
    native_agreement = endpoint_valid & native_endpoint_valid & (prediction == native_prediction)
    native_correct = native_endpoint_valid & (native_prediction == targets)
    tv = 0.5 * np.abs(softmax64(logits) - softmax64(clean_logits)).sum(axis=-1)
    centered = logits.astype(np.float64) - logits.astype(np.float64).mean(axis=-1, keepdims=True)
    clean_centered = clean_logits.astype(np.float64) - clean_logits.astype(np.float64).mean(axis=-1, keepdims=True)
    logit_angle = oriented_angles64(centered, clean_centered)
    hidden_angle = oriented_angles64(hidden, clean_hidden)
    native_tv = 0.5 * np.abs(softmax64(logits) - softmax64(native_logits)).sum(axis=-1)
    native_centered = native_logits.astype(np.float64) - native_logits.astype(np.float64).mean(axis=-1, keepdims=True)
    native_logit_angle = oriented_angles64(centered, native_centered)
    native_hidden_angle = oriented_angles64(hidden, native_hidden)
    margin = correct_class_margin64(logits, targets)
    damage_denominator = int(clean_correct.sum())
    damage_numerator = int((clean_correct & ~correct).sum())
    rescue_denominator = int((~clean_correct).sum())
    rescue_numerator = int((~clean_correct & correct).sum())
    native_damage_denominator = int(native_correct.sum())
    native_damage_numerator = int((native_correct & ~correct).sum())
    native_rescue_denominator = int((~native_correct).sum())
    native_rescue_numerator = int((~native_correct & correct).sum())

    per_length: dict[str, object] = {}
    for length in range(SUFFIX_MAX_LENGTH + 1):
        indices = [index for index, word in enumerate(suffixes) if len(word) == length]
        length_correct = correct[indices]
        length_native_correct = native_correct[indices]
        per_length[str(length)] = {
            "word_count": len(indices),
            "task_accuracy": exact_fraction(length_correct),
            "native_task_accuracy": exact_fraction(length_native_correct),
            "all_words_task_correct": exact_fraction(np.all(length_correct, axis=0)),
            "worst_context": worst_context_fraction(
                length_correct,
                context_axis=1,
            ),
            "joint_task_counts_with_native": paired_task_counts(
                length_native_correct,
                length_correct,
            ),
        }

    per_suffix: list[dict[str, object]] = []
    for word_index, word in enumerate(suffixes):
        per_suffix.append(
            {
                "word": list(word),
                "length": len(word),
                "endpoint_valid": exact_fraction(endpoint_valid[word_index]),
                "logits_finite": exact_fraction(logits_finite[word_index]),
                "hidden_ray_defined": exact_fraction(hidden_ray_defined[word_index]),
                "accuracy": exact_fraction(correct[word_index]),
                "clean_prediction_agreement": exact_fraction(agreement[word_index]),
                "native_prediction_agreement": exact_fraction(native_agreement[word_index]),
                "worst_context": worst_context_fraction(
                    correct[word_index],
                    context_axis=0,
                ),
            }
        )

    output: dict[str, object] = {
        "endpoint_valid": exact_fraction(endpoint_valid),
        "logits_finite": exact_fraction(logits_finite),
        "hidden_ray_defined": exact_fraction(hidden_ray_defined),
        "task_accuracy": exact_fraction(correct),
        "clean_prediction_agreement": exact_fraction(agreement),
        "native_prediction_agreement": exact_fraction(native_agreement),
        "joint_task_counts_with_clean": paired_task_counts(clean_correct, correct),
        "joint_task_counts_with_native": paired_task_counts(native_correct, correct),
        "damage_given_clean_correct": {
            "numerator": damage_numerator,
            "denominator": damage_denominator,
            "value": damage_numerator / damage_denominator if damage_denominator else None,
        },
        "rescue_given_clean_wrong": {
            "numerator": rescue_numerator,
            "denominator": rescue_denominator,
            "value": rescue_numerator / rescue_denominator if rescue_denominator else None,
        },
        "damage_given_native_correct": {
            "numerator": native_damage_numerator,
            "denominator": native_damage_denominator,
            "value": native_damage_numerator / native_damage_denominator if native_damage_denominator else None,
        },
        "rescue_given_native_wrong": {
            "numerator": native_rescue_numerator,
            "denominator": native_rescue_denominator,
            "value": native_rescue_numerator / native_rescue_denominator if native_rescue_denominator else None,
        },
        "native_error_reduction": {
            "rescues": native_rescue_numerator,
            "damages": native_damage_numerator,
            "native_errors": native_rescue_denominator,
            "net_errors_removed": native_rescue_numerator - native_damage_numerator,
            "value": (
                (native_rescue_numerator - native_damage_numerator)
                / native_rescue_denominator
                if native_rescue_denominator
                else None
            ),
        },
        "softmax_total_variation_from_clean": numeric_summary(tv),
        "centered_logit_angle_from_clean_radians": numeric_summary(logit_angle),
        "hidden_angle_from_clean_radians": numeric_summary(hidden_angle),
        "softmax_total_variation_from_native": numeric_summary(native_tv),
        "centered_logit_angle_from_native_radians": numeric_summary(native_logit_angle),
        "hidden_angle_from_native_radians": numeric_summary(native_hidden_angle),
        "correct_class_margin": numeric_summary(margin),
        "h6_per_context_state": {
            "any_decision_disagreement": exact_fraction(np.any(~agreement, axis=0)),
            "any_native_decision_disagreement": exact_fraction(np.any(~native_agreement, axis=0)),
            "all_suffixes_task_correct": exact_fraction(np.all(correct, axis=0)),
            "any_undefined_softmax_total_variation": exact_fraction(np.any(~np.isfinite(tv), axis=0)),
            "any_undefined_centered_logit_angle": exact_fraction(np.any(~np.isfinite(logit_angle), axis=0)),
            "any_undefined_hidden_angle": exact_fraction(np.any(~np.isfinite(hidden_angle), axis=0)),
            "any_undefined_softmax_total_variation_from_native": exact_fraction(np.any(~np.isfinite(native_tv), axis=0)),
            "any_undefined_centered_logit_angle_from_native": exact_fraction(np.any(~np.isfinite(native_logit_angle), axis=0)),
            "any_undefined_hidden_angle_from_native": exact_fraction(np.any(~np.isfinite(native_hidden_angle), axis=0)),
            "maximum_softmax_total_variation": numeric_summary(maximum_over_suffix(tv, undefined_fill=1.0)),
            "maximum_centered_logit_angle_radians": numeric_summary(maximum_over_suffix(logit_angle, undefined_fill=math.pi)),
            "maximum_hidden_angle_radians": numeric_summary(maximum_over_suffix(hidden_angle, undefined_fill=math.pi)),
            "maximum_softmax_total_variation_from_native": numeric_summary(maximum_over_suffix(native_tv, undefined_fill=1.0)),
            "maximum_centered_logit_angle_from_native_radians": numeric_summary(maximum_over_suffix(native_logit_angle, undefined_fill=math.pi)),
            "maximum_hidden_angle_from_native_radians": numeric_summary(maximum_over_suffix(native_hidden_angle, undefined_fill=math.pi)),
        },
        "worst_context": worst_context_fraction(correct, context_axis=1),
        "per_length": per_length,
        "per_suffix": per_suffix,
        "prediction_tensor": tensor_receipt(prediction.astype(np.int64)),
        "correct_tensor": tensor_receipt(correct.astype(np.bool_)),
        "correct_evidence": packed_bool_evidence(correct),
    }
    if wrong_targets is not None:
        counterfactual_correct = endpoint_valid & (prediction == wrong_targets)
        wrong_per_length: dict[str, object] = {}
        for length in range(SUFFIX_MAX_LENGTH + 1):
            indices = [
                index for index, word in enumerate(suffixes) if len(word) == length
            ]
            wrong_per_length[str(length)] = {
                "counterfactual_accuracy": exact_fraction(
                    counterfactual_correct[indices]
                ),
                "factual_leakage": exact_fraction(correct[indices]),
            }
        output["wrong_section_control"] = {
            "counterfactual_accuracy": exact_fraction(counterfactual_correct),
            "factual_leakage": exact_fraction(correct),
            "empty_suffix_counterfactual_accuracy": exact_fraction(counterfactual_correct[0]),
            "empty_suffix_factual_leakage": exact_fraction(correct[0]),
            "per_length": wrong_per_length,
            "counterfactual_correct_evidence": packed_bool_evidence(
                counterfactual_correct
            ),
        }
    if selector_correct is not None:
        selector = np.asarray(selector_correct, dtype=bool)
        if selector.shape != correct.shape[1:]:
            raise ValueError("selector-correct mask shape mismatch")
        expanded_selector = np.broadcast_to(selector[None, :, :], correct.shape)
        selected_count = int(expanded_selector.sum())
        missed_count = int((~expanded_selector).sum())
        conditional_per_length: dict[str, object] = {}
        for length in range(SUFFIX_MAX_LENGTH + 1):
            indices = [index for index, word in enumerate(suffixes) if len(word) == length]
            length_correct = correct[indices]
            length_selector = np.broadcast_to(
                selector[None, :, :],
                length_correct.shape,
            )
            denominator = int(length_selector.sum())
            numerator = int((length_correct & length_selector).sum())
            wrong_denominator = int((~length_selector).sum())
            wrong_errors = int((~length_correct & ~length_selector).sum())
            conditional_per_length[str(length)] = {
                "task_accuracy_given_selector_correct": {
                    "numerator": numerator,
                    "denominator": denominator,
                    "value": numerator / denominator if denominator else None,
                },
                "task_error_given_selector_wrong": {
                    "numerator": wrong_errors,
                    "denominator": wrong_denominator,
                    "value": (
                        wrong_errors / wrong_denominator
                        if wrong_denominator
                        else None
                    ),
                },
            }
        output["conditional_on_selector"] = {
            "selector_accuracy_at_cuts": exact_fraction(selector),
            "task_accuracy_given_selector_correct": {
                "numerator": int((correct & expanded_selector).sum()),
                "denominator": selected_count,
                "value": (
                    int((correct & expanded_selector).sum()) / selected_count
                    if selected_count
                    else None
                ),
            },
            "task_error_given_selector_wrong": {
                "numerator": int((~correct & ~expanded_selector).sum()),
                "denominator": missed_count,
                "value": (
                    int((~correct & ~expanded_selector).sum()) / missed_count
                    if missed_count
                    else None
                ),
            },
            "per_length": conditional_per_length,
        }
    return output


def build_targets(
    bank: Mapping[str, np.ndarray],
    suffixes: Sequence[tuple[int, ...]],
    starts: np.ndarray | None = None,
) -> np.ndarray:
    if starts is None:
        contexts = int(bank["maps"].shape[0])
        starts = np.broadcast_to(
            np.arange(N_STATES, dtype=np.int64),
            (contexts, N_STATES),
        )
    return np.stack(
        [
            apply_visible_word(
                bank["maps"],
                bank["canonical_to_slot"],
                starts,
                word,
            )
            for word in suffixes
        ],
        axis=0,
    )


def clean_reference_summary(
    hidden: np.ndarray,
    logits: np.ndarray,
    targets: np.ndarray,
) -> dict[str, object]:
    logits_finite = np.isfinite(logits).all(axis=-1)
    hidden_ray_defined = hidden_rays_defined64(hidden)
    endpoint_valid = logits_finite & hidden_ray_defined
    prediction = np.argmax(logits, axis=-1)
    correct = endpoint_valid & (prediction == targets)
    return {
        "endpoint_valid": exact_fraction(endpoint_valid),
        "logits_finite": exact_fraction(logits_finite),
        "hidden_ray_defined": exact_fraction(hidden_ray_defined),
        "task_accuracy": exact_fraction(correct),
        "all_suffixes_task_correct": exact_fraction(np.all(correct, axis=0)),
        "worst_context": worst_context_fraction(correct, context_axis=1),
        "correct_class_margin": numeric_summary(correct_class_margin64(logits, targets)),
        "prediction_tensor": tensor_receipt(prediction.astype(np.int64)),
        "correct_tensor": tensor_receipt(correct.astype(np.bool_)),
        "correct_evidence": packed_bool_evidence(correct),
    }


def fraction_gate(
    name: str,
    fraction: Mapping[str, Any],
    threshold: float,
    *,
    relation: str = "at_least",
) -> dict[str, object]:
    """Evaluate a rational threshold directly from integer counts."""

    numerator = int(fraction["numerator"])
    denominator = int(fraction["denominator"])
    if denominator <= 0:
        return {
            "name": name,
            "relation": relation,
            "threshold": threshold,
            "numerator": numerator,
            "denominator": denominator,
            "integer_boundary": None,
            "pass": False,
        }
    exact_threshold = Fraction(str(threshold))
    scaled_numerator = exact_threshold.numerator * denominator
    scaled_denominator = exact_threshold.denominator
    if relation == "at_least":
        boundary = (scaled_numerator + scaled_denominator - 1) // scaled_denominator
        passed = numerator >= boundary
    elif relation == "at_most":
        boundary = scaled_numerator // scaled_denominator
        passed = numerator <= boundary
    else:
        raise ValueError(f"unknown fraction-gate relation: {relation}")
    return {
        "name": name,
        "relation": relation,
        "threshold": threshold,
        "numerator": numerator,
        "denominator": denominator,
        "integer_boundary": boundary,
        "pass": bool(passed),
    }


def boolean_gate(name: str, passed: bool, **evidence: object) -> dict[str, object]:
    return {"name": name, "pass": bool(passed), **evidence}


def paired_native_gates(
    counts: Mapping[str, Any],
    *,
    total: int,
    name_prefix: str = "",
) -> list[dict[str, object]]:
    damages = int(counts["clean_only"])
    rescues = int(counts["condition_only"])
    native_correct = damages + int(counts["both_correct"])
    native_errors = rescues + int(counts["both_wrong"])
    checks = [
        fraction_gate(
            f"{name_prefix}damage_given_native_correct_at_most_0.005",
            {"numerator": damages, "denominator": native_correct},
            float(PRIMARY_GATE_CONTRACT["damage_given_native_correct_maximum"]),
            relation="at_most",
        )
    ]
    minimum_error_rate = float(
        PRIMARY_GATE_CONTRACT["native_error_rate_for_reduction_gate"]
    )
    reduction_minimum = float(
        PRIMARY_GATE_CONTRACT["net_native_error_reduction_minimum"]
    )
    minimum_error_fraction = Fraction(str(minimum_error_rate))
    minimum_error_count = (
        minimum_error_fraction.numerator * total
        + minimum_error_fraction.denominator
        - 1
    ) // minimum_error_fraction.denominator
    reduction_fraction = Fraction(str(reduction_minimum))
    if native_errors >= minimum_error_count:
        boundary = (
            reduction_fraction.numerator * native_errors
            + reduction_fraction.denominator
            - 1
        ) // reduction_fraction.denominator
        checks.append(
            boolean_gate(
                f"{name_prefix}native_net_error_reduction_at_least_0.50",
                rescues - damages >= boundary,
                rescues=rescues,
                damages=damages,
                native_errors=native_errors,
                required_net_errors_removed=boundary,
                value=(rescues - damages) / native_errors if native_errors else None,
                evaluable=True,
            )
        )
    else:
        checks.append(
            boolean_gate(
                f"{name_prefix}native_error_reduction_not_evaluable_low_base_error",
                True,
                native_errors=native_errors,
                minimum_for_evaluation=minimum_error_count,
                evaluable=False,
            )
        )
    return checks


def checkpoint_primary_gate(
    prefix_results: Mapping[str, Any],
    prototype_section_audit: Mapping[str, Any],
) -> dict[str, object]:
    """Apply the preregistered decoder-prototype H5/H6 gate per prefix."""

    checks: list[dict[str, object]] = []
    repair_superiority_checks: list[dict[str, object]] = []
    checks.append(
        boolean_gate(
            "prototype_section_is_defined",
            bool(prototype_section_audit.get("section_defined")),
        )
    )
    consistency = prototype_section_audit["section_consistency"]
    checks.append(
        fraction_gate(
            "prototype_section_decodes_8_of_8",
            consistency["self_decoded_section"],
            float(PRIMARY_GATE_CONTRACT["prototype_section_decoding_minimum"]),
        )
    )
    for generator, audit in prototype_section_audit[
        "one_step_semantic_commutation"
    ]["per_generator"].items():
        checks.append(
            fraction_gate(
                f"prototype_generator_{generator}_commutation_at_least_0.99",
                audit["self_decoded_section"],
                float(PRIMARY_GATE_CONTRACT["one_step_commutation_minimum"]),
            )
        )
        checks.append(
            fraction_gate(
                f"prototype_generator_{generator}_worst_context_at_least_0.95",
                audit["self_decoded_section_worst_context"],
                float(PRIMARY_GATE_CONTRACT["one_step_worst_context_minimum"]),
            )
        )

    for prefix_name, prefix in prefix_results.items():
        selector = prefix["selector_diagnostics"]["decoder"]
        checks.append(
            fraction_gate(
                f"{prefix_name}/decoder_selector_at_least_0.99",
                selector,
                float(PRIMARY_GATE_CONTRACT["selector_accuracy_minimum"]),
            )
        )
        checks.append(
            fraction_gate(
                f"{prefix_name}/decoder_selector_worst_context_at_least_0.98",
                prefix["selector_diagnostics"]["decoder_worst_context"],
                float(PRIMARY_GATE_CONTRACT["selector_worst_context_minimum"]),
            )
        )
        decoder = prefix["conditions"]["decoder_prototype"]
        oracle = prefix["conditions"]["oracle_prototype"]
        wrong = prefix["conditions"]["wrong_prototype_control"][
            "wrong_section_control"
        ]
        idempotence = prefix["selector_diagnostics"][
            "decoder_prototype_reset_idempotence"
        ]
        idempotence_residual = idempotence["maximum_hidden_discrepancy"]
        checks.extend(
            [
                fraction_gate(
                    f"{prefix_name}/decoder_prototype_reset_label_idempotence",
                    idempotence["selected_label_unchanged"],
                    1.0,
                ),
                boolean_gate(
                    f"{prefix_name}/decoder_prototype_reset_hidden_idempotence",
                    idempotence_residual is not None
                    and float(idempotence_residual)
                    <= float(
                        PRIMARY_GATE_CONTRACT[
                            "reset_idempotence_hidden_tolerance"
                        ]
                    ),
                    value=(
                        float(idempotence_residual)
                        if idempotence_residual is not None
                        else None
                    ),
                    threshold=float(
                        PRIMARY_GATE_CONTRACT[
                            "reset_idempotence_hidden_tolerance"
                        ]
                    ),
                ),
                fraction_gate(
                    f"{prefix_name}/empty_suffix_exact",
                    decoder["per_length"]["0"]["task_accuracy"],
                    1.0,
                ),
            ]
        )
        conditional = decoder["conditional_on_selector"]
        for length in PRIMARY_GATE_CONTRACT["horizons"]:
            key = str(length)
            decoder_length = decoder["per_length"][key]
            oracle_length = oracle["per_length"][key]
            wrong_length = wrong["per_length"][key]
            accuracy = decoder_length["task_accuracy"]
            oracle_accuracy = oracle_length["task_accuracy"]
            if int(accuracy["denominator"]) != int(oracle_accuracy["denominator"]):
                raise RuntimeError("matched factorial cells have unequal denominators")
            denominator = int(accuracy["denominator"])
            gap_fraction = Fraction(
                str(PRIMARY_GATE_CONTRACT["oracle_accuracy_gap_maximum"])
            )
            allowed_gap = (
                gap_fraction.numerator * denominator
                // gap_fraction.denominator
            )
            oracle_gap = int(oracle_accuracy["numerator"]) - int(accuracy["numerator"])
            label = f"{prefix_name}/H{length}"
            checks.extend(
                [
                    fraction_gate(
                        f"{label}/conditional_correct_selection_at_least_0.995",
                        conditional["per_length"][key][
                            "task_accuracy_given_selector_correct"
                        ],
                        float(PRIMARY_GATE_CONTRACT["conditional_accuracy_minimum"]),
                    ),
                    fraction_gate(
                        f"{label}/decoder_prototype_accuracy_at_least_0.99",
                        accuracy,
                        float(PRIMARY_GATE_CONTRACT["unconditional_accuracy_minimum"]),
                    ),
                    fraction_gate(
                        f"{label}/oracle_prototype_accuracy_at_least_0.995",
                        oracle_accuracy,
                        float(PRIMARY_GATE_CONTRACT["oracle_accuracy_minimum"]),
                    ),
                    fraction_gate(
                        f"{label}/all_words_correct_at_least_0.99",
                        decoder_length["all_words_task_correct"],
                        float(PRIMARY_GATE_CONTRACT["all_words_correct_coverage_minimum"]),
                    ),
                    fraction_gate(
                        f"{label}/worst_context_accuracy_at_least_0.95",
                        decoder_length["worst_context"],
                        float(PRIMARY_GATE_CONTRACT["worst_context_accuracy_minimum"]),
                    ),
                    boolean_gate(
                        f"{label}/oracle_gap_at_most_0.01",
                        oracle_gap <= allowed_gap,
                        oracle_successes=int(oracle_accuracy["numerator"]),
                        decoder_successes=int(accuracy["numerator"]),
                        denominator=denominator,
                        allowed_success_gap=allowed_gap,
                    ),
                    fraction_gate(
                        f"{label}/wrong_prototype_counterfactual_at_least_0.95",
                        wrong_length["counterfactual_accuracy"],
                        float(
                            PRIMARY_GATE_CONTRACT[
                                "wrong_prototype_counterfactual_minimum"
                            ]
                        ),
                    ),
                    fraction_gate(
                        f"{label}/wrong_prototype_factual_leakage_at_most_0.05",
                        wrong_length["factual_leakage"],
                        float(
                            PRIMARY_GATE_CONTRACT[
                                "wrong_prototype_factual_leakage_maximum"
                            ]
                        ),
                        relation="at_most",
                    ),
                ]
            )
            paired_checks = paired_native_gates(
                decoder_length["joint_task_counts_with_native"],
                total=denominator,
                name_prefix=f"{label}/",
            )
            checks.append(paired_checks[0])
            repair_superiority_checks.append(paired_checks[1])
    repair_evaluable = all(
        bool(check.get("evaluable")) for check in repair_superiority_checks
    )
    if repair_evaluable:
        checks.extend(repair_superiority_checks)
    return {
        "label": "AUTONOMOUS_PROTOTYPE_RETRACTION_H5_H6",
        "aggregation": "logical AND across every structural, prefix, and horizon check",
        "performance_rate_thresholds_use_integer_counts": True,
        "continuous_tolerance_checks": [
            "decoder_prototype_reset_hidden_idempotence_at_most_1e-6"
        ],
        "pass": all(bool(check["pass"]) for check in checks),
        "check_count": len(checks),
        "checks": checks,
        "repair_superiority": {
            "status": (
                "PASS"
                if repair_evaluable
                and all(bool(check["pass"]) for check in repair_superiority_checks)
                else "FAIL"
                if repair_evaluable
                else "NOT_EVALUABLE_LOW_NATIVE_ERROR"
            ),
            "evaluable": repair_evaluable,
            "pass": (
                all(bool(check["pass"]) for check in repair_superiority_checks)
                if repair_evaluable
                else None
            ),
            "required_strata": len(repair_superiority_checks),
            "checks": repair_superiority_checks,
        },
    }


def checkpoint_receipts_by_key(seal: Mapping[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    records: dict[tuple[str, int], dict[str, Any]] = {}
    for receipt in seal.get("checkpoints", []):
        key = (str(receipt["arm"]), int(receipt["seed"]))
        if key in records:
            raise ValueError(f"duplicate checkpoint receipt: {key}")
        records[key] = dict(receipt)
    expected = {(arm, seed) for arm in ARMS for seed in SEEDS}
    if set(records) != expected:
        raise ValueError("checkpoint seal does not contain the exact 4 by 3 panel")
    return records


def verify_source_metadata(
    root: Path,
    archive: Path,
) -> tuple[dict[str, Any], dict[tuple[str, int], dict[str, Any]], dict[str, object]]:
    root = require_real_directory(root, label="sealed source root")
    archive = require_regular_file(archive, label="sealed source archive")
    if sha256_file(archive) != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("v0.4 source archive SHA-256 mismatch")
    result_root = root / "results" / "packet_closure_pilot"
    seal_path = require_regular_file(
        result_root / "CHECKPOINT_SEAL.json",
        label="checkpoint seal",
    )
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    if seal.get("schema") != "komorebi.neuralese.packet_closure.checkpoint_seal.v1":
        raise ValueError("checkpoint seal schema mismatch")
    if seal.get("version") != "0.4.0" or seal.get("profile") != "pilot":
        raise ValueError("v0.4 profile metadata mismatch")
    if seal.get("strict_checkpoint_firewall") is not True:
        raise ValueError("checkpoint seal firewall is not strict")
    seal_sha = sha256_file(seal_path)
    if seal_sha != EXPECTED_SEAL_SHA256:
        raise ValueError("extracted checkpoint seal does not match the canonical v0.4 receipt")
    receipts = checkpoint_receipts_by_key(seal)
    return seal, receipts, {
        "archive": {"path": archive.as_posix(), "sha256": EXPECTED_ARCHIVE_SHA256},
        "checkpoint_seal": {"path": seal_path.as_posix(), "sha256": seal_sha},
        "prior_v0.4_evaluation_bank_opened": False,
    }


def load_verified_checkpoint_arrays(
    root: Path,
    seal: Mapping[str, Any],
    receipt: Mapping[str, Any],
    *,
    arm: str,
    seed: int,
) -> tuple[dict[str, Any], dict[str, np.ndarray], dict[str, object]]:
    relative_checkpoint = Path(str(receipt["path"]))
    if (
        relative_checkpoint.is_absolute()
        or ".." in relative_checkpoint.parts
        or relative_checkpoint.name in {"", "."}
    ):
        raise ValueError(f"checkpoint receipt path is not a safe relative path: {arm}/{seed}")
    checkpoint_path = require_regular_file(
        root / "results" / "packet_closure_pilot" / relative_checkpoint,
        label=f"checkpoint {arm}/{seed}",
    )
    observed_sha = sha256_file(checkpoint_path)
    if observed_sha != receipt["sha256"]:
        raise RuntimeError(f"checkpoint SHA-256 mismatch: {checkpoint_path}")
    payload, arrays = load_checkpoint_restricted(checkpoint_path)
    if payload.get("schema") != "komorebi.neuralese.packet_closure.checkpoint.v1":
        raise ValueError(f"checkpoint schema mismatch: {checkpoint_path}")
    if payload.get("version") != "0.4.0" or payload.get("arm") != arm:
        raise ValueError(f"checkpoint identity mismatch: {checkpoint_path}")
    if int(payload.get("train_config", {}).get("seed", -1)) != seed:
        raise ValueError(f"checkpoint seed mismatch: {checkpoint_path}")
    if payload.get("source_digest") != seal.get("source_digest"):
        raise ValueError(f"checkpoint source digest mismatch: {checkpoint_path}")
    if payload.get("contract_sha256") != seal.get("contract_sha256"):
        raise ValueError(f"checkpoint contract digest mismatch: {checkpoint_path}")
    model_family = payload.get("arm_spec", {}).get("model_family")
    expected_family = "polar" if arm.startswith("polar_") else "raw"
    if model_family != expected_family:
        raise ValueError(f"checkpoint model-family mismatch: {checkpoint_path}")
    state_validation = validate_state_dict(arrays)
    observed_state_digest = state_dict_digest_numpy(arrays)
    if observed_state_digest != receipt.get("state_dict_digest"):
        raise ValueError(f"checkpoint state-dict digest mismatch: {checkpoint_path}")
    if observed_state_digest != payload.get("provenance", {}).get("final_state_digest"):
        raise ValueError(f"checkpoint provenance state digest mismatch: {checkpoint_path}")
    return payload, arrays, {
        "path": checkpoint_path.as_posix(),
        "expected_sha256": receipt["sha256"],
        "observed_sha256": observed_sha,
        "sha256_match": True,
        "state_dict_digest": observed_state_digest,
        "payload_schema": payload["schema"],
        "payload_version": payload["version"],
        "arm_spec": json_ready(payload.get("arm_spec")),
        "train_config": json_ready(payload.get("train_config")),
        "state_validation": state_validation,
    }


def verify_runtime_contract() -> dict[str, object]:
    """Fail before spending if the executing arithmetic runtime drifted."""

    if np.__version__ != EXPECTED_NUMPY_VERSION:
        raise RuntimeError(
            "NumPy version differs from the frozen arithmetic runtime"
        )
    return {
        "numpy_version": np.__version__,
        "expected_numpy_version": EXPECTED_NUMPY_VERSION,
        "match": True,
    }


def prepare_checkpoint_panel(
    root: Path,
    seal: Mapping[str, Any],
    receipts: Mapping[tuple[str, int], Mapping[str, Any]],
) -> tuple[tuple[PreparedCheckpoint, ...], dict[str, object]]:
    """Load and authenticate all parameters before any fresh-bank forward pass."""

    prepared: list[PreparedCheckpoint] = []
    receipt_rows: list[dict[str, object]] = []
    for arm in ARMS:
        for seed in SEEDS:
            _, arrays, checkpoint = load_verified_checkpoint_arrays(
                root,
                seal,
                receipts[(arm, seed)],
                arm=arm,
                seed=seed,
            )
            immutable_arrays: dict[str, np.ndarray] = {}
            for name, value in arrays.items():
                copied = np.ascontiguousarray(value, dtype=np.dtype("<f4")).copy()
                copied.setflags(write=False)
                immutable_arrays[name] = copied
            prepared.append(
                PreparedCheckpoint(
                    arm=arm,
                    seed=seed,
                    arrays=immutable_arrays,
                    checkpoint_receipt=checkpoint,
                )
            )
            receipt_rows.append(
                {
                    "arm": arm,
                    "seed": seed,
                    "path": checkpoint["path"],
                    "sha256": checkpoint["observed_sha256"],
                    "state_dict_digest": checkpoint["state_dict_digest"],
                    "restricted_parameter_load_pass": True,
                }
            )
    return tuple(prepared), {
        "status": "ALL_CHECKPOINTS_READY_BEFORE_FRESH_BANK_EVALUATION",
        "checkpoint_count": len(prepared),
        "parameter_only": True,
        "fresh_bank_state_applied_to_checkpoint": False,
        "checkpoints": receipt_rows,
    }


def run_parameter_only_preflight(root: Path, archive: Path) -> dict[str, object]:
    """Audit all sealed checkpoint geometries without constructing a fresh bank."""

    verify_runtime_contract()
    seal, receipts, source_receipts = verify_source_metadata(root, archive)
    cells: list[dict[str, object]] = []
    for arm in ARMS:
        for seed in SEEDS:
            _, arrays, checkpoint = load_verified_checkpoint_arrays(
                root,
                seal,
                receipts[(arm, seed)],
                arm=arm,
                seed=seed,
            )
            anchors = normalized_anchors32(arrays)
            try:
                _, projector = construct_anchor_projector32(anchors)
            except (FloatingPointError, RuntimeError, np.linalg.LinAlgError) as error:
                projector = projector_failure_receipt(error)
            cells.append(
                {
                    "arm": arm,
                    "seed": seed,
                    "checkpoint": checkpoint,
                    "projector": projector,
                }
            )
    projector_outcomes_pass = all(row["projector"]["pass"] for row in cells)
    return {
        "schema": "komorebi.neuralese.semantic_retraction.parameter_preflight.v1",
        "version": VERSION,
        "author": AUTHOR,
        "status": "PASS",
        "preflight_integrity_pass": True,
        "scope": "sealed checkpoint parameters and projector geometry only",
        "evaluation_bank_generated_or_opened": False,
        "prior_v0.4_evaluation_bank_opened": False,
        "behavioral_rollout_generated": False,
        "source_receipts": source_receipts,
        "checkpoint_count": len(cells),
        "all_projectors_pass": projector_outcomes_pass,
        "projector_diagnostic_outcome": (
            "ALL_VALID" if projector_outcomes_pass else "ONE_OR_MORE_INVALID_NONBLOCKING"
        ),
        "projection_diagnostic_is_nonblocking_for_core_factorial": True,
        "cells": cells,
    }


def evaluate_checkpoint(
    arm: str,
    seed: int,
    arrays: Mapping[str, np.ndarray],
    calibration_bank: Mapping[str, np.ndarray],
    evaluation_bank: Mapping[str, np.ndarray],
    calibration_words: Mapping[str, Sequence[int]],
    evaluation_words: Mapping[str, Sequence[int]],
) -> dict[str, object]:
    state_validation = validate_state_dict(arrays)
    calibration_operators, calibration_operator_receipt = encode_operators32(
        arrays,
        calibration_bank["tables"],
        polar=arm.startswith("polar_"),
    )
    anchors = normalized_anchors32(arrays)
    decoder = np.ascontiguousarray(arrays["decoder.weight"], dtype=np.float32)
    try:
        projector, projector_audit = construct_anchor_projector32(anchors)
    except (FloatingPointError, RuntimeError, np.linalg.LinAlgError) as error:
        projector = None
        projector_audit = projector_failure_receipt(error)
    applied_projector = projector if bool(projector_audit["pass"]) else None

    calibration_split_states = split_states_for_words32(
        anchors,
        calibration_operators,
        calibration_bank["canonical_to_slot"],
        calibration_words,
    )
    for calibration_name, calibration_states in calibration_split_states.items():
        if not bool(np.isfinite(calibration_states).all()):
            raise FloatingPointError(
                "unexpected nonfinite calibration-prefix state: "
                f"{calibration_name}"
            )
    prototypes, prototype_receipt = fit_calibration_prototypes(
        calibration_split_states
    )
    prototype_receipt["fit_before_any_evaluation_operator_or_rollout"] = True
    evaluation_operators, evaluation_operator_receipt = encode_operators32(
        arrays,
        evaluation_bank["tables"],
        polar=arm.startswith("polar_"),
    )
    anchor_section_audit = autonomous_section_audit(
        anchors,
        decoder,
        evaluation_operators,
        evaluation_bank,
        section_name="anchor",
    )
    prototype_section_audit = autonomous_section_audit(
        prototypes,
        decoder,
        evaluation_operators,
        evaluation_bank,
        section_name="held_out_prototype",
    )
    suffixes = words_upto()
    targets = build_targets(evaluation_bank, suffixes)
    wrong = wrong_visible_labels(evaluation_bank["phi"])
    wrong_targets = build_targets(
        evaluation_bank,
        suffixes,
        starts=wrong,
    )

    clean_initial = np.broadcast_to(
        anchors[None, :, :],
        (EVALUATION_CONTEXTS, N_STATES, HIDDEN_DIM),
    ).copy()
    clean_hidden, clean_logits = rollout_suffix_tree32(
        clean_initial,
        evaluation_operators,
        evaluation_bank["canonical_to_slot"],
        decoder,
        suffixes,
    )
    assert_finite_rollout(clean_hidden, clean_logits, label="clean semantic reference")

    evaluation_split_states = split_states_for_words32(
        anchors,
        evaluation_operators,
        evaluation_bank["canonical_to_slot"],
        evaluation_words,
    )
    prefix_results: dict[str, object] = {}
    for prefix_name, prefix_word in evaluation_words.items():
        native = evaluation_split_states[prefix_name]
        interventions, selectors, selected_labels = construct_interventions32(
            native,
            anchors,
            decoder,
            prototypes,
            applied_projector,
            evaluation_bank["phi"],
        )
        native_future_hidden, native_future_logits = rollout_suffix_tree32(
            interventions["native"],
            evaluation_operators,
            evaluation_bank["canonical_to_slot"],
            decoder,
            suffixes,
        )
        assert_finite_rollout(
            native_future_hidden,
            native_future_logits,
            label=f"{prefix_name}/native",
        )
        conditions: dict[str, object] = {}
        rollout_cache: dict[str, tuple[np.ndarray, np.ndarray]] = {}
        correct_cache: dict[str, np.ndarray] = {}
        for name in INTERVENTIONS:
            if name == "native":
                hidden, logits = native_future_hidden, native_future_logits
                intentionally_undefined = False
            else:
                hidden, logits, intentionally_undefined = rollout_intervention32(
                    name,
                    interventions[name],
                    evaluation_operators,
                    evaluation_bank["canonical_to_slot"],
                    decoder,
                    suffixes,
                    prototype_usable=bool(prototype_receipt["usable"]),
                    projector_available=applied_projector is not None,
                )
            if not intentionally_undefined:
                assert_finite_rollout(
                    hidden,
                    logits,
                    label=f"{prefix_name}/{name}",
                )
            rollout_cache[name] = (hidden, logits)
            correct_cache[name] = correct_from_rollout(hidden, logits, targets)
            selector_key = {
                "decoder_anchor": "decoder",
                "decoder_prototype": "decoder",
                "anchor_nearest_anchor": "anchor_nearest",
                "anchor_nearest_prototype": "anchor_nearest",
                "prototype_nearest_anchor": "prototype_nearest",
                "prototype_nearest_prototype": "prototype_nearest",
            }.get(name)
            selector_correct = (
                selected_labels[selector_key] == selected_labels["true"]
                if selector_key is not None
                else None
            )
            selector_defined_key = (
                f"{selector_key}_defined" if selector_key is not None else None
            )
            if (
                selector_correct is not None
                and selector_defined_key in selected_labels
            ):
                selector_correct = (
                    selector_correct
                    & selected_labels[selector_defined_key]
                )
            conditions[name] = evaluate_condition(
                hidden,
                logits,
                clean_hidden,
                clean_logits,
                native_future_hidden,
                native_future_logits,
                targets,
                suffixes,
                wrong_targets=(
                    wrong_targets
                    if name in {"wrong_anchor_control", "wrong_prototype_control"}
                    else None
                ),
                selector_correct=selector_correct,
            )
        decoder_correct = (
            selected_labels["decoder_defined"]
            & (selected_labels["decoder"] == selected_labels["true"])
        )
        equality_receipts: dict[str, object] = {}
        for section_name in ("anchor", "prototype"):
            if section_name == "prototype" and not bool(prototype_receipt["usable"]):
                equality_receipts[section_name] = {
                    "evaluable": False,
                    "bit_identical_on_correct_selection": None,
                }
                continue
            oracle_hidden, oracle_logits = rollout_cache[f"oracle_{section_name}"]
            decoder_hidden, decoder_logits = rollout_cache[f"decoder_{section_name}"]
            if not np.array_equal(
                oracle_hidden[:, decoder_correct],
                decoder_hidden[:, decoder_correct],
            ) or not np.array_equal(
                oracle_logits[:, decoder_correct],
                decoder_logits[:, decoder_correct],
            ):
                raise RuntimeError(
                    f"oracle/decoder {section_name} rollouts disagree under correct selection"
                )
            equality_receipts[section_name] = {
                "evaluable": True,
                "bit_identical_on_correct_selection": True,
            }
        native_split_prediction, native_split_finite = finite_argmax(
            decode32(native, decoder),
            label=f"{prefix_name} native split decoder",
        )
        native_split_ray_defined = hidden_rays_defined64(native)
        true = np.broadcast_to(np.arange(N_STATES), native_split_prediction.shape)
        prefix_results[prefix_name] = {
            "word": list(prefix_word),
            "length": len(prefix_word),
            "native_split_decoder_finite": exact_fraction(native_split_finite),
            "native_split_hidden_rays_defined": exact_fraction(
                native_split_ray_defined
            ),
            "native_split_task_accuracy": exact_fraction(
                native_split_finite
                & native_split_ray_defined
                & (native_split_prediction == true)
            ),
            "native_split_angle_to_clean_anchor_radians": numeric_summary(
                oriented_angles64(native, clean_initial)
            ),
            "native_split_tensor": tensor_receipt(native),
            "selector_diagnostics": selectors,
            "conditions": conditions,
            "factorial_contrasts": factorial_contrast_summary(
                correct_cache,
                suffixes,
            ),
            "selector_error_localization": selector_localization_summary(
                correct_cache["decoder_prototype"],
                correct_cache["oracle_prototype"],
                decoder_correct,
                suffixes,
            ),
            "factorial_integrity": {
                "decoder_label_tensor_reused_for_both_sections": True,
                "section_equality": equality_receipts,
            },
        }

    primary_gate = checkpoint_primary_gate(
        prefix_results,
        prototype_section_audit,
    )
    return {
        "arm": arm,
        "seed": seed,
        "state_dict": state_validation,
        "calibration_operator_construction": calibration_operator_receipt,
        "evaluation_operator_construction": evaluation_operator_receipt,
        "anchor_tensor": tensor_receipt(anchors),
        "decoder_tensor": tensor_receipt(decoder),
        "projector_diagnostic": {
            **projector_audit,
            "isolated_from_factorial_validity": True,
            "applied_only_when_audit_passes": True,
        },
        "held_out_calibration_prototype": prototype_receipt,
        "section_audits": {
            "anchor": anchor_section_audit,
            "prototype": prototype_section_audit,
        },
        "clean_semantic_endpoint": clean_reference_summary(clean_hidden, clean_logits, targets),
        "prefixes": prefix_results,
        "primary_gate": primary_gate,
    }


def run_learned_panel(
    root: Path,
    archive: Path,
    protocol: Mapping[str, Any],
    protocol_sha256: str,
    *,
    bank_path: Path,
    bank_bytes: bytes,
    bank_verification: Mapping[str, Any],
    spend_receipt: Mapping[str, Any],
    pre_spend_source_receipts: Mapping[str, Any],
    prepared_checkpoints: Sequence[PreparedCheckpoint],
    pre_spend_checkpoint_readiness: Mapping[str, Any],
) -> dict[str, object]:
    verify_runtime_contract()
    started = time.perf_counter()
    snapshot_sha256 = sha256_bytes(bank_bytes)
    if snapshot_sha256 != bank_verification["bank_sha256"]:
        raise RuntimeError("immutable bank snapshot differs from pre-spend verification")
    (
        calibration_bank,
        evaluation_bank,
        calibration_words,
        evaluation_words,
        bank_document,
    ) = load_fresh_bank_arrays(bank_bytes)
    if bank_document["bank_id"] != bank_verification["bank_id"]:
        raise RuntimeError("immutable bank snapshot has the wrong bank identity")
    checkpoint_hashes_before: dict[str, str] = {}
    checkpoint_results: list[dict[str, object]] = []
    expected_panel = [(arm, seed) for arm in ARMS for seed in SEEDS]
    observed_panel = [(row.arm, row.seed) for row in prepared_checkpoints]
    if observed_panel != expected_panel:
        raise RuntimeError("pre-spend checkpoint panel order or census drifted")
    for prepared in prepared_checkpoints:
        checkpoint = dict(prepared.checkpoint_receipt)
        checkpoint_hashes_before[str(checkpoint["path"])] = str(
            checkpoint["observed_sha256"]
        )
        result = evaluate_checkpoint(
            prepared.arm,
            prepared.seed,
            prepared.arrays,
            calibration_bank,
            evaluation_bank,
            calibration_words,
            evaluation_words,
        )
        result["checkpoint"] = checkpoint
        checkpoint_results.append(result)

    for path_text, before in checkpoint_hashes_before.items():
        after = sha256_file(Path(path_text))
        if after != before:
            raise RuntimeError(f"checkpoint changed during read-only analysis: {path_text}")
    bank_sha256_after = sha256_file(bank_path)
    if bank_sha256_after != snapshot_sha256:
        raise RuntimeError("fresh-bank file changed after the pre-spend snapshot")
    _, _, source_receipts_after = verify_source_metadata(root, archive)
    if source_receipts_after != pre_spend_source_receipts:
        raise RuntimeError("source metadata changed during execution")

    arm_labels: dict[str, object] = {}
    for arm in ARMS:
        rows = [row for row in checkpoint_results if row["arm"] == arm]
        if [int(row["seed"]) for row in rows] != list(SEEDS):
            raise RuntimeError(f"checkpoint result order drifted for {arm}")
        arm_labels[arm] = {
            "label": "AUTONOMOUS_PROTOTYPE_RETRACTION_H5_H6",
            "aggregation": "3_of_3_checkpoint_AND",
            "passing_seeds": [
                int(row["seed"]) for row in rows if row["primary_gate"]["pass"]
            ],
            "pass": all(bool(row["primary_gate"]["pass"]) for row in rows),
            "repair_superiority": {
                "status": (
                    "PASS"
                    if all(
                        row["primary_gate"]["repair_superiority"]["status"]
                        == "PASS"
                        for row in rows
                    )
                    else "FAIL"
                    if all(
                        bool(
                            row["primary_gate"]["repair_superiority"][
                                "evaluable"
                            ]
                        )
                        for row in rows
                    )
                    else "NOT_EVALUABLE_LOW_NATIVE_ERROR"
                ),
                "all_checkpoints_evaluable": all(
                    bool(row["primary_gate"]["repair_superiority"]["evaluable"])
                    for row in rows
                ),
            },
        }
    primary_arm = str(PRIMARY_GATE_CONTRACT["primary_arm"])
    full_cohort_pass = all(bool(value["pass"]) for value in arm_labels.values())
    primary_arm_pass = bool(arm_labels[primary_arm]["pass"])
    primary_repair_superiority = arm_labels[primary_arm]["repair_superiority"]

    return {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "analysis_status": "PROSPECTIVE_FRESH_BANK_FIXED_CHECKPOINT_CONFIRMATION",
        "claim_status": (
            "PRIMARY_OPERATIONAL_GATE_PASS"
            if primary_arm_pass
            else "VALID_NEGATIVE_PRIMARY_OPERATIONAL_GATE_FAIL"
        ),
        "claim_boundary": protocol["claim_boundary"],
        "protocol": {
            "path": PROTOCOL_PATH.as_posix(),
            "sha256": protocol_sha256,
            "status": protocol["status"],
            "implementation_receipts": protocol["implementation_receipts"],
        },
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch_imported": False,
            "device": "cpu",
            "model_arithmetic": "float32",
            "diagnostic_arithmetic": "float64",
            "elapsed_seconds": time.perf_counter() - started,
        },
        "design": {
            "checkpoint_count": len(checkpoint_results),
            "arms": list(ARMS),
            "seeds": list(SEEDS),
            "calibration_contexts": CALIBRATION_CONTEXTS,
            "evaluation_contexts": EVALUATION_CONTEXTS,
            "states_per_context": N_STATES,
            "calibration_prefixes": {
                name: list(word) for name, word in calibration_words.items()
            },
            "evaluation_prefixes": {
                name: list(word) for name, word in evaluation_words.items()
            },
            "suffixes": [list(word) for word in words_upto()],
            "interventions": list(INTERVENTIONS),
            "factorial": protocol["factorial"],
            "primary_gate_contract": PRIMARY_GATE_CONTRACT,
            "work_bound": expected_work_counts(),
        },
        "source_receipts": dict(pre_spend_source_receipts),
        "pre_spend_checkpoint_readiness": dict(pre_spend_checkpoint_readiness),
        "fresh_bank": {
            **dict(bank_verification),
            "bank_id": bank_document["bank_id"],
            "bank_sha256": snapshot_sha256,
            "evaluated_from_pre_spend_immutable_byte_snapshot": True,
        },
        "spend_receipt": dict(spend_receipt),
        "checkpoint_count": len(checkpoint_results),
        "checkpoints": checkpoint_results,
        "labels": {
            "primary_arm": primary_arm,
            "primary_arm_pass": primary_arm_pass,
            "primary_arm_repair_superiority": primary_repair_superiority,
            "full_fixed_checkpoint_cohort_pass": full_cohort_pass,
            "arms": arm_labels,
            "independent_checkpoint_replication": False,
            "architecture_independent_claim": False,
            "universal_neuralese_claim": False,
        },
        "input_immutability": {
            "checkpoint_count": len(checkpoint_hashes_before),
            "all_checkpoint_hashes_unchanged": True,
            "fresh_bank_sha256_before": snapshot_sha256,
            "fresh_bank_sha256_after": bank_sha256_after,
            "fresh_bank_bytes_unchanged": True,
        },
    }


def canonical_json_bytes(value: object) -> bytes:
    return (
        json.dumps(
            json_ready(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def exclusive_write(path: Path, payload: bytes) -> None:
    require_real_directory(path.parent, label="output parent")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o444)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    except BaseException:
        raise


def require_real_directory(path: Path, *, label: str) -> Path:
    absolute = path.absolute()
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        try:
            metadata = current.lstat()
        except FileNotFoundError as error:
            raise FileNotFoundError(f"missing {label}: {current}") from error
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError(f"{label} must have no symlink/non-directory component: {current}")
    return absolute


def ensure_output_directory(path: Path, *, label: str) -> Path:
    """Create one direct child safely, or validate an existing real directory."""

    absolute = path.absolute()
    require_real_directory(absolute.parent, label=f"{label} parent")
    try:
        os.mkdir(absolute, 0o755)
        descriptor = os.open(absolute.parent, os.O_RDONLY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except FileExistsError:
        pass
    return require_real_directory(absolute, label=label)


def _allocate_regular_file(path: Path, size: int) -> tuple[int, int]:
    """Create and physically allocate one reservation file."""

    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags, 0o600)
    try:
        if not hasattr(os, "posix_fallocate"):
            raise RuntimeError("physical result reservation requires os.posix_fallocate")
        os.posix_fallocate(descriptor, 0, size)
        os.fsync(descriptor)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size != size:
            raise RuntimeError("result reservation allocation did not persist exactly")
        return int(metadata.st_dev), int(metadata.st_ino)
    finally:
        os.close(descriptor)


def _probe_hardlink_publication(
    bundle: Path,
    source: Path,
    *,
    expected_device: int,
    expected_inode: int,
) -> bool:
    """Link the actual result reservation before spend, then restore it."""

    destination = bundle / HARDLINK_CANARY_NAME
    try:
        source_metadata = source.lstat()
        if (
            not stat.S_ISREG(source_metadata.st_mode)
            or stat.S_ISLNK(source_metadata.st_mode)
            or int(source_metadata.st_dev) != expected_device
            or int(source_metadata.st_ino) != expected_inode
        ):
            raise RuntimeError("result reservation changed before hard-link canary")
        original_link_count = int(source_metadata.st_nlink)
        os.link(source, destination, follow_symlinks=False)
        destination_metadata = destination.lstat()
        linked_source_metadata = source.lstat()
        if (
            not stat.S_ISREG(destination_metadata.st_mode)
            or stat.S_ISLNK(destination_metadata.st_mode)
            or int(destination_metadata.st_dev) != expected_device
            or int(destination_metadata.st_ino) != expected_inode
            or int(linked_source_metadata.st_dev) != expected_device
            or int(linked_source_metadata.st_ino) != expected_inode
            or int(destination_metadata.st_nlink) != original_link_count + 1
            or int(linked_source_metadata.st_nlink) != original_link_count + 1
        ):
            raise RuntimeError("hard-link publication canary changed inode identity")
        destination.unlink()
        restored_metadata = source.lstat()
        if (
            int(restored_metadata.st_dev) != expected_device
            or int(restored_metadata.st_ino) != expected_inode
            or int(restored_metadata.st_nlink) != original_link_count
        ):
            raise RuntimeError("hard-link canary did not restore reservation identity")
        directory = os.open(bundle, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return True
    except BaseException:
        try:
            destination_metadata = destination.lstat()
            if (
                stat.S_ISREG(destination_metadata.st_mode)
                and not stat.S_ISLNK(destination_metadata.st_mode)
                and int(destination_metadata.st_dev) == expected_device
                and int(destination_metadata.st_ino) == expected_inode
            ):
                destination.unlink()
        except (FileNotFoundError, OSError):
            pass
        try:
            directory = os.open(bundle, os.O_RDONLY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError:
            pass
        raise


def reserve_result_bundle() -> ResultReservation:
    """Reserve the final namespace and disk blocks before the bank is spent."""

    ensure_output_directory(RESULTS_DIRECTORY, label="result directory")
    free_bytes = int(shutil.disk_usage(RESULTS_DIRECTORY).free)
    if free_bytes < MIN_FREE_BYTES_BEFORE_SPEND:
        raise OSError(
            f"insufficient free space before spend: {free_bytes} < "
            f"{MIN_FREE_BYTES_BEFORE_SPEND}"
        )
    bundle = DEFAULT_BUNDLE.absolute()
    require_real_directory(bundle.parent, label="result bundle parent")
    try:
        os.mkdir(bundle, 0o700)
    except FileExistsError as error:
        raise FileExistsError("result bundle namespace is already reserved") from error
    result_path = bundle / RESULT_RESERVATION_NAME
    commit_path = bundle / COMMIT_RESERVATION_NAME
    canary_path = bundle / HARDLINK_CANARY_NAME
    try:
        parent_directory = os.open(bundle.parent, os.O_RDONLY)
        try:
            os.fsync(parent_directory)
        finally:
            os.close(parent_directory)
        result_device, result_inode = _allocate_regular_file(
            result_path,
            MAX_RESULT_BYTES,
        )
        commit_device, commit_inode = _allocate_regular_file(
            commit_path,
            COMMIT_RESERVATION_BYTES,
        )
        hardlink_publication_canary_completed = _probe_hardlink_publication(
            bundle,
            result_path,
            expected_device=result_device,
            expected_inode=result_inode,
        )
        directory = os.open(bundle, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        parent_directory = os.open(bundle.parent, os.O_RDONLY)
        try:
            os.fsync(parent_directory)
        finally:
            os.close(parent_directory)
    except BaseException:
        for path in (
            canary_path,
            commit_path,
            result_path,
        ):
            try:
                metadata = path.lstat()
            except FileNotFoundError:
                continue
            if stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
                path.unlink()
        try:
            bundle.rmdir()
        except OSError:
            pass
        try:
            parent_directory = os.open(bundle.parent, os.O_RDONLY)
            try:
                os.fsync(parent_directory)
            finally:
                os.close(parent_directory)
        except OSError:
            pass
        raise
    return ResultReservation(
        bundle=bundle,
        result_path=result_path,
        commit_path=commit_path,
        result_device=result_device,
        result_inode=result_inode,
        commit_device=commit_device,
        commit_inode=commit_inode,
        free_bytes_before=free_bytes,
        hardlink_publication_canary_completed=(
            hardlink_publication_canary_completed
        ),
    )


def _fill_reserved_file(
    path: Path,
    payload: bytes,
    *,
    maximum_bytes: int,
    expected_device: int,
    expected_inode: int,
    final_name: str,
) -> Path:
    if len(payload) > maximum_bytes:
        raise ValueError(
            f"serialized {final_name} exceeds frozen reservation: "
            f"{len(payload)} > {maximum_bytes}"
        )
    flags = os.O_RDWR
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(path, flags)
    try:
        metadata = os.fstat(descriptor)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or int(metadata.st_dev) != expected_device
            or int(metadata.st_ino) != expected_inode
            or metadata.st_size < maximum_bytes
        ):
            raise RuntimeError(f"{final_name} reservation identity changed")
        view = memoryview(payload)
        offset = 0
        while offset < len(view):
            written = os.write(descriptor, view[offset:])
            if written <= 0:
                raise OSError(f"short write while filling {final_name} reservation")
            offset += written
        os.ftruncate(descriptor, len(payload))
        os.fchmod(descriptor, 0o444)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    destination = path.with_name(final_name)
    try:
        os.link(path, destination, follow_symlinks=False)
    except FileExistsError as error:
        raise FileExistsError(f"refusing to replace existing {final_name}") from error
    published = destination.lstat()
    if (
        not stat.S_ISREG(published.st_mode)
        or int(published.st_dev) != expected_device
        or int(published.st_ino) != expected_inode
    ):
        destination.unlink()
        raise RuntimeError(f"{final_name} publication linked a substituted inode")
    source = path.lstat()
    if (
        int(source.st_dev) != expected_device
        or int(source.st_ino) != expected_inode
    ):
        destination.unlink()
        raise RuntimeError(f"{final_name} reservation changed before publication")
    try:
        path.unlink()
    except BaseException:
        try:
            destination.unlink()
        finally:
            raise
    directory = os.open(destination.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    return destination


def release_unspent_result_reservation(reservation: ResultReservation) -> None:
    """Remove only the exact reservation owned by this process before spend."""

    for path, device, inode in (
        (reservation.commit_path, reservation.commit_device, reservation.commit_inode),
        (reservation.result_path, reservation.result_device, reservation.result_inode),
    ):
        metadata = path.lstat()
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_ISLNK(metadata.st_mode)
            or int(metadata.st_dev) != device
            or int(metadata.st_ino) != inode
        ):
            raise RuntimeError("refusing to release a substituted result reservation")
        path.unlink()
    reservation.bundle.rmdir()
    parent_directory = os.open(reservation.bundle.parent, os.O_RDONLY)
    try:
        os.fsync(parent_directory)
    finally:
        os.close(parent_directory)


def expected_armed_receipt(
    *,
    protocol_sha256: str,
    preflight_sha256: str,
    bank_verification: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "komorebi.neuralese.semantic_retraction.armed_receipt.v1",
        "version": VERSION,
        "status": "ARMED_PROSPECTIVE_EVALUATION_UNSPENT",
        "protocol_sha256": protocol_sha256,
        "preflight_sha256": preflight_sha256,
        "synthetic_tests_sha256": sha256_file(SYNTHETIC_TESTS_PATH),
        "design_commit_sha256": sha256_file(HERE / "DESIGN_COMMIT.json"),
        "bank_id": bank_verification["bank_id"],
        "bank_sha256": bank_verification["bank_sha256"],
        "bank_seal_sha256": bank_verification["seal_receipt_sha256"],
        "projector_synthetic_tests_pass": True,
        "factorial_tests_pass": True,
        "fresh_bank_tests_pass": True,
        "lifecycle_tests_pass": True,
        "packed_evidence_recompute_tests_pass": True,
        "evaluation_bank_spent": False,
    }


def verify_execution_armed() -> dict[str, Any]:
    """Verify every pre-spend receipt without opening a checkpoint."""

    verify_runtime_contract()
    require_regular_file(PROTOCOL_PATH, label="frozen protocol")
    require_regular_file(FREEZE_RECEIPT_PATH, label="frozen protocol digest")
    protocol, protocol_sha256 = assert_learned_execution_unlocked()
    preflight_path = require_regular_file(PREFLIGHT_PATH, label="parameter preflight")
    synthetic_path = require_regular_file(
        SYNTHETIC_TESTS_PATH,
        label="synthetic-test receipt",
    )
    preflight_bytes = preflight_path.read_bytes()
    preflight = json.loads(preflight_bytes)
    if canonical_json_bytes(preflight) != preflight_bytes:
        raise RuntimeError("parameter-only preflight receipt is not canonical")
    synthetic_bytes = synthetic_path.read_bytes()
    synthetic_document = json.loads(synthetic_bytes)
    if canonical_json_bytes(synthetic_document) != synthetic_bytes:
        raise RuntimeError("synthetic-test receipt is not canonical")
    if (
        preflight.get("schema")
        != "komorebi.neuralese.semantic_retraction.parameter_preflight.v1"
        or preflight.get("version") != VERSION
        or preflight.get("status") != "PASS"
        or preflight.get("preflight_integrity_pass") is not True
        or preflight.get("projection_diagnostic_is_nonblocking_for_core_factorial")
        is not True
        or preflight.get("evaluation_bank_generated_or_opened") is not False
    ):
        raise RuntimeError("parameter-only preflight is not a passing bank-free receipt")
    preflight_sha256 = sha256_file(PREFLIGHT_PATH)
    if protocol["preflight"]["sha256"] != preflight_sha256:
        raise RuntimeError("preflight digest differs from the frozen protocol")

    from fresh_bank import verify_fresh_bank

    bank_verification = verify_fresh_bank(project_root=HERE.parent)
    bank_bytes = require_regular_file(
        HERE / "FRESH_BANK.json",
        label="sealed fresh bank",
    ).read_bytes()
    if sha256_bytes(bank_bytes) != bank_verification["bank_sha256"]:
        raise RuntimeError("fresh bank changed between verification and byte snapshot")
    bank_document = json.loads(bank_bytes.decode("utf-8"))
    if bank_document.get("bank_id") != bank_verification["bank_id"]:
        raise RuntimeError("fresh-bank snapshot identity mismatch")
    # Exercise the runner-side schema, tensor-shape, and identity-prefix
    # materialization path while the bank is still unspent.  The learned run
    # repeats this deterministically from the immutable byte snapshot.
    load_fresh_bank_arrays(bank_bytes)
    armed_path = require_regular_file(ARMED_RECEIPT_PATH, label="armed receipt")
    armed_hash_path = require_regular_file(
        ARMED_RECEIPT_HASH_PATH,
        label="armed receipt digest",
    )
    armed_bytes = armed_path.read_bytes()
    armed = json.loads(armed_bytes.decode("utf-8"))
    armed_sha256 = sha256_bytes(armed_bytes)
    if canonical_json_bytes(armed) != armed_bytes:
        raise RuntimeError("armed receipt is not canonical JSON")
    receipted_armed_sha256 = armed_hash_path.read_text(
        encoding="utf-8"
    ).strip().split()[0]
    expected = expected_armed_receipt(
        protocol_sha256=protocol_sha256,
        preflight_sha256=preflight_sha256,
        bank_verification=bank_verification,
    )
    if armed != expected:
        raise RuntimeError("armed receipt content mismatch")
    if armed_sha256 != receipted_armed_sha256:
        raise RuntimeError("armed receipt hash mismatch")
    if os.path.lexists(SPEND_PATH):
        raise RuntimeError("fresh bank is already spent; prospective rerun forbidden")
    if os.path.lexists(DEFAULT_BUNDLE):
        raise RuntimeError("result bundle already exists")
    return {
        "protocol": protocol,
        "protocol_sha256": protocol_sha256,
        "preflight_sha256": preflight_sha256,
        "bank_verification": bank_verification,
        "bank_bytes": bank_bytes,
        "runner_bank_materialization_precheck": True,
        "armed_receipt": armed,
        "armed_receipt_sha256": armed_sha256,
    }


def spend_fresh_bank(
    armed: Mapping[str, Any],
    *,
    result_reservation: ResultReservation,
    checkpoint_readiness: Mapping[str, Any],
) -> dict[str, Any]:
    """Spend before any fresh evaluation state is applied to a checkpoint."""

    if result_reservation.hardlink_publication_canary_completed is not True:
        raise RuntimeError("result publication hard-link canary did not complete")

    ensure_output_directory(STATE_DIRECTORY, label="prospective state directory")
    document = {
        "schema": "komorebi.neuralese.semantic_retraction.bank_spend.v1",
        "version": VERSION,
        "status": SPEND_STATUS,
        "bank_id": armed["bank_verification"]["bank_id"],
        "bank_sha256": armed["bank_verification"]["bank_sha256"],
        "protocol_sha256": armed["protocol_sha256"],
        "armed_receipt_sha256": armed["armed_receipt_sha256"],
        "runtime_numpy_version": np.__version__,
        "checkpoint_readiness_sha256": sha256_bytes(
            canonical_json_bytes(checkpoint_readiness)
        ),
        "result_capacity": {
            "bundle": result_reservation.bundle.as_posix(),
            "result_bytes_physically_reserved": MAX_RESULT_BYTES,
            "commit_bytes_physically_reserved": COMMIT_RESERVATION_BYTES,
            "free_bytes_before_reservation": result_reservation.free_bytes_before,
            "posix_fallocate_completed": True,
            "same_directory_hardlink_publication_canary_completed": True,
        },
        "process_id": os.getpid(),
        "unix_time_ns": time.time_ns(),
        "prospective_resume_permitted": False,
    }
    payload = canonical_json_bytes(document)
    exclusive_write(SPEND_PATH, payload)
    return {**document, "receipt_sha256": sha256_bytes(payload)}


def commit_result_bundle(
    result: Mapping[str, Any],
    reservation: ResultReservation,
    *,
    root: Path,
    archive: Path,
) -> dict[str, Any]:
    """Stage, verify, and only then publish the reserved terminal commit."""

    if reservation.bundle != DEFAULT_BUNDLE.absolute():
        raise ValueError("result reservation does not target the frozen bundle")
    result_bytes = canonical_json_bytes(result)
    result_path = _fill_reserved_file(
        reservation.result_path,
        result_bytes,
        maximum_bytes=MAX_RESULT_BYTES,
        expected_device=reservation.result_device,
        expected_inode=reservation.result_inode,
        final_name="RESULT.json",
    )
    precommit_verification = verify_result_bundle(
        reservation.bundle,
        root=root,
        archive=archive,
        require_commit=False,
    )
    commit = {
        "schema": "komorebi.neuralese.semantic_retraction.result_commit.v1",
        "version": VERSION,
        "status": "VERIFIED_RESULT_COMMITTED",
        "bank_id": result["fresh_bank"]["bank_id"],
        "spend_receipt_sha256": result["spend_receipt"]["receipt_sha256"],
        "result_filename": result_path.name,
        "result_bytes": len(result_bytes),
        "result_sha256": sha256_bytes(result_bytes),
        "precommit_verification": precommit_verification,
        "precommit_verification_sha256": sha256_bytes(
            canonical_json_bytes(precommit_verification)
        ),
        "commit_written_last": True,
    }
    commit_bytes = canonical_json_bytes(commit)
    _fill_reserved_file(
        reservation.commit_path,
        commit_bytes,
        maximum_bytes=COMMIT_RESERVATION_BYTES,
        expected_device=reservation.commit_device,
        expected_inode=reservation.commit_inode,
        final_name=RESULT_COMMIT_NAME,
    )
    return {**commit, "commit_sha256": sha256_bytes(commit_bytes)}


def write_abort_receipt(error: BaseException, spend: Mapping[str, Any]) -> None:
    if (DEFAULT_BUNDLE / RESULT_COMMIT_NAME).is_file():
        raise RuntimeError("refusing to write an abort receipt after terminal commit")
    abort_path = STATE_DIRECTORY / "ABORTED_SPENT.json"
    document = {
        "schema": "komorebi.neuralese.semantic_retraction.abort.v1",
        "version": VERSION,
        "status": "ABORTED_SPENT_NO_PROSPECTIVE_RESUME",
        "bank_id": spend["bank_id"],
        "spend_receipt_sha256": spend["receipt_sha256"],
        "error_type": type(error).__name__,
        "error_message": str(error),
        "unix_time_ns": time.time_ns(),
    }
    try:
        exclusive_write(abort_path, canonical_json_bytes(document))
    except FileExistsError:
        pass


def write_spend_publication_failure(
    error: BaseException,
    armed: Mapping[str, Any],
) -> None:
    """Conservatively mark a bank lost if its spend marker may have published."""

    failure_path = STATE_DIRECTORY / "SPEND_PUBLICATION_FAILED.json"
    observed_sha256: str | None = None
    observed_bytes: int | None = None
    try:
        metadata = SPEND_PATH.lstat()
        if stat.S_ISREG(metadata.st_mode) and not stat.S_ISLNK(metadata.st_mode):
            observed_bytes = int(metadata.st_size)
            observed_sha256 = sha256_file(SPEND_PATH)
    except (FileNotFoundError, OSError):
        pass
    document = {
        "schema": "komorebi.neuralese.semantic_retraction.spend_failure.v1",
        "version": VERSION,
        "status": "SPEND_PUBLICATION_UNCERTAIN_NO_PROSPECTIVE_RESUME",
        "bank_id": armed["bank_verification"]["bank_id"],
        "bank_sha256": armed["bank_verification"]["bank_sha256"],
        "spend_path_exists": os.path.lexists(SPEND_PATH),
        "spend_path_observed_bytes": observed_bytes,
        "spend_path_observed_sha256": observed_sha256,
        "result_capacity_reservation_preserved": True,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "unix_time_ns": time.time_ns(),
        "prospective_resume_permitted": False,
    }
    try:
        exclusive_write(failure_path, canonical_json_bytes(document))
    except FileExistsError:
        pass


def handle_spend_publication_error(
    error: BaseException,
    armed: Mapping[str, Any],
    reservation: ResultReservation,
) -> None:
    """Release capacity only when no possibly durable spend marker exists."""

    if os.path.lexists(SPEND_PATH):
        try:
            write_spend_publication_failure(error, armed)
        except BaseException:
            # The marker itself fails closed.  Capacity stays reserved and the
            # original publication error remains the one raised by main.
            pass
    else:
        release_unspent_result_reservation(reservation)


def require_regular_file(path: Path, *, label: str) -> Path:
    require_real_directory(path.parent, label=f"{label} parent")
    try:
        metadata = path.lstat()
    except FileNotFoundError as error:
        raise FileNotFoundError(f"missing {label}: {path}") from error
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError(f"{label} must be a non-symlink regular file: {path}")
    return path.resolve(strict=True)


def validate_fraction_records(value: object, *, path: str = "result") -> int:
    """Recursively validate every stored exact-fraction value."""

    checked = 0
    if isinstance(value, Mapping):
        keys = set(value)
        if value.get("record_kind") == "signed_factorial_interaction":
            numerator = value.get("signed_numerator")
            denominator = value.get("denominator")
            observed = value.get("signed_value")
            if not isinstance(numerator, int) or isinstance(numerator, bool):
                raise ValueError(f"invalid signed interaction numerator at {path}")
            if (
                not isinstance(denominator, int)
                or isinstance(denominator, bool)
                or denominator <= 0
                or abs(numerator) > 2 * denominator
            ):
                raise ValueError(f"invalid signed interaction denominator/range at {path}")
            if observed != numerator / denominator:
                raise ValueError(f"signed interaction value mismatch at {path}")
            checked += 1
        if {"numerator", "denominator", "value"}.issubset(keys):
            numerator = value["numerator"]
            denominator = value["denominator"]
            observed = value["value"]
            if not isinstance(numerator, int) or isinstance(numerator, bool):
                raise ValueError(f"non-integer fraction numerator at {path}")
            if (
                not isinstance(denominator, int)
                or isinstance(denominator, bool)
                or denominator < 0
            ):
                raise ValueError(f"invalid fraction denominator at {path}")
            if numerator < 0 or numerator > denominator:
                raise ValueError(f"fraction numerator is outside [0, denominator] at {path}")
            expected = numerator / denominator if denominator else None
            if observed != expected:
                raise ValueError(f"fraction value mismatch at {path}")
            checked += 1
        for key, child in value.items():
            checked += validate_fraction_records(child, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            checked += validate_fraction_records(child, path=f"{path}[{index}]")
    return checked


def _require_equal_record(
    observed: object,
    expected: object,
    *,
    label: str,
) -> None:
    if observed != expected:
        raise ValueError(f"evidence-derived metric mismatch: {label}")


def verify_condition_evidence(
    condition: Mapping[str, Any],
    suffixes: Sequence[tuple[int, ...]],
    *,
    label: str,
) -> np.ndarray:
    """Recompute every gate-bearing condition rate from packed case evidence."""

    correct = unpack_bool_evidence(condition["correct_evidence"])
    expected_shape = (len(suffixes), EVALUATION_CONTEXTS, N_STATES)
    if correct.shape != expected_shape:
        raise ValueError(f"condition correctness-evidence shape mismatch: {label}")
    _require_equal_record(
        condition.get("correct_tensor"),
        tensor_receipt(correct),
        label=f"{label}/correct_tensor",
    )
    _require_equal_record(
        condition.get("task_accuracy"),
        exact_fraction(correct),
        label=f"{label}/task_accuracy",
    )
    per_length = condition.get("per_length", {})
    for length in range(SUFFIX_MAX_LENGTH + 1):
        key = str(length)
        indices = [index for index, word in enumerate(suffixes) if len(word) == length]
        length_correct = correct[indices]
        record = per_length[key]
        if int(record.get("word_count", -1)) != len(indices):
            raise ValueError(f"condition length word count mismatch: {label}/H{length}")
        _require_equal_record(
            record.get("task_accuracy"),
            exact_fraction(length_correct),
            label=f"{label}/H{length}/task_accuracy",
        )
        _require_equal_record(
            record.get("all_words_task_correct"),
            exact_fraction(np.all(length_correct, axis=0)),
            label=f"{label}/H{length}/all_words_task_correct",
        )
        _require_equal_record(
            record.get("worst_context"),
            worst_context_fraction(length_correct, context_axis=1),
            label=f"{label}/H{length}/worst_context",
        )
    per_suffix = condition.get("per_suffix", [])
    if len(per_suffix) != len(suffixes):
        raise ValueError(f"condition suffix count mismatch: {label}")
    for index, word in enumerate(suffixes):
        record = per_suffix[index]
        if record.get("word") != list(word) or int(record.get("length", -1)) != len(word):
            raise ValueError(f"condition suffix identity mismatch: {label}/{index}")
        _require_equal_record(
            record.get("accuracy"),
            exact_fraction(correct[index]),
            label=f"{label}/suffix-{index}/accuracy",
        )
        _require_equal_record(
            record.get("worst_context"),
            worst_context_fraction(correct[index], context_axis=0),
            label=f"{label}/suffix-{index}/worst_context",
        )
    _require_equal_record(
        condition.get("worst_context"),
        worst_context_fraction(correct, context_axis=1),
        label=f"{label}/worst_context",
    )
    wrong = condition.get("wrong_section_control")
    if wrong is not None:
        counterfactual = unpack_bool_evidence(
            wrong["counterfactual_correct_evidence"]
        )
        if counterfactual.shape != correct.shape:
            raise ValueError(f"counterfactual evidence shape mismatch: {label}")
        _require_equal_record(
            wrong.get("counterfactual_accuracy"),
            exact_fraction(counterfactual),
            label=f"{label}/counterfactual_accuracy",
        )
        _require_equal_record(
            wrong.get("factual_leakage"),
            exact_fraction(correct),
            label=f"{label}/factual_leakage",
        )
        _require_equal_record(
            wrong.get("empty_suffix_counterfactual_accuracy"),
            exact_fraction(counterfactual[0]),
            label=f"{label}/empty_counterfactual",
        )
        _require_equal_record(
            wrong.get("empty_suffix_factual_leakage"),
            exact_fraction(correct[0]),
            label=f"{label}/empty_factual",
        )
        for length in range(SUFFIX_MAX_LENGTH + 1):
            indices = [
                index for index, word in enumerate(suffixes) if len(word) == length
            ]
            length_record = wrong["per_length"][str(length)]
            _require_equal_record(
                length_record.get("counterfactual_accuracy"),
                exact_fraction(counterfactual[indices]),
                label=f"{label}/H{length}/counterfactual_accuracy",
            )
            _require_equal_record(
                length_record.get("factual_leakage"),
                exact_fraction(correct[indices]),
                label=f"{label}/H{length}/factual_leakage",
            )
    return correct


def verify_selector_evidence(
    prefix: Mapping[str, Any],
    condition_masks: Mapping[str, np.ndarray],
    suffixes: Sequence[tuple[int, ...]],
    *,
    label: str,
) -> None:
    selectors = prefix["selector_diagnostics"]
    cut_ray_defined = unpack_bool_evidence(
        selectors["native_cut_hidden_rays_defined_evidence"]
    )
    selected = unpack_bool_evidence(selectors["decoder_correct_evidence"])
    if (
        cut_ray_defined.shape != (EVALUATION_CONTEXTS, N_STATES)
        or selected.shape != (EVALUATION_CONTEXTS, N_STATES)
    ):
        raise ValueError(f"selector evidence shape mismatch: {label}")
    if bool(np.any(selected & ~cut_ray_defined)):
        raise ValueError(f"selector succeeds on an undefined native cut: {label}")
    _require_equal_record(
        selectors.get("native_cut_hidden_rays_defined"),
        exact_fraction(cut_ray_defined),
        label=f"{label}/native_cut_ray_defined",
    )
    _require_equal_record(
        selectors.get("decoder"),
        exact_fraction(selected),
        label=f"{label}/selector_accuracy",
    )
    _require_equal_record(
        selectors.get("decoder_worst_context"),
        worst_context_fraction(selected, context_axis=0),
        label=f"{label}/selector_worst_context",
    )
    idempotence = selectors["decoder_prototype_reset_idempotence"]
    unchanged = unpack_bool_evidence(
        idempotence["selected_label_unchanged_evidence"]
    )
    if unchanged.shape != (EVALUATION_CONTEXTS, N_STATES):
        raise ValueError(f"reset-idempotence evidence shape mismatch: {label}")
    _require_equal_record(
        idempotence.get("selected_label_unchanged"),
        exact_fraction(unchanged),
        label=f"{label}/prototype_reset_label_idempotence",
    )
    decoder = prefix["conditions"]["decoder_prototype"]
    correct = condition_masks["decoder_prototype"]
    expanded = np.broadcast_to(selected[None, :, :], correct.shape)
    conditional = decoder["conditional_on_selector"]
    _require_equal_record(
        conditional.get("selector_accuracy_at_cuts"),
        exact_fraction(selected),
        label=f"{label}/conditional_selector_accuracy",
    )
    selected_count = int(expanded.sum())
    numerator = int((correct & expanded).sum())
    expected_overall = {
        "numerator": numerator,
        "denominator": selected_count,
        "value": numerator / selected_count if selected_count else None,
    }
    _require_equal_record(
        conditional.get("task_accuracy_given_selector_correct"),
        expected_overall,
        label=f"{label}/conditional_accuracy",
    )
    for length in range(SUFFIX_MAX_LENGTH + 1):
        indices = [index for index, word in enumerate(suffixes) if len(word) == length]
        length_correct = correct[indices]
        length_selected = np.broadcast_to(selected[None, :, :], length_correct.shape)
        denominator = int(length_selected.sum())
        numerator = int((length_correct & length_selected).sum())
        expected = {
            "numerator": numerator,
            "denominator": denominator,
            "value": numerator / denominator if denominator else None,
        }
        _require_equal_record(
            conditional["per_length"][str(length)].get(
                "task_accuracy_given_selector_correct"
            ),
            expected,
            label=f"{label}/H{length}/conditional_accuracy",
        )


def verify_section_evidence(section: Mapping[str, Any], *, label: str) -> None:
    consistency = unpack_bool_evidence(section["section_consistency_evidence"])
    if consistency.shape != (N_STATES,):
        raise ValueError(f"section-consistency evidence shape mismatch: {label}")
    _require_equal_record(
        section["section_consistency"].get("self_decoded_section"),
        exact_fraction(consistency),
        label=f"{label}/section_consistency",
    )
    generators = section["one_step_semantic_commutation"]["per_generator"]
    if set(generators) != {"0", "1"}:
        raise ValueError(f"section generator axis mismatch: {label}")
    for generator, record in generators.items():
        ray_defined = unpack_bool_evidence(
            record["stepped_hidden_rays_defined_evidence"]
        )
        commutation = unpack_bool_evidence(
            record["self_decoded_section_evidence"]
        )
        if (
            ray_defined.shape != (EVALUATION_CONTEXTS, N_STATES)
            or commutation.shape != (EVALUATION_CONTEXTS, N_STATES)
        ):
            raise ValueError(
                f"section-commutation evidence shape mismatch: {label}/{generator}"
            )
        if bool(np.any(commutation & ~ray_defined)):
            raise ValueError(
                f"section commutation succeeds on an undefined ray: {label}/{generator}"
            )
        _require_equal_record(
            record.get("stepped_hidden_rays_defined"),
            exact_fraction(ray_defined),
            label=f"{label}/generator-{generator}/stepped_ray_defined",
        )
        _require_equal_record(
            record.get("self_decoded_section"),
            exact_fraction(commutation),
            label=f"{label}/generator-{generator}/commutation",
        )
        _require_equal_record(
            record.get("self_decoded_section_worst_context"),
            worst_context_fraction(commutation, context_axis=0),
            label=f"{label}/generator-{generator}/worst_context",
        )


def verify_result_bundle(
    bundle: Path = DEFAULT_BUNDLE,
    *,
    root: Path,
    archive: Path,
    require_commit: bool = True,
) -> dict[str, Any]:
    """Recompute evidence metrics, gates, labels, and the provenance chain."""

    require_real_directory(bundle, label="result bundle")
    expected_members = (
        {"RESULT.json", RESULT_COMMIT_NAME}
        if require_commit
        else {"RESULT.json", COMMIT_RESERVATION_NAME}
    )
    if {path.name for path in bundle.iterdir()} != expected_members:
        raise ValueError("result bundle contains an unexpected or missing file")
    result_path = bundle / "RESULT.json"
    require_regular_file(result_path, label="result member")
    result_bytes = result_path.read_bytes()
    result = json.loads(result_bytes)
    commit: dict[str, Any] | None = None
    commit_bytes: bytes | None = None
    if require_commit:
        commit_path = require_regular_file(
            bundle / RESULT_COMMIT_NAME,
            label="result commit",
        )
        commit_bytes = commit_path.read_bytes()
        commit = json.loads(commit_bytes)
    else:
        require_regular_file(
            bundle / COMMIT_RESERVATION_NAME,
            label="reserved result commit",
        )
    if canonical_json_bytes(result) != result_bytes:
        raise ValueError("result JSON is not canonical")
    if result.get("schema") != RESULT_SCHEMA or result.get("version") != VERSION:
        raise ValueError("result schema/version mismatch")
    if require_commit:
        assert commit is not None and commit_bytes is not None
        if canonical_json_bytes(commit) != commit_bytes:
            raise ValueError("commit JSON is not canonical")
        if (
            commit.get("schema")
            != "komorebi.neuralese.semantic_retraction.result_commit.v1"
            or commit.get("version") != VERSION
            or commit.get("status") != "VERIFIED_RESULT_COMMITTED"
            or commit.get("commit_written_last") is not True
        ):
            raise ValueError("result commit schema/status mismatch")
        if commit.get("result_filename") != result_path.name:
            raise ValueError("result filename mismatch")
        if int(commit.get("result_bytes", -1)) != len(result_bytes):
            raise ValueError("result byte count mismatch")
        if commit.get("result_sha256") != sha256_bytes(result_bytes):
            raise ValueError("result digest mismatch")
        if commit.get("bank_id") != result["fresh_bank"]["bank_id"]:
            raise ValueError("result/commit bank identity mismatch")
        if (
            commit.get("spend_receipt_sha256")
            != result["spend_receipt"]["receipt_sha256"]
        ):
            raise ValueError("result/commit spend identity mismatch")
    design = result.get("design", {})
    if (
        design.get("arms") != list(ARMS)
        or design.get("seeds") != list(SEEDS)
        or design.get("interventions") != list(INTERVENTIONS)
        or design.get("suffixes") != [list(word) for word in words_upto()]
        or design.get("primary_gate_contract") != PRIMARY_GATE_CONTRACT
        or design.get("work_bound") != expected_work_counts()
        or int(result.get("checkpoint_count", -1)) != len(ARMS) * len(SEEDS)
    ):
        raise ValueError("result frozen design axes mismatch")
    if result.get("claim_boundary") != CLAIM_BOUNDARY_CONTRACT:
        raise ValueError("result claim boundary mismatch")

    protocol_path = require_regular_file(PROTOCOL_PATH, label="frozen protocol")
    protocol_bytes = protocol_path.read_bytes()
    protocol = json.loads(protocol_bytes)
    freeze_path = require_regular_file(
        FREEZE_RECEIPT_PATH,
        label="frozen protocol digest",
    )
    validate_protocol_design(protocol, protocol_bytes=protocol_bytes)
    if freeze_path.read_text(encoding="utf-8").strip().split()[0] != sha256_bytes(
        protocol_bytes
    ):
        raise ValueError("frozen protocol digest file mismatch")
    if result.get("protocol", {}).get("sha256") != sha256_bytes(protocol_bytes):
        raise ValueError("result does not bind the current frozen protocol")
    if (
        result.get("protocol", {}).get("status") != FROZEN_STATUS
        or result.get("protocol", {}).get("implementation_receipts")
        != protocol.get("implementation_receipts")
    ):
        raise ValueError("result protocol metadata mismatch")

    from fresh_bank import verify_fresh_bank

    bank_verification = verify_fresh_bank(project_root=HERE.parent)
    bank_bytes_for_verification = require_regular_file(
        HERE / "FRESH_BANK.json",
        label="sealed fresh bank",
    ).read_bytes()
    (
        calibration_bank_for_verification,
        evaluation_bank_for_verification,
        calibration_words_for_verification,
        evaluation_words_for_verification,
        _,
    ) = load_fresh_bank_arrays(bank_bytes_for_verification)
    if result.get("fresh_bank", {}).get("bank_id") != bank_verification["bank_id"]:
        raise ValueError("result fresh-bank identity mismatch")
    if result.get("fresh_bank", {}).get("bank_sha256") != bank_verification[
        "bank_sha256"
    ]:
        raise ValueError("result fresh-bank digest mismatch")
    if (
        result.get("fresh_bank", {}).get(
            "evaluated_from_pre_spend_immutable_byte_snapshot"
        )
        is not True
    ):
        raise ValueError("result lacks immutable bank-snapshot receipt")
    immutability = result.get("input_immutability", {})
    if (
        immutability.get("fresh_bank_bytes_unchanged") is not True
        or immutability.get("fresh_bank_sha256_before")
        != bank_verification["bank_sha256"]
        or immutability.get("fresh_bank_sha256_after")
        != bank_verification["bank_sha256"]
        or immutability.get("all_checkpoint_hashes_unchanged") is not True
    ):
        raise ValueError("result input-immutability receipt mismatch")
    if (
        design.get("calibration_contexts")
        != int(calibration_bank_for_verification["maps"].shape[0])
        or design.get("evaluation_contexts")
        != int(evaluation_bank_for_verification["maps"].shape[0])
        or design.get("calibration_prefixes")
        != {
            name: list(word)
            for name, word in calibration_words_for_verification.items()
        }
        or design.get("evaluation_prefixes")
        != {
            name: list(word)
            for name, word in evaluation_words_for_verification.items()
        }
    ):
        raise ValueError("result fresh-bank axes differ from the sealed bank")

    spend_path = require_regular_file(SPEND_PATH, label="external spend receipt")
    spend_bytes = spend_path.read_bytes()
    spend_document = json.loads(spend_bytes)
    if canonical_json_bytes(spend_document) != spend_bytes:
        raise ValueError("external spend receipt is not canonical")
    recorded_spend = dict(result.get("spend_receipt", {}))
    recorded_spend_sha256 = recorded_spend.pop("receipt_sha256", None)
    if spend_document != recorded_spend:
        raise ValueError("result spend receipt differs from external receipt")
    if recorded_spend_sha256 != sha256_bytes(spend_bytes):
        raise ValueError("result spend-receipt digest mismatch")
    if (
        spend_document.get("status") != SPEND_STATUS
        or spend_document.get("bank_id") != bank_verification["bank_id"]
        or spend_document.get("bank_sha256") != bank_verification["bank_sha256"]
        or spend_document.get("protocol_sha256") != sha256_bytes(protocol_bytes)
        or spend_document.get("prospective_resume_permitted") is not False
        or spend_document.get("runtime_numpy_version") != EXPECTED_NUMPY_VERSION
    ):
        raise ValueError("external spend receipt provenance mismatch")
    result_capacity = spend_document.get("result_capacity", {})
    if (
        result_capacity.get("bundle") != bundle.absolute().as_posix()
        or int(result_capacity.get("result_bytes_physically_reserved", -1))
        != MAX_RESULT_BYTES
        or int(result_capacity.get("commit_bytes_physically_reserved", -1))
        != COMMIT_RESERVATION_BYTES
        or int(result_capacity.get("free_bytes_before_reservation", -1))
        < MIN_FREE_BYTES_BEFORE_SPEND
        or result_capacity.get("posix_fallocate_completed") is not True
        or result_capacity.get(
            "same_directory_hardlink_publication_canary_completed"
        )
        is not True
    ):
        raise ValueError("external spend receipt lacks the frozen capacity reservation")

    armed_path = require_regular_file(ARMED_RECEIPT_PATH, label="armed receipt")
    armed_hash_path = require_regular_file(
        ARMED_RECEIPT_HASH_PATH,
        label="armed receipt digest",
    )
    armed_bytes = armed_path.read_bytes()
    armed = json.loads(armed_bytes)
    armed_sha256 = sha256_bytes(armed_bytes)
    if canonical_json_bytes(armed) != armed_bytes:
        raise ValueError("armed receipt is not canonical")
    if armed_hash_path.read_text(encoding="utf-8").strip().split()[0] != armed_sha256:
        raise ValueError("armed receipt digest file mismatch")
    preflight_path = require_regular_file(PREFLIGHT_PATH, label="parameter preflight")
    require_regular_file(SYNTHETIC_TESTS_PATH, label="synthetic-test receipt")
    expected_armed = expected_armed_receipt(
        protocol_sha256=sha256_bytes(protocol_bytes),
        preflight_sha256=sha256_file(preflight_path),
        bank_verification=bank_verification,
    )
    if armed != expected_armed:
        raise ValueError("armed receipt content does not recompute")
    if (
        spend_document.get("armed_receipt_sha256") != armed_sha256
        or armed.get("bank_id") != bank_verification["bank_id"]
        or armed.get("bank_sha256") != bank_verification["bank_sha256"]
        or armed.get("protocol_sha256") != sha256_bytes(protocol_bytes)
        or armed.get("status") != "ARMED_PROSPECTIVE_EVALUATION_UNSPENT"
    ):
        raise ValueError("armed/spend provenance mismatch")

    root = require_real_directory(root, label="sealed source root")
    archive = require_regular_file(archive, label="sealed source archive")
    _, source_receipts, source_summary = verify_source_metadata(root, archive)
    if result.get("source_receipts") != source_summary:
        raise ValueError("result source-receipt summary mismatch")

    checkpoints = result.get("checkpoints", [])
    expected_keys = [(arm, seed) for arm in ARMS for seed in SEEDS]
    observed_keys = [(row.get("arm"), int(row.get("seed", -1))) for row in checkpoints]
    if observed_keys != expected_keys:
        raise ValueError("result checkpoint order or identity mismatch")
    readiness = result.get("pre_spend_checkpoint_readiness", {})
    if (
        readiness.get("status")
        != "ALL_CHECKPOINTS_READY_BEFORE_FRESH_BANK_EVALUATION"
        or readiness.get("parameter_only") is not True
        or readiness.get("fresh_bank_state_applied_to_checkpoint") is not False
        or int(readiness.get("checkpoint_count", -1)) != len(expected_keys)
    ):
        raise ValueError("result pre-spend checkpoint-readiness receipt mismatch")
    if spend_document.get("checkpoint_readiness_sha256") != sha256_bytes(
        canonical_json_bytes(readiness)
    ):
        raise ValueError("spend receipt checkpoint-readiness binding mismatch")
    readiness_rows = readiness.get("checkpoints", [])
    if [
        (item.get("arm"), int(item.get("seed", -1))) for item in readiness_rows
    ] != expected_keys:
        raise ValueError("pre-spend checkpoint-readiness census mismatch")
    for row_index, row in enumerate(checkpoints):
        arm = str(row["arm"])
        seed = int(row["seed"])
        receipt = source_receipts[(arm, seed)]
        relative_checkpoint = Path(str(receipt["path"]))
        if relative_checkpoint.is_absolute() or ".." in relative_checkpoint.parts:
            raise ValueError("source seal contains an unsafe checkpoint path")
        checkpoint_path = require_regular_file(
            root / "results" / "packet_closure_pilot" / relative_checkpoint,
            label=f"checkpoint {arm}/{seed}",
        )
        checkpoint_sha256 = sha256_file(checkpoint_path)
        if checkpoint_sha256 != receipt["sha256"]:
            raise ValueError("current checkpoint digest differs from source seal")
        checkpoint_record = row.get("checkpoint", {})
        if (
            checkpoint_record.get("path") != checkpoint_path.as_posix()
            or checkpoint_record.get("observed_sha256") != checkpoint_sha256
            or checkpoint_record.get("expected_sha256") != receipt["sha256"]
            or checkpoint_record.get("state_dict_digest")
            != receipt["state_dict_digest"]
        ):
            raise ValueError("result checkpoint receipt mismatch")
        ready = readiness_rows[row_index]
        if (
            ready.get("path") != checkpoint_path.as_posix()
            or ready.get("sha256") != checkpoint_sha256
            or ready.get("state_dict_digest") != receipt["state_dict_digest"]
            or ready.get("restricted_parameter_load_pass") is not True
        ):
            raise ValueError("pre-spend checkpoint-readiness row mismatch")
        verify_section_evidence(
            row["section_audits"]["prototype"],
            label=f"{arm}/{seed}/prototype-section",
        )
        clean_correct = unpack_bool_evidence(
            row["clean_semantic_endpoint"]["correct_evidence"]
        )
        if clean_correct.shape != (
            len(words_upto()),
            EVALUATION_CONTEXTS,
            N_STATES,
        ):
            raise ValueError("clean correctness-evidence shape mismatch")
        _require_equal_record(
            row["clean_semantic_endpoint"].get("correct_tensor"),
            tensor_receipt(clean_correct),
            label=f"{arm}/{seed}/clean-correct-tensor",
        )
        _require_equal_record(
            row["clean_semantic_endpoint"].get("task_accuracy"),
            exact_fraction(clean_correct),
            label=f"{arm}/{seed}/clean-task-accuracy",
        )
        prefixes = row.get("prefixes", {})
        if list(prefixes) != list(evaluation_words_for_verification):
            raise ValueError("result evaluation-prefix axis mismatch")
        for prefix_name, prefix in prefixes.items():
            if set(prefix.get("conditions", {})) != set(INTERVENTIONS):
                raise ValueError("result intervention axis mismatch")
            integrity = prefix.get("factorial_integrity", {})
            if integrity.get("decoder_label_tensor_reused_for_both_sections") is not True:
                raise ValueError("result decoder-label reuse receipt failed")
            equality = integrity.get("section_equality", {})
            anchor_equality = equality.get("anchor", {})
            if (
                anchor_equality.get("evaluable") is not True
                or anchor_equality.get("bit_identical_on_correct_selection") is not True
            ):
                raise ValueError("result anchor factorial-integrity receipt failed")
            prototype_equality = equality.get("prototype", {})
            if prototype_equality.get("evaluable") is True and (
                prototype_equality.get("bit_identical_on_correct_selection") is not True
            ):
                raise ValueError("result prototype factorial-integrity receipt failed")
            condition_masks: dict[str, np.ndarray] = {}
            for condition_name, condition in prefix["conditions"].items():
                if set(condition.get("per_length", {})) != {
                    str(length) for length in range(SUFFIX_MAX_LENGTH + 1)
                }:
                    raise ValueError("result condition length strata mismatch")
                per_suffix = condition.get("per_suffix", [])
                if [tuple(item.get("word", ())) for item in per_suffix] != list(
                    words_upto()
                ):
                    raise ValueError("result suffix axis mismatch")
                expected_denominator = (
                    len(words_upto()) * EVALUATION_CONTEXTS * N_STATES
                )
                if int(condition["task_accuracy"]["denominator"]) != expected_denominator:
                    raise ValueError("result condition denominator mismatch")
                condition_masks[condition_name] = verify_condition_evidence(
                    condition,
                    words_upto(),
                    label=f"{arm}/{seed}/{prefix_name}/{condition_name}",
                )
            native_correct = condition_masks["native"]
            for condition_name, condition in prefix["conditions"].items():
                correct = condition_masks[condition_name]
                _require_equal_record(
                    condition.get("joint_task_counts_with_native"),
                    paired_task_counts(native_correct, correct),
                    label=f"{arm}/{seed}/{prefix_name}/{condition_name}/native-joint",
                )
                for length in range(SUFFIX_MAX_LENGTH + 1):
                    indices = [
                        index
                        for index, word in enumerate(words_upto())
                        if len(word) == length
                    ]
                    length_record = condition["per_length"][str(length)]
                    _require_equal_record(
                        length_record.get("native_task_accuracy"),
                        exact_fraction(native_correct[indices]),
                        label=(
                            f"{arm}/{seed}/{prefix_name}/{condition_name}/"
                            f"H{length}/native-task-accuracy"
                        ),
                    )
                    _require_equal_record(
                        length_record.get("joint_task_counts_with_native"),
                        paired_task_counts(native_correct[indices], correct[indices]),
                        label=(
                            f"{arm}/{seed}/{prefix_name}/{condition_name}/"
                            f"H{length}/native-joint"
                        ),
                    )
            verify_selector_evidence(
                prefix,
                condition_masks,
                words_upto(),
                label=f"{arm}/{seed}/{prefix_name}",
            )
        recomputed_gate = checkpoint_primary_gate(
            prefixes,
            row["section_audits"]["prototype"],
        )
        if row.get("primary_gate") != recomputed_gate:
            raise ValueError("checkpoint primary gate does not recompute from metrics")

    recomputed_arms: dict[str, bool] = {}
    recomputed_repairs: dict[str, dict[str, object]] = {}
    for arm in ARMS:
        rows = [row for row in checkpoints if row["arm"] == arm]
        recomputed_arms[arm] = all(bool(row["primary_gate"]["pass"]) for row in rows)
        arm_record = result["labels"]["arms"][arm]
        expected_passing_seeds = [
            int(row["seed"]) for row in rows if row["primary_gate"]["pass"]
        ]
        if (
            bool(arm_record["pass"]) != recomputed_arms[arm]
            or arm_record.get("passing_seeds") != expected_passing_seeds
        ):
            raise ValueError("arm label aggregation mismatch")
        all_repair_evaluable = all(
            bool(row["primary_gate"]["repair_superiority"]["evaluable"])
            for row in rows
        )
        repair_status = (
            "PASS"
            if all(
                row["primary_gate"]["repair_superiority"]["status"] == "PASS"
                for row in rows
            )
            else "FAIL"
            if all_repair_evaluable
            else "NOT_EVALUABLE_LOW_NATIVE_ERROR"
        )
        recomputed_repairs[arm] = {
            "status": repair_status,
            "all_checkpoints_evaluable": all_repair_evaluable,
        }
        if arm_record.get("repair_superiority") != recomputed_repairs[arm]:
            raise ValueError("arm repair-superiority aggregation mismatch")
    primary_arm = str(PRIMARY_GATE_CONTRACT["primary_arm"])
    if bool(result["labels"]["primary_arm_pass"]) != recomputed_arms[primary_arm]:
        raise ValueError("primary-arm label mismatch")
    if (
        result["labels"].get("primary_arm_repair_superiority")
        != recomputed_repairs[primary_arm]
    ):
        raise ValueError("primary-arm repair-superiority label mismatch")
    expected_claim_status = (
        "PRIMARY_OPERATIONAL_GATE_PASS"
        if recomputed_arms[primary_arm]
        else "VALID_NEGATIVE_PRIMARY_OPERATIONAL_GATE_FAIL"
    )
    if result.get("claim_status") != expected_claim_status:
        raise ValueError("result claim-status mismatch")
    if bool(result["labels"]["full_fixed_checkpoint_cohort_pass"]) != all(
        recomputed_arms.values()
    ):
        raise ValueError("full-cohort label mismatch")
    fraction_count = validate_fraction_records(result)
    if fraction_count <= 0:
        raise ValueError("result contains no validated exact-fraction records")
    verification = {
        "status": "VERIFIED_STAGED_RESULT",
        "result_sha256": sha256_bytes(result_bytes),
        "bank_id": result["fresh_bank"]["bank_id"],
        "primary_arm_pass": recomputed_arms[primary_arm],
        "primary_arm_repair_superiority": recomputed_repairs[primary_arm],
        "checkpoint_count": len(checkpoints),
        "exact_fraction_records_validated": fraction_count,
        "source_checkpoint_hashes_verified": len(checkpoints),
        "packed_evidence_metrics_recomputed": True,
        "same_frozen_gate_implementation_reused": True,
        "model_forward_recomputed": False,
        "prototype_tensor_recomputed": False,
        "continuous_hidden_residual_recomputed_from_raw": False,
        "independent_learned_replication": False,
    }
    if not require_commit:
        return verification
    assert commit is not None and commit_bytes is not None
    if commit.get("precommit_verification") != verification:
        raise ValueError("terminal commit preverification binding mismatch")
    if commit.get("precommit_verification_sha256") != sha256_bytes(
        canonical_json_bytes(verification)
    ):
        raise ValueError("terminal commit preverification digest mismatch")
    return {
        **verification,
        "status": "VERIFIED_RESULT_COMMIT",
        "commit_sha256": sha256_bytes(commit_bytes),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate frozen design constants without reading learned checkpoints",
    )
    mode.add_argument(
        "--preflight",
        action="store_true",
        help="Run the bounded parameter-only projector audit without a fresh bank",
    )
    mode.add_argument(
        "--status",
        action="store_true",
        help="Report lifecycle files without opening checkpoints",
    )
    mode.add_argument(
        "--verify-result",
        action="store_true",
        help="Verify a terminal result bundle without running learned computation",
    )
    mode.add_argument(
        "--run-learned",
        action="store_true",
        help="Run only when the frozen-protocol receipt unlocks the firewall",
    )
    parser.add_argument("--root", type=Path, help="Extracted v0.4 package root")
    parser.add_argument("--archive", type=Path, help="Original sealed v0.4 ZIP")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.preflight:
        if args.root is None or args.archive is None:
            raise SystemExit("--preflight requires --root and --archive")
        if PREFLIGHT_PATH.exists():
            raise FileExistsError("preflight receipt already exists; overwrite forbidden")
        result = run_parameter_only_preflight(
            require_real_directory(args.root, label="sealed source root"),
            require_regular_file(args.archive, label="sealed source archive"),
        )
        result["runner_sha256"] = sha256_file(Path(__file__).resolve())
        exclusive_write(PREFLIGHT_PATH, canonical_json_bytes(result))
        print(
            json.dumps(
                {
                    "status": result["status"],
                    "checkpoint_count": result["checkpoint_count"],
                    "all_projectors_pass": result["all_projectors_pass"],
                    "output": PREFLIGHT_PATH.as_posix(),
                    "sha256": sha256_file(PREFLIGHT_PATH),
                },
                sort_keys=True,
            )
        )
        return 0 if result["status"] == "PASS" else 1

    if args.status:
        files = {
            "protocol": PROTOCOL_PATH,
            "protocol_receipt": FREEZE_RECEIPT_PATH,
            "preflight": PREFLIGHT_PATH,
            "synthetic_tests": SYNTHETIC_TESTS_PATH,
            "design_commit": HERE / "DESIGN_COMMIT.json",
            "fresh_bank": HERE / "FRESH_BANK.json",
            "fresh_bank_seal": BANK_SEAL_PATH,
            "armed_receipt": ARMED_RECEIPT_PATH,
            "spend_receipt": SPEND_PATH,
            "result_commit": DEFAULT_BUNDLE / "COMMIT.json",
        }
        print(
            json.dumps(
                {
                    "status": "LIFECYCLE_STATUS",
                    "files": {
                        name: {
                            "present": path.is_file(),
                            "sha256": sha256_file(path) if path.is_file() else None,
                        }
                        for name, path in files.items()
                    },
                    "checkpoint_opened": False,
                },
                sort_keys=True,
            )
        )
        return 0

    if args.verify_result:
        if args.root is None or args.archive is None:
            raise SystemExit("--verify-result requires --root and --archive")
        print(
            json.dumps(
                verify_result_bundle(
                    root=require_real_directory(
                        args.root,
                        label="sealed source root",
                    ),
                    archive=require_regular_file(
                        args.archive,
                        label="sealed source archive",
                    ),
                ),
                sort_keys=True,
            )
        )
        return 0

    protocol_bytes = PROTOCOL_PATH.read_bytes()
    protocol = json.loads(protocol_bytes.decode("utf-8"))
    design = validate_protocol_design(protocol, protocol_bytes=protocol_bytes)
    if args.validate_only:
        print(json.dumps({"status": "VALIDATION_PASS", **design}, sort_keys=True))
        return 0

    if args.root is None or args.archive is None:
        raise SystemExit("--run-learned requires --root and --archive")
    root = require_real_directory(args.root, label="sealed source root")
    archive = require_regular_file(args.archive, label="sealed source archive")
    verify_runtime_contract()
    armed = verify_execution_armed()
    seal, source_checkpoint_receipts, pre_spend_source_receipts = (
        verify_source_metadata(root, archive)
    )
    prepared_checkpoints, checkpoint_readiness = prepare_checkpoint_panel(
        root,
        seal,
        source_checkpoint_receipts,
    )
    reservation = reserve_result_bundle()
    try:
        spend = spend_fresh_bank(
            armed,
            result_reservation=reservation,
            checkpoint_readiness=checkpoint_readiness,
        )
    except BaseException as error:
        handle_spend_publication_error(error, armed, reservation)
        raise
    try:
        result = run_learned_panel(
            root,
            archive,
            armed["protocol"],
            armed["protocol_sha256"],
            bank_path=HERE / "FRESH_BANK.json",
            bank_bytes=armed["bank_bytes"],
            bank_verification=armed["bank_verification"],
            spend_receipt=spend,
            pre_spend_source_receipts=pre_spend_source_receipts,
            prepared_checkpoints=prepared_checkpoints,
            pre_spend_checkpoint_readiness=checkpoint_readiness,
        )
        commit = commit_result_bundle(
            result,
            reservation,
            root=root,
            archive=archive,
        )
    except BaseException as error:
        write_abort_receipt(error, spend)
        raise
    print(
        json.dumps(
            {
                "status": "VERIFIED_RESULT_COMMITTED",
                "checkpoint_count": result["checkpoint_count"],
                "primary_arm_pass": result["labels"]["primary_arm_pass"],
                "output": DEFAULT_BUNDLE.as_posix(),
                "commit_sha256": commit["commit_sha256"],
                "precommit_verification": commit["precommit_verification"][
                    "status"
                ],
                "elapsed_seconds": result["runtime"]["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
