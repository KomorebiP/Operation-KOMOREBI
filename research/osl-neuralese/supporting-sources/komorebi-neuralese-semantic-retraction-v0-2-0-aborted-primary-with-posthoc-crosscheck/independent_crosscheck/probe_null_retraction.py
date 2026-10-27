#!/usr/bin/env python3
"""Independent NumPy semantic-retraction sensitivity for sealed v0.4.

The learned panel is deliberately locked until ``PROTOCOL.json`` is frozen
and its exact bytes are receipted.  ``--validate-only`` never opens a learned
checkpoint.  The learned path never imports PyTorch or the source package.
"""

from __future__ import annotations

import argparse
from collections import OrderedDict
from dataclasses import dataclass
import hashlib
import io
import itertools
import json
import math
from pathlib import Path
import pickle
import platform
import time
from typing import Any, Iterable, Mapping, Sequence
import zipfile

import numpy as np


AUTHOR = "Komorebi P."
VERSION = "0.2.0"
RESULT_SCHEMA = "komorebi.neuralese.semantic_retraction_null_sensitivity.v1"
PROTOCOL_SCHEMA = "komorebi.neuralese.semantic_retraction_null_sensitivity_protocol.v1"
FROZEN_STATUS = "FROZEN_POSTHOC_NULL_SENSITIVITY"

ARMS = (
    "euclidean_supervised",
    "euclidean_cr",
    "polar_supervised",
    "polar_cr",
)
SEEDS = (101, 211, 307)
N_STATES = 8
HIDDEN_DIM = 12
NULL_CONTEXTS = 64
NULL_SEED_BASE = 530_000
RELATION_REPEAT = 16
STRESS_BASE_WORDS: dict[str, tuple[int, ...]] = {
    "r4_x16": (0, 0, 0, 0),
    "f2_x16": (1, 1),
    "frfr_x16": (1, 0, 1, 0),
}
SUFFIX_MAX_LENGTH = 4
INTERVENTIONS = (
    "native",
    "oracle_anchor",
    "self_decoded_anchor",
    "nearest_ray_anchor",
    "crossfit_oracle_prototype",
    "wrong_anchor_control",
)
NORMALIZATION_EPS = np.float32(1e-8)
EXPECTED_ARCHIVE_SHA256 = "4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d"
EXPECTED_SEAL_SHA256 = "78f8fad00b8a50edc6286b43edcc0c7433f25d9a5e39fd05c00a0f77d11d73d4"
EXPECTED_EVAL_BANK_SHA256 = "70ef5a5f85f4a5029d06b1c9838dc60fb0f502a37dcc1088582d03b037c3fe26"

HERE = Path(__file__).resolve().parent
PROTOCOL_PATH = HERE / "PROTOCOL.json"
FREEZE_RECEIPT_PATH = HERE / "FROZEN_PROTOCOL.sha256"


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


def derive_seed(base: int, *parts: object) -> int:
    encoded = json.dumps(
        [int(base), *parts],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "little") % (2**31 - 1)


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


def regenerate_null_bank() -> dict[str, np.ndarray]:
    """Reproduce EpisodeGenerator.sample(64, 0, family='d4')."""

    rng = np.random.default_rng(derive_seed(NULL_SEED_BASE, "null"))
    phi = np.argsort(rng.random((NULL_CONTEXTS, N_STATES)), axis=1).astype(np.int64)
    inverse = np.argsort(phi, axis=1)
    canonical = canonical_d4_maps()
    canonical_maps = np.empty((NULL_CONTEXTS, 2, N_STATES), dtype=np.int64)
    for operator in range(2):
        canonical_target = canonical[operator][inverse]
        canonical_maps[:, operator] = np.take_along_axis(phi, canonical_target, axis=1)

    swap = rng.integers(0, 2, size=NULL_CONTEXTS, dtype=np.int64)
    maps = np.empty_like(canonical_maps)
    maps[:, 0] = np.where(swap[:, None].astype(bool), canonical_maps[:, 1], canonical_maps[:, 0])
    maps[:, 1] = np.where(swap[:, None].astype(bool), canonical_maps[:, 0], canonical_maps[:, 1])
    canonical_to_slot = np.stack((swap, 1 - swap), axis=1)
    start = rng.integers(0, N_STATES, size=NULL_CONTEXTS, dtype=np.int64)
    tables = np.eye(N_STATES, dtype=np.float32)[maps]
    return {
        "tables": tables,
        "maps": maps,
        "op_slots": np.empty((NULL_CONTEXTS, 0), dtype=np.int64),
        "canonical_ops": np.empty((NULL_CONTEXTS, 0), dtype=np.int64),
        "start": start,
        "target": start.copy(),
        "intermediates": np.empty((NULL_CONTEXTS, 0), dtype=np.int64),
        "canonical_to_slot": canonical_to_slot,
        "phi": phi,
    }


