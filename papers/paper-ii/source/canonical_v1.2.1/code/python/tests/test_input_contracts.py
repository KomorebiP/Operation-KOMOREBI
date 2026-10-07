import numpy as np
import pytest

from seed_refinement.dyadic import (
    odd_prime_sign_projectors,
    smith_diagonal_solve,
    valuation,
)
from seed_refinement.projectors import (
    analyze_residues,
    crt_index,
    dyadic_odd_index,
    refinement_incidence,
    synthesize_residues,
)
from seed_refinement.smith_chart import phase_transform, polyphase_orbit
from seed_refinement.stability import (
    compatible_replication_tower,
    defect_norm_bound,
    power_defect,
    power_defect_expansion,
)
from seed_refinement.weighted import (
    Edge,
    direct_inverse_mod,
    neumann_inverse_mod,
    path_counts,
    path_zeta,
)


def test_residue_contracts_reject_invalid_shapes() -> None:
    with pytest.raises(ValueError):
        analyze_residues([1, 2], 0)
    with pytest.raises(ValueError):
        refinement_incidence(4, 6)
    with pytest.raises(ValueError):
        synthesize_residues([[1], [2, 3]])


def test_crt_contracts_reject_invalid_moduli() -> None:
    with pytest.raises(ValueError):
        crt_index(0, 3, 0, 0)
    with pytest.raises(ValueError):
        crt_index(4, 6, 1, 1)
    with pytest.raises(ValueError):
        dyadic_odd_index(6, 3, 0, 0)


def test_weighted_contracts_reject_invalid_data() -> None:
    with pytest.raises(ValueError):
        Edge(0, 1, 0)
    with pytest.raises(ValueError):
        path_counts(2, [Edge(0, 2, 1)], [0], [1], 3)
    with pytest.raises(ValueError):
        path_zeta(2, [], [2], [1])
    with pytest.raises(ValueError):
        direct_inverse_mod(np.eye(1), np.zeros((1, 1)), 2, 0)


@pytest.mark.parametrize(
    ("weight", "multiplicity"),
    [(1.5, 1), (True, 1), (1, 2.5), (1, False), (-1, 1), (1, 0)],
)
def test_edges_require_positive_integral_weight_and_multiplicity(
    weight: object, multiplicity: object
) -> None:
    with pytest.raises(ValueError):
        Edge(0, 1, weight, multiplicity)  # type: ignore[arg-type]


def test_arithmetic_and_chart_contracts_reject_invalid_data() -> None:
    with pytest.raises(ValueError):
        valuation(0, 2)
    with pytest.raises(ValueError):
        smith_diagonal_solve([1], [0], 1, 3)
    with pytest.raises(ValueError):
        odd_prime_sign_projectors(np.eye(2), 2)
    with pytest.raises(ValueError):
        phase_transform(2 + 1j, 0, 0)
    with pytest.raises(ValueError):
        polyphase_orbit(1.0, 4)
    with pytest.raises(ValueError):
        polyphase_orbit(0.5, 0)


@pytest.mark.parametrize("composite", [1, 4, 9, 15])
def test_prime_power_apis_reject_nonprimes(composite: int) -> None:
    with pytest.raises(ValueError, match="prime integer"):
        valuation(8, composite)
    with pytest.raises(ValueError, match="prime integer"):
        smith_diagonal_solve([1], [0], composite, 2)
    with pytest.raises(ValueError, match="prime integer"):
        direct_inverse_mod(np.eye(1, dtype=int), np.zeros((1, 1), dtype=int), composite, 2)
    with pytest.raises(ValueError, match="prime integer"):
        neumann_inverse_mod(np.eye(1, dtype=int), np.zeros((1, 1), dtype=int), composite, 2)


def test_sign_projectors_require_an_integral_involution() -> None:
    with pytest.raises(ValueError, match="involution"):
        odd_prime_sign_projectors(np.array([[1, 1], [0, 1]], dtype=int), 5)
    with pytest.raises(ValueError, match="entries must be integers"):
        odd_prime_sign_projectors(np.array([[1.0, 0.0], [0.0, -1.0]]), 5)
    with pytest.raises(ValueError, match="prime integer"):
        odd_prime_sign_projectors(np.eye(2, dtype=int), 9)


def test_refinement_tower_contracts_reject_invalid_shapes_and_powers() -> None:
    with pytest.raises(ValueError, match="one-dimensional"):
        compatible_replication_tower(np.ones((2, 2)), 2)
    with pytest.raises(ValueError, match="nonempty"):
        compatible_replication_tower(np.array([]), 2)
    with pytest.raises(ValueError, match="finite"):
        compatible_replication_tower(np.array([1.0, np.inf]), 2)
    with pytest.raises(ValueError, match="positive integer"):
        compatible_replication_tower(np.array([1.0]), 1.5)  # type: ignore[arg-type]

    coarsen = np.ones((2, 3))
    fine = np.eye(4)
    coarse = np.eye(2)
    with pytest.raises(ValueError, match="fine_operator shape"):
        power_defect(coarsen, fine, coarse)
    with pytest.raises(ValueError, match="power must be a positive integer"):
        power_defect_expansion(np.ones((2, 3)), np.eye(3), np.eye(2), 0)
    with pytest.raises(ValueError, match="power must be a positive integer"):
        defect_norm_bound(np.ones((2, 3)), np.eye(3), np.eye(2), 0)
