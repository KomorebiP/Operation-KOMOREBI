"""Projective holonomy and decision-cone diagnostics.

This is an exploratory, checkpoint-agnostic prototype for the Neuralese
v0.3.1 design.  It intentionally contains no checkpoint paths, episode seeds,
or learned endpoint values.  The functions operate on explicit NumPy arrays so
the same code can be tested on transparent controls before a learned run is
frozen.

Matrix convention
-----------------
For a word ``(g1, ..., gk)`` the recurrent state is updated left to right,
and the corresponding column-vector product is

    M[gk] @ ... @ M[g1].

All normalizations divide by a strictly positive norm.  Consequently they do
not change a positive ray or the sign of any downstream linear decision
margin.  A relation product can therefore replace its generator sequence for
ray and hard-cone calculations, provided every intermediate generator update
is nonzero.  The implementation still checks generator-wise and relation-block
executions separately when requested.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Sequence

import numpy as np


DEFAULT_MINIMUM_NORM = 1e-12


class NumericalRayError(ArithmeticError):
    """Raised when a projective update does not define a finite positive ray."""


def _strict_int(name: str, value: Any) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(
        value, (int, np.integer)
    ):
        raise ValueError(f"{name} must be an integer")
    return int(value)


def _nonnegative_finite_float(name: str, value: Any) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a finite nonnegative number")
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"{name} must be a finite nonnegative number"
        ) from error
    if not np.isfinite(result) or result < 0.0:
        raise ValueError(f"{name} must be a finite nonnegative number")
    return result


def _strict_word(word: Iterable[int], operator_count: int) -> tuple[int, ...]:
    result: list[int] = []
    for raw_generator in word:
        generator = _strict_int("generator", raw_generator)
        if generator < 0 or generator >= operator_count:
            raise ValueError("word contains an invalid generator")
        result.append(generator)
    return tuple(result)


def _as_real_matrix(name: str, value: np.ndarray) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] != array.shape[1]:
        raise ValueError(f"{name} must be a square matrix")
    if not np.isfinite(array).all():
        raise NumericalRayError(f"{name} contains a non-finite value")
    return array


def _as_operator_family(codes: np.ndarray) -> np.ndarray:
    array = np.asarray(codes, dtype=np.float64)
    if array.ndim != 3 or array.shape[1] != array.shape[2] or array.shape[0] < 1:
        raise ValueError("codes must have shape (operators, dimension, dimension)")
    if not np.isfinite(array).all():
        raise NumericalRayError("codes contain a non-finite value")
    return array


def _as_semantic_maps(
    semantic_maps: np.ndarray,
    operator_count: int | None = None,
    *,
    require_permutations: bool = False,
) -> np.ndarray:
    maps = np.asarray(semantic_maps)
    if maps.ndim != 2 or not np.issubdtype(maps.dtype, np.integer):
        raise ValueError("semantic_maps must be an integer array (operators, states)")
    if operator_count is not None and maps.shape[0] != operator_count:
        raise ValueError("semantic map operator count does not match learned operators")
    if maps.shape[1] < 1 or np.any(maps < 0) or np.any(maps >= maps.shape[1]):
        raise ValueError("semantic maps contain a state outside their domain")
    if require_permutations:
        expected = np.arange(maps.shape[1])
        if any(not np.array_equal(np.sort(row), expected) for row in maps):
            raise ValueError("relation spectroscopy requires permutation semantic maps")
    return maps.astype(np.int64, copy=False)


def _as_semantic_labels(semantic: np.ndarray, state_count: int) -> np.ndarray:
    labels = np.asarray(semantic)
    if not np.issubdtype(labels.dtype, np.integer):
        raise ValueError("semantic labels must have an integer dtype")
    if np.any(labels < 0) or np.any(labels >= state_count):
        raise ValueError("semantic label is outside the map domain")
    return labels.astype(np.int64, copy=False)


def normalize_positive_ray(
    states: np.ndarray, minimum_norm: float = DEFAULT_MINIMUM_NORM
) -> np.ndarray:
    """Normalize the last axis without identifying ``h`` and ``-h``."""

    minimum_norm = _nonnegative_finite_float("minimum_norm", minimum_norm)
    array = np.asarray(states, dtype=np.float64)
    if array.ndim < 1 or not np.isfinite(array).all():
        raise NumericalRayError("ray state is empty or non-finite")
    norms = np.linalg.norm(array, axis=-1, keepdims=True)
    if not np.isfinite(norms).all():
        raise NumericalRayError("ray norm is non-finite")
    minimum = float(np.min(norms))
    if minimum <= minimum_norm:
        raise NumericalRayError(
            f"ray norm {minimum:.17g} is at or below {minimum_norm:.17g}"
        )
    result = array / norms
    if not np.isfinite(result).all():
        raise NumericalRayError("normalized ray is non-finite")
    return result


def positive_ray_geometry(left: np.ndarray, right: np.ndarray) -> dict[str, np.ndarray]:
    """Return positive-ray L2 distance and angle for paired states."""

    left_unit = normalize_positive_ray(left)
    right_unit = normalize_positive_ray(right)
    if left_unit.shape != right_unit.shape:
        raise ValueError("paired ray arrays must have identical shapes")
    unit_l2 = np.linalg.norm(left_unit - right_unit, axis=-1)
    return {
        "unit_l2": unit_l2,
        "angle": 2.0 * np.arcsin(np.clip(unit_l2 / 2.0, 0.0, 1.0)),
    }


def word_product(codes: np.ndarray, word: Iterable[int]) -> np.ndarray:
    """Return ``M[gk] ... M[g1]`` for a left-to-right generator word."""

    operators = _as_operator_family(codes)
    result = np.eye(operators.shape[1], dtype=np.float64)
    for generator in _strict_word(word, operators.shape[0]):
        result = operators[generator] @ result
    return result


def positive_rescaled_word_product(
    codes: np.ndarray, word: Iterable[int]
) -> np.ndarray:
    """Return a stable positive scalar multiple of a temporal word product."""

    operators = _as_operator_family(codes)
    result = np.eye(operators.shape[1], dtype=np.float64)
    result /= np.linalg.norm(result, ord="fro")
    for generator in _strict_word(word, operators.shape[0]):
        result = operators[generator] @ result
        scale = float(np.linalg.norm(result, ord="fro"))
        if scale == 0.0 or not np.isfinite(scale):
            raise NumericalRayError("rescaled word product vanished or became non-finite")
        result /= scale
    return result


def apply_word_ray(
    codes: np.ndarray,
    states: np.ndarray,
    word: Iterable[int],
    minimum_norm: float = DEFAULT_MINIMUM_NORM,
) -> np.ndarray:
    """Execute and normalize after every generator application."""

    operators = _as_operator_family(codes)
    state = normalize_positive_ray(states, minimum_norm)
    for generator in _strict_word(word, operators.shape[0]):
        state = np.einsum("ij,...j->...i", operators[generator], state)
        state = normalize_positive_ray(state, minimum_norm)
    return state


def apply_relation_blocks(
    relation_product: np.ndarray,
    states: np.ndarray,
    repeat_count: int,
    minimum_norm: float = DEFAULT_MINIMUM_NORM,
) -> np.ndarray:
    """Apply a relation product repeatedly, normalizing after each block.

    This is numerically preferable to forming an unscaled high power.  It is
    positive-ray equivalent to generator-wise execution in exact arithmetic.
    """

    matrix = _as_real_matrix("relation_product", relation_product)
    repeat_count = _strict_int("repeat_count", repeat_count)
    if repeat_count < 0:
        raise ValueError("repeat_count must be nonnegative")
    state = normalize_positive_ray(states, minimum_norm)
    matrix_scale = float(np.linalg.norm(matrix, ord="fro"))
    if matrix_scale == 0.0 or not np.isfinite(matrix_scale):
        raise NumericalRayError("relation product does not define a matrix ray")
    # The raw composite contains radial contractions already discarded by the
    # generator-level recurrence. Remove its common positive scale rather than
    # applying the registered state threshold to an incommensurate quantity.
    matrix = matrix / matrix_scale
    for _ in range(repeat_count):
        state = np.einsum("ij,...j->...i", matrix, state)
        if not np.isfinite(state).all():
            raise NumericalRayError("relation-block orbit became non-finite")
        norms = np.linalg.norm(state, axis=-1, keepdims=True)
        if not np.isfinite(norms).all() or np.any(norms == 0.0):
            raise NumericalRayError("relation-block orbit reached a zero ray")
        state = state / norms
    return state


def positive_rescaled_matrix_power(matrix: np.ndarray, exponent: int) -> np.ndarray:
    """Return a positive scalar multiple of ``matrix**exponent`` stably.

    A common positive scale is projectively irrelevant.  Removing it after each
    matrix multiplication prevents the radial contraction of a learned
    relation product from underflowing before its anisotropy can be analyzed.
    This matrix-level routine intentionally does not apply a state-norm guard.
    """

    value = _as_real_matrix("matrix", matrix)
    exponent = _strict_int("exponent", exponent)
    if exponent < 0:
        raise ValueError("exponent must be nonnegative")
    base_norm = float(np.linalg.norm(value, ord="fro"))
    if base_norm == 0.0 or not np.isfinite(base_norm):
        raise NumericalRayError("zero or non-finite matrix has no stable power ray")
    base = value / base_norm
    result = np.eye(value.shape[0], dtype=np.float64)
    result /= np.linalg.norm(result, ord="fro")
    for _ in range(exponent):
        result = base @ result
        scale = float(np.linalg.norm(result, ord="fro"))
        if scale == 0.0 or not np.isfinite(scale):
            raise NumericalRayError(
                "rescaled matrix power vanished or became non-finite"
            )
        result /= scale
    return result


def compare_generator_and_block_execution(
    codes: np.ndarray,
    states: np.ndarray,
    relation_word: Sequence[int],
    repeat_count: int,
    minimum_norm: float = DEFAULT_MINIMUM_NORM,
) -> dict[str, Any]:
    """Check the exact projective reduction used by the spectroscopy."""

    repeat_count = _strict_int("repeat_count", repeat_count)
    if repeat_count < 0:
        raise ValueError("repeat_count must be nonnegative")
    relation_word = _strict_word(relation_word, _as_operator_family(codes).shape[0])
    by_generators = normalize_positive_ray(states, minimum_norm)
    for _ in range(repeat_count):
        by_generators = apply_word_ray(
            codes, by_generators, relation_word, minimum_norm
        )
    product_matrix = word_product(codes, relation_word)
    by_blocks = apply_relation_blocks(
        product_matrix, states, repeat_count, minimum_norm
    )
    geometry = positive_ray_geometry(by_generators, by_blocks)
    return {
        "generator_state": by_generators,
        "block_state": by_blocks,
        "maximum_unit_l2": float(np.max(geometry["unit_l2"])),
        "maximum_positive_ray_angle": float(np.max(geometry["angle"])),
    }


def nearest_positive_scalar_identity(matrix: np.ndarray) -> dict[str, Any]:
    """Frobenius-best positive scalar identity approximation.

    The unconstrained minimizer of ``||P - alpha I||_F`` is
    ``trace(P) / d``.  If that number is positive it is also the unique
    minimizer over ``alpha > 0``.  Otherwise the strict-positive problem has no
    minimizer: its infimum occurs as ``alpha`` approaches zero from above.  We
    report that boundary honestly instead of silently calling zero positive.
    """

    value = _as_real_matrix("matrix", matrix)
    dimension = value.shape[0]
    unconstrained_alpha = float(np.trace(value) / dimension)
    attained = unconstrained_alpha > 0.0
    alpha_at_infimum = unconstrained_alpha if attained else 0.0
    residual = value - alpha_at_infimum * np.eye(dimension)
    residual_norm = float(np.linalg.norm(residual, ord="fro"))
    matrix_norm = float(np.linalg.norm(value, ord="fro"))
    if matrix_norm <= 0.0:
        raise NumericalRayError("zero matrix does not define projective dynamics")
    return {
        "unconstrained_alpha": unconstrained_alpha,
        "positive_alpha_minimizer_attained": bool(attained),
        "alpha_or_boundary": float(alpha_at_infimum),
        "frobenius_residual": residual_norm,
        "relative_frobenius_residual": residual_norm / matrix_norm,
        "matrix_frobenius_norm": matrix_norm,
    }


def eigenspectrum(matrix: np.ndarray, relative_tolerance: float = 1e-10) -> dict[str, Any]:
    """Describe spectral projective behavior without overclaiming convergence."""

    relative_tolerance = _nonnegative_finite_float(
        "relative_tolerance", relative_tolerance
    )
    value = _as_real_matrix("matrix", matrix)
    eigenvalues, eigenvectors = np.linalg.eig(value)
    order = np.argsort(-np.abs(eigenvalues), kind="stable")
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    moduli = np.abs(eigenvalues)
    radius = float(moduli[0])
    if radius <= 0.0:
        raise NumericalRayError("nilpotent spectrum needs orbit-wise analysis")
    second = float(moduli[1]) if moduli.size > 1 else 0.0
    # This threshold must scale with the matrix. Using max(1, radius) would
    # change the classification after a harmless positive scalar rescaling.
    threshold = float(relative_tolerance) * radius
    unique_dominant = bool(radius - second > threshold)
    dominant = eigenvalues[0]
    dominant_real = bool(abs(float(np.imag(dominant))) <= threshold)

    if not unique_dominant:
        classification = "no_unique_dominant_modulus"
    elif not dominant_real:
        classification = "complex_dominant_inconsistent_with_real_unique_pair"
    elif float(np.real(dominant)) > 0.0:
        classification = "candidate_positive_ray_fixed_attractor"
    else:
        classification = "candidate_positive_ray_two_cycle"

    try:
        eigenvector_condition = float(np.linalg.cond(eigenvectors))
    except np.linalg.LinAlgError:
        eigenvector_condition = float("inf")

    singular_values = np.linalg.svd(value, compute_uv=False)
    normalized_singular_values = singular_values / singular_values[0]
    matrix_frobenius = float(np.linalg.norm(value, ord="fro"))
    departure_squared = max(
        0.0,
        matrix_frobenius * matrix_frobenius
        - float(np.sum(np.square(moduli))),
    )
    henrici_departure = float(np.sqrt(departure_squared) / matrix_frobenius)
    commutator = value.T @ value - value @ value.T
    normalized_commutator = float(
        np.linalg.norm(commutator, ord="fro") / (matrix_frobenius**2)
    )

    entries = [
        {
            "real": float(np.real(eigenvalue)),
            "imag": float(np.imag(eigenvalue)),
            "modulus": float(abs(eigenvalue)),
            "phase": float(np.angle(eigenvalue)),
            "normalized_real": float(np.real(eigenvalue / radius)),
            "normalized_imag": float(np.imag(eigenvalue / radius)),
            "normalized_modulus": float(abs(eigenvalue) / radius),
        }
        for eigenvalue in eigenvalues
    ]
    return {
        "eigenvalues": entries,
        "spectral_radius": radius,
        "second_modulus": second,
        "dominant_to_second_modulus_ratio": (
            None if second == 0.0 else radius / second
        ),
        "second_modulus_is_zero": bool(second == 0.0),
        "unique_dominant_modulus": unique_dominant,
        "dominant_is_real": dominant_real,
        "projective_asymptotic_classification": classification,
        "eigenvector_condition_number": (
            eigenvector_condition if np.isfinite(eigenvector_condition) else None
        ),
        "normalized_singular_values": normalized_singular_values.tolist(),
        "henrici_departure_from_normality": henrici_departure,
        "normalized_normal_commutator": normalized_commutator,
        "caveat": (
            "A spectral candidate is not an orbit-wise certificate. Initial states "
            "can have zero dominant left-eigenvector component, tied spectra can "
            "still have Jordan drift, and nonnormal transients can dominate finite depth."
        ),
    }


def semantic_word_action(
    semantic_maps: np.ndarray, semantic: np.ndarray, word: Iterable[int]
) -> np.ndarray:
    """Apply discrete semantic maps with the same word convention."""

    maps = _as_semantic_maps(semantic_maps)
    state = _as_semantic_labels(semantic, maps.shape[1]).copy()
    for generator in _strict_word(word, maps.shape[0]):
        state = maps[generator, state]
    return state


def decoder_facet_margins(
    decoder: np.ndarray, states: np.ndarray, targets: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Return every target-vs-competitor facet margin and target margin."""

    readout = np.asarray(decoder, dtype=np.float64)
    hidden = np.asarray(states, dtype=np.float64)
    raw_target = np.asarray(targets)
    if not np.issubdtype(raw_target.dtype, np.integer):
        raise ValueError("targets must have an integer dtype")
    target = raw_target.astype(np.int64, copy=False)
    if readout.ndim != 2 or hidden.shape[-1] != readout.shape[1]:
        raise ValueError("decoder and hidden dimensions are incompatible")
    if hidden.shape[:-1] != target.shape:
        raise ValueError("targets must match the hidden leading dimensions")
    if not np.isfinite(readout).all() or not np.isfinite(hidden).all():
        raise NumericalRayError("decoder margin input is non-finite")
    if np.any(target < 0) or np.any(target >= readout.shape[0]):
        raise ValueError("target is outside the decoder label domain")
    logits = np.einsum("...d,kd->...k", hidden, readout)
    selected = np.take_along_axis(logits, target[..., None], axis=-1)[..., 0]
    facets = selected[..., None] - logits
    competitors = np.arange(readout.shape[0])
    other = np.where(competitors == target[..., None], np.inf, facets)
    target_margin = np.min(other, axis=-1)
    return facets, target_margin


