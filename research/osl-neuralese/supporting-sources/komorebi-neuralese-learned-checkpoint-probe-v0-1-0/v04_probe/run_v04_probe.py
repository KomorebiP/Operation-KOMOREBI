#!/usr/bin/env python3
"""Posthoc causal-completion and typed-loop audit for sealed v0.4 checkpoints.

This script is deliberately external to the source archive.  It verifies every
official checkpoint receipt, uses ``torch.load(..., weights_only=True)``, and
strictly reconstructs the frozen model before computing any new statistic.
The calculations are a posthoc mechanism audit and do not repair original
confirmatory gates.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import asdict, dataclass
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys
import time
from typing import Any, Iterable, Sequence

import numpy as np
import torch


AUTHOR = "Komorebi P."
VERSION = "0.1.0"
ANALYSIS_STATUS = "POSTHOC_MECHANISM_AUDIT"
CONTEXT_SEED = 2026090301
CONTEXT_COUNT = 32
HORIZONS = (0, 1, 2, 3, 4)
RANK_TOLERANCES = (1e-2, 1e-3, 1e-4, 1e-6)
PRIMARY_RANK_TOLERANCE = 1e-6
NULL_PERTURBATION_SIZE = 0.10
RELATION_REPEATS = (1, 16)
RELATION_NAMES = ("r4", "f2", "frfr")
RELATIONS: dict[str, tuple[int, ...]] = {
    "r4": (0, 0, 0, 0),
    "f2": (1, 1),
    "frfr": (1, 0, 1, 0),
}
EXPECTED_ARCHIVE_SHA256 = "4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d"

HERE = Path(__file__).resolve().parent
WORK_ROOT = HERE.parents[1]
DEFAULT_ARCHIVE = WORK_ROOT / "learned_archive_retry" / "Komorebi_Neuralese_Packet_Closure_v0.4.0.zip"
DEFAULT_PACKAGE = (
    WORK_ROOT
    / "learned_archive_retry"
    / "extracted_v04"
    / "Komorebi_Neuralese_Packet_Closure_v0.4.0"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def import_package(package: Path) -> dict[str, Any]:
    source = package / "src"
    if not source.is_dir():
        raise FileNotFoundError(f"missing package source directory: {source}")
    source_text = str(source)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)
    from komorebi_neuralese.algebra import canonical_maps
    from komorebi_neuralese.data import EpisodeGenerator
    from komorebi_neuralese.packet_models import (
        PolarIsometricTableOperatorRNN,
        ProjectiveLinearTableOperatorRNN,
    )
    from komorebi_neuralese.packet_closure_train import (
        get_packet_closure_arm,
        state_dict_digest,
    )

    return {
        "canonical_maps": canonical_maps,
        "EpisodeGenerator": EpisodeGenerator,
        "PolarIsometricTableOperatorRNN": PolarIsometricTableOperatorRNN,
        "ProjectiveLinearTableOperatorRNN": ProjectiveLinearTableOperatorRNN,
        "get_packet_closure_arm": get_packet_closure_arm,
        "state_dict_digest": state_dict_digest,
    }


def relative_rank(matrix: np.ndarray, tolerance: float) -> tuple[int, np.ndarray]:
    singular = np.linalg.svd(matrix, compute_uv=False)
    if singular.size == 0 or singular[0] == 0.0:
        return 0, singular
    return int(np.count_nonzero(singular > tolerance * singular[0])), singular


def column_basis(matrix: np.ndarray, tolerance: float) -> tuple[np.ndarray, np.ndarray]:
    left, singular, _ = np.linalg.svd(matrix, full_matrices=False)
    if singular.size == 0 or singular[0] == 0.0:
        return left[:, :0], singular
    rank = int(np.count_nonzero(singular > tolerance * singular[0]))
    return left[:, :rank], singular


def null_basis_within(
    observation: np.ndarray,
    reachable_basis: np.ndarray,
    tolerance: float,
) -> tuple[np.ndarray, int, np.ndarray]:
    restricted = observation @ reachable_basis
    _, singular, right_t = np.linalg.svd(restricted, full_matrices=True)
    if singular.size == 0 or singular[0] == 0.0:
        rank = 0
    else:
        rank = int(np.count_nonzero(singular > tolerance * singular[0]))
    coordinates = right_t[rank:].T
    return reachable_basis @ coordinates, rank, singular


def scaled_block(block: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(block, ord="fro"))
    if norm == 0.0:
        return block.copy()
    return block / norm


def words_upto(horizon: int, alphabet: int = 2) -> tuple[tuple[int, ...], ...]:
    words: list[tuple[int, ...]] = [()]
    for length in range(1, horizon + 1):
        words.extend(itertools.product(range(alphabet), repeat=length))
    return tuple(words)


def matrix_word(operators: np.ndarray, word: Sequence[int]) -> np.ndarray:
    product = np.eye(operators.shape[-1], dtype=operators.dtype)
    for action in word:
        product = operators[int(action)] @ product
    return product


def oriented_angle(first: np.ndarray, second: np.ndarray, metric: np.ndarray | None = None) -> float:
    if metric is None:
        inner = float(first @ second)
        n_first = float(np.linalg.norm(first))
        n_second = float(np.linalg.norm(second))
    else:
        inner = float(first @ metric @ second)
        n_first = math.sqrt(max(float(first @ metric @ first), 0.0))
        n_second = math.sqrt(max(float(second @ metric @ second), 0.0))
    if n_first == 0.0 or n_second == 0.0:
        return float("nan")
    cosine = float(np.clip(inner / (n_first * n_second), -1.0, 1.0))
    return float(math.acos(cosine))


def normalized(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if not np.isfinite(norm) or norm == 0.0:
        raise FloatingPointError("cannot normalize a zero or nonfinite vector")
    return vector / norm


def numeric_summary(values: Iterable[float]) -> dict[str, float | int | None]:
    array = np.asarray(tuple(values), dtype=np.float64).reshape(-1)
    finite = array[np.isfinite(array)]
    if finite.size == 0:
        return {
            "count": int(array.size),
            "finite_count": 0,
            "minimum": None,
            "p05": None,
            "median": None,
            "mean": None,
            "p95": None,
            "maximum": None,
        }
    return {
        "count": int(array.size),
        "finite_count": int(finite.size),
        "minimum": float(np.min(finite)),
        "p05": float(np.quantile(finite, 0.05)),
        "median": float(np.median(finite)),
        "mean": float(np.mean(finite)),
        "p95": float(np.quantile(finite, 0.95)),
        "maximum": float(np.max(finite)),
    }


def make_context_bank(api: dict[str, Any]) -> dict[str, Any]:
    generator = api["EpisodeGenerator"](CONTEXT_SEED)
    # A visible D4 table has a nontrivial relabeling stabilizer, so distinct
    # sampled ``phi`` values can expose the same coordinate context. Draw in a
    # fixed stream and retain the first 32 unique visible two-table tensors.
    retained: list[Any] = []
    keys: set[bytes] = set()
    draws = 0
    while len(retained) < CONTEXT_COUNT and draws < 10000:
        batch = generator.sample(1, 0, family="d4")
        key = batch.tables[0].detach().cpu().numpy().tobytes()
        draws += 1
        if key in keys:
            continue
        keys.add(key)
        retained.append(batch)
    if len(retained) != CONTEXT_COUNT:
        raise RuntimeError("could not construct 32 unique deterministic D4 contexts")
    tables = np.concatenate(
        [batch.tables.detach().cpu().numpy() for batch in retained], axis=0
    ).astype(np.float64)
    maps = np.concatenate(
        [batch.maps.detach().cpu().numpy() for batch in retained], axis=0
    ).astype(np.int64)
    phi = np.concatenate(
        [batch.phi.detach().cpu().numpy() for batch in retained], axis=0
    ).astype(np.int64)
    canonical_to_slot = np.concatenate(
        [batch.canonical_to_slot.detach().cpu().numpy() for batch in retained], axis=0
    ).astype(np.int64)
    payload = {
        "seed": CONTEXT_SEED,
        "count": CONTEXT_COUNT,
        "family": "d4",
        "draws_required": draws,
        "phi": phi.tolist(),
        "canonical_to_slot": canonical_to_slot.tolist(),
        "maps": maps.tolist(),
    }
    return {
        "tables": tables,
        "maps": maps,
        "phi": phi,
        "canonical_to_slot": canonical_to_slot,
        "receipt": {**payload, "sha256": canonical_json_digest(payload), "unique": True},
    }


def verify_and_load_checkpoints(package: Path, api: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    result_dir = package / "results" / "packet_closure_pilot"
    seal_path = result_dir / "CHECKPOINT_SEAL.json"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    receipts = seal.get("checkpoints", [])
    expected_cells = {
        (arm, seed)
        for arm in ("euclidean_supervised", "euclidean_cr", "polar_supervised", "polar_cr")
        for seed in (101, 211, 307)
    }
    actual_cells = {(str(row["arm"]), int(row["seed"])) for row in receipts}
    if len(receipts) != 12 or actual_cells != expected_cells:
        raise RuntimeError("checkpoint seal is not the complete official 4 x 3 census")

    loaded: list[dict[str, Any]] = []
    for receipt in receipts:
        checkpoint = result_dir / receipt["path"]
        actual_sha = sha256_file(checkpoint)
        if actual_sha != receipt["sha256"]:
            raise RuntimeError(f"checkpoint SHA-256 mismatch: {checkpoint.name}")
        # Security and provenance requirement: do not relax weights_only.
        payload = torch.load(checkpoint, map_location="cpu", weights_only=True)
        arm = str(receipt["arm"])
        seed = int(receipt["seed"])
        if payload.get("arm") != arm or int(payload["train_config"]["seed"]) != seed:
            raise RuntimeError(f"checkpoint metadata mismatch: {checkpoint.name}")
        if payload.get("schema") != "komorebi.neuralese.packet_closure.checkpoint.v1":
            raise RuntimeError(f"checkpoint schema mismatch: {checkpoint.name}")
        if payload.get("version") != "0.4.0":
            raise RuntimeError(f"checkpoint version mismatch: {checkpoint.name}")
        if payload.get("source_digest") != seal.get("source_digest"):
            raise RuntimeError(f"checkpoint source digest mismatch: {checkpoint.name}")
        if payload.get("contract_sha256") != seal.get("contract_sha256"):
            raise RuntimeError(f"checkpoint contract digest mismatch: {checkpoint.name}")
        if payload.get("arm_spec") != asdict(api["get_packet_closure_arm"](arm)):
            raise RuntimeError(f"checkpoint arm specification mismatch: {checkpoint.name}")
        hidden_dim = int(payload["train_config"]["hidden_dim"])
        family = str(payload["arm_spec"]["model_family"])
        if family == "raw":
            model = api["ProjectiveLinearTableOperatorRNN"](hidden_dim=hidden_dim)
        elif family == "polar":
            model = api["PolarIsometricTableOperatorRNN"](hidden_dim=hidden_dim)
        else:
            raise RuntimeError(f"unknown frozen model family: {family}")
        incompatibility = model.load_state_dict(payload["state_dict"], strict=True)
        if incompatibility.missing_keys or incompatibility.unexpected_keys:
            raise RuntimeError(f"non-strict state load for {checkpoint.name}")
        model = model.to(device="cpu").eval()
        actual_state_digest = api["state_dict_digest"](model)
        if actual_state_digest != payload["provenance"]["final_state_digest"]:
            raise RuntimeError(f"checkpoint final-state digest mismatch: {checkpoint.name}")
        if actual_state_digest != receipt["state_dict_digest"]:
            raise RuntimeError(f"checkpoint seal state digest mismatch: {checkpoint.name}")
        loaded.append(
            {
                "arm": arm,
                "seed": seed,
                "path": str(checkpoint),
                "sha256": actual_sha,
                "model_family": family,
                "model": model,
                "strict_state_load": True,
                "weights_only_load": True,
                "state_dict_digest_verified": True,
            }
        )
    return loaded, seal


@dataclass(frozen=True)
class ExtractedModel:
    operators: np.ndarray
    anchors: np.ndarray
    decoder: np.ndarray
    centered_decoder: np.ndarray
    metric: np.ndarray
    whitening: np.ndarray
    inverse_whitening: np.ndarray


def extract_model(model: torch.nn.Module, context_tables: np.ndarray) -> ExtractedModel:
    # Preserve the checkpoint's actual float32 path, including hard-polar SVD.
    # Promotion happens only after recurrence matrices and anchors are formed.
    with torch.inference_mode():
        tables = torch.from_numpy(context_tables).to(dtype=torch.float32)
        bundle = model.encode_operator_bundle(tables)
        operators = bundle.matrices.detach().cpu().numpy().astype(np.float64)
        anchors_rows = model.state_anchors().detach().cpu().numpy().astype(np.float64)
        decoder = model.decoder.weight.detach().cpu().numpy().astype(np.float64)
        metric = model.invariant_metric().detach().cpu().numpy().astype(np.float64)
    centering = np.eye(8) - np.ones((8, 8), dtype=np.float64) / 8.0
    centered_decoder = centering @ decoder
    lower = np.linalg.cholesky(metric)
    whitening = lower.T
    inverse_whitening = np.linalg.inv(whitening)
    operators_white = np.einsum(
        "ij,cojk,kl->coil", whitening, operators, inverse_whitening, optimize=True
    )
    anchors_white = whitening @ anchors_rows.T
    decoder_white = decoder @ inverse_whitening
    centered_white = centered_decoder @ inverse_whitening
    return ExtractedModel(
        operators=operators_white,
        anchors=anchors_white,
        decoder=decoder_white,
        centered_decoder=centered_white,
        metric=np.eye(metric.shape[0], dtype=np.float64),
        whitening=whitening,
        inverse_whitening=inverse_whitening,
    )


def rank_ladder_for_context(
    operators: np.ndarray,
    anchors: np.ndarray,
    centered_decoder: np.ndarray,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    records: list[dict[str, Any]] = []
    instantaneous_null: np.ndarray | None = None
    for horizon in HORIZONS:
        products = [matrix_word(operators, word) for word in words_upto(horizon)]
        reachable_stack = np.concatenate(
            [scaled_block(product @ anchors) for product in products], axis=1
        )
        observable_stack = np.concatenate(
            [scaled_block(centered_decoder @ product) for product in products], axis=0
        )
        tolerance_records: dict[str, Any] = {}
        for tolerance in RANK_TOLERANCES:
            reachable_basis, r_singular = column_basis(reachable_stack, tolerance)
            observable_rank, o_singular = relative_rank(observable_stack, tolerance)
            null_basis, behavioral_rank, b_singular = null_basis_within(
                observable_stack, reachable_basis, tolerance
            )
            tolerance_records[f"{tolerance:.0e}"] = {
                "reachable_rank": int(reachable_basis.shape[1]),
                "observable_rank": observable_rank,
                "behavioral_rank": behavioral_rank,
                "null_dimension": int(null_basis.shape[1]),
                "reachable_relative_singular_values": (
                    (r_singular / r_singular[0]).tolist() if r_singular.size and r_singular[0] else []
                ),
                "observable_relative_singular_values": (
                    (o_singular / o_singular[0]).tolist() if o_singular.size and o_singular[0] else []
                ),
                "behavioral_relative_singular_values": (
                    (b_singular / b_singular[0]).tolist() if b_singular.size and b_singular[0] else []
                ),
            }

        reachable_basis, _ = column_basis(reachable_stack, PRIMARY_RANK_TOLERANCE)
        null_basis, behavioral_rank, _ = null_basis_within(
            observable_stack, reachable_basis, PRIMARY_RANK_TOLERANCE
        )
        if horizon == 0:
            instantaneous_null = null_basis
        leakage: list[float] = []
        if null_basis.shape[1]:
            null_projector = null_basis @ null_basis.T
            for generator in operators:
                image = generator @ null_basis
                denominator = float(np.linalg.norm(image, ord="fro"))
                numerator = float(np.linalg.norm((np.eye(generator.shape[0]) - null_projector) @ image, ord="fro"))
                leakage.append(numerator / denominator if denominator else float("nan"))
        records.append(
            {
                "horizon": horizon,
                "primary_tolerance": PRIMARY_RANK_TOLERANCE,
                "reachable_rank": int(reachable_basis.shape[1]),
                "behavioral_rank": behavioral_rank,
                "null_dimension": int(null_basis.shape[1]),
                "generator_leakage": leakage,
                "maximum_generator_leakage": max(leakage) if leakage else None,
                "tolerance_sensitivity": tolerance_records,
            }
        )
    assert instantaneous_null is not None
    perturbation = instantaneous_null_perturbation(
        operators,
        anchors,
        centered_decoder,
        instantaneous_null,
    )
    return records, perturbation


def instantaneous_null_perturbation(
    operators: np.ndarray,
    anchors: np.ndarray,
    centered_decoder: np.ndarray,
    null_basis: np.ndarray,
) -> dict[str, Any]:
    current_angles: list[float] = []
    next_angles: list[float] = []
    cases: list[dict[str, Any]] = []
    for null_index in range(null_basis.shape[1]):
        direction = null_basis[:, null_index]
        for state in range(anchors.shape[1]):
            baseline = normalized(anchors[:, state])
            for sign in (-1.0, 1.0):
                perturbed = normalized(baseline + sign * NULL_PERTURBATION_SIZE * direction)
                current = oriented_angle(centered_decoder @ baseline, centered_decoder @ perturbed)
                for action, generator in enumerate(operators):
                    next_base = generator @ baseline
                    next_perturbed = generator @ perturbed
                    future = oriented_angle(
                        centered_decoder @ next_base,
                        centered_decoder @ next_perturbed,
                    )
                    current_angles.append(current)
                    next_angles.append(future)
                    cases.append(
                        {
                            "null_index": null_index,
                            "state": state,
                            "sign": int(sign),
                            "action": action,
                            "current_centered_logit_angle": current,
                            "one_step_centered_logit_angle": future,
                        }
                    )
    return {
        "perturbation_size_in_whitened_coordinates": NULL_PERTURBATION_SIZE,
        "instantaneous_null_dimension": int(null_basis.shape[1]),
        "case_count": len(cases),
        "current_angle": numeric_summary(current_angles),
        "one_step_angle": numeric_summary(next_angles),
        "maximum_reveal_angle": max(next_angles) if next_angles else None,
        "reveal_fraction_above_1e-4": (
            float(np.mean(np.asarray(next_angles) > 1e-4)) if next_angles else None
        ),
        "cases": cases,
    }


def apply_state_word(canonical_maps: np.ndarray, state: int, word: Sequence[int]) -> int:
    current = int(state)
    for action in word:
        current = int(canonical_maps[int(action), current])
    return current


def shortest_d4_words(canonical_maps: np.ndarray) -> tuple[tuple[int, ...], ...]:
    words: list[tuple[int, ...] | None] = [None] * 8
    words[0] = ()
    queue: deque[int] = deque([0])
    while queue:
        state = queue.popleft()
        word = words[state]
        assert word is not None
        for action in (0, 1):
            target = int(canonical_maps[action, state])
            if words[target] is None:
                words[target] = word + (action,)
                queue.append(target)
    if any(word is None for word in words):
        raise RuntimeError("D4 generators did not reach all eight elements")
    return tuple(word for word in words if word is not None)


def roll_word(
    hidden: np.ndarray,
    operators: np.ndarray,
    canonical_to_slot: np.ndarray,
    word: Sequence[int],
) -> tuple[np.ndarray, float]:
    state = normalized(hidden)
    log_gain = 0.0
    for action in word:
        slot = int(canonical_to_slot[int(action)])
        proposal = operators[slot] @ state
        radius = float(np.linalg.norm(proposal))
        if not np.isfinite(radius) or radius == 0.0:
            raise FloatingPointError("relation rollout reached a zero or nonfinite proposal")
        log_gain += math.log(radius)
        state = proposal / radius
    return state, log_gain


def canonical_centered_direction(
    centered_decoder: np.ndarray,
    hidden: np.ndarray,
    phi: np.ndarray,
) -> np.ndarray:
    visible = centered_decoder @ hidden
    canonical = visible[phi]
    norm = float(np.linalg.norm(canonical))
    if norm == 0.0 or not np.isfinite(norm):
        return np.full(8, np.nan, dtype=np.float64)
    return canonical / norm


def classify_relation_audit(p95_angle: float, agreement: float, log_gain: dict[str, Any]) -> str:
    maximum_absolute_gain = max(
        abs(float(log_gain["minimum"])), abs(float(log_gain["maximum"]))
    )
    if p95_angle <= 0.01 and agreement >= 0.99:
        return "radial_only" if maximum_absolute_gain > 1e-4 else "flat_loop"
    if p95_angle > 0.05 or agreement < 0.95:
        return "angular_holonomy"
    return "mixed_or_boundary"


def relation_audit(
    extracted: ExtractedModel,
    context_bank: dict[str, Any],
    canonical_maps: np.ndarray,
    representatives: tuple[tuple[int, ...], ...],
    *,
    repeats: Sequence[int] = RELATION_REPEATS,
) -> dict[str, Any]:
    operators_all = extracted.operators
    anchors = extracted.anchors
    decoder = extracted.decoder
    centered_decoder = extracted.centered_decoder
    phi_all = context_bank["phi"]
    slots_all = context_bank["canonical_to_slot"]
    output: dict[str, Any] = {}

    for repeat in repeats:
        agreement_counts = np.zeros((8, 3, 8), dtype=np.float64)
        joint_counts = np.zeros((8, 3, 8), dtype=np.float64)
        denominators = np.zeros((8, 3, 8), dtype=np.float64)
        context_agreement_counts = np.zeros((CONTEXT_COUNT, 8, 3, 8), dtype=np.float64)
        context_joint_counts = np.zeros((CONTEXT_COUNT, 8, 3, 8), dtype=np.float64)
        context_denominators = np.zeros((CONTEXT_COUNT, 8, 3, 8), dtype=np.float64)
        canonical_delta_sum = np.zeros((8, 3, 8), dtype=np.float64)
        canonical_delta_square_sum = np.zeros((8, 3, 8), dtype=np.float64)
        canonical_delta_count = np.zeros((8, 3, 1), dtype=np.float64)
        context_delta_sum = np.zeros((CONTEXT_COUNT, 8, 3, 8), dtype=np.float64)
        context_delta_square_sum = np.zeros((CONTEXT_COUNT, 8, 3, 8), dtype=np.float64)
        context_delta_count = np.zeros((CONTEXT_COUNT, 8, 3, 1), dtype=np.float64)
        angles: list[float] = []
        log_gains: list[float] = []
        relation_angles: dict[str, list[float]] = {name: [] for name in RELATION_NAMES}
        relation_gains: dict[str, list[float]] = {name: [] for name in RELATION_NAMES}

        for context_index in range(CONTEXT_COUNT):
            operators = operators_all[context_index]
            phi = phi_all[context_index]
            slots = slots_all[context_index]
            for prefix_element, prefix in enumerate(representatives):
                for start in range(8):
                    visible_start = int(phi[start])
                    initial = anchors[:, visible_start]
                    baseline_prefix, _ = roll_word(initial, operators, slots, prefix)
                    after_prefix = apply_state_word(canonical_maps, start, prefix)
                    for relation_index, relation_name in enumerate(RELATION_NAMES):
                        loop_word = RELATIONS[relation_name] * int(repeat)
                        loop_state, loop_gain = roll_word(
                            baseline_prefix, operators, slots, loop_word
                        )
                        angle = oriented_angle(baseline_prefix, loop_state)
                        angles.append(angle)
                        log_gains.append(loop_gain)
                        relation_angles[relation_name].append(angle)
                        relation_gains[relation_name].append(loop_gain)

                        for continuation in representatives:
                            base_future, _ = roll_word(
                                baseline_prefix, operators, slots, continuation
                            )
                            loop_future, _ = roll_word(
                                loop_state, operators, slots, continuation
                            )
                            base_logits = decoder @ base_future
                            loop_logits = decoder @ loop_future
                            base_prediction = int(np.argmax(base_logits))
                            loop_prediction = int(np.argmax(loop_logits))
                            target_canonical = apply_state_word(
                                canonical_maps, after_prefix, continuation
                            )
                            target_visible = int(phi[target_canonical])
                            agreement_counts[prefix_element, relation_index, start] += float(
                                base_prediction == loop_prediction
                            )
                            joint_counts[prefix_element, relation_index, start] += float(
                                base_prediction == target_visible
                                and loop_prediction == target_visible
                            )
                            denominators[prefix_element, relation_index, start] += 1.0
                            context_agreement_counts[
                                context_index, prefix_element, relation_index, start
                            ] += float(base_prediction == loop_prediction)
                            context_joint_counts[
                                context_index, prefix_element, relation_index, start
                            ] += float(
                                base_prediction == target_visible
                                and loop_prediction == target_visible
                            )
                            context_denominators[
                                context_index, prefix_element, relation_index, start
                            ] += 1.0

                            base_direction = canonical_centered_direction(
                                centered_decoder, base_future, phi
                            )
                            loop_direction = canonical_centered_direction(
                                centered_decoder, loop_future, phi
                            )
                            delta = loop_direction - base_direction
                            if np.isfinite(delta).all():
                                canonical_delta_sum[start, relation_index] += delta
                                canonical_delta_square_sum[start, relation_index] += delta * delta
                                canonical_delta_count[start, relation_index, 0] += 1.0
                                context_delta_sum[context_index, start, relation_index] += delta
                                context_delta_square_sum[context_index, start, relation_index] += delta * delta
                                context_delta_count[context_index, start, relation_index, 0] += 1.0

        agreement_tensor = agreement_counts / denominators
        joint_tensor = joint_counts / denominators
        context_agreement_tensor = context_agreement_counts / context_denominators
        context_joint_tensor = context_joint_counts / context_denominators
        with np.errstate(invalid="ignore", divide="ignore"):
            centered_delta = canonical_delta_sum / canonical_delta_count
            centered_delta_rms = np.sqrt(
                canonical_delta_square_sum / canonical_delta_count
            )
            context_centered_delta = context_delta_sum / context_delta_count
            context_centered_delta_rms = np.sqrt(
                context_delta_square_sum / context_delta_count
            )
        angle_summary = numeric_summary(angles)
        gain_summary = numeric_summary(log_gains)
        mean_agreement = float(np.mean(agreement_tensor))
        output[str(repeat)] = {
            "repeat": int(repeat),
            "future_behavior_congruence_tensor_axes": [
                "prefix_element",
                "relation",
                "canonical_start_state",
            ],
            "future_behavior_congruence_tensor_shape": list(agreement_tensor.shape),
            "future_behavior_congruence_tensor": agreement_tensor.tolist(),
            "joint_correctness_tensor": joint_tensor.tolist(),
            "per_context_future_behavior_congruence_tensor_axes": [
                "context",
                "prefix_element",
                "relation",
                "canonical_start_state",
            ],
            "per_context_future_behavior_congruence_tensor_shape": list(
                context_agreement_tensor.shape
            ),
            "per_context_future_behavior_congruence_tensor": context_agreement_tensor.tolist(),
            "per_context_joint_correctness_tensor": context_joint_tensor.tolist(),
            "canonical_centered_logit_delta_tensor_axes": [
                "canonical_start_state",
                "relation",
                "canonical_output_coordinate",
            ],
            "canonical_centered_logit_delta_tensor_shape": list(centered_delta.shape),
            "canonical_centered_logit_delta_tensor": centered_delta.tolist(),
            "canonical_centered_logit_delta_rms_tensor": centered_delta_rms.tolist(),
            "per_context_canonical_centered_logit_delta_tensor_axes": [
                "context",
                "canonical_start_state",
                "relation",
                "canonical_output_coordinate",
            ],
            "per_context_canonical_centered_logit_delta_tensor_shape": list(
                context_centered_delta.shape
            ),
            "per_context_canonical_centered_logit_delta_tensor": context_centered_delta.tolist(),
            "per_context_canonical_centered_logit_delta_rms_tensor": context_centered_delta_rms.tolist(),
            "loop_angle": angle_summary,
            "loop_log_radial_gain": gain_summary,
            "mean_behavioral_agreement": mean_agreement,
            "minimum_behavioral_congruence_cell": float(np.min(agreement_tensor)),
            "mean_joint_correctness": float(np.mean(joint_tensor)),
            "classification": classify_relation_audit(
                float(angle_summary["p95"]), mean_agreement, gain_summary
            ),
            "hard_polar_log_gain_check": bool(
                max(abs(float(gain_summary["minimum"])), abs(float(gain_summary["maximum"])))
                <= 1e-4
            ),
            "per_relation": {
                name: {
                    "angle": numeric_summary(relation_angles[name]),
                    "log_radial_gain": numeric_summary(relation_gains[name]),
                }
                for name in RELATION_NAMES
            },
        }
    return output


def compile_anchor_action(anchors: np.ndarray, visible_map: np.ndarray) -> np.ndarray:
    if np.linalg.matrix_rank(anchors) != 8:
        raise RuntimeError("anchor compiler requires eight independent anchor columns")
    inverse = np.linalg.pinv(anchors, rcond=1e-12)
    anchor_projector = anchors @ inverse
    complement = np.eye(anchors.shape[0]) - anchor_projector
    permutation = np.zeros((8, 8), dtype=np.float64)
    permutation[visible_map, np.arange(8)] = 1.0
    return anchors @ permutation @ inverse + complement


def exact_anchor_control(
    extracted: ExtractedModel,
    context_bank: dict[str, Any],
    canonical_maps: np.ndarray,
    representatives: tuple[tuple[int, ...], ...],
) -> dict[str, Any]:
    compiled = np.empty_like(extracted.operators)
    anchor_action_residuals: list[float] = []
    for context in range(CONTEXT_COUNT):
        for slot in range(2):
            compiled[context, slot] = compile_anchor_action(
                extracted.anchors, context_bank["maps"][context, slot]
            )
            visible_map = context_bank["maps"][context, slot]
            anchor_action_residuals.append(
                float(
                    np.linalg.norm(
                        compiled[context, slot] @ extracted.anchors
                        - extracted.anchors[:, visible_map],
                        ord="fro",
                    )
                )
            )
    oracle_decoder = np.linalg.pinv(extracted.anchors, rcond=1e-12)
    output_centering = np.eye(8) - np.ones((8, 8), dtype=np.float64) / 8.0
    oracle_centered_decoder = output_centering @ oracle_decoder
    control = ExtractedModel(
        operators=compiled,
        anchors=extracted.anchors,
        decoder=oracle_decoder,
        centered_decoder=oracle_centered_decoder,
        metric=extracted.metric,
        whitening=extracted.whitening,
        inverse_whitening=extracted.inverse_whitening,
    )
    audit = relation_audit(
        control,
        context_bank,
        canonical_maps,
        representatives,
        repeats=RELATION_REPEATS,
    )
    maximum_angle = max(float(audit[str(repeat)]["loop_angle"]["maximum"]) for repeat in RELATION_REPEATS)
    minimum_agreement = min(
        float(audit[str(repeat)]["minimum_behavioral_congruence_cell"])
        for repeat in RELATION_REPEATS
    )
    minimum_oracle_joint_correctness = min(
        float(np.min(np.asarray(audit[str(repeat)]["joint_correctness_tensor"])))
        for repeat in RELATION_REPEATS
    )
    ambient_residuals: list[float] = []
    for context in range(CONTEXT_COUNT):
        slots = context_bank["canonical_to_slot"][context]
        for relation in RELATIONS.values():
            visible_word = tuple(int(slots[action]) for action in relation)
            product = matrix_word(compiled[context], visible_word)
            ambient_residuals.append(
                float(np.linalg.norm(product - np.eye(product.shape[0]), ord=2))
            )
    maximum_ambient_relator_residual = max(ambient_residuals)
    pseudoinverse_residual = float(
        np.linalg.norm(oracle_decoder @ extracted.anchors - np.eye(8), ord=2)
    )
    oracle_anchor_predictions = np.argmax(oracle_decoder @ extracted.anchors, axis=0)
    oracle_anchor_accuracy = float(np.mean(oracle_anchor_predictions == np.arange(8)))
    learned_anchor_predictions = np.argmax(extracted.decoder @ extracted.anchors, axis=0)
    learned_anchor_accuracy = float(np.mean(learned_anchor_predictions == np.arange(8)))
    return {
        "compiler": "B P B^+ + (I - B B^+), in recurrence-metric whitened coordinates",
        "maximum_loop_angle": maximum_angle,
        "minimum_behavioral_congruence_cell": minimum_agreement,
        "minimum_joint_correctness_cell_with_oracle_decoder": minimum_oracle_joint_correctness,
        "maximum_full_ambient_relator_spectral_residual": maximum_ambient_relator_residual,
        "maximum_anchor_action_frobenius_residual": max(anchor_action_residuals),
        "pseudoinverse_left_identity_spectral_residual": pseudoinverse_residual,
        "oracle_decoder": "B^+ in the whitened anchor chart",
        "oracle_anchor_accuracy": oracle_anchor_accuracy,
        "learned_decoder_anchor_accuracy_descriptive": learned_anchor_accuracy,
        "pass": bool(
            maximum_angle <= 1e-6
            and minimum_agreement == 1.0
            and minimum_oracle_joint_correctness == 1.0
            and maximum_ambient_relator_residual <= 1e-10
            and max(anchor_action_residuals) <= 1e-10
            and pseudoinverse_residual <= 1e-10
            and oracle_anchor_accuracy == 1.0
        ),
        "repeats": {
            str(repeat): {
                "loop_angle": audit[str(repeat)]["loop_angle"],
                "mean_behavioral_agreement": audit[str(repeat)]["mean_behavioral_agreement"],
                "minimum_behavioral_congruence_cell": audit[str(repeat)]["minimum_behavioral_congruence_cell"],
                "minimum_oracle_joint_correctness_cell": float(
                    np.min(np.asarray(audit[str(repeat)]["joint_correctness_tensor"]))
                ),
            }
            for repeat in RELATION_REPEATS
        },
    }


def summarize_by_arm(records: list[dict[str, Any]]) -> dict[str, Any]:
    arms: dict[str, Any] = {}
    for arm in ("euclidean_supervised", "euclidean_cr", "polar_supervised", "polar_cr"):
        selected = sorted((row for row in records if row["arm"] == arm), key=lambda row: row["seed"])
        seed_rows: list[dict[str, Any]] = []
        for row in selected:
            horizon_four = [
                context["rank_ladder"][4] for context in row["contexts"]
            ]
            leakages = [
                cell["maximum_generator_leakage"]
                for cell in horizon_four
                if cell["maximum_generator_leakage"] is not None
            ]
            seed_rows.append(
                {
                    "seed": row["seed"],
                    "q4_minimum": min(cell["behavioral_rank"] for cell in horizon_four),
                    "q4_median": float(np.median([cell["behavioral_rank"] for cell in horizon_four])),
                    "q4_maximum": max(cell["behavioral_rank"] for cell in horizon_four),
                    "h4_null_dimension_range": [
                        min(cell["null_dimension"] for cell in horizon_four),
                        max(cell["null_dimension"] for cell in horizon_four),
                    ],
                    "h4_maximum_generator_leakage": max(leakages) if leakages else 0.0,
                    "instantaneous_null_reveal_maximum": max(
                        float(context["instantaneous_null_perturbation"]["maximum_reveal_angle"] or 0.0)
                        for context in row["contexts"]
                    ),
                    "relation": {
                        repeat: {
                            "p95_loop_angle": row["relation_audit"][repeat]["loop_angle"]["p95"],
                            "mean_behavioral_agreement": row["relation_audit"][repeat]["mean_behavioral_agreement"],
                            "minimum_behavioral_congruence_cell": row["relation_audit"][repeat]["minimum_behavioral_congruence_cell"],
                            "loop_log_gain_median": row["relation_audit"][repeat]["loop_log_radial_gain"]["median"],
                            "classification": row["relation_audit"][repeat]["classification"],
                        }
                        for repeat in ("1", "16")
                    },
                }
            )

        def aggregate_scalar(key: str) -> dict[str, float]:
            values = np.asarray([float(row[key]) for row in seed_rows], dtype=np.float64)
            return {
                "median": float(np.median(values)),
                "minimum": float(np.min(values)),
                "maximum": float(np.max(values)),
            }

        arms[arm] = {
            "independent_replication_unit": "training_seed",
            "seeds": seed_rows,
            "three_seed_summary": {
                "q4_maximum": aggregate_scalar("q4_maximum"),
                "h4_maximum_generator_leakage": aggregate_scalar("h4_maximum_generator_leakage"),
                "instantaneous_null_reveal_maximum": aggregate_scalar("instantaneous_null_reveal_maximum"),
                "relation_repeat_16_p95_loop_angle": {
                    "median": float(np.median([row["relation"]["16"]["p95_loop_angle"] for row in seed_rows])),
                    "minimum": float(np.min([row["relation"]["16"]["p95_loop_angle"] for row in seed_rows])),
                    "maximum": float(np.max([row["relation"]["16"]["p95_loop_angle"] for row in seed_rows])),
                },
                "relation_repeat_16_behavioral_agreement": {
                    "median": float(np.median([row["relation"]["16"]["mean_behavioral_agreement"] for row in seed_rows])),
                    "minimum": float(np.min([row["relation"]["16"]["mean_behavioral_agreement"] for row in seed_rows])),
                    "maximum": float(np.max([row["relation"]["16"]["mean_behavioral_agreement"] for row in seed_rows])),
                },
            },
        }
    return arms


def retained_failure(package: Path) -> dict[str, Any]:
    result_dir = package / "results" / "packet_closure_pilot"
    gates = json.loads((result_dir / "GATES.json").read_text(encoding="utf-8"))
    diagnosis = json.loads((result_dir / "A15_DIAGNOSIS.json").read_text(encoding="utf-8"))
    a15 = gates["assay_gates"]["A15_packet_result_contract"]
    if a15["status"] != "FAIL":
        raise RuntimeError("expected retained A15 failure is absent")
    return {
        "status": "RETAINED_NOT_REPAIRED",
        "original_assay_status": gates["assay_status"],
        "A15_packet_result_contract": a15,
        "diagnosis": diagnosis,
    }


def run_probe(package: Path, archive: Path) -> dict[str, Any]:
    started = time.time()
    archive_sha = sha256_file(archive)
    if archive_sha != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("v0.4 source archive SHA-256 mismatch")
    api = import_package(package)
    context_bank = make_context_bank(api)
    checkpoints, seal = verify_and_load_checkpoints(package, api)
    canonical_maps = api["canonical_maps"]("d4").astype(np.int64)
    representatives = shortest_d4_words(canonical_maps)

    model_records: list[dict[str, Any]] = []
    for index, checkpoint in enumerate(checkpoints, start=1):
        print(
            f"[{index:02d}/12] arm={checkpoint['arm']} seed={checkpoint['seed']}",
            flush=True,
        )
        extracted = extract_model(checkpoint["model"], context_bank["tables"])
        context_records: list[dict[str, Any]] = []
        for context_index in range(CONTEXT_COUNT):
            ladder, perturbation = rank_ladder_for_context(
                extracted.operators[context_index],
                extracted.anchors,
                extracted.centered_decoder,
            )
            context_records.append(
                {
                    "context_index": context_index,
                    "rank_ladder": ladder,
                    "instantaneous_null_perturbation": perturbation,
                }
            )
        typed_relations = relation_audit(
            extracted,
            context_bank,
            canonical_maps,
            representatives,
        )
        control = exact_anchor_control(
            extracted,
            context_bank,
            canonical_maps,
            representatives,
        )
        model_records.append(
            {
                "arm": checkpoint["arm"],
                "seed": checkpoint["seed"],
                "model_family": checkpoint["model_family"],
                "checkpoint": {
                    "filename": Path(checkpoint["path"]).name,
                    "sha256": checkpoint["sha256"],
                    "weights_only_load": checkpoint["weights_only_load"],
                    "strict_state_load": checkpoint["strict_state_load"],
                },
                "contexts": context_records,
                "relation_audit": typed_relations,
                "exact_anchor_compiled_positive_control": control,
            }
        )

    by_arm = summarize_by_arm(model_records)
    polar_cr_seeds = by_arm["polar_cr"]["seeds"]
    compact_supported = all(
        row["q4_maximum"] <= 8 and row["h4_maximum_generator_leakage"] <= 0.05
        for row in polar_cr_seeds
    )
    control_pass = all(
        row["exact_anchor_compiled_positive_control"]["pass"] for row in model_records
    )
    result = {
        "schema": "komorebi.neuralese.causal_completion_probe.v1",
        "version": VERSION,
        "author": AUTHOR,
        "analysis_status": ANALYSIS_STATUS,
        "claim_boundary": (
            "Posthoc audit of sealed learned checkpoints. It does not repair, replace, "
            "or supersede any original v0.4 gate."
        ),
        "source": {
            "archive": str(archive),
            "archive_sha256": archive_sha,
            "expected_archive_sha256": EXPECTED_ARCHIVE_SHA256,
            "archive_verified": True,
            "package": str(package),
            "checkpoint_seal_sha256": sha256_file(
                package / "results" / "packet_closure_pilot" / "CHECKPOINT_SEAL.json"
            ),
            "official_checkpoint_count": len(checkpoints),
            "all_checkpoint_sha256_verified": True,
            "all_weights_only_loads": True,
            "all_strict_state_loads": True,
        },
        "runtime": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "torch": torch.__version__,
            "device": "cpu",
            "checkpoint_forward_dtype": "float32, including operator encoding and polar SVD",
            "downstream_diagnostic_dtype": "float64 after extracting recurrence matrices, anchors, decoder, and metric",
            "elapsed_seconds": time.time() - started,
        },
        "context_bank": context_bank["receipt"],
        "design": {
            "horizons": list(HORIZONS),
            "rank_tolerances": list(RANK_TOLERANCES),
            "primary_rank_tolerance": PRIMARY_RANK_TOLERANCE,
            "block_rescaling": "each product block divided by its Frobenius norm",
            "null_perturbation_size": NULL_PERTURBATION_SIZE,
            "relation_names": list(RELATION_NAMES),
            "relation_repeats": list(RELATION_REPEATS),
            "oriented_positive_rays": True,
            "d4_shortest_representatives": [list(word) for word in representatives],
            "independent_replication_unit": "training_seed",
        },
        "compact_additive_quotient_test": {
            "criterion": "all polar_cr contexts have q4 <= 8 and seedwise maximum H4 null leakage <= 0.05",
            "supported": compact_supported,
            "status": "SUPPORTED" if compact_supported else "UNSUPPORTED",
        },
        "positive_control": {
            "all_12_checkpoint_charts_pass": control_pass,
            "status": "PASS" if control_pass else "FAIL",
        },
        "retained_original_failure": retained_failure(package),
        "by_arm": by_arm,
        "models": model_records,
        "checkpoint_seal_receipt_count": len(seal["checkpoints"]),
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", type=Path, default=DEFAULT_PACKAGE)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--output", type=Path, default=HERE / "RESULTS.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results = run_probe(args.package.resolve(), args.archive.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    print(
        json.dumps(
            {
                "status": "COMPLETE",
                "compact_additive_quotient": results["compact_additive_quotient_test"]["status"],
                "positive_control": results["positive_control"]["status"],
                "elapsed_seconds": results["runtime"]["elapsed_seconds"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
