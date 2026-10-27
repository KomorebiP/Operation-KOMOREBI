"""Exact bounded Block 19 audit: complete projector families and their rigidity.

Only integers, Fraction, and explicitly stated modular rings are used. This
script imports the pinned predecessor's elementary matrix arithmetic. It does
not call the predecessor's correction or sample generators. Constructed tests
are deterministic, not an exhaustive classification of quotient families.
"""
from fractions import Fraction
from itertools import product
from pathlib import Path
import argparse
import hashlib
import json
import platform

from exact_summands import (need, eye, add, sub, scale, mul, mod, vanishes,
                            congruent, residual, defect, average,
                            validate_group, s3, valuation)

ROOT = Path(__file__).resolve().parents[1]
TARGET_DEPTH = 9


def total(matrices, n):
    out = (0,) * (n*n)
    for a in matrices:
        out = add(out, a)
    return out


def conjugate(w, a, wi, n):
    return mul(mul(w, a, n), wi, n)


def elementary(n, i, j):
    return tuple(int(a == i and b == j) for a in range(n) for b in range(n))


def mixed_frame(n):
    """Unipotent integral frame and its finite geometric-series inverse."""
    upper = tuple(int(j == i+1) * (1 + i % 2) for i in range(n) for j in range(n))
    w, wi, term = add(eye(n), upper), eye(n), eye(n)
    for j in range(1, n):
        term = mul(term, upper, n)
        wi = add(wi, scale((-1)**j, term))
    need(mul(w, wi, n) == eye(n) and mul(wi, w, n) == eye(n), 'mixed frame inverse')
    return w, wi


def repeated(action, block_size, copies):
    n = block_size * copies
    return tuple(tuple(a[(i % block_size)*block_size+j % block_size]
                       if i//block_size == j//block_size else 0
                       for i in range(n) for j in range(n)) for a in action)


def assert_family(family, action, n, modulus):
    need(vanishes(sub(total(family, n), eye(n)), modulus), 'family sum is not identity')
    for i, a in enumerate(family):
        need(vanishes(defect(a, n), modulus), 'family member not idempotent')
        for j, b in enumerate(family):
            if i != j:
                need(vanishes(mul(a, b, n), modulus), 'ordered orthogonality failed')
        need(all(vanishes(sub(mul(a, g, n), mul(g, a, n)), modulus) for g in action),
             'family member not equivariant')


def corner_newton(a, c, action, n, p, k, depth):
    """Correct inside the supplied finite quotient corner, checking each step."""
    q = p**depth
    x = mod(a, q)
    precision = k
    iterations = 0
    while precision < depth:
        need(vanishes(defect(x, n), p**precision), 'corner input defect precision')
        need(vanishes(sub(mul(c, x, n), x), q) and
             vanishes(sub(mul(x, c, n), x), q), 'corner support lost')
        x2 = mul(x, x, n)
        y = mod(sub(scale(3, x2), scale(2, mul(x2, x, n))), q)
        d = defect(x, n)
        identity_rhs = mul(mul(d, d, n), sub(scale(4, d), scale(3, eye(n))), n)
        need(vanishes(sub(defect(y, n), identity_rhs), q), 'independent defect factorization')
        need(vanishes(sub(y, x), p**precision), 'Newton lost retained digits')
        precision = min(2*precision, depth)
        need(vanishes(defect(y, n), p**precision), 'defect precision failed to double')
        x = y
        iterations += 1
    result = mod(mul(mul(c, x, n), c, n), q)
    need(result == x, 'zero-constant polynomial did not remain supported in corner')
    need(vanishes(defect(result, n), q), 'corrected corner not idempotent')
    need(all(vanishes(sub(mul(result, g, n), mul(g, result, n)), q) for g in action),
         'corrected corner not equivariant')
    need(congruent(result, a, p, k), 'corner correction lost precision k')
    return result, iterations


