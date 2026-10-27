"""Twenty-four exact numerical lessons for Papers VII and VIII.

Portable finite core derived from the equations and algorithms in:
  projector_generated_special_functions_vii.py
    SHA256 35bcbf6e2a42c7e13222a4907e63db341b1d22b4f8e3731d5552dd8844e41265
  projector_generated_special_functions_viii.py
    SHA256 632ec2b1e85aa06c159c8b1e797820ad1c6394b3dbcd6588d80d63e0a4c1479a
Original manuscripts: Komorebi P., Projector-Generated Special Functions VII
and VIII. This local implementation preserves attribution and the declared
ordered symmetric-q convention. No separate license grant is inferred from
the archived releases; any public redistribution follows their owner's terms.
New diagrams and diagnostic computations belong to this guide.

Run: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python figures_vii_viii.py
Dependencies: Python, NumPy, SciPy, Matplotlib, and adjacent guide_style.py.
All matrices are computed here; no extraction directory or network is used.
"""
from __future__ import annotations

from datetime import datetime, timezone
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import math
import platform
import sys
import time

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
import numpy as np
import scipy
from scipy.linalg import null_space

from guide_style import apply_style, save_figure, COLORS, INK, MUTED, PALE

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
FIGURES = ROOT / "figures"
CHECKS: list[dict] = []
STEMS: list[str] = []
SHAPES = (0.7, 1.1, 0.9)
FOUR_SHAPES = (0.55, 0.8, 1.05, 1.3)
TREES = (
    ("(((12)3)4)", ((0, 1), (0, 1, 2))),
    ("((1(23))4)", ((1, 2), (0, 1, 2))),
    ("(1((23)4))", ((1, 2), (1, 2, 3))),
    ("(1(2(34)))", ((2, 3), (1, 2, 3))),
    ("((12)(34))", ((0, 1), (2, 3))),
)


def check(name, residual, tolerance=1e-9, **scope):
    record = {"name": name, "residual": float(residual),
              "tolerance": float(tolerance), "passed": bool(residual <= tolerance),
              "scope": scope}
    CHECKS.append(record)
    if not record["passed"]:
        raise AssertionError(record)


def witness(name, passed, **scope):
    CHECKS.append({"name": name, "passed": bool(passed), "scope": scope})
    if not passed:
        raise AssertionError(name)


def qnum(x, q):
    if abs(q - 1.0) < 1e-14:
        return float(x)
    theta = -math.log(q)
    return math.sinh(float(x) * theta) / math.sinh(theta)


@lru_cache(maxsize=None)
def compositions(total, factors):
    if factors == 1:
        return ((total,),)
    return tuple((n,) + tail for n in range(total + 1)
                 for tail in compositions(total - n, factors - 1))


def lowering(total, kappas, q=1.0, subset=None):
    kappas = tuple(kappas)
    m = len(kappas)
    active = tuple(range(m)) if subset is None else tuple(subset)
    current = compositions(total, m)
    if total == 0:
        return np.zeros((0, len(current)))
    previous = compositions(total - 1, m)
    row = {s: j for j, s in enumerate(previous)}
    out = np.zeros((len(previous), len(current)))
    for j, state in enumerate(current):
        for pos, factor in enumerate(active):
            n = state[factor]
            if n == 0:
                continue
            weight = math.sqrt(qnum(n, q) * qnum(2*kappas[factor]+n-1, q))
            exponent = (sum(state[r]+kappas[r] for r in active[pos+1:])
                        - sum(state[r]+kappas[r] for r in active[:pos]))
            target = list(state)
            target[factor] -= 1
            out[row[tuple(target)], j] += weight * q**exponent
    return out


def casimir(total, kappas, q, subset):
    basis = compositions(total, len(kappas))
    k0 = [sum(s[r]+kappas[r] for r in subset) for s in basis]
    low = lowering(total, kappas, q, subset)
    return np.diag([qnum(x, q)*qnum(x-1, q) for x in k0]) - low.T @ low


@lru_cache(maxsize=512)
def frame(total, kappas, q=1.0):
    kappas = tuple(kappas)
    if total == 0:
        return np.ones((1, 1))
    return null_space(lowering(total, kappas, q), rcond=1e-12)


def pair_spectrum(total, ka, kb, q):
    return np.array([qnum(ka+kb+j, q)*qnum(ka+kb+j-1, q)
                     for j in range(total+1)])


@lru_cache(maxsize=512)
def recouple(total, kappas=SHAPES, q=1.0):
    kappas = tuple(kappas)
    Q = frame(total, kappas, q)
    A = Q.T @ casimir(total, kappas, q, (0, 1)) @ Q
    B = Q.T @ casimir(total, kappas, q, (1, 2)) @ Q
    lv, L = np.linalg.eigh(A)
    rv, R = np.linalg.eigh(B)
    L, R = Q @ L, Q @ R
    overlap = L.T @ R
    for j in range(overlap.shape[1]):
        if overlap[0, j] < 0:
            R[:, j] *= -1
    overlap = L.T @ R
    for j in range(overlap.shape[0]):
        if overlap[j, 0] < 0:
            L[:, j] *= -1
    overlap = L.T @ R
    return {"Q": Q, "L": L, "R": R, "overlap": overlap, "lv": lv, "rv": rv,
            "J": overlap @ np.diag(rv) @ overlap.T}


def entropy(p):
    p = np.asarray(p, dtype=float)
    return -np.sum(p*np.log(np.maximum(p, 1e-300)), axis=-1)


def exact_r2():
    return np.array([[1/3, 1/math.sqrt(3), math.sqrt(5)/3],
                     [1/math.sqrt(3), 1/2, -math.sqrt(15)/6],
                     [math.sqrt(5)/3, -math.sqrt(15)/6, 1/6]])


def beam(q):
    S = 1+q*q
    c, s = q/S, math.sqrt(1+q*q+q**4)/S
    return np.array([[c, s], [s, -c]])


def lowest_seed(N, k1, k2, q):
    v = np.ones(N+1)
    tilt = q**(-(N-1+k1+k2))
    for n in range(N):
        v[n+1] = -tilt*v[n]*math.sqrt(
            qnum(N-n, q)*qnum(2*k2+N-n-1, q)
            / (qnum(n+1, q)*qnum(2*k1+n, q)))
    return v/np.linalg.norm(v)


