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
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
import numpy as np
import sympy as sp
from scipy.linalg import null_space

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"
TABLES = ROOT / "tables"
GENERATED = ROOT / "generated_tables"
for directory in (FIGURES, RESULTS, TABLES, GENERATED):
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
# Positive discrete-series packet spaces
# ---------------------------------------------------------------------------


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


def multiplicity_dimension(total: int, factors: int) -> int:
    if factors < 2:
        return 1
    return math.comb(total + factors - 2, factors - 2)


def excitation_dimension(total: int, factors: int) -> int:
    return math.comb(total + factors - 1, factors - 1)


def lowering_matrix(total: int, kappas: Sequence[float], subset: Iterable[int] | None = None) -> np.ndarray:
    m = len(kappas)
    active = set(range(m)) if subset is None else set(subset)
    basis_n = compositions(total, m)
    if total == 0:
        return np.zeros((0, len(basis_n)), dtype=float)
    basis_prev = compositions(total - 1, m)
    index_prev = {state: i for i, state in enumerate(basis_prev)}
    matrix = np.zeros((len(basis_prev), len(basis_n)), dtype=float)
    for col, state in enumerate(basis_n):
        for i in active:
            occupation = state[i]
            if occupation == 0:
                continue
            target = list(state)
            target[i] -= 1
            coefficient = math.sqrt(occupation * (occupation + 2.0 * kappas[i] - 1.0))
            matrix[index_prev[tuple(target)], col] += coefficient
    return matrix


def raising_matrix(total: int, kappas: Sequence[float], subset: Iterable[int] | None = None) -> np.ndarray:
    return lowering_matrix(total + 1, kappas, subset).T


def casimir_matrix(total: int, kappas: Sequence[float], subset: Iterable[int]) -> np.ndarray:
    active = set(subset)
    basis = compositions(total, len(kappas))
    k0 = np.array([sum(state[i] + kappas[i] for i in active) for state in basis], dtype=float)
    lowering = lowering_matrix(total, kappas, active)
    return np.diag(k0 * (k0 - 1.0)) - lowering.T @ lowering


def multiplicity_frame(total: int, kappas: Sequence[float], atol: float = 1e-11) -> np.ndarray:
    lowering = lowering_matrix(total, kappas)
    if total == 0:
        return np.ones((1, 1), dtype=float)
    frame = null_space(lowering, rcond=atol)
    return frame


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


@dataclass
class RecouplingData:
    total: int
    kappas: tuple[float, float, float]
    multiplicity_frame: np.ndarray
    left_eigenvalues: np.ndarray
    right_eigenvalues: np.ndarray
    left_basis: np.ndarray
    right_basis: np.ndarray
    overlap_raw: np.ndarray
    overlap: np.ndarray
    right_in_left: np.ndarray


def three_body_recoupling(total: int, kappas: Sequence[float]) -> RecouplingData:
    if len(kappas) != 3:
        raise ValueError("three_body_recoupling requires three shapes")
    kappas_tuple = tuple(float(value) for value in kappas)
    frame = multiplicity_frame(total, kappas_tuple)
    c12 = frame.T @ casimir_matrix(total, kappas_tuple, (0, 1)) @ frame
    c23 = frame.T @ casimir_matrix(total, kappas_tuple, (1, 2)) @ frame
    left_values, left_vectors = np.linalg.eigh(c12)
    right_values, right_vectors = np.linalg.eigh(c23)
    left_vectors = sign_fix_columns(left_vectors)
    right_vectors = sign_fix_columns(right_vectors)
    left_basis = frame @ left_vectors
    right_basis = frame @ right_vectors
    raw = left_basis.T @ right_basis
    overlap = canonicalize_overlap(raw)
    right_in_left = overlap @ np.diag(right_values) @ overlap.T
    return RecouplingData(
        total=total,
        kappas=kappas_tuple,
        multiplicity_frame=frame,
        left_eigenvalues=left_values,
        right_eigenvalues=right_values,
        left_basis=left_basis,
        right_basis=right_basis,
        overlap_raw=raw,
        overlap=overlap,
        right_in_left=right_in_left,
    )


def theoretical_pair_spectrum(total: int, kappa_a: float, kappa_b: float) -> np.ndarray:
    j = np.arange(total + 1, dtype=float)
    shape = kappa_a + kappa_b + j
    return shape * (shape - 1.0)


def one_excitation_closed_form(kappas: Sequence[float]) -> np.ndarray:
    k1, k2, k3 = map(float, kappas)
    denominator = (k1 + k2) * (k2 + k3)
    cosine = math.sqrt(k1 * k3 / denominator)
    sine = math.sqrt(k2 * (k1 + k2 + k3) / denominator)
    return np.array([[cosine, sine], [sine, -cosine]], dtype=float)


def equal_shape_two_excitation_matrix() -> np.ndarray:
    return np.array(
        [
            [1.0 / 3.0, 1.0 / math.sqrt(3.0), math.sqrt(5.0) / 3.0],
            [1.0 / math.sqrt(3.0), 1.0 / 2.0, -math.sqrt(15.0) / 6.0],
            [math.sqrt(5.0) / 3.0, -math.sqrt(15.0) / 6.0, 1.0 / 6.0],
        ],
        dtype=float,
    )


def tridiagonal_residual(matrix: np.ndarray) -> float:
    residual = np.array(matrix, copy=True)
    rows, cols = residual.shape
    for row in range(rows):
        for col in range(cols):
            if abs(row - col) <= 1:
                residual[row, col] = 0.0
    return float(np.max(np.abs(residual)))


def row_entropies(probability_matrix: np.ndarray) -> np.ndarray:
    safe = np.where(probability_matrix > 0, probability_matrix, 1.0)
    return -np.sum(np.where(probability_matrix > 0, probability_matrix * np.log(probability_matrix), 0.0), axis=1)


def doubly_stochastic_residual(matrix: np.ndarray) -> float:
    return float(
        max(
            np.max(np.abs(np.sum(matrix, axis=0) - 1.0)),
            np.max(np.abs(np.sum(matrix, axis=1) - 1.0)),
            np.max(np.maximum(-matrix, 0.0)),
        )
    )


# ---------------------------------------------------------------------------
# Four-body coupling trees and pentagon coherence
# ---------------------------------------------------------------------------


FOUR_TREES: tuple[tuple[str, tuple[tuple[int, ...], tuple[int, ...]]], ...] = (
    ("(((12)3)4)", ((0, 1), (0, 1, 2))),
    ("((1(23))4)", ((1, 2), (0, 1, 2))),
    ("(1((23)4))", ((1, 2), (1, 2, 3))),
    ("(1(2(34)))", ((2, 3), (1, 2, 3))),
    ("((12)(34))", ((0, 1), (2, 3))),
)


