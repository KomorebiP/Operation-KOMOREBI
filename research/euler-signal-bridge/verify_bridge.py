"""Exact FIR / Euler coefficient bridge and reproducible signal-response figure.

Run: python verify_bridge.py
All arithmetic assertions use Python integers. The figure's frequency curves
use NumPy floating point and illustrate the filter, not an Euler DTFT.
"""
from datetime import datetime, timezone
from math import comb
from pathlib import Path
import hashlib
import json
import platform
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent


def mul(a, b):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def transfer_row(m, s, k):
    """Coefficients of (1+t)^s ((1+t)^m - 1)^k."""
    base = [0] + [comb(m, j) for j in range(1, m + 1)]
    out = [comb(s, j) for j in range(s + 1)]
    for _ in range(k):
        out = mul(out, base)
    return out


def forward_difference(values, order, start=0, stride=1):
    """Direct sample-space FIR stencil, independent of polynomial multiplication."""
    return sum((-1) ** (order - j) * comb(order, j)
               * values[start + stride * j] for j in range(order + 1))


def euler_even(count):
    """Signed Euler convention: cosh(t) * sech(t) = 1."""
    out = [1]
    for n in range(1, count):
        out.append(-sum(comb(2 * n, 2 * j) * out[j] for j in range(n)))
    return out


def pad(values, n):
    return values + [0] * (n - len(values))


