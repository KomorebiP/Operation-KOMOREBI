import numpy as np

from packet_gpu.krylov import conjugate_gradient, lanczos_tridiagonal, preconditioned_condition_bound
from packet_gpu.operators import BlockDiagonal


def test_condition_bound() -> None:
    assert np.isclose(preconditioned_condition_bound(0.2), 1.5)


def test_packet_preconditioned_cg() -> None:
    rng = np.random.default_rng(9)
    blocks = []
    for _ in range(6):
        a = rng.normal(size=(6, 6))
        blocks.append(a.T @ a + 5 * np.eye(6))
    d = BlockDiagonal(tuple(blocks))
    n = d.n
    coupling = rng.normal(size=(n, n))
    coupling = 0.01 * (coupling + coupling.T)
    a = d.materialize() + coupling
    b = rng.normal(size=n)
    plain = conjugate_gradient(lambda x: a @ x, b, tol=1e-10, maxiter=200)
    packet = conjugate_gradient(lambda x: a @ x, b, precondition=d.solve, tol=1e-10, maxiter=200)
    assert plain.converged and packet.converged
    assert np.linalg.norm(a @ packet.x - b) < 1e-9
    assert packet.iterations <= plain.iterations


def test_lanczos_ritz_values() -> None:
    rng = np.random.default_rng(10)
    q, _ = np.linalg.qr(rng.normal(size=(12, 12)))
    eigenvalues = np.linspace(1, 12, 12)
    a = q @ np.diag(eigenvalues) @ q.T
    t, basis, _ = lanczos_tridiagonal(lambda x: a @ x, 12, 12, seed=4)
    ritz = np.linalg.eigvalsh(t)
    assert np.max(np.abs(np.sort(ritz) - eigenvalues)) < 1e-8
    assert np.linalg.norm(basis.T @ basis - np.eye(basis.shape[1])) < 1e-10