def tensor_receipt(array: np.ndarray) -> dict[str, object]:
    local = np.ascontiguousarray(array)
    return {
        "shape": list(local.shape),
        "dtype": str(local.dtype),
        "sha256": sha256_bytes(local.tobytes(order="C")),
    }


def verify_null_bank_receipts(
    bank: Mapping[str, np.ndarray],
    evaluation_bank: Mapping[str, Any],
) -> dict[str, object]:
    expected = evaluation_bank["episode_receipts"]["null"]["tensors"]
    if set(expected) != set(bank):
        raise RuntimeError("sealed null-bank tensor field set mismatch")
    fields: dict[str, object] = {}
    for name, array in bank.items():
        observed = tensor_receipt(array)
        match = observed == expected[name]
        fields[name] = {"observed": observed, "expected": expected[name], "match": match}
        if not match:
            raise RuntimeError(f"sealed null-bank receipt mismatch: {name}")
    return {
        "name": "null",
        "role": "sealed_null_bank_sensitivity",
        "seed": derive_seed(NULL_SEED_BASE, "null"),
        "contexts": NULL_CONTEXTS,
        "all_tensor_receipts_match": True,
        "fields": fields,
    }


def words_upto(maximum_length: int = SUFFIX_MAX_LENGTH) -> tuple[tuple[int, ...], ...]:
    return tuple(
        word
        for length in range(maximum_length + 1)
        for word in itertools.product(range(2), repeat=length)
    )


def expanded_stress_words() -> dict[str, tuple[int, ...]]:
    return {
        name: tuple(base_word) * RELATION_REPEAT
        for name, base_word in STRESS_BASE_WORDS.items()
    }


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


def validate_stress_semantics(bank: Mapping[str, np.ndarray]) -> dict[str, object]:
    starts = np.broadcast_to(np.arange(N_STATES, dtype=np.int64), (NULL_CONTEXTS, N_STATES))
    output: dict[str, object] = {}
    for name, word in expanded_stress_words().items():
        endpoint = apply_visible_word(bank["maps"], bank["canonical_to_slot"], starts, word)
        identity = bool(np.array_equal(endpoint, starts))
        output[name] = {"length": len(word), "identity_on_all_context_states": identity}
        if not identity:
            raise RuntimeError(f"stress prefix is not semantically null: {name}")
    return output


