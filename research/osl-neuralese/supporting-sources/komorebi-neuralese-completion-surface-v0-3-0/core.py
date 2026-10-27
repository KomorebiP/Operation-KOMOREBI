"""NumPy implementation of the finite Neuralese operator task and diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from checkpoint_io import LinearOperatorWeights


N_STATES = 8
N_OPERATORS = 2

_D4_R = np.array([4 * (i // 4) + ((i % 4 + 1) % 4) for i in range(8)], dtype=np.int64)
_D4_F = np.array([4 * (1 - i // 4) + ((-(i % 4)) % 4) for i in range(8)], dtype=np.int64)
_C8_A = np.array([(i + 1) % 8 for i in range(8)], dtype=np.int64)
_C8_B = np.array([(i + 3) % 8 for i in range(8)], dtype=np.int64)
_MIXED_A = _C8_A.copy()
_MIXED_B = np.array([i ^ 1 for i in range(8)], dtype=np.int64)

D4_RELATIONS: dict[str, tuple[int, ...]] = {
    "r4": (0, 0, 0, 0),
    "f2": (1, 1),
    "frfr": (1, 0, 1, 0),
}

D4_EQUIVALENT_PATHS: dict[str, tuple[tuple[int, ...], tuple[int, ...]]] = {
    "identity_r4": ((), (0, 0, 0, 0)),
    "identity_f2": ((), (1, 1)),
    "r_inverse": ((0, 0, 0), (1, 0, 1)),
    "rf_rewrite": ((0, 1), (1, 0, 0, 0)),
}

D4_REPRESENTATIVE_WORDS: tuple[tuple[int, ...], ...] = (
    (),
    (0,),
    (0, 0),
    (0, 0, 0),
    (1,),
    (1, 0),
    (1, 0, 0),
    (1, 0, 0, 0),
)


def d4_cayley_reduction() -> dict[tuple[int, int], int]:
    canonical = canonical_maps("d4")
    actions = [tuple(compose_maps(canonical, word)) for word in D4_REPRESENTATIVE_WORDS]
    if len(set(actions)) != N_STATES:
        raise ArithmeticError("D4 representative words are not distinct")
    action_to_index = {action: index for index, action in enumerate(actions)}
    reduction: dict[tuple[int, int], int] = {}
    for left, left_word in enumerate(D4_REPRESENTATIVE_WORDS):
        for right, right_word in enumerate(D4_REPRESENTATIVE_WORDS):
            action = tuple(compose_maps(canonical, left_word + right_word))
            reduction[(left, right)] = action_to_index[action]
    return reduction


@dataclass(frozen=True)
class EpisodeBatch:
    tables: np.ndarray
    maps: np.ndarray
    op_slots: np.ndarray
    canonical_ops: np.ndarray
    start: np.ndarray
    target: np.ndarray
    canonical_to_slot: np.ndarray
    phi: np.ndarray
    family: str


def canonical_maps(family: str) -> np.ndarray:
    key = family.lower()
    if key == "d4":
        return np.stack((_D4_R, _D4_F))
    if key == "c8":
        return np.stack((_C8_A, _C8_B))
    if key == "mixed_cycle":
        return np.stack((_MIXED_A, _MIXED_B))
    raise ValueError(f"unknown fixed family: {family}")


def compose_maps(maps: np.ndarray, word: Iterable[int]) -> np.ndarray:
    current = np.arange(N_STATES, dtype=np.int64)
    for operator in word:
        current = maps[int(operator), current]
    return current


def _permutations(rng: np.random.Generator, batch_size: int) -> np.ndarray:
    return np.argsort(rng.random((batch_size, N_STATES)), axis=1).astype(np.int64)


def conjugate_maps(canonical: np.ndarray, phi: np.ndarray) -> np.ndarray:
    inverse = np.argsort(phi, axis=1)
    output = np.empty((phi.shape[0], canonical.shape[0], canonical.shape[1]), dtype=np.int64)
    for operator in range(canonical.shape[0]):
        canonical_target = canonical[operator][inverse]
        output[:, operator] = np.take_along_axis(phi, canonical_target, axis=1)
    return output


def sample_batch(
    rng: np.random.Generator,
    batch_size: int,
    length: int,
    family: str = "d4",
    canonical_word: tuple[int, ...] | None = None,
    starts: np.ndarray | None = None,
) -> EpisodeBatch:
    if batch_size < 1 or length < 0:
        raise ValueError("batch_size must be positive and length nonnegative")
    phi = _permutations(rng, batch_size)
    if family == "random":
        canonical_batch_maps = np.stack(
            (_permutations(rng, batch_size), _permutations(rng, batch_size)), axis=1
        )
    else:
        canonical_batch_maps = conjugate_maps(canonical_maps(family), phi)
    swap = rng.integers(0, 2, size=batch_size, dtype=np.int64)
    slot_maps = np.empty_like(canonical_batch_maps)
    slot_maps[:, 0] = np.where(
        swap[:, None].astype(bool), canonical_batch_maps[:, 1], canonical_batch_maps[:, 0]
    )
    slot_maps[:, 1] = np.where(
        swap[:, None].astype(bool), canonical_batch_maps[:, 0], canonical_batch_maps[:, 1]
    )
    canonical_to_slot = np.stack((swap, 1 - swap), axis=1)
    if canonical_word is None:
        canonical_ops = rng.integers(0, 2, size=(batch_size, length), dtype=np.int64)
    else:
        if len(canonical_word) != length:
            raise ValueError("canonical word length mismatch")
        canonical_ops = np.broadcast_to(
            np.asarray(canonical_word, dtype=np.int64), (batch_size, length)
        ).copy()
    if length:
        op_slots = np.take_along_axis(canonical_to_slot, canonical_ops, axis=1)
    else:
        op_slots = np.empty((batch_size, 0), dtype=np.int64)
    if starts is None:
        start = rng.integers(0, N_STATES, size=batch_size, dtype=np.int64)
    else:
        start = np.asarray(starts, dtype=np.int64).copy()
        if start.shape != (batch_size,):
            raise ValueError("starts must have shape (batch_size,)")
    current = start.copy()
    rows = np.arange(batch_size)
    for step in range(length):
        selected = slot_maps[rows, op_slots[:, step]]
        current = selected[rows, current]
    tables = np.eye(N_STATES, dtype=np.float32)[slot_maps]
    return EpisodeBatch(
        tables=tables,
        maps=slot_maps,
        op_slots=op_slots,
        canonical_ops=canonical_ops,
        start=start,
        target=current,
        canonical_to_slot=canonical_to_slot,
        phi=phi,
        family=family,
    )


def slots_for_word(canonical_to_slot: np.ndarray, word: tuple[int, ...]) -> np.ndarray:
    if not word:
        return np.empty((canonical_to_slot.shape[0], 0), dtype=np.int64)
    return canonical_to_slot[:, np.asarray(word, dtype=np.int64)]


def encode_tables(weights: LinearOperatorWeights, tables: np.ndarray, dtype=None) -> np.ndarray:
    requested_dtype = np.dtype(dtype or tables.dtype)
    flat = np.asarray(tables, dtype=requested_dtype).reshape(-1, N_STATES * N_STATES)
    encoder = weights.operator_encoder.astype(requested_dtype, copy=False)
    encoded = flat @ encoder.T
    return encoded.reshape(tables.shape[0], N_OPERATORS, N_STATES, N_STATES)


def normalize_rows(states: np.ndarray, epsilon: float = 1e-12) -> np.ndarray:
    norms = np.linalg.norm(states, axis=-1, keepdims=True)
    return states / np.maximum(norms, epsilon)


def apply_slots(
    hidden: np.ndarray,
    codes: np.ndarray,
    op_slots: np.ndarray,
    normalize_each_step: bool,
) -> np.ndarray:
    rows = np.arange(hidden.shape[0])
    state = hidden
    for step in range(op_slots.shape[1]):
        selected = codes[rows, op_slots[:, step]]
        state = np.einsum("bij,bj->bi", selected, state)
        if normalize_each_step:
            state = normalize_rows(state)
    return state


def run_batch(
    weights: LinearOperatorWeights,
    batch: EpisodeBatch,
    normalize_each_step: bool,
    dtype=np.float32,
) -> tuple[np.ndarray, np.ndarray]:
    requested_dtype = np.dtype(dtype)
    codes = encode_tables(weights, batch.tables, requested_dtype)
    hidden = weights.state_embedding.astype(requested_dtype, copy=False)[batch.start].copy()
    hidden = apply_slots(hidden, codes, batch.op_slots, normalize_each_step)
    decoder = weights.decoder.astype(requested_dtype, copy=False)
    logits = hidden @ decoder.T
    return hidden, logits


def predict(weights: LinearOperatorWeights, hidden: np.ndarray) -> np.ndarray:
    decoder = weights.decoder.astype(hidden.dtype, copy=False)
    return np.argmax(hidden @ decoder.T, axis=-1)


def positive_ray_angle(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    """Oriented positive-ray angle; opposite signs are not identified."""

    left_unit = normalize_rows(np.asarray(left, dtype=np.float64))
    right_unit = normalize_rows(np.asarray(right, dtype=np.float64))
    cosine = np.sum(left_unit * right_unit, axis=-1)
    return np.arccos(np.clip(cosine, -1.0, 1.0))


def target_margin(weights: LinearOperatorWeights, hidden: np.ndarray, target: np.ndarray) -> np.ndarray:
    logits = hidden @ weights.decoder.astype(hidden.dtype, copy=False).T
    rows = np.arange(logits.shape[0])
    selected = logits[rows, target]
    masked = logits.copy()
    masked[rows, target] = -np.inf
    return selected - np.max(masked, axis=1)


def all_start_cases(
    weights: LinearOperatorWeights,
    codes: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    episodes = codes.shape[0]
    starts = np.tile(np.arange(N_STATES, dtype=np.int64), episodes)
    hidden = np.tile(weights.state_embedding, (episodes, 1))
    expanded_codes = np.repeat(codes, N_STATES, axis=0)
    return hidden, expanded_codes, starts


def reachable_all_start_cases(
    weights: LinearOperatorWeights,
    batch: EpisodeBatch,
    codes: np.ndarray,
    prefix_slots: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Reach one registered history per episode and every starting state."""

    initial, expanded_codes, semantic = all_start_cases(weights, codes)
    if prefix_slots.shape[0] != batch.tables.shape[0]:
        raise ValueError("prefix episode count mismatch")
    case_prefix = np.repeat(np.asarray(prefix_slots, dtype=np.int64), N_STATES, axis=0)
    reached = apply_slots(initial, expanded_codes, case_prefix, normalize_each_step=True)
    maps = np.repeat(batch.maps, N_STATES, axis=0)
    rows = np.arange(semantic.shape[0])
    for step in range(case_prefix.shape[1]):
        selected = maps[rows, case_prefix[:, step]]
        semantic = selected[rows, semantic]
    return reached, expanded_codes, semantic


