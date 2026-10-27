from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .benchmark_data import dataset_summary, load_benchmark, sanitized_benchmark, write_analysis_tables
from .complexity import (
    amortized_break_even,
    bdlr_apply_flops,
    bdlr_storage,
    dense_apply_flops,
    dense_storage,
    equal_packet_sizes,
    ideal_bdlr_speedup,
)
from .krylov import conjugate_gradient, preconditioned_condition_bound
from .mixed_precision import actual_block_diagonal_error, optimal_precision_tolerances, packet_error_bound, quantize_by_packet
from .operators import BDLRMatrix, BlockDiagonal, BlockSparseMatrix


def run_finite_experiments(seed: int = 20260711) -> dict:
    rng = np.random.default_rng(seed)
    sizes = (8, 8, 8, 8)
    blocks = []
    for size in sizes:
        a = rng.normal(size=(size, size))
        blocks.append(a.T @ a + 2.0 * np.eye(size))
    diagonal = BlockDiagonal.from_sequence(blocks)
    n = diagonal.n
    rank = 3
    u = rng.normal(size=(n, rank)) * 0.08
    v = u.copy()
    matrix = BDLRMatrix(diagonal, u, v)
    x = rng.normal(size=(n, 5))
    dense = matrix.materialize()
    apply_residual = float(np.linalg.norm(matrix.apply(x) - dense @ x))
    b = rng.normal(size=n)
    solve_residual = float(np.linalg.norm(dense @ matrix.solve(b) - b))

    other_u = rng.normal(size=(n, rank)) * 0.05
    other = BDLRMatrix(diagonal, other_u, other_u.copy())
    product = matrix.compressed_product(other)
    product_residual = float(np.linalg.norm(product.materialize() - dense @ other.materialize()))

    edges = {}
    for alpha in range(len(sizes)):
        edges[(alpha, alpha)] = blocks[alpha]
        if alpha + 1 < len(sizes):
            edges[(alpha + 1, alpha)] = rng.normal(size=(sizes[alpha + 1], sizes[alpha])) * 0.02
            edges[(alpha, alpha + 1)] = edges[(alpha + 1, alpha)].T
    sparse = BlockSparseMatrix(sizes, edges)
    sparse_residual = float(np.linalg.norm(sparse.apply(x) - sparse.materialize() @ x))

    # Mixed precision certificate.
    qblocks = quantize_by_packet(blocks, [16, 32, 32, 64])
    packet_x = [x[slc] for slc in diagonal.slices]
    actual_mp = actual_block_diagonal_error(blocks, qblocks, packet_x)
    block_norms = [float(np.linalg.norm(block, 2)) for block in blocks]
    rel_errors = [float(np.linalg.norm(q - b0, 2) / np.linalg.norm(b0, 2)) for b0, q in zip(blocks, qblocks, strict=True)]
    input_norms = [float(np.linalg.norm(xi)) for xi in packet_x]
    mp_bound = packet_error_bound(block_norms, rel_errors, input_norms)

    sensitivities = np.array(block_norms) * np.array(input_norms)
    tolerances = optimal_precision_tolerances(sensitivities, [1, 2, 2, 4], 1e-4)

    # Packet preconditioned CG.
    coupling = sparse.materialize() - diagonal.materialize()
    a_spd = diagonal.materialize() + coupling
    # Shift to maintain a robust SPD finite test.
    min_eig = float(np.linalg.eigvalsh(a_spd).min())
    if min_eig <= 0:
        shift = 1.0 - min_eig
        shifted = tuple(block + shift * np.eye(block.shape[0]) for block in blocks)
        diagonal = BlockDiagonal.from_sequence(shifted)
        a_spd = diagonal.materialize() + coupling
    rhs = rng.normal(size=n)
    cg_plain = conjugate_gradient(lambda z: a_spd @ z, rhs, tol=1e-10, maxiter=300)
    cg_packet = conjugate_gradient(lambda z: a_spd @ z, rhs, precondition=diagonal.solve, tol=1e-10, maxiter=300)
    e = np.linalg.solve(np.linalg.cholesky(diagonal.materialize()), coupling)
    # Similarity norm computed directly.
    d_half_inv = np.linalg.inv(np.linalg.cholesky(diagonal.materialize()))
    eta = float(np.linalg.norm(d_half_inv @ coupling @ d_half_inv.T, 2))
    cond_bound = preconditioned_condition_bound(min(eta, 0.999999)) if eta < 1 else None

    model_sizes = equal_packet_sizes(8192, 64)
    return {
        "author": "Komorebi P.",
        "seed": seed,
        "finite_certificates": {
            "bdlr_apply_residual": apply_residual,
            "woodbury_solve_residual": solve_residual,
            "compressed_product_residual": product_residual,
            "block_sparse_apply_residual": sparse_residual,
            "mixed_precision_actual_error": actual_mp,
            "mixed_precision_bound": mp_bound,
            "mixed_precision_bound_holds": actual_mp <= mp_bound + 1e-12,
            "optimal_tolerances": tolerances.tolist(),
            "cg_plain_iterations": cg_plain.iterations,
            "cg_packet_iterations": cg_packet.iterations,
            "cg_plain_residual": cg_plain.residual_norms[-1],
            "cg_packet_residual": cg_packet.residual_norms[-1],
            "preconditioned_eta": eta,
            "preconditioned_condition_bound": cond_bound,
        },
        "complexity_model": {
            "n": 8192,
            "block_size": 64,
            "rank": 8,
            "rhs": 32,
            "dense_apply_flops": dense_apply_flops(8192, 32),
            "bdlr_apply_flops": bdlr_apply_flops(model_sizes, 8, 32),
            "ideal_arithmetic_speedup": ideal_bdlr_speedup(8192, 64, 8),
            "dense_storage_bytes_fp32": dense_storage(8192, 4),
            "bdlr_storage_bytes_fp32": bdlr_storage(model_sizes, 8, 4),
            "storage_reduction": dense_storage(8192, 4) / bdlr_storage(model_sizes, 8, 4),
        },
        "amortization_examples": {
            "hidden_block_discovery_512": amortized_break_even(2.1102, 0.0969, 0.0151),
            "hidden_block_discovery_1024": amortized_break_even(5.2726, 0.1896, 0.0241),
        },
    }


def run_all(benchmark_path: str | Path, root: str | Path) -> dict:
    root = Path(root)
    data = load_benchmark(benchmark_path)
    clean = sanitized_benchmark(data)
    (root / "data").mkdir(parents=True, exist_ok=True)
    (root / "results").mkdir(parents=True, exist_ok=True)
    clean_path = root / "data" / "benchmark_results_sanitized.json"
    clean_path.write_text(json.dumps(clean, indent=2, sort_keys=True), encoding="utf-8")
    tables = write_analysis_tables(clean, root / "tables")
    result = run_finite_experiments()
    result["measured_dataset"] = dataset_summary(clean)
    result["measured_dataset"]["source_rows"] = len(clean["results"])
    result["generated_tables"] = {key: str(path.relative_to(root)) for key, path in tables.items()}
    out = root / "results" / "paper_viii_results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result
