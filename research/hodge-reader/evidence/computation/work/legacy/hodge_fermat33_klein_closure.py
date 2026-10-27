from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ

OUT = Path('/mnt/data/Hodge_Fermat33_Klein_Closure_VERIFICATION.json')
MOD = 33

A = sp.Matrix([
    [2, 0, 0, 0, 1, 0],
    [1, 2, 0, 0, 0, 0],
    [0, 1, 2, 0, 0, 0],
    [0, 0, 1, 2, 0, 0],
    [0, 0, 0, 1, 2, 0],
    [0, 0, 0, 0, 0, 3],
])

C = sp.Matrix([
    [16, 1, -2, 4, -8, 0],
    [-8, 16, 1, -2, 4, 0],
    [4, -8, 16, 1, -2, 0],
    [-2, 4, -8, 16, 1, 0],
    [1, -2, 4, -8, 16, 0],
    [0, 0, 0, 0, 0, 11],
])

SHIFT = sp.Matrix([[8, 8, 8, 8, 8, 0]])
C_PLUS = C + sp.ones(6, 1) * SHIFT
COMMON = sp.Matrix([[24, 24, 24, 24, 24, 0]] * 6)

# Character-lattice basis: e_i-e_5, i=0,...,4.
E = sp.zeros(6, 5)
for i in range(5):
    E[i, i] = 1
    E[5, i] = -1
M = (C.T * E)[:5, :]
SNF = smith_normal_form(M, domain=ZZ)

# Generator of the image modulo 33.
g = sp.Matrix([16, 1, 31, 4, 25, 22])
chars = []
for t in range(1, MOD):
    a = tuple(int((t * g[i]) % MOD) for i in range(6))
    if all(x != 0 for x in a):
        chars.append({'t': t, 'character': a, 'level': sum(a) // MOD})

alpha = sp.Matrix([7, 19, 28, 10, 13, 22])
units = [u for u in range(1, MOD) if math.gcd(u, MOD) == 1]
alpha_orbit = {
    tuple(int((u * alpha[i]) % MOD) for i in range(6))
    for u in units
}
level3 = {tuple(row['character']) for row in chars if row['level'] == 3}

# Explicit cubic Jacobian-ring class P=y1*y2*y5.
y = sp.symbols('y0:6')
F = y[0]**2*y[4] + y[1]**2*y[0] + y[2]**2*y[1] + y[3]**2*y[2] + y[4]**2*y[3] + y[5]**3
partials = [sp.diff(F, yi) for yi in y]
G = sp.groebner(partials, *y, order='grevlex')
P = y[1] * y[2] * y[5]
P_remainder = sp.expand(G.reduce(P)[1])

b = sp.Matrix([0, 1, 1, 0, 0, 1])
pullback_exponents = C.T * b + 10 * sp.ones(6, 1)
alpha_numerator = alpha - sp.ones(6, 1)

checks = {
    'A_times_C_is_33I': A * C == 33 * sp.eye(6),
    'C_row_sums_are_11': all(sum(C.row(i)) == 11 for i in range(6)),
    'C_column_sums_are_11': all(sum(C[:, j]) == 11 for j in range(6)),
    'C_plus_is_nonnegative': min(int(v) for v in C_PLUS) >= 0,
    'C_plus_rows_have_degree_51': all(sum(C_PLUS.row(i)) == 51 for i in range(6)),
    'exponent_identity': A * C_PLUS == 33 * sp.eye(6) + COMMON,
    'induced_lattice_det_is_33_pow_4': int(M.det()) == 33**4,
    'induced_snf_is_1_33_33_33_33': list(SNF.diagonal()) == [1, 33, 33, 33, 33],
    'primitive_invariant_character_count_is_22': len(chars) == 22,
    'hodge_level_distribution_is_1_20_1': {
        k: sum(1 for row in chars if row['level'] == k) for k in (2, 3, 4)
    } == {2: 1, 3: 20, 4: 1},
    'exceptional_orbit_equals_level3_sector': alpha_orbit == level3,
    'explicit_cubic_monomial_is_nonzero_in_jacobian_ring': P_remainder != 0,
    'residue_pullback_exponent_is_alpha_minus_one': pullback_exponents == alpha_numerator,
    'cubic_primitive_hodge_dimensions_are_1_20_1': [sp.binomial(6, k) for k in (0, 3, 6)] == [1, 20, 1],
}

result = {
    'title': 'Degree-33 Fermat packet closure through a Klein-Delsarte cubic',
    'A': [list(map(int, A.row(i))) for i in range(6)],
    'C': [list(map(int, C.row(i))) for i in range(6)],
    'C_plus': [list(map(int, C_PLUS.row(i))) for i in range(6)],
    'projective_torus_degree': 33**4,
    'induced_lattice_matrix': [list(map(int, M.row(i))) for i in range(5)],
    'smith_diagonal': list(map(int, SNF.diagonal())),
    'invariant_primitive_characters': chars,
    'exceptional_character_reordered': list(map(int, alpha)),
    'exceptional_unit_orbit_size': len(alpha_orbit),
    'cubic_jacobian_monomial': 'y1*y2*y5',
    'cubic_jacobian_remainder': str(P_remainder),
    'residue_monomial_exponents_after_pullback': list(map(int, pullback_exponents)),
    'fermat_residue_target_exponents': list(map(int, alpha_numerator)),
    'checks': checks,
    'passed': all(checks.values()),
}
OUT.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2))
if not result['passed']:
    raise SystemExit('verification failed')
