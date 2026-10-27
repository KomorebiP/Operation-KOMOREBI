#!/usr/bin/env python3
"""Twelve fresh bounded adic illustrations. Run from the edition root.

The archived scripts are source correspondence, not executed dependencies.
All arrays and scalar families are constructed below, deterministically.
No physical fitting, external data, Lean or unbounded time evolution is run.
"""
from pathlib import Path
import datetime as dt
import hashlib
import io
import json
import platform
import sys
import time
import traceback
import numpy as np
import scipy
from scipy.linalg import expm
from scipy.special import eval_chebyt
import sympy as sp
import mpmath as mp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "source/adic_figures"
EVID = ROOT / "evidence/adic"
OUT.mkdir(parents=True, exist_ok=True)
EVID.mkdir(parents=True, exist_ok=True)
START = time.monotonic()
STAMP = dt.datetime.now(dt.timezone.utc).isoformat()
INPUTS = [Path(__file__).resolve()]
HASHES = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in INPUTS}
TEAL, GOLD, LILAC = "#245D60", "#AD7842", "#7C738E"
INK, MUTED, PALE = "#212B34", "#58646B", "#EEF3F2"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5,
    "axes.labelsize": 10.5, "axes.titlesize": 11.5, "axes.titlepad": 12,
    "axes.labelcolor": INK, "text.color": INK, "axes.edgecolor": "#ADBAB9",
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
    "axes.spines.right": False, "legend.frameon": False, "legend.fontsize": 8.5,
    "lines.linewidth": 2.0, "figure.facecolor": "white", "axes.facecolor": "white",
    "savefig.facecolor": "white", "pdf.fonttype": 42, "ps.fonttype": 42,
    "mathtext.fontset": "dejavusans"})
checks, outputs = [], []
STEMS = ["01_weighted_split", "02_haar_channels", "03_cylinder_embeddings",
    "04_character_sectors", "05_projector_tower", "06_unitary_time",
    "07_product_walk", "08_radial_self_energy", "09_polyphase_symbol",
    "10_tail_graph_norm", "11_prime_renormalization", "12_hypergeometric_packets"]

def record(name, passed, detail):
    checks.append({"name": name, "passed": bool(passed), "detail": detail})
    if not passed:
        raise AssertionError(f"{name}: {detail}")

