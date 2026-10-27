"""Bounded exact checks for finite-group averaging with loss of p-adic precision.

Every group action is defined over Z before reduction.  Congruences are tested
in Z_(p), embedded in Z_p.  A pass audits these finite inputs, not the universal
Lean theorem or any arithmetic local-type realization.
"""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
import hashlib
import json
import platform
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
I = (1, 0, 0, 1)
ZERO = (0, 0, 0, 0)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def mul(a, b):
    return (a[0]*b[0] + a[1]*b[2], a[0]*b[1] + a[1]*b[3],
            a[2]*b[0] + a[3]*b[2], a[2]*b[1] + a[3]*b[3])


def det(a):
    return a[0]*a[3] - a[1]*a[2]


def inv(a):
    require(det(a) != 0, "inverse requires a nonsingular matrix")
    return tuple(Fraction(x, det(a)) for x in (a[3], -a[1], -a[2], a[0]))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def divisible(a, q):
    return all(x % q == 0 for x in a)


def p_integral(x, p):
    return Fraction(x).denominator % p != 0


def congruent(a, b, p, k):
    q = p**k
    differences = tuple(Fraction(x)-Fraction(y) for x, y in zip(a, b))
    return all(x.denominator % p != 0 and x.numerator % q == 0
               for x in differences)


def integral_conjugate(frame, action):
    fi = inv(frame)
    result = tuple(mul(mul(frame, t), fi) for t in action)
    if any(Fraction(x).denominator != 1 for a in result for x in a):
        return None
    return tuple(tuple(int(x) for x in a) for a in result)


def cyclic(generator, order):
    matrices = [I]
    for _ in range(1, order):
        matrices.append(mul(matrices[-1], generator))
    require(mul(matrices[-1], generator) == I, "cyclic relation failed over Z")
    table = tuple(tuple((i+j) % order for j in range(order)) for i in range(order))
    inverses = tuple((-i) % order for i in range(order))
    return tuple(matrices), table, inverses


def s3_action():
    # Permutations act on column vectors.  The basis is e0-e2, e1-e2.
    elements = tuple(permutations(range(3)))
    indices = {g: i for i, g in enumerate(elements)}
    action = []
    for g in elements:
        columns = []
        for j in (0, 1):
            v = [0, 0, 0]
            v[g[j]] += 1
            v[g[2]] -= 1
            columns.append(v[:2])
        action.append((columns[0][0], columns[1][0], columns[0][1], columns[1][1]))
    table = tuple(tuple(indices[tuple(g[h[k]] for k in range(3))]
                        for h in elements) for g in elements)
    inverses = tuple(next(j for j in range(6) if table[i][j] == 0)
                     for i in range(6))
    require(any(table[i][j] != table[j][i] for i in range(6) for j in range(6)),
            "S3 test must be noncommutative")
    return tuple(action), table, inverses


def verify_action(action, table, inverses, counts, label):
    require(action[0] == I, "identity element must act as identity")
    for i in range(len(action)):
        require(mul(action[i], action[inverses[i]]) == I, "inverse action mismatch")
        for j in range(len(action)):
            require(mul(action[i], action[j]) == action[table[i][j]],
                    f"{label}: an action law failed over Z")
            counts[label + '_integral_group_laws'] += 1


def average(rho, tau, inverses, a):
    totals = [0, 0, 0, 0]
    for i in range(len(rho)):
        summand = mul(mul(rho[i], a), tau[inverses[i]])
        for j in range(4):
            totals[j] += summand[j]
    return tuple(Fraction(x, len(rho)) for x in totals)


def check_family(label, tau, rho, table, inverses, p, k, extra_lift_digits, counts):
    order = len(tau)
    e, remaining = 0, order
    while remaining % p == 0:
        e += 1
        remaining //= p
    require(e > 0, "these tests target nonunit group order")
    verify_action(rho, table, inverses, counts, label)
    q = p**(e+k)
    counts[label + '_representation_families'] += 1
    # Exhaust all comparison residue matrices; invertibility is not presumed.
    for residue in product(range(q), repeat=4):
        counts[label + '_comparison_residues_inspected'] += 1
        if not all(divisible(sub(mul(rho[i], residue), mul(residue, tau[i])), q)
                   for i in range(order)):
            continue
        counts[label + '_equivariant_comparison_residues'] += 1
        for digits in product(range(extra_lift_digits), repeat=4):
            a = tuple(x+q*d for x, d in zip(residue, digits))
            result = average(rho, tau, inverses, a)
            require(all(p_integral(x, p) for x in result), label + ': nonintegral average')
            require(congruent(result, a, p, k), label + ': promised congruence failed')
            for i in range(order):
                require(mul(rho[i], result) == mul(result, tau[i]),
                        label + ': exact intertwining failed')
                counts[label + '_exact_intertwining_equations'] += 1
            require(average(rho, tau, inverses, result) == result,
                    label + ': averaging is not idempotent')
            counts[label + '_comparison_lifts_averaged'] += 1
            if det(a) % p != 0:
                dr = Fraction(det(result))
                require(dr.numerator % p != 0 and dr.denominator % p != 0,
                        label + ': invertible comparison failed to stay a p-adic unit')
                require(mul(mul(result, tau[1]), inv(result)) == rho[1],
                        label + ': conjugation check failed')
                counts[label + '_unit_determinants_preserved'] += 1
            if any(x.denominator != 1 for x in result):
                counts[label + '_noninteger_but_p_integral_averages'] += 1
            if not congruent(result, a, p, e+k):
                counts[label + '_full_input_precision_not_preserved_by_average'] += 1


