from __future__ import annotations

from dataclasses import dataclass
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from kcos import exact_cgf_derivative
from kcos_v2 import adaptive_kcos_logsf, exact_tilted_logsf

HERE = Path(__file__).resolve().parent


def simulate_copy_ld_fixed(
    n=600, m=3000, block=50, copy_prob=0.90, seed=88
):
    """Fixed version of the historical copy-LD simulator.

    Historical bug repaired:
      old code used np.empty(...) followed by +=.
    """
    rng = np.random.default_rng(seed)
    G = np.zeros((n, m), dtype=np.float64)
    maf = np.empty(m, dtype=np.float64)

    for left in range(0, m, block):
        right = min(m, left + block)
        b = right - left

        base = float(0.003 + 0.04 * rng.beta(0.8, 3.0))
        local = np.clip(
            base * np.exp(rng.normal(0.0, 0.08, size=b)),
            0.001,
            0.05,
        )
        maf[left:right] = local

        for _hap in range(2):
            state = (rng.random(n) < local[0]).astype(np.int8)
            G[:, left] += state
            for j in range(1, b):
                redraw = rng.random(n) > copy_prob
                new = (rng.random(n) < local[j]).astype(np.int8)
                state = np.where(redraw, new, state)
                G[:, left + j] += state

    return G, maf


def simulate_gaussian_ld(
    n=600, m=3000, block=50, rho=0.80, seed=20260923
):
    """Existing latent-Gaussian LD generator from the K-COS benchmark family."""
    rng = np.random.default_rng(seed)
    G = np.empty((n, m), dtype=np.float64)
    maf = 0.002 + 0.048 * rng.beta(0.8, 3.0, size=m)
    sr = math.sqrt(1.0 - rho * rho)

    for left in range(0, m, block):
        right = min(m, left + block)
        b = right - left
        thresholds = stats.norm.ppf(maf[left:right])

        z1 = rng.normal(size=(n, 1))
        z2 = rng.normal(size=(n, 1))
        h1 = (
            rho * z1 + sr * rng.normal(size=(n, b))
            < thresholds[None, :]
        )
        h2 = (
            rho * z2 + sr * rng.normal(size=(n, b))
            < thresholds[None, :]
        )
        G[:, left:right] = h1 + h2

    return G, maf


def covariates(n, seed):
    rng = np.random.default_rng(seed)
    age = rng.normal(size=n)
    pc1 = rng.normal(size=n)
    batch = rng.integers(0, 2, size=n).astype(float)
    X = np.column_stack([np.ones(n), age, pc1, batch])
    Qx, _ = np.linalg.qr(X, mode="reduced")
    return X, Qx


def process_full(G, maf, Qx):
    C = G - G.mean(axis=0, keepdims=True)
    sd = C.std(axis=0, ddof=1)
    keep = sd > 1e-12
    C = C[:, keep] / sd[keep]
    mafr = maf[keep]
    C = C - Qx @ (Qx.T @ C)
    A = C * np.sqrt((1.0 - mafr) ** 24)[None, :]
    K = A @ A.T
    return A, K, mafr, keep


def stream_kernel_raw(G, maf, Qx, block_size):
    """Exact variant-block construction from raw genotype columns."""
    n, m = G.shape
    K = np.zeros((n, n), dtype=np.float64)
    retained = 0

    for left in range(0, m, block_size):
        right = min(m, left + block_size)
        Gb = G[:, left:right]
        mb = maf[left:right]

        C = Gb - Gb.mean(axis=0, keepdims=True)
        sd = C.std(axis=0, ddof=1)
        keep = sd > 1e-12
        if not np.any(keep):
            continue

        C = C[:, keep] / sd[keep]
        C = C - Qx @ (Qx.T @ C)
        wb = (1.0 - mb[keep]) ** 24
        Ab = C * np.sqrt(wb)[None, :]
        K += Ab @ Ab.T
        retained += int(np.sum(keep))

    return 0.5 * (K + K.T), retained


