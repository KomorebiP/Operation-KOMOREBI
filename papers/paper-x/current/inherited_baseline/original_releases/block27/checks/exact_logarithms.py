"""Block 20: deterministic exact finite tests of nilpotent exponential/logarithm.

No project or third-party imports. All scalar arithmetic uses Fraction or int.
The finite constructed families below do not classify all nilpotent matrices.
"""
from fractions import Fraction as Q
from math import factorial
from pathlib import Path
import argparse
import hashlib
import json
import platform

ROOT = Path(__file__).resolve().parents[1]
TIMES = (Q(1), Q(-2), Q(1, 2), Q(-2, 3), Q(3, 5))
PARTITIONS = tuple((n,) for n in range(1, 13)) + (
    (1, 1, 1), (2, 2), (1, 2, 3), (2, 3, 4), (1, 4, 6), (2, 4, 6))


def need(value, message):
    if not value:
        raise AssertionError(message)


def zero(m, n=None):
    return tuple(tuple(Q(0) for _ in range(m if n is None else n)) for _ in range(m))


def eye(n):
    return tuple(tuple(Q(i == j) for j in range(n)) for i in range(n))


def add(a, b):
    return tuple(tuple(x + y for x, y in zip(u, v)) for u, v in zip(a, b))


def scale(c, a):
    return tuple(tuple(c*x for x in row) for row in a)


def sub(a, b):
    return add(a, scale(-1, b))


def mul(a, b):
    need(len(a[0]) == len(b), 'incompatible matrix shapes')
    out = [[Q(0) for _ in b[0]] for _ in a]
    for i, row in enumerate(a):
        for k, x in enumerate(row):
            if x:
                for j, y in enumerate(b[k]):
                    if y:
                        out[i][j] += x*y
    return tuple(tuple(row) for row in out)


def powers(a, count):
    out = [eye(len(a))]
    for _ in range(count):
        out.append(mul(out[-1], a))
    return out