def lift_family(inputs, action, inverses, n, p, k, depth):
    e = valuation(len(action), p)
    input_modulus, output_modulus = p**(e+k), p**depth
    assert_family(inputs, action, n, input_modulus)
    # Each input is averaged once, with no repeated averaging in the induction.
    averaged = tuple(average(a, action, inverses, n) for a in inputs)
    for a, b in zip(inputs, averaged):
        need(congruent(a, b, p, k), 'one averaging pass lost more than e digits')
        need(all(mul(g, b, n) == mul(b, g, n) for g in action), 'average not exactly equivariant')
    outputs, steps = [], 0
    for i in range(len(inputs)-1):
        c = mod(sub(eye(n), total(outputs, n)), output_modulus)
        need(vanishes(defect(c, n), output_modulus), 'remaining complement not idempotent')
        a = mod(mul(mul(c, residual(averaged[i], p, depth), n), c, n), output_modulus)
        need(congruent(a, inputs[i], p, k), 'corner multiplication lost precision k')
        f, iterations = corner_newton(a, c, action, n, p, k, depth)
        for previous in outputs:
            need(vanishes(mul(previous, f, n), output_modulus) and
                 vanishes(mul(f, previous, n), output_modulus), 'induction orthogonality failed')
        outputs.append(f)
        steps += iterations
    if inputs:
        outputs.append(mod(sub(eye(n), total(outputs, n)), output_modulus))
    assert_family(outputs, action, n, output_modulus)
    need(all(congruent(a, b, p, k) for a, b in zip(inputs, outputs)),
         'whole family failed prescribed reduction')
    need(len(outputs) == len(inputs), 'label count changed')
    return tuple(outputs), dict(newton_iterations=steps,
                               averaged_matrices=len(averaged),
                               non_idempotent_exact_averages=sum(defect(b, n) != (0,)*(n*n)
                                                                 for b in averaged),
                               input_depth_preserved=all(congruent(a, b, p, e+k)
                                                         for a, b in zip(inputs, outputs)))


def modular_inverse(a, n, q):
    """Independent Gaussian elimination over Z/q, using only unit pivots."""
    rows = [[a[i*n+j] % q for j in range(n)] + [int(i == j) for j in range(n)]
            for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if Fraction(rows[r][col], q).denominator == q), None)
        need(pivot is not None, 'no unit pivot for near-identity conjugator')
        rows[col], rows[pivot] = rows[pivot], rows[col]
        rows[col] = [(x*pow(rows[col][col], -1, q)) % q for x in rows[col]]
        for r in range(n):
            if r != col:
                scalar = rows[r][col]
                rows[r] = [(a-scalar*b) % q for a, b in zip(rows[r], rows[col])]
    need(all(rows[i][j] == int(i == j) for i in range(n) for j in range(n)), 'Gaussian inverse left block')
    inverse = tuple(rows[i][n+j] for i in range(n) for j in range(n))
    need(mod(mul(a, inverse, n), q) == eye(n) and
         mod(mul(inverse, a, n), q) == eye(n), 'two-sided inverse check')
    return inverse


def rigidity(e_family, f_family, action, n, p, k, depth):
    q = p**depth
    u = mod(total((mul(f, e, n) for e, f in zip(e_family, f_family)), n), q)
    need(congruent(u, eye(n), p, k), 'canonical conjugator not near identity')
    ui = modular_inverse(u, n, q)
    for e, f in zip(e_family, f_family):
        need(vanishes(sub(mul(u, e, n), mul(f, u, n)), q), 'labeled intertwining equation')
        need(mod(conjugate(u, e, ui, n), q) == f, 'labeled conjugation failed')
    need(all(vanishes(sub(mul(g, u, n), mul(u, g, n)), q) for g in action), 'conjugator not equivariant')
    return dict(distinct_output_families=e_family != f_family,
                nonidentity_conjugator=u != eye(n),
                conjugator_sha256=hashlib.sha256(str(u).encode()).hexdigest())