def apply_canonical_word_cases(
    hidden: np.ndarray,
    codes: np.ndarray,
    canonical_to_slot: np.ndarray,
    word: tuple[int, ...],
    repeats: int = 1,
) -> np.ndarray:
    if hidden.shape[0] % canonical_to_slot.shape[0] != 0:
        raise ValueError("case count must be a multiple of episode count")
    multiplicity = hidden.shape[0] // canonical_to_slot.shape[0]
    episode_slots = slots_for_word(canonical_to_slot, word * int(repeats))
    case_slots = np.repeat(episode_slots, multiplicity, axis=0)
    return apply_slots(hidden.copy(), codes, case_slots, normalize_each_step=True)


def future_equivalence_curve(
    weights: LinearOperatorWeights,
    left: np.ndarray,
    right: np.ndarray,
    codes: np.ndarray,
    horizon: int,
) -> dict[str, object]:
    """Exhaust all two-generator suffixes and locate first behavioral reveal."""

    if horizon < 0:
        raise ValueError("horizon must be nonnegative")
    case_count = left.shape[0]
    left_frontier = left[:, None, :]
    right_frontier = right[:, None, :]
    revealed = np.zeros(case_count, dtype=bool)
    first_reveal = np.full(case_count, horizon + 1, dtype=np.int64)
    exact_any: list[float] = []
    survival: list[float] = []
    worst_centered_logit_l2: list[float] = []
    decoder = weights.decoder.astype(np.float64)
    centering = np.eye(N_STATES) - np.ones((N_STATES, N_STATES)) / N_STATES
    centered_decoder = centering @ decoder
    for depth in range(horizon + 1):
        left_logits = np.einsum("cbi,ki->cbk", left_frontier, decoder)
        right_logits = np.einsum("cbi,ki->cbk", right_frontier, decoder)
        disagree = np.argmax(left_logits, axis=-1) != np.argmax(right_logits, axis=-1)
        any_disagree = np.any(disagree, axis=1)
        newly = (~revealed) & any_disagree
        first_reveal[newly] = depth
        revealed |= any_disagree
        exact_any.append(float(np.mean(any_disagree)))
        survival.append(float(np.mean(~revealed)))
        left_centered = np.einsum("cbi,ki->cbk", left_frontier, centered_decoder)
        right_centered = np.einsum("cbi,ki->cbk", right_frontier, centered_decoder)
        per_case = np.max(np.linalg.norm(left_centered - right_centered, axis=-1), axis=1)
        worst_centered_logit_l2.append(float(np.mean(per_case)))
        if depth == horizon:
            break
        left_next = np.einsum("coij,cbj->cboi", codes, left_frontier)
        right_next = np.einsum("coij,cbj->cboi", codes, right_frontier)
        left_frontier = normalize_rows(left_next).reshape(case_count, -1, N_STATES)
        right_frontier = normalize_rows(right_next).reshape(case_count, -1, N_STATES)
    histogram = {
        str(depth): int(np.sum(first_reveal == depth)) for depth in range(horizon + 1)
    }
    histogram[f">{horizon}"] = int(np.sum(first_reveal == horizon + 1))
    return {
        "case_count": int(case_count),
        "horizon": int(horizon),
        "exact_depth_any_disagreement_fraction": exact_any,
        "equivalent_through_horizon_fraction": survival,
        "first_reveal_histogram": histogram,
        "first_reveal_depth": first_reveal.tolist(),
        "mean_case_worst_centered_logit_l2": worst_centered_logit_l2,
    }


