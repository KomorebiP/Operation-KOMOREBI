import numpy as np

from projector_transfer_semigroups.feynman_kac import discrete_feynman_kac, enumerate_feynman_kac
from projector_transfer_semigroups.semigroup import (
    generator_refinement_defect,
    semigroup_refinement_residual,
    duhamel_defect_integral,
)


def test_feynman_kac_enumeration() -> None:
    k = np.array([[0.75, 0.25], [0.25, 0.75]])
    v = np.array([0.15, 0.7])
    f = np.array([1.0, 2.0])
    for n in range(7):
        assert np.max(np.abs(discrete_feynman_kac(k, v, f, n) - enumerate_feynman_kac(k, v, f, n))) < 1e-13


def _refinement_system():
    coarse = np.array([[-0.4, 0.2], [0.4, -0.2]])
    c = np.array([[0.5, 0.5, 0.0, 0.0], [0.0, 0.0, 0.5, 0.5]])
    e = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [0.0, 1.0]])
    micro = np.array([[-1.0, 1.0, 0.0, 0.0], [1.0, -1.0, 0.0, 0.0], [0.0, 0.0, -1.3, 1.3], [0.0, 0.0, 1.3, -1.3]])
    fine = e @ coarse @ c + micro
    return c, fine, coarse


def test_exact_generator_intertwining_implies_semigroup_intertwining() -> None:
    c, fine, coarse = _refinement_system()
    assert np.max(np.abs(generator_refinement_defect(c, fine, coarse))) < 1e-15
    for t in (0.1, 0.8, 2.0):
        assert np.max(np.abs(semigroup_refinement_residual(c, fine, coarse, t))) < 2e-14


def test_duhamel_defect_identity() -> None:
    c, fine, coarse = _refinement_system()
    perturbation = np.array([[0.02, 0.0, -0.01, 0.0], [0.0, -0.02, 0.0, 0.01], [-0.02, 0.0, 0.01, 0.0], [0.0, 0.02, 0.0, -0.01]])
    fp = fine + perturbation
    for t in (0.2, 0.85, 1.5):
        direct = semigroup_refinement_residual(c, fp, coarse, t)
        integral = duhamel_defect_integral(c, fp, coarse, t)
        assert np.max(np.abs(direct - integral)) < 2e-10
