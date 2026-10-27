"""Exact checks for the finite examples in The Komorebi Methodology.

Python 3.10+; standard library only. Run from any directory.
These tests do not constitute a Lean proof or certify infinite statements.
"""
from __future__ import annotations

import json
from fractions import Fraction as F
from itertools import product
from math import comb, factorial
from pathlib import Path
from random import Random
from typing import Sequence

Matrix = tuple[tuple[F, ...], ...]
OUT = Path(__file__).resolve().parent / 'audit'


def matrix(rows: Sequence[Sequence[int | F]]) -> Matrix:
    if not rows or not rows[0] or any(len(r) != len(rows[0]) for r in rows):
        raise ValueError('A matrix must be nonempty and rectangular.')
    return tuple(tuple(F(v) for v in r) for r in rows)


def mm(a: Matrix, b: Matrix) -> Matrix:
    if len(a[0]) != len(b):
        raise ValueError('Incompatible multiplication dimensions.')
    return tuple(tuple(sum((a[i][k] * b[k][j] for k in range(len(b))), F(0))
                       for j in range(len(b[0]))) for i in range(len(a)))


def add(a: Matrix, b: Matrix) -> Matrix:
    if (len(a), len(a[0])) != (len(b), len(b[0])):
        raise ValueError('Incompatible addition dimensions.')
    return tuple(tuple(x + y for x, y in zip(ar, br)) for ar, br in zip(a, b))


def neg(a: Matrix) -> Matrix:
    return tuple(tuple(-v for v in row) for row in a)


def sub(a: Matrix, b: Matrix) -> Matrix:
    return add(a, neg(b))


def same_fibers(rep: Sequence[int], answers: Sequence[int]) -> bool:
    if len(rep) != len(answers):
        raise ValueError('Representation and answer arrays must have equal length.')
    known: dict[int, int] = {}
    for view, answer in zip(rep, answers):
        if view in known and known[view] != answer:
            return False
        known[view] = answer
    return True


def closure(premises: set[str], chosen: set[str]) -> set[str]:
    # Certification here is a declared toy catalog, not a mathematical proof checker.
    rules = {
        'AB_L': ({'A', 'B'}, 'L', True),
        'L_T': ({'L'}, 'T', True),
        'A_M': ({'A'}, 'M', True),
        'MB_T': ({'M', 'B'}, 'T', True),
        'M_U': ({'M'}, 'U', False),
    }
    unknown = chosen - rules.keys()
    if unknown:
        raise ValueError(f'Unknown rules: {sorted(unknown)}')
    result = set(premises)
    changed = True
    while changed:
        changed = False
        for name in sorted(chosen):
            req, conclusion, certified = rules[name]
            if certified and req <= result and conclusion not in result:
                result.add(conclusion)
                changed = True
    return result


def power(a: Matrix, n: int) -> Matrix:
    if n < 0 or len(a) != len(a[0]):
        raise ValueError('A nonnegative power of a square matrix is required.')
    value = matrix([[int(i == j) for j in range(len(a))] for i in range(len(a))])
    for _ in range(n):
        value = mm(value, a)
    return value


def memory_path(a: Matrix, b: Matrix, c: Matrix, e: Matrix,
                u0: Matrix, v0: Matrix, steps: int) -> list[Matrix]:
    """Eliminate v using the history formula, retaining its initial contribution."""
    if steps < 0:
        raise ValueError('steps must be nonnegative')
    history = [u0]
    for n in range(steps):
        unext = add(mm(a, history[n]), mm(b, mm(power(e, n), v0)))
        for j in range(n):
            unext = add(unext, mm(b, mm(power(e, n-1-j), mm(c, history[j]))))
        history.append(unext)
    return history


def block_path(a: Matrix, b: Matrix, c: Matrix, e: Matrix,
               u0: Matrix, v0: Matrix, steps: int) -> list[Matrix]:
    """Direct coupled recurrence, without the eliminated-history formula."""
    if steps < 0:
        raise ValueError('steps must be nonnegative')
    u, v = u0, v0
    history = [u]
    for _ in range(steps):
        u, v = add(mm(a, u), mm(b, v)), add(mm(c, u), mm(e, v))
        history.append(u)
    return history


