#!/usr/bin/env python3
"""Read-only NumPy cross-check of all sealed v0.4 learned checkpoints.

The probe never imports PyTorch and never executes checkpoint globals.  It
uses a deliberately restricted unpickler that permits only tensor descriptors
and OrderedDict, then reads the raw tensor storage members from the .pt ZIP.

It evaluates:

* finite-horizon reachable, observable, and reachable-quotient ranks H=0..4;
* local positive-ray tangent observability H=0..4;
* visibility and one-step reachability of the four-dimensional anchor
  complement; and
* direct positive-ray D4 loop angle, log radial gain, and answer accuracy for
  r^4, f^2, and frfr at repeats 1 and 16.

No archive or checkpoint is modified.
"""

from __future__ import annotations

import argparse
from collections import OrderedDict
from dataclasses import dataclass
import hashlib
import io
import json
import math
from pathlib import Path
import pickle
import platform
from typing import Any
import zipfile

import numpy as np


ARMS = (
    "euclidean_supervised",
    "euclidean_cr",
    "polar_supervised",
    "polar_cr",
)
SEEDS = (101, 211, 307)
RELATIONS = {
    "r4": (0, 0, 0, 0),
    "f2": (1, 1),
    "frfr": (1, 0, 1, 0),
}
REPEATS = (1, 16)
HORIZONS = tuple(range(5))
RANK_RTOL = 1e-6
N_STATES = 8
HIDDEN_DIM = 12


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
    """Decode only the inert subset needed for a weights-only state dict."""

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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_checkpoint_restricted(path: Path) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Read a checkpoint without importing torch or allowing arbitrary globals."""

    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        data_names = [name for name in names if name.endswith("/data.pkl")]
        if len(data_names) != 1:
            raise ValueError(f"checkpoint must contain one data.pkl: {path}")
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
            if any(value < 0 for value in descriptor.size):
                raise ValueError(f"negative tensor size for {name}")
            if any(value < 0 for value in descriptor.stride):
                raise ValueError(f"negative tensor stride for {name}")
            dtype = np.dtype(descriptor.storage.dtype)
            storage_name = prefix + "data/" + descriptor.storage.key
            raw = archive.read(storage_name)
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
            array = np.ndarray(
                descriptor.size,
                dtype=dtype,
                buffer=raw,
                offset=descriptor.offset * dtype.itemsize,
                strides=tuple(value * dtype.itemsize for value in descriptor.stride),
            ).copy()
            arrays[name] = array
    return payload, arrays


def json_ready(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    if isinstance(value, np.generic):
        return value.item()
    return value


def derive_seed(base: int, *parts: object) -> int:
    encoded = json.dumps(
        [int(base), *parts],
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return int.from_bytes(hashlib.sha256(encoded).digest()[:8], "little") % (2**31 - 1)


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


def regenerate_zero_length_bank(seed: int, contexts: int) -> dict[str, np.ndarray]:
    """Reproduce EpisodeGenerator.sample(contexts, 0, family='d4')."""

    rng = np.random.default_rng(seed)
    phi = np.argsort(rng.random((contexts, N_STATES)), axis=1).astype(np.int64)
    inverse = np.argsort(phi, axis=1)
    canonical = canonical_d4_maps()
    canonical_maps = np.empty((contexts, 2, N_STATES), dtype=np.int64)
    for operator in range(2):
        canonical_target = canonical[operator][inverse]
        canonical_maps[:, operator] = np.take_along_axis(phi, canonical_target, axis=1)

    swap = rng.integers(0, 2, size=contexts, dtype=np.int64)
    maps = np.empty_like(canonical_maps)
    maps[:, 0] = np.where(
        swap[:, None].astype(bool),
        canonical_maps[:, 1],
        canonical_maps[:, 0],
    )
    maps[:, 1] = np.where(
        swap[:, None].astype(bool),
        canonical_maps[:, 0],
        canonical_maps[:, 1],
    )
    canonical_to_slot = np.stack((swap, 1 - swap), axis=1)
    canonical_ops = rng.integers(0, 2, size=(contexts, 0), dtype=np.int64)
    op_slots = np.empty((contexts, 0), dtype=np.int64)
    start = rng.integers(0, N_STATES, size=contexts, dtype=np.int64)
    target = start.copy()
    intermediates = np.empty((contexts, 0), dtype=np.int64)
    tables = np.eye(N_STATES, dtype=np.float32)[maps]
    return {
        "tables": tables,
        "maps": maps,
        "op_slots": op_slots,
        "canonical_ops": canonical_ops,
        "start": start,
        "target": target,
        "intermediates": intermediates,
        "canonical_to_slot": canonical_to_slot,
        "phi": phi,
    }


def tensor_receipt(array: np.ndarray) -> dict[str, object]:
    local = np.ascontiguousarray(array)
    return {
        "shape": list(local.shape),
        "dtype": str(local.dtype),
        "sha256": hashlib.sha256(local.tobytes(order="C")).hexdigest(),
    }


def bank_receipt_check(
    name: str,
    bank: dict[str, np.ndarray],
    expected: dict[str, Any],
) -> dict[str, object]:
    observed = {field: tensor_receipt(value) for field, value in bank.items()}
    expected_tensors = expected["episode_receipts"][name]["tensors"]
    fields = {
        field: {
            "observed": observed[field],
            "expected": expected_tensors[field],
            "match": observed[field] == expected_tensors[field],
        }
        for field in bank
    }
    return {
        "seed": derive_seed(530_000, name),
        "contexts": int(bank["tables"].shape[0]),
        "all_tensor_receipts_match": all(item["match"] for item in fields.values()),
        "fields": fields,
    }


def numerical_rank(matrix: np.ndarray, relative_tolerance: float = RANK_RTOL) -> int:
    singular = np.linalg.svd(np.asarray(matrix, dtype=np.float64), compute_uv=False)
    if singular.size == 0 or singular[0] == 0.0:
        return 0
    return int(np.sum(singular > singular[0] * relative_tolerance))


def rank_diagnostics(matrix: np.ndarray, relative_tolerance: float = RANK_RTOL) -> dict[str, object]:
    singular = np.linalg.svd(np.asarray(matrix, dtype=np.float64), compute_uv=False)
    if singular.size == 0 or singular[0] == 0.0:
        return {
            "rank": 0,
            "leading_singular_value": 0.0,
            "smallest_retained_relative": None,
            "largest_rejected_relative": None,
        }
    rank = int(np.sum(singular > singular[0] * relative_tolerance))
    return {
        "rank": rank,
        "leading_singular_value": float(singular[0]),
        "smallest_retained_relative": (
            float(singular[rank - 1] / singular[0]) if rank else None
        ),
        "largest_rejected_relative": (
            float(singular[rank] / singular[0]) if rank < singular.size else None
        ),
    }


def rank_distribution(values: list[int]) -> dict[str, object]:
    counts: dict[str, int] = {}
    for value in values:
        counts[str(value)] = counts.get(str(value), 0) + 1
    return {
        "minimum": min(values),
        "maximum": max(values),
        "counts": counts,
    }


def numeric_summary(values: list[float] | np.ndarray) -> dict[str, object]:
    array = np.asarray(values, dtype=np.float64)
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return {
            "count": 0,
            "minimum": None,
            "p10": None,
            "median": None,
            "p90": None,
            "maximum": None,
        }
    return {
        "count": int(finite.size),
        "minimum": float(finite.min()),
        "p10": float(np.quantile(finite, 0.10)),
        "median": float(np.median(finite)),
        "p90": float(np.quantile(finite, 0.90)),
        "maximum": float(finite.max()),
    }


def validate_v04_state_dict(arrays: dict[str, np.ndarray]) -> dict[str, object]:
    expected_shapes = {
        "metric_log_diagonal": (12,),
        "metric_strict_lower": (66,),
        "state_embedding.weight": (8, 12),
        "operator_encoder.weight": (144, 64),
        "decoder.weight": (8, 12),
    }
    observed = {
        name: {
            "shape": list(value.shape),
            "dtype": str(value.dtype),
            "finite": bool(np.isfinite(value).all()),
        }
        for name, value in arrays.items()
    }
    exact_keys = set(arrays) == set(expected_shapes)
    exact_shapes = exact_keys and all(
        arrays[name].shape == shape for name, shape in expected_shapes.items()
    )
    finite = all(bool(np.isfinite(value).all()) for value in arrays.values())
    metric_frozen_identity = bool(
        np.count_nonzero(arrays["metric_log_diagonal"]) == 0
        and np.count_nonzero(arrays["metric_strict_lower"]) == 0
    )
    return {
        "exact_keys": exact_keys,
        "exact_shapes": exact_shapes,
        "all_finite": finite,
        "metric_is_frozen_euclidean": metric_frozen_identity,
        "tensors": observed,
    }


def encode_operators(
    arrays: dict[str, np.ndarray],
    tables: np.ndarray,
    polar: bool,
) -> tuple[np.ndarray, dict[str, object]]:
    """Match the bias-free table encoder and optional hard O(12) retraction."""

    weight = arrays["operator_encoder.weight"]
    raw = (tables.reshape(-1, 64) @ weight.T).reshape(-1, 2, 12, 12)
    raw = np.asarray(raw, dtype=np.float32)
    if not polar:
        return raw.astype(np.float64), {
            "polar_retraction": False,
            "maximum_orthogonality_defect_frobenius": None,
        }

    operators = np.empty_like(raw)
    for index in np.ndindex(raw.shape[:2]):
        left, _, right_transpose = np.linalg.svd(raw[index], full_matrices=False)
        operators[index] = left @ right_transpose
    identity = np.eye(HIDDEN_DIM, dtype=np.float64)
    defects = [
        np.linalg.norm(matrix.astype(np.float64).T @ matrix.astype(np.float64) - identity, ord="fro")
        for matrix in operators.reshape(-1, HIDDEN_DIM, HIDDEN_DIM)
    ]
    return operators.astype(np.float64), {
        "polar_retraction": True,
        "maximum_orthogonality_defect_frobenius": float(max(defects)),
    }


def centered_decoder(arrays: dict[str, np.ndarray]) -> np.ndarray:
    decoder = arrays["decoder.weight"].astype(np.float64)
    centering = np.eye(N_STATES) - np.ones((N_STATES, N_STATES)) / N_STATES
    return centering @ decoder


def normalized_anchors(arrays: dict[str, np.ndarray]) -> np.ndarray:
    anchors = arrays["state_embedding.weight"].astype(np.float64)
    norms = np.linalg.norm(anchors, axis=1, keepdims=True)
    if np.any(norms <= 0.0):
        raise ValueError("checkpoint contains a zero anchor")
    return anchors / norms


def reachable_observable_quotient(
    arrays: dict[str, np.ndarray],
    operators: np.ndarray,
) -> dict[str, object]:
    """Per-context positive-homogeneous finite-horizon quotient ranks."""

    anchors = normalized_anchors(arrays)
    basis = anchors.T
    observation = centered_decoder(arrays)
    per_context: list[dict[str, object]] = []
    aggregate: dict[str, dict[str, object]] = {}

    for context_index, context_operators in enumerate(operators):
        row_blocks: list[np.ndarray] = []
        reachable_blocks: list[np.ndarray] = []
        frontier = [np.eye(HIDDEN_DIM, dtype=np.float64)]
        horizon_records: dict[str, object] = {}
        for horizon in HORIZONS:
            row_blocks.extend(observation @ product for product in frontier)
            reachable_blocks.extend(product @ basis for product in frontier)
            observability = np.concatenate(row_blocks, axis=0)
            reachability = np.concatenate(reachable_blocks, axis=1)
            left, singular, _ = np.linalg.svd(reachability, full_matrices=False)
            reachable_rank = numerical_rank(reachability)
            reachable_basis = left[:, :reachable_rank]
            quotient_map = observability @ reachable_basis
            quotient_rank = numerical_rank(quotient_map)
            horizon_records[str(horizon)] = {
                "reachable": rank_diagnostics(reachability),
                "observable": rank_diagnostics(observability),
                "reachable_quotient": rank_diagnostics(quotient_map),
                "reachable_null_dimension": reachable_rank - quotient_rank,
            }
            frontier = [
                context_operators[operator] @ product
                for product in frontier
                for operator in range(2)
            ]
        per_context.append({"context_index": context_index, "horizons": horizon_records})

    for horizon in HORIZONS:
        records = [item["horizons"][str(horizon)] for item in per_context]
        aggregate[str(horizon)] = {
            "reachable_rank": rank_distribution(
                [int(item["reachable"]["rank"]) for item in records]
            ),
            "observable_rank": rank_distribution(
                [int(item["observable"]["rank"]) for item in records]
            ),
            "reachable_quotient_rank": rank_distribution(
                [int(item["reachable_quotient"]["rank"]) for item in records]
            ),
            "reachable_null_dimension": rank_distribution(
                [int(item["reachable_null_dimension"]) for item in records]
            ),
        }
    return {"aggregate": aggregate, "per_context": per_context}


def projective_tangent_observability(
    arrays: dict[str, np.ndarray],
    operators: np.ndarray,
) -> dict[str, object]:
    """Local differential observability on the eleven-dimensional ray tangent."""

    anchors = normalized_anchors(arrays)
    observation = centered_decoder(arrays)
    per_context: list[dict[str, object]] = []
    aggregate_values = {str(horizon): [] for horizon in HORIZONS}

    for context_index, context_operators in enumerate(operators):
        anchor_records: list[dict[str, object]] = []
        for state, initial in enumerate(anchors):
            _, _, right = np.linalg.svd(initial[None, :], full_matrices=True)
            tangent_basis = right[1:].T
            frontier = [(initial, np.eye(HIDDEN_DIM, dtype=np.float64))]
            rows: list[np.ndarray] = []
            horizons: dict[str, object] = {}
            for horizon in HORIZONS:
                rows.extend(observation @ jacobian for _, jacobian in frontier)
                tangent_observation = np.concatenate(rows, axis=0) @ tangent_basis
                diagnostics = rank_diagnostics(tangent_observation)
                horizons[str(horizon)] = diagnostics
                aggregate_values[str(horizon)].append(int(diagnostics["rank"]))
                next_frontier: list[tuple[np.ndarray, np.ndarray]] = []
                for current, jacobian in frontier:
                    for operator in range(2):
                        proposal = context_operators[operator] @ current
                        radius = np.linalg.norm(proposal)
                        if not np.isfinite(radius) or radius <= 0.0:
                            raise FloatingPointError("undefined projective tangent step")
                        endpoint = proposal / radius
                        local = (
                            (np.eye(HIDDEN_DIM) - np.outer(endpoint, endpoint))
                            @ context_operators[operator]
                            / radius
                        )
                        next_frontier.append((endpoint, local @ jacobian))
                frontier = next_frontier
            anchor_records.append({"state": state, "horizons": horizons})
        per_context.append({"context_index": context_index, "anchors": anchor_records})

    return {
        "tangent_dimension": HIDDEN_DIM - 1,
        "aggregate": {
            horizon: rank_distribution(values)
            for horizon, values in aggregate_values.items()
        },
        "per_context": per_context,
    }


def anchor_complement_diagnostics(
    arrays: dict[str, np.ndarray],
    operators: np.ndarray,
) -> dict[str, object]:
    anchors = normalized_anchors(arrays)
    observation = centered_decoder(arrays)
    _, anchor_singular, right = np.linalg.svd(anchors, full_matrices=True)
    anchor_rank = numerical_rank(anchors)
    retained = right[:anchor_rank].T
    complement = right[anchor_rank:].T
    records: list[dict[str, int]] = []
    for context_index, context_operators in enumerate(operators):
        q_departure = np.concatenate(
            [complement.T @ context_operators[operator] @ retained for operator in range(2)],
            axis=1,
        )
        q_return = np.concatenate(
            [retained.T @ context_operators[operator] @ complement for operator in range(2)],
            axis=1,
        )
        records.append(
            {
                "context_index": context_index,
                "retained_decoder_visibility_rank": numerical_rank(observation @ retained),
                "complement_decoder_visibility_rank": numerical_rank(observation @ complement),
                "one_step_retained_to_complement_rank": numerical_rank(q_departure),
                "one_step_complement_to_retained_rank": numerical_rank(q_return),
            }
        )
    fields = tuple(key for key in records[0] if key != "context_index")
    return {
        "anchor_rank": anchor_rank,
        "anchor_singular_values": [float(value) for value in anchor_singular],
        "retained_dimension": int(retained.shape[1]),
        "complement_dimension": int(complement.shape[1]),
        "aggregate": {
            field: rank_distribution([int(record[field]) for record in records])
            for field in fields
        },
        "per_context": records,
    }


def loop_diagnostics(
    arrays: dict[str, np.ndarray],
    operators: np.ndarray,
    canonical_to_slot: np.ndarray,
) -> dict[str, object]:
    anchors = normalized_anchors(arrays)
    decoder = arrays["decoder.weight"].astype(np.float64)
    baseline_predictions = np.argmax(anchors @ decoder.T, axis=1)
    output: dict[str, object] = {
        "baseline_anchor_accuracy": float(
            np.mean(baseline_predictions == np.arange(N_STATES))
        ),
        "relations": {},
    }

    for relation, base_word in RELATIONS.items():
        relation_output: dict[str, object] = {}
        for repeat in REPEATS:
            log_gains: list[float] = []
            angles: list[float] = []
            correct: list[int] = []
            context_records: list[dict[str, object]] = []
            finite = True
            for context_index, context_operators in enumerate(operators):
                slots = [
                    int(canonical_to_slot[context_index, operator])
                    for operator in base_word
                ] * repeat
                context_log_gains: list[float] = []
                context_angles: list[float] = []
                context_correct: list[int] = []
                for state, initial in enumerate(anchors):
                    hidden = initial.copy()
                    log_gain = 0.0
                    for slot in slots:
                        proposal = context_operators[slot] @ hidden
                        radius = np.linalg.norm(proposal)
                        if not np.isfinite(radius) or radius <= 0.0:
                            finite = False
                            break
                        log_gain += math.log(radius)
                        hidden = proposal / radius
                    if not finite:
                        break
                    cosine = float(np.clip(hidden @ initial, -1.0, 1.0))
                    angle = math.acos(cosine)
                    is_correct = int(np.argmax(decoder @ hidden) == state)
                    context_log_gains.append(log_gain)
                    context_angles.append(angle)
                    context_correct.append(is_correct)
                    log_gains.append(log_gain)
                    angles.append(angle)
                    correct.append(is_correct)
                if not finite:
                    break
                context_records.append(
                    {
                        "context_index": context_index,
                        "log_radial_gain": numeric_summary(context_log_gains),
                        "absolute_log_radial_gain": numeric_summary(
                            np.abs(context_log_gains)
                        ),
                        "positive_ray_angle_radians": numeric_summary(context_angles),
                        "accuracy": float(np.mean(context_correct)),
                        "correct": int(sum(context_correct)),
                        "total": len(context_correct),
                    }
                )
            relation_output[str(repeat)] = {
                "finite": finite,
                "samples": len(log_gains),
                "log_radial_gain": numeric_summary(log_gains),
                "absolute_log_radial_gain": numeric_summary(np.abs(log_gains)),
                "positive_ray_angle_radians": numeric_summary(angles),
                "accuracy": float(np.mean(correct)) if correct else None,
                "correct": int(sum(correct)),
                "total": len(correct),
                "per_context": context_records,
            }
        output["relations"][relation] = relation_output
    return output


def checkpoint_receipts_by_key(seal: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    result: dict[tuple[str, int], dict[str, Any]] = {}
    for receipt in seal["checkpoints"]:
        key = (str(receipt["arm"]), int(receipt["seed"]))
        if key in result:
            raise ValueError(f"duplicate checkpoint receipt: {key}")
        result[key] = receipt
    return result


def run_probe(root: Path) -> dict[str, object]:
    seal_path = root / "results" / "packet_closure_pilot" / "CHECKPOINT_SEAL.json"
    bank_path = root / "results" / "packet_closure_pilot" / "EVAL_BANK.json"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    eval_bank = json.loads(bank_path.read_text(encoding="utf-8"))
    receipts = checkpoint_receipts_by_key(seal)

    feshbach_bank = regenerate_zero_length_bank(
        derive_seed(530_000, "feshbach"),
        contexts=32,
    )
    null_bank = regenerate_zero_length_bank(
        derive_seed(530_000, "null"),
        contexts=64,
    )
    bank_checks = {
        "feshbach": bank_receipt_check("feshbach", feshbach_bank, eval_bank),
        "null": bank_receipt_check("null", null_bank, eval_bank),
    }
    if not all(item["all_tensor_receipts_match"] for item in bank_checks.values()):
        raise RuntimeError("regenerated evaluation bank does not match sealed receipts")

    checkpoint_results: list[dict[str, object]] = []
    for arm in ARMS:
        for seed in SEEDS:
            receipt = receipts[(arm, seed)]
            checkpoint_path = root / "results" / "packet_closure_pilot" / receipt["path"]
            observed_sha = file_sha256(checkpoint_path)
            if observed_sha != receipt["sha256"]:
                raise RuntimeError(f"checkpoint hash mismatch: {checkpoint_path}")
            payload, arrays = load_checkpoint_restricted(checkpoint_path)
            if payload.get("schema") != "komorebi.neuralese.packet_closure.checkpoint.v1":
                raise ValueError(f"checkpoint schema mismatch: {checkpoint_path}")
            if payload.get("version") != "0.4.0":
                raise ValueError(f"checkpoint version mismatch: {checkpoint_path}")
            if payload.get("arm") != arm:
                raise ValueError(f"checkpoint arm mismatch: {checkpoint_path}")
            if int(payload.get("train_config", {}).get("seed", -1)) != seed:
                raise ValueError(f"checkpoint seed mismatch: {checkpoint_path}")
            state_validation = validate_v04_state_dict(arrays)
            if not all(
                state_validation[field]
                for field in (
                    "exact_keys",
                    "exact_shapes",
                    "all_finite",
                    "metric_is_frozen_euclidean",
                )
            ):
                raise ValueError(f"checkpoint state validation failed: {checkpoint_path}")

            polar = arm.startswith("polar_")
            feshbach_operators, feshbach_operator_receipt = encode_operators(
                arrays,
                feshbach_bank["tables"],
                polar=polar,
            )
            null_operators, null_operator_receipt = encode_operators(
                arrays,
                null_bank["tables"],
                polar=polar,
            )
            checkpoint_results.append(
                {
                    "arm": arm,
                    "seed": seed,
                    "checkpoint": {
                        "path": checkpoint_path.as_posix(),
                        "expected_sha256": receipt["sha256"],
                        "observed_sha256": observed_sha,
                        "sha256_match": True,
                        "schema": payload["schema"],
                        "version": payload["version"],
                        "arm_spec": json_ready(payload["arm_spec"]),
                        "train_config": json_ready(payload["train_config"]),
                        "state_dict": state_validation,
                    },
                    "operator_construction": {
                        "feshbach_bank": feshbach_operator_receipt,
                        "null_bank": null_operator_receipt,
                    },
                    "finite_horizon_linear_quotient": reachable_observable_quotient(
                        arrays,
                        feshbach_operators,
                    ),
                    "finite_horizon_projective_tangent": projective_tangent_observability(
                        arrays,
                        feshbach_operators,
                    ),
                    "anchor_complement": anchor_complement_diagnostics(
                        arrays,
                        feshbach_operators,
                    ),
                    "positive_ray_d4_loops": loop_diagnostics(
                        arrays,
                        null_operators,
                        null_bank["canonical_to_slot"],
                    ),
                }
            )

    return {
        "schema": "komorebi.neuralese.v04_crosscheck.result.v1",
        "author": "Komorebi P.",
        "claim_status": "read_only_independent_numpy_crosscheck_of_frozen_learned_checkpoints",
        "archive_root": root.as_posix(),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "torch_imported": False,
        },
        "method": {
            "rank_relative_tolerance": RANK_RTOL,
            "horizons": list(HORIZONS),
            "relations": {name: list(word) for name, word in RELATIONS.items()},
            "repeats": list(REPEATS),
            "feshbach_contexts": 32,
            "null_contexts": 64,
            "states_per_context": 8,
            "centered_decoder": True,
            "positive_rays_are_oriented": True,
            "operator_encoder_arithmetic": "float32",
            "diagnostic_arithmetic": "float64",
            "checkpoint_reader": "restricted_inert_tensor_descriptor_unpickler",
        },
        "source_receipts": {
            "checkpoint_seal": {
                "path": seal_path.as_posix(),
                "sha256": file_sha256(seal_path),
            },
            "eval_bank": {
                "path": bank_path.as_posix(),
                "sha256": file_sha256(bank_path),
            },
        },
        "bank_checks": bank_checks,
        "checkpoint_count": len(checkpoint_results),
        "checkpoints": checkpoint_results,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Path to Komorebi_Neuralese_Packet_Closure_v0.4.0",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path for the full JSON result",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = run_probe(args.root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "output": args.output.resolve().as_posix(),
                "checkpoint_count": result["checkpoint_count"],
                "bank_checks_pass": all(
                    item["all_tensor_receipts_match"]
                    for item in result["bank_checks"].values()
                ),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