def main():
    started = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()
    a = euler_even(48)
    c = [forward_difference(a, r) for r in range(len(a))]
    assert a[:5] == [1, -1, 5, -61, 1385]
    assert c[:5] == [1, -2, 8, -80, 1664]
    counts = {"Euler_coefficient_transfer": 0, "integer_signal_transfer": 0,
              "refinement_composition_rows": 0, "prime_residual_polynomials": 0}
    integer_signal = [(n * n * n - 7 * n + 3) * (-1) ** n for n in range(48)]
    for values, label in [(a, "Euler_coefficient_transfer"),
                          (integer_signal, "integer_signal_transfer")]:
        coefficients = [forward_difference(values, r) for r in range(48)]
        for m in range(1, 6):
            for s in range(m):
                for k in range(7):
                    row = transfer_row(m, s, k)
                    actual = sum(w * coefficients[r] for r, w in enumerate(row))
                    expected = forward_difference(values, k, s, m)
                    assert actual == expected, (label, m, s, k)
                    counts[label] += 1
    for m in range(1, 4):
        for n in range(1, 4):
            for s in range(m):
                for t in range(n):
                    for ell in range(5):
                        second = transfer_row(n, t, ell)
                        combined = [0] * (m * n * ell + m * t + s + 1)
                        for k, w in enumerate(second):
                            first = transfer_row(m, s, k)
                            for r, coefficient in enumerate(first):
                                combined[r] += w * coefficient
                        direct = transfer_row(m * n, m * t + s, ell)
                        assert combined == pad(direct, len(combined))
                        counts["refinement_composition_rows"] += 1
    for p in [2, 3, 5, 7, 11]:
        # Phi_p(t) = t^p + p B_p(t), with B_p integral.
        row = transfer_row(p, 0, 1)
        assert row[0] == 0 and row[p] == 1
        assert all(row[j] % p == 0 for j in range(1, p))
        counts["prime_residual_polynomials"] += 1

    outputs = [forward_difference(a, 1, stride=m) for m in [1, 2, 4]]
    assert outputs == [-2, 4, 1384]
    assert 2 * c[1] + c[2] == 4
    assert 2 * 4 + 1376 == 1384
    assert 4 * c[1] + 6 * c[2] + 4 * c[3] + c[4] == 1384
    result = {"status": "PASS", "exact_cases": sum(counts.values()),
              "checks": counts, "Euler_initial_values": a[:5],
              "Euler_binomial_coefficients": c[:5],
              "first_difference_outputs_at_spacing_1_2_4": outputs,
              "scope": "Finite exact controls of the derived operator identities; no universal congruence inferred from this run."}
    result_path = ROOT / "exact_results.json"
    result_path.write_text(json.dumps(result, indent=2) + "\n")

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                         "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.0))
    fig.patch.set_facecolor("#fbfaf7")
    colors = ["#256c87", "#ad5b32", "#65528a"]
    omega = np.linspace(0, np.pi, 1001)
    for col, (m, color, output) in enumerate(zip([1, 2, 4], colors, outputs)):
        ax = axes[0, col]
        ax.set_facecolor("#fbfaf7")
        # Forward-index stencil a[n+m] - a[n].
        ax.axhline(0, color="#8a8a8a", linewidth=0.8)
        ax.vlines([0, m], 0, [-1, 1], color=color, linewidth=3)
        ax.scatter([0, m], [-1, 1], color=color, s=70, zorder=3)
        ax.set(xlim=(-0.5, 4.5), ylim=(-1.35, 1.35), xticks=range(5),
               yticks=[-1, 0, 1], xlabel="Sample offset", ylabel="Tap weight")
        ax.set_title(f"Spacing {m}: a[n+{m}] − a[n]", fontsize=13, pad=14)
        ax.text(0.5, -0.38, f"Euler output at n = 0: {output:,}",
                transform=ax.transAxes, ha="center", color=color, fontsize=12)
        ax = axes[1, col]
        ax.set_facecolor("#fbfaf7")
        gain = np.abs(np.exp(1j * m * omega) - 1)
        ax.plot(omega / np.pi, gain, color=color, linewidth=2.5)
        ax.set(xlim=(0, 1), ylim=(-0.08, 2.18), xticks=[0, 0.5, 1],
               yticks=[0, 1, 2], xlabel="Frequency ω / π", ylabel="Filter gain |H(ω)|")
        ax.grid(alpha=0.18)
    fig.suptitle("One difference filter, two mathematical readings", x=0.07,
                 ha="left", fontsize=21, fontweight="bold", y=0.98)
    fig.text(0.07, 0.915,
             "Top: exact integer taps and Euler outputs. Bottom: response to sinusoidal signals.", fontsize=12)
    fig.text(0.07, 0.025,
             "The response belongs to the filter. No Fourier spectrum is assigned to the growing Euler sequence.",
             fontsize=11, color="#555555")
    fig.subplots_adjust(left=0.075, right=0.975, top=0.80, bottom=0.115,
                        hspace=0.95, wspace=0.35)
    image_path = ROOT / "Komorebi_Euler_Signal_Bridge.png"
    fig.savefig(image_path, dpi=170, facecolor=fig.get_facecolor())
    plt.close(fig)

    manifest = {
        "schema_version": 1,
        "claim_id": "EulerSignalBridge-FIR-2026-10-09",
        "repository": {"commit": "standalone script; no Git repository", "dirty": True},
        "command": "python verify_bridge.py",
        "environment": {"software": [f"Python {platform.python_version()}",
                                         f"NumPy {np.__version__}",
                                         f"Matplotlib {matplotlib.__version__}"],
                        "hardware": f"{platform.system()} {platform.machine()}; CPU only"},
        "mathematics": {
            "assertion_tested": "FIR stencil equals finite binomial-coordinate transfer; successive affine transfers compose; prime residual coefficients are integral.",
            "coefficient_domain": "Python arbitrary-precision integers for all arithmetic checks; float64 only for illustrative frequency curves",
            "conventions": "Signed Euler EGF sech(t); a(n)=E_(2n); advance shift S a(n)=a(n+1); Delta=S-I.",
            "inputs": ["Signed Euler sequence through E_94", "deterministic alternating cubic integer signal", "affine transfer polynomial rows"],
            "bounds": {"sample_count": 48, "transfer_M": [1, 5], "phase_s": "0 <= s < M", "difference_k": [0, 6], "composition_M_N": [1, 3], "composition_order": [0, 4], "primes": [2, 3, 5, 7, 11]},
            "non_claims": ["No Fourier transform of the Euler sequence", "No universal Euler congruence follows from finite checks", "No novelty claim for the FIR or binomial identities", "No Lean build performed"]},
        "randomness": {"used": False, "generator": "none", "seed": None},
        "run": {"started_at": started, "runtime_seconds": time.perf_counter() - clock, "exit_status": 0},
        "outputs": [{"path": p.name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                    for p in [result_path, image_path]],
        "checks": ["direct sample stencil versus independently expanded polynomial rows", "exact composition coefficient comparison", "small hand-computable Euler controls", "prime coefficient divisibility"],
        "result": f"PASS: {sum(counts.values())} exact finite assertions plus initial-value controls.",
        "residual_risks": ["A version 1 manifest records limited execution provenance; the script hash is separately supplied.", "Full-branch valuation bounds require a separate mathematical argument."]}
    (ROOT / "computation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (ROOT / "SOURCE_SHA256.txt").write_text(hashlib.sha256(Path(__file__).read_bytes()).hexdigest() + "  verify_bridge.py\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
