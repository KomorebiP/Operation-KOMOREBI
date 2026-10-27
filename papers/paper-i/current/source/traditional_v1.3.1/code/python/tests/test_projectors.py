import numpy as np

from seed_calculus.core import analysis, projector_residuals, reconstruct_operator, synthesis, transfer_blocks, transport_projectors
from seed_calculus.examples import coordinate_projectors


def test_exact_analysis_synthesis() -> None:
    p = coordinate_projectors(9, [[0, 3, 6], [1, 4, 7], [2, 5, 8]])
    x = np.arange(9, dtype=float)
    assert np.linalg.norm(synthesis(analysis(p, x)) - x) == 0


def test_projector_axioms() -> None:
    p = coordinate_projectors(10, [list(range(4)), list(range(4, 7)), list(range(7, 10))])
    residuals = projector_residuals(p)
    assert residuals == {"idempotence": 0.0, "annihilation": 0.0, "completeness": 0.0}


def test_operator_block_reconstruction() -> None:
    rng = np.random.default_rng(3)
    t = rng.normal(size=(10, 10))
    p = coordinate_projectors(10, [list(range(0, 2)), list(range(2, 6)), list(range(6, 10))])
    assert np.linalg.norm(reconstruct_operator(transfer_blocks(t, p)) - t) < 1e-12


def test_coordinate_transport() -> None:
    rng = np.random.default_rng(12)
    u = rng.normal(size=(7, 7))
    while abs(np.linalg.det(u)) < 1e-6:
        u = rng.normal(size=(7, 7))
    p = coordinate_projectors(7, [[0, 1], [2, 3, 4], [5, 6]])
    q = transport_projectors(u, p)
    residuals = projector_residuals(q)
    assert max(residuals.values()) < 1e-11
