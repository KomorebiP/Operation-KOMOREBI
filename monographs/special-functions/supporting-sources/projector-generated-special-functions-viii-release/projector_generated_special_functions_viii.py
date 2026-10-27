from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon
import numpy as np
from scipy.linalg import null_space

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"
for directory in (FIGURES, RESULTS, TABLES):
    directory.mkdir(parents=True, exist_ok=True)

INK = "#17202A"
BLUE = "#2E86AB"
TEAL = "#2A9D8F"
ORANGE = "#F4A261"
MAGENTA = "#A23E8C"
RED = "#E76F51"
YELLOW = "#E9C46A"
PURPLE = "#6C5CE7"
MUTED = "#5D6D7E"
PAPER = "#FAFAF7"
GRID = "#D5D8DC"
WHITE = "#FFFFFF"
COLORS = [BLUE, TEAL, ORANGE, MAGENTA, RED, YELLOW, PURPLE]

plt.rcParams.update(
    {
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.edgecolor": INK,
        "axes.labelcolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "text.color": INK,
        "font.size": 10.5,
        "axes.titlesize": 12.2,
        "axes.titleweight": "bold",
        "legend.frameon": False,
        "savefig.bbox": "tight",
        "savefig.facecolor": PAPER,
    }
)


def jsonable(value):
    """Convert NumPy scalar containers into JSON-safe Python objects."""
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIGURES / f"{stem}.pdf")
    fig.savefig(FIGURES / f"{stem}.png", dpi=220)
    plt.close(fig)


def diagram_axes(figsize: tuple[float, float] = (12.6, 6.1)) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return fig, ax


def box(
    ax: plt.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    face: str = WHITE,
    edge: str = INK,
    fontsize: float = 10.5,
) -> None:
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=.012,rounding_size=.018",
        facecolor=face,
        edgecolor=edge,
        linewidth=1.6,
    )
    ax.add_patch(patch)
    ax.text(xy[0] + width / 2, xy[1] + height / 2, text, ha="center", va="center", fontsize=fontsize)


def arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    color: str = INK,
    text: str | None = None,
    text_offset: tuple[float, float] = (0.0, 0.035),
) -> None:
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=13, linewidth=1.5, color=color)
    ax.add_patch(patch)
    if text:
        ax.text(
            (start[0] + end[0]) / 2 + text_offset[0],
            (start[1] + end[1]) / 2 + text_offset[1],
            text,
            ha="center",
            va="center",
            fontsize=9.5,
            color=color,
        )


# ---------------------------------------------------------------------------
# q-arithmetic and positive discrete-series packet spaces
# ---------------------------------------------------------------------------


def q_number(x: float, q: float) -> float:
    if q <= 0:
        raise ValueError("q must be positive")
    if abs(q - 1.0) < 1e-12:
        return float(x)
    theta = math.log(q)
    return float(math.sinh(x * theta) / math.sinh(theta))


def q_factorial(n: int, q: float) -> float:
    result = 1.0
    for j in range(1, n + 1):
        result *= q_number(float(j), q)
    return result


def q_binomial(n: int, r: int, q: float) -> float:
    if r < 0 or r > n:
        return 0.0
    return q_factorial(n, q) / (q_factorial(r, q) * q_factorial(n - r, q))


def q_rising(x: float, n: int, q: float) -> float:
    result = 1.0
    for j in range(n):
        result *= q_number(x + j, q)
    return result


@lru_cache(maxsize=None)
def compositions(total: int, parts: int) -> tuple[tuple[int, ...], ...]:
    if total < 0:
        return tuple()
    if parts == 1:
        return ((total,),)
    out: list[tuple[int, ...]] = []
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            out.append((first,) + rest)
    return tuple(out)


def excitation_dimension(total: int, factors: int) -> int:
    return math.comb(total + factors - 1, factors - 1)


def multiplicity_dimension(total: int, factors: int) -> int:
    if factors < 2:
        return 1
    return math.comb(total + factors - 2, factors - 2)