@dataclass
class TreeBasisData:
    name: str
    subsets: tuple[tuple[int, ...], ...]
    basis: np.ndarray
    joint_diagonals: tuple[np.ndarray, ...]
    commutator_residual: float
    diagonalization_residual: float


def joint_tree_basis(total: int, kappas: Sequence[float], name: str, subsets: Sequence[Sequence[int]]) -> TreeBasisData:
    frame = multiplicity_frame(total, kappas)
    restricted = [frame.T @ casimir_matrix(total, kappas, subset) @ frame for subset in subsets]
    commutator = 0.0
    for i in range(len(restricted)):
        for j in range(i + 1, len(restricted)):
            commutator = max(commutator, float(np.max(np.abs(restricted[i] @ restricted[j] - restricted[j] @ restricted[i]))))
    irrational_weights = [math.sqrt(2.0), math.sqrt(3.0), math.sqrt(5.0), math.sqrt(7.0)]
    combined = sum(weight * matrix for weight, matrix in zip(irrational_weights, restricted))
    _, vectors = np.linalg.eigh(combined)
    vectors = sign_fix_columns(vectors)
    diagonals = tuple(vectors.T @ matrix @ vectors for matrix in restricted)
    residual = max(float(np.max(np.abs(diagonal - np.diag(np.diag(diagonal))))) for diagonal in diagonals)
    tuples = []
    for column in range(vectors.shape[1]):
        key = tuple(round(float(diagonal[column, column]), 10) for diagonal in diagonals)
        tuples.append((key, column))
    order = [column for _, column in sorted(tuples, key=lambda item: item[0])]
    vectors = vectors[:, order]
    diagonals = tuple(vectors.T @ matrix @ vectors for matrix in restricted)
    residual = max(float(np.max(np.abs(diagonal - np.diag(np.diag(diagonal))))) for diagonal in diagonals)
    basis = frame @ vectors
    return TreeBasisData(
        name=name,
        subsets=tuple(tuple(int(index) for index in subset) for subset in subsets),
        basis=basis,
        joint_diagonals=diagonals,
        commutator_residual=commutator,
        diagonalization_residual=residual,
    )


def four_body_tree_bases(total: int, kappas: Sequence[float]) -> list[TreeBasisData]:
    if len(kappas) != 4:
        raise ValueError("four_body_tree_bases requires four shapes")
    return [joint_tree_basis(total, kappas, name, subsets) for name, subsets in FOUR_TREES]


def pentagon_product(tree_bases: Sequence[TreeBasisData]) -> tuple[np.ndarray, list[np.ndarray]]:
    overlaps: list[np.ndarray] = []
    dimension = tree_bases[0].basis.shape[1]
    product_matrix = np.eye(dimension)
    for index in range(len(tree_bases)):
        left = tree_bases[index].basis
        right = tree_bases[(index + 1) % len(tree_bases)].basis
        overlap = left.T @ right
        overlaps.append(overlap)
        product_matrix = product_matrix @ overlap
    return product_matrix, overlaps


# ---------------------------------------------------------------------------
# Givens synthesis and finite quantum transforms
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
    diagonal = np.diag(np.diag(matrix))
    return rotations, diagonal


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
# Checks
# ---------------------------------------------------------------------------


def run_checks() -> dict[str, dict[str, float | int | str | bool]]:
    checks: dict[str, dict[str, float | int | str | bool]] = {}

    kappas = (0.7, 1.1, 0.9)
    data = three_body_recoupling(7, kappas)
    expected_left = theoretical_pair_spectrum(7, kappas[0], kappas[1])
    expected_right = theoretical_pair_spectrum(7, kappas[1], kappas[2])
    spectrum_error = max(
        float(np.max(np.abs(data.left_eigenvalues - expected_left))),
        float(np.max(np.abs(data.right_eigenvalues - expected_right))),
    )
    checks["pair_casimir_spectrum"] = {"passed": spectrum_error < 2e-10, "residual": spectrum_error}

    orthogonality_error = float(np.max(np.abs(data.overlap @ data.overlap.T - np.eye(8))))
    checks["three_body_orthogonality"] = {"passed": orthogonality_error < 2e-10, "residual": orthogonality_error}

    n1_numeric = three_body_recoupling(1, kappas).overlap
    n1_exact = one_excitation_closed_form(kappas)
    n1_error = float(np.max(np.abs(n1_numeric - n1_exact)))
    checks["one_excitation_closed_form"] = {"passed": n1_error < 2e-10, "residual": n1_error}

    n2_numeric = three_body_recoupling(2, (0.5, 0.5, 0.5)).overlap
    n2_exact = equal_shape_two_excitation_matrix()
    n2_error = float(np.max(np.abs(n2_numeric - n2_exact)))
    checks["two_excitation_exact_matrix"] = {"passed": n2_error < 2e-10, "residual": n2_error}

    tri_error = tridiagonal_residual(data.right_in_left)
    checks["racah_tridiagonal_selection"] = {"passed": tri_error < 2e-10, "residual": tri_error}

    probability = data.overlap ** 2
    stochastic_error = doubly_stochastic_residual(probability)
    checks["bistochastic_kernel"] = {"passed": stochastic_error < 2e-10, "residual": stochastic_error}

    rng = np.random.default_rng(1007)
    entropy_gaps = []
    for _ in range(100):
        raw = rng.random(probability.shape[0])
        distribution = raw / raw.sum()
        output = distribution @ probability
        input_entropy = -float(np.sum(distribution * np.log(distribution)))
        output_entropy = -float(np.sum(output * np.log(np.maximum(output, 1e-300))))
        entropy_gaps.append(output_entropy - input_entropy)
    minimum_gap = float(min(entropy_gaps))
    checks["entropy_monotonicity"] = {"passed": minimum_gap > -2e-12, "minimum_gap": minimum_gap}

    dimensions_ok = True
    maximum_dimension_error = 0
    for factors in (3, 4, 5):
        for total in range(0, 8):
            frame = multiplicity_frame(total, [0.5 + 0.1 * index for index in range(factors)])
            expected = multiplicity_dimension(total, factors)
            error = abs(frame.shape[1] - expected)
            maximum_dimension_error = max(maximum_dimension_error, error)
            dimensions_ok = dimensions_ok and error == 0
    checks["multiplicity_dimension"] = {"passed": dimensions_ok, "maximum_error": maximum_dimension_error}

    four_kappas = (0.55, 0.8, 1.05, 1.3)
    trees = four_body_tree_bases(4, four_kappas)
    product_matrix, overlaps = pentagon_product(trees)
    pentagon_error = float(np.max(np.abs(product_matrix - np.eye(product_matrix.shape[0]))))
    checks["pentagon_coherence"] = {"passed": pentagon_error < 3e-10, "residual": pentagon_error}

    tree_commutator = max(tree.commutator_residual for tree in trees)
    tree_diagonal = max(tree.diagonalization_residual for tree in trees)
    checks["tree_casimir_commutation"] = {"passed": tree_commutator < 3e-10, "residual": tree_commutator}
    checks["tree_joint_diagonalization"] = {"passed": tree_diagonal < 3e-10, "residual": tree_diagonal}

    rotations, diagonal = givens_decompose(data.overlap)
    reconstructed = givens_reconstruct(rotations, diagonal)
    givens_error = float(np.max(np.abs(reconstructed - data.overlap)))
    checks["givens_reconstruction"] = {
        "passed": givens_error < 3e-10,
        "residual": givens_error,
        "rotation_count": len(rotations),
    }

    equal_probability = three_body_recoupling(8, (0.5, 0.5, 0.5)).overlap ** 2
    symmetry_error = float(np.max(np.abs(equal_probability - equal_probability.T)))
    checks["equal_shape_probability_symmetry"] = {"passed": symmetry_error < 3e-10, "residual": symmetry_error}

    passed = sum(1 for result in checks.values() if bool(result["passed"]))
    summary = {
        "checks": checks,
        "passed": passed,
        "total": len(checks),
        "all_passed": passed == len(checks),
    }
    (RESULTS / "checks.json").write_text(json.dumps(summary, indent=2))
    return checks


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------