def exact_words(operator_count: int, length: int) -> tuple[tuple[int, ...], ...]:
    operator_count = _strict_int("operator_count", operator_count)
    length = _strict_int("length", length)
    if operator_count < 1 or length < 0:
        raise ValueError("operator_count must be positive and length nonnegative")
    return tuple(product(range(operator_count), repeat=length))


@dataclass(frozen=True)
class _FirstEvent:
    horizon: int
    suffix_index: int
    suffix: tuple[int, ...]
    prediction: int
    target: int
    target_margin: float
    active_competitor: int
    pulled_back_facet_unit_normal: tuple[float, ...] | None
    normalized_pulled_back_facet_margin: float | None
    signed_spherical_boundary_distance: float | None


def _event_dict(event: _FirstEvent | None) -> dict[str, Any] | None:
    if event is None:
        return None
    return {
        "horizon": event.horizon,
        "suffix_index": event.suffix_index,
        "suffix": list(event.suffix),
        "prediction": event.prediction,
        "target": event.target,
        "target_margin": event.target_margin,
        "active_competitor": event.active_competitor,
        "pulled_back_facet_unit_normal": (
            None
            if event.pulled_back_facet_unit_normal is None
            else list(event.pulled_back_facet_unit_normal)
        ),
        "normalized_pulled_back_facet_margin": (
            event.normalized_pulled_back_facet_margin
        ),
        "signed_spherical_boundary_distance": (
            event.signed_spherical_boundary_distance
        ),
    }


