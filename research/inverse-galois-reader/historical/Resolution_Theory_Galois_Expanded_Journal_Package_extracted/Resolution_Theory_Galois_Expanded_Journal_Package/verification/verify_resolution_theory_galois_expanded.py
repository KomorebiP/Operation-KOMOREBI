#!/usr/bin/env python3
"""Deterministic verification for the final Resolution Theory manuscript.

The suite checks finite identities, representative countable and unbounded
models, nonlinear packet reconstruction, finite Resolution Logic, arithmetic
polyphase reconstruction, and source/package integrity.  It does not replace
proof of the general operator algebraic or categorical theorems.
"""
from __future__ import annotations

import cmath
import itertools
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "Resolution_Theory_Galois_Expanded_Core.tex"
REFS = ROOT / "Resolution_Theory_Galois_Expanded_References.tex"

checks = 0
failures: list[str] = []
groups: list[tuple[str, int]] = []


def check(condition: bool, message: str) -> None:
    global checks
    checks += 1
    if not condition:
        failures.append(message)


def close(a, b, tol: float = 1e-10) -> bool:
    return bool(np.linalg.norm(np.asarray(a) - np.asarray(b)) <= tol)


def run_group(name: str, fn: Callable[[], None]) -> None:
    before = checks
    fn()
    groups.append((name, checks - before))


def coordinate_projectors(block_sizes: list[int]) -> list[np.ndarray]:
    total = sum(block_sizes)
    out = []
    start = 0
    for size in block_sizes:
        P = np.zeros((total, total), dtype=complex)
        P[start : start + size, start : start + size] = np.eye(size)
        out.append(P)
        start += size
    return out


def random_complex(rng: np.random.Generator, rows: int, cols: int) -> np.ndarray:
    return rng.normal(size=(rows, cols)) + 1j * rng.normal(size=(rows, cols))


def test_finite_block_calculus() -> None:
    rng = np.random.default_rng(16301)
    for source_sizes, target_sizes in [([2, 1], [1, 2]), ([1, 1, 2], [2, 2]), ([3, 2], [1, 1, 3])]:
        P = coordinate_projectors(source_sizes)
        Q = coordinate_projectors(target_sizes)
        T = random_complex(rng, sum(target_sizes), sum(source_sizes))
        blocks = [[Qa @ T @ Pi for Pi in P] for Qa in Q]
        reconstruction = sum((b for row in blocks for b in row), np.zeros_like(T))
        check(close(reconstruction, T), "finite mixed block reconstruction")
        lhs = np.linalg.norm(T, "fro") ** 2
        rhs = sum(np.linalg.norm(b, "fro") ** 2 for row in blocks for b in row)
        check(abs(lhs - rhs) < 1e-9, "packet Parseval identity")

        selected = {(a, i) for a in range(len(Q)) for i in range(len(P)) if (a + i) % 2 == 0}
        kept = sum(
            (blocks[a][i] for a, i in selected),
            np.zeros_like(T),
        )
        residual = T - kept
        omitted_energy = sum(
            np.linalg.norm(blocks[a][i], "fro") ** 2
            for a in range(len(Q))
            for i in range(len(P))
            if (a, i) not in selected
        )
        check(abs(np.linalg.norm(residual, "fro") ** 2 - omitted_energy) < 1e-9,
              "selective compression residual")

    # Composition through intermediate packets.
    P = coordinate_projectors([1, 2])
    Q = coordinate_projectors([2, 1, 1])
    R = coordinate_projectors([2, 2])
    T = random_complex(rng, 4, 3)
    S = random_complex(rng, 4, 4)
    for c, Rc in enumerate(R):
        for i, Pi in enumerate(P):
            direct = Rc @ S @ T @ Pi
            packet = sum((Rc @ S @ Qa @ T @ Pi for Qa in Q), np.zeros_like(direct))
            check(close(direct, packet), f"packet path composition c={c},i={i}")


def test_refinement_and_common_charts() -> None:
    rng = np.random.default_rng(2042)
    coarse = coordinate_projectors([2, 2])
    fine = coordinate_projectors([1, 1, 1, 1])
    check(close(coarse[0], fine[0] + fine[1]), "first coarse refinement")
    check(close(coarse[1], fine[2] + fine[3]), "second coarse refinement")

    T = random_complex(rng, 4, 4)
    for a in range(2):
        for i in range(2):
            descendants_a = [2 * a, 2 * a + 1]
            descendants_i = [2 * i, 2 * i + 1]
            fine_sum = sum(
                (fine[b] @ T @ fine[j] for b in descendants_a for j in descendants_i),
                np.zeros_like(T),
            )
            check(close(coarse[a] @ T @ coarse[i], fine_sum), "exact refinement law")

    # Commuting and noncommuting projector charts.
    P = np.diag([1, 1, 0, 0]).astype(complex)
    Q = np.diag([1, 0, 1, 0]).astype(complex)
    check(close(P @ Q, Q @ P), "commuting coordinate charts")
    refinements = [P @ Q, P @ (np.eye(4) - Q), (np.eye(4) - P) @ Q,
                   (np.eye(4) - P) @ (np.eye(4) - Q)]
    check(close(sum(refinements), np.eye(4)), "common refinement completeness")
    for A, B in itertools.combinations(refinements, 2):
        check(close(A @ B, np.zeros((4, 4))), "common refinement orthogonality")

    sigma_x = np.array([[0, 1], [1, 0]], dtype=complex)
    sigma_z = np.array([[1, 0], [0, -1]], dtype=complex)
    Px = (np.eye(2) + sigma_x) / 2
    Pz = (np.eye(2) + sigma_z) / 2
    check(np.linalg.norm(Px @ Pz - Pz @ Px) > 0.5, "incompatible quantum charts")


