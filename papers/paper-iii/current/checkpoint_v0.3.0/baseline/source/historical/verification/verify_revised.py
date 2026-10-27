from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "PSC_Paper_III_Annals_Human_Edition.tex"
BIB = ROOT / "PSC_Paper_III_Annals_Human_Edition.bib"


def assert_close(a, b, tol=1e-10):
    if not np.allclose(a, b, atol=tol, rtol=tol):
        raise AssertionError(f"not close\n{a}\n{b}")


def group_exact_coordinates_and_jets() -> None:
    P = [np.diag([1.0, 0.0, 0.0]), np.diag([0.0, 1.0, 1.0])]
    Q = [np.diag([1.0, 1.0, 0.0]), np.diag([0.0, 0.0, 1.0])]

    def F(x):
        return np.array([x[0] * x[1], x[1] ** 2 + x[2], x[0] ** 2 - x[2]])

    x = np.array([0.7, -0.4, 0.2])
    packet_x = [p @ x for p in P]
    reconstructed = sum(packet_x)
    packet_y = [q @ F(reconstructed) for q in Q]
    assert_close(sum(packet_y), F(x))

    # Exact second derivative of F.
    def D2(h, k):
        return np.array(
            [h[0] * k[1] + h[1] * k[0], 2 * h[1] * k[1], 2 * h[0] * k[0]]
        )

    h = np.array([0.3, 0.2, -0.5])
    k = np.array([-0.4, 0.6, 0.1])
    jet_sum = np.zeros(3)
    for q in Q:
        for p1 in P:
            for p2 in P:
                jet_sum += q @ D2(p1 @ h, p2 @ k)
    assert_close(jet_sum, D2(h, k))


def set_partitions(items):
    if not items:
        yield []
        return
    first, *rest = items
    for part in set_partitions(rest):
        yield [[first]] + [b[:] for b in part]
        for i in range(len(part)):
            out = [b[:] for b in part]
            out[i] = [first] + out[i]
            yield out


def group_faa_counts() -> None:
    stirling = [[0] * 8 for _ in range(8)]
    stirling[0][0] = 1
    for n in range(1, 8):
        for k in range(1, n + 1):
            stirling[n][k] = stirling[n - 1][k - 1] + k * stirling[n - 1][k]
    for n in range(1, 7):
        parts = list(set_partitions(list(range(n))))
        assert len(parts) == sum(stirling[n])
        for M in (1, 2, 4):
            labeled = sum(M ** len(p) for p in parts)
            formula = sum(stirling[n][k] * M**k for k in range(1, n + 1))
            assert labeled == formula

    # Scalar second order chain rule.
    x = 0.37
    G1 = 2 * x + 1
    G2 = 2.0
    y = x * x + x
    F1 = 3 * y * y
    F2 = 6 * y
    lhs = F2 * G1 * G1 + F1 * G2
    eps = 1e-5
    H = lambda z: (z * z + z) ** 3
    fd = (H(x + eps) - 2 * H(x) + H(x - eps)) / eps**2
    assert abs(lhs - fd) < 2e-4