def decision_cone_survival(
    codes: np.ndarray,
    semantic_maps: np.ndarray,
    decoder: np.ndarray,
    states: np.ndarray,
    semantic: np.ndarray,
    maximum_suffix_horizon: int,
    *,
    baseline_states: np.ndarray | None = None,
    minimum_norm: float = DEFAULT_MINIMUM_NORM,
) -> dict[str, Any]:
    """Audit exact suffix decision cones for a batch of positive rays.

    The returned first-failure event includes the pulled-back active facet

        M_v.T @ (decoder[target] - decoder[competitor]),

    whose sign at the pre-suffix state is identical to the final normalized
    margin sign.  ``baseline_states`` optionally adds the v0.3-style first
    decision-disagreement (reveal) horizon.
    """

    operators = _as_operator_family(codes)
    maps = _as_semantic_maps(semantic_maps, operators.shape[0])
    readout = np.asarray(decoder, dtype=np.float64)
    maximum_suffix_horizon = _strict_int(
        "maximum_suffix_horizon", maximum_suffix_horizon
    )
    if maximum_suffix_horizon < 0:
        raise ValueError("maximum_suffix_horizon must be nonnegative")
    if maps.shape != (operators.shape[0], readout.shape[0]):
        raise ValueError("semantic maps must match operators and decoder labels")
    if operators.shape[1] != readout.shape[1]:
        raise ValueError("operator and decoder hidden dimensions differ")

    initial = normalize_positive_ray(states, minimum_norm)
    if initial.ndim == 1:
        initial = initial[None, :]
    labels = _as_semantic_labels(semantic, maps.shape[1])
    if labels.ndim != 1:
        raise ValueError("semantic labels must be a one-dimensional array")
    if initial.shape != (labels.size, operators.shape[1]):
        raise ValueError("states and semantic labels have incompatible shapes")

    baseline_initial = None
    if baseline_states is not None:
        baseline_initial = normalize_positive_ray(baseline_states, minimum_norm)
        if baseline_initial.ndim == 1:
            baseline_initial = baseline_initial[None, :]
        if baseline_initial.shape != initial.shape:
            raise ValueError("baseline states must match analyzed states")

    case_count = initial.shape[0]
    first_failure: list[_FirstEvent | None] = [None] * case_count
    first_reveal: list[dict[str, Any] | None] = [None] * case_count
    shell_records: list[dict[str, Any]] = []

    current = initial[:, None, :]
    current_labels = labels[:, None]
    baseline_current = None if baseline_initial is None else baseline_initial[:, None, :]

    for horizon in range(maximum_suffix_horizon + 1):
        words = exact_words(operators.shape[0], horizon)
        logits = np.einsum("bsd,kd->bsk", current, readout)
        predictions = np.argmax(logits, axis=-1)
        _, margins = decoder_facet_margins(readout, current, current_labels)
        strict = (predictions == current_labels) & (margins > 0.0)

        if baseline_current is not None:
            baseline_predictions = np.argmax(
                np.einsum("bsd,kd->bsk", baseline_current, readout), axis=-1
            )
            reveals = predictions != baseline_predictions
        else:
            reveals = np.zeros_like(strict)

        for case_index in range(case_count):
            if first_reveal[case_index] is None and np.any(reveals[case_index]):
                suffix_index = int(np.argmax(reveals[case_index]))
                first_reveal[case_index] = {
                    "horizon": int(horizon),
                    "suffix_index": suffix_index,
                    "suffix": list(words[suffix_index]),
                    "prediction": int(predictions[case_index, suffix_index]),
                    "baseline_prediction": int(
                        baseline_predictions[case_index, suffix_index]
                    ),
                }

            if first_failure[case_index] is None and np.any(~strict[case_index]):
                suffix_index = int(np.argmax(~strict[case_index]))
                suffix = words[suffix_index]
                target = int(current_labels[case_index, suffix_index])
                prediction = int(predictions[case_index, suffix_index])
                competing_logits = logits[case_index, suffix_index].copy()
                competing_logits[target] = -np.inf
                competitor = int(np.argmax(competing_logits))
                suffix_matrix = positive_rescaled_word_product(operators, suffix)
                facet = readout[target] - readout[competitor]
                effective_normal = suffix_matrix.T @ facet
                facet_norm = float(np.linalg.norm(effective_normal))
                if facet_norm > 0.0:
                    effective_unit_normal = effective_normal / facet_norm
                    normalized_facet_margin = float(
                        effective_unit_normal @ initial[case_index]
                        / np.linalg.norm(initial[case_index])
                    )
                    spherical_distance = float(
                        np.arcsin(np.clip(normalized_facet_margin, -1.0, 1.0))
                    )
                else:
                    effective_unit_normal = None
                    normalized_facet_margin = None
                    spherical_distance = None
                first_failure[case_index] = _FirstEvent(
                    horizon=int(horizon),
                    suffix_index=suffix_index,
                    suffix=suffix,
                    prediction=prediction,
                    target=target,
                    target_margin=float(margins[case_index, suffix_index]),
                    active_competitor=competitor,
                    pulled_back_facet_unit_normal=(
                        None
                        if effective_unit_normal is None
                        else tuple(map(float, effective_unit_normal))
                    ),
                    normalized_pulled_back_facet_margin=normalized_facet_margin,
                    signed_spherical_boundary_distance=spherical_distance,
                )

        shell_records.append(
            {
                "horizon": int(horizon),
                "suffix_count": len(words),
                "decision_count": int(strict.size),
                "strict_correct_count": int(np.sum(strict)),
                "minimum_target_margin": float(np.min(margins)),
                "reveal_count": int(np.sum(reveals)),
            }
        )

        if horizon < maximum_suffix_horizon:
            expanded = np.einsum("oij,bsj->bsoi", operators, current)
            current = expanded.reshape(
                case_count, current.shape[1] * operators.shape[0], operators.shape[1]
            )
            current = normalize_positive_ray(current, minimum_norm)
            current_labels = np.stack(
                [maps[g, current_labels] for g in range(operators.shape[0])], axis=2
            ).reshape(case_count, -1)
            if baseline_current is not None:
                baseline_expanded = np.einsum(
                    "oij,bsj->bsoi", operators, baseline_current
                )
                baseline_current = baseline_expanded.reshape(
                    case_count,
                    baseline_current.shape[1] * operators.shape[0],
                    operators.shape[1],
                )
                baseline_current = normalize_positive_ray(
                    baseline_current, minimum_norm
                )

    return {
        "case_count": case_count,
        "maximum_suffix_horizon": int(maximum_suffix_horizon),
        "shells": shell_records,
        "first_failure": [_event_dict(event) for event in first_failure],
        "first_reveal": first_reveal,
        "all_cases_survive": all(event is None for event in first_failure),
    }