def q_local_matrices(dimension: int, kappa: float, q: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    k0 = np.diag([n + kappa for n in range(dimension)])
    kp = np.zeros((dimension, dimension), dtype=float)
    km = np.zeros((dimension, dimension), dtype=float)
    for n in range(dimension - 1):
        coefficient = math.sqrt(q_number(n + 1.0, q) * q_number(2.0 * kappa + n, q))
        kp[n + 1, n] = coefficient
        km[n, n + 1] = coefficient
    return k0, kp, km


def q_lowering_matrix(
    total: int,
    kappas: Sequence[float],
    q: float,
    subset: Iterable[int] | None = None,
) -> np.ndarray:
    factors = len(kappas)
    active = list(range(factors)) if subset is None else [int(value) for value in subset]
    basis_now = compositions(total, factors)
    if total == 0:
        return np.zeros((0, len(basis_now)), dtype=float)
    basis_previous = compositions(total - 1, factors)
    previous_index = {state: index for index, state in enumerate(basis_previous)}
    matrix = np.zeros((len(basis_previous), len(basis_now)), dtype=float)
    for column, state in enumerate(basis_now):
        for position, factor in enumerate(active):
            occupation = state[factor]
            if occupation == 0:
                continue
            coefficient = math.sqrt(
                q_number(float(occupation), q)
                * q_number(2.0 * kappas[factor] + occupation - 1.0, q)
            )
            exponent = 0.0
            for left in active[:position]:
                exponent -= state[left] + kappas[left]
            for right in active[position + 1 :]:
                exponent += state[right] + kappas[right]
            coefficient *= q**exponent
            target = list(state)
            target[factor] -= 1
            matrix[previous_index[tuple(target)], column] += coefficient
    return matrix


def q_casimir_matrix(total: int, kappas: Sequence[float], q: float, subset: Iterable[int]) -> np.ndarray:
    active = [int(value) for value in subset]
    basis = compositions(total, len(kappas))
    k0_values = np.array([sum(state[index] + kappas[index] for index in active) for state in basis])
    lowering = q_lowering_matrix(total, kappas, q, active)
    diagonal = np.array([q_number(value, q) * q_number(value - 1.0, q) for value in k0_values])
    return np.diag(diagonal) - lowering.T @ lowering


def q_multiplicity_frame(total: int, kappas: Sequence[float], q: float, atol: float = 1e-11) -> np.ndarray:
    if total == 0:
        return np.ones((1, 1), dtype=float)
    lowering = q_lowering_matrix(total, kappas, q)
    return null_space(lowering, rcond=atol)


def sign_fix_columns(matrix: np.ndarray) -> np.ndarray:
    result = np.array(matrix, dtype=float, copy=True)
    for column in range(result.shape[1]):
        row = int(np.argmax(np.abs(result[:, column])))
        if result[row, column] < 0:
            result[:, column] *= -1.0
    return result


def canonicalize_overlap(matrix: np.ndarray) -> np.ndarray:
    result = np.array(matrix, dtype=float, copy=True)
    for column in range(result.shape[1]):
        if result[0, column] < 0:
            result[:, column] *= -1.0
    for row in range(result.shape[0]):
        if result[row, 0] < 0:
            result[row, :] *= -1.0
    return result


def align_signed_matrix(reference: np.ndarray, candidate: np.ndarray, iterations: int = 8) -> np.ndarray:
    result = np.array(candidate, dtype=float, copy=True)
    for _ in range(iterations):
        for column in range(result.shape[1]):
            if float(np.dot(reference[:, column], result[:, column])) < 0:
                result[:, column] *= -1.0
        for row in range(result.shape[0]):
            if float(np.dot(reference[row, :], result[row, :])) < 0:
                result[row, :] *= -1.0
    return result


@dataclass
class QRecouplingData:
    total: int
    kappas: tuple[float, float, float]
    q: float
    multiplicity_frame: np.ndarray
    left_eigenvalues: np.ndarray
    right_eigenvalues: np.ndarray
    left_basis: np.ndarray
    right_basis: np.ndarray
    overlap: np.ndarray
    right_in_left: np.ndarray


def q_three_body_recoupling(total: int, kappas: Sequence[float], q: float) -> QRecouplingData:
    if len(kappas) != 3:
        raise ValueError("q_three_body_recoupling requires three shapes")
    kappas_tuple = tuple(float(value) for value in kappas)
    frame = q_multiplicity_frame(total, kappas_tuple, q)
    c12 = frame.T @ q_casimir_matrix(total, kappas_tuple, q, (0, 1)) @ frame
    c23 = frame.T @ q_casimir_matrix(total, kappas_tuple, q, (1, 2)) @ frame
    left_values, left_vectors = np.linalg.eigh(c12)
    right_values, right_vectors = np.linalg.eigh(c23)
    left_vectors = sign_fix_columns(left_vectors)
    right_vectors = sign_fix_columns(right_vectors)
    left_basis = frame @ left_vectors
    right_basis = frame @ right_vectors
    overlap = canonicalize_overlap(left_basis.T @ right_basis)
    right_in_left = overlap @ np.diag(right_values) @ overlap.T
    return QRecouplingData(
        total=total,
        kappas=kappas_tuple,
        q=float(q),
        multiplicity_frame=frame,
        left_eigenvalues=left_values,
        right_eigenvalues=right_values,
        left_basis=left_basis,
        right_basis=right_basis,
        overlap=overlap,
        right_in_left=right_in_left,
    )


def q_pair_spectrum(total: int, kappa_a: float, kappa_b: float, q: float) -> np.ndarray:
    return np.array(
        [
            q_number(kappa_a + kappa_b + j, q)
            * q_number(kappa_a + kappa_b + j - 1.0, q)
            for j in range(total + 1)
        ]
    )


def q_two_body_lowest_coefficients(total: int, kappa_1: float, kappa_2: float, q: float) -> np.ndarray:
    tilt = q ** (-(total - 1.0 + kappa_1 + kappa_2))
    coefficients = []
    for n in range(total + 1):
        weight = q_binomial(total, n, q)
        weight *= q_rising(2.0 * kappa_2 + total - n, n, q)
        weight /= q_rising(2.0 * kappa_1, n, q)
        coefficients.append(((-tilt) ** n) * math.sqrt(weight))
    vector = np.array(coefficients, dtype=float)
    return vector / np.linalg.norm(vector)


def equal_shape_one_excitation_matrix(q: float) -> np.ndarray:
    denominator = 1.0 + q * q
    cosine = q / denominator
    sine = math.sqrt(1.0 + q * q + q**4) / denominator
    return np.array([[cosine, sine], [sine, -cosine]], dtype=float)


def tridiagonal_residual(matrix: np.ndarray) -> float:
    residual = np.array(matrix, copy=True)
    for row in range(residual.shape[0]):
        for column in range(residual.shape[1]):
            if abs(row - column) <= 1:
                residual[row, column] = 0.0
    return float(np.max(np.abs(residual)))


def row_entropies(probability_matrix: np.ndarray) -> np.ndarray:
    safe = np.where(probability_matrix > 0, probability_matrix, 1.0)
    return -np.sum(np.where(probability_matrix > 0, probability_matrix * np.log(safe), 0.0), axis=1)


def doubly_stochastic_residual(matrix: np.ndarray) -> float:
    return float(
        max(
            np.max(np.abs(matrix.sum(axis=0) - 1.0)),
            np.max(np.abs(matrix.sum(axis=1) - 1.0)),
            np.max(np.maximum(-matrix, 0.0)),
        )
    )


def spectral_mixing_gap(probability_matrix: np.ndarray) -> float:
    eigenvalues = np.linalg.eigvals(probability_matrix)
    magnitudes = sorted((abs(value) for value in eigenvalues), reverse=True)
    if len(magnitudes) < 2:
        return 1.0
    return float(1.0 - magnitudes[1])


# ---------------------------------------------------------------------------
# q-deformation flow
# ---------------------------------------------------------------------------


def deformation_generator(total: int, kappas: Sequence[float], theta: float, step: float = 2e-5) -> dict[str, np.ndarray | float]:
    q0 = math.exp(-theta)
    reference = q_three_body_recoupling(total, kappas, q0).overlap
    plus = q_three_body_recoupling(total, kappas, math.exp(-(theta + step))).overlap
    minus = q_three_body_recoupling(total, kappas, math.exp(-(theta - step))).overlap
    plus = align_signed_matrix(reference, plus)
    minus = align_signed_matrix(reference, minus)
    derivative = (plus - minus) / (2.0 * step)
    raw = reference.T @ derivative
    generator = 0.5 * (raw - raw.T)
    skew_residual = float(np.max(np.abs(raw + raw.T)))
    tangent_residual = float(np.max(np.abs(derivative - reference @ generator)))
    metric = 0.5 * float(np.sum(generator * generator))
    return {
        "q": q0,
        "matrix": reference,
        "derivative": derivative,
        "generator": generator,
        "skew_residual": skew_residual,
        "tangent_residual": tangent_residual,
        "metric": metric,
    }


# ---------------------------------------------------------------------------
# Four-body q-coupling trees and pentagon coherence
# ---------------------------------------------------------------------------


FOUR_TREES: tuple[tuple[str, tuple[tuple[int, ...], tuple[int, ...]]], ...] = (
    ("(((12)3)4)", ((0, 1), (0, 1, 2))),
    ("((1(23))4)", ((1, 2), (0, 1, 2))),
    ("(1((23)4))", ((1, 2), (1, 2, 3))),
    ("(1(2(34)))", ((2, 3), (1, 2, 3))),
    ("((12)(34))", ((0, 1), (2, 3))),
)


@dataclass
class QTreeBasisData:
    name: str
    subsets: tuple[tuple[int, ...], ...]
    basis: np.ndarray
    joint_diagonals: tuple[np.ndarray, ...]
    commutator_residual: float
    diagonalization_residual: float


def q_joint_tree_basis(
    total: int,
    kappas: Sequence[float],
    q: float,
    name: str,
    subsets: Sequence[Sequence[int]],
) -> QTreeBasisData:
    frame = q_multiplicity_frame(total, kappas, q)
    restricted = [frame.T @ q_casimir_matrix(total, kappas, q, subset) @ frame for subset in subsets]
    commutator = 0.0
    for i in range(len(restricted)):
        for j in range(i + 1, len(restricted)):
            commutator = max(
                commutator,
                float(np.max(np.abs(restricted[i] @ restricted[j] - restricted[j] @ restricted[i]))),
            )
    irrational_weights = [math.sqrt(2.0), math.sqrt(3.0), math.sqrt(5.0)]
    combined = sum(weight * matrix for weight, matrix in zip(irrational_weights, restricted))
    _, vectors = np.linalg.eigh(combined)
    vectors = sign_fix_columns(vectors)
    diagonals = tuple(vectors.T @ matrix @ vectors for matrix in restricted)
    tuples = []
    for column in range(vectors.shape[1]):
        key = tuple(round(float(diagonal[column, column]), 10) for diagonal in diagonals)
        tuples.append((key, column))
    order = [column for _, column in sorted(tuples, key=lambda item: item[0])]
    vectors = vectors[:, order]
    diagonals = tuple(vectors.T @ matrix @ vectors for matrix in restricted)
    diagonalization_residual = max(
        float(np.max(np.abs(diagonal - np.diag(np.diag(diagonal))))) for diagonal in diagonals
    )
    return QTreeBasisData(
        name=name,
        subsets=tuple(tuple(int(index) for index in subset) for subset in subsets),
        basis=frame @ vectors,
        joint_diagonals=diagonals,
        commutator_residual=commutator,
        diagonalization_residual=diagonalization_residual,
    )


def q_four_body_tree_bases(total: int, kappas: Sequence[float], q: float) -> list[QTreeBasisData]:
    if len(kappas) != 4:
        raise ValueError("q_four_body_tree_bases requires four shapes")
    return [q_joint_tree_basis(total, kappas, q, name, subsets) for name, subsets in FOUR_TREES]


def q_pentagon_product(tree_bases: Sequence[QTreeBasisData]) -> tuple[np.ndarray, list[np.ndarray]]:
    dimension = tree_bases[0].basis.shape[1]
    product_matrix = np.eye(dimension)
    overlaps: list[np.ndarray] = []
    for index in range(len(tree_bases)):
        left = tree_bases[index].basis
        right = tree_bases[(index + 1) % len(tree_bases)].basis
        overlap = left.T @ right
        overlaps.append(overlap)
        product_matrix = product_matrix @ overlap
    return product_matrix, overlaps


# ---------------------------------------------------------------------------
# q-hypergeometric q-Racah and Askey-Wilson functions
# ---------------------------------------------------------------------------


def q_pochhammer(a: complex, q: float, n: int) -> complex:
    result = 1.0 + 0.0j
    for j in range(n):
        result *= 1.0 - a * (q**j)
    return result


def q_racah_polynomial(
    n: int,
    y: int,
    alpha: float,
    beta: float,
    gamma: float,
    delta: float,
    q: float,
) -> complex:
    result = 0.0 + 0.0j
    for ell in range(n + 1):
        numerator = q_pochhammer(q ** (-n), q, ell)
        numerator *= q_pochhammer(alpha * beta * q ** (n + 1), q, ell)
        numerator *= q_pochhammer(q ** (-y), q, ell)
        numerator *= q_pochhammer(gamma * delta * q ** (y + 1), q, ell)
        denominator = q_pochhammer(alpha * q, q, ell)
        denominator *= q_pochhammer(beta * delta * q, q, ell)
        denominator *= q_pochhammer(gamma * q, q, ell)
        denominator *= q_pochhammer(q, q, ell)
        result += numerator / denominator * q**ell
    return result


def rising(a: float, n: int) -> float:
    result = 1.0
    for j in range(n):
        result *= a + j
    return result


def classical_racah_polynomial(n: int, y: int, alpha: float, beta: float, gamma: float, delta: float) -> float:
    result = 0.0
    for ell in range(n + 1):
        numerator = rising(-float(n), ell)
        numerator *= rising(n + alpha + beta + 1.0, ell)
        numerator *= rising(-float(y), ell)
        numerator *= rising(y + gamma + delta + 1.0, ell)
        denominator = rising(alpha + 1.0, ell)
        denominator *= rising(beta + delta + 1.0, ell)
        denominator *= rising(gamma + 1.0, ell)
        denominator *= math.factorial(ell)
        result += numerator / denominator
    return result


def askey_wilson_r(
    n: int,
    z: complex,
    a: float,
    b: float,
    c: float,
    d: float,
    q: float,
) -> complex:
    result = 0.0 + 0.0j
    for ell in range(n + 1):
        numerator = q_pochhammer(q ** (-n), q, ell)
        numerator *= q_pochhammer(a * b * c * d * q ** (n - 1), q, ell)
        numerator *= q_pochhammer(a * z, q, ell)
        numerator *= q_pochhammer(a / z, q, ell)
        denominator = q_pochhammer(a * b, q, ell)
        denominator *= q_pochhammer(a * c, q, ell)
        denominator *= q_pochhammer(a * d, q, ell)
        denominator *= q_pochhammer(q, q, ell)
        result += numerator / denominator * q**ell
    return result


def askey_wilson_operator(
    function,
    z: complex,
    a: float,
    b: float,
    c: float,
    d: float,
    q: float,
) -> complex:
    first = ((1 - a * z) * (1 - b * z) * (1 - c * z) * (1 - d * z))
    first /= (1 - z * z) * (1 - q * z * z)
    inverse = 1.0 / z
    second = ((1 - a * inverse) * (1 - b * inverse) * (1 - c * inverse) * (1 - d * inverse))
    second /= (1 - inverse * inverse) * (1 - q * inverse * inverse)
    return (
        first * (function(q * z) - function(z))
        + second * (function(z / q) - function(z))
        + (1.0 + a * b * c * d / q) * function(z)
    )


# ---------------------------------------------------------------------------
# Givens compilation
# ---------------------------------------------------------------------------


@dataclass
class GivensRotation:
    upper: int
    lower: int
    cosine: float
    sine: float


def givens_decompose(orthogonal: np.ndarray, atol: float = 1e-14) -> tuple[list[GivensRotation], np.ndarray]:
    matrix = np.array(orthogonal, dtype=float, copy=True)
    dimension = matrix.shape[0]
    rotations: list[GivensRotation] = []
    for column in range(dimension):
        for lower in range(dimension - 1, column, -1):
            upper = lower - 1
            a = matrix[upper, column]
            b = matrix[lower, column]
            radius = math.hypot(a, b)
            if radius < atol:
                continue
            cosine = a / radius
            sine = b / radius
            row_upper = cosine * matrix[upper, :] + sine * matrix[lower, :]
            row_lower = -sine * matrix[upper, :] + cosine * matrix[lower, :]
            matrix[upper, :] = row_upper
            matrix[lower, :] = row_lower
            rotations.append(GivensRotation(upper, lower, cosine, sine))
    return rotations, np.diag(np.diag(matrix))


def givens_reconstruct(rotations: Sequence[GivensRotation], diagonal: np.ndarray) -> np.ndarray:
    matrix = np.array(diagonal, dtype=float, copy=True)
    for rotation in reversed(rotations):
        upper = rotation.upper
        lower = rotation.lower
        cosine = rotation.cosine
        sine = rotation.sine
        row_upper = cosine * matrix[upper, :] - sine * matrix[lower, :]
        row_lower = sine * matrix[upper, :] + cosine * matrix[lower, :]
        matrix[upper, :] = row_upper
        matrix[lower, :] = row_lower
    return matrix


# ---------------------------------------------------------------------------
# Checks and result tables
# ---------------------------------------------------------------------------


def run_checks() -> dict[str, dict[str, float | int | str | bool]]:
    checks: dict[str, dict[str, float | int | str | bool]] = {}

    q = 0.73
    kappa = 0.8
    dimension = 12
    k0, kp, km = q_local_matrices(dimension, kappa, q)
    commutator = km @ kp - kp @ km
    target = np.diag([q_number(2.0 * (n + kappa), q) for n in range(dimension)])
    algebra_residual = float(np.max(np.abs(commutator[:-1, :-1] - target[:-1, :-1])))
    checks["q_algebra"] = {"passed": algebra_residual < 2e-10, "residual": algebra_residual}

    total = 5
    kappas_two = (0.7, 1.1)
    coefficients = q_two_body_lowest_coefficients(total, *kappas_two, q)
    lowest_residual = float(np.max(np.abs(q_lowering_matrix(total, kappas_two, q) @ coefficients)))
    checks["q_hahn_lowest_weight"] = {"passed": lowest_residual < 2e-10, "residual": lowest_residual}

    casimir = q_casimir_matrix(6, (kappa,), q, (0,))
    scalar = q_number(kappa, q) * q_number(kappa - 1.0, q)
    casimir_residual = float(np.max(np.abs(casimir - scalar * np.eye(casimir.shape[0]))))
    checks["q_casimir_scalar"] = {"passed": casimir_residual < 2e-10, "residual": casimir_residual}

    data = q_three_body_recoupling(8, (0.7, 1.1, 0.9), q)
    orthogonality = float(np.max(np.abs(data.overlap @ data.overlap.T - np.eye(9))))
    checks["q_racah_orthogonality"] = {"passed": orthogonality < 2e-10, "residual": orthogonality}

    left_theory = q_pair_spectrum(8, 0.7, 1.1, q)
    spectrum_residual = float(np.max(np.abs(data.left_eigenvalues - left_theory)))
    checks["q_pair_spectrum"] = {"passed": spectrum_residual < 2e-9, "residual": spectrum_residual}

    tri_residual = tridiagonal_residual(data.right_in_left)
    checks["q_racah_tridiagonal"] = {"passed": tri_residual < 3e-9, "residual": tri_residual}

    exact = equal_shape_one_excitation_matrix(q)
    computed = q_three_body_recoupling(1, (0.5, 0.5, 0.5), q).overlap
    beam_residual = float(np.max(np.abs(computed - exact)))
    checks["q_beam_splitter_closed_form"] = {"passed": beam_residual < 2e-10, "residual": beam_residual}

    probability = data.overlap**2
    stochastic_residual = doubly_stochastic_residual(probability)
    checks["q_bistochastic_kernel"] = {"passed": stochastic_residual < 2e-10, "residual": stochastic_residual}

    rng = np.random.default_rng(801)
    entropy_fail = 0.0
    for _ in range(80):
        vector = rng.random(probability.shape[0])
        vector /= vector.sum()
        before = -float(np.sum(vector * np.log(vector)))
        after_vector = vector @ probability
        after = -float(np.sum(after_vector * np.log(after_vector)))
        entropy_fail = max(entropy_fail, before - after)
    checks["q_entropy_non_decrease"] = {"passed": entropy_fail < 2e-12, "residual": entropy_fail}

    q_values = np.linspace(0.12, 1.0, 80)
    entropy_one = []
    for value in q_values:
        matrix = equal_shape_one_excitation_matrix(float(value))
        entropy_one.append(row_entropies(matrix**2)[0])
    monotone_residual = float(max(0.0, -np.min(np.diff(entropy_one))))
    checks["one_excitation_entropy_monotone"] = {"passed": monotone_residual < 2e-10, "residual": monotone_residual}

    entropy_middle = []
    for value in q_values:
        matrix = q_three_body_recoupling(3, (0.5, 0.5, 0.5), float(value)).overlap
        entropy_middle.append(row_entropies(matrix**2)[1])
    negative_control = float(np.min(np.diff(entropy_middle)))
    checks["higher_entropy_nonmonotone_control"] = {
        "passed": negative_control < -1e-5,
        "minimum_increment": negative_control,
    }

    classical = q_three_body_recoupling(8, (0.7, 1.1, 0.9), 1.0).overlap
    near = align_signed_matrix(classical, q_three_body_recoupling(8, (0.7, 1.1, 0.9), 0.9999).overlap)
    classical_limit = float(np.max(np.abs(near - classical)))
    checks["q_to_one_recoupling"] = {"passed": classical_limit < 2e-5, "residual": classical_limit}

    qh_classical = q_two_body_lowest_coefficients(7, 0.7, 1.1, 1.0)
    qh_near = q_two_body_lowest_coefficients(7, 0.7, 1.1, 0.999999)
    if float(np.dot(qh_classical, qh_near)) < 0:
        qh_near *= -1.0
    qh_limit = float(np.max(np.abs(qh_near - qh_classical)))
    checks["q_hahn_classical_limit"] = {"passed": qh_limit < 2e-5, "residual": qh_limit}

    small_q = equal_shape_one_excitation_matrix(1e-5)
    routing_target = np.array([[0.0, 1.0], [1.0, 0.0]])
    routing_residual = float(np.max(np.abs(small_q - routing_target)))
    checks["q_to_zero_routing"] = {"passed": routing_residual < 2e-5, "residual": routing_residual}

    deformation = deformation_generator(6, (0.7, 1.1, 0.9), theta=0.35)
    checks["deformation_generator_skew"] = {
        "passed": float(deformation["skew_residual"]) < 2e-7,
        "residual": float(deformation["skew_residual"]),
    }
    checks["deformation_tangent_equation"] = {
        "passed": float(deformation["tangent_residual"]) < 2e-7,
        "residual": float(deformation["tangent_residual"]),
    }

    four_kappas = (0.55, 0.8, 1.05, 1.3)
    trees = q_four_body_tree_bases(4, four_kappas, 0.78)
    commutator_residual = max(tree.commutator_residual for tree in trees)
    diagonal_residual = max(tree.diagonalization_residual for tree in trees)
    product_matrix, _ = q_pentagon_product(trees)
    pentagon_residual = float(np.max(np.abs(product_matrix - np.eye(product_matrix.shape[0]))))
    checks["q_tree_commutation"] = {"passed": commutator_residual < 2e-8, "residual": commutator_residual}
    checks["q_tree_diagonalization"] = {"passed": diagonal_residual < 2e-8, "residual": diagonal_residual}
    checks["q_pentagon"] = {"passed": pentagon_residual < 2e-8, "residual": pentagon_residual}

    rotations, diagonal = givens_decompose(data.overlap)
    reconstructed = givens_reconstruct(rotations, diagonal)
    givens_residual = float(np.max(np.abs(reconstructed - data.overlap)))
    checks["q_givens_compilation"] = {
        "passed": givens_residual < 2e-10,
        "residual": givens_residual,
        "rotation_count": len(rotations),
    }

    q_poly = 0.73
    degree_limit = 6
    alpha_exp = 0.6
    beta_exp = 0.8
    gamma_exp = -degree_limit - 1.0
    delta_exp = 0.4
    alpha = q_poly**alpha_exp
    beta = q_poly**beta_exp
    gamma = q_poly**gamma_exp
    delta = q_poly**delta_exp
    duality_residual = 0.0
    for n in range(degree_limit + 1):
        for y in range(degree_limit + 1):
            left = q_racah_polynomial(n, y, alpha, beta, gamma, delta, q_poly)
            right = q_racah_polynomial(y, n, gamma, delta, alpha, beta, q_poly)
            duality_residual = max(duality_residual, abs(left - right))
    checks["q_racah_duality"] = {"passed": duality_residual < 2e-10, "residual": float(duality_residual)}

    q_limit = 0.999
    alpha = q_limit**alpha_exp
    beta = q_limit**beta_exp
    gamma = q_limit**gamma_exp
    delta = q_limit**delta_exp
    polynomial_limit = 0.0
    for n in range(4):
        for y in range(degree_limit + 1):
            q_value = q_racah_polynomial(n, y, alpha, beta, gamma, delta, q_limit).real
            classical_value = classical_racah_polynomial(n, y, alpha_exp, beta_exp, gamma_exp, delta_exp)
            polynomial_limit = max(polynomial_limit, abs(q_value - classical_value))
    checks["q_racah_polynomial_limit"] = {"passed": polynomial_limit < 2e-4, "residual": polynomial_limit}

    aw_q = 0.7
    aw_parameters = (0.2, 0.3, -0.25, 0.4)
    aw_residual = 0.0
    for n in range(6):
        for theta in np.linspace(0.31, 2.72, 8):
            z = np.exp(1j * theta)
            function = lambda value, degree=n: askey_wilson_r(degree, value, *aw_parameters, aw_q)
            left = askey_wilson_operator(function, z, *aw_parameters, aw_q)
            eigenvalue = aw_q ** (-n) + np.prod(aw_parameters) * aw_q ** (n - 1)
            aw_residual = max(aw_residual, abs(left - eigenvalue * function(z)))
    checks["askey_wilson_difference_equation"] = {"passed": aw_residual < 2e-9, "residual": float(aw_residual)}

    passed = sum(1 for item in checks.values() if bool(item["passed"]))
    summary = {"checks": checks, "passed": passed, "total": len(checks), "all_passed": passed == len(checks)}
    (RESULTS / "checks.json").write_text(json.dumps(jsonable(summary), indent=2))
    return checks


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------


def generate_figures() -> list[str]:
    generated: list[str] = []

    fig, ax = diagram_axes((13.0, 6.3))
    ax.text(0.5, 0.94, "From classical shape packets to q-deformed recoupling", ha="center", fontsize=21, weight="bold")
    stages = [
        (0.03, 0.58, 0.16, 0.17, "q-number\nladder", BLUE),
        (0.23, 0.58, 0.16, 0.17, "q-Hahn\nlowest packet", TEAL),
        (0.43, 0.58, 0.16, 0.17, "q-Casimir\natlases", ORANGE),
        (0.63, 0.58, 0.16, 0.17, "q-Racah\ntransform", MAGENTA),
        (0.83, 0.58, 0.14, 0.17, "q-pentagon\ncoherence", RED),
    ]
    for x, y, w, h, label, color in stages:
        box(ax, (x, y), w, h, label, face=color + "1C", edge=color, fontsize=11.5)
    for left, right in zip(stages[:-1], stages[1:]):
        arrow(ax, (left[0] + left[2], left[1] + left[3] / 2), (right[0], right[1] + right[3] / 2))
    box(ax, (0.12, 0.18), 0.20, 0.16, "bistochastic\nmeasurement", face=YELLOW + "25", edge=YELLOW, fontsize=11.5)
    box(ax, (0.40, 0.18), 0.20, 0.16, "deformation\ngenerator", face=PURPLE + "1C", edge=PURPLE, fontsize=11.5)
    box(ax, (0.68, 0.18), 0.20, 0.16, "Askey-Wilson\ncontinuous lift", face=BLUE + "1C", edge=BLUE, fontsize=11.5)
    arrow(ax, (0.70, 0.58), (0.22, 0.34), color=MAGENTA)
    arrow(ax, (0.72, 0.58), (0.50, 0.34), color=PURPLE)
    arrow(ax, (0.88, 0.58), (0.78, 0.34), color=RED)
    ax.text(0.5, 0.07, "The deformation parameter changes the packet algebra while preserving exact analysis, synthesis, and associator closure.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "01_theory_pipeline")
    generated.append("01_theory_pipeline")

    x = np.linspace(0.0, 8.0, 300)
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    for q, color in zip((0.45, 0.65, 0.82, 0.95, 1.0), COLORS[:5]):
        ax.plot(x, [q_number(value, q) for value in x], color=color, linewidth=2.0, label=f"q={q:g}")
    ax.plot(x, x, color=INK, linestyle="--", linewidth=1.2, label="classical x")
    ax.set_xlabel("x")
    ax.set_ylabel(r"$[x]_q$")
    ax.set_title("Symmetric q-numbers deform the linear ladder")
    ax.grid(alpha=0.18)
    ax.legend(ncol=3)
    save_figure(fig, "02_q_number_deformation")
    generated.append("02_q_number_deformation")

    n = np.arange(0, 14)
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    for q, color in zip((0.45, 0.7, 0.9, 1.0), (BLUE, TEAL, ORANGE, MAGENTA)):
        values = [math.sqrt(q_number(value + 1.0, q) * q_number(value + 1.6, q)) for value in n]
        ax.plot(n, values, marker="o", markersize=3.5, color=color, label=f"q={q:g}")
    ax.set_xlabel("packet degree n")
    ax.set_ylabel("raising coefficient")
    ax.set_title(r"q-deformed positive-series ladder at $\kappa=0.8$")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "03_q_ladder_coefficients")
    generated.append("03_q_ladder_coefficients")

    fig, ax = diagram_axes((12.8, 6.2))
    ax.text(0.5, 0.94, "The symmetric coproduct routes one lowering event through every factor", ha="center", fontsize=20, weight="bold")
    centers = [(0.16, 0.60), (0.50, 0.60), (0.84, 0.60)]
    for index, center in enumerate(centers, start=1):
        box(ax, (center[0] - 0.09, center[1] - 0.08), 0.18, 0.16, f"packet {index}\n$D^+_{{\\kappa_{index},q}}$", face=COLORS[index - 1] + "1C", edge=COLORS[index - 1])
    ax.text(0.5, 0.35, r"$\Delta^{(3)}K_- = K_-q^{K_0}q^{K_0} + q^{-K_0}K_-q^{K_0} + q^{-K_0}q^{-K_0}K_-$", ha="center", fontsize=14)
    for center, color in zip(centers, COLORS[:3]):
        arrow(ax, (center[0], center[1] - 0.08), (0.50, 0.27), color=color)
    box(ax, (0.38, 0.11), 0.24, 0.12, "one exact\nlowest-weight projector", face=PURPLE + "1C", edge=PURPLE)
    ax.text(0.5, 0.04, "The q-powers retain the ordering data needed by the deformed tensor product.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "04_q_coproduct_paths")
    generated.append("04_q_coproduct_paths")

    total = 9
    fig, ax = plt.subplots(figsize=(11.8, 5.5))
    for q, color in zip((0.35, 0.55, 0.75, 0.9, 1.0), COLORS[:5]):
        probabilities = q_two_body_lowest_coefficients(total, 0.7, 1.1, q) ** 2
        ax.plot(range(total + 1), probabilities, marker="o", color=color, label=f"q={q:g}")
    ax.set_xlabel("first-factor excitation n")
    ax.set_ylabel("packet probability")
    ax.set_title("q-Hahn lowest-weight packet redistributes excitation")
    ax.grid(alpha=0.18)
    ax.legend(ncol=3)
    save_figure(fig, "05_q_hahn_packet_distribution")
    generated.append("05_q_hahn_packet_distribution")

    q_values = 1.0 - 10.0 ** (-np.linspace(1.0, 5.0, 45))
    classical = q_two_body_lowest_coefficients(9, 0.7, 1.1, 1.0)
    errors = []
    for value in q_values:
        vector = q_two_body_lowest_coefficients(9, 0.7, 1.1, float(value))
        if np.dot(vector, classical) < 0:
            vector *= -1
        errors.append(np.max(np.abs(vector - classical)))
    fig, ax = plt.subplots(figsize=(11.8, 5.2))
    ax.loglog(1.0 - q_values, errors, marker="o", color=TEAL)
    ax.set_xlabel(r"$1-q$")
    ax.set_ylabel("maximum coefficient error")
    ax.set_title("q-Hahn packets converge to the classical lowest-weight packet")
    ax.grid(alpha=0.18, which="both")
    save_figure(fig, "06_q_hahn_classical_limit")
    generated.append("06_q_hahn_classical_limit")

    q_values = np.linspace(0.02, 1.0, 320)
    cosines = q_values / (1.0 + q_values**2)
    sines = np.sqrt(1.0 + q_values**2 + q_values**4) / (1.0 + q_values**2)
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    ax.plot(q_values, cosines, color=BLUE, linewidth=2.2, label=r"$q/(1+q^2)$")
    ax.plot(q_values, sines, color=ORANGE, linewidth=2.2, label=r"$\sqrt{1+q^2+q^4}/(1+q^2)$")
    ax.set_xlabel("q")
    ax.set_ylabel("recoupling amplitude")
    ax.set_title("Exact equal-shape one-excitation q-beam splitter")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "07_q_beam_splitter_amplitudes")
    generated.append("07_q_beam_splitter_amplitudes")

    fig, axes = plt.subplots(1, 3, figsize=(12.8, 4.2))
    for ax, q in zip(axes, (0.15, 0.55, 1.0)):
        matrix = equal_shape_one_excitation_matrix(q) ** 2
        image = ax.imshow(matrix, cmap="viridis", vmin=0, vmax=1)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{matrix[i,j]:.3f}", ha="center", va="center", color=WHITE if matrix[i,j] > 0.55 else INK)
        ax.set_xticks([0, 1])
        ax.set_yticks([0, 1])
        ax.set_title(f"q={q:g}")
    fig.suptitle("The q-beam splitter interpolates between routing and mixing", fontsize=16, weight="bold")
    fig.colorbar(image, ax=axes, fraction=0.025, pad=0.025, label="transition probability")
    fig.subplots_adjust(left=0.06, right=0.92, bottom=0.12, top=0.82, wspace=0.25)
    save_figure(fig, "08_q_beam_splitter_kernel")
    generated.append("08_q_beam_splitter_kernel")

    entropy = []
    gap = []
    for q in q_values:
        probability = equal_shape_one_excitation_matrix(float(q)) ** 2
        entropy.append(row_entropies(probability)[0])
        gap.append(spectral_mixing_gap(probability))
    fig, ax = plt.subplots(figsize=(11.8, 5.4))
    ax.plot(q_values, entropy, color=BLUE, linewidth=2.2, label="row entropy")
    ax.plot(q_values, gap, color=ORANGE, linewidth=2.2, label="absolute spectral gap")
    ax.set_xlabel("q")
    ax.set_ylabel("value")
    ax.set_title("One-excitation mixing strengthens toward the classical endpoint")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "09_beam_splitter_entropy_gap")
    generated.append("09_beam_splitter_entropy_gap")

    total = 10
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    for q, color in zip((0.45, 0.65, 0.82, 1.0), (BLUE, TEAL, ORANGE, MAGENTA)):
        spectrum = q_pair_spectrum(total, 0.7, 1.1, q)
        ax.plot(range(total + 1), spectrum, marker="o", markersize=3.5, color=color, label=f"q={q:g}")
    ax.set_xlabel("intermediate packet label")
    ax.set_ylabel("q-Casimir eigenvalue")
    ax.set_title("q-Casimir spectra remain simple and ordered")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "10_q_casimir_spectra")
    generated.append("10_q_casimir_spectra")

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.6))
    vmax = 0.0
    matrices = []
    for q in (0.45, 0.72, 1.0):
        matrix = q_three_body_recoupling(10, (0.7, 1.1, 0.9), q).overlap
        matrices.append(matrix)
        vmax = max(vmax, np.max(np.abs(matrix)))
    for ax, matrix, q in zip(axes, matrices, (0.45, 0.72, 1.0)):
        image = ax.imshow(matrix, cmap="coolwarm", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_title(f"q={q:g}")
        ax.set_xlabel(r"$C_{23}$ label")
        ax.set_ylabel(r"$C_{12}$ label")
    fig.suptitle("q-Racah packet transforms across the deformation", fontsize=16, weight="bold")
    fig.colorbar(image, ax=axes, fraction=0.022, pad=0.025, label="overlap amplitude")
    fig.subplots_adjust(left=0.06, right=0.92, bottom=0.12, top=0.82, wspace=0.25)
    save_figure(fig, "11_q_racah_heatmaps")
    generated.append("11_q_racah_heatmaps")

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.6))
    for ax, matrix, q in zip(axes, matrices, (0.45, 0.72, 1.0)):
        image = ax.imshow(matrix**2, cmap="viridis", vmin=0, vmax=np.max(matrix**2), aspect="auto")
        ax.set_title(f"q={q:g}")
        ax.set_xlabel("measurement output")
        ax.set_ylabel("input packet")
    fig.suptitle("Squared q-Racah amplitudes remain bistochastic", fontsize=16, weight="bold")
    fig.colorbar(image, ax=axes, fraction=0.022, pad=0.025, label="probability")
    fig.subplots_adjust(left=0.06, right=0.92, bottom=0.12, top=0.82, wspace=0.25)
    save_figure(fig, "12_q_racah_probability_kernels")
    generated.append("12_q_racah_probability_kernels")

    totals = np.arange(1, 17)
    fig, ax = plt.subplots(figsize=(11.8, 5.2))
    for q, color in zip((0.45, 0.65, 0.82, 1.0), (BLUE, TEAL, ORANGE, MAGENTA)):
        residuals = []
        for total in totals:
            matrix = q_three_body_recoupling(int(total), (0.7, 1.1, 0.9), q).overlap
            residuals.append(np.max(np.abs(matrix @ matrix.T - np.eye(total + 1))))
        ax.semilogy(totals, residuals, marker="o", markersize=3.5, color=color, label=f"q={q:g}")
    ax.set_xlabel("total excitation N")
    ax.set_ylabel("maximum orthogonality residual")
    ax.set_title("q-Racah analysis and synthesis remain numerically exact")
    ax.grid(alpha=0.18, which="both")
    ax.legend()
    save_figure(fig, "13_q_orthogonality_residual")
    generated.append("13_q_orthogonality_residual")

    data = q_three_body_recoupling(12, (0.7, 1.1, 0.9), 0.7)
    matrix = data.right_in_left
    fig, ax = plt.subplots(figsize=(8.2, 7.0))
    vmax = np.percentile(np.abs(matrix), 99)
    image = ax.imshow(matrix, cmap="coolwarm", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xlabel(r"$C_{12}$ packet label")
    ax.set_ylabel(r"$C_{12}$ packet label")
    ax.set_title(r"The opposing q-Casimir is tridiagonal in the left atlas")
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03)
    save_figure(fig, "14_opposing_q_casimir")
    generated.append("14_opposing_q_casimir")

    q_poly = 0.73
    N = 8
    A, B, G, D = 0.6, 0.8, -N - 1.0, 0.4
    alpha, beta, gamma, delta = q_poly**A, q_poly**B, q_poly**G, q_poly**D
    values = np.array(
        [[q_racah_polynomial(n, y, alpha, beta, gamma, delta, q_poly).real for y in range(N + 1)] for n in range(N + 1)]
    )
    fig, ax = plt.subplots(figsize=(8.4, 7.2))
    image = ax.imshow(values, cmap="coolwarm", aspect="auto")
    ax.set_xlabel("lattice coordinate y")
    ax.set_ylabel("polynomial degree n")
    ax.set_title("q-Racah basic-hypergeometric packet table")
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03, label="polynomial value")
    save_figure(fig, "15_q_racah_polynomial_table")
    generated.append("15_q_racah_polynomial_table")

    dual_values = np.array(
        [[q_racah_polynomial(y, n, gamma, delta, alpha, beta, q_poly).real for y in range(N + 1)] for n in range(N + 1)]
    )
    duality = values - dual_values
    fig, ax = plt.subplots(figsize=(7.8, 6.6))
    image = ax.imshow(np.abs(duality), cmap="magma", aspect="auto")
    ax.set_xlabel("y")
    ax.set_ylabel("n")
    ax.set_title("q-Racah duality residual after parameter exchange")
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03, label="absolute residual")
    save_figure(fig, "16_q_racah_duality")
    generated.append("16_q_racah_duality")

    q_limits = 1.0 - 10.0 ** (-np.linspace(0.55, 4.0, 42))
    errors = []
    for q in q_limits:
        alpha, beta, gamma, delta = q**A, q**B, q**G, q**D
        error = 0.0
        for n in range(4):
            for y in range(N + 1):
                q_value = q_racah_polynomial(n, y, alpha, beta, gamma, delta, float(q)).real
                classical_value = classical_racah_polynomial(n, y, A, B, G, D)
                error = max(error, abs(q_value - classical_value))
        errors.append(error)
    fig, ax = plt.subplots(figsize=(11.8, 5.2))
    ax.loglog(1.0 - q_limits, errors, marker="o", color=TEAL)
    ax.set_xlabel(r"$1-q$")
    ax.set_ylabel("maximum polynomial error")
    ax.set_title("The explicit q-Racah family converges to Racah")
    ax.grid(alpha=0.18, which="both")
    save_figure(fig, "17_q_racah_to_racah")
    generated.append("17_q_racah_to_racah")

    classical = q_three_body_recoupling(10, (0.7, 1.1, 0.9), 1.0).overlap
    matrix_errors = []
    for q in q_limits:
        matrix = q_three_body_recoupling(10, (0.7, 1.1, 0.9), float(q)).overlap
        matrix = align_signed_matrix(classical, matrix)
        matrix_errors.append(np.max(np.abs(matrix - classical)))
    fig, ax = plt.subplots(figsize=(11.8, 5.2))
    ax.loglog(1.0 - q_limits, matrix_errors, marker="o", color=BLUE)
    ax.set_xlabel(r"$1-q$")
    ax.set_ylabel("maximum matrix error")
    ax.set_title("The packet recoupling matrix has the same classical limit")
    ax.grid(alpha=0.18, which="both")
    save_figure(fig, "18_recoupling_classical_limit")
    generated.append("18_recoupling_classical_limit")

    deformation = deformation_generator(8, (0.7, 1.1, 0.9), theta=0.38)
    generator = np.asarray(deformation["generator"])
    fig, ax = plt.subplots(figsize=(8.2, 7.0))
    vmax = np.max(np.abs(generator))
    image = ax.imshow(generator, cmap="coolwarm", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xlabel("packet coordinate")
    ax.set_ylabel("packet coordinate")
    ax.set_title(r"Skew deformation generator $A=R^{\mathrm{T}}\partial_\theta R$")
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03)
    save_figure(fig, "19_deformation_generator")
    generated.append("19_deformation_generator")

    thetas = np.linspace(0.02, 1.25, 80)
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    for total, color in zip((1, 3, 6, 9), (BLUE, TEAL, ORANGE, MAGENTA)):
        metric = [float(deformation_generator(total, (0.7, 1.1, 0.9), float(theta))["metric"]) for theta in thetas]
        ax.plot(thetas, metric, color=color, linewidth=2.0, label=f"N={total}")
    ax.set_xlabel(r"deformation coordinate $\theta=-\log q$")
    ax.set_ylabel(r"$\frac{1}{2}\|A_N(\theta)\|_F^2$")
    ax.set_title("Packet deformation has a finite transport metric")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "20_deformation_metric")
    generated.append("20_deformation_metric")

    q_grid = np.linspace(0.12, 1.0, 100)
    fig, ax = plt.subplots(figsize=(11.8, 5.4))
    for total, row, color in ((1, 0, BLUE), (2, 1, TEAL), (3, 1, ORANGE), (5, 2, MAGENTA)):
        entropies = []
        for q in q_grid:
            matrix = q_three_body_recoupling(total, (0.5, 0.5, 0.5), float(q)).overlap
            entropies.append(row_entropies(matrix**2)[row])
        ax.plot(q_grid, entropies, color=color, linewidth=2.0, label=f"N={total}, row={row}")
    ax.set_xlabel("q")
    ax.set_ylabel("row entropy")
    ax.set_title("Higher q-Racah channels need not vary monotonically")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "21_entropy_nonmonotonicity")
    generated.append("21_entropy_nonmonotonicity")

    fig, ax = plt.subplots(figsize=(11.8, 5.4))
    for total, color in zip((1, 2, 4, 7), (BLUE, TEAL, ORANGE, MAGENTA)):
        gaps = []
        for q in q_grid:
            probability = q_three_body_recoupling(total, (0.5, 0.5, 0.5), float(q)).overlap**2
            gaps.append(spectral_mixing_gap(probability))
        ax.plot(q_grid, gaps, color=color, linewidth=2.0, label=f"N={total}")
    ax.set_xlabel("q")
    ax.set_ylabel("absolute spectral gap")
    ax.set_title("Measurement mixing depends on both deformation and excitation")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "22_stochastic_spectral_gap")
    generated.append("22_stochastic_spectral_gap")

    fig, ax = diagram_axes((12.8, 6.6))
    ax.text(0.5, 0.95, "Five q-coupling trees form the same associahedral pentagon", ha="center", fontsize=20, weight="bold")
    angles = np.linspace(math.pi / 2, math.pi / 2 + 2 * math.pi, 6)[:-1]
    points = [(0.5 + 0.34 * math.cos(angle), 0.50 + 0.34 * math.sin(angle)) for angle in angles]
    labels = [name for name, _ in FOUR_TREES]
    for index, (point, label) in enumerate(zip(points, labels)):
        box(ax, (point[0] - 0.09, point[1] - 0.055), 0.18, 0.11, label, face=COLORS[index] + "1C", edge=COLORS[index], fontsize=9.5)
    for index in range(5):
        arrow(ax, points[index], points[(index + 1) % 5], color=INK)
    ax.text(0.5, 0.50, r"$\prod_{e\in\partial K_4} U_e(q)=I$", ha="center", va="center", fontsize=16, weight="bold")
    ax.text(0.5, 0.08, "Changing q changes every edge transform but not the closed associator path.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "23_q_pentagon_trees")
    generated.append("23_q_pentagon_trees")

    q_grid_pent = np.linspace(0.45, 1.0, 24)
    totals = (1, 2, 3, 4, 5)
    residual_grid = np.zeros((len(totals), len(q_grid_pent)))
    for i, total in enumerate(totals):
        for j, q in enumerate(q_grid_pent):
            trees = q_four_body_tree_bases(total, (0.55, 0.8, 1.05, 1.3), float(q))
            product_matrix, _ = q_pentagon_product(trees)
            residual_grid[i, j] = np.max(np.abs(product_matrix - np.eye(product_matrix.shape[0])))
    fig, ax = plt.subplots(figsize=(11.8, 5.7))
    image = ax.imshow(np.log10(np.maximum(residual_grid, 1e-18)), cmap="viridis", aspect="auto", origin="lower", extent=[q_grid_pent[0], q_grid_pent[-1], totals[0]-0.5, totals[-1]+0.5])
    ax.set_xlabel("q")
    ax.set_ylabel("total excitation N")
    ax.set_title("q-pentagon residual remains at floating-point scale")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.025, label=r"$\log_{10}$ residual")
    save_figure(fig, "24_q_pentagon_residual")
    generated.append("24_q_pentagon_residual")

    trees = q_four_body_tree_bases(3, (0.55, 0.8, 1.05, 1.3), 0.68)
    _, overlaps = q_pentagon_product(trees)
    fig, axes = plt.subplots(1, 5, figsize=(14.5, 3.6))
    vmax = max(np.max(np.abs(matrix)) for matrix in overlaps)
    for index, (ax, matrix) in enumerate(zip(axes, overlaps), start=1):
        image = ax.imshow(matrix, cmap="coolwarm", vmin=-vmax, vmax=vmax, aspect="auto")
        ax.set_title(f"edge {index}")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("The five signed q-associator edges", fontsize=16, weight="bold")
    fig.colorbar(image, ax=axes, fraction=0.018, pad=0.02)
    fig.subplots_adjust(left=0.04, right=0.94, bottom=0.08, top=0.78, wspace=0.10)
    save_figure(fig, "25_q_pentagon_edge_matrices")
    generated.append("25_q_pentagon_edge_matrices")

    fig, axes = plt.subplots(1, 3, figsize=(13.0, 4.6))
    for ax, q in zip(axes, (0.5, 0.75, 1.0)):
        trees = q_four_body_tree_bases(3, (0.55, 0.8, 1.05, 1.3), q)
        matrix = trees[0].basis.T @ trees[1].basis
        image = ax.imshow(matrix, cmap="coolwarm", vmin=-np.max(np.abs(matrix)), vmax=np.max(np.abs(matrix)), aspect="auto")
        ax.set_title(f"q={q:g}")
        ax.set_xticks([])
        ax.set_yticks([])
    fig.suptitle("One associator edge deforms continuously", fontsize=16, weight="bold")
    fig.colorbar(image, ax=axes, fraction=0.022, pad=0.025)
    fig.subplots_adjust(left=0.05, right=0.92, bottom=0.08, top=0.80, wspace=0.20)
    save_figure(fig, "26_associator_deformation")
    generated.append("26_associator_deformation")

    totals = np.arange(1, 14)
    rotation_counts = []
    residuals = []
    for total in totals:
        matrix = q_three_body_recoupling(int(total), (0.7, 1.1, 0.9), 0.72).overlap
        rotations, diagonal = givens_decompose(matrix)
        reconstruction = givens_reconstruct(rotations, diagonal)
        rotation_counts.append(len(rotations))
        residuals.append(np.max(np.abs(reconstruction - matrix)))
    fig, ax = plt.subplots(figsize=(11.8, 5.4))
    ax.plot(totals, rotation_counts, marker="o", color=BLUE, label="used rotations")
    ax.plot(totals, totals * (totals + 1) / 2, linestyle="--", color=ORANGE, label=r"$d(d-1)/2$ bound")
    ax.set_xlabel("total excitation N")
    ax.set_ylabel("two-coordinate rotations")
    ax.set_title("Finite q-Racah transforms compile into Givens circuits")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "27_q_givens_counts")
    generated.append("27_q_givens_counts")

    fig, ax = plt.subplots(figsize=(11.8, 5.1))
    ax.semilogy(totals, residuals, marker="o", color=TEAL)
    ax.set_xlabel("total excitation N")
    ax.set_ylabel("maximum reconstruction residual")
    ax.set_title("The compiled q-transform reconstructs the packet matrix")
    ax.grid(alpha=0.18, which="both")
    save_figure(fig, "28_q_givens_residual")
    generated.append("28_q_givens_residual")

    aw_q = 0.7
    aw_parameters = (0.2, 0.3, -0.25, 0.4)
    theta = np.linspace(0.08, math.pi - 0.08, 360)
    fig, ax = plt.subplots(figsize=(11.8, 5.5))
    for n, color in zip(range(5), COLORS[:5]):
        values = [askey_wilson_r(n, np.exp(1j * value), *aw_parameters, aw_q).real for value in theta]
        ax.plot(np.cos(theta), values, color=color, linewidth=1.8, label=f"n={n}")
    ax.set_xlabel(r"$x=\cos\theta$")
    ax.set_ylabel("normalized Askey-Wilson value")
    ax.set_title("The continuous Askey-Wilson packet lift")
    ax.grid(alpha=0.18)
    ax.legend(ncol=3)
    save_figure(fig, "29_askey_wilson_curves")
    generated.append("29_askey_wilson_curves")

    residual_table = np.zeros((6, 36))
    theta_grid = np.linspace(0.12, math.pi - 0.12, residual_table.shape[1])
    for n in range(residual_table.shape[0]):
        function = lambda value, degree=n: askey_wilson_r(degree, value, *aw_parameters, aw_q)
        eigenvalue = aw_q ** (-n) + np.prod(aw_parameters) * aw_q ** (n - 1)
        for j, value in enumerate(theta_grid):
            z = np.exp(1j * value)
            residual_table[n, j] = abs(askey_wilson_operator(function, z, *aw_parameters, aw_q) - eigenvalue * function(z))
    fig, ax = plt.subplots(figsize=(11.8, 5.4))
    image = ax.imshow(np.log10(np.maximum(residual_table, 1e-18)), cmap="magma", aspect="auto", origin="lower", extent=[theta_grid[0], theta_grid[-1], -0.5, 5.5])
    ax.set_xlabel(r"$\theta$")
    ax.set_ylabel("degree n")
    ax.set_title("Askey-Wilson q-difference equation residual")
    fig.colorbar(image, ax=ax, fraction=0.035, pad=0.025, label=r"$\log_{10}$ residual")
    save_figure(fig, "30_askey_wilson_difference_residual")
    generated.append("30_askey_wilson_difference_residual")

    fig, ax = diagram_axes((12.8, 6.4))
    ax.text(0.5, 0.94, "The finite and continuous q-functions belong to one transfer class", ha="center", fontsize=20, weight="bold")
    box(ax, (0.06, 0.58), 0.20, 0.16, "Uq(su(1,1))\nq-Hahn packets", face=TEAL + "1C", edge=TEAL)
    box(ax, (0.40, 0.58), 0.20, 0.16, "finite q-Racah\nrecoupling", face=MAGENTA + "1C", edge=MAGENTA)
    box(ax, (0.74, 0.58), 0.20, 0.16, "continuous\nAskey-Wilson lift", face=BLUE + "1C", edge=BLUE)
    arrow(ax, (0.26, 0.66), (0.40, 0.66), text="pair Casimir")
    arrow(ax, (0.60, 0.66), (0.74, 0.66), text="continuous spectrum")
    box(ax, (0.18, 0.20), 0.22, 0.15, "q -> 1\nclassical Racah", face=ORANGE + "1C", edge=ORANGE)
    box(ax, (0.60, 0.20), 0.22, 0.15, "q -> 0\nsparse routing", face=YELLOW + "25", edge=YELLOW)
    arrow(ax, (0.50, 0.58), (0.29, 0.35), color=ORANGE)
    arrow(ax, (0.50, 0.58), (0.71, 0.35), color=YELLOW)
    ax.text(0.5, 0.07, "The packet calculus keeps the exact reconstruction law while q changes the local transfer geometry.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "31_q_function_class_map")
    generated.append("31_q_function_class_map")

    fig, ax = diagram_axes((13.0, 6.4))
    ax.text(0.5, 0.94, "A programmable q-packet execution path", ha="center", fontsize=20, weight="bold")
    stages = [
        (0.04, 0.58, 0.16, 0.16, "packet shapes\n$\\kappa_i$", BLUE),
        (0.24, 0.58, 0.16, 0.16, "choose q and\nexcitation N", TEAL),
        (0.44, 0.58, 0.16, 0.16, "build q-Casimir\nprojectors", ORANGE),
        (0.64, 0.58, 0.16, 0.16, "diagonalize\nmultiplicity", MAGENTA),
        (0.84, 0.58, 0.13, 0.16, "compile\nrotations", RED),
    ]
    for x, y, w, h, label, color in stages:
        box(ax, (x, y), w, h, label, face=color + "1C", edge=color, fontsize=11)
    for left, right in zip(stages[:-1], stages[1:]):
        arrow(ax, (left[0] + left[2], left[1] + left[3] / 2), (right[0], right[1] + right[3] / 2))
    box(ax, (0.16, 0.20), 0.20, 0.15, "signed\nq-transform", face=PURPLE + "1C", edge=PURPLE)
    box(ax, (0.40, 0.20), 0.20, 0.15, "measurement\nkernel", face=YELLOW + "25", edge=YELLOW)
    box(ax, (0.64, 0.20), 0.20, 0.15, "pentagon\ncertificate", face=TEAL + "1C", edge=TEAL)
    arrow(ax, (0.90, 0.58), (0.26, 0.35), color=PURPLE)
    arrow(ax, (0.90, 0.58), (0.50, 0.35), color=YELLOW)
    arrow(ax, (0.90, 0.58), (0.74, 0.35), color=TEAL)
    ax.text(0.5, 0.07, "Dense tensor spaces are used only to define the projector. Execution takes place in the smaller multiplicity packet.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "32_q_packet_compiler")
    generated.append("32_q_packet_compiler")

    return generated


def write_tables(checks: dict[str, dict[str, float | int | str | bool]]) -> None:
    with (TABLES / "check_summary.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["check", "passed", "detail"])
        for name, result in checks.items():
            detail = ", ".join(f"{key}={value}" for key, value in result.items() if key != "passed")
            writer.writerow([name, result["passed"], detail])

    with (TABLES / "q_beam_splitter.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["q", "cosine", "sine", "row_entropy", "spectral_gap"])
        for q in (0.1, 0.25, 0.5, 0.75, 1.0):
            matrix = equal_shape_one_excitation_matrix(q)
            probability = matrix**2
            writer.writerow([
                q,
                matrix[0, 0],
                matrix[0, 1],
                row_entropies(probability)[0],
                spectral_mixing_gap(probability),
            ])

    with (TABLES / "q_pentagon.csv").open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["q", "N", "dimension", "pentagon_residual"])
        for q in (0.5, 0.7, 0.85, 1.0):
            for total in (1, 2, 3, 4):
                trees = q_four_body_tree_bases(total, (0.55, 0.8, 1.05, 1.3), q)
                product_matrix, _ = q_pentagon_product(trees)
                writer.writerow([q, total, product_matrix.shape[0], np.max(np.abs(product_matrix - np.eye(product_matrix.shape[0])))])


def write_manifest(generated: Sequence[str], checks: dict[str, dict[str, float | int | str | bool]]) -> None:
    manifest = {
        "title": "Projector-Generated Special Functions VIII",
        "author": "Komorebi P.",
        "figures": list(generated),
        "figure_pairs": len(generated),
        "checks_passed": sum(1 for value in checks.values() if bool(value["passed"])),
        "checks_total": len(checks),
    }
    (RESULTS / "manifest.json").write_text(json.dumps(jsonable(manifest), indent=2))


def main() -> None:
    checks = run_checks()
    generated = generate_figures()
    write_tables(checks)
    write_manifest(generated, checks)
    passed = sum(1 for result in checks.values() if bool(result["passed"]))
    print(f"Generated {len(generated)} figure pairs")
    print(f"Checks passed: {passed}/{len(checks)}")
    if passed != len(checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
