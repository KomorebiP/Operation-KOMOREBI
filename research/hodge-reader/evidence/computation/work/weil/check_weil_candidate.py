#!/usr/bin/env python3
"""Exact finite audit of a Q(i)-Weil sixfold model.

This verifies exterior-algebra and tangent-space assertions, not nonalgebraicity.
Arithmetic: Python integers/Fraction and SymPy exact rational arithmetic.
Basis: (x1,y1,...,x6,y6); complex orientation is minus this ordered basis.
Run: python check_weil_candidate.py --output results.json
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time
import sympy as sp

Number = int | Fraction
Poly = dict[int, Number]
NB = 12
TOP = (1 << NB) - 1
D = (1, 1, 1, -1, -1, -3)


def clean(p: Poly) -> Poly:
    return {m: c for m, c in p.items() if c}


def add(a: Poly, b: Poly, scalar: Number = 1) -> Poly:
    out = a.copy()
    for m, c in b.items():
        out[m] = out.get(m, 0) + scalar*c
    return clean(out)


def scale(a: Poly, scalar: Number) -> Poly:
    return clean({m: scalar*c for m, c in a.items()})


def sign(a: int, b: int) -> int:
    if a & b:
        return 0
    inversions = 0
    while a:
        bit = a & -a
        inversions += (b & (bit - 1)).bit_count()
        a -= bit
    return -1 if inversions % 2 else 1


def wedge(a: Poly, b: Poly) -> Poly:
    out: Poly = {}
    for m, c in a.items():
        for n, d in b.items():
            s = sign(m, n)
            if s:
                k = m | n
                out[k] = out.get(k, 0) + s*c*d
    return clean(out)


def power(a: Poly, n: int) -> Poly:
    out: Poly = {0: 1}
    for _ in range(n):
        out = wedge(out, a)
    return out


def pull_monomial(mask: int, images: list[Poly]) -> Poly:
    out: Poly = {0: 1}
    while mask:
        bit = mask & -mask
        out = wedge(out, images[bit.bit_length()-1])
        mask -= bit
    return out


def pull(poly: Poly, images: list[Poly]) -> Poly:
    out: Poly = {}
    for mask, c in poly.items():
        out = add(out, pull_monomial(mask, images), c)
    return out


def integral(poly: Poly) -> Number:
    # Three factors carry J=-I, so the complex orientation is negative.
    return -poly.get(TOP, 0)


def pairing(a: Poly, b: Poly) -> Number:
    return integral(wedge(a, b))


def determinant_parts(indices: tuple[int, ...]) -> tuple[Poly, Poly]:
    """Real/imaginary parts of wedge_j (x_j+i*y_j), indices zero-based."""
    real: Poly = {0: 1}
    imag: Poly = {}
    for j in indices:
        x, y = {1 << (2*j): 1}, {1 << (2*j+1): 1}
        real, imag = add(wedge(real, x), wedge(imag, y), -1), add(wedge(real, y), wedge(imag, x))
    return real, imag


def complex_wedge(a: tuple[Poly, Poly], b: tuple[Poly, Poly]) -> tuple[Poly, Poly]:
    return (add(wedge(a[0],b[0]), wedge(a[1],b[1]), -1),
            add(wedge(a[0],b[1]), wedge(a[1],b[0])))


def derivation(poly: Poly, matrix: sp.Matrix) -> Poly:
    """Induced Lie-algebra action on covectors/exterior forms, not pullback."""
    images: list[Poly] = []
    for row in range(matrix.rows):
        images.append({1 << col: Fraction(matrix[row,col])
                       for col in range(matrix.cols) if matrix[row,col]})
    out: Poly = {}
    for mask, coefficient in poly.items():
        positions = [i for i in range(matrix.rows) if mask & (1 << i)]
        for replaced in positions:
            term: Poly = {0: 1}
            for pos in positions:
                term = wedge(term, images[pos] if pos == replaced else {1 << pos: 1})
            out = add(out, term, coefficient)
    return out


def scalar_string(x: Number | sp.Expr) -> int | str:
    if isinstance(x, int):
        return x
    if isinstance(x, Fraction):
        return x.numerator if x.denominator == 1 else f"{x.numerator}/{x.denominator}"
    return str(x)


def matrix_to_real(m: sp.Matrix) -> sp.Matrix:
    out = sp.zeros(2*m.rows, 2*m.cols)
    for i in range(m.rows):
        for j in range(m.cols):
            a, b = sp.expand_complex(m[i, j]).as_real_imag()
            out[2*i:2*i+2, 2*j:2*j+2] = sp.Matrix([[a, -b], [b, a]])
    return out


def graph_tangent_report(weights: tuple[int, int, int]) -> dict:
    # Delta J=[[0,B],[M^-1 B^dagger,0]], where B is arbitrary complex 3x3.
    # L={(z,conjugate(z))}; Delta J(L) subset L iff B^t=M B.
    xs = sp.symbols('b0:9', real=True)
    ys = sp.symbols('c0:9', real=True)
    b = sp.Matrix(3, 3, lambda i, j: xs[3*i+j] + sp.I*ys[3*i+j])
    m = sp.diag(*weights)
    equations = []
    for z in b.T-m*b:
        equations += [sp.re(z), sp.im(z)]
    mat, rhs = sp.linear_eq_to_matrix(equations, (*xs, *ys))
    assert rhs == sp.zeros(rhs.rows, 1)
    real_rank = mat.rank()
    # Independent real-matrix check of the same condition.
    delta = sp.zeros(6)
    delta[:3, 3:] = b
    delta[3:, :3] = m.inv()*sp.conjugate(b.T)
    real_delta = matrix_to_real(delta)
    q = sp.zeros(12, 6)
    for j in range(3):
        q[2*j, 2*j] = 1
        q[2*j+1, 2*j+1] = 1
        q[2*(j+3), 2*j] = 1
        q[2*(j+3)+1, 2*j+1] = -1
    image = real_delta*q
    residuals = []
    for j in range(3):
        for k in range(6):
            residuals.append(image[2*(j+3), k]-image[2*j, k])
            residuals.append(image[2*(j+3)+1, k]+image[2*j+1, k])
    direct, _ = sp.linear_eq_to_matrix(residuals, (*xs, *ys))
    assert direct.rank() == real_rank
    assert sp.Matrix.vstack(mat, direct).rank() == real_rank
    return {
        'weights': list(weights),
        'ambient_real_tangent_dimension': 18,
        'constraint_real_rank': real_rank,
        'graph_preserving_real_tangent_dimension': 18-real_rank,
        'graph_preserving_complex_tangent_dimension': (18-real_rank)//2,
        'independent_real_matrix_check': True,
    }


def run() -> dict:
    start = time.perf_counter()
    theta = {3 << (2*j): D[j] for j in range(6)}
    u: Poly = {}
    v: Poly = {}
    for choices in range(1 << 6):
        k = choices.bit_count()
        mask = sum(1 << (2*j + ((choices >> j) & 1)) for j in range(6))
        if k % 2 == 0:
            u[mask] = (-1)**(k//2)
        else:
            v[mask] = (-1)**((k-1)//2)
    assert len(u) == len(v) == 32
    assert not wedge(theta, u) and not wedge(theta, v)
    t3 = power(theta, 3)
    gram = [[pairing(a, b) for b in (t3, u, v)] for a in (t3, u, v)]
    assert gram == [[2160, 0, 0], [0, -32, 0], [0, 0, -32]]
    # Orthogonal check: J0^2=-1; E J0 is positive definite and diagonal.
    E = sp.diag(*[sp.Matrix([[0, d], [-d, 0]]) for d in D])
    J0 = sp.diag(*[sp.Matrix([[0, -s], [s, 0]]) for s in (1,1,1,-1,-1,-1)])
    assert J0*J0 == -sp.eye(12)
    assert J0.T*E*J0 == E
    assert E*J0 == sp.diag(*[abs(d) for d in D for _ in range(2)])
    # Isogeny pullbacks a=2+i and conjugate(a)=2-i on H^1.
    plus: list[Poly] = []
    minus: list[Poly] = []
    for j in range(6):
        x, y = 1 << (2*j), 1 << (2*j+1)
        plus.extend([{x: 2, y: -1}, {x: 1, y: 2}])
        minus.extend([{x: 2, y: 1}, {x: -1, y: 2}])
    basis6 = [sum(1 << j for j in comb) for comb in combinations(range(12), 6)]
    assert len(basis6) == 924
    scol = {mask: add(pull_monomial(mask, plus), pull_monomial(mask, minus)) for mask in basis6}
    def S(poly: Poly) -> Poly:
        out: Poly = {}
        for mask, c in poly.items():
            out = add(out, scol[mask], c)
        return out
    denominator = (-234+70)*(-234-150)*(-234-250)
    assert denominator == -30480384
    def projector(poly: Poly) -> Poly:
        for shift in (70, -150, -250):
            poly = add(S(poly), poly, shift)
        return scale(poly, Fraction(1, denominator))
    assert S(u) == scale(u, -234)
    assert S(v) == scale(v, -234)
    assert S(t3) == scale(t3, 250)
    assert pull(u, plus) == add(scale(u, -117), scale(v, -44))
    assert pull(v, plus) == add(scale(u, 44), scale(v, -117))
    assert pull(t3, plus) == scale(t3, 125)
    assert projector(u) == u and projector(v) == v
    assert not projector(t3)
    anchor_u, anchor_v = next(iter(u)), next(iter(v))
    nonzero_columns = 0
    for mask in basis6:
        projected = projector({mask: 1})
        a = Fraction(projected.get(anchor_u, 0), u[anchor_u])
        b = Fraction(projected.get(anchor_v, 0), v[anchor_v])
        assert projected == add(scale(u, a), scale(v, b))
        orthogonal_formula = add(scale(u, Fraction(pairing({mask: 1}, u), -32)),
                                 scale(v, Fraction(pairing({mask: 1}, v), -32)))
        assert projected == orthogonal_formula
        nonzero_columns += bool(projected)
    # Invariance/eigenspace dimensions, checked separately by Gaussian arithmetic.
    counts = Counter()
    for r in range(7):
        lam = sp.expand((2+sp.I)**r*(2-sp.I)**(6-r))
        eigen = int(sp.simplify(lam+sp.conjugate(lam)))
        counts[eigen] += math.comb(6, r)**2
    assert dict(counts) == {-234: 2, -70: 72, 150: 450, 250: 400}
    # Explicit algebraic graph threefold Z at J0:
    # (z1,z2,z3,conjugate(z1),conjugate(z2),conjugate(z3)).
    graph_images: list[Poly] = []
    for j in range(6):
        a, b = 1 << (2*(j%3)), 1 << (2*(j%3)+1)
        graph_images.extend([{a: 1}, {b: 1 if j<3 else -1}])
    top_z = (1 << 6)-1
    periods = [pull(a, graph_images).get(top_z, 0) for a in (t3, u, v)]
    assert periods == [96, 0, -8]
    # Construct the Poincare dual from its integrals against all 924 basis forms.
    clz: Poly = {}
    for mask in basis6:
        value = pull_monomial(mask, graph_images).get(top_z, 0)
        if value:
            complement = TOP ^ mask
            clz[complement] = -sign(complement, mask)*value
    for mask in basis6:
        assert pairing(clz, {mask: 1}) == pull_monomial(mask, graph_images).get(top_z, 0)
    pz = projector(clz)
    assert pz == scale(v, Fraction(1, 4))
    # Pullback of 1+i supplies the other rational Weil direction.
    qimages: list[Poly] = []
    for j in range(6):
        x, y = 1 << (2*j), 1 << (2*j+1)
        qimages.extend([{x: 1, y: -1}, {x: 1, y: 1}])
    assert pull(u, qimages) == scale(v, 8)
    assert pull(v, qimages) == scale(u, -8)
    # Explicit rational nilpotent in the unitary Lie algebra.
    H = sp.diag(*D)
    N = sp.zeros(6)
    for j in (0, 1):
        N[j,j] = sp.I
        N[j,j+3] = -sp.I
        N[j+3,j] = sp.I
        N[j+3,j+3] = -sp.I
    assert N*N == sp.zeros(6)
    assert sp.conjugate(N.T)*H + H*N == sp.zeros(6)
    nr = matrix_to_real(N)
    assert N.rank() == 2 and nr.rank() == 4
    assert nr*nr == sp.zeros(12)
    assert nr.T*E+E*nr == sp.zeros(12)
    tangent_nonsplit = graph_tangent_report((1,1,3))
    tangent_split = graph_tangent_report((1,1,1))
    assert tangent_nonsplit['graph_preserving_complex_tangent_dimension'] == 3
    assert tangent_split['graph_preserving_complex_tangent_dimension'] == 6
    # Product replacement: C has indices (1,2,4,5), B has (3,6).
    cparts = determinant_parts((0,1,3,4))
    bparts = determinant_parts((2,5))
    assert complex_wedge(cparts,bparts) == (u,v)
    # The original pair decomposition has odd permutation sign.
    original = complex_wedge(complex_wedge(determinant_parts((0,3)),
                                            determinant_parts((1,4))),
                                            determinant_parts((2,5)))
    assert original == (scale(u,-1),scale(v,-1))
    # An alternative decomposition (1,6),(2,5),(3,4) has even sign.
    alternative_pairs = ((0,5),(1,4),(2,3))
    alternative = complex_wedge(complex_wedge(determinant_parts(alternative_pairs[0]),
                                               determinant_parts(alternative_pairs[1])),
                                               determinant_parts(alternative_pairs[2]))
    assert alternative == (u,v)
    # Full 18-real-dimensional tangent test for constancy of the Weil class.
    tangent_tests = 0
    mixed_report = None
    for row in range(3):
        for col in range(3):
            for entry in (sp.Integer(1), sp.I):
                bmat = sp.zeros(3)
                bmat[row,col] = entry
                delta = sp.zeros(6)
                delta[:3,3:] = bmat
                delta[3:,:3] = sp.diag(1,1,sp.Rational(1,3))*sp.conjugate(bmat.T)
                delta_real = matrix_to_real(delta)
                assert delta_real*J0+J0*delta_real == sp.zeros(12)
                assert delta_real.T*E+E*delta_real == sp.zeros(12)
                assert not derivation(u,delta_real)
                assert not derivation(v,delta_real)
                tangent_tests += 1
                if (row,col,entry)==(0,2,1):
                    assert derivation(bparts[0],delta_real)
                    assert derivation(bparts[1],delta_real)
                    assert derivation(cparts[0],delta_real)
                    assert derivation(cparts[1],delta_real)
                    for pair in alternative_pairs:
                        for form in determinant_parts(pair):
                            assert not derivation(form,delta_real)
                    # The generator X integrates the selected tangent: [X,J0]=Delta.
                    xgen = -sp.Rational(1,2)*delta_real*J0
                    assert xgen*J0-J0*xgen == delta_real
                    assert xgen.T*E+E*xgen == sp.zeros(12)
                    mixed_report = {
                        'selected_tangent': 'B_13=1; all other entries zero',
                        'old_B_surface_factor_loses_type_11_infinitesimally': True,
                        'old_C_factor_loses_type_22_infinitesimally': True,
                        'full_u_v_remain_type_33_infinitesimally': True,
                        'replacement_pairs_one_based': [[1,6],[2,5],[3,4]],
                        'replacement_divisor_factors_preserved_infinitesimally': True,
                        'integrating_generator': 'X=-(1/2) DeltaJ J0; J(t)=exp(tX) J0 exp(-tX)',
                        'pair_blocks_preserved_by_X': True,
                    }
    assert tangent_tests == 18 and mixed_report is not None
    # Low-precision modular illustration; the universal norm argument is descent,
    # not this finite check.
    mod3 = [(a,b) for a in range(3) for b in range(3) if (a*a+b*b)%3 == 0]
    assert mod3 == [(0,0)]
    return {
        'status': 'PASS: exact finite algebra and linearized graph-preservation assertions',
        'not_claimed': [
            'Nonalgebraicity of any rational Hodge class',
            'A Hodge counterexample',
            'An upper bound for deformation ranks of all algebraic cycles',
            'Construction of an algebraic semistable degeneration from N alone',
            'Lean verification or novelty of the identities',
        ],
        'arithmetic': 'integers, Fraction, exact SymPy QQ(i); no numerical tolerance',
        'basis_order': ['x1','y1','x2','y2','x3','y3','x4','y4','x5','y5','x6','y6'],
        'orientation': 'integral(x1 y1 ... x6 y6)=-1 for J0=(i,i,i,-i,-i,-i)',
        'polarization_weights': list(D),
        'riemann_seed_checks': True,
        'u_terms': len(u), 'v_terms': len(v),
        'theta_wedges_u_v_zero': True,
        'intersection_gram_basis_theta3_u_v': gram,
        'projector': {
            'S': '[2+i]^* + [2-i]^* on H^6',
            'polynomial': '(S+70)(S-150)(S-250)/(-30480384)',
            'eigenvalues_and_dimensions': {str(k): val for k, val in counts.items()},
            'full_rational_basis_tested': len(basis6),
            'nonzero_columns': nonzero_columns,
            'image_dimension': 2,
            'image_basis': ['u','v'],
            'orthogonal_projection_formula_checked_on_all_basis_vectors': True,
            'formula': 'P(c)=-(pairing(c,u)*u+pairing(c,v)*v)/32',
            'two_plus_i_eigenvalues_on_W': '-117+44i, -117-44i',
            'two_plus_i_eigenvalue_on_theta3': 125,
            'idempotence': 'Image contained in span(u,v), and both u and v fixed',
        },
        'seed_graph': {
            'periods_theta3_u_v': periods,
            'poincare_dual_terms': len(clz),
            'poincare_duality_basis_tests': len(basis6),
            'projected_class': 'v/4',
            'algebraic_seed_realizations': ['v=4 P_W cl(Z)', 'u=-(1/2)[1+i]^* P_W cl(Z)'],
            'one_plus_i_action': ['u -> 8v','v -> -8u'],
        },
        'graph_tangent_nonsplit': tangent_nonsplit,
        'graph_tangent_split_control': tangent_split,
        'nilpotent': {
            'square_zero': True, 'unitary_lie_algebra': True,
            'K_rank': int(N.rank()), 'Q_rank': int(nr.rank()),
            'defined_on_pairs': '(e1,e4) and (e2,e5)',
            'block_on_each_pair': 'i*[[1,-1],[1,-1]]',
            'residual_hermitian_plane': 'diag(1,-3)',
        },
        'factorization_checks': {
            'Omega6_equals_OmegaC_wedge_OmegaB': True,
            'u': 'c_R b_R - c_I b_I',
            'v': 'c_R b_I + c_I b_R',
            'C_complex_dimension': 4, 'B_complex_dimension': 2,
            'product_moduli_complex_dimension': 5,
            'full_weil_real_tangent_directions_tested': tangent_tests,
            'alternative_pair_factorization_verified': True,
            'selected_mixed_direction': mixed_report,
            'geometric_dependency': 'C Weil classes algebraic by a cited theorem; B Weil classes are divisor classes by Lefschetz (1,1)',
        },
        'mod3_solutions_x2_plus_y2_zero': mod3,
        'runtime_seconds': round(time.perf_counter()-start, 6),
        'environment': {'python': sys.version, 'sympy': sp.__version__, 'platform': platform.platform()},
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('results.json'))
    args = parser.parse_args()
    try:
        result = run()
    except Exception as exc:
        failure = {'status':'FAIL', 'exception':type(exc).__name__, 'message':str(exc)}
        args.output.write_text(json.dumps(failure, indent=2)+'\n')
        raise
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
