from __future__ import annotations

from fractions import Fraction
from itertools import product
from pathlib import Path
import re

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


def assert_matrix_equal(a: sp.Matrix, b: sp.Matrix, message: str) -> None:
    if a != b:
        raise AssertionError(f"{message}\n{a}\n!=\n{b}")


def test_refinement_and_blocks() -> None:
    n = 4
    q = []
    for i in range(n):
        m = sp.zeros(n)
        m[i, i] = 1
        q.append(m)
    p = [q[0] + q[1], q[2] + q[3]]
    assert sum(q, sp.zeros(n)) == sp.eye(n)
    assert sum(p, sp.zeros(n)) == sp.eye(n)
    t = sp.Matrix([[2, 1, 3, 0], [4, 5, 0, 1], [1, 0, 7, 2], [0, 3, 4, 6]])
    for b in range(2):
        for a in range(2):
            fine = sp.zeros(n)
            for beta in range(2 * b, 2 * b + 2):
                for alpha in range(2 * a, 2 * a + 2):
                    fine += q[beta] * t * q[alpha]
            assert_matrix_equal(p[b] * t * p[a], fine, "block refinement failed")


def test_common_refinement() -> None:
    n = 4
    e = []
    for i in range(n):
        m = sp.zeros(n)
        m[i, i] = 1
        e.append(m)
    p = [e[0] + e[1], e[2] + e[3]]
    q = [e[0] + e[2], e[1] + e[3]]
    products = [a * b for a in p for b in q if a * b != sp.zeros(n)]
    assert len(products) == 4
    assert sum(products, sp.zeros(n)) == sp.eye(n)
    for i, a in enumerate(products):
        assert a * a == a
        for j, b in enumerate(products):
            if i != j:
                assert a * b == sp.zeros(n)


def residue_packet(values: list[int], modulus: int, residue: int) -> list[int]:
    return [x if i % modulus == residue else 0 for i, x in enumerate(values)]


def test_residue_refinement_and_crt() -> None:
    values = list(range(36))
    coarse = residue_packet(values, 3, 1)
    fine = [0] * len(values)
    for s in [1, 4, 7, 10]:
        part = residue_packet(values, 12, s)
        fine = [a + b for a, b in zip(fine, part)]
    assert coarse == fine
    p12 = residue_packet(values, 12, 7)
    p4 = residue_packet(values, 4, 3)
    p3 = residue_packet(values, 3, 1)
    product_packet = [a if b else 0 for a, b in zip(p4, [x != 0 or i == 0 for i, x in enumerate(p3)])]
    # Direct support comparison avoids the zero coefficient at index zero.
    assert [i for i, x in enumerate(p12) if x or i == 7] == [i for i in range(len(values)) if i % 4 == 3 and i % 3 == 1]


def inv_mod_matrix(m: sp.Matrix, modulus: int) -> sp.Matrix:
    return m.inv_mod(modulus)


def test_weighted_inverse() -> None:
    p = 3
    level = 6
    modulus = p**level
    d = sp.diag(1, 2, 1)
    n = sp.Matrix([[0, 3, 0], [0, 0, 9], [27, 0, 0]])
    t = d + n
    d_inv = inv_mod_matrix(d, modulus)
    a = (d_inv * n).applyfunc(lambda x: int(x) % modulus)
    total = sp.eye(3)
    power = sp.eye(3)
    sign = -1
    for _ in range(40):
        power = (power * a).applyfunc(lambda x: int(x) % modulus)
        if power == sp.zeros(3):
            break
        total = (total + sign * power).applyfunc(lambda x: int(x) % modulus)
        sign *= -1
    candidate = (total * d_inv).applyfunc(lambda x: int(x) % modulus)
    direct = inv_mod_matrix(t, modulus).applyfunc(lambda x: int(x) % modulus)
    assert_matrix_equal(candidate, direct, "weighted inverse failed")


def test_transfer_series() -> None:
    t = sp.symbols("t")
    a = sp.Matrix([[0, t, 0], [0, t**2, t], [0, 0, 0]])
    z = (sp.Matrix([[1, 0, 0]]) * (sp.eye(3) - a).inv() * sp.Matrix([0, 0, 1]))[0]
    assert sp.simplify(z - t**2 / (1 - t**2)) == 0


