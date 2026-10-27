"""Exact, finite models used by the Paper III monograph figures.

Run with Python 3 and SymPy.  These checks verify only the displayed finite
models and identities; they are not a proof of the manuscript's general
theorems.  Figure geometry uses floats only after these exact checks pass.
"""
from __future__ import annotations

from fractions import Fraction
import importlib
import json
from pathlib import Path
import sys

try:
    import sympy as sp
except ImportError:
    # Optional previously cached dependencies; no installation or download.
    cached = Path('/workspace/scratch/de82c13900d1/special_work/verification_dependencies')
    if cached.is_dir():
        sys.path.insert(0, str(cached))
    sp = importlib.import_module('sympy')

DATA = {
    'scope': 'Illustrative exact finite models, not universal proof certificates.',
    'conventions': {
        'edge_matrix': 'target row, source column; products execute rightmost first',
        'jets': 'ordered input slots; Hessian entries are derivative responses',
        'correction': 'L u = -d; standard Euclidean inner product',
        'rotation': 'column vectors; counterclockwise R(theta); P and I-P are both retained',
    },
    'typed_edges': {'vertices': [0, 1, 2, 3], 'word': [[0, 1], [1, 2], [2, 3]],
                    'broken_pair': [[0, 1], [2, 3]]},
    'holonomy_blocks': {'packet_count': 4, 'highlight': {'output': 1, 'input': 3},
                        'highlight_interpretation': 'conditional nonzero mixing witness'},
    'packet_jets': {'map': ['x+x*y', 'y+x**2'], 'basepoint': [0, 0],
                    'DF': [[1, 0], [0, 1]],
                    'H1': [[0, 1], [1, 0]], 'H2': [[2, 0], [0, 0]],
                    'ordered_nonzero_second_jets': [[1, 'x', 'y', 1], [1, 'y', 'x', 1],
                                                    [2, 'x', 'x', 2]]},
    'correction_plane': {'L': [[1, 0], [0, 0]], 'defect': [2, 3],
                         'correctable_part': [2, 0], 'cokernel_representative': [0, 3],
                         'correction': [-2, 0], 'detector': [0, 1], 'detector_value': 3},
    'rotating_projector': {'u': ['cos(theta)', 'sin(theta)'],
                           'interval': ['0', 'pi/3'], 'generator': [[0, -1], [1, 0]],
                           'meshes': [2, 4, 8], 'nearby_condition': 'abs(delta)<pi/2',
                           'polar_factor': 'R(delta)', 'product': 'R(pi/3)'},
}


def simplify_matrix(M):
    return M.applyfunc(lambda v: sp.trigsimp(sp.trigsimp(sp.expand_trig(v)), method='fu'))


def rotation(t):
    return sp.Matrix([[sp.cos(t), -sp.sin(t)], [sp.sin(t), sp.cos(t)]])


def projector(t):
    u = sp.Matrix([sp.cos(t), sp.sin(t)])
    return u * u.T


