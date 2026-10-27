import numpy as np
from scipy.linalg import expm

from projector_transfer_semigroups.conditional import (
    weighted_conditional_expectation,
    martingale_differences,
    gaussian_hermite_gram,
)
from projector_transfer_semigroups.fractional import (
    spectral_fractional_power,
    fractional_semigroup,
    scalar_square_root_subordination,
)
from projector_transfer_semigroups.pde import (
    dirichlet_laplacian_1d,
    continuous_dirichlet_green,
    discrete_green_scaled,
    low_mode_eigenvalue_error,
)


def test_conditional_expectation_projector_and_tower() -> None:
    pi = np.ones(8) / 8
    coarse = weighted_conditional_expectation([list(range(4)), list(range(4, 8))], pi)
    fine = weighted_conditional_expectation([[0, 1], [2, 3], [4, 5], [6, 7]], pi)
    assert np.max(np.abs(coarse @ coarse - coarse)) < 1e-15
    assert np.max(np.abs(fine @ fine - fine)) < 1e-15
    assert np.max(np.abs(coarse @ fine - coarse)) < 1e-15
    assert np.max(np.abs(fine @ coarse - coarse)) < 1e-15


def test_martingale_differences_orthogonal() -> None:
    pi = np.ones(8) / 8
    projectors = [
        weighted_conditional_expectation([list(range(8))], pi),
        weighted_conditional_expectation([list(range(4)), list(range(4, 8))], pi),
        weighted_conditional_expectation([[0, 1], [2, 3], [4, 5], [6, 7]], pi),
        np.eye(8),
    ]
    ds = martingale_differences(projectors)
    for i in range(len(ds)):
        assert np.max(np.abs(ds[i] @ ds[i] - ds[i])) < 1e-15
        for j in range(len(ds)):
            if i != j:
                assert np.max(np.abs(ds[i] @ ds[j])) < 1e-15


def test_hermite_orthogonality() -> None:
    gram = gaussian_hermite_gram(8, 80)
    assert np.max(np.abs(gram - np.eye(9))) < 1e-12


def test_fractional_power_square() -> None:
    a = np.array([[2.0, -1.0], [-1.0, 2.0]])
    root = spectral_fractional_power(a, 0.5)
    assert np.max(np.abs(root @ root - a)) < 1e-12


def test_fractional_semigroup_law() -> None:
    a, _, _ = dirichlet_laplacian_1d(16)
    left = fractional_semigroup(a, 0.6, 0.2) @ fractional_semigroup(a, 0.6, 0.35)
    right = fractional_semigroup(a, 0.6, 0.55)
    assert np.max(np.abs(left - right)) < 1e-12


def test_square_root_subordination() -> None:
    for lam in (0.25, 1.0, 4.0, 9.0):
        numeric = scalar_square_root_subordination(lam, 0.7)
        exact = np.exp(-0.7 * np.sqrt(lam))
        assert abs(numeric - exact) < 2e-10


def test_discrete_green_is_exact_at_grid_nodes() -> None:
    for n in (7, 15, 31, 63):
        discrete, grid, _ = discrete_green_scaled(n)
        exact = continuous_dirichlet_green(grid, grid)
        assert np.max(np.abs(discrete - exact)) < 2e-14


def test_low_mode_second_order() -> None:
    n1, n2 = 63, 127
    h1, h2 = 1 / (n1 + 1), 1 / (n2 + 1)
    e1 = low_mode_eigenvalue_error(n1, 1)
    e2 = low_mode_eigenvalue_error(n2, 1)
    observed = np.log(e1 / e2) / np.log(h1 / h2)
    assert 1.95 < observed < 2.05


def test_heat_semigroup_positive_contraction() -> None:
    lap, _, _ = dirichlet_laplacian_1d(24)
    heat = expm(-0.05 * lap)
    assert np.min(heat) > -1e-13
    assert np.linalg.norm(heat, 2) <= 1 + 1e-12


def test_fractional_naturality_exact_intertwining() -> None:
    from projector_transfer_semigroups.fractional import (
        generator_intertwining_defect,
        fractional_intertwining_defect,
        fractional_semigroup_intertwining_defect,
    )

    fine = np.diag([0.0, 1.0, 2.0, 4.0])
    coarse = np.diag([0.0, 2.0])
    coarsener = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0]])
    assert np.linalg.norm(generator_intertwining_defect(fine, coarse, coarsener), 2) < 1e-14
    assert np.linalg.norm(fractional_intertwining_defect(fine, coarse, coarsener, 0.37), 2) < 1e-14
    assert np.linalg.norm(
        fractional_semigroup_intertwining_defect(fine, coarse, coarsener, 0.37, 0.8), 2
    ) < 1e-14


def test_fractional_holder_defect_bound_without_spectral_gap() -> None:
    from projector_transfer_semigroups.fractional import (
        fractional_holder_bound,
        fractional_intertwining_defect,
    )

    fine = np.array(
        [
            [1.0, -1.0, 0.0, 0.0],
            [-1.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 2.0, -2.0],
            [0.0, 0.0, -2.0, 2.0],
        ]
    )
    coarse = np.array([[0.5, -0.5], [-0.5, 0.5]])
    coarsener = np.array([[0.6, 0.4, 0.1, -0.1], [0.0, 0.2, 0.5, 0.3]])
    alpha = 0.63
    actual = np.linalg.norm(fractional_intertwining_defect(fine, coarse, coarsener, alpha), 2)
    bound = fractional_holder_bound(fine, coarse, coarsener, alpha)
    assert actual <= bound * (1.0 + 2e-12)


def test_fractional_gap_defect_bound() -> None:
    from projector_transfer_semigroups.fractional import (
        fractional_gap_bound,
        fractional_intertwining_defect,
    )

    fine = np.diag([0.4, 1.1, 2.0, 3.8])
    coarse = np.array([[0.7, -0.1], [-0.1, 1.6]])
    coarsener = np.array([[0.7, 0.1, 0.2, 0.0], [0.0, 0.3, 0.2, 0.8]])
    alpha = 0.42
    actual = np.linalg.norm(fractional_intertwining_defect(fine, coarse, coarsener, alpha), 2)
    bound = fractional_gap_bound(fine, coarse, coarsener, alpha)
    assert actual <= bound * (1.0 + 2e-12)


def test_fractional_semigroup_duhamel_bound() -> None:
    from projector_transfer_semigroups.fractional import (
        fractional_semigroup_bound,
        fractional_semigroup_intertwining_defect,
    )

    fine = np.diag([0.45, 0.9, 1.8, 3.2])
    coarse = np.array([[0.6, -0.08], [-0.08, 1.4]])
    coarsener = np.array([[0.8, 0.1, 0.0, 0.2], [0.0, 0.25, 0.5, 0.55]])
    alpha = 0.58
    time = 0.75
    actual = np.linalg.norm(
        fractional_semigroup_intertwining_defect(fine, coarse, coarsener, alpha, time), 2
    )
    bound = fractional_semigroup_bound(
        fine, coarse, coarsener, alpha, time, use_gap=True
    )
    assert actual <= bound * (1.0 + 2e-12)