def align(reference, candidate):
    candidate = candidate.copy()
    for _ in range(8):
        for j in range(candidate.shape[1]):
            if np.dot(reference[:, j], candidate[:, j]) < 0:
                candidate[:, j] *= -1
        for j in range(candidate.shape[0]):
            if np.dot(reference[j], candidate[j]) < 0:
                candidate[j] *= -1
    return candidate


def tangent(N, theta, step=2e-5):
    R = recouple(N, SHAPES, math.exp(-theta))["overlap"]
    plus = align(R, recouple(N, SHAPES, math.exp(-(theta+step)))["overlap"])
    minus = align(R, recouple(N, SHAPES, math.exp(-(theta-step)))["overlap"])
    derivative = (plus-minus)/(2*step)
    raw = R.T @ derivative
    A = (raw-raw.T)/2
    return R, derivative, raw, A


def tree_bases(N, q=1.0):
    Q = frame(N, FOUR_SHAPES, q)
    result = []
    for name, subsets in TREES:
        operators = [Q.T @ casimir(N, FOUR_SHAPES, q, s) @ Q for s in subsets]
        _, V = np.linalg.eigh(math.sqrt(2)*operators[0]+math.sqrt(3)*operators[1])
        diagonal = [V.T @ C @ V for C in operators]
        order = sorted(range(V.shape[1]),
                       key=lambda j: tuple(round(D[j, j], 9) for D in diagonal))
        V = V[:, order]
        diagonal = [V.T @ C @ V for C in operators]
        labels = []
        for j in range(V.shape[1]):
            labels.append(tuple(int(np.argmin(np.abs(
                pair_spectrum(N, sum(FOUR_SHAPES[r] for r in s), 0, q)
                - diagonal[k][j, j]))) for k, s in enumerate(subsets)))
        comm = np.max(np.abs(operators[0] @ operators[1]
                             - operators[1] @ operators[0]))
        diag = max(np.max(np.abs(D-np.diag(np.diag(D)))) for D in diagonal)
        result.append({"name": name, "basis": Q @ V, "labels": labels,
                       "commutator": comm, "diagonalization": diag})
    return result


def loop_product(bases):
    arrays = [b["basis"] if isinstance(b, dict) else b for b in bases]
    edges = [a.T @ arrays[(j+1) % len(arrays)] for j, a in enumerate(arrays)]
    out = np.eye(edges[0].shape[0])
    for edge in edges:
        out = out @ edge
    return out, edges


def givens(R):
    work = R.copy()
    rotations = []
    d = len(R)
    for col in range(d-1):
        for row in range(d-1, col, -1):
            a, b = work[row-1, col], work[row, col]
            if abs(b) < 1e-14:
                continue
            length = math.hypot(a, b)
            G = np.eye(d)
            G[row-1, row-1] = G[row, row] = a/length
            G[row-1, row] = b/length
            G[row, row-1] = -b/length
            work = G @ work
            rotations.append(G)
    rebuilt = work.copy()
    for G in reversed(rotations):
        rebuilt = G.T @ rebuilt
    return rotations, work, rebuilt


def qp(a, q, n):
    product = 1+0j
    for r in range(n):
        product *= 1-a*q**r
    return product


def qr(n, y, a, b, c, d, q):
    return sum(qp(q**(-n), q, k)*qp(a*b*q**(n+1), q, k)
               *qp(q**(-y), q, k)*qp(c*d*q**(y+1), q, k)
               / (qp(a*q, q, k)*qp(b*d*q, q, k)
                  *qp(c*q, q, k)*qp(q, q, k))*q**k
               for k in range(min(n, y)+1))


def aw(n, z, a, b, c, d, q):
    return sum(qp(q**(-n), q, k)*qp(a*b*c*d*q**(n-1), q, k)
               *qp(a*z, q, k)*qp(a/z, q, k)
               / (qp(a*b, q, k)*qp(a*c, q, k)
                  *qp(a*d, q, k)*qp(q, q, k))*q**k
               for k in range(n+1))


def aw_operator(f, z, a, b, c, d, q):
    def coeff(x):
        return ((1-a*x)*(1-b*x)*(1-c*x)*(1-d*x)
                / ((1-x*x)*(1-q*x*x)))
    return (coeff(z)*(f(q*z)-f(z))+coeff(1/z)*(f(z/q)-f(z))
            +(1+a*b*c*d/q)*f(z))


def two_axes():
    return plt.subplots(1, 2, figsize=(8.1, 4.2), constrained_layout=True)


def heat(ax, values, title, signed=True, annotate=False, colorbar=True):
    values = np.asarray(values)
    if signed:
        limit = max(float(np.max(np.abs(values))), 1e-15)
        image = ax.imshow(values, cmap="RdBu_r", vmin=-limit, vmax=limit)
    else:
        image = ax.imshow(values, cmap="YlGnBu", vmin=0,
                          vmax=max(float(np.max(values)), 1e-15))
    ax.set_title(title)
    ax.set_xlabel("right / column label")
    ax.set_ylabel("left / row label")
    if len(values) <= 8:
        ax.set_xticks(range(values.shape[1]))
        ax.set_yticks(range(values.shape[0]))
    if annotate:
        for j in range(values.shape[0]):
            for k in range(values.shape[1]):
                text_color = "white" if abs(values[j, k]) > .65*np.max(abs(values)) else INK
                label = "0" if abs(values[j, k]) < 5e-4 else f"{values[j,k]:.3f}"
                ax.text(k, j, label, ha="center", va="center",
                        fontsize=11, color=text_color)
    if colorbar:
        ax.figure.colorbar(image, ax=ax, fraction=.048, pad=.025)
    return image


def save(fig, stem):
    save_figure(fig, stem)
    STEMS.append(stem)


