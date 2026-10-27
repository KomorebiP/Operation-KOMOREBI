from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from psc_packet.packet_algorithms import (
    DTypeChoice,
    PacketIR,
    PacketLayout,
    TreeNode,
    amortization_threshold,
    assign_discrete_precisions,
    clipped_precision_allocation,
    compile_tree_budget,
    compile_tree_lagrangian,
    dense_apply_flops,
    packet_apply_flops,
    packet_streaming_bytes,
    product_chain_error_bound,
    recompress_factors,
    roofline_time_lower_bound,
    schur_fill_support,
    support_power,
    topological_levels,
    block_banded_block_count,
    block_diagonal_projection,
    circulant_apply_fft,
    circulant_matrix,
    kronecker_modewise_apply,
    repeated_recompression_bound,
    toeplitz_apply_embedding,
    walsh_hadamard_transform,
)


def test_packet_ir_semantics() -> None:
    rng = np.random.default_rng(1)
    layout = PacketLayout((3, 2, 4))
    blocks = {
        (0, 0): rng.normal(size=(3, 3)),
        (1, 0): rng.normal(size=(2, 3)),
        (2, 1): rng.normal(size=(4, 2)),
        (2, 2): rng.normal(size=(4, 4)),
    }
    a = PacketIR(layout, blocks)
    x = rng.normal(size=(layout.n, 5))
    assert np.allclose(a.apply(x), a.materialize() @ x)
    assert np.allclose(a.adjoint().materialize(), a.materialize().conj().T)
    b = PacketIR(layout, {(0, 2): rng.normal(size=(3, 4)), (1, 1): rng.normal(size=(2, 2))})
    assert np.allclose(a.compose(b).materialize(), a.materialize() @ b.materialize())


def test_recompression_is_optimal_for_factor_product() -> None:
    rng = np.random.default_rng(2)
    left = rng.normal(size=(40, 9))
    right = rng.normal(size=(35, 9))
    matrix = left @ right.T
    result = recompress_factors(left, right, 4)
    u, s, vh = np.linalg.svd(matrix, full_matrices=False)
    best = (u[:, :4] * s[:4]) @ vh[:4]
    assert np.allclose(result.materialize(), best, atol=1e-10)
    assert np.isclose(np.linalg.norm(matrix - result.materialize(), 2), s[4], rtol=1e-9, atol=1e-9)
    assert np.isclose(np.linalg.norm(matrix - result.materialize(), "fro"), np.linalg.norm(s[4:]), rtol=1e-9)


def test_product_chain_error_bound() -> None:
    rng = np.random.default_rng(3)
    exact = [rng.normal(size=(5, 5)) / 5 for _ in range(4)]
    approx = [a + 1e-3 * rng.normal(size=(5, 5)) for a in exact]
    p = np.eye(5)
    ph = np.eye(5)
    for a, ah in zip(exact, approx, strict=True):
        p = a @ p
        ph = ah @ ph
    assert np.linalg.norm(ph - p, 2) <= product_chain_error_bound(exact, approx) + 1e-12


def test_cost_models() -> None:
    layout = PacketLayout((4, 4, 4))
    support = {(0, 0), (1, 0), (2, 1), (2, 2)}
    assert dense_apply_flops(12, 3) == 864
    assert packet_apply_flops(layout, support, 3) == 384
    assert packet_streaming_bytes(layout, support, 3, 4) > 0
    assert roofline_time_lower_bound(100.0, 200.0, 50.0, 25.0) == 8.0
    assert amortization_threshold(10.0, 4.0, 1.0) == 4
    assert amortization_threshold(10.0, 1.0, 2.0) is None


def test_graph_support_and_schedule() -> None:
    support = {(1, 0), (2, 1), (3, 2)}
    assert (3, 0) in support_power(support, 3)
    levels = topological_levels(4, {(0, 1), (1, 2), (0, 3)})
    assert levels[0] == (0,)
    assert levels[-1] == (2,)
    fill = schur_fill_support([0, 2], [1], {(1, 0), (2, 1), (0, 0), (2, 2)})
    assert (2, 0) in fill


def _tree() -> TreeNode:
    return TreeNode(
        "root",
        keep_cost=10.0,
        keep_error=0.0,
        split_cost=1.0,
        children=(
            TreeNode("a", 2.0, 2.0, 0.5, (TreeNode("a0", 1.0, 0.2), TreeNode("a1", 1.1, 0.2))),
            TreeNode("b", 3.0, 1.0, 0.5, (TreeNode("b0", 0.8, 0.1), TreeNode("b1", 0.9, 0.1))),
        ),
    )