def relation_spectroscopy(
    codes: np.ndarray,
    semantic_maps: np.ndarray,
    decoder: np.ndarray,
    base_states: np.ndarray,
    base_semantic: np.ndarray,
    relation_word: Sequence[int],
    repeat_count: int,
    maximum_suffix_horizon: int,
    *,
    verify_generator_execution: bool = True,
    minimum_norm: float = DEFAULT_MINIMUM_NORM,
) -> dict[str, Any]:
    """Combine relation-product, spectrum, and suffix-cone diagnostics."""

    operators = _as_operator_family(codes)
    maps = _as_semantic_maps(
        semantic_maps, operators.shape[0], require_permutations=True
    )
    relation_word = _strict_word(relation_word, operators.shape[0])
    repeat_count = _strict_int("repeat_count", repeat_count)
    if repeat_count < 0:
        raise ValueError("repeat_count must be nonnegative")
    maximum_suffix_horizon = _strict_int(
        "maximum_suffix_horizon", maximum_suffix_horizon
    )
    product_matrix = word_product(operators, relation_word)
    repeated_product_matrix = positive_rescaled_matrix_power(
        product_matrix, repeat_count
    )
    labels = _as_semantic_labels(base_semantic, maps.shape[1])
    if labels.ndim != 1:
        raise ValueError("base_semantic must be a one-dimensional label array")
    action = semantic_word_action(
        maps, np.arange(maps.shape[1]), relation_word
    )
    identity_action = bool(
        np.array_equal(action, np.arange(maps.shape[1]))
    )
    repeated_action = np.arange(maps.shape[1], dtype=np.int64)
    for _ in range(repeat_count):
        repeated_action = action[repeated_action]
    repeated_identity_action = bool(
        np.array_equal(repeated_action, np.arange(maps.shape[1]))
    )
    loop_labels = repeated_action[labels]
    loop_states = apply_relation_blocks(
        product_matrix, base_states, repeat_count, minimum_norm
    )

    execution_agreement = None
    if verify_generator_execution:
        comparison = compare_generator_and_block_execution(
            operators,
            base_states,
            relation_word,
            repeat_count,
            minimum_norm,
        )
        execution_agreement = {
            "maximum_unit_l2": comparison["maximum_unit_l2"],
            "maximum_positive_ray_angle": comparison[
                "maximum_positive_ray_angle"
            ],
        }
        # Reproduce hard gates from the registered generator-level path. The
        # composite state is used only after its ray has been checked against
        # this execution.
        loop_states = comparison["generator_state"]

    cone = decision_cone_survival(
        operators,
        maps,
        decoder,
        loop_states,
        loop_labels,
        maximum_suffix_horizon,
        baseline_states=base_states,
        minimum_norm=minimum_norm,
    )
    return {
        "relation_word": list(relation_word),
        "repeat_count": repeat_count,
        "identity_semantic_action": identity_action,
        "semantic_action": action.tolist(),
        "repeated_identity_semantic_action": repeated_identity_action,
        "repeated_semantic_action": repeated_action.tolist(),
        "nearest_positive_scalar_identity": nearest_positive_scalar_identity(
            product_matrix
        ),
        "eigenspectrum": eigenspectrum(product_matrix),
        "repeated_composite": {
            "positive_rescaled_power": repeated_product_matrix.tolist(),
            "nearest_positive_scalar_identity": nearest_positive_scalar_identity(
                repeated_product_matrix
            ),
            "eigenspectrum": eigenspectrum(repeated_product_matrix),
        },
        "generator_vs_relation_block": execution_agreement,
        "decision_cone_survival": cone,
    }