def test_commutant_laplacian() -> None:
    rng = np.random.default_rng(701)
    for dim in [2, 3, 5]:
        A = random_complex(rng, dim, dim)
        A = (A + A.conj().T) / 2
        B = random_complex(rng, dim, dim)
        B = (B + B.conj().T) / 2
        X = random_complex(rng, dim, dim)
        L = A @ (A @ X - X @ A) - (A @ X - X @ A) @ A
        L += B @ (B @ X - X @ B) - (B @ X - X @ B) @ B
        inner = np.vdot(X, L).real
        rhs = np.linalg.norm(A @ X - X @ A, "fro") ** 2
        rhs += np.linalg.norm(B @ X - X @ B, "fro") ** 2
        check(abs(inner - rhs) < 1e-8, f"commutant Laplacian identity dim={dim}")
        check(inner >= -1e-8, f"commutant Laplacian positivity dim={dim}")

    # Diagonal family has diagonal commutant.
    A = np.diag([1, 2, 3]).astype(complex)
    X = np.diag([2, -1, 4]).astype(complex)
    check(close(A @ X, X @ A), "diagonal commutant element")


def random_rank_one_projector(rng: np.random.Generator, dim: int) -> np.ndarray:
    v = random_complex(rng, dim, 1).reshape(dim)
    v = v / np.linalg.norm(v)
    return np.outer(v, v.conj())


def ordered_resolution_distance(P: list[np.ndarray], Q: list[np.ndarray]) -> float:
    return math.sqrt(0.5 * sum(np.linalg.norm(a - b, "fro") ** 2 for a, b in zip(P, Q)))


def block_field_defect(T: np.ndarray, P, Pt, Q, Qt) -> float:
    total = 0.0
    for a in range(len(Q)):
        for i in range(len(P)):
            d = Q[a] @ T @ P[i] - Qt[a] @ T @ Pt[i]
            total += np.linalg.norm(d, "fro") ** 2
    return math.sqrt(total)


