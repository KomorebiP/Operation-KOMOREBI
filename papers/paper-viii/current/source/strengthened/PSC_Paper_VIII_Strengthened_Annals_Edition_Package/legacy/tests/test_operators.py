import numpy as np

from packet_gpu.operators import BDLRMatrix, BlockDiagonal, BlockSparseMatrix, materialize_blocks, packet_blocks


def random_spd_blocks(seed: int = 1):
    rng = np.random.default_rng(seed)
    blocks = []
    for size in (3, 4, 5):
        a = rng.normal(size=(size, size))
        blocks.append(a.T @ a + np.eye(size))
    return blocks


def test_materialize_and_packet_blocks() -> None:
    blocks = random_spd_blocks()
    dense = materialize_blocks(blocks)
    resolved = packet_blocks(dense, [3, 4, 5])
    for i, block in enumerate(blocks):
        assert np.allclose(resolved[(i, i)], block)
    assert all(np.allclose(value, 0) for key, value in resolved.items() if key[0] != key[1])


def test_block_diagonal_apply_and_solve() -> None:
    blocks = random_spd_blocks()
    d = BlockDiagonal.from_sequence(blocks)
    rng = np.random.default_rng(2)
    x = rng.normal(size=(d.n, 4))
    assert np.allclose(d.apply(x), d.materialize() @ x)
    b = rng.normal(size=d.n)
    assert np.linalg.norm(d.materialize() @ d.solve(b) - b) < 1e-10


def test_bdlr_apply_and_woodbury() -> None:
    blocks = random_spd_blocks()
    d = BlockDiagonal.from_sequence(blocks)
    rng = np.random.default_rng(3)
    u = rng.normal(size=(d.n, 2)) * 0.1
    a = BDLRMatrix(d, u, u.copy())
    x = rng.normal(size=(d.n, 3))
    assert np.linalg.norm(a.apply(x) - a.materialize() @ x) < 1e-11
    b = rng.normal(size=d.n)
    assert np.linalg.norm(a.materialize() @ a.solve(b) - b) < 1e-10


def test_bdlr_compressed_product() -> None:
    blocks = random_spd_blocks()
    d = BlockDiagonal.from_sequence(blocks)
    rng = np.random.default_rng(4)
    u1 = rng.normal(size=(d.n, 2)) * 0.1
    u2 = rng.normal(size=(d.n, 3)) * 0.1
    a = BDLRMatrix(d, u1, rng.normal(size=u1.shape) * 0.1)
    b = BDLRMatrix(d, u2, rng.normal(size=u2.shape) * 0.1)
    c = a.compressed_product(b)
    assert c.rank == a.rank + b.rank
    assert np.linalg.norm(c.materialize() - a.materialize() @ b.materialize()) < 1e-10


def test_block_sparse_apply() -> None:
    rng = np.random.default_rng(5)
    sizes = (3, 2, 4)
    edges = {
        (0, 0): rng.normal(size=(3, 3)),
        (1, 0): rng.normal(size=(2, 3)),
        (2, 1): rng.normal(size=(4, 2)),
        (2, 2): rng.normal(size=(4, 4)),
    }
    a = BlockSparseMatrix(sizes, edges)
    x = rng.normal(size=(sum(sizes), 2))
    assert np.linalg.norm(a.apply(x) - a.materialize() @ x) < 1e-12
    assert a.stored_entries == sum(v.size for v in edges.values())