def carrier(label, summands):
    if label == 'C2':
        n, block_size = summands, 1
        action = (eye(n), tuple((1 if i % 2 == 0 else -1) if i == j else 0
                                for i in range(n) for j in range(n)))
    elif label == 'Klein4':
        n, block_size = summands, 1
        action = tuple(tuple((1, s, t)[i % 3] if i == j else 0
                             for i in range(n) for j in range(n)) for s, t in product((-1, 1), repeat=2))
    elif label == 'S3':
        n, block_size = summands*2, 2
        action = repeated(s3(), 2, summands)
    elif label == 'C4':
        n, block_size = summands*2, 2
        action = repeated((eye(2), (0, -1, 1, 0), (-1, 0, 0, -1), (0, 1, -1, 0)), 2, summands)
    else:
        raise ValueError(label)
    return n, block_size, action


def constructed_case(label, summands, p, k):
    n, block_size, base_action = carrier(label, summands)
    e = valuation(len(base_action), p)
    input_modulus = p**(e+k)
    w, wi = mixed_frame(n)
    action = tuple(conjugate(w, g, wi, n) for g in base_action)
    inverses = validate_group(action, n)
    noncommutative = any(mul(g, h, n) != mul(h, g, n) for g in action for h in action)
    need(noncommutative == (label == 'S3'), 'carrier commutativity benchmark')
    # For diagonal sign characters and p=2, the shear is only equivariant at
    # the requested quotient depth. This exercises genuine loss of precision.
    shear_depth = e+k-1 if label in ('C2', 'Klein4') and p == 2 else e+k
    shear = scale(p**shear_depth, elementary(n, 0, 1))
    v, vi = add(eye(n), shear), sub(eye(n), shear)
    need(mul(v, vi, n) == eye(n), 'near-equivariant shear inverse')
    seeds = tuple(conjugate(w, conjugate(v,
                        tuple(int(i == j and i//block_size == t) for i in range(n) for j in range(n)),
                        vi, n), wi, n) for t in range(summands))
    assert_family(seeds, action, n, input_modulus)
    need(total(seeds, n) == eye(n) and all(defect(a, n) == (0,)*(n*n) for a in seeds),
         'exact seed family benchmark')
    lifted, stats = [], []
    for variant in range(2):
        inputs = tuple(add(a, scale(input_modulus,
                       tuple(((i+1)*(j+3)+5*t+7*variant+variant*i*j) % 11-5
                             for i in range(n) for j in range(n)))) for t, a in enumerate(seeds))
        result, record = lift_family(inputs, action, inverses, n, p, k, TARGET_DEPTH)
        # Every constructed label remains nonzero. Exact ranks of image modules
        # are not inferred from trace alone; these traces are benchmark invariants.
        need(all(any(x % p for x in a) for a in result), 'nonzero summand disappeared')
        need(all(sum(a[i*n+i] for i in range(n)) % p**TARGET_DEPTH == block_size for a in result),
             'expected trace benchmark')
        lifted.append(result)
        stats.append(record)
    rigid = rigidity(lifted[0], lifted[1], action, n, p, k, TARGET_DEPTH)
    return dict(family=label,ambient_rank=n,summands=summands,p=p,k=k,e=e,
                group_order=len(action),input_depth=e+k,target_depth=TARGET_DEPTH,
                noncommutative=noncommutative,construction_variants=2,
                newton_iterations=sum(a['newton_iterations'] for a in stats),
                averaged_matrices=sum(a['averaged_matrices'] for a in stats),
                non_idempotent_exact_averages=sum(a['non_idempotent_exact_averages'] for a in stats),
                full_input_depth_preserved_variants=sum(a['input_depth_preserved'] for a in stats),
                **rigid)


def exhaustive_small_pairs():
    """All complete labeled pairs for the trivial rank-two carrier modulo 2."""
    action, inverses, n = (eye(2),), (eye(2),), 2
    accepted, steps = 0, 0
    for raw in product((0, 1), repeat=4):
        if not vanishes(defect(raw, n), 2):
            continue
        accepted += 1
        input_family = (raw, sub(eye(n), raw))
        output, stat = lift_family(input_family, action, inverses, n, 2, 1, TARGET_DEPTH)
        steps += stat['newton_iterations']
        # Independent enumeration of vector decomposition in the output mod 4.
        for vector in product(range(4), repeat=2):
            pieces = [tuple(sum(a[i*n+j]*vector[j] for j in range(n)) % 4
                            for i in range(n)) for a in output]
            need(tuple(sum(v[i] for v in pieces) % 4 for i in range(n)) == vector,
                 'independent vector decomposition')
            for i in range(2):
                for j in range(2):
                    value = tuple(sum(output[i][a*n+b]*pieces[j][b] for b in range(n)) % 4
                                  for a in range(n))
                    need(value == (pieces[j] if i == j else (0, 0)), 'labeled image reconstruction')
    need(accepted == 8, 'known count of 2x2 idempotents over F2')
    return dict(all_matrices_enumerated=16,complete_labeled_pairs=accepted,
                vectors_enumerated=accepted*16,newton_iterations=steps)


def boundary_checks():
    n, p, k = 3, 2, 1
    basis = tuple(elementary(n, i, i) for i in range(n))
    bad = (add(basis[0], scale(2, elementary(n, 0, 1))), basis[1], basis[2])
    need(all(defect(a, n) == (0,)*(n*n) for a in bad), 'independent lifts must be exact idempotents')
    need(all(congruent(a, b, p, k) for a, b in zip(bad, basis)), 'independent lift residue benchmark')
    need(mul(bad[0], bad[1], n) == scale(2, elementary(n, 0, 1)), 'independent orthogonality defect')
    sum_only = (scale(2, eye(n)), scale(-2, eye(n)), eye(n))
    need(total(sum_only, n) == eye(n) and any(defect(a, n) != (0,)*(n*n) for a in sum_only),
         'sum-one-only boundary')
    # k=0 gives no near-identity information: swapping labels makes U zero.
    swap_e = ((1, 0, 0, 0), (0, 0, 0, 1))
    swap_f = tuple(reversed(swap_e))
    swap_u = total((mul(f, e, 2) for e, f in zip(swap_e, swap_f)), 2)
    need(swap_u == (0, 0, 0, 0), 'positive retained depth boundary')
    action = (eye(3), (1, 0, 0, 0, -1, 0, 0, 0, 1))
    precision_family = (bad[0], sub(basis[1], scale(2, elementary(n, 0, 1))), basis[2])
    assert_family(precision_family, action, n, 4)
    # Every scalar lifting the upper-right value 2 mod 4 fails equivariance mod8.
    candidate_entries = [a for a in range(8) if a % 4 == 2]
    need(candidate_entries == [2, 6] and all((2*a) % 8 != 0 for a in candidate_entries),
         'precision loss coefficient obstruction')
    output, stats = lift_family(precision_family, action, validate_group(action, n), n, 2, 1, 9)
    need(output == basis, 'precision loss endpoint benchmark')
    return dict(independent_lifts=dict(input_family=[list(a) for a in basis],
                                      lifted_family=[list(a) for a in bad],
                                      nonzero_product=list(mul(bad[0], bad[1], n)),
                                      conclusion='Individual idempotent lifts need not be orthogonal.'),
                sum_one_alone=dict(scalar_multiples=[2, -2, 1],
                                   conclusion='Summing to identity does not imply projector relations.'),
                nonpositive_depth=dict(k=0,conjugator=list(swap_u),
                                       conclusion='Without positive retained depth, the canonical labeled conjugator can be zero.'),
                unavoidable_precision_loss=dict(p=2,group_order=2,e=1,k=1,input_depth=2,
                                                complete_family=[list(a) for a in precision_family],
                                                upper_entry_lifts_mod8=candidate_entries,
                                                equivariant_upper_entry_lifts_mod8=0,
                                                output_family_mod512=[list(a) for a in output],
                                                newton_iterations=stats['newton_iterations'],
                                                conclusion='No integral equivariant lift retains the whole family modulo4; retaining modulo2 succeeds.'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT/'exact_families.json')
    args = parser.parse_args()
    specs = [('C2', r, p, k) for r, p, k in product((3, 4, 5), (2, 3), (1, 2, 3))]
    specs += [('Klein4', r, 2, k) for r, k in product((3, 4, 5), (1, 2, 3))]
    specs += [('S3', r, p, k) for r, p, k in product((3, 4), (2, 3, 5), (1, 2, 3))]
    specs += [('C4', r, 2, k) for r, k in product((3, 4), (1, 2))]
    cases = [constructed_case(*spec) for spec in specs]
    tiny = exhaustive_small_pairs()
    boundaries = boundary_checks()
    # The empty family is valid only on the zero module; the singleton is I.
    empty, _ = lift_family((), ((),), ((),), 0, 2, 1, 9)
    singleton, _ = lift_family((eye(3),), (eye(3),), (eye(3),), 3, 2, 1, 9)
    need(empty == () and singleton == (eye(3),), 'empty or singleton family boundary')
    totals = dict(constructed_parameter_cases=len(cases),
                  constructed_family_lifts=sum(r['construction_variants'] for r in cases),
                  constructed_projectors=sum(r['summands']*r['construction_variants'] for r in cases),
                  exact_averages=sum(r['averaged_matrices'] for r in cases),
                  non_idempotent_exact_averages=sum(r['non_idempotent_exact_averages'] for r in cases),
                  constructed_newton_iterations=sum(r['newton_iterations'] for r in cases),
                  rigidity_cases=len(cases),
                  distinct_output_family_pairs=sum(r['distinct_output_families'] for r in cases),
                  nonidentity_canonical_conjugators=sum(r['nonidentity_conjugator'] for r in cases),
                  constructed_variants_not_preserving_full_input_depth=sum(2-r['full_input_depth_preserved_variants'] for r in cases),
                  noncommutative_family_lifts=sum(r['construction_variants'] for r in cases if r['noncommutative']),
                  exhaustive_small_family_lifts=tiny['complete_labeled_pairs'],
                  independent_vectors_enumerated=tiny['vectors_enumerated'],
                  total_newton_iterations=sum(r['newton_iterations'] for r in cases)+tiny['newton_iterations']+
                                           boundaries['unavoidable_precision_loss']['newton_iterations'],
                  empty_and_singleton_cases=2)
    need(totals['distinct_output_family_pairs'] > 0 and totals['nonidentity_canonical_conjugators'] > 0,
         'rigidity tests accidentally trivial')
    report = dict(status='PASS: exact finite assertion verified in stated range',schema_version=1,
                  python=platform.python_version(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  predecessor_helpers_sha256=hashlib.sha256((ROOT/'checks/exact_summands.py').read_bytes()).hexdigest(),
                  coefficient_domain='Exact Z and Q, and exact finite rings Z/(p^D).',
                  conventions='Column-vector actions, one conjugation average per input, corner C A C, cubic Newton 3A^2-2A^3, last label complement, U=sum F_i E_i.',
                  randomness=dict(used=False,generator='',seed=None),
                  target_depth=TARGET_DEPTH,constructed_cases=cases,exhaustive_small=tiny,
                  boundaries=boundaries,totals=totals,
                  non_claims=['Does not prove universal lifting or convergence in any complete DVR.',
                              'The high-rank constructed families do not exhaust all quotient families.',
                              'Modular traces are benchmark invariants, not alone proofs of module rank.',
                              'No arithmetic packet, Weil-Deligne, or Hodge-Tate assertion is established.',
                              'The independent vector checks and polynomial factorization still use the shared elementary arithmetic helpers.'])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    need(json.loads(args.output.read_text()) == report, 'JSON roundtrip')
    print(json.dumps(dict(status=report['status'],totals=totals), sort_keys=True))


if __name__ == '__main__':
    main()
