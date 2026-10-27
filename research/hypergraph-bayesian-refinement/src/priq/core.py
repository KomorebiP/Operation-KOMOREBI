"""Finite reference implementation for interaction quotients resolved by projectors.

Tensor convention:
A multilinear map of order m, A : R^n x ... x R^n -> R^p, is represented by
an array with shape ``(p, n, ..., n)``.  Axis 0 is the output axis and axes
1..m are the ordered input slots.

The implementation is intentionally dense and explicit.  It is meant for
small certificates attached to theorems, not production workloads at large scale.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import exp
from typing import Callable, Iterable, Sequence

import numpy as np

Array = np.ndarray


class PRIQError(ValueError):
    """Raised when a finite PRIQ object violates its required shape contract."""


def _as_float_array(value: Array | Sequence[float], *, ndim: int | None = None) -> Array:
    arr = np.asarray(value, dtype=float)
    if ndim is not None and arr.ndim != ndim:
        raise PRIQError(f"expected an array with ndim={ndim}, received shape {arr.shape}")
    if not np.all(np.isfinite(arr)):
        raise PRIQError("all entries must be finite")
    return arr


def block_sum_matrix(packet_map: Sequence[int], coarse_count: int | None = None) -> Array:
    """Return the block sum aggregation ``C`` determined by a packet map.

    ``packet_map[j]`` is the coarse packet containing fine coordinate ``j``.
    The returned matrix satisfies ``(C @ x)[a] = sum_{j:pi(j)=a} x[j]``.
    """

    pi = np.asarray(packet_map, dtype=int)
    if pi.ndim != 1 or pi.size == 0:
        raise PRIQError("packet_map must be a nonempty sequence of one dimension")
    if np.any(pi < 0):
        raise PRIQError("packet labels must be nonnegative")
    q = int(pi.max()) + 1 if coarse_count is None else int(coarse_count)
    if q <= int(pi.max()):
        raise PRIQError("coarse_count does not contain every packet label")
    C = np.zeros((q, pi.size), dtype=float)
    C[pi, np.arange(pi.size)] = 1.0
    if np.any(C.sum(axis=1) == 0):
        raise PRIQError("every coarse packet must have a nonempty fine fiber")
    return C


def averaging_section(packet_map: Sequence[int], coarse_count: int | None = None) -> Array:
    """Return the canonical right inverse ``E`` with equal weights in each block."""

    pi = np.asarray(packet_map, dtype=int)
    C = block_sum_matrix(pi, coarse_count)
    q, n = C.shape
    E = np.zeros((n, q), dtype=float)
    for a in range(q):
        members = np.flatnonzero(pi == a)
        E[members, a] = 1.0 / members.size
    if not np.allclose(C @ E, np.eye(q), atol=1e-14, rtol=1e-14):
        raise PRIQError("failed to construct a right inverse")
    return E


def kernel_basis(C: Array, *, rtol: float = 1e-12) -> Array:
    """Compute an orthonormal basis for ``ker(C)`` using an SVD."""

    C = _as_float_array(C, ndim=2)
    _, singular, vh = np.linalg.svd(C, full_matrices=True)
    if singular.size == 0:
        return np.eye(C.shape[1])
    threshold = rtol * max(C.shape) * singular.max(initial=0.0)
    rank = int(np.sum(singular > threshold))
    return vh[rank:].T.copy()


def validate_tensor(tensor: Array) -> tuple[int, int, int]:
    """Validate a multilinear tensor whose input dimensions are equal.

    Returns ``(order, output_dimension, input_dimension)``.
    """

    A = _as_float_array(tensor)
    if A.ndim < 2:
        raise PRIQError("a multilinear tensor must have one output and at least one input axis")
    m = A.ndim - 1
    input_dims = A.shape[1:]
    if len(set(input_dims)) != 1:
        raise PRIQError(f"all input dimensions must agree, received {input_dims}")
    return m, A.shape[0], input_dims[0]


def transform_tensor(
    tensor: Array,
    output_map: Array,
    input_maps: Sequence[Array],
) -> Array:
    """Apply a linear map to the output and one linear map to every input slot.

    If ``tensor`` has coefficients ``A[o,i1,...,im]``, ``output_map`` has shape
    ``(O,o)``, and input map ``r`` has shape ``(ir,Ir)``, the returned tensor is

    ``B[O,I1,...,Im] = output_map[O,o] A[o,i1,...,im] Π_r input_map_r[ir,Ir]``.
    """

    A = _as_float_array(tensor)
    if A.ndim < 2:
        raise PRIQError("tensor must have at least one input slot")
    m = A.ndim - 1
    if len(input_maps) != m:
        raise PRIQError(f"expected {m} input maps, received {len(input_maps)}")
    O = _as_float_array(output_map, ndim=2)
    if O.shape[1] != A.shape[0]:
        raise PRIQError("output_map has an incompatible source output dimension")

    # NumPy's integer subscript form of einsum avoids fragile generated strings.
    # It supports every modest tensor order used by this package.
    old_output = 0
    old_inputs = list(range(1, m + 1))
    new_output = m + 1
    new_inputs = list(range(m + 2, 2 * m + 2))

    operands: list[object] = [A, [old_output, *old_inputs], O, [new_output, old_output]]
    for axis, (M, old_label, new_label) in enumerate(
        zip(input_maps, old_inputs, new_inputs, strict=True), start=1
    ):
        M_arr = _as_float_array(M, ndim=2)
        if M_arr.shape[0] != A.shape[axis]:
            raise PRIQError(f"input map for slot {axis} has an incompatible source input dimension")
        operands.extend([M_arr, [old_label, new_label]])
    operands.append([new_output, *new_inputs])
    return np.einsum(*operands, optimize=True)


def apply_tensor(tensor: Array, *vectors: Array) -> Array:
    """Evaluate a multilinear tensor on ordered input vectors."""

    A = _as_float_array(tensor)
    m, _, input_dim = validate_tensor(A)
    if len(vectors) != m:
        raise PRIQError(f"expected {m} vectors, received {len(vectors)}")
    operands: list[object] = [A, list(range(m + 1))]
    for slot, vector in enumerate(vectors, start=1):
        x = _as_float_array(vector, ndim=1)
        if x.size != input_dim:
            raise PRIQError(f"vector in slot {slot} has length {x.size}, expected {input_dim}")
        operands.extend([x, [slot]])
    operands.append([0])
    return np.einsum(*operands, optimize=True)


def symmetrize_inputs(tensor: Array) -> Array:
    """Average a tensor over all permutations of its input axes."""

    from itertools import permutations

    A = _as_float_array(tensor)
    m, _, _ = validate_tensor(A)
    result = np.zeros_like(A)
    perms = list(permutations(range(1, m + 1)))
    for perm in perms:
        result += np.transpose(A, axes=(0, *perm))
    return result / len(perms)


def quotient_defect(fine_tensor: Array, coarse_tensor: Array, C: Array) -> Array:
    """Return ``C A_f - A_c C^{x m}`` as a coefficient tensor."""

    Af = _as_float_array(fine_tensor)
    Ac = _as_float_array(coarse_tensor)
    C = _as_float_array(C, ndim=2)
    m_f, out_f, in_f = validate_tensor(Af)
    m_c, out_c, in_c = validate_tensor(Ac)
    if m_f != m_c:
        raise PRIQError("fine and coarse tensors must have the same order")
    if C.shape != (out_c, out_f) or in_f != out_f or in_c != out_c:
        raise PRIQError("this reference routine expects square fine/coarse state tensors")
    left = transform_tensor(Af, C, [np.eye(in_f)] * m_f)
    right = transform_tensor(Ac, np.eye(out_c), [C] * m_f)
    return left - right


def exact_lift_tensor(
    coarse_tensor: Array,
    C: Array,
    E: Array,
    *,
    hidden_tensor: Array | None = None,
) -> Array:
    """Lift a coarse tensor and optionally add a tensor with hidden output.

    The base lift is ``E A_c C^{x m}``.  Any supplied hidden tensor is projected
    through ``Q = I - E C`` on its output, so its aggregate is identically zero.
    """

    Ac = _as_float_array(coarse_tensor)
    C = _as_float_array(C, ndim=2)
    E = _as_float_array(E, ndim=2)
    m, q_out, q_in = validate_tensor(Ac)
    q, n = C.shape
    if q_out != q or q_in != q or E.shape != (n, q):
        raise PRIQError("coarse tensor, aggregation, and section have incompatible dimensions")
    if not np.allclose(C @ E, np.eye(q), atol=1e-10, rtol=1e-10):
        raise PRIQError("E must be a right inverse of C")
    base = transform_tensor(Ac, E, [C] * m)
    if hidden_tensor is None:
        return base
    H = _as_float_array(hidden_tensor)
    if H.shape != base.shape:
        raise PRIQError(f"hidden tensor has shape {H.shape}, expected {base.shape}")
    Q = np.eye(n) - E @ C
    hidden = transform_tensor(H, Q, [np.eye(n)] * m)
    return base + hidden


def aggregate_output_coefficients(fine_tensor: Array, C: Array) -> Array:
    """Return the coefficient array ``C A_f`` after output aggregation."""

    Af = _as_float_array(fine_tensor)
    C = _as_float_array(C, ndim=2)
    m, out_dim, in_dim = validate_tensor(Af)
    if C.shape[1] != out_dim:
        raise PRIQError("aggregation has incompatible output dimension")
    return transform_tensor(Af, C, [np.eye(in_dim)] * m)


@dataclass(frozen=True)
class RecoveryResult:
    coarse_tensor: Array
    max_fiber_variation: float
    witness: tuple[int, tuple[int, ...], tuple[int, ...]] | None


def recover_coarse_tensor(
    fine_tensor: Array,
    packet_map: Sequence[int],
    *,
    tolerance: float = 1e-10,
    representative: str = "mean",
) -> RecoveryResult:
    """Recover a coarse tensor from fiber values in packet coordinates.

    ``representative`` may be ``"mean"`` or ``"midrange"``.  The returned
    variation records the full spread within the worst fiber.  A numerical run
    may accept a spread below ``tolerance``.  Algebraic exactness still means
    that the spread is zero.
    """

    Af = _as_float_array(fine_tensor)
    m, n_out, n_in = validate_tensor(Af)
    if n_out != n_in:
        raise PRIQError("block sum recovery expects a state tensor with equal input and output dimensions")
    pi = np.asarray(packet_map, dtype=int)
    if pi.size != n_in:
        raise PRIQError("packet_map length must equal the fine state dimension")
    C = block_sum_matrix(pi)
    q = C.shape[0]
    G = aggregate_output_coefficients(Af, C)
    fibers = [np.flatnonzero(pi == a).tolist() for a in range(q)]
    coarse = np.empty((q, *([q] * m)), dtype=float)
    max_variation = 0.0
    witness: tuple[int, tuple[int, ...], tuple[int, ...]] | None = None

    for coarse_inputs in product(range(q), repeat=m):
        fine_tuples = list(product(*(fibers[a] for a in coarse_inputs)))
        for a in range(q):
            values = np.asarray([G[(a, *idx)] for idx in fine_tuples], dtype=float)
            variation = float(values.max() - values.min())
            if variation > max_variation:
                max_variation = variation
                i_min = fine_tuples[int(np.argmin(values))]
                i_max = fine_tuples[int(np.argmax(values))]
                witness = (a, tuple(i_min), tuple(i_max))
            if representative == "mean":
                value = float(values.mean())
            elif representative == "midrange":
                value = float(0.5 * (values.max() + values.min()))
            else:
                raise PRIQError("representative must be 'mean' or 'midrange'")
            coarse[(a, *coarse_inputs)] = value

    if max_variation <= tolerance:
        witness = None
    return RecoveryResult(coarse, max_variation, witness)


def slot_kernel_residual(fine_tensor: Array, C: Array) -> float:
    """Return the largest Frobenius residual after inserting ``ker(C)`` in one slot."""

    Af = _as_float_array(fine_tensor)
    C = _as_float_array(C, ndim=2)
    m, n_out, n_in = validate_tensor(Af)
    if C.shape[1] != n_out or n_in != n_out:
        raise PRIQError("the slot kernel test expects a square fine state tensor")
    K = kernel_basis(C)
    if K.shape[1] == 0:
        return 0.0
    residual = 0.0
    for slot in range(m):
        maps = [np.eye(n_in) for _ in range(m)]
        maps[slot] = K
        transformed = transform_tensor(Af, C, maps)
        residual = max(residual, float(np.linalg.norm(transformed)))
    return residual


def bayes_update(mu: Array, likelihood: Array) -> Array:
    """Return the normalized positive likelihood update."""

    p = _as_float_array(mu, ndim=1)
    lam = _as_float_array(likelihood, ndim=1)
    if p.size != lam.size:
        raise PRIQError("state and likelihood dimensions differ")
    if np.any(p < 0) or np.any(lam < 0):
        raise PRIQError("Bayesian update requires nonnegative state and likelihood")
    unnormalized = lam * p
    evidence = float(unnormalized.sum())
    if evidence <= 0:
        raise PRIQError("Bayesian evidence must be positive")
    return unnormalized / evidence


def bayes_commutation_residual(
    mu_fine: Array,
    lambda_fine: Array,
    lambda_coarse: Array,
    C: Array,
    *,
    ord: int | float = 1,
) -> float:
    """Compute ``|| C B_f(mu) - B_c(C mu) ||``."""

    C = _as_float_array(C, ndim=2)
    lhs = C @ bayes_update(mu_fine, lambda_fine)
    rhs = bayes_update(C @ _as_float_array(mu_fine, ndim=1), lambda_coarse)
    return float(np.linalg.norm(lhs - rhs, ord=ord))


def normalization_perturbation_bound(u: Array, v: Array) -> float:
    """Return the symmetric l1 bound for normalization of positive vectors."""

    u = _as_float_array(u, ndim=1)
    v = _as_float_array(v, ndim=1)
    if np.any(u < 0) or np.any(v < 0):
        raise PRIQError("normalization vectors must be nonnegative")
    a = float(np.sum(u))
    b = float(np.sum(v))
    if a <= 0 or b <= 0:
        raise PRIQError("normalization masses must be positive")
    return 2.0 * float(np.linalg.norm(u - v, ord=1)) / max(a, b)


def rk4_step(field: Callable[[Array], Array], state: Array, step: float) -> Array:
    """Take one deterministic classical RK4 step."""

    x = _as_float_array(state, ndim=1)
    h = float(step)
    if h <= 0:
        raise PRIQError("step must be positive")
    k1 = _as_float_array(field(x), ndim=1)
    k2 = _as_float_array(field(x + 0.5 * h * k1), ndim=1)
    k3 = _as_float_array(field(x + 0.5 * h * k2), ndim=1)
    k4 = _as_float_array(field(x + h * k3), ndim=1)
    if not (k1.size == k2.size == k3.size == k4.size == x.size):
        raise PRIQError("field returned an incompatible state dimension")
    return x + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


def integrate_rk4(
    field: Callable[[Array], Array],
    initial: Array,
    duration: float,
    *,
    max_step: float = 1e-3,
    project_simplex: bool = False,
) -> Array:
    """Integrate an autonomous finite ODE over one interval."""

    T = float(duration)
    if T < 0:
        raise PRIQError("duration must be nonnegative")
    x = _as_float_array(initial, ndim=1).copy()
    if T == 0:
        return x
    steps = max(1, int(np.ceil(T / max_step)))
    h = T / steps
    for _ in range(steps):
        x = rk4_step(field, x, h)
        if project_simplex:
            # Exact commutation tests do not use projection.  It is available only
            # as a numerical safeguard for explicitly approximate runs.
            x = np.maximum(x, 0.0)
            total = float(x.sum())
            if total <= 0:
                raise PRIQError("simplex projection encountered zero total mass")
            x /= total
    return x


@dataclass(frozen=True)
class FilterTrace:
    fine_posteriors: Array
    coarse_posteriors: Array
    fine_predictions: Array
    coarse_predictions: Array
    fine_evidence: Array
    coarse_evidence: Array


def simulate_prediction_update_filter(
    fine_initial: Array,
    coarse_initial: Array,
    fine_field: Callable[[Array], Array],
    coarse_field: Callable[[Array], Array],
    fine_likelihoods: Sequence[Array],
    coarse_likelihoods: Sequence[Array],
    durations: Sequence[float],
    *,
    max_step: float = 1e-3,
) -> FilterTrace:
    """Run matched prediction and update recursions for the fine and coarse models."""

    if not (len(fine_likelihoods) == len(coarse_likelihoods) == len(durations)):
        raise PRIQError("likelihood and duration sequences must have the same length")
    xf = _as_float_array(fine_initial, ndim=1).copy()
    xc = _as_float_array(coarse_initial, ndim=1).copy()
    fine_posts = [xf.copy()]
    coarse_posts = [xc.copy()]
    fine_preds: list[Array] = []
    coarse_preds: list[Array] = []
    fine_evidence: list[float] = []
    coarse_evidence: list[float] = []

    for lf, lc, T in zip(fine_likelihoods, coarse_likelihoods, durations, strict=True):
        xf_hat = integrate_rk4(fine_field, xf, T, max_step=max_step)
        xc_hat = integrate_rk4(coarse_field, xc, T, max_step=max_step)
        lf_arr = _as_float_array(lf, ndim=1)
        lc_arr = _as_float_array(lc, ndim=1)
        zf = float(lf_arr @ xf_hat)
        zc = float(lc_arr @ xc_hat)
        xf = bayes_update(xf_hat, lf_arr)
        xc = bayes_update(xc_hat, lc_arr)
        fine_preds.append(xf_hat)
        coarse_preds.append(xc_hat)
        fine_evidence.append(zf)
        coarse_evidence.append(zc)
        fine_posts.append(xf.copy())
        coarse_posts.append(xc.copy())

    return FilterTrace(
        fine_posteriors=np.asarray(fine_posts),
        coarse_posteriors=np.asarray(coarse_posts),
        fine_predictions=np.asarray(fine_preds),
        coarse_predictions=np.asarray(coarse_preds),
        fine_evidence=np.asarray(fine_evidence),
        coarse_evidence=np.asarray(coarse_evidence),
    )


def posterior_error_certificate(
    initial_error: float,
    flow_lipschitz: Sequence[float],
    bayes_lipschitz: Sequence[float],
    flow_defects: Sequence[float],
    bayes_defects: Sequence[float],
) -> tuple[float, Array, Array]:
    """Propagate the affine error recurrence for prediction and update."""

    arrays = [
        np.asarray(flow_lipschitz, dtype=float),
        np.asarray(bayes_lipschitz, dtype=float),
        np.asarray(flow_defects, dtype=float),
        np.asarray(bayes_defects, dtype=float),
    ]
    lengths = {arr.size for arr in arrays}
    if len(lengths) != 1:
        raise PRIQError("all certificate sequences must have the same length")
    if any(np.any(arr < 0) for arr in arrays):
        raise PRIQError("certificate factors and defects must be nonnegative")
    e_plus = float(initial_error)
    minus_trace: list[float] = []
    plus_trace: list[float] = [e_plus]
    for Lphi, LB, dphi, dB in zip(*arrays, strict=True):
        e_minus = float(Lphi * e_plus + dphi)
        e_plus = float(LB * e_minus + dB)
        minus_trace.append(e_minus)
        plus_trace.append(e_plus)
    return e_plus, np.asarray(minus_trace), np.asarray(plus_trace)


def hidden_exchange_fields(
    *,
    a: float = 0.7,
    b: float = 0.4,
    r0: float = 0.25,
    r1: float = 0.30,
    s0: float = 0.20,
    s1: float = 0.18,
    u0: float = 0.22,
    u1: float = 0.24,
    v0: float = 0.19,
    v1: float = 0.20,
    epsilon: float = 0.0,
) -> tuple[Callable[[Array], Array], Callable[[Array], Array], Array]:
    """Return the exact example with four fine states and two coarse states."""

    params = [a, b, r0, r1, s0, s1, u0, u1, v0, v1, epsilon]
    if any(value < 0 for value in params):
        raise PRIQError("all example rates must be nonnegative")
    C = block_sum_matrix([0, 0, 1, 1])

    def coarse(z: Array) -> Array:
        z = _as_float_array(z, ndim=1)
        return np.asarray([-a * z[0] + b * z[1], a * z[0] - b * z[1]])

    def fine(x: Array) -> Array:
        x = _as_float_array(x, ndim=1)
        h12 = (r0 + r1 * x[2]) * x[1] - (s0 + s1 * x[3]) * x[0]
        h34 = (u0 + u1 * x[0]) * x[3] - (v0 + v1 * x[1]) * x[2]
        dx = np.asarray(
            [
                -a * x[0] + b * x[2] + h12,
                -a * x[1] + b * x[3] - h12,
                a * x[0] - b * x[2] + h34,
                a * x[1] - b * x[3] - h34,
            ],
            dtype=float,
        )
        if epsilon:
            dx += epsilon * x[0] * np.asarray([-1.0, 0.0, 1.0, 0.0])
        return dx

    return fine, coarse, C


def hyperedge_energy_statistics(coefficients: Array) -> tuple[Array, float, float]:
    """Return normalized squared energies, Shannon entropy, and effective count."""

    values = _as_float_array(coefficients).ravel()
    energy = values * values
    total = float(energy.sum())
    if total <= 0:
        raise PRIQError("at least one hyperedge coefficient must be nonzero")
    probabilities = energy / total
    positive = probabilities > 0
    entropy = float(-np.sum(probabilities[positive] * np.log(probabilities[positive])))
    return probabilities, entropy, exp(entropy)


def best_k_residuals(coefficients: Array) -> Array:
    """Return exact Frobenius residual after retaining each number of largest blocks."""

    values = _as_float_array(coefficients).ravel()
    energies = np.sort(values * values)[::-1]
    residual_sq = np.zeros(energies.size + 1, dtype=float)
    residual_sq[:-1] = np.cumsum(energies[::-1])[::-1]
    return np.sqrt(residual_sq)


def total_variation(p: Array, q: Array) -> float:
    """Finite total variation distance."""

    p_arr = _as_float_array(p, ndim=1)
    q_arr = _as_float_array(q, ndim=1)
    if p_arr.size != q_arr.size:
        raise PRIQError("probability vectors must have the same dimension")
    return 0.5 * float(np.linalg.norm(p_arr - q_arr, ord=1))
