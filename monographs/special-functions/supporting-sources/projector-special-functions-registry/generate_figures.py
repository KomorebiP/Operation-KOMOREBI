from __future__ import annotations

from pathlib import Path
import json

import matplotlib.pyplot as plt
import mpmath as mp
import numpy as np
import sympy as sp

from special_functions import (
    D_value,
    block_appell_polynomials,
    congruential_euler_coefficients,
    congruential_euler_value,
    registry_entries,
    secant_coefficients,
    secant_parameter_polynomial,
    secant_value,
    spectral_zeta_N2_partial,
    spectral_zeta_N2_positive,
    theta_polynomials,
    transfer_exponential,
    transfer_tangent_coefficients,
    transfer_tangent_value,
    write_registry,
)

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)


def save(fig, name: str) -> None:
    fig.savefig(FIG / f"{name}.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


# 1. Transfer exponential decomposition.
x = np.linspace(-3.0, 3.0, 700)
fig, ax = plt.subplots(figsize=(9.0, 5.4))
N = 4
for j in range(N):
    values = np.array([transfer_exponential(N, j, float(t), terms=35).real for t in x])
    ax.plot(x, values, label=fr"$j={j}$")
ax.plot(x, np.exp(x), linestyle="--", linewidth=1.4, label=r"$e^x$ reconstruction")
ax.set_title(r"Transfer-exponential sections for $N=4$")
ax.set_xlabel("x")
ax.set_ylabel("value")
ax.legend(ncol=3)
ax.grid(alpha=0.25)
save(fig, "01_transfer_exponentials_N4")

# 2. Denominators.
x = np.linspace(-4.5, 4.5, 1000)
fig, ax = plt.subplots(figsize=(9.0, 5.2))
for N in (2, 3, 4, 5):
    y = np.array([D_value(N, float(t), terms=45).real for t in x])
    ax.plot(x, y, label=fr"$D_{N}$")
ax.axhline(0, linewidth=0.8)
ax.set_ylim(-4, 4)
ax.set_title("Universal transfer denominators")
ax.set_xlabel("x")
ax.set_ylabel(r"$D_N(x)$")
ax.legend()
ax.grid(alpha=0.25)
save(fig, "02_transfer_denominators")

# 3. Secants near origin.
x = np.linspace(-1.25, 1.25, 700)
fig, ax = plt.subplots(figsize=(9.0, 5.2))
for N in (2, 3, 4, 5):
    y = np.array([secant_value(N, 1, float(t), terms=50).real for t in x])
    ax.plot(x, y, label=fr"$\mathsf{{Sec}}_{N}$")
ax.set_title("Transfer secants on a common regular interval")
ax.set_xlabel("x")
ax.set_ylabel("value")
ax.legend()
ax.grid(alpha=0.25)
save(fig, "03_transfer_secants")

# 4. Transfer tangents.
x = np.linspace(-1.15, 1.15, 700)
fig, ax = plt.subplots(figsize=(9.0, 5.2))
for N in (2, 3, 4, 5):
    y = np.array([transfer_tangent_value(N, float(t), terms=55).real for t in x])
    ax.plot(x, y, label=fr"$\mathsf{{Tan}}_{N}$")
ax.set_title("Logarithmic-derivative companions")
ax.set_xlabel("x")
ax.set_ylabel("value")
ax.legend()
ax.grid(alpha=0.25)
save(fig, "04_transfer_tangents")

# 5. Congruential Euler coefficients.
Ns = list(range(2, 9))
rows = []
labels = []
for N in Ns:
    for j in range(N):
        coeff = congruential_euler_coefficients(N, j, 5)
        rows.append([float(abs(c)) if c else 0.0 for c in coeff])
        labels.append(f"{N},{j}")
arr = np.log10(1 + np.array(rows))
fig, ax = plt.subplots(figsize=(9.2, 10.0))
im = ax.imshow(arr, aspect="auto")
fig.colorbar(im, ax=ax, label=r"$\log_{10}(1+|E_{Nn}^{(N,j)}|)$")
ax.set_xticks(range(6), [str(n) for n in range(6)])
ax.set_yticks(range(len(labels)), labels, fontsize=7)
ax.set_xlabel("block index n")
ax.set_ylabel("(N,j)")
ax.set_title("Congruential Euler block coefficient atlas")
save(fig, "05_congruential_euler_heatmap")

# 6. Block-Appell polynomials.
polys = block_appell_polynomials(3, 1, 1, 7)
xx = np.linspace(-2.2, 2.2, 600)
fig, ax = plt.subplots(figsize=(9.0, 5.4))
x_symbol = sp.Symbol("x")
for m in range(1, 8):
    fn = sp.lambdify(x_symbol, polys[m], "numpy")
    ax.plot(xx, fn(xx), label=fr"$m={m}$")
ax.set_ylim(-30, 30)
ax.set_title(r"Block-Appell polynomials $E_m^{(3,1)}(x)$")
ax.set_xlabel("x")
ax.set_ylabel("polynomial value")
ax.legend(ncol=2)
ax.grid(alpha=0.25)
save(fig, "06_block_appell_polynomials")

# 7. Secancy parameter polynomials.
r = sp.Symbol("r")
rr = np.linspace(-2, 5, 500)
fig, ax = plt.subplots(figsize=(9.0, 5.4))
for n in range(1, 6):
    poly = secant_parameter_polynomial(3, n)
    fn = sp.lambdify(r, poly, "numpy")
    ax.plot(rr, fn(rr), label=fr"$P_{{3,{n}}}(r)$")
ax.set_ylim(-5000, 5000)
ax.set_title("Transfer-secancy parameter polynomials")
ax.set_xlabel("order parameter r")
ax.set_ylabel("coefficient polynomial")
ax.legend(ncol=2)
ax.grid(alpha=0.25)
save(fig, "07_secancy_parameter_polynomials")

# 8. Theta polynomials.
theta = theta_polynomials(5)
fig, ax = plt.subplots(figsize=(9.0, 5.4))
xx = np.linspace(-2.5, 2.5, 500)
for m in range(1, 6):
    fn = sp.lambdify(x_symbol, theta[m], "numpy")
    ax.plot(xx, fn(xx), label=fr"$\Theta_{{{2*m}}}(x)$")
ax.set_ylim(-5000, 5000)
ax.set_title("Euler-transfer theta polynomials")
ax.set_xlabel("x")
ax.set_ylabel("value")
ax.legend(ncol=2)
ax.grid(alpha=0.25)
save(fig, "08_theta_polynomials")

# 9. D4 zero geometry: exact axes from factorization.
ks = np.arange(-6, 7)
real_zeros = np.sqrt(2) * np.pi * (ks + 0.5)
imag_zeros = 1j * np.sqrt(2) * np.pi * (ks + 0.5)
fig, ax = plt.subplots(figsize=(7.0, 7.0))
ax.scatter(real_zeros, np.zeros_like(real_zeros), marker="o", label="cos factor")
ax.scatter(np.zeros_like(ks), imag_zeros.imag, marker="x", label="cosh factor")
ax.axhline(0, linewidth=0.8)
ax.axvline(0, linewidth=0.8)
ax.set_aspect("equal")
ax.set_xlabel("Re z")
ax.set_ylabel("Im z")
ax.set_title(r"Zero packets of $D_4(z)=\cos(z/\sqrt{2})\cosh(z/\sqrt{2})$")
ax.legend()
ax.grid(alpha=0.25)
save(fig, "09_D4_zero_packets")

# 10. Spectral zeta convergence for N=2.
ss = [2.0, 3.0, 4.0]
terms = np.unique(np.logspace(0, 4, 70).astype(int))
fig, ax = plt.subplots(figsize=(9.0, 5.3))
for s in ss:
    exact = spectral_zeta_N2_positive(s)
    errors = [float(abs(spectral_zeta_N2_partial(s, int(M)) - exact)) for M in terms]
    ax.loglog(terms, errors, label=fr"$s={s:g}$")
ax.set_xlabel("number of positive zeros")
ax.set_ylabel("absolute truncation error")
ax.set_title(r"Convergence of the positive-zero block zeta for $D_2=\cos z$")
ax.legend()
ax.grid(alpha=0.25)
save(fig, "10_spectral_zeta_convergence")

# 11. Novelty/status matrix.
entries = registry_entries()
status_names = ["classical boundary", "explicit derived", "candidate-new", "operator/schema"]
mat = np.zeros((len(entries), len(status_names)))
for i, e in enumerate(entries):
    text = (e.status + " " + e.object_type).lower()
    if "classical" in text:
        mat[i, 0] = 1
    if "explicit" in text or "proved" in text or "derived" in text:
        mat[i, 1] = 1
    if "candidate-new" in text:
        mat[i, 2] = 1
    if "operator" in text or "schema" in text or "multilinear" in text:
        mat[i, 3] = 1
fig, ax = plt.subplots(figsize=(9.6, 8.0))
im = ax.imshow(mat, aspect="auto")
ax.set_xticks(range(len(status_names)), status_names, rotation=20, ha="right")
ax.set_yticks(range(len(entries)), [e.family for e in entries], fontsize=8)
ax.set_title("Function registry by mathematical and novelty status")
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        if mat[i, j]:
            ax.text(j, i, "x", ha="center", va="center")
save(fig, "11_registry_status_matrix")

# 12. Coefficient growth of transfer secants.
fig, ax = plt.subplots(figsize=(9.0, 5.3))
for N in (2, 3, 4, 5, 6):
    coeff = secant_coefficients(N, 1, 12)
    y = [np.log10(1 + abs(float(v))) for v in coeff]
    ax.plot(range(len(y)), y, marker="o", label=fr"$N={N}$")
ax.set_xlabel("block index n")
ax.set_ylabel(r"$\log_{10}(1+|A_N(n)|)$")
ax.set_title("Growth of the principal transfer-secant coefficients")
ax.legend()
ax.grid(alpha=0.25)
save(fig, "12_secant_coefficient_growth")

write_registry(ROOT / "results")
print("generated 12 figure pairs and registry files")