def classical_lessons():
    # VII.01: local ladder.
    fig, axs = two_axes()
    n = np.arange(7)
    for k in (.5, 1., 1.5):
        axs[0].plot(n, n+k, marker="o", label=fr"$\kappa={k:g}$")
        axs[1].plot(n, np.sqrt((n+1)*(n+2*k)), marker="o", label=fr"$\kappa={k:g}$")
    axs[0].set(title="Degree and weight", xlabel="occupation n", ylabel=r"$K_0$ eigenvalue")
    axs[1].set(title="Raising amplitudes", xlabel="occupation n", ylabel=r"$\sqrt{(n+1)(n+2\kappa)}$")
    axs[0].legend()
    for ax in axs: ax.grid()
    check("VII01 half-shape raising coefficient", abs(math.sqrt(3*3)-3), 0, n=2, kappa=.5)
    save(fig, "vii_01_ladder")

    # VII.02: exact excitation simplex and compression.
    fig, axs = two_axes()
    states = np.array(compositions(4, 3))
    x = states[:, 1]+states[:, 2]/2
    y = math.sqrt(3)*states[:, 2]/2
    dots = axs[0].scatter(x, y, c=states[:, 2], cmap="viridis", s=180, edgecolors="white")
    for state, a, b in zip(states, x, y):
        axs[0].text(a, b+.15, "".join(map(str, state)), ha="center", fontsize=9)
    axs[0].set(title="N = 4: fifteen occupation states", aspect="equal")
    axs[0].axis("off")
    fig.colorbar(dots, ax=axs[0], fraction=.045, label=r"$n_3$")
    ns = np.arange(9)
    axs[1].plot(ns, [(N+1)*(N+2)/2 for N in ns], "o-", label="full excitation")
    axs[1].plot(ns, ns+1, "s-", label="lowest-weight packet")
    axs[1].set(title="Three-factor dimensions", xlabel="total excitation N", ylabel="dimension")
    axs[1].legend()
    axs[1].grid()
    check("VII02 composition count", abs(len(states)-15), 0, total=4, factors=3)
    save(fig, "vii_02_simplex")

    # VII.03: exact coefficient plane and next lowering matrix.
    fig = plt.figure(figsize=(8.1, 4.2), constrained_layout=True)
    ax = fig.add_subplot(121, projection="3d")
    u, v = np.meshgrid(np.linspace(-.8, .8, 7), np.linspace(-.8, .8, 7))
    ax.plot_surface(u, v, -u-v, alpha=.25, color=COLORS[0], edgecolor="white")
    vectors = [np.array([1, 1, -2])/math.sqrt(6), np.array([1, -1, 0])/math.sqrt(2)]
    for color, vector, label in zip(COLORS, vectors, [r"$\ell_0$", r"$\ell_1$"]):
        ax.quiver(0, 0, 0, *vector, color=color, linewidth=2.3, arrow_length_ratio=.13)
        ax.text(*(vector*1.12), label, color=color)
    ax.set(xlabel=r"$x_{100}$", ylabel=r"$x_{010}$", zlabel=r"$x_{001}$",
           title="N = 1: lowest-weight plane")
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(22, 135)
    ax.set_xticks([-.8, 0, .8])
    ax.set_yticks([-.8, 0, .8])
    ax.set_zticks([-1, 0, 1])
    ax.set_zlabel("")
    ax.text2D(.03, .91, r"$x_{001}$: vertical axis", transform=ax.transAxes,
              fontsize=10, bbox={"facecolor": "white", "edgecolor": "none", "alpha": .9})
    ax.tick_params(labelsize=8)
    low = lowering(2, (.5, .5, .5))
    ax2 = fig.add_subplot(122)
    heat(ax2, low, "N = 2: lowering 6 → 3", signed=False, annotate=True)
    ax2.set(xlabel="degree-two source", ylabel="degree-one target")
    Q = frame(2, (.5, .5, .5), 1.)
    check("VII03 lowest-weight kernel", np.max(abs(low @ Q)), 1e-12, total=2, shapes=[.5]*3)
    check("VII03 kernel dimension", abs(Q.shape[1]-3), 0, total=2)
    save(fig, "vii_03_lowest_plane")

    # VII.04: pair observables carry spectra and basis information.
    data = recouple(4)
    fig, axs = two_axes()
    j = np.arange(5)
    axs[0].plot(j, data["lv"], "o-", label=r"$C_{12}$")
    axs[0].plot(j, data["rv"], "s-", label=r"$C_{23}$")
    axs[0].set(title="Two quadratic spectra", xlabel="intermediate label", ylabel="Casimir eigenvalue")
    axs[0].legend()
    axs[0].grid()
    heat(axs[1], data["overlap"], "Overlap between eigenbases", annotate=True)
    check("VII04 pair spectra", max(np.max(abs(data["lv"]-pair_spectrum(4, .7, 1.1, 1.))),
          np.max(abs(data["rv"]-pair_spectrum(4, 1.1, .9, 1.)))), 1e-11, total=4, shapes=SHAPES)
    save(fig, "vii_04_pair_atlases")

    # VII.05: exact shape-controlled two-channel overlap.
    fig, axs = two_axes()
    middle = np.linspace(.1, 2., 100)
    cs = np.sqrt(.7*.9/((.7+middle)*(middle+.9)))
    ss = np.sqrt(middle*(.7+middle+.9)/((.7+middle)*(middle+.9)))
    axs[0].plot(middle, cs, label="c")
    axs[0].plot(middle, ss, label="s")
    axs[0].axvline(1.1, ls=":", color=MUTED)
    axs[0].set(title="The middle shape controls mixing", xlabel=r"$\kappa_2$", ylabel="amplitude", ylim=(0, 1.03))
    axs[0].legend()
    axs[0].grid()
    c, s = math.sqrt(.175), math.sqrt(.825)
    R = np.array([[c, s], [s, -c]])
    heat(axs[1], R, "N = 1, shapes (0.7, 1.1, 0.9)", annotate=True)
    check("VII05 shape beam splitter", np.max(abs(R-recouple(1)["overlap"])), 1e-12, shapes=SHAPES)
    save(fig, "vii_05_shape_beam")

    # VII.06: full exact three-channel example.
    R = exact_r2()
    fig, axs = two_axes()
    heat(axs[0], R, "Signed amplitude matrix", annotate=True)
    heat(axs[1], R*R, "Measured probability matrix", signed=False, annotate=True)
    check("VII06 exact N2 overlap", np.max(abs(R-recouple(2, (.5, .5, .5))["overlap"])),
          1e-12, total=2, shapes=[.5]*3)
    check("VII06 orthogonality", np.max(abs(R.T@R-np.eye(3))), 1e-12, total=2)
    save(fig, "vii_06_exact_three")

    # VII.07: interference survives coherent recoupling.
    fig, axs = two_axes()
    a = np.array([1., -1., 0.])/math.sqrt(2)
    contributions = np.vstack([R[0]/math.sqrt(2), -R[1]/math.sqrt(2)])
    b = R.T @ a
    x = np.arange(3)
    axs[0].bar(x-.17, contributions[0], .34, label="from left 0")
    axs[0].bar(x+.17, contributions[1], .34, label="from left 1")
    axs[0].plot(x, b, "ko", label="coherent sum")
    axs[0].axhline(0, color=MUTED, lw=.8)
    axs[0].set(title="Add signed routes first", xlabel="right label", ylabel="amplitude", xticks=x)
    axs[0].legend(fontsize=10)
    coherent, dephased = b*b, (a*a) @ (R*R)
    axs[1].bar(x-.17, coherent, .34, label="retain phase")
    axs[1].bar(x+.17, dephased, .34, label="dephase first")
    axs[1].set(title="Two different output laws", xlabel="right label", ylabel="probability", xticks=x)
    axs[1].legend(fontsize=10)
    check("VII07 coherent probability sum", abs(sum(coherent)-1), 1e-12, amplitudes=a.tolist())
    check("VII07 dephased probability sum", abs(sum(dephased)-1), 1e-12)
    witness("VII07 phase distinction", np.max(abs(coherent-dephased)) > .1,
            coherent=coherent.tolist(), dephased=dephased.tolist())
    save(fig, "vii_07_phase_measurement")

    # VII.08: signed recurrence and positive Jacobi gauge.
    data = recouple(6)
    J, R = data["J"], data["overlap"]
    signs = np.ones(7)
    for j in range(6):
        signs[j+1] = signs[j]*np.sign(J[j, j+1])
    positive = signs[:, None]*J*signs[None, :]
    fig, axs = two_axes()
    heat(axs[0], J, "First-row/column-positive overlap gauge")
    heat(axs[1], positive, "Rephased positive-adjacent gauge")
    for ax in axs: ax.set(xlabel="left Casimir label", ylabel="left Casimir label")
    mask = np.abs(np.arange(7)[:, None]-np.arange(7)[None, :]) > 1
    check("VII08 tridiagonal selection", np.max(abs(J[mask])), 1e-11, total=6, shapes=SHAPES)
    witness("VII08 positive adjacent gauge", np.min(np.diag(positive, 1)) > 0,
            adjacent= np.diag(positive, 1).tolist())
    check("VII08 recurrence after gauge", np.max(abs(positive@(signs[:, None]*R)
          -(signs[:, None]*R)@np.diag(data["rv"]))), 1e-10, total=6)
    save(fig, "vii_08_recurrence_gauge")

    # VII.09: entropy and majorization for a fixed measured kernel.
    fig, axs = two_axes()
    R = recouple(5)["overlap"]
    p = np.array([.7, .1, .05, .05, .05, .05])
    out = p @ (R*R)
    x = np.arange(6)
    axs[0].bar(x-.17, p, .34, label=f"input H={entropy(p):.3f}")
    axs[0].bar(x+.17, out, .34, label=f"output H={entropy(out):.3f}")
    axs[0].set(title="One fixed measurement channel", xlabel="label", ylabel="probability")
    axs[0].legend(fontsize=10)
    axs[1].plot(np.arange(7), np.r_[0, np.cumsum(np.sort(p)[::-1])], "o-", label="sorted input")
    axs[1].plot(np.arange(7), np.r_[0, np.cumsum(np.sort(out)[::-1])], "s-", label="sorted output")
    axs[1].set(title="Majorization: concentration decreases", xlabel="largest entries retained", ylabel="cumulative probability")
    axs[1].legend(fontsize=10)
    axs[1].grid()
    witness("VII09 entropy nondecrease", entropy(out) >= entropy(p)-1e-12,
            total=5, input=p.tolist(), output=out.tolist(),
            input_entropy=float(entropy(p)), output_entropy=float(entropy(out)))
    check("VII09 bistochasticity", max(np.max(abs(np.sum(R*R, 0)-1)),
          np.max(abs(np.sum(R*R, 1)-1))), 1e-12, total=5)
    save(fig, "vii_09_entropy")

    # VII.10: five planar trees and one exact joint-address lattice.
    fig, axs = two_axes()
    draw_pentagon(axs[0], "Five complete tree atlases")
    trees = tree_bases(4)
    labels = np.array(trees[0]["labels"])
    axs[1].scatter(labels[:, 0], labels[:, 1], s=100, color=COLORS[0])
    for a, b in labels:
        axs[1].text(a+.10, b-.10, f"{a},{b}", fontsize=9)
    axs[1].set(title="Addresses for (((12)3)4)", xlabel=r"$j_{12}$", ylabel=r"$j_{123}$",
               xticks=range(5), yticks=range(5), xlim=(-.4, 4.6), ylim=(-.4, 4.5))
    axs[1].grid()
    witness("VII10 joint address completeness",
            set(map(tuple, labels)) == {(j, k) for k in range(5) for j in range(k+1)},
            total=4, dimension=len(labels))
    check("VII10 joint eigenbases", max(t["diagonalization"] for t in trees), 1e-10, total=4)
    save(fig, "vii_10_tree_addresses")

    # VII.11: a loop is not an independent projector test.
    fig, axs = two_axes()
    N = 2
    trees = tree_bases(N)
    Q = frame(N, FOUR_SHAPES, 1.)
    d = Q.shape[1]
    rng = np.random.default_rng(73011)
    random_changes = [np.linalg.qr(rng.normal(size=(d, d)))[0] for _ in range(5)]
    rephased = [t["basis"] @ O for t, O in zip(trees, random_changes)]
    wrong = np.eye(Q.shape[0])[:, :d]
    wrong_bases = [wrong @ O for O in random_changes]
    low = lowering(N, FOUR_SHAPES)
    loop_errors = []
    kernel_errors = []
    for bases, F in [(trees, Q), (rephased, Q), (wrong_bases, wrong)]:
        product, _ = loop_product(bases)
        loop_errors.append(np.max(abs(product-np.eye(d))))
        kernel_errors.append(np.max(abs(low @ F)))
    positions = np.arange(3)
    axs[0].bar(positions, np.maximum(loop_errors, 1e-16), color=COLORS[0])
    axs[1].bar(positions, np.maximum(kernel_errors, 1e-16), color=[COLORS[0], COLORS[0], COLORS[1]])
    for ax in axs:
        ax.set_yscale("log")
        ax.set_xticks(positions, ["Casimir\natlases", "changed\ncoordinates", "wrong common\nsubspace"])
        ax.tick_params(axis="x", labelsize=10)
        ax.grid(axis="y")
    axs[0].set(title="Every common-space loop closes", ylabel="maximum loop error")
    axs[1].set(title="The lowering check distinguishes them", ylabel="maximum kernel error")
    check("VII11 loop checks", max(loop_errors), 1e-12, total=N, dimension=d)
    witness("VII11 wrong projector negative control", kernel_errors[-1] > 1,
            loop_errors=loop_errors, lowering_errors=kernel_errors,
            seed=73011)
    save(fig, "vii_11_loop_scope")

    # VII.12: finite rotation compiler.
    fig, axs = two_axes()
    R = recouple(5)["overlap"]
    rotations, D, rebuilt = givens(R)
    heat(axs[0], D, "After row rotations: diagonal signs", annotate=True)
    dimensions = np.arange(2, 10)
    counts = [len(givens(recouple(int(d-1))["overlap"])[0]) for d in dimensions]
    axs[1].plot(dimensions, counts, "o-", label="generated rotations")
    axs[1].plot(dimensions, dimensions*(dimensions-1)/2, "--", color=COLORS[1], label="triangular bound")
    axs[1].set(title="Rotation counts in reduced dimension", xlabel="packet dimension d", ylabel="two-coordinate rotations")
    axs[1].legend(fontsize=10)
    axs[1].grid()
    check("VII12 Givens reconstruction", np.max(abs(rebuilt-R)), 1e-12,
          total=5, dimension=6, rotations=len(rotations))
    check("VII12 diagonal signs", np.max(abs(D-np.diag(np.diag(D)))), 1e-12)
    witness("VII12 rotation bound", all(c <= d*(d-1)//2 for c, d in zip(counts, dimensions)),
            dimensions=dimensions.tolist(), counts=counts)
    save(fig, "vii_12_compiler")


def draw_pentagon(ax, title):
    angles = np.pi/2 + np.arange(5)*2*np.pi/5
    positions = np.column_stack([np.cos(angles), np.sin(angles)])
    for j, p in enumerate(positions):
        nxt = positions[(j+1) % 5]
        ax.plot([p[0], nxt[0]], [p[1], nxt[1]], color=COLORS[0], alpha=.6)
    short = ["12 / 123", "23 / 123", "23 / 234", "34 / 234", "12 / 34"]
    for j, ((name, _), p) in enumerate(zip(TREES, positions)):
        ax.scatter(*p, s=550, color=PALE, edgecolor=COLORS[0], linewidth=1.5, zorder=3)
        ax.text(*p, str(j), ha="center", va="center", fontweight="bold", zorder=4)
        outward = p*1.48
        alignment = "right" if p[0] < -.4 else "left" if p[0] > .4 else "center"
        ax.text(outward[0], outward[1], name+"\n"+short[j],
                ha=alignment, va="center", fontsize=9)
    ax.set(title=title, xlim=(-1.9, 1.9), ylim=(-1.65, 1.72), aspect="equal")
    ax.axis("off")


def deformed_lessons():
    # VIII.01: positive symmetric q-numbers.
    fig, axs = two_axes()
    x = np.linspace(0, 5, 100)
    for q in (1., .85, .5):
        values = np.array([qnum(t, q) for t in x])
        axs[0].plot(x, values, label=f"q={q:g}")
        positive = x > 0
        axs[1].plot(x[positive], values[positive]/x[positive], label=f"q={q:g}")
    axs[0].set(title="Symmetric q-number", xlabel="x", ylabel=r"$[x]_q$")
    axs[1].set(title="Deformation relative to x", xlabel="positive x", ylabel=r"$[x]_q/x$")
    axs[0].legend()
    for ax in axs: ax.grid()
    check("VIII01 q-number benchmark", abs(qnum(2, .5)-2.5), 1e-14, q=.5, x=2)
    save(fig, "viii_01_q_numbers")

    # VIII.02: ordered coproduct coefficients and an independent N1 formula.
    fig, axs = two_axes()
    kappas = SHAPES
    q_grid = np.linspace(.6, 1., 81)
    coefficients = np.array([lowering(1, kappas, q)[0] for q in q_grid])
    # Composition order is 001,010,100; show this declared order.
    for j, label in enumerate(["001", "010", "100"]):
        axs[0].plot(q_grid, coefficients[:, j], label=label)
    axs[0].set(title="Three ordered lowering routes", xlabel="q", ylabel="lowering amplitude")
    axs[0].legend()
    axs[0].grid()
    q = .73
    direct = np.array([
        q**(-kappas[0]-kappas[1])*math.sqrt(qnum(2*kappas[2], q)),
        q**(-kappas[0]+kappas[2])*math.sqrt(qnum(2*kappas[1], q)),
        q**(kappas[1]+kappas[2])*math.sqrt(qnum(2*kappas[0], q)),
    ])
    values = lowering(1, kappas, q)[0]
    xx = np.arange(3)
    axs[1].bar(xx-.17, values, .34, label="iterated matrix")
    axs[1].bar(xx+.17, direct, .34, label="three-term coproduct")
    axs[1].set(title="Both bracketings agree at q = 0.73", xlabel="source occupation", ylabel="amplitude",
               xticks=xx, xticklabels=["001", "010", "100"])
    axs[1].legend(fontsize=10)
    check("VIII02 coproduct routing", np.max(abs(values-direct)), 1e-12,
          q=q, total=1, shapes=kappas, composition_order=["001", "010", "100"])
    save(fig, "viii_02_coproduct")

    # VIII.03: signed lowest-weight seed and q-tilted probabilities.
    fig, axs = two_axes()
    n = np.arange(6)
    for q in (1., .85, .73):
        v = lowest_seed(5, .7, 1.1, q)
        axs[0].plot(n, v, "o-", label=f"q={q:g}")
        axs[1].plot(n, v*v, "s-", label=f"q={q:g}")
        check("VIII03 seed lowering", np.max(abs(lowering(5, (.7, 1.1), q) @ v)),
              1e-10, q=q, total=5, shapes=[.7, 1.1])
        Q = frame(5, (.7, 1.1), q)[:, 0]
        check("VIII03 seed and nullspace", 1-abs(float(np.dot(v, Q))), 1e-12, q=q, total=5)
    axs[0].axhline(0, color=MUTED, lw=.8)
    axs[0].set(title="The lowest seed alternates sign", xlabel=r"$n\ \mathrm{in}\ |n,5-n\rangle$", ylabel="amplitude")
    axs[1].set(title="Deformation tilts its weights", xlabel=r"$n\ \mathrm{in}\ |n,5-n\rangle$", ylabel="probability")
    axs[0].legend(fontsize=10)
    for ax in axs: ax.grid()
    save(fig, "viii_03_lowest_seed")

    # VIII.04: q-spectrum deformation and its complete overlap.
    fig, axs = two_axes()
    for q in (1., .85, .73):
        axs[0].plot(range(7), pair_spectrum(6, .7, 1.1, q), "o-", label=f"q={q:g}")
    axs[0].set(title="The pair spectrum deforms", xlabel="intermediate label", ylabel=r"$\lambda_j^{12}(q)$")
    axs[0].legend(fontsize=10)
    axs[0].grid()
    data = recouple(6, SHAPES, .73)
    heat(axs[1], data["overlap"], "Seven-channel overlap at q = 0.73")
    check("VIII04 deformed pair spectrum", np.max(abs(data["lv"]-pair_spectrum(6, .7, 1.1, .73))),
          1e-9, total=6, q=.73, shapes=SHAPES)
    check("VIII04 recoupling orthogonality", np.max(abs(data["overlap"].T @ data["overlap"]-np.eye(7))),
          1e-12, total=6, q=.73)
    save(fig, "viii_04_deformed_atlases")

    # VIII.05: exact q-controlled beam splitter and routing endpoint.
    fig, axs = two_axes()
    qs = np.linspace(.03, 1., 120)
    axs[0].plot(qs, qs/(1+qs*qs), label=r"$c_q$")
    axs[0].plot(qs, np.sqrt(1+qs*qs+qs**4)/(1+qs*qs), label=r"$s_q$")
    axs[0].set(title="From routing toward classical mixing", xlabel="q", ylabel="signed-matrix amplitude",
               ylim=(0, 1.03))
    axs[0].legend()
    axs[0].grid()
    heat(axs[1], beam(.5), "Exact amplitude matrix at q = 0.5", annotate=True)
    for q in (.2, .5, .8, 1.):
        check("VIII05 exact q beam", np.max(abs(beam(q)-recouple(1, (.5, .5, .5), q)["overlap"])),
              1e-12, q=q, total=1, shapes=[.5]*3)
    check("VIII05 routing endpoint", np.max(abs(beam(1e-7)-np.array([[0, 1], [1, 0]]))),
          2e-7, q=1e-7, only_closed_two_channel_formula=True)
    save(fig, "viii_05_q_beam")

    # VIII.06: two-channel entropy and absolute mixing gap.
    fig, axs = two_axes()
    qs = np.linspace(.01, 1., 150)
    p = qs*qs/(1+qs*qs)**2
    h = np.array([entropy([v, 1-v]) for v in p])
    axs[0].plot(qs, h, label="row entropy")
    axs[0].axvline(.5, ls=":", color=MUTED)
    axs[0].set(title="Entropy increases in this model", xlabel="q", ylabel="entropy / nats")
    axs[1].plot(qs, 2*p, label="absolute mixing gap")
    axs[1].plot(qs, 1-2*p, "--", label=r"$|\lambda_2|$")
    axs[1].set(title="Distance from a periodic swap", xlabel="q", ylabel="spectral quantity", ylim=(0, 1.03))
    axs[1].legend(fontsize=10)
    for ax in axs: ax.grid()
    witness("VIII06 one-channel-family monotonicity",
            np.min(np.diff(h)) >= -1e-12 and np.min(np.diff(2*p)) >= -1e-12,
            q_grid=[float(qs[0]), float(qs[-1]), len(qs)], equal_half_shapes=True, total=1)
    save(fig, "viii_06_entropy_gap")

    # VIII.07: the finite higher-level entropy counterexample.
    fig, axs = two_axes()
    qs = np.linspace(.65, .9, 120)
    probabilities = np.array([recouple(3, (.5, .5, .5), float(q))["overlap"][1]**2 for q in qs])
    for j in range(4):
        axs[0].plot(qs, probabilities[:, j], label=f"right {j}")
    axs[0].set(title="Four probabilities in row index 1", xlabel="q", ylabel="probability")
    axs[0].legend(fontsize=9, ncol=2)
    values = entropy(probabilities)
    axs[1].plot(qs, values, color=COLORS[0])
    q0, q1 = 307/395, 1557/1975
    row0 = recouple(3, (.5, .5, .5), q0)["overlap"][1]**2
    row1 = recouple(3, (.5, .5, .5), q1)["overlap"][1]**2
    h0, h1 = float(entropy(row0)), float(entropy(row1))
    axs[1].scatter([q0, q1], [h0, h1], color=COLORS[1], s=60, zorder=5)
    axs[1].axvspan(q0, q1, color=COLORS[1], alpha=.15)
    axs[1].text(.655, float(max(values))-.004, f"ΔH = {h1-h0:.6f} nats", fontsize=11,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": .94})
    axs[1].set(title="Entropy is not monotone in q", xlabel="q", ylabel="row entropy / nats")
    for ax in axs: ax.grid()
    witness("VIII07 entropy negative control", h1-h0 < -.007,
            total=3, shapes=[.5]*3, row_index_zero_based=1, q=[q0, q1],
            entropy_nats=[h0, h1], difference_nats=h1-h0,
            row_probabilities=[row0.tolist(), row1.tolist()])
    check("VIII07 independent reported comparison", abs((h1-h0)-(-.0077839865621885427)),
          1e-12, comparison="child pivot/Gram-Schmidt 70-digit report; code not bundled",
          independently_saved_comparison="evidence/independent_cross_series_run/results.json")
    save(fig, "viii_07_nonmonotone")

    # VIII.08: unprojected skew residual and finite deformation speed.
    fig, axs = two_axes()
    R, derivative, raw, A = tangent(6, .35)
    heat(axs[0], A, "Seven-channel tangent (N = 6)")
    axs[0].set(xlabel="packet label", ylabel="packet label")
    theta = np.linspace(.1, .6, 45)
    for N in (3, 6):
        metric = [np.sum(tangent(N, float(t))[3]**2)/2 for t in theta]
        axs[1].plot(theta, metric, label=f"N={N}")
    axs[1].set(title="Squared speed in the θ coordinate", xlabel=r"$\theta=-\log q$", ylabel=r"$\frac{1}{2}\|A\|_F^2$")
    axs[1].legend()
    axs[1].grid()
    check("VIII08 raw tangent skew residual", np.max(abs(raw+raw.T)), 2e-7,
          total=6, theta=.35, central_difference_step=2e-5)
    check("VIII08 tangent equation", np.max(abs(derivative-R@A)), 2e-7,
          total=6, theta=.35)
    save(fig, "viii_08_tangent")

    # VIII.09: two distinct classical limits.
    fig, axs = two_axes()
    eps = np.logspace(-4, -1, 40)
    R1 = recouple(6)["overlap"]
    v1 = lowest_seed(5, .7, 1.1, 1.)
    matrix_errors, seed_errors = [], []
    for e in eps:
        Rq = align(R1, recouple(6, SHAPES, float(1-e))["overlap"])
        matrix_errors.append(np.max(abs(Rq-R1)))
        seed_errors.append(np.max(abs(lowest_seed(5, .7, 1.1, float(1-e))-v1)))
    axs[0].loglog(eps, matrix_errors, label="complete overlap")
    axs[0].loglog(eps, seed_errors, label="two-body seed")
    axs[0].set(title="Both converge; rates differ", xlabel="1 − q", ylabel="maximum entry error")
    axs[0].legend(fontsize=10)
    axs[0].grid()
    delta = align(R1, recouple(6, SHAPES, .99)["overlap"])-R1
    heat(axs[1], delta, "Signed overlap correction at q = 0.99")
    check("VIII09 matrix near-classical agreement", matrix_errors[0], 2e-5,
          total=6, q=1-float(eps[0]), shapes=SHAPES)
    witness("VIII09 finite limit trends", matrix_errors[0] < matrix_errors[-1]
            and seed_errors[0] < seed_errors[-1],
            q_range=[.9, .9999], matrix_endpoint_errors=[matrix_errors[0], matrix_errors[-1]],
            seed_endpoint_errors=[seed_errors[0], seed_errors[-1]])
    save(fig, "viii_09_classical_limit")

    # VIII.10: q-tree closure with independent operator diagnostics.
    fig, axs = two_axes()
    draw_pentagon(axs[0], "The same tree graph at q = 0.78")
    qs = [.65, .75, .85, 1.]
    metrics = {"loop": [], "lowering kernel": [], "joint diagonalization": []}
    for q in qs:
        trees = tree_bases(3, q)
        product, _ = loop_product(trees)
        Q = frame(3, FOUR_SHAPES, q)
        metrics["loop"].append(np.max(abs(product-np.eye(10))))
        metrics["lowering kernel"].append(np.max(abs(lowering(3, FOUR_SHAPES, q) @ Q)))
        metrics["joint diagonalization"].append(max(t["diagonalization"] for t in trees))
        check("VIII10 q-tree joint operators", max(t["commutator"] for t in trees), 1e-8,
              total=3, q=q, shapes=FOUR_SHAPES)
    for label, values in metrics.items():
        axs[1].semilogy(qs, np.maximum(values, 1e-16), "o-", label=label)
        check("VIII10 "+label, max(values), 1e-9, total=3, q_grid=qs, dimension=10)
    axs[1].set(title="Three distinct numerical checks", xlabel="q", ylabel="maximum absolute residual")
    axs[1].legend(fontsize=9, loc="upper right")
    axs[1].grid()
    save(fig, "viii_10_q_trees")

    # VIII.11: scalar duality and a collapsed finite lattice.
    fig, axs = two_axes()
    q, N = .73, 6
    a, b, c, d = q**.6, q**.8, q**(-7), q**.4
    table = np.array([[qr(n, y, a, b, c, d, q).real for y in range(7)] for n in range(7)])
    dual = np.array([[qr(y, n, c, d, a, b, q).real for y in range(7)] for n in range(7)])
    heat(axs[0], table, "A separate scalar q-Racah table")
    axs[0].set(xlabel="scalar coordinate y", ylabel="scalar degree n")
    residual = float(np.max(abs(table-dual)))
    axs[0].text(.02, .03, f"duality error {residual:.1e}", transform=axs[0].transAxes,
                fontsize=10, bbox={"facecolor": "white", "alpha": .85, "edgecolor": "none"})
    axs[1].plot([0, 1], [1, 1], "-", color=COLORS[0], label=r"$R_0$ evaluated")
    axs[1].scatter([0, 1], [1, 1], s=150, facecolors="none", edgecolors=COLORS[1], linewidth=2,
                   label=r"$R_1$ evaluated")
    axs[1].text(.5, 1.13, r"$\mu(0)=\mu(1)=3$", ha="center")
    axs[1].set(title="Termination can leave a collapsed lattice", xlabel="finite coordinate y", ylabel="polynomial value",
               xticks=[0, 1], ylim=(.65, 1.3))
    axs[1].legend(fontsize=10, loc="lower center")
    check("VIII11 scalar duality", residual, 1e-10, q=q, N=N,
          exponent_parameters=[.6, .8, -7, .4], no_shape_parameter_map=True)
    fq = Fraction(1, 2)
    mus = [fq**(-y)+4*fq**(y+1) for y in (0, 1)]
    r1 = [Fraction(6)-Fraction(5, 3)*mu for mu in mus]
    witness("VIII11 exact scalar collapsed lattice",
            mus == [Fraction(3)]*2 and r1 == [Fraction(1)]*2,
            arithmetic="fractions.Fraction", q="1/2", N=1,
            alpha="1/2", beta="1/2", gamma="4", delta="1",
            lattice=list(map(str, mus)), R0=["1", "1"], R1=list(map(str, r1)),
            inference="positive inner product equals w0+w1 > 0")
    save(fig, "viii_11_scalar_bridge")

    # VIII.12: scalar Askey-Wilson identity on nonsingular points.
    fig, axs = two_axes()
    q = .7
    pars = (.2, .3, -.25, .4)
    theta = np.linspace(.3, 2.7, 100)
    for n in (0, 1, 2):
        values = np.array([aw(n, np.exp(1j*t), *pars, q) for t in theta])
        axs[0].plot(theta, values.real, label=f"n={n}")
        check("VIII12 real unit-circle values", np.max(abs(values.imag)), 1e-10,
              degree=n, q=q, parameters=pars, theta_range=[.3, 2.7])
    axs[0].set(title="Normalized scalar polynomials", xlabel=r"$\theta$ in $z=e^{i\theta}$", ylabel=r"$\mathcal{A}_n(z)$")
    axs[0].legend()
    axs[0].grid()
    points = np.linspace(.3, 2.7, 13)
    errors = np.zeros((6, len(points)))
    for n in range(6):
        function = lambda z, n=n: aw(n, z, *pars, q)
        eigenvalue = q**(-n)+np.prod(pars)*q**(n-1)
        for j, t in enumerate(points):
            z = np.exp(1j*t)
            errors[n, j] = abs(aw_operator(function, z, *pars, q)-eigenvalue*function(z))
    image = axs[1].imshow(np.log10(np.maximum(errors, 1e-16)), aspect="auto",
                          extent=(.3, 2.7, 5.5, -.5), cmap="viridis", vmin=-16, vmax=-10)
    axs[1].set(title="Direct q-difference residual", xlabel=r"$\theta$", ylabel="degree n", yticks=range(6))
    fig.colorbar(image, ax=axs[1], fraction=.048, pad=.025, label=r"$\log_{10}$ error")
    check("VIII12 Askey-Wilson identity", np.max(errors), 1e-9, q=q, parameters=pars,
          degrees=list(range(6)), theta_points=points.tolist(),
          no_continuous_series_packet_transform_claim=True)
    save(fig, "viii_12_askey_wilson")


def main():
    started = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()
    apply_style()
    classical_lessons()
    deformed_lessons()
    assert len(STEMS) == 24 and len(set(STEMS)) == 24
    EVIDENCE.mkdir(exist_ok=True, parents=True)
    outputs = []
    for stem in STEMS:
        for suffix in (".pdf", ".png"):
            path = FIGURES/(stem+suffix)
            outputs.append({"path": str(path.relative_to(ROOT)),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    for filename in ("figures_vii_viii.py", "chapters_vii_viii.tex", "guide_style.py"):
        path = ROOT/filename
        if path.exists():
            outputs.append({"path": filename, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {
        "schema_version": 1,
        "claim_id": "SpecialFunctionsVisualV02.PapersVII_VIII.FiniteFigureChecks",
        "repository": {"commit": "not a Git checkout; archived-source SHA256 in generator header", "dirty": True},
        "command": "OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python figures_vii_viii.py",
        "environment": {"software": [f"Python {platform.python_version()}",
                         f"NumPy {np.__version__}", f"SciPy {scipy.__version__}",
                         f"Matplotlib {matplotlib.__version__}"],
                        "hardware": f"{platform.machine()} / {platform.system()}"},
        "mathematics": {
            "assertion_tested": "Finite matrix, seed, overlap, gauge, entropy, tree, compiler, scalar duality and q-difference assertions for the 24 newly generated lessons.",
            "coefficient_domain": "IEEE float64/complex128 except exact fractions.Fraction scalar collapse witness.",
            "conventions": "Ordered occupation compositions; symmetric q-numbers; first overlap row/column positive; row probability vectors; entropy in nats; row index 1 is zero-based.",
            "inputs": ["Positive shape triples (0.7,1.1,0.9) and (0.5,0.5,0.5)",
                       "Four shapes (0.55,0.8,1.05,1.3)", "Two shapes (0.7,1.1)",
                       "Scalar q-Racah exponents (0.6,0.8,-7,0.4)",
                       "Askey-Wilson parameters (0.2,0.3,-0.25,0.4)"],
            "bounds": {"matrix_total_excitation_max": 8, "tensor_factors_max": 4,
                       "four_factor_excitation_max": 4, "scalar_degree_max": 6,
                       "q_matrix_range": [0.2, 1.0],
                       "closed_beam_routing_q": 1e-7,
                       "finite_difference_step": 2e-5, "thread_caps": ["OPENBLAS_NUM_THREADS=1", "OMP_NUM_THREADS=1"]},
            "non_claims": ["No universal floating-point accuracy guarantee",
                          "No newly proved classical representation-theory identification",
                          "No full shape-to-scalar parameter/weight/phase comparison",
                          "No positive scalar orthogonality inferred from termination",
                          "No pentagon-only validation of projectors or labels",
                          "No universal monotonicity of entropy in q",
                          "No continuous-series Askey-Wilson packet transform"]},
        "randomness": {"used": True, "generator": "NumPy default_rng / PCG64", "seed": 73011},
        "run": {"started_at": started, "runtime_seconds": time.perf_counter()-start, "exit_status": 0},
        "outputs": outputs, "checks": CHECKS,
        "result": "implementation and finite assertion verified in the stated range",
        "residual_risks": ["Finite floating-point tolerances are not interval error bounds",
                           "External classical scalar/representation identifications retain their source status",
                           "The 70-digit child comparison is reported; the separately saved root verification witness uses its own documented points"] }
    (EVIDENCE/"vii_viii_audit.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({"figures": len(STEMS), "checks": len(CHECKS),
                      "all_passed": all(c["passed"] for c in CHECKS),
                      "runtime_seconds": manifest["run"]["runtime_seconds"]}))


if __name__ == "__main__":
    main()