def tangent_basis(ray: np.ndarray) -> np.ndarray:
    unit = normalize_rows(np.asarray(ray, dtype=np.float64)[None, :])[0]
    e0 = np.zeros_like(unit)
    e0[0] = 1.0
    vector = e0 - unit
    if np.linalg.norm(vector) < 1e-12:
        householder = np.eye(unit.size)
    else:
        householder = np.eye(unit.size) - 2.0 * np.outer(vector, vector) / np.dot(vector, vector)
    basis = householder[:, 1:]
    if np.linalg.norm(basis.T @ unit) > 1e-10:
        raise ArithmeticError("failed to construct a tangent basis")
    return basis


def projective_word_tangent(
    hidden: np.ndarray,
    matrices: Iterable[np.ndarray],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return final ray, tangent singular values, and full tangent derivative."""

    state = normalize_rows(np.asarray(hidden, dtype=np.float64)[None, :])[0]
    derivative = tangent_basis(state)
    identity = np.eye(state.size)
    for matrix in matrices:
        matrix = np.asarray(matrix, dtype=np.float64)
        unnormalized = matrix @ state
        radial_norm = float(np.linalg.norm(unnormalized))
        if not np.isfinite(radial_norm) or radial_norm <= 1e-15:
            raise ArithmeticError("projective operator reached the zero ray")
        state = unnormalized / radial_norm
        jacobian = (identity - np.outer(state, state)) @ matrix / radial_norm
        derivative = jacobian @ derivative
    singular_values = np.linalg.svd(derivative, compute_uv=False)
    return state, singular_values, derivative


def tangent_observability_tower(
    weights: LinearOperatorWeights,
    hidden: np.ndarray,
    operators: np.ndarray,
    horizon: int,
    relative_tolerance: float = 1e-8,
) -> list[dict[str, object]]:
    """Local logit-observability proxy on the seven-dimensional ray tangent."""

    state = normalize_rows(np.asarray(hidden, dtype=np.float64)[None, :])[0]
    basis = tangent_basis(state)
    decoder = weights.decoder.astype(np.float64)
    centering = np.eye(N_STATES) - np.ones((N_STATES, N_STATES)) / N_STATES
    observation = centering @ decoder
    frontier: list[tuple[np.ndarray, np.ndarray]] = [(state, basis)]
    cumulative = np.zeros((N_STATES - 1, N_STATES - 1), dtype=np.float64)
    output: list[dict[str, object]] = []
    identity = np.eye(N_STATES)
    for depth in range(horizon + 1):
        exact = np.zeros_like(cumulative)
        for _, derivative in frontier:
            observed = observation @ derivative
            exact += observed.T @ observed
        exact /= len(frontier)
        cumulative += exact
        eigenvalues = np.linalg.eigvalsh((cumulative + cumulative.T) / 2)
        eigenvalues = np.clip(eigenvalues, 0.0, None)
        threshold = relative_tolerance * max(1.0, float(eigenvalues[-1]))
        rank = int(np.sum(eigenvalues > threshold))
        trace = float(np.sum(eigenvalues))
        effective_rank = trace * trace / max(float(np.sum(eigenvalues**2)), 1e-30)
        output.append(
            {
                "depth": depth,
                "rank": rank,
                "null_dimension": (N_STATES - 1) - rank,
                "eigenvalues": eigenvalues.tolist(),
                "condition_number_on_rank": (
                    float(eigenvalues[-1] / eigenvalues[-rank]) if rank else None
                ),
                "effective_rank": float(effective_rank),
                "exact_depth_trace": float(np.trace(exact)),
                "cumulative_trace": trace,
            }
        )
        if depth == horizon:
            break
        next_frontier: list[tuple[np.ndarray, np.ndarray]] = []
        for current, derivative in frontier:
            for matrix in operators:
                unnormalized = matrix.astype(np.float64) @ current
                radial_norm = float(np.linalg.norm(unnormalized))
                updated = unnormalized / radial_norm
                jacobian = (identity - np.outer(updated, updated)) @ matrix / radial_norm
                next_frontier.append((updated, jacobian @ derivative))
        frontier = next_frontier
    return output