def generate_figures() -> list[str]:
    generated: list[str] = []

    # 01. Theory pipeline
    fig, ax = diagram_axes((13.0, 6.3))
    ax.text(0.5, 0.94, "From shape refinement to Racah recoupling", ha="center", fontsize=21, weight="bold")
    stages = [
        (0.04, 0.58, 0.15, 0.17, "Meixner shape\npacket", BLUE),
        (0.23, 0.58, 0.15, 0.17, "positive discrete\nseries", TEAL),
        (0.42, 0.58, 0.15, 0.17, "lowest-weight\nmultiplicity", ORANGE),
        (0.61, 0.58, 0.15, 0.17, "pair-Casimir\nbases", MAGENTA),
        (0.80, 0.58, 0.16, 0.17, "Racah packet\ntransform", RED),
    ]
    for x, y, w, h, label, color in stages:
        box(ax, (x, y), w, h, label, face=color + "1C", edge=color, fontsize=11.5)
    for left, right in zip(stages[:-1], stages[1:]):
        arrow(ax, (left[0] + left[2], left[1] + left[3] / 2), (right[0], right[1] + right[3] / 2), color=INK)
    box(ax, (0.18, 0.19), 0.22, 0.16, "bistochastic\nmeasurement channel", face=YELLOW + "22", edge=YELLOW, fontsize=11.5)
    box(ax, (0.46, 0.19), 0.22, 0.16, "pentagon\ncoherence", face=PURPLE + "1C", edge=PURPLE, fontsize=11.5)
    box(ax, (0.74, 0.19), 0.18, 0.16, "finite quantum\nbasis circuit", face=BLUE + "1C", edge=BLUE, fontsize=11.5)
    arrow(ax, (0.88, 0.58), (0.83, 0.35), color=RED)
    arrow(ax, (0.76, 0.58), (0.57, 0.35), color=MAGENTA)
    arrow(ax, (0.67, 0.58), (0.29, 0.35), color=ORANGE)
    ax.text(0.5, 0.07, "Different refinement trees describe the same total packet space and are connected by exact orthogonal transforms.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "01_theory_pipeline")
    generated.append("01_theory_pipeline")

    # 02. su(1,1) ladder coefficients
    kappa = 0.8
    n = np.arange(0, 14)
    raise_coeff = np.sqrt((n + 1) * (n + 2 * kappa))
    lower_coeff = np.sqrt(n * np.maximum(n + 2 * kappa - 1, 0))
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    ax.plot(n, raise_coeff, marker="o", color=BLUE, label=r"$\sqrt{(n+1)(n+2\kappa)}$")
    ax.plot(n, lower_coeff, marker="s", color=ORANGE, label=r"$\sqrt{n(n+2\kappa-1)}$")
    ax.set_xlabel("packet degree n")
    ax.set_ylabel("ladder coefficient")
    ax.set_title(r"Positive discrete-series ladder at $\kappa=0.8$")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "02_su11_ladder")
    generated.append("02_su11_ladder")

    # 03. Three-factor excitation simplex
    total = 7
    states = compositions(total, 3)
    xy = np.array([[state[0] + 0.5 * state[1], math.sqrt(3) * state[1] / 2] for state in states])
    fig, ax = plt.subplots(figsize=(8.2, 7.1))
    values = np.array([state[0] - state[2] for state in states])
    scatter = ax.scatter(xy[:, 0], xy[:, 1], c=values, cmap="coolwarm", s=80, edgecolor=INK, linewidth=0.5)
    for point, state in zip(xy, states):
        ax.text(point[0], point[1] + 0.17, "".join(map(str, state)), ha="center", fontsize=7.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(r"Total-excitation simplex $n_1+n_2+n_3=7$")
    fig.colorbar(scatter, ax=ax, fraction=0.04, pad=0.02, label=r"$n_1-n_3$")
    save_figure(fig, "03_excitation_simplex")
    generated.append("03_excitation_simplex")

    # 04. Dimension compression
    totals = np.arange(0, 21)
    fig, ax = plt.subplots(figsize=(11.8, 5.5))
    for factors, color in zip((3, 4, 5), (BLUE, TEAL, MAGENTA)):
        full = np.array([excitation_dimension(int(value), factors) for value in totals])
        multiplicity = np.array([multiplicity_dimension(int(value), factors) for value in totals])
        ax.semilogy(totals, full, color=color, linewidth=2.0, label=f"{factors} factors: full level")
        ax.semilogy(totals, multiplicity, color=color, linestyle="--", linewidth=2.0, label=f"{factors} factors: lowest-weight packet")
    ax.set_xlabel("total excitation N")
    ax.set_ylabel("dimension")
    ax.set_title("Projector reduction before recoupling")
    ax.grid(alpha=0.18, which="both")
    ax.legend(ncol=2, fontsize=9)
    save_figure(fig, "04_dimension_compression")
    generated.append("04_dimension_compression")

    # 05. Pair-Casimir spectra
    data = three_body_recoupling(10, (0.7, 1.1, 0.9))
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    index = np.arange(11)
    ax.plot(index, data.left_eigenvalues, marker="o", color=BLUE, label=r"$C_{12}$")
    ax.plot(index, data.right_eigenvalues, marker="s", color=ORANGE, label=r"$C_{23}$")
    ax.set_xlabel("intermediate packet label")
    ax.set_ylabel("Casimir eigenvalue")
    ax.set_title("Two coupling schemes have simple quadratic spectra")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "05_pair_casimir_spectra")
    generated.append("05_pair_casimir_spectra")

    # 06. Shape mixing angle
    middle = np.logspace(-2, 2, 260)
    k1, k3 = 0.7, 1.3
    cosines = np.sqrt(k1 * k3 / ((k1 + middle) * (middle + k3)))
    sines = np.sqrt(middle * (k1 + middle + k3) / ((k1 + middle) * (middle + k3)))
    fig, ax = plt.subplots(figsize=(11.8, 5.4))
    ax.semilogx(middle, cosines, color=BLUE, linewidth=2.2, label=r"$\cos\theta$")
    ax.semilogx(middle, sines, color=ORANGE, linewidth=2.2, label=r"$\sin\theta$")
    ax.axhline(1 / math.sqrt(2), color=GRID, linestyle="--", linewidth=1.2)
    ax.set_xlabel(r"middle shape $\kappa_2$")
    ax.set_ylabel("mixing amplitude")
    ax.set_title(r"One-excitation recoupling is a shape-controlled beam splitter")
    ax.grid(alpha=0.18, which="both")
    ax.legend()
    save_figure(fig, "06_shape_mixing_angle")
    generated.append("06_shape_mixing_angle")

    # 07. One-excitation matrix
    matrix = one_excitation_closed_form((0.7, 1.1, 0.9))
    fig, ax = plt.subplots(figsize=(6.8, 5.8))
    image = ax.imshow(matrix, cmap="coolwarm", vmin=-1, vmax=1)
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{matrix[i,j]:.6f}", ha="center", va="center", fontsize=12, color=WHITE if abs(matrix[i,j]) > 0.55 else INK)
    ax.set_xticks([0, 1], ["right 0", "right 1"])
    ax.set_yticks([0, 1], ["left 0", "left 1"])
    ax.set_title("Exact one-excitation recoupling matrix")
    fig.colorbar(image, ax=ax, fraction=0.05, pad=0.04)
    save_figure(fig, "07_one_excitation_matrix")
    generated.append("07_one_excitation_matrix")

    # 08. Two-excitation exact matrix
    matrix = equal_shape_two_excitation_matrix()
    fig, ax = plt.subplots(figsize=(7.2, 6.1))
    image = ax.imshow(matrix, cmap="coolwarm", vmin=-1, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{matrix[i,j]:.6f}", ha="center", va="center", fontsize=10.5, color=WHITE if abs(matrix[i,j]) > 0.56 else INK)
    ax.set_xticks(range(3), ["right 0", "right 1", "right 2"])
    ax.set_yticks(range(3), ["left 0", "left 1", "left 2"])
    ax.set_title(r"Equal-shape matrix at $N=2$")
    fig.colorbar(image, ax=ax, fraction=0.05, pad=0.04)
    save_figure(fig, "08_two_excitation_exact")
    generated.append("08_two_excitation_exact")

    # 09. General Racah packet heatmap
    data = three_body_recoupling(12, (0.7, 1.1, 0.9))
    fig, ax = plt.subplots(figsize=(8.3, 7.2))
    image = ax.imshow(data.overlap, cmap="coolwarm", vmin=-np.max(np.abs(data.overlap)), vmax=np.max(np.abs(data.overlap)), aspect="auto")
    ax.set_xlabel(r"$C_{23}$ packet label")
    ax.set_ylabel(r"$C_{12}$ packet label")
    ax.set_title("Racah packet transform at total excitation 12")
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03, label="overlap amplitude")
    save_figure(fig, "09_racah_packet_heatmap")
    generated.append("09_racah_packet_heatmap")

    # 10. Bistochastic kernel
    probability = data.overlap ** 2
    fig, ax = plt.subplots(figsize=(8.3, 7.2))
    image = ax.imshow(probability, cmap="viridis", aspect="auto")
    ax.set_xlabel(r"$C_{23}$ measurement outcome")
    ax.set_ylabel(r"$C_{12}$ input packet")
    ax.set_title("Squared recoupling amplitudes form a bistochastic kernel")
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03, label="transition probability")
    save_figure(fig, "10_bistochastic_kernel")
    generated.append("10_bistochastic_kernel")

    # 11. Orthogonality residual
    totals = np.arange(1, 23)
    residuals = []
    for value in totals:
        rec = three_body_recoupling(int(value), (0.7, 1.1, 0.9)).overlap
        residuals.append(np.max(np.abs(rec @ rec.T - np.eye(value + 1))))
    fig, ax = plt.subplots(figsize=(11.8, 5.1))
    ax.semilogy(totals, residuals, marker="o", color=TEAL)
    ax.set_xlabel("total excitation N")
    ax.set_ylabel("maximum orthogonality residual")
    ax.set_title("Numerical orthogonality remains at floating-point scale")
    ax.grid(alpha=0.18, which="both")
    save_figure(fig, "11_orthogonality_residual")
    generated.append("11_orthogonality_residual")

    # 12. Leonard tridiagonal matrix
    data = three_body_recoupling(10, (0.7, 1.1, 0.9))
    fig, ax = plt.subplots(figsize=(8.3, 7.0))
    image = ax.imshow(data.right_in_left, cmap="magma", aspect="auto")
    ax.set_xlabel(r"$C_{12}$ basis column")
    ax.set_ylabel(r"$C_{12}$ basis row")
    ax.set_title(r"$C_{23}$ is tridiagonal in the $C_{12}$ basis")
    fig.colorbar(image, ax=ax, fraction=0.04, pad=0.03, label="matrix entry")
    save_figure(fig, "12_leonard_tridiagonal")
    generated.append("12_leonard_tridiagonal")

    # 13. Recurrence columns
    data = three_body_recoupling(14, (0.7, 1.1, 0.9))
    fig, ax = plt.subplots(figsize=(12.0, 5.5))
    for column, color in zip((0, 2, 5, 9, 14), COLORS[:5]):
        ax.plot(np.arange(15), data.overlap[:, column], marker="o", linewidth=1.5, color=color, label=f"right packet {column}")
    ax.set_xlabel(r"left packet label $r$")
    ax.set_ylabel(r"$R_{r,s}$")
    ax.set_title("Columns are finite Racah packet functions")
    ax.grid(alpha=0.18)
    ax.legend(ncol=3, fontsize=9)
    save_figure(fig, "13_racah_columns")
    generated.append("13_racah_columns")

    # 14. Maximum coherence vs N
    totals = np.arange(1, 31)
    equal_max = []
    unequal_max = []
    for value in totals:
        equal_max.append(np.max(np.abs(three_body_recoupling(int(value), (0.5, 0.5, 0.5)).overlap)))
        unequal_max.append(np.max(np.abs(three_body_recoupling(int(value), (0.7, 1.1, 0.9)).overlap)))
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    ax.plot(totals, equal_max, color=BLUE, marker="o", label="equal shapes")
    ax.plot(totals, unequal_max, color=ORANGE, marker="s", label="unequal shapes")
    ax.set_xlabel("total excitation N")
    ax.set_ylabel(r"$\max_{r,s}|R_{r,s}|$")
    ax.set_title("Coupling-basis coherence across packet depth")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "14_maximum_coherence")
    generated.append("14_maximum_coherence")

    # 15. Row entropy vs N
    entropy_mean = []
    entropy_min = []
    entropy_max = []
    for value in totals:
        probabilities = three_body_recoupling(int(value), (0.7, 1.1, 0.9)).overlap ** 2
        entropies = row_entropies(probabilities)
        entropy_mean.append(np.mean(entropies))
        entropy_min.append(np.min(entropies))
        entropy_max.append(np.max(entropies))
    fig, ax = plt.subplots(figsize=(11.8, 5.4))
    ax.fill_between(totals, entropy_min, entropy_max, color=TEAL, alpha=0.18, label="row range")
    ax.plot(totals, entropy_mean, color=TEAL, linewidth=2.2, label="mean row entropy")
    ax.plot(totals, np.log(totals + 1), color=MUTED, linestyle="--", label=r"$\log(N+1)$")
    ax.set_xlabel("total excitation N")
    ax.set_ylabel("Shannon entropy")
    ax.set_title("A basis packet becomes a spread distribution after recoupling")
    ax.grid(alpha=0.18)
    ax.legend()
    save_figure(fig, "15_row_entropy")
    generated.append("15_row_entropy")

    # 16. Parameter sensitivity heatmap
    middle_values = np.geomspace(0.08, 8.0, 90)
    totals_small = np.arange(1, 11)
    surface = np.zeros((len(totals_small), len(middle_values)))
    for i, value in enumerate(totals_small):
        for j, middle_shape in enumerate(middle_values):
            surface[i, j] = np.max(np.abs(three_body_recoupling(int(value), (0.7, float(middle_shape), 1.3)).overlap))
    fig, ax = plt.subplots(figsize=(12.0, 5.8))
    image = ax.imshow(surface, origin="lower", aspect="auto", extent=[math.log10(middle_values[0]), math.log10(middle_values[-1]), totals_small[0], totals_small[-1]], cmap="viridis")
    ticks = [-1, 0, 1]
    ax.set_xticks(ticks, [r"$10^{-1}$", r"$10^0$", r"$10^1$"])
    ax.set_xlabel(r"middle shape $\kappa_2$")
    ax.set_ylabel("total excitation N")
    ax.set_title("Shape dependence of the largest recoupling amplitude")
    fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02)
    save_figure(fig, "16_parameter_sensitivity")
    generated.append("16_parameter_sensitivity")

    # 17. Bistochastic marginal check
    data = three_body_recoupling(9, (0.7, 1.1, 0.9))
    probability = data.overlap ** 2
    fig, ax = plt.subplots(figsize=(11.8, 5.1))
    ax.plot(np.arange(10), probability.sum(axis=0), marker="o", color=BLUE, label="column sums")
    ax.plot(np.arange(10), probability.sum(axis=1), marker="s", color=ORANGE, label="row sums")
    ax.axhline(1.0, color=INK, linewidth=1.2)
    ax.set_ylim(0.999999999999, 1.000000000001)
    ax.set_xlabel("packet label")
    ax.set_ylabel("marginal sum")
    ax.set_title("Both recoupling marginals equal one")
    ax.legend()
    ax.grid(alpha=0.18)
    save_figure(fig, "17_bistochastic_marginals")
    generated.append("17_bistochastic_marginals")

    # 18. Three-body basis diagram
    fig, ax = diagram_axes((12.8, 6.2))
    ax.text(0.5, 0.94, "Two exact coupling trees on the same three-packet space", ha="center", fontsize=20, weight="bold")
    points_left = {"1": (0.12, 0.68), "2": (0.28, 0.68), "3": (0.44, 0.68), "12": (0.20, 0.43), "123": (0.32, 0.18)}
    points_right = {"1": (0.58, 0.68), "2": (0.74, 0.68), "3": (0.90, 0.68), "23": (0.82, 0.43), "123": (0.70, 0.18)}
    for label, point in points_left.items():
        ax.add_patch(Circle(point, 0.035, facecolor=BLUE + "33", edgecolor=BLUE, linewidth=1.6))
        ax.text(*point, label, ha="center", va="center", fontsize=10)
    for label, point in points_right.items():
        ax.add_patch(Circle(point, 0.035, facecolor=ORANGE + "33", edgecolor=ORANGE, linewidth=1.6))
        ax.text(*point, label, ha="center", va="center", fontsize=10)
    for a, b in [("1", "12"), ("2", "12"), ("12", "123"), ("3", "123")]:
        ax.plot([points_left[a][0], points_left[b][0]], [points_left[a][1], points_left[b][1]], color=BLUE, linewidth=1.8)
    for a, b in [("2", "23"), ("3", "23"), ("1", "123"), ("23", "123")]:
        ax.plot([points_right[a][0], points_right[b][0]], [points_right[a][1], points_right[b][1]], color=ORANGE, linewidth=1.8)
    arrow(ax, (0.42, 0.32), (0.58, 0.32), color=MAGENTA, text="Racah transform", text_offset=(0, 0.05))
    ax.text(0.27, 0.82, r"$((1,2),3)$", ha="center", fontsize=13, color=BLUE, weight="bold")
    ax.text(0.76, 0.82, r"$(1,(2,3))$", ha="center", fontsize=13, color=ORANGE, weight="bold")
    save_figure(fig, "18_three_body_trees")
    generated.append("18_three_body_trees")

    # 19. Four-body associahedron pentagon
    fig, ax = diagram_axes((12.8, 7.0))
    ax.text(0.5, 0.95, "Five four-packet coupling trees form an associahedral pentagon", ha="center", fontsize=20, weight="bold")
    angles = np.linspace(math.pi / 2, math.pi / 2 + 2 * math.pi, 6)[:-1]
    positions = [(0.5 + 0.34 * math.cos(angle), 0.48 + 0.34 * math.sin(angle)) for angle in angles]
    for index, ((name, _), point) in enumerate(zip(FOUR_TREES, positions)):
        ax.add_patch(FancyBboxPatch((point[0] - 0.105, point[1] - 0.055), 0.21, 0.11, boxstyle="round,pad=.008,rounding_size=.015", facecolor=COLORS[index] + "22", edgecolor=COLORS[index], linewidth=1.7))
        ax.text(point[0], point[1], name, ha="center", va="center", fontsize=10.2)
    for index in range(5):
        start = positions[index]
        end = positions[(index + 1) % 5]
        arrow(ax, start, end, color=INK)
    ax.text(0.5, 0.48, r"$R_{01}R_{12}R_{23}R_{34}R_{40}=I$", ha="center", va="center", fontsize=15, weight="bold")
    save_figure(fig, "19_pentagon_trees")
    generated.append("19_pentagon_trees")

    # 20. Pentagon residual
    totals = np.arange(1, 10)
    residuals = []
    dimensions = []
    for value in totals:
        trees = four_body_tree_bases(int(value), (0.55, 0.8, 1.05, 1.3))
        product_matrix, _ = pentagon_product(trees)
        residuals.append(np.max(np.abs(product_matrix - np.eye(product_matrix.shape[0]))))
        dimensions.append(product_matrix.shape[0])
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    ax.semilogy(totals, residuals, marker="o", color=PURPLE)
    for x, y, dimension in zip(totals, residuals, dimensions):
        ax.text(x, y * 1.25, str(dimension), ha="center", fontsize=8, color=MUTED)
    ax.set_xlabel("total excitation N")
    ax.set_ylabel("pentagon residual")
    ax.set_title("Pentagon closure on growing multiplicity spaces")
    ax.grid(alpha=0.18, which="both")
    save_figure(fig, "20_pentagon_residual")
    generated.append("20_pentagon_residual")

    # 21. Five edge-overlap heatmaps
    trees = four_body_tree_bases(3, (0.55, 0.8, 1.05, 1.3))
    _, overlaps = pentagon_product(trees)
    fig, axes = plt.subplots(1, 5, figsize=(14.0, 3.5))
    vmax = max(np.max(np.abs(matrix)) for matrix in overlaps)
    for index, (axis, matrix) in enumerate(zip(axes, overlaps)):
        image = axis.imshow(matrix, cmap="coolwarm", vmin=-vmax, vmax=vmax, aspect="auto")
        axis.set_title(f"edge {index+1}", fontsize=9.5)
        axis.set_xticks([])
        axis.set_yticks([])
    fig.colorbar(image, ax=axes.ravel().tolist(), fraction=0.018, pad=0.02, label="overlap amplitude")
    fig.suptitle("The five elementary associators at total excitation 3", fontsize=15, weight="bold")
    fig.subplots_adjust(left=0.03, right=0.92, bottom=0.10, top=0.78, wspace=0.10)
    save_figure(fig, "21_pentagon_edge_kernels")
    generated.append("21_pentagon_edge_kernels")

    # 22. Joint spectra for one four-body tree
    tree = trees[0]
    diagonal_a = np.diag(tree.joint_diagonals[0])
    diagonal_b = np.diag(tree.joint_diagonals[1])
    fig, ax = plt.subplots(figsize=(8.0, 6.3))
    scatter = ax.scatter(diagonal_a, diagonal_b, c=np.arange(len(diagonal_a)), cmap="viridis", s=90, edgecolor=INK, linewidth=0.5)
    for index, (x, y) in enumerate(zip(diagonal_a, diagonal_b)):
        ax.text(x, y + 0.2, str(index), ha="center", fontsize=8)
    ax.set_xlabel("inner Casimir eigenvalue")
    ax.set_ylabel("nested Casimir eigenvalue")
    ax.set_title("Joint packet labels for one four-body tree")
    fig.colorbar(scatter, ax=ax, fraction=0.04, pad=0.03, label="basis index")
    ax.grid(alpha=0.15)
    save_figure(fig, "22_joint_tree_spectrum")
    generated.append("22_joint_tree_spectrum")

    # 23. Four-body compression ratio
    totals = np.arange(0, 23)
    full = np.array([excitation_dimension(int(value), 4) for value in totals])
    packet = np.array([multiplicity_dimension(int(value), 4) for value in totals])
    ratio = full / packet
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    ax.plot(totals, ratio, color=BLUE, marker="o")
    ax.set_xlabel("total excitation N")
    ax.set_ylabel("full level / multiplicity dimension")
    ax.set_title("Four-body projector reduction before associator synthesis")
    ax.grid(alpha=0.18)
    save_figure(fig, "23_four_body_compression")
    generated.append("23_four_body_compression")

    # 24. Givens circuit schematic
    dimension = 6
    fig, ax = diagram_axes((12.8, 6.2))
    ax.text(0.5, 0.94, "Finite recoupling transform as a triangular Givens network", ha="center", fontsize=20, weight="bold")
    x_positions = np.linspace(0.08, 0.92, 8)
    y_positions = np.linspace(0.18, 0.78, dimension)
    for y in y_positions:
        ax.plot([x_positions[0], x_positions[-1]], [y, y], color=GRID, linewidth=1.3)
    gate_index = 0
    for column in range(dimension - 1):
        x = x_positions[column + 1]
        for row in range(dimension - 1, column, -1):
            y0, y1 = y_positions[row - 1], y_positions[row]
            ax.plot([x, x], [y0, y1], color=COLORS[gate_index % len(COLORS)], linewidth=3.2)
            ax.add_patch(Circle((x, y0), 0.012, facecolor=WHITE, edgecolor=COLORS[gate_index % len(COLORS)], linewidth=1.4))
            ax.add_patch(Circle((x, y1), 0.012, facecolor=COLORS[gate_index % len(COLORS)], edgecolor=COLORS[gate_index % len(COLORS)], linewidth=1.4))
            gate_index += 1
            x += 0.012
    for index, y in enumerate(y_positions):
        ax.text(0.045, y, str(index), ha="center", va="center", fontsize=9)
    ax.text(0.5, 0.08, r"At most $d(d-1)/2$ real plane rotations plus diagonal signs", ha="center", fontsize=12, color=MUTED)
    save_figure(fig, "24_givens_network")
    generated.append("24_givens_network")

    # 25. Deterministic complexity profiles
    totals = np.arange(2, 25, 2)
    dimensions = totals + 1
    dense_proxy = dimensions.astype(float) ** 3
    full_transform_proxy = dimensions.astype(float) ** 2
    selected_column_proxy = dimensions.astype(float)
    dense_proxy /= dense_proxy[0]
    full_transform_proxy /= full_transform_proxy[0]
    selected_column_proxy /= selected_column_proxy[0]
    fig, ax = plt.subplots(figsize=(11.8, 5.3))
    ax.loglog(dimensions, dense_proxy, marker="o", color=TEAL, label=r"dense reduced eigensolve $d^3$")
    ax.loglog(dimensions, full_transform_proxy, marker="o", color=BLUE, label=r"structured full transform $d^2$")
    ax.loglog(dimensions, selected_column_proxy, marker="o", color=ORANGE, label=r"selected recurrence column $d$")
    ax.set_xlabel("multiplicity dimension d=N+1")
    ax.set_ylabel("normalized cost proxy")
    ax.set_title("Reference complexity profiles in the multiplicity packet")
    ax.grid(alpha=0.18, which="both")
    ax.legend()
    save_figure(fig, "25_runtime_scaling")
    generated.append("25_runtime_scaling")

    # 26. Packet algorithm flow
    fig, ax = diagram_axes((13.0, 6.5))
    ax.text(0.5, 0.95, "Output-sensitive recoupling algorithm", ha="center", fontsize=21, weight="bold")
    stages = [
        (0.06, 0.66, 0.18, 0.15, "declare shapes\nand total degree", BLUE),
        (0.31, 0.66, 0.18, 0.15, "project to\nlowest weight", TEAL),
        (0.56, 0.66, 0.18, 0.15, "diagonalize pair\nCasimirs", ORANGE),
        (0.79, 0.66, 0.16, 0.15, "form overlap\nkernel", MAGENTA),
        (0.18, 0.25, 0.22, 0.15, "square amplitudes\nfor Markov channel", YELLOW),
        (0.47, 0.25, 0.20, 0.15, "compose trees\nthrough pentagon", PURPLE),
        (0.74, 0.25, 0.18, 0.15, "compile Givens\nnetwork", RED),
    ]
    for x, y, w, h, text, color in stages:
        box(ax, (x, y), w, h, text, face=color + "20", edge=color, fontsize=11)
    for a, b in [(0, 1), (1, 2), (2, 3)]:
        left, right = stages[a], stages[b]
        arrow(ax, (left[0] + left[2], left[1] + left[3] / 2), (right[0], right[1] + right[3] / 2), color=INK)
    arrow(ax, (0.87, 0.66), (0.83, 0.40), color=MAGENTA)
    arrow(ax, (0.72, 0.66), (0.57, 0.40), color=ORANGE)
    arrow(ax, (0.64, 0.66), (0.29, 0.40), color=TEAL)
    ax.text(0.5, 0.08, "The full tensor level is used only to define the projector. Every later step occurs in the multiplicity packet space.", ha="center", fontsize=11.5, color=MUTED)
    save_figure(fig, "26_packet_algorithm")
    generated.append("26_packet_algorithm")

    # 27. Classical-family map
    fig, ax = diagram_axes((13.0, 6.5))
    ax.text(0.5, 0.95, "Where the generated recoupling functions sit in the classical hierarchy", ha="center", fontsize=20, weight="bold")
    nodes = [
        (0.08, 0.68, 0.20, 0.14, "Meixner-Pollaczek\npacket basis", BLUE),
        (0.40, 0.68, 0.20, 0.14, "Clebsch-Gordan\nHahn coordinates", TEAL),
        (0.72, 0.68, 0.20, 0.14, "Racah\nrecoupling", ORANGE),
        (0.21, 0.30, 0.20, 0.14, "Jacobi and\ncontinuous limits", MAGENTA),
        (0.52, 0.30, 0.20, 0.14, "Wilson-function\nextensions", PURPLE),
        (0.78, 0.30, 0.16, 0.14, "q-Racah and\nAskey-Wilson", RED),
    ]
    for x, y, w, h, text, color in nodes:
        box(ax, (x, y), w, h, text, face=color + "1E", edge=color, fontsize=11)
    arrow(ax, (0.28, 0.75), (0.40, 0.75), color=INK)
    arrow(ax, (0.60, 0.75), (0.72, 0.75), color=INK)
    arrow(ax, (0.82, 0.68), (0.62, 0.44), color=ORANGE)
    arrow(ax, (0.50, 0.68), (0.31, 0.44), color=TEAL)
    arrow(ax, (0.72, 0.37), (0.78, 0.37), color=PURPLE)
    ax.text(0.5, 0.10, "The classical names are retained. The packet calculus supplies the common refinement and associator interpretation.", ha="center", fontsize=11.3, color=MUTED)
    save_figure(fig, "27_classical_family_map")
    generated.append("27_classical_family_map")

    # 28. Quantum/logarithmic connection
    fig, ax = diagram_axes((13.0, 6.5))
    ax.text(0.5, 0.95, "Two quantum coordinates in the extended calculus", ha="center", fontsize=20, weight="bold")
    box(ax, (0.07, 0.60), 0.22, 0.18, "number basis\n$|n\\rangle$", face=BLUE + "1E", edge=BLUE, fontsize=13)
    box(ax, (0.39, 0.60), 0.22, 0.18, "logarithmic phase\n$e^{-it\\log n}$", face=TEAL + "1E", edge=TEAL, fontsize=12)
    box(ax, (0.71, 0.60), 0.22, 0.18, "shape ladder\n$D^+_{\\kappa}$", face=ORANGE + "1E", edge=ORANGE, fontsize=13)
    box(ax, (0.20, 0.22), 0.24, 0.17, "dynamical zeta\nobservable", face=MAGENTA + "1E", edge=MAGENTA, fontsize=12)
    box(ax, (0.58, 0.22), 0.24, 0.17, "finite Racah\nbasis transform", face=PURPLE + "1E", edge=PURPLE, fontsize=12)
    arrow(ax, (0.29, 0.69), (0.39, 0.69), color=INK)
    arrow(ax, (0.61, 0.69), (0.71, 0.69), color=INK)
    arrow(ax, (0.48, 0.60), (0.32, 0.39), color=TEAL)
    arrow(ax, (0.82, 0.60), (0.70, 0.39), color=ORANGE)
    ax.text(0.5, 0.08, "The logarithmic Hamiltonian and the shape recoupling transform are distinct modules and can be composed without identifying their spectra.", ha="center", fontsize=11.2, color=MUTED)
    save_figure(fig, "28_quantum_connection")
    generated.append("28_quantum_connection")

    # 29. Theorem dependency map
    fig, ax = diagram_axes((13.0, 6.8))
    ax.text(0.5, 0.96, "Theorem dependency map", ha="center", fontsize=21, weight="bold")
    nodes = [
        (0.05, 0.73, 0.20, 0.12, "positive discrete\nseries", BLUE),
        (0.30, 0.73, 0.20, 0.12, "lowest-weight\nprojector", TEAL),
        (0.55, 0.73, 0.20, 0.12, "pair Casimir\nspectra", ORANGE),
        (0.80, 0.73, 0.15, 0.12, "orthogonal\noverlap", MAGENTA),
        (0.12, 0.43, 0.20, 0.12, "Racah\nrecurrence", YELLOW),
        (0.40, 0.43, 0.20, 0.12, "bistochastic\nchannel", PURPLE),
        (0.68, 0.43, 0.20, 0.12, "four-body\npentagon", RED),
        (0.27, 0.14, 0.20, 0.12, "entropy and\nuncertainty", BLUE),
        (0.56, 0.14, 0.20, 0.12, "finite quantum\ncompiler", TEAL),
    ]
    for x, y, w, h, text, color in nodes:
        box(ax, (x, y), w, h, text, face=color + "1C", edge=color, fontsize=10.5)
    for left, right in [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (3, 6), (5, 7), (6, 8)]:
        a, b = nodes[left], nodes[right]
        arrow(ax, (a[0] + a[2] / 2, a[1]), (b[0] + b[2] / 2, b[1] + b[3]), color=INK)
    save_figure(fig, "29_theorem_map")
    generated.append("29_theorem_map")

    # 30. Future hierarchy
    fig, ax = diagram_axes((13.0, 6.4))
    ax.text(0.5, 0.95, "Next deformation directions", ha="center", fontsize=21, weight="bold")
    box(ax, (0.06, 0.58), 0.20, 0.18, "current paper\nfinite $SU(1,1)$\nRacah packets", face=BLUE + "20", edge=BLUE, fontsize=12)
    box(ax, (0.34, 0.58), 0.20, 0.18, "continuous series\nWilson functions", face=TEAL + "20", edge=TEAL, fontsize=12)
    box(ax, (0.62, 0.58), 0.20, 0.18, "$q$-deformation\nAskey-Wilson packets", face=ORANGE + "20", edge=ORANGE, fontsize=12)
    box(ax, (0.24, 0.20), 0.22, 0.16, "multivariate\n$3nj$ packet trees", face=MAGENTA + "20", edge=MAGENTA, fontsize=12)
    box(ax, (0.56, 0.20), 0.22, 0.16, "tensor-network and\nquantum circuits", face=PURPLE + "20", edge=PURPLE, fontsize=12)
    arrow(ax, (0.26, 0.67), (0.34, 0.67), color=INK)
    arrow(ax, (0.54, 0.67), (0.62, 0.67), color=INK)
    arrow(ax, (0.16, 0.58), (0.35, 0.36), color=BLUE)
    arrow(ax, (0.72, 0.58), (0.67, 0.36), color=ORANGE)
    ax.text(0.5, 0.08, "Each extension keeps the same rule: declare a complete coupling atlas, compute the associator, and certify reconstruction.", ha="center", fontsize=11.4, color=MUTED)
    save_figure(fig, "30_future_directions")
    generated.append("30_future_directions")

    return generated