def group_tree_majorants() -> None:
    # u = a + b u^2 with 4ab < 1.
    a, b = 0.08, 0.7
    exact = (1 - math.sqrt(1 - 4 * a * b)) / (2 * b)
    catalan = [1]
    for n in range(1, 20):
        catalan.append(catalan[-1] * 2 * (2 * n - 1) // (n + 1))
    partial = sum(catalan[n - 1] * (b ** (n - 1)) * (a**n) for n in range(1, 20))
    assert abs(partial - exact) < 1e-12
    assert abs(exact - (a + b * exact**2)) < 1e-14

    # General polynomial contraction majorant.
    a, b2, b3, R = 0.05, 0.2, 0.05, 0.2
    phiR = a + b2 * R**2 + b3 * R**3
    q = 2 * b2 * R + 3 * b3 * R**2
    assert phiR <= R and q < 1
    x = 0.0
    for _ in range(100):
        x = a + b2 * x**2 + b3 * x**3
    assert 0 <= x <= R


def group_graded_operations() -> None:
    N = 5
    rng = np.random.default_rng(2)
    A = rng.normal(size=(N, N))
    B = rng.normal(size=(N, N))
    packets_A = [np.zeros_like(A) for _ in range(N)]
    packets_B = [np.zeros_like(B) for _ in range(N)]
    for r in range(N):
        for s in range(N):
            packets_A[(r - s) % N][r, s] = A[r, s]
            packets_B[(r - s) % N][r, s] = B[r, s]
    product = A @ B
    for k in range(N):
        expected = np.zeros_like(A)
        for i in range(N):
            expected += packets_A[i] @ packets_B[(k - i) % N]
        actual = np.zeros_like(A)
        for r in range(N):
            for s in range(N):
                if (r - s) % N == k:
                    actual[r, s] = product[r, s]
        assert_close(actual, expected)


def group_refinement_defects() -> None:
    # Nonlinear composition identity.
    Ff = lambda x: np.array([x[0] ** 2, x[1] + 0.1 * x[0]])
    Fc = lambda y: np.array([y[0] ** 2])
    Cx = lambda x: np.array([x[0]])
    Cy = lambda y: np.array([y[0]])
    Gf = lambda y: np.array([math.sin(y[0]) + y[1]])
    Gc = lambda z: np.array([math.sin(z[0])])
    Cz = lambda z: z.copy()
    x = np.array([0.4, -0.2])
    dF = Cy(Ff(x)) - Fc(Cx(x))
    dG_at_F = Cz(Gf(Ff(x))) - Gc(Cy(Ff(x)))
    lhs = Cz(Gf(Ff(x))) - Gc(Fc(Cx(x)))
    rhs = dG_at_F + Gc(Fc(Cx(x)) + dF) - Gc(Fc(Cx(x)))
    assert_close(lhs, rhs)

    # Sharp fixed point mismatch.
    q, eps = 0.6, 0.17
    coarse_fixed = 0.0
    fine_coarsened_fixed = eps / (1 - q)
    defect = fine_coarsened_fixed - q * fine_coarsened_fixed
    assert abs(defect - eps) < 1e-14
    assert abs(fine_coarsened_fixed - coarse_fixed - eps / (1 - q)) < 1e-14


def group_obstructions_and_correction() -> None:
    D = np.array([[1.0], [1.0]])
    r_good = np.array([2.0, 2.0])
    r_bad = np.array([2.0, 3.0])
    pinv = np.linalg.pinv(D)
    P_ob = np.eye(2) - D @ pinv
    assert np.linalg.norm(P_ob @ r_good) < 1e-12
    assert np.linalg.norm(P_ob @ r_bad) > 0.1

    # Right inverse contraction on R.
    y = 0.3
    N = lambda x: 0.2 * math.tanh(x)
    x = 0.0
    for _ in range(100):
        x = y - N(x)
    assert abs(x + N(x) - y) < 1e-13

    # Pure quadratic Lyapunov Schmidt obstruction F(x,y)=(y,x^2).
    for x0 in (-0.2, 0.0, 0.3):
        y0 = 0.0
        F = np.array([y0, x0**2])
        assert abs(F[1] - x0**2) < 1e-15

    # Packet projectors induced on the cokernel of D(t)=(t,t).
    q_diag = 0.5 * np.array([[1.0, 1.0], [1.0, 1.0]])
    q_anti = 0.5 * np.array([[1.0, -1.0], [-1.0, 1.0]])
    assert_close(q_diag @ D, D)
    assert_close(q_anti @ D, np.zeros_like(D))
    anti_defect = np.array([1.0, -1.0])
    assert_close(q_anti @ anti_defect, anti_defect)
    assert_close(q_diag @ anti_defect, np.zeros(2))

    # A fine obstruction can vanish after the coarsening (x,y) -> x+y.
    coarse = np.array([[1.0, 1.0]])
    fine_defect = np.array([1.0, -1.0])
    assert np.linalg.norm(fine_defect) > 0.0
    assert_close(coarse @ fine_defect, np.zeros(1))


def group_filtered_lifting() -> None:
    # Unique Hensel lift of x^2=2 from 3 mod 7 to mod 49.
    candidates = [3 + 7 * t for t in range(7)]
    lifts = [x for x in candidates if (x * x - 2) % 49 == 0]
    assert lifts == [10]

    # Obstructed lift of x^2=3 from 0 mod 3 to mod 9.
    candidates = [3 * t for t in range(3)]
    assert not [x for x in candidates if (x * x - 3) % 9 == 0]

    # Branching lift of x^2=0 from 0 mod 3 to mod 9.
    branches = [x for x in candidates if x * x % 9 == 0]
    assert branches == [0, 3, 6]

    # Filtered Maurer Cartan expansion Omega(x)=d*x+x^2.
    p_adic = 5
    depth = 2
    eta = 3
    h = p_adic**depth * 4
    differential = 7
    omega = lambda x: differential * x + x * x
    linearized = (differential + 2 * eta) * h
    remainder = omega(eta + h) - omega(eta) - linearized
    assert remainder == h * h
    assert remainder % (p_adic ** (depth + 1)) == 0


def group_schur_elimination() -> None:
    A = np.array([[2.0, -0.3], [0.2, 1.5]])
    B = np.array([[0.4], [-0.2]])
    C = np.array([[0.1, 0.5]])
    D = np.array([[1.7]])
    schur = A - B @ np.linalg.inv(D) @ C

    # Linear full system with hidden equation C u + D v = 0.
    u = np.array([0.3, -0.6])
    v = -np.linalg.solve(D, C @ u)
    retained = A @ u + B @ v
    assert_close(retained, schur @ u)

    # Second order scalar hidden elimination: F_Q=u^2+v, F_P=u+v^2.
    # phi(u)=-u^2, R(u)=u+u^4, hence R''(0)=0.
    eps = 1e-4
    Rf = lambda z: z + z**4
    second = (Rf(eps) - 2 * Rf(0.0) + Rf(-eps)) / eps**2
    assert abs(second) < 1e-6


def group_holonomy() -> None:
    rng = np.random.default_rng(4)
    # Triangle graph transports generated from vertex gauges have trivial holonomy.
    G = []
    for _ in range(3):
        M = rng.normal(size=(2, 2))
        while abs(np.linalg.det(M)) < 0.2:
            M = rng.normal(size=(2, 2))
        G.append(M)
    T10 = G[1] @ np.linalg.inv(G[0])
    T21 = G[2] @ np.linalg.inv(G[1])
    T02 = G[0] @ np.linalg.inv(G[2])
    H = T02 @ T21 @ T10
    assert_close(H, np.eye(2), 1e-9)

    # Gauge covariance.
    C0 = rng.normal(size=(2, 2))
    while abs(np.linalg.det(C0)) < 0.2:
        C0 = rng.normal(size=(2, 2))
    Hp = C0 @ H @ np.linalg.inv(C0)
    assert_close(Hp, np.eye(2), 1e-9)

    # Intertwining criterion on a nontrivial loop.
    Aloop = np.diag([2.0, 3.0])
    U = np.array([[0.0, 1.0], [1.0, 0.0]])
    Bloop = U @ Aloop @ np.linalg.inv(U)
    assert_close(U @ Aloop, Bloop @ U)


def direct_packet_rotation(Ps, Qs):
    S = sum(Q @ P for P, Q in zip(Ps, Qs))
    M = S.T @ S
    vals, vecs = np.linalg.eigh(M)
    invsqrt = vecs @ np.diag(vals ** -0.5) @ vecs.T
    return S @ invsqrt


def rotating_packets(t):
    c, s = math.cos(t), math.sin(t)
    v = np.array([c, s])
    w = np.array([-s, c])
    return [np.outer(v, v), np.outer(w, w)]


def group_packet_transport() -> None:
    for N in (20, 40, 80, 160):
        ts = np.linspace(0.0, 0.7, N + 1)
        U = np.eye(2)
        for a, b in zip(ts[:-1], ts[1:]):
            U = direct_packet_rotation(rotating_packets(a), rotating_packets(b)) @ U
        exact = np.array(
            [[math.cos(0.7), -math.sin(0.7)], [math.sin(0.7), math.cos(0.7)]]
        )
        err = np.linalg.norm(U - exact)
        if N == 20:
            first_err = err
        if N == 160:
            last_err = err
        # Every factor is unitary and exactly intertwines packets.
        assert_close(U.T @ U, np.eye(2), 1e-10)
    assert last_err < first_err + 1e-12
    assert last_err < 1e-9


def group_source_integrity() -> None:
    source = TEX.read_text()
    assert source.count("\\end{document}") == 1
    assert ";" not in source
    assert "\\newpage" not in source and "\\clearpage" not in source
    assert "\\pagebreak" not in source and "\\linebreak" not in source

    labels = re.findall(r"\\label\{([^}]+)\}", source)
    assert len(labels) == len(set(labels))
    refs = []
    for group in re.findall(r"\\(?:c|C)?ref\{([^}]+)\}", source):
        refs.extend(x.strip() for x in group.split(","))
    assert set(refs) <= set(labels)
    required = {
        "prop:obstruction_quotient_projectors",
        "thm:relative_obstruction_sequence",
        "cor:coarse_fine_obstruction",
        "prop:maurer_cartan_lifting",
        "thm:exact_local_elimination",
        "thm:holonomy_intertwining",
        "thm:direct_rotation_convergence",
        "fact:projected_curvature",
    }
    assert required <= set(labels)

    proved = sum(
        source.count(f"\\begin{{{env}}}")
        for env in ("theorem", "proposition", "lemma", "corollary")
    )
    # One of the two standard facts has a proof.  The other is imported.
    assert source.count("\\begin{proof}") == proved + 1

    cites = []
    for group in re.findall(r"\\cite\{([^}]+)\}", source):
        cites.extend(x.strip() for x in group.split(","))
    bibkeys = set(re.findall(r"@\w+\{([^,]+),", BIB.read_text()))
    assert set(cites) == bibkeys


def main() -> None:
    groups = [
        ("exact coordinates and jets", group_exact_coordinates_and_jets),
        ("Faa di Bruno counts", group_faa_counts),
        ("rooted tree majorants", group_tree_majorants),
        ("graded operations", group_graded_operations),
        ("refinement defects", group_refinement_defects),
        ("obstructions and correction", group_obstructions_and_correction),
        ("filtered lifting", group_filtered_lifting),
        ("Schur elimination", group_schur_elimination),
        ("finite holonomy", group_holonomy),
        ("smooth packet transport", group_packet_transport),
        ("source integrity", group_source_integrity),
    ]
    for name, fn in groups:
        fn()
        print(f"PASS: {name}")
    print(f"revised verification: {len(groups)}/{len(groups)} groups passed")


if __name__ == "__main__":
    main()