def test_tree_compilers() -> None:
    root = _tree()
    plan0 = compile_tree_lagrangian(root, 0.0)
    assert set(plan0.leaves) == {"a", "b0", "b1"}
    plan_high = compile_tree_lagrangian(root, 100.0)
    assert plan_high.leaves == ("root",)
    budget = compile_tree_budget(root, budget=6, scale=0.1)
    assert budget is not None
    assert budget.error <= 0.6 + 1e-12


def test_discrete_precision_assignment() -> None:
    options = [
        [DTypeChoice("fp16", 1.0, 4), DTypeChoice("fp32", 2.0, 1)],
        [DTypeChoice("fp16", 1.0, 5), DTypeChoice("fp32", 2.2, 1)],
    ]
    result = assign_discrete_precisions(options, budget=5)
    assert result is not None
    cost, names = result
    assert cost == 3.2
    assert names == ("fp16", "fp32")


def test_clipped_precision_allocation() -> None:
    s = np.array([1.0, 3.0, 5.0])
    c = np.array([1.0, 2.0, 4.0])
    maxima = np.array([0.2, 0.2, 0.2])
    eps = clipped_precision_allocation(s, c, 0.45, maxima)
    assert np.all(eps > 0)
    assert np.all(eps <= maxima + 1e-10)
    assert np.isclose(np.dot(s, eps), 0.45, atol=1e-8)


def test_benchmark_corpus() -> None:
    path = Path(__file__).with_name("benchmark_results_sanitized.json")
    data = json.loads(path.read_text())
    rows = data["results"]
    assert len(rows) == 154
    assert sum(r["device"] == "CPU" for r in rows) == 74
    assert sum(r["device"] != "CPU" for r in rows) == 80
    assert len({r["suite"] for r in rows}) == 16
    assert all(r["status"] == "measured" for r in rows)
    assert max(float(r.get("relative_error") or 0.0) for r in rows) < 3e-3



def test_structured_packet_primitives() -> None:
    rng = np.random.default_rng(21)
    assert block_banded_block_count(8, 2) == 34

    c = rng.normal(size=16)
    x = rng.normal(size=16)
    assert np.allclose(circulant_apply_fft(c, x), circulant_matrix(c) @ x)

    col = rng.normal(size=11)
    row = rng.normal(size=11)
    row[0] = col[0]
    t = np.fromfunction(lambda i, j: np.where(i >= j, col[(i - j).astype(int)], row[(j - i).astype(int)]), (11, 11))
    assert np.allclose(toeplitz_apply_embedding(col, row, x[:11]), t @ x[:11])

    a = rng.normal(size=(5, 5))
    b = rng.normal(size=(4, 4))
    mat = rng.normal(size=(4, 5))
    lhs = np.kron(a, b) @ mat.reshape(-1, order="F")
    rhs = kronecker_modewise_apply(a, b, mat).reshape(-1, order="F")
    assert np.allclose(lhs, rhs)

    z = rng.normal(size=32)
    hz = walsh_hadamard_transform(z)
    assert np.allclose(walsh_hadamard_transform(hz), 32 * z)
    assert np.isclose(np.linalg.norm(walsh_hadamard_transform(z, normalized=True)), np.linalg.norm(z))


def test_discovery_and_recompression_certificates() -> None:
    rng = np.random.default_rng(22)
    layout = PacketLayout((3, 2, 4))
    a = rng.normal(size=(layout.n, layout.n))
    d = block_diagonal_projection(a, layout)
    off = a - d
    squares = 0.0
    for beta, slb in enumerate(layout.slices):
        for alpha, sla in enumerate(layout.slices):
            if beta != alpha:
                squares += np.linalg.norm(a[slb, sla], "fro") ** 2
    assert np.isclose(np.linalg.norm(off, "fro") ** 2, squares)

    factors = [rng.normal(size=(4, 4)) / 3 for _ in range(5)]
    errors = [1e-4 * rng.normal(size=(4, 4)) for _ in range(5)]
    exact = np.eye(4)
    approx = np.eye(4)
    for factor, error in zip(factors, errors, strict=True):
        exact = factor @ exact
        approx = factor @ approx + error
    assert np.linalg.norm(approx - exact, 2) <= repeated_recompression_bound(factors, errors) + 1e-12