def compare_with_published_witness_record(
    cone_result: dict[str, Any], published_record: dict[str, Any], margin_atol: float = 1e-11
) -> dict[str, Any]:
    """Compare recomputed events with a v0.3-format published witness record.

    This helper is intended for the post-freeze learned run.  It performs no
    checkpoint loading and cannot expose learned values by itself.
    """

    margin_atol = _nonnegative_finite_float("margin_atol", margin_atol)
    computed_reveals = {
        index: event
        for index, event in enumerate(cone_result["first_reveal"])
        if event is not None
    }
    expected_reveal_list = published_record.get("hard_counterexamples", [])
    expected_reveals = {
        int(event["case_index"]): event
        for event in expected_reveal_list
    }
    reveal_ids_unique = len(expected_reveals) == len(expected_reveal_list)
    reveal_keys_equal = set(computed_reveals) == set(expected_reveals)
    reveal_event_equal = reveal_ids_unique and reveal_keys_equal and all(
        computed_reveals[index]["horizon"]
        == expected_reveals[index]["first_reveal_horizon"]
        and computed_reveals[index]["suffix_index"]
        == expected_reveals[index]["first_revealing_suffix_index"]
        and computed_reveals[index]["suffix"]
        == expected_reveals[index]["first_revealing_suffix"]
        for index in expected_reveals
    )

    maximum_horizon = _strict_int(
        "maximum_suffix_horizon", cone_result["maximum_suffix_horizon"]
    )
    computed_histogram = {
        str(horizon): sum(
            event is not None and event["horizon"] == horizon
            for event in cone_result["first_reveal"]
        )
        for horizon in range(maximum_horizon + 1)
    }
    computed_histogram[f">{maximum_horizon}"] = sum(
        event is None for event in cone_result["first_reveal"]
    )
    reveal_counts_equal = (
        published_record.get("hard_counterexample_count") == len(computed_reveals)
        and published_record.get("first_reveal_histogram") == computed_histogram
    )

    computed_failures = {
        index: event
        for index, event in enumerate(cone_result["first_failure"])
        if event is not None
    }
    expected_failure_list = published_record.get(
        "identity_semantic_or_margin_failures", []
    )
    expected_failures = {
        int(event["case_index"]): event
        for event in expected_failure_list
    }
    failure_ids_unique = len(expected_failures) == len(expected_failure_list)
    failure_keys_equal = set(computed_failures) == set(expected_failures)
    failure_event_equal = failure_ids_unique and failure_keys_equal and all(
        computed_failures[index]["horizon"]
        == expected_failures[index]["first_failure_horizon"]
        and computed_failures[index]["suffix_index"]
        == expected_failures[index]["first_failure_suffix_index"]
        and computed_failures[index]["suffix"]
        == expected_failures[index]["first_failure_suffix"]
        and (computed_failures[index]["prediction"] == computed_failures[index]["target"])
        == expected_failures[index]["argmax_correct"]
        and (
            "nonpositive_margin"
            if computed_failures[index]["prediction"]
            == computed_failures[index]["target"]
            else "wrong_argmax"
        )
        == expected_failures[index]["failure_kind"]
        and abs(
            computed_failures[index]["target_margin"]
            - expected_failures[index]["target_margin"]
        )
        <= margin_atol
        for index in expected_failures
    )
    failure_counts_equal = (
        published_record.get("identity_semantic_or_margin_failure_count")
        == len(computed_failures)
    )
    exact_agreement = bool(
        reveal_event_equal
        and reveal_counts_equal
        and failure_event_equal
        and failure_counts_equal
    )
    return {
        "comparison_scope": (
            "case IDs, first horizons, suffix indices and words, failure kinds, "
            "failure margins, registered counts, and first-reveal histogram"
        ),
        "published_reveal_case_ids_unique": reveal_ids_unique,
        "reveal_case_sets_equal": reveal_keys_equal,
        "reveal_events_equal": reveal_event_equal,
        "reveal_counts_and_histogram_equal": reveal_counts_equal,
        "published_failure_case_ids_unique": failure_ids_unique,
        "failure_case_sets_equal": failure_keys_equal,
        "failure_events_and_margins_equal": failure_event_equal,
        "failure_counts_equal": failure_counts_equal,
        "exact_agreement": exact_agreement,
    }


__all__ = [
    "DEFAULT_MINIMUM_NORM",
    "NumericalRayError",
    "apply_relation_blocks",
    "apply_word_ray",
    "compare_generator_and_block_execution",
    "compare_with_published_witness_record",
    "decision_cone_survival",
    "decoder_facet_margins",
    "eigenspectrum",
    "exact_words",
    "nearest_positive_scalar_identity",
    "normalize_positive_ray",
    "positive_ray_geometry",
    "positive_rescaled_matrix_power",
    "positive_rescaled_word_product",
    "relation_spectroscopy",
    "semantic_word_action",
    "word_product",
]
