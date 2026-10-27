import numpy as np

from projector_quantum_calculus.basic import (
    X, basis_state, embed_one_qubit, packet_blocks, reachable_span_rank, reconstruct_blocks,
)
from projector_quantum_calculus.symmetry import (
    coarse_mod_projectors, cyclic_projectors, parity_operator, parity_projectors,
)


def test_cyclic_projectors() -> None:
    s = np.diag([1, 1j, -1, -1j]).astype(complex)
    ps = cyclic_projectors(s, 4)
    assert np.linalg.norm(sum(ps) - np.eye(4)) < 1e-10
    for i, p in enumerate(ps):
        assert np.linalg.norm(p @ p - p) < 1e-10
        assert np.linalg.norm(p - p.conj().T) < 1e-10
        for j, q in enumerate(ps):
            if i != j:
                assert np.linalg.norm(p @ q) < 1e-10


def test_parity_projectors() -> None:
    pe, po = parity_projectors(3)
    assert np.linalg.norm(pe + po - np.eye(8)) < 1e-12
    assert np.linalg.matrix_rank(pe, tol=1e-10) == 4
    assert np.linalg.matrix_rank(po, tol=1e-10) == 4
    assert np.linalg.norm(parity_operator(3) @ pe - pe) < 1e-12
    assert np.linalg.norm(parity_operator(3) @ po + po) < 1e-12


def test_tensor_refines_parity() -> None:
    local = [[np.diag([1, 0]).astype(complex), np.diag([0, 1]).astype(complex)] for _ in range(3)]
    coarse = coarse_mod_projectors(local, 2)
    parity = parity_projectors(3)
    assert max(np.linalg.norm(coarse[i] - parity[i]) for i in range(2)) < 1e-12


def test_block_reconstruction() -> None:
    rng = np.random.default_rng(4)
    a = rng.standard_normal((8, 8)) + 1j * rng.standard_normal((8, 8))
    ps = parity_projectors(3)
    assert np.linalg.norm(reconstruct_blocks(packet_blocks(a, ps)) - a) < 1e-10


def test_reachable_seed() -> None:
    gens = [embed_one_qubit(X, q, 3) for q in range(3)]
    assert reachable_span_rank(gens, basis_state(3, 0), max_depth=5) == 8