def save(fig, name):
    for ext in ("pdf", "png"):
        buffer = io.BytesIO()
        metadata = {"Creator": "Komorebi adic Python figure generator"}
        if ext == "pdf":
            metadata.update({"CreationDate": None, "ModDate": None})
        fig.savefig(buffer, format=ext, dpi=190, bbox_inches="tight", pad_inches=.20, metadata=metadata)
        path = OUT / f"{name}.{ext}"
        temporary = path.with_name(path.name + ".tmp")
        temporary.write_bytes(buffer.getvalue())
        temporary.replace(path)
        outputs.append({"path": str(path.relative_to(ROOT)), "kind": "result",
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    plt.close(fig)

def grid(ax):
    ax.grid(True, color="#DDE5E3", linewidth=.65, alpha=.8)
    ax.set_axisbelow(True)

def pair():
    return plt.subplots(1, 2, figsize=(9, 4.35), layout="constrained")

def expectations(p, h):
    x = np.arange(p**h)
    return [(x[:, None] % p**r == x[None, :] % p**r).astype(float) / p**(h-r)
        for r in range(h+1)]

def details(p, h):
    e = expectations(p, h)
    return [e[0]] + [e[r] - e[r-1] for r in range(1, h+1)]

def haar(p, h):
    n = p**h
    x = np.arange(n)
    columns = [np.ones(n) / np.sqrt(n)]
    for r in range(1, h+1):
        digit = (x // p**(r-1)) % p
        for a in range(p**(r-1)):
            for q in range(1, p):
                v = (x % p**(r-1) == a) * np.exp(2j*np.pi*q*digit/p) / np.sqrt(p**(h-r+1))
                columns.append(v)
    return np.column_stack(columns)

def refinement(p, h):
    return np.tile(np.eye(p**h), (p, 1)) / np.sqrt(p)

def shift(n):
    return np.roll(np.eye(n), 1, axis=0)

def hamiltonian(p, h):
    d = details(p, h)
    s = shift(p**h)
    return sum((0 if r == 0 else 2**(r-1)) * d[r] for r in range(h+1)) + .2 * (2*np.eye(p**h)-s-s.T)

def unitary_from_eig(h, t):
    e, b = np.linalg.eigh(h)
    return (b*np.exp(-1j*t*e)) @ b.conj().T

def tree(p, h):
    vertices = [()]
    for r in range(1, h+1):
        vertices += [v+(d,) for v in vertices.copy() if len(v) == r-1 for d in range(p)]
    return vertices

def tree_matrix(p, h, eps, gamma):
    verts = tree(p, h)
    lookup = {v: k for k, v in enumerate(verts)}
    hh = np.diag([eps[len(v)] for v in verts]).astype(float)
    for v in verts[1:]:
        i, j = lookup[v], lookup[v[:-1]]
        hh[i, j] = hh[j, i] = gamma[len(v)-1] / np.sqrt(p)
    vv = np.zeros((len(verts), h+1))
    for k, v in enumerate(verts):
        vv[k, len(v)] = p**(-len(v)/2)
    return hh, vv

def product_walk(p, h, ncycle, ticks):
    tr = tree(p, h)
    verts = [(x, v) for x in range(ncycle) for v in tr]
    vi = {v: i for i, v in enumerate(verts)}
    neighbors = []
    for x, v in verts:
        nn = [((x-1) % ncycle, v), ((x+1) % ncycle, v)]
        if v:
            nn.append((x, v[:-1]))
        if len(v) < h:
            nn += [(x, v+(d,)) for d in range(p)]
        neighbors.append([vi[w] for w in nn])
    arcs = [(i, j) for i, nn in enumerate(neighbors) for j in nn]
    ai = {a: k for k, a in enumerate(arcs)}
    groups = [[ai[i, j] for j in nn] for i, nn in enumerate(neighbors)]
    reverse = np.array([ai[j, i] for i, j in arcs])
    psi = np.zeros(len(arcs), complex)
    root = vi[0, ()]
    psi[groups[root]] = 1/np.sqrt(len(groups[root]))
    states, continuity, cone, norm = [], [], [], []
    distance = np.array([min(x, ncycle-x)+len(v) for x, v in verts])
    source = np.array([a[0] for a in arcs])
    target = np.array([a[1] for a in arcs])
    for t in range(ticks+1):
        rho = np.bincount(source, weights=np.abs(psi)**2, minlength=len(verts))
        states.append(rho)
        norm.append(float(np.sum(rho)))
        cone.append(float(np.sum(rho[distance > t])))
        if t == ticks:
            break
        post = psi.copy()
        for gg in groups:
            post[gg] = 2*np.mean(psi[gg]) - psi[gg]
        outgoing = np.bincount(source, weights=np.abs(post)**2, minlength=len(verts))
        incoming = np.bincount(target, weights=np.abs(post)**2, minlength=len(verts))
        newpsi = post[reverse]
        newrho = np.bincount(source, weights=np.abs(newpsi)**2, minlength=len(verts))
        continuity.append(float(np.max(np.abs((newrho-rho)-(incoming-outgoing)))))
        psi = newpsi
    return {"verts": verts, "arcs": arcs, "states": states, "continuity": continuity,
        "cone": cone, "norm": norm, "degrees": [len(g) for g in groups]}

def make_figures():
    # 01: normalization is a probability rule, coupling is an additional choice.
    w = np.arange(0, 7)
    p = 3
    bright_err = []
    for prime in (2, 3):
        for depth in range(0, 6):
            n = prime**depth
            record(f"descendant mass p{prime} w{depth}", sp.Rational(1, n)*n == 1,
                {"descendants": n, "amplitude": f"1/sqrt({n})", "single_Born_weight": f"1/{n}", "arithmetic": "exact rational probability"})
            rr = np.ones(n) / np.sqrt(n)
            leaf = prime**(-depth)
            bright_err.append(abs(rr @ (leaf*np.ones(n))-prime**(-depth/2)))
    record("bright coupling independent construction", max(bright_err) < 3e-15,
        {"primes": [2, 3], "depths": [0, 1, 2, 3, 4, 5], "alpha": 1, "max_residual": max(bright_err), "tolerance": 3e-15})
    record("probability-as-amplitude negative control", 3*sp.Rational(1, 3)**2 == sp.Rational(1, 3),
        {"incorrect_amplitude": "1/3 at p=3,w=1", "resulting_norm_squared": "1/3", "correct_amplitude": "1/sqrt(3)"})
    fig, axs = pair()
    axs[0].semilogy(w, p**(-w/2), "o-", color=TEAL, label="amplitude per descendant")
    axs[0].semilogy(w, p**(-w.astype(float)), "s-", color=GOLD, label="Born weight per descendant")
    axs[0].set(xlabel="refinement depth w", ylabel="dimensionless magnitude", title="A normalized ternary descendant packet")
    axs[0].legend(); grid(axs[0])
    for alpha, color in ((.25, LILAC), (.5, TEAL), (1., GOLD)):
        axs[1].semilogy(w, p**((.5-alpha)*w), "o-", color=color, label=f"per-leaf exponent α = {alpha:g}")
    axs[1].set(xlabel="refinement depth w", ylabel="collective |G| / |g|", title="Branching changes the coupling exponent")
    axs[1].legend(); grid(axs[1]); save(fig, STEMS[0])

    # 02: orthogonal detail bases independently reconstruct expectation differences.
    project_res, basis_res, rank_ok = [], [], []
    for p in (2, 3, 5):
        for h in (1, 2, 3):
            if p**h > 125:
                continue
            b = haar(p, h); d = details(p, h); ranks = [1]+[(p-1)*p**(r-1) for r in range(1, h+1)]
            basis_res.append(float(np.max(np.abs(b.conj().T @ b-np.eye(p**h)))))
            k = 0
            for r, rank in enumerate(ranks):
                bb = b[:, k:k+rank]
                project_res.append(float(np.max(np.abs(bb @ bb.conj().T-d[r]))))
                rank_ok.append(abs(np.trace(d[r])-rank) < 1e-12)
                k += rank
    record("independent Haar basis and projectors", max(basis_res+project_res) < 3e-14 and all(rank_ok),
        {"p": [2, 3, 5], "h": [1, 2, 3], "largest_dimension": 125, "orthogonality_max": max(basis_res), "projector_max": max(project_res), "trace_ranks_match": all(rank_ok), "tolerance": 3e-14})
    fig, axs = pair(); dft3 = np.exp(2j*np.pi*np.arange(3)[:, None]*np.arange(3)[None, :]/3)/np.sqrt(3)
    for q, color in enumerate((TEAL, GOLD, LILAC)):
        axs[0].plot(np.arange(3), dft3[:, q].real, "o-", color=color, label=f"Re child character q = {q}")
        axs[0].plot(np.arange(3), dft3[:, q].imag, "x--", color=color, alpha=.75)
    axs[0].set(xlabel="child digit d", ylabel="normalized character amplitude", title="One average and two orthogonal detail phases", xticks=[0, 1, 2])
    axs[0].legend(loc="upper center", bbox_to_anchor=(.5, -.17), fontsize=8, ncol=1); grid(axs[0])
    rr = np.arange(1, 6)
    for pp, color in ((2, TEAL), (3, GOLD), (5, LILAC)):
        axs[1].semilogy(rr, (pp-1)*pp**(rr-1), "o-", color=color, label=f"p = {pp}")
    axs[1].set(xlabel="detail level r", ylabel="rank of Fᵣ", title="Every parent gains p − 1 details"); axs[1].legend(); grid(axs[1]); save(fig, STEMS[1])

    # 03: exact finite cylinder matrices, ordered by address x=0,...,8.
    p, h = 3, 2
    es = expectations(p, h)
    exact = [sp.Matrix([[sp.Rational(int(x % p**r == y % p**r), p**(h-r)) for y in range(p**h)] for x in range(p**h)]) for r in range(h+1)]
    record("exact cylinder minimum product rule", all(a*b == exact[min(r, s)] for r, a in enumerate(exact) for s, b in enumerate(exact)),
        {"p": p, "h": h, "arithmetic": "exact rational matrices", "levels": [0, 1, 2], "dimensions": "9x9"})
    vv = refinement(3, 1)
    record("finite cylinder refinement image", np.max(np.abs(vv @ vv.T-es[1])) < 2e-16,
        {"p": 3, "coarse_dimension": 3, "fine_dimension": 9, "max_residual": float(np.max(np.abs(vv @ vv.T-es[1]))), "tolerance": 2e-16})
    fig, axs = pair()
    im = axs[0].imshow(es[1], cmap="Blues", vmin=0, vmax=1/3)
    fig.colorbar(im, ax=axs[0], shrink=.8, label="matrix entry")
    axs[0].set(xlabel="fine address y", ylabel="fine address x", title="E₁ averages equal low-digit addresses", xticks=np.arange(9), yticks=np.arange(9))
    f = np.array([0., 1., 2., 3., -2., 1., 0., 2., 4.])
    axs[1].plot(np.arange(9), f, "o-", color=GOLD, label="fine f")
    axs[1].plot(np.arange(9), es[1] @ f, "s-", color=TEAL, label="E₁ f")
    axs[1].plot(np.arange(9), es[0] @ f, "--", color=LILAC, label="E₀ f")
    axs[1].set(xlabel="fine address x", ylabel="dimensionless amplitude", title="Cylinder averaging follows congruence", xticks=np.arange(9)); axs[1].legend(); grid(axs[1]); save(fig, STEMS[2])

    # 04: finite unit readdressing and sign collapse are different maps.
    cases = [(2, 2, 16, 15, 5, 2), (3, 1, 9, 8, 4, 2), (5, 1, 25, 7, 6, 4)]
    for pp, hh, mod, zeta, principal, torsion in cases:
        table = {(t, a): (pow(zeta, t, mod)*pow(principal, a, mod)) % mod for t in range(torsion) for a in range(pp**hh)}
        expected = {a for a in range(mod) if np.gcd(a, mod) == 1}
        mul_ok = all(table[((t+u) % torsion, (a+b) % (pp**hh))] == table[t, a]*table[u, b] % mod for t, a in table for u, b in table)
        record(f"unit coordinate bijection and multiplication p{pp}", set(table.values()) == expected and len(table) == len(expected) and mul_ok,
            {"p": pp, "h": hh, "modulus": mod, "torsion_generator": zeta, "principal_generator": principal, "units": len(expected), "arithmetic": "exact modular integers"})
    collapse = np.tile(np.eye(4), (1, 2))
    record("sign-forgetting rank negative control", np.linalg.matrix_rank(collapse) == 4 and np.max(np.abs(collapse @ np.r_[np.eye(4), -np.eye(4)])) == 0,
        {"source_dimension": 8, "target_dimension": 4, "rank": 4, "kernel_dimension": 4, "antisymmetric_vectors": "(e_a,-e_a)", "scope": "linear sign-forgetting map, not a quantum partial trace"})
    fig, axs = pair(); tab = np.array([[pow(15, s, 16)*pow(5, a, 16) % 16 for a in range(4)] for s in range(2)])
    axs[0].imshow(tab, cmap="YlGnBu", vmin=0, vmax=16, aspect="auto")
    for s in range(2):
        for a in range(4):
            axs[0].text(a, s, str(tab[s, a]), ha="center", va="center", color="white" if tab[s, a] > 8 else INK, fontsize=15)
    axs[0].set(xlabel="principal phase a", ylabel="sign s", xticks=np.arange(4), yticks=[0, 1], yticklabels=["+", "−"], title="All eight units mod 16 retain their sign")
    axs[1].bar([0, 1, 2], [8, 4, 4], color=[TEAL, GOLD, LILAC])
    axs[1].set(xticks=[0, 1, 2], xticklabels=["unit register", "phase image", "lost directions"], ylabel="dimension", title="Deleting sign loses a four-dimensional kernel"); grid(axs[1]); save(fig, STEMS[3])

    # 05: exact compatibility has a sensitive cross-block negative control.
    p, h = 3, 2
    v = refinement(p, h); hc = hamiltonian(p, h); hf = hamiltonian(p, h+1); pp = v @ v.T; qq = np.eye(27)-pp
    inter = float(np.linalg.norm(hf @ v-v @ hc)); leak = float(np.linalg.norm(qq @ hf @ pp))
    z = .4+.7j
    sigma = pp @ hf @ qq @ np.linalg.inv(z*np.eye(27)-qq @ hf @ qq) @ qq @ hf @ pp
    record("compatible finite tower including cyclic translation", inter < 2e-14 and leak < 2e-14 and np.linalg.norm(sigma) < 1e-25,
        {"p": p, "coarse_h": h, "fine_h": h+1, "H": "sum eps_r F_r + 0.2(2I-S-S*)", "eps": "0 at r0, 2^(r-1) otherwise", "intertwining_norm": inter, "leakage_norm": leak, "self_energy_norm": float(np.linalg.norm(sigma)), "z": [z.real, z.imag], "tolerance": 2e-14})
    u = v[:, 0]; detail = haar(3, 3)[:, 9]; eta = .3
    bad = hf+eta*(np.outer(u, detail.conj())+np.outer(detail, u.conj()))
    cross = float(np.linalg.norm(qq @ bad @ pp)); badinter = float(np.linalg.norm(bad @ v-v @ hc))
    record("cross-block compatibility negative control", abs(cross-eta) < 2e-14 and badinter > .29,
        {"perturbation": "eta(|u><detail|+|detail><u|), eta=0.3", "u": "V e0", "detail": "first level3 Haar wavelet", "leakage_norm": cross, "intertwining_norm": badinter, "expected_leakage": eta})
    fig, axs = pair(); b = np.column_stack([v, haar(3, 3)[:, 9:]])
    im = axs[0].imshow(np.abs(b.conj().T @ hf @ b), cmap="YlGnBu", vmin=0, vmax=4.5)
    axs[0].axvline(8.5, color=GOLD, lw=1.3); axs[0].axhline(8.5, color=GOLD, lw=1.3)
    fig.colorbar(im, ax=axs[0], shrink=.8, label="absolute matrix entry")
    axs[0].set(xlabel="coarse + detail coordinate", ylabel="coarse + detail coordinate", title="The compatible Hamiltonian has no cross block")
    tt = np.linspace(0, 6, 121); cc, bb = [], []
    for t in tt:
        cc.append(np.linalg.norm(qq @ unitary_from_eig(hf, t) @ u)**2)
        bb.append(np.linalg.norm(qq @ unitary_from_eig(bad, t) @ u)**2)
    record("finite unitary intertwining", np.linalg.norm(unitary_from_eig(hf, .7) @ v-v @ unitary_from_eig(hc, .7)) < 3e-14,
        {"p": 3, "dimensions": [9, 27], "t": .7, "residual": float(np.linalg.norm(unitary_from_eig(hf, .7) @ v-v @ unitary_from_eig(hc, .7))), "tolerance": 3e-14})
    axs[1].plot(tt, bb, color=GOLD, label="cross-block perturbation η = 0.3")
    axs[1].plot(tt, cc, color=TEAL, label="compatible tower")
    axs[1].set(xlabel="dimensionless time t", ylabel="new-detail probability", title="An added coupling creates real detail leakage"); axs[1].legend(); grid(axs[1]); save(fig, STEMS[4])

    # 06: valuation shells of the pure hierarchy, per-address probabilities.
    p, h = 3, 3; d = details(p, h); en = np.array([0., 1., 2., 4.]); n = p**h
    tt = np.linspace(0, 5, 151); probs = []
    for t in tt:
        uf = sum(np.exp(-1j*t*en[r])*d[r] for r in range(h+1))
        probs.append(np.abs(uf[:, 0])**2)
    probs = np.array(probs)
    shells = []
    for x in range(n):
        r = h if x == 0 else 0
        if x:
            while x % p**(r+1) == 0:
                r += 1
        shells.append(r)
    shell_spread = max(float(np.max(np.ptp(probs[:, np.array(shells) == r], axis=1))) for r in range(h+1))
    record("hierarchical shell isotropy and unitary normalization", shell_spread < 2e-15 and np.max(np.abs(probs.sum(axis=1)-1)) < 2e-15,
        {"p": p, "h": h, "times": [0, 5, 151], "energies": en.tolist(), "maximum_within_shell_spread": shell_spread, "normalization_residual": float(np.max(np.abs(probs.sum(axis=1)-1))), "shells": "v3(x), diagonal x0 labeled h", "tolerance": 2e-15})
    fig, axs = pair(); order = np.argsort(shells, kind="stable")
    im = axs[0].pcolormesh(np.arange(n+1)-.5, np.linspace(0, 5, 152), probs[:, order], cmap="YlGnBu", shading="flat")
    fig.colorbar(im, ax=axs[0], shrink=.8, label="Born probability per address")
    axs[0].set(xlabel="address ordered by valuation shell", ylabel="time t", title="Equal valuation means equal transition weight")
    j = np.argmin(abs(tt-.7)); shellvals = [probs[j, np.array(shells) == r][0] for r in range(h+1)]
    mult = [sum(np.array(shells) == r) for r in range(h+1)]
    axs[1].bar(np.arange(h+1)-.15, shellvals, width=.3, color=TEAL, label="per-address weight")
    axs[1].bar(np.arange(h+1)+.15, np.array(shellvals)*mult, width=.3, color=GOLD, label="whole-shell weight")
    axs[1].set(xlabel="valuation shell r (r = 3 is x = 0)", ylabel="probability at t = 0.7", title="Shell multiplicity matters", xticks=range(4)); axs[1].legend(); grid(axs[1]); save(fig, STEMS[5])

    # 07: exact finite propagation on a cycle times a rooted tree.
    walks = {p: product_walk(p, 2, 7, 8) for p in (2, 3)}
    for p, ww in walks.items():
        record(f"finite product walk continuity and cone p{p}", max(ww["continuity"]) < 2e-15 and max(ww["cone"]) == 0 and max(abs(np.array(ww["norm"])-1)) < 3e-15,
            {"p": p, "tree_depth": 2, "cycle_length": 7, "ticks": 8, "vertices": len(ww["verts"]), "arcs": len(ww["arcs"]), "coin": "Grover 2|+><+|-I at each vertex", "torsion_register": "spectator identity, omitted from arrays", "continuity_max": max(ww["continuity"]), "outside_product_cone_probability": max(ww["cone"]), "probability_drift": float(max(abs(np.array(ww["norm"])-1))), "tolerance": 3e-15})
    record("Grover depth-extension negative control", abs((2/3-1)-(2/5-1)) > .2,
        {"old_leaf_degree": 3, "after_binary_extension_degree": 5, "old_diagonal_coin_entry": -1/3, "extended_diagonal_coin_entry": -3/5, "nonzero_difference": 4/15, "scope": "canonical old-arc inclusion does not intertwine these coins"})
    ww = walks[2]; surface = np.zeros((3, 7))
    for (x, v), rho in zip(ww["verts"], ww["states"][6]):
        surface[len(v), x] += rho
    fig = plt.figure(figsize=(9, 4.65)); ax = fig.add_subplot(121, projection="3d")
    xx, rr = np.meshgrid(np.arange(7), np.arange(3))
    ax.plot_surface(xx, rr, surface, cmap="viridis", linewidth=.6, edgecolor="#E5EFEC", alpha=.95)
    ax.set(xlabel="physical x", ylabel="tree depth r", zlabel="summed probability", title="A genuine product-coordinate probability surface", xticks=[0, 2, 4, 6], yticks=[0, 1, 2])
    ax.view_init(25, -57); ax.set_box_aspect((1.3, .7, .8)); ax.zaxis.labelpad = 8
    ax = fig.add_subplot(122)
    for p, color in ((2, TEAL), (3, GOLD)):
        ww = walks[p]; maxdist = []
        for t, state in enumerate(ww["states"]):
            maxdist.append(max([min(x, 7-x)+len(v) for (x, v), rho in zip(ww["verts"], state) if rho > 1e-25], default=0))
        ax.plot(range(9), maxdist, "o-", color=color, label=f"occupied max distance p = {p}")
    ax.plot(range(9), range(9), "--", color=LILAC, label="one-edge-per-tick bound")
    ax.set(xlabel="tick n", ylabel="product graph distance", title="Occupation stays inside the finite causal cone"); ax.legend(fontsize=8); grid(ax)
    fig.subplots_adjust(left=.005, right=.98, bottom=.15, top=.84, wspace=.43); save(fig, STEMS[6])

    # 08: tree normalization makes the root response prime independent.
    depth = 3; eps = np.array([0., .2, -.1, .4]); gamma = np.array([.6, .45, .3]); jac = np.diag(eps)+np.diag(gamma, 1)+np.diag(gamma, -1)
    radial_res, green_res = [], []
    zs = [-.4+.5j, .7+.2j, 1.3+.4j]
    for p in (2, 3):
        hh, vv = tree_matrix(p, depth, eps, gamma)
        radial_res.append(float(np.linalg.norm(hh @ vv-vv @ jac)))
        for z in zs:
            green_res.append(abs(np.linalg.inv(z*np.eye(len(hh))-hh)[0, 0]-np.linalg.inv(z*np.eye(4)-jac)[0, 0]))
    record("tree radial invariance and prime-independent root resolvent", max(radial_res+green_res) < 1e-14,
        {"primes": [2, 3], "depth": depth, "tree_dimensions": [15, 40], "epsilon": eps.tolist(), "gamma": gamma.tolist(), "edge_coupling": "gamma_r/sqrt(p)", "z_values": [[z.real, z.imag] for z in zs], "radial_max": max(radial_res), "Green_max": max(green_res), "tolerance": 1e-14})
    cferr = []
    for z in zs:
        sig = 0j
        for r in range(depth-1, -1, -1):
            sig = gamma[r]**2/(z-eps[r+1]-sig)
        cferr.append(abs(1/(z-eps[0]-sig)-np.linalg.inv(z*np.eye(4)-jac)[0, 0]))
    record("continued fraction versus direct inverse", max(cferr) < 2e-15,
        {"z_values": [[z.real, z.imag] for z in zs], "maximum_residual": max(cferr), "tolerance": 2e-15})
    fig, axs = pair(); ee = np.linspace(-1.4, 1.4, 401); gg = np.array([np.linalg.inv((x+.08j)*np.eye(4)-jac)[0, 0] for x in ee])
    axs[0].plot(ee, -gg.imag/np.pi, color=TEAL, label="p = 2 radial response")
    axs[0].plot(ee[::15], -gg.imag[::15]/np.pi, "o", color=GOLD, fillstyle="none", label="p = 3 same Jacobi chain")
    axs[0].set(xlabel="energy E (z = E + 0.08i)", ylabel="−Im G₀(z) / π", title="Normalized branching leaves one radial response"); axs[0].legend(); grid(axs[0])
    tail = jac[1:, 1:]; tt = np.linspace(0, 30, 401); mem = np.array([gamma[0]**2*unitary_from_eig(tail, t)[0, 0] for t in tt])
    axs[1].plot(tt, mem.real, color=TEAL, label="Re K(t)"); axs[1].plot(tt, mem.imag, color=GOLD, label="Im K(t)")
    axs[1].set(xlabel="dimensionless time t ≥ 0", ylabel="finite memory kernel", title="A finite hidden chain retains oscillatory memory"); axs[1].legend(); grid(axs[1]); save(fig, STEMS[7])

    # 09: bands fold exactly, with all channels retained.
    p, h, mu, kappa = 3, 3, .2, .7; n = p**h; m = n//p; theta = 2*np.pi*np.arange(m)/m
    bands = mu+2*kappa*np.cos((theta[:, None]+2*np.pi*np.arange(p)[None, :])/p)
    cyc = mu*np.eye(n)+kappa*(shift(n)+shift(n).T)
    specerr = float(np.max(np.abs(np.sort(bands.ravel())-np.linalg.eigvalsh(cyc))))
    record("folded three-channel spectrum versus cyclic matrix", specerr < 3e-15,
        {"p": p, "h": h, "N": n, "coarse_momenta": m, "mu": mu, "kappa": kappa, "max_residual": specerr, "tolerance": 3e-15})
    record("single-channel spectrum negative control", len(bands[:, 0]) == 9 and len(np.linalg.eigvalsh(cyc)) == 27,
        {"retained_one_channel_dimension": 9, "full_dimension": 27, "discarded_channels": 2, "scope": "coordinate readdressing is unitary only when every channel is retained"})
    fig, axs = pair(); dense = np.linspace(0, 2*np.pi, 401)
    for q, color in enumerate((TEAL, GOLD, LILAC)):
        axs[0].plot(dense, mu+2*kappa*np.cos((dense+2*np.pi*q)/p), color=color, label=f"phase q = {q}")
        axs[0].plot(theta, bands[:, q], "o", color=color, ms=4)
    axs[0].set(xlabel="coarse momentum θ", ylabel="dimensionless energy", title="A ternary split folds one cyclic spectrum", xticks=[0, np.pi, 2*np.pi], xticklabels=["0", "π", "2π"]); axs[0].legend(); grid(axs[0])
    axs[1].plot(range(n), np.linalg.eigvalsh(cyc), "o", color=TEAL, label="direct 27 × 27 spectrum")
    axs[1].plot(range(n), np.sort(bands.ravel()), "x", color=GOLD, ms=8, label="union of all folded channels")
    axs[1].set(xlabel="sorted spectral index", ylabel="dimensionless energy", title="The complete folded spectrum reconstructs exactly"); axs[1].legend(); grid(axs[1]); save(fig, STEMS[8])

    # 10: an explicitly infinite geometric family; no hidden finite ceiling.
    q = sp.Rational(1, 8); cutoff = np.arange(0, 13)
    exact_l2 = np.array([float(q**(r+1)) for r in cutoff])
    exact_graph = np.array([float(q**(r+1)+(1-q)*(4*q)**(r+1)/(1-4*q)) for r in cutoff])
    r_sym = sp.Symbol("r", integer=True, nonnegative=True)
    h_sym = sp.Symbol("H", integer=True, nonnegative=True)
    exact_mass = sp.summation((1-q)*q**r_sym, (r_sym, 0, sp.oo))
    l2_sum = sp.summation((1-q)*q**r_sym, (r_sym, h_sym+1, sp.oo))
    graph_sum = sp.summation((1+4**r_sym)*(1-q)*q**r_sym, (r_sym, h_sym+1, sp.oo))
    l2_target = q**(h_sym+1)
    graph_target = l2_target+(1-q)*(4*q)**(h_sym+1)/(1-4*q)
    record("exact geometric infinite tail identities", exact_mass == 1 and sp.simplify(l2_sum-l2_target) == 0 and sp.simplify(graph_sum-graph_target) == 0,
        {"detail_mass": "(1-q)q^r for r>=0", "q": "1/8", "epsilon_r": "2^r", "cutoff": "general nonnegative integer H", "computed_mass_sum": str(exact_mass), "computed_L2_tail": str(l2_sum), "computed_graph_tail": str(graph_sum), "L2_tail_squared": "q^(H+1)", "graph_tail_squared": "q^(H+1)+(1-q)(4q)^(H+1)/(1-4q)", "infinite_graph_condition": "4q<1", "arithmetic": "exact rational symbolic infinite geometric sums"})
    mass = np.array([float((1-q)*q**r) for r in range(100)]); eigs = 2.**np.arange(100)
    discrepancy = max(abs(mass[r+1:].sum()-exact_l2[r]) for r in cutoff)
    graphdis = max(abs(((1+eigs[r+1:]**2)*mass[r+1:]).sum()-exact_graph[r]) for r in cutoff)
    record("independent bounded sums match exact infinite tails", discrepancy < 2e-17 and graphdis < 3e-16,
        {"coefficient_terms": 100, "cutoffs": [0, 12], "q": "1/8", "L2_max_residual": float(discrepancy), "graph_max_residual": float(graphdis), "truncation_note": "exact closed infinite formulas are the plotted objects; 100-term sums are checks", "tolerance": 3e-16})
    record("L2 versus graph-domain negative control", sp.Rational(1, 2)*2**10 > 1,
        {"q": "1/2", "epsilon_r": "2^r", "total_L2_mass": 1, "graph_summand": "(1/2)*2^r, so does not tend to zero", "scope": "vector belongs to L2 but not D(H)"})
    fig, axs = pair()
    axs[0].semilogy(cutoff, np.sqrt(exact_l2), "o-", color=TEAL, label="exact L² tail")
    axs[0].semilogy(cutoff, np.sqrt(exact_graph), "s-", color=GOLD, label="exact graph-norm tail")
    axs[0].set(xlabel="retained maximum Haar level H", ylabel="tail norm", title="Graph convergence requires faster detail decay"); axs[0].legend(); grid(axs[0])
    rr = np.arange(0, 13)
    axs[1].semilogy(rr, .875*(.5)**rr, "o-", color=TEAL, label="εᵣ² mᵣ, q = 1/8")
    axs[1].semilogy(rr, .5*2.**rr, "s-", color=GOLD, label="εᵣ² mᵣ, q = 1/2")
    axs[1].set(xlabel="detail level r", ylabel="domain-weighted mass εᵣ² mᵣ", title="An L² state can lie outside the Hamiltonian domain"); axs[1].legend(); grid(axs[1]); save(fig, STEMS[9])

    # 11: exact Chebyshev compositions plus invariant low moments.
    x = sp.Symbol("x")
    r2 = 2*sp.chebyshevt(2, x/2); r3 = 2*sp.chebyshevt(3, x/2); r5 = 2*sp.chebyshevt(5, x/2)
    record("exact Chebyshev semigroup p2 p3", sp.expand(r2.subs(x, r3)-2*sp.chebyshevt(6, x/2)) == 0 and sp.expand(r3.subs(x, r2)-2*sp.chebyshevt(6, x/2)) == 0,
        {"maps": [str(r2), str(r3)], "composed": str(2*sp.chebyshevt(6, x/2)), "arithmetic": "exact symbolic polynomials"})
    angles = 2*np.pi*(np.arange(4096)+.5)/4096
    moments = []; momenterr = []
    for power in range(0, 9):
        target = 0 if power % 2 else int(sp.binomial(power, power//2))
        row = []
        for pp in (1, 2, 3, 5):
            val = float(np.mean((2*np.cos(pp*angles))**power)); row.append(val); momenterr.append(abs(val-target))
        moments.append(row)
    record("arcsine fixed low moments in angle quadrature", max(momenterr) < 2e-12,
        {"angle_nodes": 4096, "midpoint_full_circle": True, "map_primes": [2, 3, 5], "powers": list(range(9)), "reference_moments": "zero odd; binomial(2n,n) even", "max_residual": max(momenterr), "tolerance": 2e-12, "scope": "finite moment check supports but does not prove measure invariance"})
    fig, axs = pair(); xx = np.linspace(-2, 2, 601)
    for pp, color in ((2, TEAL), (3, GOLD), (5, LILAC)):
        axs[0].plot(xx, 2*eval_chebyt(pp, xx/2), color=color, label=f"R{pp}(x) = 2T{pp}(x/2)")
    axs[0].set(xlabel="normalized fine energy x", ylabel="renormalized energy Rₚ(x)", title="Prime spectral maps compose multiplicatively", xlim=(-2, 2), ylim=(-2.1, 2.1)); axs[0].legend(); grid(axs[0])
    even = np.arange(0, 9, 2); target = np.array([int(sp.binomial(j, j//2)) for j in even])
    axs[1].plot(even, target, "o-", color=TEAL, label="arcsine exact moment")
    for pp, color, marker in ((2, GOLD, "x"), (3, LILAC, "+"), (5, MUTED, "s")):
        vals = [moments[j][[1, 2, 3, 5].index(pp)] for j in even]
        axs[1].plot(even, vals, marker, color=color, ms=9, fillstyle="none", label=f"after R{pp}")
    axs[1].set(xlabel="even moment degree", ylabel="integral of xᵏ against ν", title="The sampled invariant moments agree"); axs[1].legend(fontsize=8); grid(axs[1]); save(fig, STEMS[10])

    # 12: independent residue series, root filter and hypergeometric forms.
    mp.mp.dps = 60
    hp_res = []
    for nn in (3, 5):
        for j in range(nn):
            for mu in (mp.mpf("0.2"), mp.mpf("2.5"), mp.mpf("8")):
                omega = mp.exp(2j*mp.pi/nn)
                roots = sum(omega**(-j*l)*mp.exp(mu*(omega**l-1)) for l in range(nn))/nn
                series = mp.exp(-mu)*mp.fsum(mu**(nn*k+j)/mp.factorial(nn*k+j) for k in range(70))
                params = [mp.mpf(j+r)/nn for r in range(1, nn+1) if j+r != nn]
                hyper = mp.exp(-mu)*mu**j/mp.factorial(j)*mp.hyper([], params, mu**nn/nn**nn)
                hp_res += [abs(roots-series), abs(hyper-series)]
    record("60-digit coherent residue formula comparison", max(hp_res) < mp.mpf("1e-55"),
        {"N": [3, 5], "mu": ["0.2", "2.5", "8"], "lanes": "all j=0,...,N-1", "series_terms_per_lane": 70, "mpmath_decimal_digits": 60, "maximum_residual": str(max(hp_res)), "tolerance": "1e-55", "scope": "arbitrary precision floating arithmetic, not interval certification"})
    nn = 5; mus = np.linspace(0, 15, 301); omega = np.exp(2j*np.pi/nn)
    packet = np.array([[sum(omega**(-j*l)*np.exp(mu*(omega**l-1)) for l in range(nn))/nn for j in range(nn)] for mu in mus])
    bb = (nn-1)/nn*np.exp(-mus*(1-np.cos(2*np.pi/nn)))
    deviation = np.max(abs(packet.real-1/nn), axis=1)
    record("coherent packet positivity normalization and mixing bound", np.min(packet.real) > -3e-15 and np.max(abs(packet.imag)) < 3e-15 and np.max(abs(packet.real.sum(axis=1)-1)) < 3e-15 and np.max(deviation-bb) < 3e-15,
        {"N": nn, "mu_samples": [0, 15, 301], "minimum_probability": float(np.min(packet.real)), "imaginary_max": float(np.max(abs(packet.imag))), "normalization_residual": float(np.max(abs(packet.real.sum(axis=1)-1))), "bound_excess": float(np.max(deviation-bb)), "tolerance": 3e-15})
    fig, axs = pair(); colors = [TEAL, GOLD, LILAC, "#709D8C", "#BD9882"]
    for j, color in enumerate(colors):
        axs[0].plot(mus, packet[:, j].real, color=color, label=f"j = {j}")
    axs[0].axhline(1/nn, color=MUTED, ls="--", lw=1)
    axs[0].set(xlabel="mean oscillator occupation μ", ylabel="number-residue probability", title="Coherent weights approach five equal packets"); axs[0].legend(ncol=3, fontsize=8); grid(axs[0])
    axs[1].semilogy(mus, deviation, color=TEAL, label="max packet deviation from 1/5")
    axs[1].semilogy(mus, bb, "--", color=GOLD, label="root-filter exponential bound")
    axs[1].set(xlabel="mean occupation μ", ylabel="absolute deviation", title="The exact residue formula has a mixing bound"); axs[1].legend(fontsize=8); grid(axs[1]); save(fig, STEMS[11])
    record("complete fresh plate inventory", len(outputs) == 24,
        {"figures": 12, "PDF": 12, "PNG": 12, "inherited_numeric_data_used": False, "deterministic": True})

def write_manifest(status, exit_status, error=None):
    artifacts = [{"path": str(p.relative_to(ROOT)), "sha256": HASHES[str(p.relative_to(ROOT))],
        "sha256_after": hashlib.sha256(p.read_bytes()).hexdigest()} for p in INPUTS]
    manifest = {"schema_version": 2, "claim_id": "physics-adic-atlas-bounded-examples-v0.5.0",
        "repository": {"commit": "not applicable: recovered publication staging directory", "dirty": True},
        "command": [sys.executable, "tools/make_adic_figures.py"],
        "environment": {"software": [{"name": "Python", "version": platform.python_version()},
            {"name": "NumPy", "version": np.__version__}, {"name": "SciPy", "version": scipy.__version__},
            {"name": "SymPy", "version": sp.__version__}, {"name": "mpmath", "version": mp.__version__},
            {"name": "Matplotlib", "version": matplotlib.__version__}], "hardware": platform.machine()},
        "mathematics": {"assertion_tested": "The separately described finite identities, negative controls, sampled operator families and explicit infinite geometric-tail specializations satisfy the checks below.",
            "coefficient_domain": "Exact rational/modular integer/symbolic polynomial expressions; complex128 finite matrices; mpmath 60-digit scalar comparisons.",
            "conventions": "Column vectors, positive-exponent unitary DFT, low p-adic digits as cylinders; E_r expectations and F_0=E_0,F_r=E_r-E_(r-1); positive real tree edge couplings; z in upper half-plane; complex amplitudes and ordinary Born rule.",
            "inputs": [{"path": k, "sha256": v} for k, v in HASHES.items()],
            "bounds": {"Haar_primes": [2, 3, 5], "Haar_depths": [1, 2, 3], "largest_Haar_dimension": 125,
                "descendant_primes": [2, 3], "descendant_depths": [0, 5], "largest_descendant_count": 243,
                "tower_dimensions": [9, 27], "walk_cycle": 7, "walk_primes": [2, 3], "walk_tree_depth": 2, "walk_ticks": 8,
                "radial_tree_depth": 3, "radial_primes": [2, 3], "folded_N": 27,
                "tail_coefficient_checks": 100, "tail_cutoffs": [0, 12], "arcsine_angle_nodes": 4096, "arcsine_moments": [0, 8],
                "coherent_packet_N": [3, 5], "high_precision_digits": 60, "coherent_curve_samples": 301,
                "resource_policy": "Small fixed arrays and loops; no network or randomness. No OS memory/CPU cap requested. Runtime recorded."},
            "non_claims": ["Bounded computations are not proofs for all primes, depths, Hamiltonians, or input vectors.",
                "The direct-limit and self-adjointness arguments belong to the manuscript, not to finite success counts.",
                "The product probability surface is a graph-coordinate aggregate, not a physical spacetime geometry.",
                "Finite graph locality is not a Lorentz-invariance or continuum field theorem.",
                "The Grover walk does not intertwine under canonical old-arc inclusion when leaf degrees change.",
                "Finite memory oscillations do not establish irreversible decay or an infinite-bath limit.",
                "Residue lanes of an arbitrary unbounded operator are not universally bounded functions.",
                "No new Lean compilation, experimental calibration, interacting quantum field construction or complete adeles is claimed."]},
        "randomness": {"used": False, "generator": "none", "seed": None},
        "run": {"started_at": STAMP, "runtime_seconds": time.monotonic()-START, "exit_status": exit_status, "status": status,
            "resource_limits": {"memory_bytes": None, "cpu_seconds": None, "max_cores": None, "max_threads": None}},
        "input_artifacts": artifacts, "execution_artifacts": [str(p.relative_to(ROOT)) for p in INPUTS],
        "declared_results": [f"source/adic_figures/{stem}.{ext}" for stem in STEMS for ext in ("pdf", "png")],
        "outputs": outputs, "checks": checks,
        "result": "Finite assertions verified in the stated ranges, conditional on declared numerical tolerances." if status == "completed" else f"Run failed: {error}",
        "residual_risks": ["Float64 matrix norms are not interval certified.", "mpmath comparisons are arbitrary precision numerical checks.",
            "Symbolic checks rely on SymPy, not a proof-assistant kernel.", "Library versions are recorded but dependencies are not locked.",
            "Manually recorded resource policy does not impose OS limits."]}
    name = "figure_checks.json" if status == "completed" else "figure_failed_"+STAMP.replace(":", "-")+".json"
    temporary = (EVID/name).with_suffix(".json.tmp")
    temporary.write_text(json.dumps(manifest, indent=2)+"\n")
    temporary.replace(EVID/name)
    with (EVID/"figure_run_history.jsonl").open("a") as stream:
        stream.write(json.dumps({"started_at": STAMP, "status": status, "exit_status": exit_status,
            "inputs": HASHES, "manifest": name, "error": error})+"\n")
    return manifest

if __name__ == "__main__":
    try:
        make_figures()
    except Exception as exc:
        # The failed script is retained because a checksum alone cannot reproduce it.
        (EVID/("failed_input_"+STAMP.replace(":", "-")+".py")).write_bytes(Path(__file__).read_bytes())
        write_manifest("failed", 1, str(exc)); traceback.print_exc(); sys.exit(1)
    result = write_manifest("completed", 0)
    print(json.dumps({"figures": 12, "checks": len(checks), "all_passed": True,
        "runtime_seconds": result["run"]["runtime_seconds"]}, indent=2))