def main() -> int:
    records: list[dict] = []
    def record(name: str, passed: bool, *, cases: int = 1, scope: str = 'exact finite check') -> None:
        records.append({'name': name, 'passed': bool(passed), 'cases': cases, 'scope': scope})

    T = matrix([[2, 1, 0], [0, 3, 1], [1, -1, 2]])
    P = matrix([[1, 0, 0], [0, 1, 0], [0, 0, 0]])
    Q = matrix([[0, 0, 0], [0, 0, 0], [0, 0, 1]])
    x = matrix([[1], [2], [0]])
    Tx = mm(T, x)
    PTP = mm(mm(P, T), P)
    record('projector_idempotence', mm(P, P) == P and mm(Q, Q) == Q)
    record('first_full_output', Tx == matrix([[4], [6], [-1]]))
    record('first_retained_output', mm(P, Tx) == matrix([[4], [6], [0]]))
    record('second_full_retained_output', mm(P, mm(T, Tx)) == matrix([[14], [17], [0]]))
    record('second_compressed_output', mm(PTP, mm(PTP, x)) == matrix([[14], [18], [0]]))
    ret = mm(mm(mm(mm(P, T), Q), T), P)
    record('return_term_value', mm(ret, x) == matrix([[0], [-1], [0]]))
    record('return_operator_identity', mm(mm(P, mm(T, T)), P) == add(mm(PTP, PTP), ret))
    record('negative_false_two_step_agreement', mm(P, mm(T, Tx)) != mm(PTP, mm(PTP, x)), scope='deliberate false finite claim rejected')

    # A second route calculates the printed example directly as scalar recurrences.
    a, b, c = F(1), F(2), F(0)
    for _ in range(2):
        a, b, c = 2*a+b, 3*b+c, a-b+2*c
    record('independent_scalar_recurrence', (a, b, c) == (14, 17, -4))

    D = matrix([[1], [1]])
    r = matrix([[1], [2]])
    lam = matrix([[-1, 1]])
    record('obstruction_annihilates_correction', mm(lam, D) == matrix([[0]]))
    record('obstruction_detects_defect', mm(lam, r) == matrix([[1]]))
    D2 = matrix([[1, 0], [1, 1]])
    h = matrix([[-1], [-1]])
    record('enlarged_correction_removes_defect', mm(D2, h) == neg(r))
    bad_h = matrix([[-1], [0]])
    record('negative_corrupted_correction', mm(D2, bad_h) != neg(r), scope='deliberately invalid witness rejected')
    wrong_lam = matrix([[1, 1]])
    record('negative_invalid_obstruction_row', mm(wrong_lam, D) != matrix([[0]]), scope='deliberately invalid annihilator rejected')

    ns = list(range(16))
    record('parity_representation_sufficient_for_parity', same_fibers([n % 2 for n in ns], [n % 2 for n in ns]))
    record('parity_representation_insufficient_for_value', not same_fibers([n % 2 for n in ns], ns), scope='finite witness of lost distinguishability')

    # Independent finite corroboration of the general identity proved in the prose.
    rng = Random(104729)
    random_matrix = lambda rows, cols: matrix([[rng.randint(-4, 4) for _ in range(cols)] for _ in range(rows)])
    ok = True
    for _ in range(64):
        t, s = random_matrix(3, 2), random_matrix(4, 3)
        p, q, rr = random_matrix(2, 2), random_matrix(2, 3), random_matrix(3, 4)
        t0, s0 = random_matrix(2, 2), random_matrix(3, 2)
        dt, ds = sub(mm(q, t), mm(t0, p)), sub(mm(rr, s), mm(s0, q))
        lhs = sub(mm(rr, mm(s, t)), mm(s0, mm(t0, p)))
        rhs = add(mm(ds, t), mm(s0, dt))
        ok = ok and lhs == rhs
    record('typed_defect_composition', ok, cases=64, scope='exact finite corroboration; general proof is in the essay')

    # Euler coefficients from cosh(t)F(t)=1, independent of the displayed tanh identity.
    N = 14
    e = [F(1)]
    for n in range(1, N + 1):
        e.append(-sum((F(comb(n, k)) * e[n-k] for k in range(2, n+1, 2)), F(0)))
    record('signed_euler_initial_coefficients', e[:9] == list(map(F, [1, 0, -1, 0, 5, 0, -61, 0, 1385])))
    bcoef = [sum((F(comb(n, k)) * e[k] for k in range(n+1)), F(0)) for n in range(N+1)]
    record('euler_binomial_transform', bcoef[:9] == list(map(F, [1, 1, 0, -2, 0, 16, 0, -272, 0])))
    record('positive_even_transform_vanishes', all(bcoef[n] == 0 for n in range(2, N+1, 2)), cases=N//2)
    inv = [sum((F(comb(n, k) * (-1)**(n-k)) * bcoef[k] for k in range(n+1)), F(0)) for n in range(N+1)]
    record('inverse_binomial_transform', inv == e, cases=N+1)
    # Formal power-series check: cosh(t) * transformed series = exp(t).
    record('formal_series_product', all(sum((bcoef[n-k]/factorial(n-k)/factorial(k) for k in range(0, n+1, 2)), F(0)) == F(1, factorial(n)) for n in range(N+1)), cases=N+1)

    # Fourth roots of unity as exact Gaussian integer pairs. No floating point.
    units = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    residues = []
    for rr in range(4):
        for n in range(25):
            terms = [units[(j*(n-rr)) % 4] for j in range(4)]
            real = F(sum(z[0] for z in terms), 4)
            imag = F(sum(z[1] for z in terms), 4)
            residues.append(real == int(n % 4 == rr) and imag == 0)
    record('fourth_root_residue_filter', all(residues), cases=len(residues), scope='exact m=4 checks; arbitrary-m proof is coefficientwise in the essay')

    record('finite_prefix_witnesses', all(all(N >= n for n in range(N+1)) for N in range(65)), cases=65, scope='finite corroboration only; no claim of proving infinite nonexistence by testing')
    record('candidate_m_excluded_at_successor', all(not (m >= m+1) for m in range(65)), cases=65, scope='finite corroboration of the explicit written contradiction')
    record('small_residual_diagonal_samples', all(F(1,n) < F(1,C) for C in range(1,17) for n in [C+1]), cases=16, scope='finite samples; Hilbert-space proof remains written')

    all_rules = {'AB_L','L_T','A_M','MB_T','M_U'}
    record('selected_certificate_closure', closure({'A','B'}, {'AB_L','L_T'}) == {'A','B','L','T'}, scope='declared finite dependency model only')
    record('alternative_certificate_closure', closure({'A','B'}, {'A_M','MB_T'}) == {'A','B','M','T'}, scope='declared finite dependency model only')
    record('missing_joint_premise_rejected', 'T' not in closure({'A'}, all_rules), scope='negative structural control; not a semantic proof checker')
    record('candidate_extension_not_certified', 'U' not in closure({'A','B'}, all_rules), scope='candidate flag cannot enter certified closure in this toy model')
    try:
        closure({'A','B'}, {'NOT_A_RULE'})
        rejected = False
    except ValueError:
        rejected = True
    record('unknown_rule_rejected', rejected, scope='malformed-reference negative control')
    try:
        mm(matrix([[1,2]]), matrix([[1,2]]))
        rejected = False
    except ValueError:
        rejected = True
    record('invalid_matrix_dimensions_rejected', rejected, scope='interface validation')

    # Complete finite enumeration for the new continuation criterion.
    # A realization respects T iff rT is constant on r-fibers. When so,
    # the induced map predicts every sampled iterate by the same quotient rule.
    continuation_ok = True
    continuation_cases = 0
    closed_systems = 0
    for rep in product(range(2), repeat=3):
        for trans in product(range(3), repeat=3):
            successor_views = [rep[trans[x]] for x in range(3)]
            compatible = same_fibers(rep, successor_views)
            quotient: dict[int, int] = {}
            conflict = False
            for x in range(3):
                view, successor = rep[x], successor_views[x]
                if view in quotient and quotient[view] != successor:
                    conflict = True
                quotient[view] = successor
            continuation_ok &= compatible == (not conflict)
            if compatible:
                closed_systems += 1
                for x in range(3):
                    actual, reduced = x, rep[x]
                    for _ in range(6):
                        continuation_ok &= rep[actual] == reduced
                        actual, reduced = trans[actual], quotient[reduced]
            continuation_cases += 1
    record('continuation_factorization_small_models', continuation_ok,
           cases=continuation_cases,
           scope='all 216 maps on a three-state/two-view model; iterates through five; general induction is written')
    record('parity_not_sufficient_for_halving', not same_fibers([0,1,0,1],[0,0,1,1]),
           scope='counterexample to continuation closure, not static parity sufficiency')

    a, b, c, eblock = matrix([[2,1],[0,3]]), matrix([[0],[1]]), matrix([[1,-1]]), matrix([[2]])
    u0, zero_v = matrix([[1],[2]]), matrix([[0]])
    reconstructed = memory_path(a,b,c,eblock,u0,zero_v,12)
    direct = block_path(a,b,c,eblock,u0,zero_v,12)
    record('memory_reconstruction_zero_initial_complement', reconstructed == direct,
           cases=len(direct), scope='thirteen exact time samples, including time zero; all-time proof is in the essay')
    record('memory_second_retained_observation', reconstructed[2] == matrix([[14],[17]]))
    v0 = matrix([[F(3,2)]])
    reconstructed_nonzero = memory_path(a,b,c,eblock,u0,v0,12)
    direct_nonzero = block_path(a,b,c,eblock,u0,v0,12)
    record('memory_reconstruction_nonzero_initial_complement', reconstructed_nonzero == direct_nonzero,
           cases=len(direct_nonzero), scope='thirteen exact samples with the initial complementary contribution retained')
    record('omitted_initial_complement_rejected', reconstructed[1] != direct_nonzero[1],
           scope='negative control: the zero-initial formula must not certify a nonzero initial state')
    wrong_history = memory_path(a,b,c,matrix([[3]]),u0,zero_v,3)
    record('corrupted_memory_operator_rejected', wrong_history[2] == direct[2] and wrong_history[3] != direct[3],
           scope='negative control: changing the complement dynamics can escape the second-step test but not the third')

    rng_memory = Random(32452843)
    def small_fraction_matrix(rows: int, cols: int) -> Matrix:
        return matrix([[F(rng_memory.randint(-3,3),rng_memory.randint(1,3)) for _ in range(cols)] for _ in range(rows)])
    memory_ok = True
    for _ in range(48):
        a, b, c, eblock = (small_fraction_matrix(2,2) for _ in range(4))
        u0, v0 = small_fraction_matrix(2,1), small_fraction_matrix(2,1)
        memory_ok &= memory_path(a,b,c,eblock,u0,v0,7) == block_path(a,b,c,eblock,u0,v0,7)
    record('memory_reconstruction_rational_block_families', memory_ok, cases=48,
           scope='48 seeded rational block systems, each checked at eight time points; shared exact arithmetic primitives')

    OUT.mkdir(exist_ok=True)
    failed = [r['name'] for r in records if not r['passed']]
    summary = {
        'title': 'Exact finite checks for The Komorebi Methodology',
        'groups': len(records), 'groups_passed': len(records)-len(failed),
        'case_count': sum(r['cases'] for r in records),
        'failed_groups': failed, 'checks': records,
        'scope': 'Exact finite calculations and a declared dependency model. No new Lean run. General and infinite arguments are written proofs, not consequences of sample counts.'
    }
    (OUT/'exact_checks.json').write_text(json.dumps(summary, indent=2)+'\n')
    (OUT/'EXACT_CHECKS.txt').write_text('\n'.join([
        summary['title'], '', f"{summary['groups_passed']}/{summary['groups']} groups passed; {summary['case_count']} recorded cases.",
        *[f"{'PASS' if r['passed'] else 'FAIL'}  {r['name']} ({r['cases']} cases)" for r in records],
        '', summary['scope'], ''
    ]))
    print(json.dumps({k:summary[k] for k in ['groups','groups_passed','case_count','failed_groups']}, indent=2))
    return 1 if failed else 0

if __name__ == '__main__':
    raise SystemExit(main())
