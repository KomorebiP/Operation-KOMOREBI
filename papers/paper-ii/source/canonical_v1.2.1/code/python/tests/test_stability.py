import numpy as np
import pytest

from seed_refinement.stability import (
    compatible_replication_tower,
    defect_norm_bound,
    power_defect,
    power_defect_expansion,
    resolvent_defect,
)


def test_exact_replication_tower() -> None:
    E, C, Tf, Tc = compatible_replication_tower(np.array([0.4, 0.8, 1.3]), 4)
    assert np.linalg.norm(C @ E - np.eye(3)) < 1e-12
    assert np.linalg.norm(power_defect(C, Tf, Tc)) < 1e-12
    for n in range(1, 9):
        assert np.linalg.norm(C @ np.linalg.matrix_power(Tf, n) - np.linalg.matrix_power(Tc, n) @ C) < 1e-12


def test_power_defect_telescoping_identity() -> None:
    E, C, Tf, Tc = compatible_replication_tower(np.array([0.4, 0.8, 1.3]), 3)
    Tf[0, 0] += 0.09
    for n in range(1, 10):
        lhs = C @ np.linalg.matrix_power(Tf, n) - np.linalg.matrix_power(Tc, n) @ C
        rhs = power_defect_expansion(C, Tf, Tc, n)
        assert np.linalg.norm(lhs - rhs) < 1e-10


def test_power_defect_bound() -> None:
    _, C, Tf, Tc = compatible_replication_tower(np.array([0.4, 0.8, 1.3]), 3)
    Tf[0, 0] += 0.09
    for n in range(1, 10):
        actual, bound = defect_norm_bound(C, Tf, Tc, n)
        assert actual <= bound + 1e-10


def test_resolvent_defect_identity() -> None:
    _, C, Tf, Tc = compatible_replication_tower(np.array([0.4, 0.8, 1.3]), 3)
    Tf[0, 0] += 0.09
    lhs, rhs = resolvent_defect(C, Tf, Tc, 3.1 + 0.7j)
    assert np.linalg.norm(lhs - rhs) < 1e-10


def test_all_defect_apis_reject_incompatible_tower_shapes() -> None:
    C = np.ones((2, 3))
    Tf = np.eye(3)
    wrong_Tc = np.eye(3)
    with pytest.raises(ValueError, match="coarse_operator shape"):
        power_defect(C, Tf, wrong_Tc)
    with pytest.raises(ValueError, match="coarse_operator shape"):
        power_defect_expansion(C, Tf, wrong_Tc, 2)
    with pytest.raises(ValueError, match="coarse_operator shape"):
        resolvent_defect(C, Tf, wrong_Tc, 2.0)
    with pytest.raises(ValueError, match="coarse_operator shape"):
        defect_norm_bound(C, Tf, wrong_Tc, 2)
