from __future__ import annotations

from pathlib import Path
import json
import platform
import sys
import time

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from approximate_lightcone import (
    apply_polynomial,
    block_transfer_matrix,
    phase_norm_vector,
    polynomial_difference_envelope,
    power_difference_envelope,
    power_phase_envelope,
    threshold_operator,
)

HERE = Path(__file__).resolve().parent
SEED = 20260923
rng = np.random.default_rng(SEED)

phases = 12
width = 4
widths = [width] * phases
n = phases * width

# Strong local PSD operator: H0 = L0^T L0, with block-bidiagonal L0.
L0 = np.zeros((n, n), dtype=np.float64)
for h in range(phases):
    sh = slice(h * width, (h + 1) * width)
    L0[sh, sh] = 2.2 * np.eye(width) + 0.05 * rng.normal(size=(width, width))
    if h + 1 < phases:
        sg = slice((h + 1) * width, (h + 2) * width)
        L0[sh, sg] = 0.12 * rng.normal(size=(width, width))
H0_unscaled = L0.T @ L0

# Weak long-range couplings at graph distances >= 2.
E = np.zeros_like(H0_unscaled)
for h in range(phases):
    for g in range(h + 2, phases):
        sh = slice(h * width, (h + 1) * width)
        sg = slice(g * width, (g + 1) * width)
        C = rng.normal(size=(width, width))
        E[sh, sg] = C
        E[sg, sh] = C.T
E /= np.linalg.norm(E, ord=2)
weak_scale = 0.05
H_unscaled = H0_unscaled + weak_scale * E

# Normalize to a contraction-like scale so depth plots are readable.
normalization = np.linalg.norm(H_unscaled, ord=2)
H = H_unscaled / normalization
H0 = H0_unscaled / normalization

min_eig_H0 = float(np.linalg.eigvalsh(H0).min())
min_eig_H = float(np.linalg.eigvalsh(H).min())

B = block_transfer_matrix(H, widths)
B0 = block_transfer_matrix(H0, widths)

X = np.zeros((n, 3), dtype=np.float64)
X[:width] = rng.normal(size=(width, 3))
rho0 = phase_norm_vector(X, widths)
distance = np.arange(phases)

# Depth ladder.
Y = X.copy()
Y0 = X.copy()
depth_rows = []
profile_rows = []
for k in range(1, 9):
    Y = H @ Y
    Y0 = H0 @ Y0
    actual_phase = phase_norm_vector(Y, widths)
    exact_cone_phase = phase_norm_vector(Y0, widths)
    actual_error = phase_norm_vector(Y - Y0, widths)
    envelope = power_phase_envelope(B, rho0, k)
    error_bound = power_difference_envelope(B, B0, rho0, k)
    outside = distance > k

    depth_rows.append({
        "depth": k,
        "actual_total_norm": float(np.linalg.norm(Y, ord="fro")),
        "actual_difference_norm": float(np.linalg.norm(actual_error)),
        "certified_difference_norm": float(np.linalg.norm(error_bound)),
        "actual_outside_cone_norm": float(np.linalg.norm(actual_phase[outside])),
        "certified_outside_cone_norm": float(np.linalg.norm(error_bound[outside])),
        "max_phase_envelope_ratio": float(np.max(actual_phase / np.maximum(envelope, 1e-300))),
        "max_phase_difference_ratio": float(np.max(actual_error / np.maximum(error_bound, 1e-300))),
        "phasewise_envelope_valid": bool(np.all(actual_phase <= envelope + 1e-12)),
        "phasewise_difference_valid": bool(np.all(actual_error <= error_bound + 1e-12)),
    })

    for h in range(phases):
        profile_rows.append({
            "depth": k,
            "phase": h,
            "distance": h,
            "actual_phase_norm": float(actual_phase[h]),
            "retained_operator_phase_norm": float(exact_cone_phase[h]),
            "actual_difference_norm": float(actual_error[h]),
            "phase_envelope": float(envelope[h]),
            "difference_certificate": float(error_bound[h]),
            "outside_retained_light_cone": bool(h > k),
        })

depth_df = pd.DataFrame(depth_rows)
profile_df = pd.DataFrame(profile_rows)
depth_df.to_csv(HERE / "approximate_lightcone_depth.csv", index=False)
profile_df.to_csv(HERE / "approximate_lightcone_phase_profile.csv", index=False)

# Threshold sweep at fixed depth.
fixed_depth = 5
Y_exact = np.linalg.matrix_power(H, fixed_depth) @ X
thresholds = [0.0, 0.0015, 0.0019, 0.0021, 0.0023, 0.0026, 0.0030]
threshold_rows = []
for eta in thresholds:
    Heta, Beta, retained = threshold_operator(H, widths, eta)
    Yeta = np.linalg.matrix_power(Heta, fixed_depth) @ X
    actual_error = float(np.linalg.norm(Y_exact - Yeta, ord="fro"))
    phase_bound = power_difference_envelope(B, Beta, rho0, fixed_depth)
    certified_error = float(np.linalg.norm(phase_bound))
    threshold_rows.append({
        "threshold": eta,
        "retained_directed_off_diagonal_blocks": retained,
        "total_directed_off_diagonal_blocks": phases * (phases - 1),
        "retained_fraction": retained / (phases * (phases - 1)),
        "actual_error_frobenius": actual_error,
        "certified_error_frobenius": certified_error,
        "certificate_ratio": actual_error / certified_error if certified_error > 0 else 0.0,
        "certificate_valid": bool(actual_error <= certified_error + 1e-12),
    })
