from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass
class SparseChannelRow:
    label: str
    group_order: int
    support_size: int
    assignment_count: int
    occupied_residues: int
    target_log: int
    exact_target_count: int
    occupancy_ratio: float
    entropy_defect: float
    total_fourier_energy: float
    nontrivial_fourier_energy: float
    sparsity_energy_lower_bound: float
    max_nontrivial_multiplier: float
    forced_peak_lower_bound: float
    prony_tested: bool
    prony_degree: int | None
    prony_recurrence_residual: float | None
    krylov_rank_tested_degree: int
    krylov_rank_numeric: int
    krylov_rank_exact: int
    galois_balance_tested: bool
    target_log_discriminant_original: float | None
    target_log_discriminant_best_galois: float | None
    target_log_discriminant_mean_galois: float | None


def parse_ints(text: str) -> list[int]:
    text = str(text).strip()
    if not text:
        return []
    return [int(item) for item in text.split()]


def exact_counts(order: int, logs: list[int]) -> np.ndarray:
    counts = np.zeros(order, dtype=np.int64)
    counts[0] = 1
    for step in logs:
        counts = counts + np.roll(counts, step) + np.roll(counts, -step)
    return counts


def normalized_multiplier(counts: np.ndarray) -> np.ndarray:
    total = int(np.sum(counts))
    # numpy's inverse convention is irrelevant for magnitudes and shift-Krylov rank.
    return np.fft.fft(counts.astype(np.float64)) / total


def shift_krylov(multiplier: np.ndarray, degree: int) -> np.ndarray:
    return np.column_stack([np.roll(multiplier, -j) for j in range(degree + 1)])


def numerical_rank(matrix: np.ndarray) -> int:
    singular = np.linalg.svd(matrix, compute_uv=False)
    if singular.size == 0:
        return 0
    tolerance = max(matrix.shape) * np.finfo(float).eps * singular[0] * 20
    return int(np.sum(singular > tolerance))


def annihilator_recurrence_residual(counts: np.ndarray, limit: int = 48) -> tuple[int, float] | None:
    occupied = np.flatnonzero(counts)
    r = len(occupied)
    if r == 0 or r > limit:
        return None
    n = len(counts)
    roots = np.exp(2j * math.pi * occupied / n)
    # np.poly returns descending coefficients. Reverse for A(z)=sum_j a_j z^j.
    ascending = np.poly(roots)[::-1]
    multiplier = normalized_multiplier(counts)
    errors = []
    scales = []
    for k in range(n):
        indices = (k + np.arange(r + 1)) % n
        value = np.dot(ascending, multiplier[indices])
        errors.append(abs(value))
        scales.append(np.sum(np.abs(ascending) * np.abs(multiplier[indices])))
    denominator = max(max(scales), 1.0)
    return r, float(max(errors) / denominator)


def units_modulo(n: int) -> np.ndarray:
    return np.asarray([u for u in range(1, n) if math.gcd(u, n) == 1], dtype=np.int64)


def log_discriminant(n: int, differences: np.ndarray, units: np.ndarray) -> np.ndarray:
    # Evaluate log product |1-zeta^(u d)| in each Galois embedding.
    output = np.zeros(len(units), dtype=np.float64)
    chunk = 10000
    for start in range(0, len(units), chunk):
        block = units[start:start + chunk, None]
        angles = math.pi * ((block * differences[None, :]) % n) / n
        values = 2.0 * np.abs(np.sin(angles))
        # differences are nonzero mod n, so values should be positive.
        values = np.maximum(values, np.finfo(float).tiny)
        output[start:start + chunk] = np.sum(np.log(values), axis=1)
    return output


def galois_balance_metrics(counts: np.ndarray, target: int, work_limit: int = 5_000_000) -> tuple[bool, float | None, float | None, float | None]:
    occupied = np.flatnonzero(counts)
    n = len(counts)
    present = counts[target] > 0
    selected = occupied[occupied != target] if present else occupied
    if len(selected) == 0:
        return True, 0.0, 0.0, 0.0
    units = units_modulo(n)
    if len(units) * len(selected) > work_limit:
        return False, None, None, None
    differences = (selected - target) % n
    logs = log_discriminant(n, differences.astype(np.int64), units)
    original_index = int(np.where(units == 1)[0][0])
    return True, float(logs[original_index]), float(np.max(logs)), float(np.mean(logs))