def exact_checks():
    checks = []

    def check(name, statement, condition):
        if condition is not True:
            raise AssertionError(f'{name}: {condition!r}')
        checks.append({'name': name, 'statement': statement, 'status': 'pass', 'arithmetic': 'exact'})

    # Noncommuting formal coefficients preserve the manuscript's word order.
    c1, c2, c3 = sp.symbols('c1 c2 c3', commutative=False)
    def edge(source, target, c):
        M = sp.zeros(4)
        M[target, source] = c
        return M
    E1, E2, E3 = edge(0, 1, c1), edge(1, 2, c2), edge(2, 3, c3)
    check('typed-composable-support', 'E3 E2 E1 has only (row 3,column 0)=c3 c2 c1',
          E3 * E2 * E1 == edge(0, 3, c3 * c2 * c1))
    check('typed-broken-interface', '(2→3) after (0→1) vanishes', E3 * E1 == sp.zeros(4))

    # An exact representative of canonical coordinate cancellation.
    A = [sp.eye(2), sp.Matrix([[1, 1], [0, 1]]), sp.Matrix([[1, 0], [1, 1]])]
    Jba, Jcb, Jac = A[1] * A[0].inv(), A[2] * A[1].inv(), A[0] * A[2].inv()
    check('canonical-coordinate-loop', 'J(a←c) J(c←b) J(b←a)=I', Jac * Jcb * Jba == sp.eye(2))

    M = sp.Matrix(4, 4, sp.symbols('m0:16'))
    packet = [sp.diag(*[int(i == j) for j in range(4)]) for i in range(4)]
    reconstruction = sum((P * M * Q for P in packet for Q in packet), sp.zeros(4))
    check('complete-two-sided-blocks', 'sum_mu,nu P_mu M P_nu=M for a general 4×4 matrix', reconstruction == M)
    check('highlight-support', 'P1 M P3 has only target row1/source column3',
          packet[1] * M * packet[3] == edge(3, 1, M[1, 3]))

    x, y = sp.symbols('x y')
    F = sp.Matrix([x + x * y, y + x**2])
    at0 = {x: 0, y: 0}
    check('first-jet', 'DF(0)=I', F.jacobian([x, y]).subs(at0) == sp.eye(2))
    H1, H2 = [sp.hessian(f, [x, y]).subs(at0) for f in F]
    check('second-jet-output1', 'H1=[[0,1],[1,0]]', H1 == sp.Matrix(DATA['packet_jets']['H1']))
    check('second-jet-output2', 'H2=[[2,0],[0,0]]', H2 == sp.Matrix(DATA['packet_jets']['H2']))
    h = sp.Matrix([x, y])
    quadratic = sp.Matrix([(h.T * H1 * h)[0], (h.T * H2 * h)[0]]) / 2
    check('exact-packet-taylor', 'F(h)=h+1/2 D²F(0)[h,h], including both ordered mixed slots',
          sp.simplify(F - h - quadratic) == sp.zeros(2, 1))
    check('no-higher-jets', 'All order3 partial derivatives of both degree2 outputs vanish',
          all(sp.diff(f, x, k, y, 3-k) == 0 for f in F for k in range(4)))

    L = [[Fraction(v) for v in row] for row in DATA['correction_plane']['L']]
    d = list(map(Fraction, [2, 3]))
    u = list(map(Fraction, [-2, 0]))
    Lu = [sum(row[j] * u[j] for j in range(2)) for row in L]
    residual = [d[i] + Lu[i] for i in range(2)]
    check('correction-residual', 'L(-2,0)=(-2,0); d+Lu=(0,3)', residual == [Fraction(0), Fraction(3)])
    check('scalar-cokernel-detector', 'ell(x,y)=y annihilates im L and ell(d)=3',
          all(L[1][j] == 0 for j in range(2)) and d[1] == 3)

    t, delta = sp.symbols('theta delta', real=True)
    P, Q = projector(t), sp.eye(2) - projector(t)
    check('orthogonal-complete-packets', 'P²=P=Pᵀ, Q²=Q=Qᵀ, PQ=0, P+Q=I',
          simplify_matrix(P * P - P) == sp.zeros(2) and P == P.T and
          simplify_matrix(Q * Q - Q) == sp.zeros(2) and Q == Q.T and
          simplify_matrix(P * Q) == sp.zeros(2) and P + Q == sp.eye(2))
    K = sp.Matrix([[0, -1], [1, 0]])
    check('rotation-generator', "[P',P]=P'P+Q'Q=K=[[0,-1],[1,0]]",
          simplify_matrix(P.diff(t) * P - P * P.diff(t)) == K and
          simplify_matrix(P.diff(t) * P + Q.diff(t) * Q) == K)
    R = rotation(t)
    check('continuous-transport', "R'=KR, R(0)=I, P(t)R(t)=R(t)P(0)",
          simplify_matrix(R.diff(t) - K * R) == sp.zeros(2) and R.subs(t, 0) == sp.eye(2) and
          simplify_matrix(P * R - R * projector(0)) == sp.zeros(2))
    Pnew, Qnew = projector(t + delta), sp.eye(2) - projector(t + delta)
    S = simplify_matrix(Pnew * P + Qnew * Q)
    check('polar-input', 'S(P(theta+delta),P(theta))=cos(delta) R(delta)',
          simplify_matrix(S - sp.cos(delta) * rotation(delta)) == sp.zeros(2))
    check('polar-normalization', 'SᵀS=cos²(delta) I; for abs(delta)<pi/2, polar(S)=R(delta)',
          simplify_matrix(S.T * S - sp.cos(delta)**2 * sp.eye(2)) == sp.zeros(2) and
          simplify_matrix(S / sp.cos(delta) - rotation(delta)) == sp.zeros(2))
    for n in DATA['rotating_projector']['meshes']:
        step = sp.pi / (3*n)
        check(f'mesh-{n}', f'{n} factors R(pi/{3*n}) give R(pi/3) exactly',
              simplify_matrix(rotation(step)**n - rotation(sp.pi/3)) == sp.zeros(2))
    return checks


if __name__ == '__main__':
    print(json.dumps({'model_data': DATA, 'checks': exact_checks(), 'sympy': sp.__version__}, indent=2))