def ld_diagnostics(G, block=50, seed=44, draws=150):
    rng = np.random.default_rng(seed)
    C = G - G.mean(axis=0, keepdims=True)
    sd = C.std(axis=0, ddof=1)
    good = sd > 1e-12
    C[:, good] /= sd[good]
    m = G.shape[1]
    nb = max(1, m // block)
    within, between = [], []

    for _ in range(draws):
        b = int(rng.integers(0, nb))
        i = b * block + int(rng.integers(0, max(1, block - 1)))
        j = min(i + 1, m - 1)
        if good[i] and good[j]:
            c = np.corrcoef(C[:, i], C[:, j])[0, 1]
            if np.isfinite(c):
                within.append(c * c)

        if nb >= 2:
            b1, b2 = rng.choice(nb, size=2, replace=False)
            i = min(b1 * block, m - 1)
            j = min(b2 * block, m - 1)
            if good[i] and good[j]:
                c = np.corrcoef(C[:, i], C[:, j])[0, 1]
                if np.isfinite(c):
                    between.append(c * c)

    return (
        float(np.median(within)) if within else np.nan,
        float(np.quantile(within, 0.9)) if within else np.nan,
        float(np.median(between)) if between else np.nan,
    )


def phenotype_path_audit(A, K, Qx, eigvals, eigvecs, draws=100, seed=123):
    rng = np.random.default_rng(seed)
    max_factor_kernel = 0.0
    max_kernel_eig = 0.0
    max_rel = 0.0

    for _ in range(draws):
        eps = rng.normal(size=A.shape[0])
        e = eps - Qx @ (Qx.T @ eps)

        q_factor = 0.5 * float(np.sum((A.T @ e) ** 2))
        q_kernel = 0.5 * float(e @ (K @ e))
        z = eigvecs.T @ e
        q_eig = 0.5 * float(np.sum(eigvals * z * z))

        max_factor_kernel = max(max_factor_kernel, abs(q_factor - q_kernel))
        max_kernel_eig = max(max_kernel_eig, abs(q_kernel - q_eig))
        denom = max(abs(q_factor), 1e-300)
        max_rel = max(
            max_rel,
            abs(q_factor - q_kernel) / denom,
            abs(q_factor - q_eig) / denom,
        )

    return max_factor_kernel, max_kernel_eig, max_rel


def spectrum_from_kernel(K):
    ev, U = np.linalg.eigh(K)
    order = np.argsort(ev)[::-1]
    ev = np.maximum(ev[order], 0.0)
    U = U[:, order]
    if ev.size and ev[0] > 0:
        keep = ev > ev[0] * 1e-13
        ev = ev[keep]
        U = U[:, keep]
    lam = 0.5 * ev
    return lam, ev, U


def run_scenario(name, simulator, sim_kwargs, block_sizes=(31,127,509)):
    t0 = time.perf_counter()
    G, maf = simulator(**sim_kwargs)
    gen_s = time.perf_counter() - t0
    n, m = G.shape

    _, Qx = covariates(n, seed=sim_kwargs.get("seed", 1) + 991)

    t0 = time.perf_counter()
    A, Kfull, mafr, keep = process_full(G, maf, Qx)
    full_factor_s = time.perf_counter() - t0

    stream_rows = []
    for bs in block_sizes:
        t0 = time.perf_counter()
        Ks, retained = stream_kernel_raw(G, maf, Qx, bs)
        dt = time.perf_counter() - t0
        rel = np.linalg.norm(Ks - Kfull) / np.linalg.norm(Kfull)
        stream_rows.append({
            "scenario": name,
            "n": n,
            "m": m,
            "block_size": bs,
            "retained_variants": retained,
            "stream_seconds": dt,
            "kernel_relative_error": rel,
        })

    t0 = time.perf_counter()
    lam, ev, U = spectrum_from_kernel(Kfull)
    spectrum_s = time.perf_counter() - t0

    med_within, p90_within, med_between = ld_diagnostics(G)

    qfa, qke, qrel = phenotype_path_audit(
        A, Kfull, Qx, ev, U, draws=100,
        seed=sim_kwargs.get("seed", 1) + 173,
    )

    tail_rows = []
    for frac in (0.90, 0.97, 0.99):
        theta = frac / (2.0 * lam.max())
        q = exact_cgf_derivative(theta, lam, 1)

        t0 = time.perf_counter()
        kres = adaptive_kcos_logsf(
            q, lam, relative_tolerance=1e-8, max_K=262144
        )
        ktime = time.perf_counter() - t0

        Kref = max(4096, 2 * kres.certificate.K)
        t0 = time.perf_counter()
        ref_logp, _ = exact_tilted_logsf(
            q, lam, K=Kref, L=max(22, kres.certificate.L + 4)
        )
        rtime = time.perf_counter() - t0

        tail_rows.append({
            "scenario": name,
            "theta_fraction": frac,
            "q": q,
            "rank": len(lam),
            "kcos_log10_p": kres.log10_p,
            "reference_log10_p": ref_logp / math.log(10.0),
            "difference_decades": (kres.log_p - ref_logp) / math.log(10.0),
            "certificate": kres.certificate.certified_relative_bound,
            "K": kres.certificate.K,
            "L": kres.certificate.L,
            "packets": kres.certificate.packet_count,
            "kcos_seconds": ktime,
            "reference_seconds": rtime,
        })

    scenario_row = {
        "scenario": name,
        "n": n,
        "m": m,
        "retained_variants": int(np.sum(keep)),
        "rank": len(lam),
        "generation_seconds": gen_s,
        "full_factor_seconds": full_factor_s,
        "spectrum_seconds": spectrum_s,
        "median_adjacent_within_block_r2": med_within,
        "p90_adjacent_within_block_r2": p90_within,
        "median_between_block_r2": med_between,
        "phenotype_max_abs_factor_vs_kernel": qfa,
        "phenotype_max_abs_kernel_vs_eig": qke,
        "phenotype_max_relative_discrepancy": qrel,
        "lambda_max": float(lam.max()),
        "trace_lambda": float(lam.sum()),
        "effective_rank": float(lam.sum()**2 / np.sum(lam*lam)),
    }

    return scenario_row, stream_rows, tail_rows


def main():
    scenarios = [
        (
            "gaussian_ld_moderate",
            simulate_gaussian_ld,
            dict(n=600, m=3000, block=50, rho=0.65, seed=101),
        ),
        (
            "gaussian_ld_strong",
            simulate_gaussian_ld,
            dict(n=600, m=3000, block=50, rho=0.90, seed=102),
        ),
        (
            "copy_ld_strong_fixed",
            simulate_copy_ld_fixed,
            dict(n=600, m=3000, block=50, copy_prob=0.90, seed=103),
        ),
        (
            "copy_ld_large_fixed",
            simulate_copy_ld_fixed,
            dict(n=1000, m=5000, block=50, copy_prob=0.90, seed=104),
        ),
    ]

    summary, streams, tails = [], [], []
    for name, sim, kwargs in scenarios:
        s, st, ta = run_scenario(name, sim, kwargs)
        summary.append(s)
        streams.extend(st)
        tails.extend(ta)
        print(f"completed {name}")

    sdf = pd.DataFrame(summary)
    bdf = pd.DataFrame(streams)
    tdf = pd.DataFrame(tails)

    sdf.to_csv(HERE / "realistic_skat_scenarios.csv", index=False)
    bdf.to_csv(HERE / "realistic_streaming_invariance.csv", index=False)
    tdf.to_csv(HERE / "realistic_deep_tail_accuracy.csv", index=False)

    print("\n=== SCENARIOS ===")
    print(sdf.to_string(index=False))
    print("\n=== STREAMING ===")
    print(bdf.to_string(index=False))
    print("\n=== TAILS ===")
    print(tdf.to_string(index=False))


if __name__ == "__main__":
    main()
