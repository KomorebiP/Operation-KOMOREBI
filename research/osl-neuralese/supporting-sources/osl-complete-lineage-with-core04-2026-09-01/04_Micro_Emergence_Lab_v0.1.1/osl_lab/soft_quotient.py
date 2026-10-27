"""Finite exact quotients and fuzzy operator-lumpability analysis.

The convention is the one used in the theory notes: rows index concrete
states, ``P_g`` is a row-stochastic transition matrix, and ``W`` maps concrete
states to symbolic memberships.  Closure asks for ``P_g W ~= W M_g``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np


def _as_2d(value: Any, *, name: str) -> np.ndarray:
    array = np.asarray(value, dtype=float)
    if array.ndim == 1:
        array = array[:, None]
    if array.ndim != 2:
        raise ValueError(f"{name} must be a one- or two-dimensional array")
    return array


def validate_transition_matrices(
    transitions: Mapping[str, Any], *, tolerance: float = 1e-7
) -> tuple[dict[str, np.ndarray], int]:
    if not transitions:
        raise ValueError("At least one transition matrix is required")
    converted: dict[str, np.ndarray] = {}
    state_count: int | None = None
    for name in sorted(transitions):
        matrix = np.asarray(transitions[name], dtype=float)
        if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
            raise ValueError(f"Transition {name!r} must be square")
        if state_count is None:
            state_count = matrix.shape[0]
        elif matrix.shape != (state_count, state_count):
            raise ValueError("All transition matrices must use the same state space")
        if not np.all(np.isfinite(matrix)) or np.any(matrix < -tolerance):
            raise ValueError(f"Transition {name!r} has invalid probabilities")
        row_sums = matrix.sum(axis=1)
        if not np.allclose(row_sums, 1.0, atol=tolerance, rtol=0):
            raise ValueError(f"Rows of transition {name!r} must sum to one")
        converted[str(name)] = matrix
    return converted, int(state_count or 0)


def validate_membership(membership: Any, *, tolerance: float = 1e-7) -> np.ndarray:
    value = _as_2d(membership, name="membership")
    if not np.all(np.isfinite(value)) or np.any(value < -tolerance):
        raise ValueError("Membership entries must be finite and nonnegative")
    if not np.allclose(value.sum(axis=1), 1.0, atol=tolerance, rtol=0):
        raise ValueError("Every membership row must sum to one")
    return value


def estimate_symbolic_operator(transition: Any, membership: Any) -> np.ndarray:
    """Least-squares estimate of ``M`` in ``P W = W M``."""

    p = np.asarray(transition, dtype=float)
    w = validate_membership(membership)
    if p.shape != (w.shape[0], w.shape[0]):
        raise ValueError("Transition and membership state dimensions do not match")
    matrix, *_ = np.linalg.lstsq(w, p @ w, rcond=None)
    return matrix


def lumpability_residual(
    transition: Any,
    membership: Any,
    symbolic_operator: Any | None = None,
    *,
    epsilon: float = 1e-12,
) -> dict[str, Any]:
    p = np.asarray(transition, dtype=float)
    w = validate_membership(membership)
    m = (
        estimate_symbolic_operator(p, w)
        if symbolic_operator is None
        else np.asarray(symbolic_operator, dtype=float)
    )
    concrete_then_compress = p @ w
    compress_then_symbolic = w @ m
    error = concrete_then_compress - compress_then_symbolic
    denominator = max(float(np.linalg.norm(concrete_then_compress, ord="fro")), epsilon)
    return {
        "absolute_residual": float(np.linalg.norm(error, ord="fro")),
        "relative_residual": float(np.linalg.norm(error, ord="fro") / denominator),
        "max_absolute_error": float(np.max(np.abs(error))) if error.size else 0.0,
        "symbolic_operator": m,
    }


def estimate_observation_decoder(membership: Any, observations: Any) -> np.ndarray:
    w = validate_membership(membership)
    o = _as_2d(observations, name="observations")
    if o.shape[0] != w.shape[0]:
        raise ValueError("Observations and membership must have the same number of states")
    decoder, *_ = np.linalg.lstsq(w, o, rcond=None)
    return decoder


def observation_residual(
    membership: Any, observations: Any, decoder: Any | None = None, *, epsilon: float = 1e-12
) -> dict[str, Any]:
    w = validate_membership(membership)
    o = _as_2d(observations, name="observations")
    d = estimate_observation_decoder(w, o) if decoder is None else np.asarray(decoder, dtype=float)
    error = o - w @ d
    denominator = max(float(np.linalg.norm(o, ord="fro")), epsilon)
    return {
        "absolute_residual": float(np.linalg.norm(error, ord="fro")),
        "relative_residual": float(np.linalg.norm(error, ord="fro") / denominator),
        "max_absolute_error": float(np.max(np.abs(error))) if error.size else 0.0,
        "decoder": d,
    }


def membership_statistics(membership: Any, *, epsilon: float = 1e-12) -> dict[str, float]:
    w = validate_membership(membership)
    entropy_by_state = -np.sum(w * np.log(np.clip(w, epsilon, 1.0)), axis=1)
    symbol_mass = w.mean(axis=0)
    symbol_entropy = -float(np.sum(symbol_mass * np.log(np.clip(symbol_mass, epsilon, 1.0))))
    return {
        "mean_state_entropy": float(entropy_by_state.mean()),
        "max_state_entropy": float(entropy_by_state.max(initial=0.0)),
        "effective_symbols": float(np.exp(symbol_entropy)),
        "minimum_symbol_mass": float(symbol_mass.min()) if symbol_mass.size else 0.0,
        "maximum_symbol_mass": float(symbol_mass.max()) if symbol_mass.size else 0.0,
    }


def harden_membership(membership: Any) -> np.ndarray:
    w = validate_membership(membership)
    hard = np.zeros_like(w)
    hard[np.arange(w.shape[0]), np.argmax(w, axis=1)] = 1.0
    return hard


def _observation_keys(observations: Any, state_count: int) -> tuple[list[tuple[Any, ...]], np.ndarray]:
    array = np.asarray(observations)
    if array.ndim == 1:
        if array.shape[0] != state_count:
            raise ValueError("Observation count does not match the transition state space")
        raw_keys = [(str(value),) for value in array.tolist()]
        classes = sorted({key[0] for key in raw_keys})
        class_index = {value: index for index, value in enumerate(classes)}
        encoded = np.zeros((state_count, len(classes)), dtype=float)
        for state, key in enumerate(raw_keys):
            encoded[state, class_index[key[0]]] = 1.0
        return raw_keys, encoded
    numeric = _as_2d(observations, name="observations")
    if numeric.shape[0] != state_count:
        raise ValueError("Observation count does not match the transition state space")
    keys = [tuple(float(value) for value in row) for row in numeric]
    return keys, numeric.astype(float)


def exact_partition(
    transitions: Mapping[str, Any], observations: Any, *, tolerance: float = 1e-9
) -> dict[str, Any]:
    """Compute the coarsest observation-respecting deterministic quotient.

    This partition-refinement routine requires one-hot deterministic transition
    rows.  For stochastic systems, use :func:`fit_soft_quotient`.
    """

    matrices, state_count = validate_transition_matrices(transitions)
    observation_keys, encoded_observations = _observation_keys(observations, state_count)
    next_states: dict[str, np.ndarray] = {}
    for name, matrix in matrices.items():
        maxima = np.argmax(matrix, axis=1)
        one_hot = np.zeros_like(matrix)
        one_hot[np.arange(state_count), maxima] = 1.0
        if not np.allclose(matrix, one_hot, atol=tolerance, rtol=0):
            raise ValueError("exact_partition requires deterministic one-hot transitions")
        next_states[name] = maxima

    unique_observations = sorted(set(observation_keys), key=repr)
    obs_to_block = {signature: index for index, signature in enumerate(unique_observations)}
    labels = np.asarray([obs_to_block[key] for key in observation_keys], dtype=int)
    iterations = 0
    while True:
        signatures = []
        for state in range(state_count):
            targets = tuple(int(labels[next_states[name][state]]) for name in sorted(next_states))
            signatures.append((observation_keys[state], targets))
        unique = sorted(set(signatures), key=repr)
        mapping = {signature: index for index, signature in enumerate(unique)}
        refined = np.asarray([mapping[signature] for signature in signatures], dtype=int)
        iterations += 1
        # Partition labels can be renamed; compare pairwise equivalence instead.
        old_relation = labels[:, None] == labels[None, :]
        new_relation = refined[:, None] == refined[None, :]
        labels = refined
        if np.array_equal(old_relation, new_relation):
            break
        if iterations > state_count:
            raise RuntimeError("Partition refinement did not converge")
    symbol_count = int(labels.max(initial=-1) + 1)
    membership = np.zeros((state_count, symbol_count), dtype=float)
    membership[np.arange(state_count), labels] = 1.0
    analysis = analyze_membership(matrices, membership, encoded_observations)
    return {
        "labels": labels,
        "membership": membership,
        "symbol_count": symbol_count,
        "iterations": iterations,
        "analysis": analysis,
    }


def _semantic_features(
    transitions: Mapping[str, np.ndarray], observations: np.ndarray, depth: int
) -> np.ndarray:
    features = [observations]
    frontier = [observations]
    for _ in range(max(0, int(depth))):
        next_frontier = []
        for base in frontier:
            for name in sorted(transitions):
                transformed = transitions[name] @ base
                features.append(transformed)
                next_frontier.append(transformed)
        frontier = next_frontier
    result = np.concatenate(features, axis=1)
    means = result.mean(axis=0, keepdims=True)
    scales = result.std(axis=0, keepdims=True)
    return (result - means) / np.where(scales > 1e-12, scales, 1.0)


def _deterministic_kmeans(
    features: np.ndarray, clusters: int, *, seed: int, iterations: int = 100
) -> tuple[np.ndarray, np.ndarray]:
    if clusters < 1 or clusters > features.shape[0]:
        raise ValueError("n_symbols must be between one and the number of concrete states")
    rng = np.random.default_rng(seed)
    # Seed the first center far from the mean, then use farthest-point seeding.
    center_indices = [int(np.argmax(np.sum((features - features.mean(axis=0)) ** 2, axis=1)))]
    while len(center_indices) < clusters:
        distances = np.min(
            np.stack(
                [np.sum((features - features[index]) ** 2, axis=1) for index in center_indices],
                axis=1,
            ),
            axis=1,
        )
        distances[center_indices] = -1
        maximum = np.flatnonzero(distances == distances.max())
        center_indices.append(int(rng.choice(maximum)))
    centers = features[center_indices].copy()
    labels = np.zeros(features.shape[0], dtype=int)
    for _ in range(int(iterations)):
        squared = np.sum((features[:, None, :] - centers[None, :, :]) ** 2, axis=2)
        new_labels = np.argmin(squared, axis=1)
        if np.array_equal(labels, new_labels) and _ > 0:
            break
        labels = new_labels
        for cluster in range(clusters):
            members = features[labels == cluster]
            if len(members):
                centers[cluster] = members.mean(axis=0)
            else:
                nearest = np.min(squared, axis=1)
                replacement = int(np.argmax(nearest))
                centers[cluster] = features[replacement]
                labels[replacement] = cluster
    return centers, labels


def fuzzy_membership(features: Any, centers: Any, *, temperature: float = 1.0) -> np.ndarray:
    x = _as_2d(features, name="features")
    c = _as_2d(centers, name="centers")
    if x.shape[1] != c.shape[1]:
        raise ValueError("Feature and center dimensions differ")
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    squared = np.sum((x[:, None, :] - c[None, :, :]) ** 2, axis=2)
    logits = -squared / float(temperature)
    logits -= logits.max(axis=1, keepdims=True)
    weights = np.exp(logits)
    return weights / weights.sum(axis=1, keepdims=True)


def analyze_membership(
    transitions: Mapping[str, Any], membership: Any, observations: Any
) -> dict[str, Any]:
    matrices, state_count = validate_transition_matrices(transitions)
    w = validate_membership(membership)
    if w.shape[0] != state_count:
        raise ValueError("Membership and transition state dimensions differ")
    o = _as_2d(observations, name="observations")
    operator_results: dict[str, Any] = {}
    relative_values = []
    for name, matrix in matrices.items():
        result = lumpability_residual(matrix, w)
        relative_values.append(result["relative_residual"])
        operator_results[name] = result
    obs_result = observation_residual(w, o)
    return {
        "operators": operator_results,
        "mean_lumpability_residual": float(np.mean(relative_values)) if relative_values else 0.0,
        "max_lumpability_residual": float(np.max(relative_values)) if relative_values else 0.0,
        "observation": obs_result,
        "membership": membership_statistics(w),
    }


def fit_soft_quotient(
    transitions: Mapping[str, Any],
    observations: Any,
    n_symbols: int,
    *,
    temperature: float = 1.0,
    feature_depth: int = 2,
    seed: int = 17,
    kmeans_iterations: int = 100,
) -> dict[str, Any]:
    """Discover a reproducible fuzzy quotient from finite transition data."""

    matrices, state_count = validate_transition_matrices(transitions)
    _, encoded_observations = _observation_keys(observations, state_count)
    features = _semantic_features(matrices, encoded_observations, feature_depth)
    centers, hard_labels = _deterministic_kmeans(
        features, int(n_symbols), seed=int(seed), iterations=int(kmeans_iterations)
    )
    membership = fuzzy_membership(features, centers, temperature=float(temperature))
    analysis = analyze_membership(matrices, membership, encoded_observations)
    hard = harden_membership(membership)
    hard_analysis = analyze_membership(matrices, hard, encoded_observations)
    return {
        "membership": membership,
        "hard_membership": hard,
        "hard_labels": hard_labels,
        "centers": centers,
        "features": features,
        "temperature": float(temperature),
        "feature_depth": int(feature_depth),
        "analysis": analysis,
        "hard_analysis": hard_analysis,
    }


def temperature_hardening_sweep(
    transitions: Mapping[str, Any],
    observations: Any,
    n_symbols: int,
    temperatures: Sequence[float],
    *,
    feature_depth: int = 2,
    seed: int = 17,
) -> dict[str, Any]:
    matrices, state_count = validate_transition_matrices(transitions)
    _, encoded_observations = _observation_keys(observations, state_count)
    features = _semantic_features(matrices, encoded_observations, feature_depth)
    centers, _ = _deterministic_kmeans(features, int(n_symbols), seed=int(seed))
    rows = []
    for temperature in temperatures:
        membership = fuzzy_membership(features, centers, temperature=float(temperature))
        analysis = analyze_membership(matrices, membership, encoded_observations)
        rows.append(
            {
                "temperature": float(temperature),
                "mean_lumpability_residual": analysis["mean_lumpability_residual"],
                "max_lumpability_residual": analysis["max_lumpability_residual"],
                "observation_residual": analysis["observation"]["relative_residual"],
                **analysis["membership"],
            }
        )
    return {"n_symbols": int(n_symbols), "feature_depth": int(feature_depth), "rows": rows}


def world_transition_system(
    world: str,
    *,
    query_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Enumerate a built-in world into matrices for quotient analysis.

    ``query_ids`` defines the observation doctrine.  Omitting it uses all
    declared queries, which is intentionally conservative and may yield the
    identity partition when every concrete state is externally distinguishable.
    """

    from .worlds import canonical_json, enumerate_states, execute, get_world, query_answers

    spec = get_world(world)
    states = list(enumerate_states(spec))
    state_index = {canonical_json(state): index for index, state in enumerate(states)}
    transitions: dict[str, np.ndarray] = {}
    for operator in spec.operators:
        matrix = np.zeros((len(states), len(states)), dtype=float)
        for source, state in enumerate(states):
            destination_state = execute(spec, state, (operator,)).final_state
            destination = state_index[canonical_json(destination_state)]
            matrix[source, destination] = 1.0
        transitions[operator] = matrix
    selected_queries = tuple(query_ids) if query_ids is not None else spec.query_ids
    unknown = sorted(set(selected_queries) - set(spec.query_ids))
    if unknown:
        raise ValueError(f"Unknown queries for {world!r}: {unknown}")
    observation_labels = np.asarray(
        [
            canonical_json(
                {query: query_answers(spec, state)[query] for query in selected_queries}
            )
            for state in states
        ],
        dtype=object,
    )
    return {
        "world": spec.name,
        "states": states,
        "operators": list(spec.operators),
        "query_ids": list(selected_queries),
        "transitions": transitions,
        "observations": observation_labels,
    }


def analyze_world_quotient(
    world: str,
    n_symbols: int,
    *,
    query_ids: Sequence[str] | None = None,
    temperature: float = 1.0,
    feature_depth: int = 2,
    seed: int = 17,
) -> dict[str, Any]:
    """Convenience entry point used by the offline command-line runner."""

    system = world_transition_system(world, query_ids=query_ids)
    fitted = fit_soft_quotient(
        system["transitions"],
        system["observations"],
        n_symbols,
        temperature=temperature,
        feature_depth=feature_depth,
        seed=seed,
    )
    return {
        "world": system["world"],
        "state_count": len(system["states"]),
        "operators": system["operators"],
        "query_ids": system["query_ids"],
        "n_symbols": int(n_symbols),
        "result": fitted,
    }


def json_ready(value: Any) -> Any:
    """Recursively convert analysis results to JSON-native values."""

    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Mapping):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_ready(item) for item in value]
    return value