threshold_df = pd.DataFrame(threshold_rows)
threshold_df.to_csv(HERE / "approximate_lightcone_threshold_sweep.csv", index=False)

# Polynomial-Krylov certificate.
coefficients = np.array([0.2, -0.8, 1.3, -0.7, 0.25], dtype=np.float64)
poly_actual_phase = phase_norm_vector(
    apply_polynomial(H, X, coefficients) - apply_polynomial(H0, X, coefficients),
    widths,
)
poly_bound_phase = polynomial_difference_envelope(B, B0, rho0, coefficients)
poly_df = pd.DataFrame({
    "phase": np.arange(phases),
    "actual_difference_norm": poly_actual_phase,
    "certified_difference_norm": poly_bound_phase,
    "certificate_valid": poly_actual_phase <= poly_bound_phase + 1e-12,
})
poly_df.to_csv(HERE / "polynomial_krylov_certificate.csv", index=False)

# Figure 9: depth-dependent leakage.
fig = plt.figure(figsize=(9.5, 7.2))
ax = fig.add_subplot(111)
ax.plot(
    depth_df["depth"],
    depth_df["actual_outside_cone_norm"],
    marker="o",
    label="Actual norm outside retained light cone",
)
ax.plot(
    depth_df["depth"],
    depth_df["certified_outside_cone_norm"],
    marker="o",
    label="Phasewise certified upper bound",
)
ax.set_yscale("log")
ax.set_xlabel("Krylov depth $k$")
ax.set_ylabel("Frobenius norm")
ax.set_title("Weak couplings turn the exact light cone into a certified envelope")
ax.text(
    0.04,
    0.08,
    r"$\rho(H^kX) \leq \mathcal{B}^k\rho(X)$" + "\n"
    + r"$\rho((H^k-H_0^k)X) \leq (\mathcal{B}^k-\mathcal{B}_0^k)\rho(X)$",
    transform=ax.transAxes,
    fontsize=14,
    va="bottom",
)
ax.legend()
ax.grid(True, alpha=0.3)
fig.savefig(HERE / "figures_final" / "figure_09_approximate_lightcone_certificate.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# Figure 10: pruning tradeoff.
trade = threshold_df[threshold_df["certified_error_frobenius"] > 0].sort_values("retained_directed_off_diagonal_blocks")
fig = plt.figure(figsize=(9.5, 7.2))
ax = fig.add_subplot(111)
ax.plot(
    trade["retained_directed_off_diagonal_blocks"],
    trade["actual_error_frobenius"],
    marker="o",
    label="Actual truncation error",
)
ax.plot(
    trade["retained_directed_off_diagonal_blocks"],
    trade["certified_error_frobenius"],
    marker="o",
    label="Certified upper bound",
)
ax.set_yscale("log")
ax.set_xlabel("Retained directed off-diagonal phase blocks")
ax.set_ylabel("Depth-5 Frobenius error")
ax.set_title("Certified sparsity-error tradeoff for thresholded phase graphs")
ax.text(
    0.04,
    0.08,
    "Moving left prunes more weak phase couplings.\n"
    "The certificate remains valid while communication decreases.",
    transform=ax.transAxes,
    fontsize=14,
    va="bottom",
)
ax.legend()
ax.grid(True, alpha=0.3)
fig.savefig(HERE / "figures_final" / "figure_10_threshold_tradeoff.png", dpi=300, bbox_inches="tight")
plt.close(fig)

manifest = {
    "schema": "komorebi-computation-manifest-v1",
    "date": "2026-09-23",
    "claim": "Phasewise transfer-matrix bounds certify leakage and thresholding error for weakly coupled polyphase Krylov operators.",
    "finite_surrogate": {
        "phases": phases,
        "phase_width": width,
        "operator_dimension": n,
        "depths": list(range(1, 9)),
        "thresholds": thresholds,
        "polynomial_coefficients": coefficients.tolist(),
        "seed": SEED,
        "arithmetic": "IEEE-754 float64",
    },
    "checks": {
        "H0_min_eigenvalue": min_eig_H0,
        "H_min_eigenvalue": min_eig_H,
        "all_depth_phase_envelopes_valid": bool(depth_df["phasewise_envelope_valid"].all()),
        "all_depth_difference_certificates_valid": bool(depth_df["phasewise_difference_valid"].all()),
        "all_threshold_certificates_valid": bool(threshold_df["certificate_valid"].all()),
        "all_polynomial_phase_certificates_valid": bool(poly_df["certificate_valid"].all()),
    },
    "non_claims": [
        "The finite experiment is not the proof of the theorem; the theorem is proved analytically in the manuscript.",
        "The experiment does not determine optimal pruning thresholds for arbitrary hardware or genotype data.",
        "The phasewise bounds may be conservative because they discard cancellation and singular-vector alignment.",
    ],
    "software": {
        "python": sys.version,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "matplotlib": matplotlib.__version__,
        "platform": platform.platform(),
    },
}
(HERE / "APPROXIMATE_LIGHTCONE_MANIFEST.json").write_text(json.dumps(manifest, indent=2))

print("Depth validation")
print(depth_df.to_string(index=False))
print("\nThreshold sweep")
print(threshold_df.to_string(index=False))
print("\nPolynomial certificate")
print(poly_df.to_string(index=False))
print("\nManifest checks")
print(json.dumps(manifest["checks"], indent=2))