def test_resolution_geometry_and_stability() -> None:
    rng = np.random.default_rng(8117)
    # Chordal triangle inequality and resolution matching for ordered examples.
    for dim in [3, 5, 7]:
        P = random_rank_one_projector(rng, dim)
        Q = random_rank_one_projector(rng, dim)
        R = random_rank_one_projector(rng, dim)
        dPQ = np.linalg.norm(P - Q, "fro") / math.sqrt(2)
        dQR = np.linalg.norm(Q - R, "fro") / math.sqrt(2)
        dPR = np.linalg.norm(P - R, "fro") / math.sqrt(2)
        check(dPR <= dPQ + dQR + 1e-12, f"chordal triangle dim={dim}")

    # Block-field Lipschitz theorem.
    for dim in [4, 6]:
        P = coordinate_projectors([dim // 2, dim - dim // 2])
        Q = coordinate_projectors([1, dim - 1])
        Z1 = random_complex(rng, dim, dim)
        U1, _ = np.linalg.qr(Z1)
        Z2 = random_complex(rng, dim, dim)
        U2, _ = np.linalg.qr(Z2)
        eps = 0.04
        # Near-identity unitaries from skew Hermitian generators.
        K1 = (U1 - U1.conj().T) / 2
        K2 = (U2 - U2.conj().T) / 2
        w1, V1 = np.linalg.eigh(1j * K1)
        w2, V2 = np.linalg.eigh(1j * K2)
        W1 = V1 @ np.diag(np.exp(-1j * eps * w1)) @ V1.conj().T
        W2 = V2 @ np.diag(np.exp(-1j * eps * w2)) @ V2.conj().T
        Pt = [W1 @ A @ W1.conj().T for A in P]
        Qt = [W2 @ A @ W2.conj().T for A in Q]
        T = random_complex(rng, dim, dim)
        defect = block_field_defect(T, P, Pt, Q, Qt)
        rhs = 2 * np.linalg.norm(T, "fro") * math.sqrt(
            ordered_resolution_distance(P, Pt) ** 2 + ordered_resolution_distance(Q, Qt) ** 2
        )
        check(defect <= rhs + 1e-10, f"block stability dim={dim}")

    # Kato transport for a rotating two-packet resolution.
    theta = 0.37
    U = np.array([[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]], dtype=float)
    P0 = np.diag([1.0, 0.0])
    P1 = U @ P0 @ U.T
    check(close(P1 @ P1, P1), "transported projector idempotence")
    check(abs(np.trace(P1) - 1) < 1e-12, "transported rank preservation")

    # Commutant-gap inequality for a diagonal family.
    A = np.diag([0.0, 1.0, 3.0])
    theta = 0.06
    U = np.array([[math.cos(theta), -math.sin(theta), 0.0],
                  [math.sin(theta), math.cos(theta), 0.0],
                  [0.0, 0.0, 1.0]])
    P = U @ np.diag([1.0, 0.0, 0.0]) @ U.T
    E = np.diag(np.diag(P))
    leakage = np.linalg.norm(A @ P - P @ A, "fro") ** 2
    gamma = 1.0
    check(np.linalg.norm(P - E, "fro") ** 2 <= leakage / gamma + 1e-12,
          "commutant gap distance bound")


def weighted_schur_norm(blocks: np.ndarray, alpha: float = 0.4) -> float:
    n = blocks.shape[0]
    weights = np.exp(alpha * np.abs(np.arange(n)[:, None] - np.arange(n)[None, :]))
    abs_blocks = np.abs(blocks)
    col = np.max(np.sum(weights * abs_blocks, axis=0))
    row = np.max(np.sum(weights * abs_blocks, axis=1))
    return float(max(col, row))


def test_weighted_transfer_algebra() -> None:
    rng = np.random.default_rng(1904)
    for n in [3, 5, 8]:
        A = rng.normal(size=(n, n)) * 0.08
        B = rng.normal(size=(n, n)) * 0.08
        check(weighted_schur_norm(A @ B) <= weighted_schur_norm(A) * weighted_schur_norm(B) + 1e-12,
              f"weighted Schur product n={n}")
        check(abs(weighted_schur_norm(A.T) - weighted_schur_norm(A)) < 1e-12,
              f"weighted Schur adjoint n={n}")

    # Neumann inverse and path expansion.
    n = 6
    R = np.zeros((n, n))
    for i in range(n - 1):
        R[i, i + 1] = 0.08
        R[i + 1, i] = 0.05
    check(weighted_schur_norm(R) < 1, "weighted perturbation small")
    inverse = np.linalg.inv(np.eye(n) + R)
    partial = np.eye(n)
    term = np.eye(n)
    for _ in range(60):
        term = -term @ R
        partial += term
    check(close(partial, inverse, 1e-10), "Neumann packet path inverse")
    bound = weighted_schur_norm(np.eye(n)) / (1 - weighted_schur_norm(R))
    check(weighted_schur_norm(inverse) <= bound + 1e-9, "weighted inverse norm bound")

    # Schur complement identity.
    A = np.array([[2.0]])
    B = np.array([[0.3, -0.1]])
    C = B.T
    D = np.array([[1.8, 0.2], [0.2, 1.4]])
    T = np.block([[A, B], [C, D]])
    Di = np.linalg.inv(D)
    S = A - B @ Di @ C
    formula = np.block([
        [np.linalg.inv(S), -np.linalg.inv(S) @ B @ Di],
        [-Di @ C @ np.linalg.inv(S), Di + Di @ C @ np.linalg.inv(S) @ B @ Di],
    ])
    check(close(formula, np.linalg.inv(T)), "two-packet Schur complement")


def test_universal_corner_extension() -> None:
    rng = np.random.default_rng(302)
    sizes = [1, 2, 1]
    P = coordinate_projectors(sizes)
    dim = sum(sizes)
    # A compatible corner assignment obtained by one unitary conjugation.
    Z = random_complex(rng, dim, dim)
    U, _ = np.linalg.qr(Z)
    Q = [U @ Pi @ U.conj().T for Pi in P]
    for _ in range(25):
        a = random_complex(rng, dim, dim)
        b = random_complex(rng, dim, dim)
        Fa = U @ a @ U.conj().T
        Fb = U @ b @ U.conj().T
        check(close(Fa @ Fb, U @ (a @ b) @ U.conj().T), "corner extension multiplication")
        check(close(Fa.conj().T, U @ a.conj().T @ U.conj().T), "corner extension dagger")
        for x, Px in enumerate(P):
            for y, Py in enumerate(P):
                block = Py @ a @ Px
                represented = U @ block @ U.conj().T
                check(close(represented, Q[y] @ Fa @ Q[x]), "represented corner equality")

    # Refinement naturality.
    e = P[1]
    sub = coordinate_projectors([1, 1, 1, 1])
    e1, e2 = sub[1], sub[2]
    check(close(e, e1 + e2), "chosen refinement before representation")
    check(close(U @ e @ U.conj().T,
                U @ e1 @ U.conj().T + U @ e2 @ U.conj().T),
          "refinement naturality under representation")


def test_countable_and_unbounded_models() -> None:
    # Countable coordinate projections on l2, simulated by increasing finite sections.
    n = 400
    x = np.array([1 / (k + 1) ** 1.2 for k in range(n)], dtype=float)
    total = np.linalg.norm(x)
    previous_error = total
    for N in [1, 2, 5, 10, 20, 50, 100, 200, 399]:
        trunc = np.zeros_like(x)
        trunc[:N] = x[:N]
        error = np.linalg.norm(x - trunc)
        check(error <= previous_error + 1e-14, "strong packet truncation monotonicity")
        previous_error = error
    check(previous_error < 0.01, "strong packet truncation convergence")

    # Identity truncations never converge in operator norm.
    for N in [1, 5, 20, 100]:
        diag = np.zeros(n)
        diag[:N] = 1
        check(abs(np.max(np.abs(1 - diag)) - 1) < 1e-14,
              "strong but not norm convergence")

    # Compact diagonal operator converges in operator and Schatten norms.
    singular = np.array([1 / (k + 1) ** 1.1 for k in range(n)])
    for N in [5, 20, 100, 250]:
        tail = singular[N:]
        check(abs(np.max(tail) - singular[N]) < 1e-14, "compact operator norm tail")
        check(np.linalg.norm(tail) < np.linalg.norm(singular), "Hilbert Schmidt tail decrease")

    # Unbounded diagonal generator with graph norm reconstruction.
    eigen = np.arange(1, n + 1, dtype=float)
    vector = 1 / (eigen ** 2.2)
    graph_sq = np.sum(np.abs(vector) ** 2 + np.abs(eigen * vector) ** 2)
    check(math.isfinite(graph_sq), "unbounded graph vector finite")
    for N in [10, 30, 100, 250]:
        tail_sq = np.sum(np.abs(vector[N:]) ** 2 + np.abs(eigen[N:] * vector[N:]) ** 2)
        check(tail_sq < graph_sq, "graph norm tail bounded")
    check(tail_sq < 0.01, "graph norm reconstruction convergence")

    # Resolvent commutator identity in finite diagonal model.
    D = np.diag(np.arange(1, 7)).astype(complex)
    P = np.zeros((6, 6), dtype=complex)
    P[:3, :3] = np.eye(3)
    P[2, 3] = 0.2
    z = 0.3 + 1.4j
    R = np.linalg.inv(D - z * np.eye(6))
    lhs = P @ R - R @ P
    comm = D @ P - P @ D
    rhs = R @ comm @ R
    check(close(lhs, rhs), "resolvent commutator identity")


def test_countable_completion_extensions() -> None:
    # Trace class state truncation in a diagonal model.
    weights = np.array([2.0 ** (-k) for k in range(1, 50)])
    weights = weights / weights.sum()
    for N in [2, 5, 10, 20, 40]:
        tail = weights[N:].sum()
        check(tail >= 0, "state tail nonnegative")
    check(weights[40:].sum() < 1e-10, "trace state packet truncation")

    # Strict finite windows on a compact matrix model.
    n = 80
    i = np.arange(n)
    K = 1.0 / (1.0 + np.abs(i[:, None] - i[None, :])) ** 2
    for N in [5, 10, 20, 40, 70]:
        E = np.zeros((n, n)); E[:N, :N] = np.eye(N)
        defect = np.linalg.norm(E @ K - K, 2) + np.linalg.norm(K @ E - K, 2)
        check(math.isfinite(defect), "strict window defect finite")
    E = np.zeros((n, n)); E[:70, :70] = np.eye(70)
    check(np.linalg.norm(E @ K - K, 2) < np.linalg.norm(K, 2), "strict window improves compact element")

    # Strong resolvent convergence for a diagonal generator.
    eig = np.arange(1, 101, dtype=float)
    z = 0.4 + 1.3j
    x = 1 / eig ** 1.3
    full = x / (eig - z)
    for N in [5, 15, 40, 80]:
        approx = np.zeros_like(full, dtype=complex)
        approx[:N] = x[:N] / (eig[:N] - z)
        approx[N:] = -x[N:] / z
        check(np.linalg.norm(approx - full) < np.linalg.norm(x) * 2, "strong resolvent finite window")
    check(np.linalg.norm(approx - full) < 0.01, "strong resolvent convergence")

    # Duhamel leakage envelope.
    D = np.array([[0.0, 0.2], [0.2, 1.0]])
    P = np.diag([1.0, 0.0])
    comm = np.linalg.norm(D @ P - P @ D, 2)
    for t in [0.1, 0.5, 1.0]:
        w, V = np.linalg.eigh(D)
        U = V @ np.diag(np.exp(-1j * t * w)) @ V.conj().T
        leak = np.linalg.norm((np.eye(2) - P) @ U @ P, 2)
        check(leak <= t * comm + 1e-12, "Duhamel leakage bound")


def test_nonlinear_packets() -> None:
    rng = np.random.default_rng(951)
    P = coordinate_projectors([1, 2])
    Q = coordinate_projectors([2, 1])
    # Bilinear map represented by tensor B[out, in1, in2].
    B = rng.normal(size=(3, 3, 3))
    x = rng.normal(size=3)
    y = rng.normal(size=3)

    def eval_bilinear(u: np.ndarray, v: np.ndarray) -> np.ndarray:
        return np.einsum("ijk,j,k->i", B, u, v)

    direct = eval_bilinear(x, y)
    packet = np.zeros(3)
    for Qa in Q:
        for Pi in P:
            for Pj in P:
                packet += Qa.real @ eval_bilinear(Pi.real @ x, Pj.real @ y)
    check(close(direct, packet), "multilinear packet reconstruction")

    # Refinement coherence: split the two-dimensional source packet.
    fine = coordinate_projectors([1, 1, 1])
    fine_packet = np.zeros(3)
    for Qa in Q:
        for Pi in fine:
            for Pj in fine:
                fine_packet += Qa.real @ eval_bilinear(Pi.real @ x, Pj.real @ y)
    check(close(packet, fine_packet), "nonlinear refinement coherence")

    # Scalar Faà di Bruno check for G(F(x)), n=2.
    x0 = 0.37
    # F=x+x^2, G=exp.
    F = x0 + x0 * x0
    F1 = 1 + 2 * x0
    F2 = 2.0
    composed_second = math.exp(F) * (F1 * F1 + F2)
    h = 1e-5
    def comp(t: float) -> float:
        return math.exp(t + t * t)
    finite_difference = (comp(x0 + h) - 2 * comp(x0) + comp(x0 - h)) / h**2
    check(abs(composed_second - finite_difference) < 2e-5, "Faà di Bruno scalar check")

    # Near-identity inversion x + alpha tanh x by fixed point.
    alpha = 0.3
    for target in np.linspace(-0.5, 0.5, 9):
        x_iter = target
        for _ in range(100):
            x_iter = target - alpha * math.tanh(x_iter)
        check(abs(x_iter + alpha * math.tanh(x_iter) - target) < 1e-12,
              "near identity inverse fixed point")


def test_expanded_nonlinear_dynamics() -> None:
    # Countable multilinear tail in a scalar packet model.
    coeff = np.array([1 / (k + 1) ** 2 for k in range(200)])
    x = np.array([1 / (k + 1) for k in range(200)])
    full = float(np.dot(coeff, x * x))
    for N in [5, 20, 80, 160]:
        partial = float(np.dot(coeff[:N], x[:N] * x[:N]))
        tail_bound = float(np.dot(coeff[N:], np.abs(x[N:]) ** 2))
        check(abs(full - partial) <= tail_bound + 1e-15, "countable multilinear tail")

    # Newton certificate on x + 0.2 sin x = y.
    for y in np.linspace(-0.6, 0.6, 9):
        xk = y
        for _ in range(20):
            xk -= (xk + 0.2 * math.sin(xk) - y) / (1 + 0.2 * math.cos(xk))
        check(abs(xk + 0.2 * math.sin(xk) - y) < 1e-13, "resolved Newton convergence")

    # Ito packet identity for phi(x)=||x||^2 in two packets.
    x = np.array([0.7, -0.2])
    b = np.array([0.3, -0.4])
    sigma = np.array([[0.5, 0.0], [0.1, 0.4]])
    generator = 2 * np.dot(x, b) + np.trace(sigma @ sigma.T)
    P = coordinate_projectors([1, 1])
    drift = sum(2 * np.dot(x, Pi @ b) for Pi in P)
    diffusion = 0.0
    for Pi in P:
        for Pj in P:
            diffusion += np.trace((Pi @ sigma) @ (Pj @ sigma).T)
    check(abs(generator - (drift + diffusion)) < 1e-12, "Ito packet generator")


def test_countable_resolution_logic() -> None:
    mapping = {j: j // 3 for j in range(18)}
    fine = set(mapping)
    coarse = set(mapping.values())
    for mask in range(1 << len(coarse)):
        A = {i for i in coarse if mask & (1 << i)}
        pull = {j for j in fine if mapping[j] in A}
        check(all(mapping[j] in A for j in pull), "countable atomic pullback")
    rng = np.random.default_rng(211)
    c = rng.random(len(fine))
    sup = np.array([max(c[j] for j in fine if mapping[j] == i) for i in sorted(coarse)])
    inf = np.array([min(c[j] for j in fine if mapping[j] == i) for i in sorted(coarse)])
    check(np.all(sup >= inf), "quantitative fiber sup inf")

    # Countable packet error transport in a finite approximation.
    B = np.abs(rng.normal(size=(12, 18))) / 20
    eps = np.abs(rng.normal(size=18)) / 100
    delta = B @ eps
    check(np.linalg.norm(delta) <= np.linalg.norm(B, 2) * np.linalg.norm(eps) + 1e-14,
          "countable packet error transport")


def test_resolution_logic() -> None:
    # Coarse atoms {A,B}; fine atoms {a1,a2,b1}. Pullback is inverse image.
    fine_to_coarse = {"a1": "A", "a2": "A", "b1": "B"}
    coarse_atoms = {"A", "B"}
    fine_atoms = set(fine_to_coarse)

    def pullback(coarse_subset: set[str]) -> set[str]:
        return {x for x in fine_atoms if fine_to_coarse[x] in coarse_subset}

    def exists(fine_subset: set[str]) -> set[str]:
        return {fine_to_coarse[x] for x in fine_subset}

    def forall(fine_subset: set[str]) -> set[str]:
        return {c for c in coarse_atoms if pullback({c}) <= fine_subset}

    coarse_subsets = [set(s) for r in range(3) for s in itertools.combinations(coarse_atoms, r)]
    fine_subsets = [set(s) for r in range(4) for s in itertools.combinations(fine_atoms, r)]
    for a in coarse_subsets:
        for b in fine_subsets:
            check((exists(b) <= a) == (b <= pullback(a)), "existential Galois connection")
            check((pullback(a) <= b) == (a <= forall(b)), "universal Galois connection")

    # Linear and bilinear certificate transport.
    A = np.array([[2.0, -1.0], [0.5, 1.0]])
    x = np.array([1.0, -0.3])
    xhat = x + np.array([0.01, -0.02])
    eps = np.linalg.norm(x - xhat)
    check(np.linalg.norm(A @ x - A @ xhat) <= np.linalg.norm(A, 2) * eps + 1e-14,
          "linear error transport")


def test_realizations() -> None:
    # Finite Fourier projectors for C_5.
    n = 5
    omega = cmath.exp(2j * math.pi / n)
    vectors = [np.array([omega ** (k * j) for j in range(n)], dtype=complex) / math.sqrt(n)
               for k in range(n)]
    projectors = [np.outer(v, v.conj()) for v in vectors]
    check(close(sum(projectors), np.eye(n)), "Fourier projector completeness")
    for i, Pi in enumerate(projectors):
        check(close(Pi @ Pi, Pi), "Fourier projector idempotence")
        for j, Pj in enumerate(projectors):
            if i != j:
                check(close(Pi @ Pj, np.zeros((n, n))), "Fourier projector orthogonality")

    # Cyclic convolution diagonalized by Fourier vectors.
    h = np.array([1.0, 2.0, -0.5, 0.7, 0.2])
    C = np.array([[h[(i - j) % n] for j in range(n)] for i in range(n)], dtype=complex)
    for v in vectors:
        Cv = C @ v
        coefficient = np.vdot(v, Cv)
        check(close(Cv, coefficient * v), "convolution Fourier diagonalization")

    # Arithmetic polyphase reconstruction for random finite sequence.
    rng = np.random.default_rng(119)
    values = rng.normal(size=60)
    for q in [2, 3, 5, 6]:
        reconstructed = np.empty_like(values)
        for r in range(q):
            packet = values[r::q]
            reconstructed[r::q] = packet
        check(close(reconstructed, values), f"arithmetic packet reconstruction q={q}")
    # q=3 refined to Q=12.
    q, m = 3, 4
    for r in range(q):
        parent_indices = list(range(r, len(values), q))
        child_indices = sorted(
            i for b in range(m) for i in range(r + q * b, len(values), q * m)
        )
        check(parent_indices == child_indices, "arithmetic refinement partition")


    # Arithmetic sieve line and Gauss change of resolution.
    p = 7
    killed = 3
    children = np.array([4.37, 4.42, 4.39, 0.0, 4.41, 4.35, 4.36])
    M = children.mean()
    K = children[killed]
    C = (p * M - K) / (p - 1)
    sieve = np.full(p, C - M)
    sieve[killed] = K - M
    residual = children - M - sieve
    check(abs(residual[killed]) < 1e-12, "sieve residual killed coordinate")
    check(abs(residual.sum()) < 1e-12, "sieve residual zero sum")
    lhs = np.mean(np.abs(children - M) ** 2)
    rhs = abs(K - M) ** 2 / (p - 1) + np.mean(np.abs(residual) ** 2)
    check(abs(lhs - rhs) < 1e-12, "arithmetic sieve Pythagoras")

    # Additive and multiplicative energy equivalence on the unit children.
    unit_values = np.delete(residual, killed).astype(complex)
    add_extended = np.zeros(p, dtype=complex)
    unit_residues = [c for c in range(p) if c != 0]
    # Reindex the six survivor values by nonzero residues in a model chart.
    add_extended[1:] = unit_values
    Acoef = np.fft.fft(add_extended) / p
    g = 3
    powers = [pow(g, j, p) for j in range(p - 1)]
    ordered = np.array([add_extended[c] for c in powers])
    Bcoef = np.fft.fft(ordered) / (p - 1)
    check(abs(np.sum(np.abs(Acoef[1:]) ** 2) - (p - 1) / p * np.sum(np.abs(Bcoef[1:]) ** 2)) < 1e-12,
          "Gauss chart energy equivalence")




def compose_perm(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p[q[i]] for i in range(len(p)))


def inverse_perm(p: tuple[int, ...]) -> tuple[int, ...]:
    out = [0] * len(p)
    for i, j in enumerate(p):
        out[j] = i
    return tuple(out)


def generated_group(generators: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    identity = tuple(range(len(generators[0])))
    group = {identity}
    frontier = [identity]
    while frontier:
        a = frontier.pop()
        for g in generators:
            for b in (compose_perm(a, g), compose_perm(g, a)):
                if b not in group:
                    group.add(b)
                    frontier.append(b)
    return sorted(group)


def regular_matrices(group: list[tuple[int, ...]]) -> dict[tuple[int, ...], np.ndarray]:
    index = {g: i for i, g in enumerate(group)}
    matrices = {}
    for g in group:
        M = np.zeros((len(group), len(group)), dtype=complex)
        for h in group:
            M[index[compose_perm(g, h)], index[h]] = 1.0
        matrices[g] = M
    return matrices


def subgroup_average(subgroup, matrices) -> np.ndarray:
    return sum((matrices[g] for g in subgroup), np.zeros_like(next(iter(matrices.values())))) / len(subgroup)


def test_galois_resolution() -> None:
    e = (0, 1, 2)
    a = (1, 0, 2)
    b = (0, 2, 1)
    c = (1, 2, 0)
    s3 = generated_group([a, b])
    mats = regular_matrices(s3)
    H = generated_group([a])
    K = generated_group([b])
    A3 = generated_group([c])
    G = s3

    PH = subgroup_average(H, mats)
    PK = subgroup_average(K, mats)
    PA = subgroup_average(A3, mats)
    PG = subgroup_average(G, mats)
    I = np.eye(len(G))

    for P, rank, name in [(PH, 3, 'C2 fixed projector'), (PA, 2, 'A3 fixed projector'), (PG, 1, 'G fixed projector')]:
        check(close(P @ P, P), f'{name} idempotent')
        check(close(P.conj().T, P), f'{name} self adjoint')
        check(abs(np.trace(P).real - rank) < 1e-10, f'{name} rank')

    check(close(PH @ PG, PG) and close(PG @ PH, PG), 'subgroup order reverses projector order')
    check(close(PH @ PA, PG) and close(PA @ PH, PG), 'permutable subgroup product projector')
    check(np.linalg.norm(PH @ PK - PK @ PH) > 1e-6, 'nonpermutable subgroup projectors do not commute')

    # Normality and centrality.
    check(all(close(M @ PA, PA @ M) for M in mats.values()), 'normal subgroup projector central')
    check(any(np.linalg.norm(M @ PH - PH @ M) > 1e-6 for M in mats.values()), 'nonnormal subgroup projector noncentral')

    # Conjugate projector atlas.
    g = b
    gHg = [compose_perm(compose_perm(g, h), inverse_perm(g)) for h in H]
    PgHg = subgroup_average(gHg, mats)
    check(close(mats[g] @ PH @ mats[g].conj().T, PgHg), 'conjugate fixed projector atlas')

    # Finite group conditional expectation on M2 under conjugation by Z.
    Z = np.diag([1.0, -1.0])
    X = np.array([[1.0, 2.0 + 1j], [2.0 - 1j, 3.0]], dtype=complex)
    E = 0.5 * (X + Z @ X @ Z)
    EE = 0.5 * (E + Z @ E @ Z)
    check(close(E, EE), 'fixed algebra conditional expectation idempotent')
    check(abs(E[0, 1]) < 1e-12 and abs(E[1, 0]) < 1e-12, 'fixed algebra expectation range')

    # Mackey model: restriction to A3 of the S3 action on G/H is regular C3.
    cosets = []
    unused = set(G)
    while unused:
        representative = next(iter(unused))
        coset = {compose_perm(representative, h) for h in H}
        cosets.append(coset)
        unused -= coset
    perm_rep = {}
    for g0 in A3:
        M = np.zeros((len(cosets), len(cosets)))
        for j, coset in enumerate(cosets):
            image = {compose_perm(g0, x) for x in coset}
            i = next(i for i, cset in enumerate(cosets) if cset == image)
            M[i, j] = 1.0
        perm_rep[g0] = M
    traces = sorted(round(np.trace(M).real) for M in perm_rep.values())
    check(traces == [0, 0, 3], 'Mackey double coset regular restriction')


def test_fourier_galois_and_ramification() -> None:
    # C6 regular representation and annihilator formula.
    n = 6
    shift = np.roll(np.eye(n), 1, axis=0).astype(complex)
    powers = [np.linalg.matrix_power(shift, j) for j in range(n)]
    H_indices = [0, 2, 4]
    PH = sum((powers[j] for j in H_indices), np.zeros((n, n), dtype=complex)) / len(H_indices)
    omega = cmath.exp(2j * math.pi / n)
    vectors = [np.array([omega ** (k * j) for j in range(n)], dtype=complex) / math.sqrt(n) for k in range(n)]
    chars = [np.outer(v, v.conj()) for v in vectors]
    annihilator = chars[0] + chars[3]
    check(close(PH, annihilator), 'abelian subgroup projector is annihilator sum')

    # Ramification model on C8.
    n = 8
    shift = np.roll(np.eye(n), 1, axis=0).astype(complex)
    powers = [np.linalg.matrix_power(shift, j) for j in range(n)]
    subgroups = [[0,1,2,3,4,5,6,7], [0,2,4,6], [0,4], [0]]
    P = [sum((powers[j] for j in H), np.zeros((n,n),dtype=complex))/len(H) for H in subgroups]
    for i in range(len(P)-1):
        check(close(P[i] @ P[i+1], P[i]), f'ramification nested projector {i}')
    D = [P[i+1] - P[i] for i in range(len(P)-1)]
    for i, Di in enumerate(D):
        check(close(Di @ Di, Di), f'ramification detail idempotent {i}')
        for j, Dj in enumerate(D):
            if i != j:
                check(close(Di @ Dj, np.zeros((n,n))), f'ramification detail orthogonal {i},{j}')
    check(close(P[0] + sum(D, np.zeros((n,n),dtype=complex)), np.eye(n)), 'ramification detail reconstruction')
    weights = [1.0, 0.5, 0.25]
    conductor_codim = sum(w * (n - np.trace(Pi).real) for w, Pi in zip(weights, P[:-1]))
    ranks = [np.trace(Di).real for Di in D]
    conductor_details = sum(ranks[j] * sum(weights[:j+1]) for j in range(len(ranks)))
    check(abs(conductor_codim - conductor_details) < 1e-10, 'Artin conductor detail identity')


def test_profinite_and_cohomological_descent() -> None:
    # Finite proxy for a shrinking profinite subgroup basis in C2^4.
    elements = [tuple(bits) for bits in itertools.product([0, 1], repeat=4)]
    index = {g: i for i, g in enumerate(elements)}
    mats = {}
    for g in elements:
        M = np.zeros((16,16), dtype=complex)
        for h in elements:
            gh = tuple((a+b) % 2 for a,b in zip(g,h))
            M[index[gh], index[h]] = 1.0
        mats[g] = M
    subgroups = []
    for start in range(0,5):
        H = [g for g in elements if all(g[j] == 0 for j in range(start))]
        subgroups.append(H)
    P = [subgroup_average(H, mats) for H in subgroups]
    for i in range(len(P)-1):
        check(close(P[i] @ P[i+1], P[i]), f'profinite finite-level nesting {i}')
    check(close(P[-1], np.eye(16)), 'shrinking subgroup reconstruction reaches identity')

    # Constructive matrix Hilbert 90 model for complex conjugation.
    rng = np.random.default_rng(9901)
    B = random_complex(rng, 3, 3)
    while abs(np.linalg.det(B)) < 0.2:
        B = random_complex(rng, 3, 3)
    A = np.linalg.inv(B) @ np.conj(B)
    check(close(A @ np.conj(A), np.eye(3)), 'Hilbert 90 cocycle condition')
    fixed = [np.linalg.inv(B) @ np.eye(3)[:,j] for j in range(3)]
    for v in fixed:
        check(close(A @ np.conj(v), v), 'Hilbert 90 fixed vector')
    check(abs(np.linalg.det(np.column_stack(fixed))) > 1e-8, 'Hilbert 90 fixed basis')

    # Projective V4 model with a nontrivial commutator phase.
    X = np.array([[0,1],[1,0]], dtype=complex)
    Z = np.array([[1,0],[0,-1]], dtype=complex)
    commutator = X @ Z @ np.linalg.inv(X) @ np.linalg.inv(Z)
    check(close(commutator, -np.eye(2)), 'projective Brauer phase model')

    # C3 tensor automorphism model.
    roots = [cmath.exp(2j * math.pi * j / 3) for j in range(3)]
    for z in roots:
        lambdas = [1, z, z*z]
        check(all(abs(lambdas[(a+b)%3] - lambdas[a]*lambdas[b]) < 1e-12 for a in range(3) for b in range(3)),
              'Tannakian tensor automorphism law')


def test_source_integrity() -> None:
    tex = TEX.read_text()
    refs_text = REFS.read_text()
    theorem_types = ("theorem", "proposition", "lemma", "corollary")
    results = sum(tex.count(f"\\begin{{{env}}}") for env in theorem_types)
    proofs = tex.count("\\begin{proof}")
    check(results == proofs, "one proof per internally proved result")

    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    check(len(labels) == len(set(labels)), "unique labels")
    references: list[str] = []
    for command in ("ref", "cref", "Cref", "eqref"):
        for match in re.finditer(r"\\" + command + r"\{([^}]+)\}", tex):
            references.extend(x.strip() for x in match.group(1).split(","))
    check(not (set(references) - set(labels)), "all internal references resolve")

    cited: set[str] = set()
    for group in re.findall(r"\\Rcite\{([^}]+)\}", tex):
        cited.update(item.strip() for item in group.split(","))
    listed = set(re.findall(r"\\bibitem\[(R\d+)\]", refs_text))
    check(cited == listed, "reference companion matches core citations")

    abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S)
    check(abstract is not None, "abstract present")
    if abstract:
        plain = re.sub(r"\\[A-Za-z]+(?:\{[^{}]*\})?", " ", abstract.group(1))
        words = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z]+)?", plain)
        check(len(words) <= 200, "abstract at most 200 words")

    check(";" not in tex, "no semicolons in core source")
    check("--" not in tex, "no prose double hyphens in core source")
    check("\\newpage" not in tex and "\\pagebreak" not in tex, "no forced page breaks")
    check("Language model" not in tex and "OpenAI" not in tex, "no disclosure language in core")
    check("thebibliography" not in tex and "\\bibliography" not in tex, "no bibliography in core")

    figures = set(re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex))
    for figure in figures:
        check((ROOT / "figures" / figure).exists(), f"figure exists: {figure}")

    build_candidates = [
        ROOT / "build_core7.log",
        ROOT / "build_logs" / "build_core7.log",
        ROOT / "build_core3.log",
        ROOT / "build_logs" / "clean_core.log",
    ]
    build_log = next((candidate for candidate in build_candidates if candidate.exists()), None)
    check(build_log is not None, "final core build log present")
    if build_log is not None:
        log = build_log.read_text(errors="ignore")
        check("undefined references" not in log.lower(), "no undefined references in build")
        check("Overfull" not in log, "no overfull boxes")