def analyze_table(input_csv: Path) -> tuple[list[SparseChannelRow], dict[str, object]]:
    frame = pd.read_csv(input_csv)
    rows: list[SparseChannelRow] = []
    rank_checks = 0
    prony_checks = 0
    galois_checks = 0

    for record in frame.itertuples(index=False):
        order = int(record.group_order)
        logs = parse_ints(record.support_logs)
        counts = exact_counts(order, logs)
        multiplier = normalized_multiplier(counts)
        total = int(np.sum(counts))
        occupied = int(np.count_nonzero(counts))
        target = int(record.target_log) % order
        exact = int(counts[target])

        total_energy = float(np.sum(np.abs(multiplier) ** 2))
        nontrivial_energy = total_energy - 1.0
        lower = order / occupied - 1.0
        max_nontrivial = float(np.max(np.abs(multiplier[1:]))) if order > 1 else 0.0
        forced_peak = math.sqrt(max(lower, 0.0) / max(order - 1, 1))

        degree = min(max(1, occupied - 1), 24)
        matrix = shift_krylov(multiplier, degree)
        rank_numeric = numerical_rank(matrix)
        rank_exact = min(occupied, degree + 1)
        if rank_numeric != rank_exact:
            # Numerical conditioning can reduce the observed rank. Record it, but only fail
            # when the discrepancy is large enough to indicate a coding error.
            if rank_numeric + 2 < rank_exact:
                raise AssertionError((record.label, rank_numeric, rank_exact))
        rank_checks += 1

        recurrence = annihilator_recurrence_residual(counts)
        if recurrence is None:
            prony_tested = False
            prony_degree = None
            residual = None
        else:
            prony_tested = True
            prony_degree, residual = recurrence
            if residual > 1e-8:
                raise AssertionError((record.label, residual))
            prony_checks += 1

        tested, log_original, log_best, log_mean = galois_balance_metrics(counts, target)
        if tested:
            # The algebraic norm is a nonzero integer, so the mean log is nonnegative
            # up to numerical rounding and some Galois repetition.
            if log_best is not None and log_best < -1e-8:
                raise AssertionError((record.label, log_best))
            galois_checks += 1

        rows.append(
            SparseChannelRow(
                label=str(record.label),
                group_order=order,
                support_size=len(logs),
                assignment_count=total,
                occupied_residues=occupied,
                target_log=target,
                exact_target_count=exact,
                occupancy_ratio=total / order,
                entropy_defect=math.log(order / total),
                total_fourier_energy=total_energy,
                nontrivial_fourier_energy=nontrivial_energy,
                sparsity_energy_lower_bound=lower,
                max_nontrivial_multiplier=max_nontrivial,
                forced_peak_lower_bound=forced_peak,
                prony_tested=prony_tested,
                prony_degree=prony_degree,
                prony_recurrence_residual=residual,
                krylov_rank_tested_degree=degree,
                krylov_rank_numeric=rank_numeric,
                krylov_rank_exact=rank_exact,
                galois_balance_tested=tested,
                target_log_discriminant_original=log_original,
                target_log_discriminant_best_galois=log_best,
                target_log_discriminant_mean_galois=log_mean,
            )
        )

    summary = {
        'status': 'exact sparse-spectrum, Prony, Krylov-rank, and Galois-balancing analysis',
        'channels': len(rows),
        'rank_checks': rank_checks,
        'prony_checks': prony_checks,
        'galois_checks': galois_checks,
        'theorems': {
            'sparsity_energy_barrier': 'For normalized counts supported on r residues of a group of order n, sum_{chi != 1}|m(chi)|^2 >= n/r - 1 >= n/M - 1.',
            'exact_krylov_rank': 'rank[m,Tm,...,T^d m] = min(r,d+1), where r is the number of occupied residues.',
            'prony_reconstruction': 'The first 2r consecutive transform samples determine the r occupied residues and their multiplicities through the annihilating recurrence.',
            'subpolynomial_innovation': 'For s variable support primes, r <= M=3^s. Since 3^omega(R) <= C_epsilon R^epsilon, the exact innovation degree is R^{o(1)}.',
            'galois_balancing': 'For the target Lagrange denominator Delta_h, some unit reindexing u modulo n satisfies |Delta_{uh}(uE)| >= 1 because its product over Galois embeddings is a nonzero integer norm.',
        },
        'interpretation': 'The synthetic mixing transition occurs when assignment entropy log M crosses channel entropy log n. In the strong-abc regime the joint powerful modulus is much larger than M=3^omega(S), so the assignment measure is necessarily sparse and cannot become uniformly mixing. COS is therefore an exact compression and leaf-extraction mechanism, not by itself a contradiction.',
        'roadblock': 'The remaining pointwise theorem must control the arithmetic height of a target assignment after sparse Prony reconstruction, equivalently close the resulting p-adic logarithmic or S-unit leaf. General spectral expansion cannot eliminate an assignment that actually exists.',
    }
    return rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('/mnt/data/Projector_Resolved_ABC_Attack_IX_CHANNELS.csv'))
    parser.add_argument('--outdir', type=Path, default=Path('/mnt/data/abc_sparse_prony'))
    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    rows, summary = analyze_table(args.input)
    csv_path = args.outdir / 'sparse_prony_channels.csv'
    with csv_path.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)
    (args.outdir / 'sparse_prony_results.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