def rref(a):
    rows = [list(row) for row in a]
    pivot_row = 0
    for col in range(len(rows[0])):
        found = next((i for i in range(pivot_row, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot_row], rows[found] = rows[found], rows[pivot_row]
        p = rows[pivot_row][col]
        rows[pivot_row] = [x/p for x in rows[pivot_row]]
        for i in range(len(rows)):
            if i != pivot_row and rows[i][col]:
                c = rows[i][col]
                rows[i] = [x-c*y for x, y in zip(rows[i], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return tuple(tuple(row) for row in rows)


def inverse(a):
    n = len(a)
    reduced = rref(tuple(tuple(a[i]) + eye(n)[i] for i in range(n)))
    need(tuple(row[:n] for row in reduced) == eye(n), 'singular change of basis')
    inv = tuple(row[n:] for row in reduced)
    need(mul(a, inv) == eye(n) and mul(inv, a) == eye(n), 'inverse verification')
    return inv


def conjugate(s, a, si):
    return mul(mul(s, a), si)


def frame(n, variant):
    if variant == 0:
        return eye(n), eye(n)
    # Different lower/upper shears mix direct-sum blocks. Diagonal factors make
    # the changes of basis rational and nonintegral, even at dimension one.
    lo = tuple(tuple(Q(i == j) + (Q((-1)**i, i+2) if i == j+1 else 0)
                     for j in range(n)) for i in range(n))
    up = tuple(tuple(Q(i == j) + (Q(variant*(i+1), i+3) if j == i+1 else 0)
                     for j in range(n)) for i in range(n))
    diag = tuple(tuple(Q((i+2)**variant, i+1) if i == j else Q(0)
                       for j in range(n)) for i in range(n))
    s = mul(mul(lo, diag), up)
    return s, inverse(s)


def jordan(parts):
    n = sum(parts)
    a = [list(row) for row in zero(n)]
    start = 0
    for length in parts:
        for i in range(start, start+length-1):
            a[i][i+1] = Q(1)
        start += length
    return tuple(tuple(row) for row in a)


def exp_nil(a, bound):
    ps = powers(a, bound)
    need(ps[-1] == zero(len(a)), 'exponential nilpotency bound incorrect')
    out = zero(len(a))
    for j in range(bound):
        out = add(out, scale(Q(1, factorial(j)), ps[j]))
    return out


def log_unipotent(u, bound):
    x = sub(u, eye(len(u)))
    ps = powers(x, bound)
    need(ps[-1] == zero(len(x)), 'logarithm nilpotency bound incorrect')
    out = zero(len(x))
    for j in range(1, bound):
        out = add(out, scale(Q((-1)**(j+1), j), ps[j]))
    return out


def closed_jordan(parts, t, logarithm=False):
    n = sum(parts)
    out = [list(row) for row in zero(n)]
    start = 0
    for length in parts:
        for i in range(length):
            for j in range(i, length):
                d = j-i
                if logarithm:
                    value = Q((-1)**(d+1), d) if d else Q(0)
                else:
                    value = t**d/factorial(d)
                out[start+i][start+j] = value
        start += length
    return tuple(tuple(row) for row in out)


def conv(a, b):
    n = len(a)
    return tuple(sum((a[j]*b[i-j] for j in range(i+1)), Q(0)) for i in range(n))


def series_compose(outer, inner):
    n = len(outer)
    term = (Q(1),) + (Q(0),)*(n-1)
    out = (Q(0),)*n
    for c in outer:
        out = tuple(x+c*y for x, y in zip(out, term))
        term = conv(term, inner)
    return out


def polynomial_checks():
    cases = 0
    for n in range(1, 21):
        exp = tuple(Q(1, factorial(j)) for j in range(n))
        log = (Q(0),) + tuple(Q((-1)**(j+1), j) for j in range(1, n))
        exp_minus_one = (Q(0),) + exp[1:]
        expected_x = tuple(Q(i == 1) for i in range(n))
        expected_1x = tuple(Q(i in (0, 1)) for i in range(n))
        need(series_compose(log, exp_minus_one) == expected_x, 'coefficient log(exp)')
        need(series_compose(exp, log) == expected_1x, 'coefficient exp(log)')
        cases += 1
    return cases


def matrix_checks():
    records = []
    inverse_cases = 0
    for parts in PARTITIONS:
        n, bound = sum(parts), max(parts)
        j = jordan(parts)
        for variant in range(3):
            s, si = frame(n, variant)
            a = conjugate(s, j, si)
            need(powers(a, bound)[-1] == zero(n), 'conjugate nilpotency')
            if bound > 1:
                need(powers(a, bound-1)[-1] != zero(n), 'nilpotency index dropped')
            lp = log_unipotent(add(eye(n), a), bound)
            need(lp == conjugate(s, closed_jordan(parts, Q(1), True), si),
                 'closed Jordan logarithm and naturality')
            need(exp_nil(lp, bound) == add(eye(n), a), 'exp(log(1+N))')
            inverse_cases += 1
            for t in TIMES:
                e = exp_nil(scale(t, a), bound)
                need(e == conjugate(s, closed_jordan(parts, t), si),
                     'independent closed Jordan exponential')
                need(log_unipotent(e, bound) == scale(t, a), 'log(exp(tN))')
                need(scale(1/t, log_unipotent(e, bound)) == a, 'nonzero sample recovery')
                need(log_unipotent(e, bound+2) == scale(t, a), 'cutoff independence')
                x = sub(e, eye(n))
                need(rref(x) == rref(a), 'kernel equality by exact row reduction')
                rank = sum(any(row) for row in rref(x))
                need(rank == n-len(parts), 'independent Jordan rank formula')
                need(mul(e, exp_nil(scale(-t, a), bound)) == eye(n), 'inverse exponential')
                records.append({'parts': list(parts), 'basis': variant, 't': str(t),
                                'dimension': n, 'nilpotency_index': bound, 'rank': rank})
    return records, inverse_cases


def hom_jordan(a, b, s):
    # Source dimension a, target dimension b. The image of the last source
    # basis vector is target e_s. Its annihilation by J_b^a determines a hom.
    return tuple(tuple(Q(i == s-a+1+j) for j in range(a)) for i in range(b))


def rectangular_checks():
    cases = 0
    shape_counts = {}
    for a in range(1, 7):
        for b in range(1, 7):
            sa, sai = frame(a, 1)
            sb, sbi = frame(b, 2)
            na = conjugate(sa, jordan((a,)), sai)
            nb = conjugate(sb, jordan((b,)), sbi)
            for generator in range(min(a, b)):
                h = mul(mul(sb, hom_jordan(a, b, generator)), sai)
                need(mul(nb, h) == mul(h, na), 'rectangular generator is not intertwiner')
                for t in (Q(-2, 3), Q(3, 5)):
                    ea, eb = exp_nil(scale(t, na), a), exp_nil(scale(t, nb), b)
                    need(mul(eb, h) == mul(h, ea), 'rectangular exponential naturality')
                    la, lb = log_unipotent(ea, a), log_unipotent(eb, b)
                    need(mul(lb, h) == mul(h, la), 'rectangular logarithm naturality')
                    need(mul(scale(1/t, lb), h) == mul(h, scale(1/t, la)),
                         'rectangular monodromy recovery')
                    cases += 1
                    key = f'{b}x{a}'
                    shape_counts[key] = shape_counts.get(key, 0)+1
    return cases, shape_counts


def dilation(n, z):
    return tuple(tuple(Q(3)**(-z*i) if i == j else Q(0) for j in range(n))
                 for i in range(n))


def rho(a, s, si, t, z):
    n = len(a)
    return mul(exp_nil(scale(t, a), n), conjugate(s, dilation(n, z), si))


def reconstructed_checks():
    records = []
    # Here the group is the explicit rational affine group with multiplication
    # (t,z)(u,w)=(t+3^z*u,z+w); r(t,z)=diag(3^(-zi)).
    samples = ((Q(-2), -1), (Q(1, 2), 0), (Q(3, 5), 1))
    group_laws = 0
    for a, b in ((1, 4), (2, 6), (4, 6), (6, 12)):
        sa, sai = frame(a, 1)
        sb, sbi = frame(b, 2)
        na = conjugate(sa, jordan((a,)), sai)
        nb = conjugate(sb, jordan((b,)), sbi)
        inclusion = tuple(tuple(Q(i == j) for j in range(a)) for i in range(b))
        h = mul(mul(sb, inclusion), sai)
        sample_t = Q(-2, 3)
        ea = rho(na, sa, sai, sample_t, 0)
        eb = rho(nb, sb, sbi, sample_t, 0)
        ra = scale(1/sample_t, log_unipotent(ea, a))
        rb = scale(1/sample_t, log_unipotent(eb, b))
        need(ra == na and rb == nb, 'recovered monodromy differs')
        for t, z in samples:
            pa, pb = rho(na, sa, sai, t, z), rho(nb, sb, sbi, t, z)
            need(mul(pb, h) == mul(h, pa), 'reconstructed representations do not intertwine')
            original_a = conjugate(sa, dilation(a, z), sai)
            original_b = conjugate(sb, dilation(b, z), sbi)
            recovered_a = mul(exp_nil(scale(-t, ra), a), pa)
            recovered_b = mul(exp_nil(scale(-t, rb), b), pb)
            need(recovered_a == original_a and recovered_b == original_b,
                 'original group action not recovered')
            need(mul(recovered_b, h) == mul(h, recovered_a), 'recovered r intertwining')
            for u, w in samples:
                product = rho(nb, sb, sbi, t+Q(3)**z*u, z+w)
                need(mul(pb, rho(nb, sb, sbi, u, w)) == product, 'affine representation law')
                group_laws += 1
            records.append({'source_dimension': a, 'target_dimension': b,
                            't': str(t), 'z': z, 'sample_t': str(sample_t)})
    return records, group_laws


def boundary_checks():
    truncation = []
    for degree in range(2, 7):
        n = degree+2
        a = jordan((n,))
        x = sub(exp_nil(a, n), eye(n))
        ps = powers(x, degree)
        short = zero(n)
        for j in range(1, degree+1):
            short = add(short, scale(Q((-1)**(j+1), j), ps[j]))
        defect = sub(short, a)
        expected = Q((-1)**(degree+1), degree+1)
        need(defect != zero(n), 'short logarithm unexpectedly recovers N')
        need(defect[0][degree+1] == expected, 'omitted leading coefficient incorrect')
        truncation.append({'log_degree': degree, 'chain_length': n,
                           'defect_entry_0_degree_plus_1': str(expected)})
    a = jordan((6,))
    need(a != zero(6), 'zero sample boundary requires nonzero monodromy')
    need(exp_nil(scale(0, a), 6) == exp_nil(zero(6), 6) == eye(6), 'zero sample collision')
    need(rref(sub(exp_nil(scale(0, a), 6), eye(6))) != rref(a), 'zero sample kernel control')
    aa = ((Q(0), Q(1), Q(0)), (Q(0), Q(0), Q(0)), (Q(0), Q(0), Q(0)))
    bb = ((Q(0), Q(0), Q(0)), (Q(0), Q(0), Q(1)), (Q(0), Q(0), Q(0)))
    need(mul(aa, bb) != mul(bb, aa), 'noncommuting boundary accidentally commutes')
    defect = sub(mul(exp_nil(aa, 3), exp_nil(bb, 3)), exp_nil(add(aa, bb), 3))
    need(defect[0][2] == Q(1, 2), 'noncommutative exponential boundary')
    return {'fixed_degree_failures': truncation, 'zero_sample_collision_dimension': 6,
            'zero_sample_kernel_equality_rejected': True,
            'noncommuting_exp_product_defect_0_2': '1/2'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    polynomials = polynomial_checks()
    matrices, inverse_cases = matrix_checks()
    rectangles, shapes = rectangular_checks()
    reconstructed, group_laws = reconstructed_checks()
    boundaries = boundary_checks()
    result = {
        'block': 20,
        'verdict': 'All implemented finite assertions passed in the declared constructed range.',
        'arithmetic': 'Python integers and fractions.Fraction; no floating point or external libraries.',
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'python_version': platform.python_version(),
        'counts': {'polynomial_truncation_degrees': polynomials,
                   'matrix_exp_log_samples': len(matrices),
                   'matrix_exp_of_log_samples': inverse_cases,
                   'rectangular_intertwiner_samples': rectangles,
                   'reconstructed_action_samples': len(reconstructed),
                   'affine_group_law_samples': group_laws,
                   'short_log_failure_examples': len(boundaries['fixed_degree_failures'])},
        'matrix_samples': matrices,
        'rectangular_shapes': shapes,
        'reconstructed_action_samples': reconstructed,
        'boundaries': boundaries,
        'non_claims': [
            'These are finite deterministic constructed examples, not a universal proof.',
            'The rectangular census ranges over listed Jordan-module generators, not every rational matrix.',
            'No actual arithmetic Galois-to-Weil-Deligne attachment or period comparison is tested.',
            'No analytic convergence, theorem novelty, or completeness of the five arithmetic claims is asserted.'
        ]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'verdict': result['verdict'], 'counts': result['counts']}, sort_keys=True))


if __name__ == '__main__':
    main()