def json_safe_matrix(a):
    return [str(Fraction(x)) for x in a]


def main():
    start = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat()
    counts = Counter()
    c2, table2, inv2 = cyclic((1, 0, 0, -1), 2)
    verify_action(c2, table2, inv2, counts, 'C2_template')
    # Enumerate rational conjugacies represented by every nonsingular integer
    # frame in [-2,2]^4, then retain only actual integral actions and deduplicate.
    c2_conjugates = {}
    for frame in product(range(-2, 3), repeat=4):
        counts['C2_frames_inspected'] += 1
        if det(frame) == 0:
            continue
        counts['C2_nonsingular_frames'] += 1
        rho = integral_conjugate(frame, c2)
        if rho is not None:
            counts['C2_frames_giving_integral_actions'] += 1
            c2_conjugates.setdefault(rho, frame)
    counts['C2_distinct_integral_actions'] = len(c2_conjugates)
    for k in (1, 2):
        for rho in sorted(c2_conjugates):
            check_family(f'C2_p2_k{k}', c2, rho, table2, inv2, 2, k, 1, counts)

    c4, table4, inv4 = cyclic((0, -1, 1, 0), 4)
    require(len(set(c4)) == 4, 'C4 action must be faithful, not factor through C2')
    verify_action(c4, table4, inv4, counts, 'C4_template')
    for h in (-1, 0, 1):
        rho = integral_conjugate((1, h, 0, 1), c4)
        require(rho is not None, 'unimodular C4 conjugate must be integral')
        check_family('C4_p2_k1', c4, rho, table4, inv4, 2, 1, 1, counts)

    s3, table3, inv3 = s3_action()
    verify_action(s3, table3, inv3, counts, 'S3_template')
    for p in (2, 3):
        for frame in (I, (1, 1, 0, 1), (1, 0, 1, 1)):
            rho = integral_conjugate(frame, s3)
            require(rho is not None, 'unimodular S3 conjugate must be integral')
            # For every accepted residue, exhaust all p^4 entrywise lifts by
            # one additional base-p digit.  No random inputs are used.
            check_family(f'S3_p{p}_k1', s3, rho, table3, inv3, p, 1, p, counts)
    require(counts['S3_p3_k1_noninteger_but_p_integral_averages'] > 0,
            'S3 test must exercise denominators prime to 3')

    # Exact, hand-readable sharpness witness.  Its mod-4 comparison exists,
    # but no mod-8 intertwiner reduces to that prescribed comparison mod 4.
    rho, _, _ = cyclic((1, 2, 0, -1), 2)
    a = (1, 1, 0, 1)
    result = average(rho, c2, inv2, a)
    require(divisible(sub(mul(rho[1], a), mul(a, c2[1])), 4), 'witness not equivariant mod 4')
    require(mul(rho[1], a) != mul(a, c2[1]), 'witness must fail exact intertwining')
    require(result == (1, -1, 0, 1), 'unexpected sharpness average')
    require(congruent(result, a, 2, 1) and not congruent(result, a, 2, 2),
            'sharpness witness must preserve exactly the stated lower precision')
    for digits in product(range(2), repeat=4):
        candidate = tuple(x+4*d for x, d in zip(a, digits))
        require(not divisible(sub(mul(rho[1], candidate), mul(candidate, c2[1])), 8),
                'unexpected lift retaining all input precision')
        counts['sharpness_all_mod8_lifts_rejected'] += 1
    counts['false_strengthenings_rejected'] += 1

    # Same mod-2 residual isomorphism is insufficient without the extra input
    # digit.  The trivial and sign characters cannot be conjugate over Z_2:
    # every putative unit already violates the equation modulo 4.
    require(1 % 2 == (-1) % 2, 'characters should agree modulo 2')
    for u in (1, 3):
        require((u - (-u)) % 4 != 0, 'unexpected scalar unit intertwiner mod 4')
        counts['trivial_sign_mod4_units_rejected'] += 1
    bad = average((I, I), c2, inv2, I)
    require(bad == (1, 0, 0, 0) and det(bad) == 0, 'wrong insufficient-depth average')
    require(not congruent(bad, I, 2, 1), 'extra input digit is not optional')
    counts['false_strengthenings_rejected'] += 1

    script_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    contract = {
        'claim': 'Averaging an actual integral finite-group comparison equivariant mod p^(e+k) produces a p-integral exact intertwiner congruent to it mod p^k, where e = v_p(|G|); unit determinant persists when k >= 1.',
        'arithmetic': 'Exact integers and fractions only. Fractions whose denominators are prime to p are elements of Z_(p), hence of Z_p. No floating point enters any decision.',
        'matrix_convention': 'Row-major 2 by 2 matrices acting on column vectors; rho(g) P = P tau(g); average = sum_g rho(g) A tau(g^-1)/|G|.',
        'actual_integral_actions': 'All actions are constructed over Z and their full group multiplication tables checked before any reduction. No torsion representation is presumed to have an integral lift.',
        'C2': 'Template diag(1,-1); every nonsingular frame in {-2,-1,0,1,2}^4, integral conjugate actions only, deduplicated; p=2; k=1,2; all four entries of A modulo 2^(1+k).',
        'C4': 'Faithful order-four rotation [[0,-1],[1,0]], conjugated by [[1,h],[0,1]] for h=-1,0,1; p=2, e=2, k=1; all A modulo 8. This checks e>1, without asserting e=2 is optimal for this particular action.',
        'S3': 'Permutation action on basis e0-e2,e1-e2; identity, upper-unit shear, lower-unit shear frames; p=2,3; e=k=1; all A modulo p^2, with every p^4 lift by one further entrywise digit for each equivariant residue.',
        'invertibility': 'All equivariant comparison matrices are included, even singular ones; unit preservation and conjugacy are checked only when det(A) is a p-adic unit.',
        'sharpness': 'Explicit C2 example; all 16 lifts of the prescribed mod-4 matrix to mod 8 fail equivariance, although its average preserves the mod-2 matrix.',
        'randomness': 'none',
        'resource_cutoff': 'none; all stated ranges completed',
        'failure_interpretation': 'A failed invariant aborts with AssertionError; no partial count is recorded as a pass. A timeout is inconclusive.',
        'limitations': [
            'Bounded implementation audit; not a universal proof of the lifting or completion theorems.',
            'Only the stated actual integral finite-group actions and rational p-integral averages are tested.',
            'No arbitrary torsion representation is claimed to lift integrally.',
            'No Galois, Hodge-Tate, Weil-Deligne or arithmetic packet identification is inferred.',
            'Group-order valuation gives a sufficient bound; this audit does not assert it is always optimal.'
        ]
    }
    report = {
        'status': 'passed', 'counts': dict(sorted(counts.items())),
        'contract': contract,
        'sharpness_example': {'p': 2, 'e': 1, 'k': 1,
                              'tau_generator': list(c2[1]), 'rho_generator': list(rho[1]),
                              'comparison_A': list(a), 'average_P': json_safe_matrix(result),
                              'input_modulus': 4, 'retained_modulus': 2,
                              'no_mod8_lift_retaining_A_mod4': True},
        'C2_distinct_integral_generators': [list(r[1]) for r in sorted(c2_conjugates)],
        'script_sha256': script_sha,
        'run_command': 'python3 block17/checks/exact_precision.py',
        'environment': {'python': platform.python_version(), 'implementation': platform.python_implementation(),
                        'platform': platform.platform(), 'packages': 'Python standard library only'},
        'runtime_seconds': time.perf_counter()-start
    }
    output = ROOT / 'exact_precision.json'
    output.write_text(json.dumps(report, indent=2) + '\n')
    manifest = {
        'schema_version': 1, 'claim_id': 'PaperX-Block17-precision-averaging-finite-audit',
        'repository': {'commit': 'not a git checkout; script checksum records exact source', 'dirty': False},
        'command': report['run_command'],
        'environment': {'software': ['Python ' + platform.python_version(), 'standard library only'],
                        'hardware': platform.machine()},
        'mathematics': {'assertion_tested': contract['claim'], 'coefficient_domain': contract['arithmetic'],
                        'conventions': contract['matrix_convention'],
                        'inputs': [contract['C2'], contract['C4'], contract['S3']],
                        'bounds': {'C2_frame_entries': [-2, 2], 'C2_moduli': [4, 8], 'C4_modulus': 8,
                                   'S3_moduli': [4, 9], 'S3_extra_lift_digits': [2, 3], 'resource_cutoff': None},
                        'non_claims': contract['limitations']},
        'randomness': {'used': False, 'generator': 'none', 'seed': None},
        'run': {'started_at': started_at, 'runtime_seconds': report['runtime_seconds'], 'exit_status': 0},
        'outputs': [{'path': 'checks/exact_precision.py', 'sha256': script_sha},
                    {'path': 'exact_precision.json', 'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}],
        'checks': ['Actual integer group laws', 'Exact rational Reynolds average', 'p-integral entries',
                   'Exact all-group intertwining', 'Precision loss congruence', 'Averaging idempotence',
                   'Unit determinant preservation', 'Mod-8 obstruction to preserving full precision',
                   'Mod-4 obstruction for trivial and sign characters'],
        'result': 'implementation and finite assertion verified in the stated range; independent review separate',
        'residual_risks': ['Finite ranges are not universal theorems; independent code review pending.']
    }
    (ROOT / 'exact_precision_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'status': 'passed', 'counts': report['counts'],
                      'script_sha256': script_sha, 'runtime_seconds': report['runtime_seconds']}))


if __name__ == '__main__':
    main()