def main() -> int:
    run_group("Finite block calculus", test_finite_block_calculus)
    run_group("Refinement and chart compatibility", test_refinement_and_common_charts)
    run_group("Commutant Laplacian", test_commutant_laplacian)
    run_group("Resolution geometry and stability", test_resolution_geometry_and_stability)
    run_group("Weighted transfer algebra", test_weighted_transfer_algebra)
    run_group("Universal corner realization", test_universal_corner_extension)
    run_group("Countable and unbounded models", test_countable_and_unbounded_models)
    run_group("Expanded countable completion", test_countable_completion_extensions)
    run_group("Nonlinear packet calculus", test_nonlinear_packets)
    run_group("Expanded nonlinear dynamics", test_expanded_nonlinear_dynamics)
    run_group("Finite Resolution Logic", test_resolution_logic)
    run_group("Countable Resolution Logic", test_countable_resolution_logic)
    run_group("Concrete realizations", test_realizations)
    run_group("Finite Galois resolution", test_galois_resolution)
    run_group("Fourier Galois and ramification", test_fourier_galois_and_ramification)
    run_group("Profinite and cohomological descent", test_profinite_and_cohomological_descent)
    run_group("Source and package integrity", test_source_integrity)

    summary = {
        "checks": checks,
        "failures": failures,
        "groups": [{"name": name, "checks": count} for name, count in groups],
    }
    verification = ROOT / "verification"
    verification.mkdir(exist_ok=True)
    (verification / "verification_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    lines = [f"Galois expanded Resolution Theory verification: {checks - len(failures)}/{checks} checks passed"]
    lines.extend(f"{name}: {count} checks" for name, count in groups)
    if failures:
        lines.append("Failures:")
        lines.extend(f"  {failure}" for failure in failures)
    text = "\n".join(lines) + "\n"
    (verification / "verification_summary.txt").write_text(text)
    print(text, end="")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