def test_gluing_smith_weight() -> None:
    pi = 2
    s = 3
    # Columns are a basis of the split sublattice in the basis of Lambda_s.
    inclusion = sp.Matrix([[1, -1], [0, pi**s]])
    form = smith_normal_form(inclusion, domain=ZZ)
    diagonal = [abs(int(form[i, i])) for i in range(2)]
    assert diagonal == [1, pi**s]
    assert max(sp.factorint(x).get(pi, 0) for x in diagonal) == s
    # The split lattice has weight zero even with the same rational eigenvalues.
    split = smith_normal_form(sp.eye(2), domain=ZZ)
    assert list(split.diagonal()) == [1, 1]


def test_precision_delay() -> None:
    s = 2
    m = 3
    # Matrix of the projector E in the Lambda_s basis.
    e = [[Fraction(1), Fraction(1, 2**s)], [Fraction(0), Fraction(0)]]
    # Sufficiency for all differences divisible by 2^(m+s) on a small box.
    for a, b in product(range(-2, 3), repeat=2):
        z = [a, b]
        diff = [2 ** (m + s) * z[0], 2 ** (m + s) * z[1]]
        out0 = e[0][0] * diff[0] + e[0][1] * diff[1]
        out1 = e[1][0] * diff[0] + e[1][1] * diff[1]
        assert out0.denominator == 1 and out1.denominator == 1
        assert int(out0) % (2**m) == 0 and int(out1) % (2**m) == 0
    # One fewer digit fails using z=(0,1).
    d = s - 1
    diff = [0, 2 ** (m + d)]
    out0 = e[0][1] * diff[1]
    assert out0.denominator == 1
    assert int(out0) % (2**m) != 0


def test_smith_congruence_count() -> None:
    modulus = 8
    weights = [0, 1, 2]
    b = [1, 2, 4]
    count = 0
    for x in product(range(modulus), repeat=3):
        if all((2**weights[i] * x[i] - b[i]) % modulus == 0 for i in range(3)):
            count += 1
    assert count == 2 ** sum(min(s, 3) for s in weights)
    bad = [1, 2, 2]
    assert not any(all((2**weights[i] * x[i] - bad[i]) % modulus == 0 for i in range(3)) for x in product(range(modulus), repeat=3))


def test_defect_identities() -> None:
    c = sp.Matrix([[1, 0]])
    tf = sp.Matrix([[2, 3], [5, 7]])
    tc = sp.Matrix([[2]])
    delta = c * tf - tc * c
    for n in range(1, 7):
        lhs = c * (tf**n) - (tc**n) * c
        rhs = sp.zeros(1, 2)
        for k in range(n):
            rhs += (tc ** (n - 1 - k)) * delta * (tf**k)
        assert_matrix_equal(lhs, rhs, "power defect failed")
    z = sp.Integer(11)
    lhs = c * (z * sp.eye(2) - tf).inv() - (z * sp.eye(1) - tc).inv() * c
    rhs = (z * sp.eye(1) - tc).inv() * delta * (z * sp.eye(2) - tf).inv()
    assert_matrix_equal(sp.simplify(lhs), sp.simplify(rhs), "resolvent defect failed")


def test_source_integrity() -> None:
    root = Path(__file__).resolve().parents[1]
    tex = (root / "PSC_Paper_II_Annals_Human_Edition.tex").read_text()
    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    if len(labels) != len(set(labels)):
        raise AssertionError("duplicate labels")
    refs = re.findall(r"\\(?:cref|ref)\{([^}]+)\}", tex)
    expanded = []
    for item in refs:
        expanded.extend(x.strip() for x in item.split(","))
    missing = sorted(set(expanded) - set(labels))
    if missing:
        raise AssertionError(f"missing labels: {missing}")
    proved = len(re.findall(r"\\begin\{(?:theorem|proposition|lemma|corollary)\}", tex))
    proofs = tex.count("\\begin{proof}")
    if proved != proofs:
        raise AssertionError(f"proved environments {proved} != proofs {proofs}")
    if ";" in tex:
        raise AssertionError("semicolon found in manuscript source")


def main() -> None:
    tests = [
        test_refinement_and_blocks,
        test_common_refinement,
        test_residue_refinement_and_crt,
        test_weighted_inverse,
        test_transfer_series,
        test_gluing_smith_weight,
        test_precision_delay,
        test_smith_congruence_count,
        test_defect_identities,
        test_source_integrity,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"revised verification: {len(tests)}/{len(tests)} groups passed")


if __name__ == "__main__":
    main()