def load_protocol(path: Path = PROTOCOL_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("protocol must be a JSON object")
    return value


def expected_work_counts() -> dict[str, int]:
    suffixes = len(words_upto())
    split_states = NULL_CONTEXTS * N_STATES * len(STRESS_BASE_WORDS)
    suffix_endpoints = (
        split_states * suffixes * len(INTERVENTIONS)
        + NULL_CONTEXTS * N_STATES * suffixes
    )
    prefix_matvecs = NULL_CONTEXTS * N_STATES * sum(len(word) for word in expanded_stress_words().values())
    suffix_tree_edges = suffixes - 1
    suffix_matvecs = split_states * len(INTERVENTIONS) * suffix_tree_edges
    clean_matvecs = NULL_CONTEXTS * N_STATES * suffix_tree_edges
    section_audit_matvecs = 2 * NULL_CONTEXTS * N_STATES
    total_matvecs = prefix_matvecs + suffix_matvecs + clean_matvecs + section_audit_matvecs
    return {
        "split_states_per_checkpoint": split_states,
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
    if tuple(protocol["source_panel"]["arms"]) != ARMS:
        raise ValueError("protocol arm order mismatch")
    if tuple(int(value) for value in protocol["source_panel"]["seeds"]) != SEEDS:
        raise ValueError("protocol seed set mismatch")
    if protocol["source_panel"]["archive_sha256"] != EXPECTED_ARCHIVE_SHA256:
        raise ValueError("protocol archive digest mismatch")
    if protocol["source_panel"]["checkpoint_seal_sha256"] != EXPECTED_SEAL_SHA256:
        raise ValueError("protocol checkpoint-seal digest mismatch")
    if protocol["source_panel"]["evaluation_bank_sha256"] != EXPECTED_EVAL_BANK_SHA256:
        raise ValueError("protocol evaluation-bank digest mismatch")
    if int(protocol["sealed_bank"]["contexts"]) != NULL_CONTEXTS:
        raise ValueError("protocol null context count mismatch")
    if int(protocol["stress_prefixes"]["repeat"]) != RELATION_REPEAT:
        raise ValueError("protocol relation repeat mismatch")
    if tuple(protocol["interventions"]) != INTERVENTIONS:
        raise ValueError("protocol intervention order mismatch")
    if int(protocol["continuations"]["maximum_length"]) != SUFFIX_MAX_LENGTH:
        raise ValueError("protocol suffix horizon mismatch")
    if int(protocol["continuations"]["word_count"]) != len(words_upto()):
        raise ValueError("protocol suffix word count mismatch")
    expected_words = {name: list(word) for name, word in STRESS_BASE_WORDS.items()}
    if protocol["stress_prefixes"]["words"] != expected_words:
        raise ValueError("protocol stress relation mismatch")
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
    implementation = protocol.get("implementation_receipts", {})
    implementation_paths = {
        "probe_sha256": Path(__file__).resolve(),
        "test_sha256": (HERE / "test_null_retraction.py").resolve(),
    }
    observed_implementation: dict[str, str] = {}
    for field, path in implementation_paths.items():
        expected = implementation.get(field)
        observed = sha256_file(path)
        if expected != observed:
            raise ValueError(f"protocol implementation digest mismatch: {field}")
        observed_implementation[field] = observed
    unlock = protocol_unlock_state(
        protocol,
        protocol_bytes=protocol_bytes,
        freeze_receipt_path=freeze_receipt_path,
    )
    return {
        "valid": True,
        "status": protocol["status"],
        "suffix_word_count": len(words_upto()),
        "stress_lengths": {name: len(word) for name, word in expanded_stress_words().items()},
        "bounded_work": work,
        "implementation_receipts": observed_implementation,
        "learned_execution_unlocked": unlock["learned_execution_unlocked"],
        "unlock_state": unlock,
    }


def assert_learned_execution_unlocked() -> tuple[dict[str, Any], str]:
    protocol_bytes = PROTOCOL_PATH.read_bytes()
    protocol = json.loads(protocol_bytes.decode("utf-8"))
    design = validate_protocol_design(protocol, protocol_bytes=protocol_bytes)
    unlock = design["unlock_state"]
    if not unlock["status_frozen"]:
        raise RuntimeError("learned execution is locked: protocol status is not frozen")
    if not unlock["receipt_present"]:
        raise RuntimeError("learned execution is locked: FROZEN_PROTOCOL.sha256 is absent")
    if not unlock["receipt_matches"]:
        raise RuntimeError("learned execution is locked: protocol receipt mismatch")
    return protocol, str(unlock["observed_protocol_sha256"])


def validate_output_path(root: Path, archive: Path, output: Path) -> Path:
    """Reject any result target that could overwrite a source or prior result."""

    root_resolved = root.resolve()
    archive_resolved = archive.resolve()
    output_resolved = output.resolve()
    if output_resolved == archive_resolved:
        raise ValueError("output path aliases the sealed source archive")
    if output_resolved == root_resolved or output_resolved.is_relative_to(root_resolved):
        raise ValueError("output path is inside the protected extracted source tree")
    protected = {
        PROTOCOL_PATH.resolve(),
        FREEZE_RECEIPT_PATH.resolve(),
        Path(__file__).resolve(),
        (HERE / "test_null_retraction.py").resolve(),
        (HERE / "README.md").resolve(),
    }
    if output_resolved in protected:
        raise ValueError("output path aliases a cross-check protocol or source file")
    if output_resolved.exists():
        raise FileExistsError("output path already exists; results are never overwritten")
    return output_resolved


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
    squared = np.sum(value * value, axis=-1, dtype=np.float32)
    floor = np.float32(NORMALIZATION_EPS * NORMALIZATION_EPS)
    radius = np.sqrt(np.maximum(squared, floor)).astype(np.float32, copy=False)
    return np.asarray(value / radius[..., None], dtype=np.float32)


def normalized_anchors32(arrays: Mapping[str, np.ndarray]) -> np.ndarray:
    anchors = normalize32(arrays["state_embedding.weight"])
    if not bool(np.isfinite(anchors).all()):
        raise FloatingPointError("checkpoint contains an undefined anchor")
    return anchors


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
    """Select the positive anchor ray by oriented Euclidean cosine."""

    value = np.asarray(hidden, dtype=np.float64)
    section = np.asarray(anchors, dtype=np.float64)
    value_norm = np.linalg.norm(value, axis=-1)
    section_norm = np.linalg.norm(section, axis=-1)
    defined = (
        np.isfinite(value).all(axis=-1)
        & np.isfinite(value_norm)
        & (value_norm > 1e-12)
    )
    section_defined = (
        np.isfinite(section).all(axis=-1)
        & np.isfinite(section_norm)
        & (section_norm > 1e-12)
    )
    if not bool(defined.all()) or not bool(section_defined.all()):
        raise FloatingPointError(f"{label} contains an undefined oriented ray")
    scores = np.matmul(value, section.T)
    scores /= value_norm[..., None] * section_norm[None, ...]
    return finite_argmax(scores, label=label)


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


def stress_split_states32(
    anchors: np.ndarray,
    operators: np.ndarray,
    canonical_to_slot: np.ndarray,
) -> dict[str, np.ndarray]:
    initial = np.broadcast_to(
        anchors[None, :, :],
        (operators.shape[0], N_STATES, HIDDEN_DIM),
    ).copy()
    return {
        name: rollout_word32(initial, operators, canonical_to_slot, word)
        for name, word in expanded_stress_words().items()
    }


def crossfit_prototypes(
    split_states: Mapping[str, np.ndarray],
) -> tuple[np.ndarray, dict[str, object]]:
    """Fit prototypes away from both test context fold and test loop family."""

    names = tuple(STRESS_BASE_WORDS)
    output = np.empty((len(names), 2, N_STATES, HIDDEN_DIM), dtype=np.float32)
    records: list[dict[str, object]] = []
    context_index = np.arange(NULL_CONTEXTS)
    for test_prefix_index, test_prefix in enumerate(names):
        fit_prefixes = [name for name in names if name != test_prefix]
        for test_fold in (0, 1):
            fit_context = context_index[context_index % 2 != test_fold]
            samples = np.concatenate(
                [split_states[name][fit_context] for name in fit_prefixes],
                axis=0,
            )
            if samples.shape != (64, N_STATES, HIDDEN_DIM):
                raise RuntimeError("cross-fit prototype contribution count drifted")
            resultant = samples.astype(np.float64).sum(axis=0)
            lengths = np.linalg.norm(resultant, axis=-1)
            if not bool(np.isfinite(lengths).all()) or bool(np.any(lengths <= 0.0)):
                raise FloatingPointError("undefined cross-fit semantic prototype")
            prototype = resultant / lengths[:, None]
            output[test_prefix_index, test_fold] = np.asarray(prototype, dtype=np.float32)
            records.append(
                {
                    "test_prefix": test_prefix,
                    "test_context_fold": test_fold,
                    "fit_prefixes": fit_prefixes,
                    "fit_context_fold": 1 - test_fold,
                    "contributions_per_state": int(samples.shape[0]),
                    "resultant_length": numeric_summary(lengths),
                    "prototype_tensor": tensor_receipt(output[test_prefix_index, test_fold]),
                }
            )
    return output, {
        "shape": list(output.shape),
        "tensor": tensor_receipt(output),
        "records": records,
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
    prefix_index: int,
    native: np.ndarray,
    anchors: np.ndarray,
    decoder: np.ndarray,
    prototypes: np.ndarray,
    phi: np.ndarray,
) -> tuple[dict[str, np.ndarray], dict[str, object]]:
    contexts = native.shape[0]
    oracle = np.broadcast_to(anchors[None, :, :], native.shape).copy()
    decoded, decoded_finite = finite_argmax(
        decode32(native, decoder),
        label="native self-decoder selector",
    )
    nearest, nearest_defined = nearest_anchor_labels64(
        native,
        anchors,
        label="native nearest-anchor selector",
    )
    folds = np.arange(contexts) % 2
    prototype = np.empty_like(native)
    for context in range(contexts):
        prototype[context] = prototypes[prefix_index, folds[context]]
    wrong = wrong_visible_labels(phi)
    states = {
        "native": native.copy(),
        "oracle_anchor": oracle,
        "self_decoded_anchor": anchors[decoded],
        "nearest_ray_anchor": anchors[nearest],
        "crossfit_oracle_prototype": prototype,
        "wrong_anchor_control": anchors[wrong],
    }
    if tuple(states) != INTERVENTIONS:
        raise RuntimeError("intervention order drifted")
    true = np.broadcast_to(np.arange(N_STATES), decoded.shape)
    return states, {
        "self_decoder_scores_finite": exact_fraction(decoded_finite),
        "nearest_ray_scores_defined": exact_fraction(nearest_defined),
        "self_decoded_anchor": exact_fraction(decoded == true),
        "nearest_ray_anchor": exact_fraction(nearest == true),
        "wrong_anchor_is_distinct": bool(np.all(wrong != true)),
        "self_selected_labels_tensor": tensor_receipt(decoded.astype(np.int64)),
        "nearest_selected_labels_tensor": tensor_receipt(nearest.astype(np.int64)),
        "wrong_labels_tensor": tensor_receipt(wrong.astype(np.int64)),
    }


def autonomous_section_audit(
    anchors: np.ndarray,
    decoder: np.ndarray,
    operators: np.ndarray,
    bank: Mapping[str, np.ndarray],
) -> dict[str, object]:
    """Audit section consistency, idempotence, and generator commutation."""

    labels = np.arange(N_STATES, dtype=np.int64)
    self_on_anchor, self_anchor_finite = finite_argmax(
        decode32(anchors, decoder),
        label="anchor self-decoder section",
    )
    nearest_on_anchor, nearest_anchor_defined = nearest_anchor_labels64(
        anchors,
        anchors,
        label="anchor nearest-ray section",
    )
    self_twice = self_on_anchor[self_on_anchor]
    nearest_twice = nearest_on_anchor[nearest_on_anchor]

    initial = np.broadcast_to(
        anchors[None, :, :],
        (NULL_CONTEXTS, N_STATES, HIDDEN_DIM),
    ).copy()
    true_starts = np.broadcast_to(labels, (NULL_CONTEXTS, N_STATES))
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
        nearest_selected, nearest_defined = nearest_anchor_labels64(
            stepped,
            anchors,
            label=f"generator-{operator} nearest-ray commutation",
        )
        self_ok = self_selected == target
        nearest_ok = nearest_selected == target
        self_commutation.append(self_ok)
        nearest_commutation.append(nearest_ok)
        per_generator[str(operator)] = {
            "self_decoder_scores_finite": exact_fraction(self_finite),
            "nearest_ray_scores_defined": exact_fraction(nearest_defined),
            "self_decoded_anchor": exact_fraction(self_ok),
            "nearest_ray_anchor": exact_fraction(nearest_ok),
        }
    return {
        "tie_break": "lowest_visible_state_index",
        "section_consistency": {
            "self_decoder_scores_finite": exact_fraction(self_anchor_finite),
            "nearest_ray_scores_defined": exact_fraction(nearest_anchor_defined),
            "self_decoded_anchor": exact_fraction(self_on_anchor == labels),
            "nearest_ray_anchor": exact_fraction(nearest_on_anchor == labels),
        },
        "reset_idempotence": {
            "self_decoded_anchor": exact_fraction(self_twice == self_on_anchor),
            "nearest_ray_anchor": exact_fraction(nearest_twice == nearest_on_anchor),
        },
        "one_step_semantic_commutation": {
            "self_decoded_anchor": exact_fraction(np.stack(self_commutation, axis=0)),
            "nearest_ray_anchor": exact_fraction(np.stack(nearest_commutation, axis=0)),
            "per_generator": per_generator,
        },
        "anchor_self_labels": tensor_receipt(self_on_anchor.astype(np.int64)),
        "anchor_nearest_labels": tensor_receipt(nearest_on_anchor.astype(np.int64)),
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
        & (first_norm > 1e-12)
        & (second_norm > 1e-12)
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
        & (norm > 1e-12)
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

    per_suffix: list[dict[str, object]] = []
    for word_index, word in enumerate(suffixes):
        context_accuracy = correct[word_index].mean(axis=1)
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
                "worst_context_accuracy": float(context_accuracy.min()),
                "softmax_total_variation": numeric_summary(tv[word_index]),
                "centered_logit_angle_radians": numeric_summary(logit_angle[word_index]),
                "hidden_angle_radians": numeric_summary(hidden_angle[word_index]),
                "correct_class_margin": numeric_summary(margin[word_index]),
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
        "softmax_total_variation_from_clean": numeric_summary(tv),
        "centered_logit_angle_from_clean_radians": numeric_summary(logit_angle),
        "hidden_angle_from_clean_radians": numeric_summary(hidden_angle),
        "softmax_total_variation_from_native": numeric_summary(native_tv),
        "centered_logit_angle_from_native_radians": numeric_summary(native_logit_angle),
        "hidden_angle_from_native_radians": numeric_summary(native_hidden_angle),
        "correct_class_margin": numeric_summary(margin),
        "h4_per_context_state": {
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
        "worst_context_accuracy": float(correct.transpose(1, 0, 2).reshape(correct.shape[1], -1).mean(axis=1).min()),
        "per_suffix": per_suffix,
        "prediction_tensor": tensor_receipt(prediction.astype(np.int64)),
        "correct_tensor": tensor_receipt(correct.astype(np.bool_)),
    }
    if wrong_targets is not None:
        counterfactual_correct = endpoint_valid & (prediction == wrong_targets)
        output["wrong_anchor_control"] = {
            "counterfactual_accuracy": exact_fraction(counterfactual_correct),
            "factual_leakage": exact_fraction(correct),
            "empty_suffix_counterfactual_accuracy": exact_fraction(counterfactual_correct[0]),
            "empty_suffix_factual_leakage": exact_fraction(correct[0]),
        }
    return output


def build_targets(
    bank: Mapping[str, np.ndarray],
    suffixes: Sequence[tuple[int, ...]],
    starts: np.ndarray | None = None,
) -> np.ndarray:
    if starts is None:
        starts = np.broadcast_to(
            np.arange(N_STATES, dtype=np.int64),
            (NULL_CONTEXTS, N_STATES),
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
        "worst_context_accuracy": float(correct.transpose(1, 0, 2).reshape(correct.shape[1], -1).mean(axis=1).min()),
        "correct_class_margin": numeric_summary(correct_class_margin64(logits, targets)),
        "prediction_tensor": tensor_receipt(prediction.astype(np.int64)),
        "correct_tensor": tensor_receipt(correct.astype(np.bool_)),
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
) -> tuple[dict[str, Any], dict[str, Any], dict[tuple[str, int], dict[str, Any]], dict[str, object]]:
    if sha256_file(archive) != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("v0.4 source archive SHA-256 mismatch")
    result_root = root / "results" / "packet_closure_pilot"
    seal_path = result_root / "CHECKPOINT_SEAL.json"
    bank_path = result_root / "EVAL_BANK.json"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    evaluation_bank = json.loads(bank_path.read_text(encoding="utf-8"))
    if seal.get("schema") != "komorebi.neuralese.packet_closure.checkpoint_seal.v1":
        raise ValueError("checkpoint seal schema mismatch")
    if evaluation_bank.get("schema") != "komorebi.neuralese.packet_closure.evaluation_bank.v1":
        raise ValueError("evaluation bank schema mismatch")
    for item in (seal, evaluation_bank):
        if item.get("version") != "0.4.0" or item.get("profile") != "pilot":
            raise ValueError("v0.4 profile metadata mismatch")
    if seal.get("strict_checkpoint_firewall") is not True:
        raise ValueError("checkpoint seal firewall is not strict")
    if evaluation_bank.get("source_digest") != seal.get("source_digest"):
        raise ValueError("source digest disagreement between seal and bank")
    if evaluation_bank.get("contract_sha256") != seal.get("contract_sha256"):
        raise ValueError("contract digest disagreement between seal and bank")
    seal_sha = sha256_file(seal_path)
    bank_sha = sha256_file(bank_path)
    if seal_sha != EXPECTED_SEAL_SHA256:
        raise ValueError("extracted checkpoint seal does not match the canonical v0.4 receipt")
    if bank_sha != EXPECTED_EVAL_BANK_SHA256:
        raise ValueError("extracted evaluation bank does not match the canonical v0.4 receipt")
    if evaluation_bank.get("checkpoint_seal_sha256") != seal_sha:
        raise ValueError("evaluation bank does not receipt the checkpoint seal")
    receipts = checkpoint_receipts_by_key(seal)
    return seal, evaluation_bank, receipts, {
        "archive": {"path": archive.as_posix(), "sha256": EXPECTED_ARCHIVE_SHA256},
        "checkpoint_seal": {"path": seal_path.as_posix(), "sha256": seal_sha},
        "evaluation_bank": {"path": bank_path.as_posix(), "sha256": bank_sha},
    }


def evaluate_checkpoint(
    arm: str,
    seed: int,
    arrays: Mapping[str, np.ndarray],
    bank: Mapping[str, np.ndarray],
) -> dict[str, object]:
    state_validation = validate_state_dict(arrays)
    operators, operator_receipt = encode_operators32(
        arrays,
        bank["tables"],
        polar=arm.startswith("polar_"),
    )
    anchors = normalized_anchors32(arrays)
    decoder = np.ascontiguousarray(arrays["decoder.weight"], dtype=np.float32)
    split_states = stress_split_states32(anchors, operators, bank["canonical_to_slot"])
    prototypes, prototype_receipt = crossfit_prototypes(split_states)
    section_audit = autonomous_section_audit(
        anchors,
        decoder,
        operators,
        bank,
    )
    suffixes = words_upto()
    targets = build_targets(bank, suffixes)
    wrong = wrong_visible_labels(bank["phi"])
    wrong_targets = build_targets(bank, suffixes, starts=wrong)

    clean_initial = np.broadcast_to(
        anchors[None, :, :],
        (NULL_CONTEXTS, N_STATES, HIDDEN_DIM),
    ).copy()
    clean_hidden, clean_logits = rollout_suffix_tree32(
        clean_initial,
        operators,
        bank["canonical_to_slot"],
        decoder,
        suffixes,
    )

    prefix_results: dict[str, object] = {}
    for prefix_index, prefix_name in enumerate(STRESS_BASE_WORDS):
        native = split_states[prefix_name]
        interventions, selectors = construct_interventions32(
            prefix_index,
            native,
            anchors,
            decoder,
            prototypes,
            bank["phi"],
        )
        native_future_hidden, native_future_logits = rollout_suffix_tree32(
            interventions["native"],
            operators,
            bank["canonical_to_slot"],
            decoder,
            suffixes,
        )
        conditions: dict[str, object] = {}
        for name in INTERVENTIONS:
            if name == "native":
                hidden, logits = native_future_hidden, native_future_logits
            else:
                hidden, logits = rollout_suffix_tree32(
                    interventions[name],
                    operators,
                    bank["canonical_to_slot"],
                    decoder,
                    suffixes,
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
                wrong_targets=wrong_targets if name == "wrong_anchor_control" else None,
            )
        native_split_prediction, native_split_finite = finite_argmax(
            decode32(native, decoder),
            label=f"{prefix_name} native split decoder",
        )
        true = np.broadcast_to(np.arange(N_STATES), native_split_prediction.shape)
        prefix_results[prefix_name] = {
            "expanded_word": list(expanded_stress_words()[prefix_name]),
            "expanded_length": len(expanded_stress_words()[prefix_name]),
            "native_split_decoder_finite": exact_fraction(native_split_finite),
            "native_split_task_accuracy": exact_fraction(
                native_split_finite & (native_split_prediction == true)
            ),
            "native_split_angle_to_clean_anchor_radians": numeric_summary(
                oriented_angles64(native, clean_initial)
            ),
            "native_split_tensor": tensor_receipt(native),
            "selector_diagnostics": selectors,
            "conditions": conditions,
        }

    return {
        "arm": arm,
        "seed": seed,
        "state_dict": state_validation,
        "operator_construction": operator_receipt,
        "anchor_tensor": tensor_receipt(anchors),
        "decoder_tensor": tensor_receipt(decoder),
        "prototype_crossfit": prototype_receipt,
        "autonomous_section_audit": section_audit,
        "clean_semantic_endpoint": clean_reference_summary(clean_hidden, clean_logits, targets),
        "prefixes": prefix_results,
    }


def run_learned_panel(
    root: Path,
    archive: Path,
    protocol: Mapping[str, Any],
    protocol_sha256: str,
) -> dict[str, object]:
    started = time.perf_counter()
    seal, evaluation_bank, receipts, source_receipts = verify_source_metadata(root, archive)
    bank = regenerate_null_bank()
    bank_receipt = verify_null_bank_receipts(bank, evaluation_bank)
    stress_receipt = validate_stress_semantics(bank)

    checkpoint_hashes_before: dict[str, str] = {}
    checkpoint_results: list[dict[str, object]] = []
    receipt_by_key = receipts
    for arm in ARMS:
        for seed in SEEDS:
            receipt = receipt_by_key[(arm, seed)]
            checkpoint_path = root / "results" / "packet_closure_pilot" / receipt["path"]
            observed_sha = sha256_file(checkpoint_path)
            if observed_sha != receipt["sha256"]:
                raise RuntimeError(f"checkpoint SHA-256 mismatch: {checkpoint_path}")
            checkpoint_hashes_before[checkpoint_path.as_posix()] = observed_sha
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
            observed_state_digest = state_dict_digest_numpy(arrays)
            if observed_state_digest != receipt.get("state_dict_digest"):
                raise ValueError(f"checkpoint state-dict digest mismatch: {checkpoint_path}")
            if observed_state_digest != payload.get("provenance", {}).get("final_state_digest"):
                raise ValueError(f"checkpoint provenance state digest mismatch: {checkpoint_path}")
            result = evaluate_checkpoint(arm, seed, arrays, bank)
            result["checkpoint"] = {
                "path": checkpoint_path.as_posix(),
                "expected_sha256": receipt["sha256"],
                "observed_sha256": observed_sha,
                "sha256_match": True,
                "state_dict_digest": observed_state_digest,
                "payload_schema": payload["schema"],
                "payload_version": payload["version"],
                "arm_spec": json_ready(payload.get("arm_spec")),
                "train_config": json_ready(payload.get("train_config")),
            }
            checkpoint_results.append(result)

    for path_text, before in checkpoint_hashes_before.items():
        after = sha256_file(Path(path_text))
        if after != before:
            raise RuntimeError(f"checkpoint changed during read-only analysis: {path_text}")

    return {
        "schema": RESULT_SCHEMA,
        "version": VERSION,
        "author": AUTHOR,
        "analysis_status": "POSTHOC_SEALED_NULL_BANK_SENSITIVITY",
        "claim_status": "independent_read_only_numpy_crosscheck_of_frozen_learned_checkpoints",
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
            "null_contexts": NULL_CONTEXTS,
            "states_per_context": N_STATES,
            "stress_prefixes": {
                name: list(word) for name, word in expanded_stress_words().items()
            },
            "suffixes": [list(word) for word in words_upto()],
            "interventions": list(INTERVENTIONS),
            "work_bound": expected_work_counts(),
        },
        "source_receipts": source_receipts,
        "sealed_null_bank": bank_receipt,
        "stress_semantics": stress_receipt,
        "checkpoint_count": len(checkpoint_results),
        "checkpoints": checkpoint_results,
        "input_immutability": {
            "checkpoint_count": len(checkpoint_hashes_before),
            "all_checkpoint_hashes_unchanged": True,
        },
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
        "--run-learned",
        action="store_true",
        help="Run only when the frozen-protocol receipt unlocks the firewall",
    )
    parser.add_argument("--root", type=Path, help="Extracted v0.4 package root")
    parser.add_argument("--archive", type=Path, help="Original sealed v0.4 ZIP")
    parser.add_argument("--output", type=Path, help="Result JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    protocol_bytes = PROTOCOL_PATH.read_bytes()
    protocol = json.loads(protocol_bytes.decode("utf-8"))
    design = validate_protocol_design(protocol, protocol_bytes=protocol_bytes)
    if args.validate_only:
        print(json.dumps({"status": "VALIDATION_PASS", **design}, sort_keys=True))
        return 0

    if args.root is None or args.archive is None or args.output is None:
        raise SystemExit("--run-learned requires --root, --archive, and --output")
    root = args.root.resolve()
    archive = args.archive.resolve()
    output = validate_output_path(root, archive, args.output)
    protocol, protocol_sha = assert_learned_execution_unlocked()
    result = run_learned_panel(
        root,
        archive,
        protocol,
        protocol_sha,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "status": "PASS",
                "checkpoint_count": result["checkpoint_count"],
                "output": output.as_posix(),
                "elapsed_seconds": result["runtime"]["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