# ---------------------------------------------------------------------------
# Tables and manifest
# ---------------------------------------------------------------------------


def write_tables() -> None:
    kappas = (0.7, 1.1, 0.9)
    rows = []
    for total in range(1, 13):
        data = three_body_recoupling(total, kappas)
        probability = data.overlap ** 2
        rows.append(
            {
                "N": total,
                "dimension": total + 1,
                "max_abs_overlap": float(np.max(np.abs(data.overlap))),
                "mean_row_entropy": float(np.mean(row_entropies(probability))),
                "orthogonality_residual": float(np.max(np.abs(data.overlap @ data.overlap.T - np.eye(total + 1)))),
                "tridiagonal_residual": tridiagonal_residual(data.right_in_left),
            }
        )
    with (TABLES / "three_body_metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    pentagon_rows = []
    for total in range(1, 8):
        trees = four_body_tree_bases(total, (0.55, 0.8, 1.05, 1.3))
        product_matrix, _ = pentagon_product(trees)
        pentagon_rows.append(
            {
                "N": total,
                "multiplicity_dimension": product_matrix.shape[0],
                "pentagon_residual": float(np.max(np.abs(product_matrix - np.eye(product_matrix.shape[0])))),
                "max_commutator_residual": max(tree.commutator_residual for tree in trees),
                "max_joint_diagonalization_residual": max(tree.diagonalization_residual for tree in trees),
            }
        )
    with (TABLES / "pentagon_metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pentagon_rows[0].keys()))
        writer.writeheader()
        writer.writerows(pentagon_rows)

    exact_matrix = sp.Matrix(equal_shape_two_excitation_matrix()).applyfunc(lambda value: sp.nsimplify(value))
    (GENERATED / "equal_shape_N2_matrix.tex").write_text(sp.latex(exact_matrix))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(figures: Sequence[str], checks: dict[str, dict[str, float | int | str | bool]]) -> None:
    manifest = {
        "title": "Projector-Generated Special Functions VII",
        "author": "Komorebi P.",
        "figure_pairs": len(figures),
        "figures": list(figures),
        "checks_passed": sum(1 for item in checks.values() if bool(item["passed"])),
        "checks_total": len(checks),
        "files": {},
    }
    for path in sorted(ROOT.rglob("*")):
        if path.is_file() and path.name not in {"manifest.json", "SHA256SUMS.txt"}:
            manifest["files"][str(path.relative_to(ROOT))] = {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
    (RESULTS / "manifest.json").write_text(json.dumps(manifest, indent=2))
    lines = [f"{entry['sha256']}  {name}" for name, entry in manifest["files"].items()]
    (ROOT / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n")


def main() -> None:
    figures = generate_figures()
    checks = run_checks()
    write_tables()
    write_manifest(figures, checks)
    summary = {
        "figures": len(figures),
        "checks_passed": sum(1 for item in checks.values() if bool(item["passed"])),
        "checks_total": len(checks),
        "all_passed": all(bool(item["passed"]) for item in checks.values()),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
