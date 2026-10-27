#!/usr/bin/env python3
"""Complete polynomial identities modulo 2^P, with inherited Euler inputs.

No new coefficient, Bernoulli, or actual-parameter reconstruction is done.
The load-bearing finite assertion is coefficientwise p = A h + R mod 2^P.
"""
import hashlib
import json
from pathlib import Path
import sys


def trim(a):
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def add(a, b, modulus, scale=1):
    return trim([((a[i] if i < len(a) else 0) +
                  scale*(b[i] if i < len(b) else 0)) % modulus
                 for i in range(max(len(a), len(b)))])


def mul(a, b, modulus):
    c = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i+j] = (c[i+j]+x*y) % modulus
    return trim(c)


def evaluate(a, x, modulus):
    y = 0
    for t in reversed(a):
        y = (y*x+t) % modulus
    return y


def v2(a, cap):
    return (a & -a).bit_length()-1 if a else cap


def local_division(p, h, bits):
    """Digitwise division by h, whose complete reduction has degree one."""
    modulus = 1 << bits
    assert h[1] % 2 == 1 and all(x % 2 == 0 for x in h[2:])
    root_bit = h[0] % 2
    a, remainder = [0], 0
    for k in range(bits):
        error = add(add(p, mul(a, h, modulus), modulus, -1),
                    [remainder], modulus, -1)
        assert all(x % (1 << k) == 0 for x in error)
        e = [((x >> k) & 1) for x in error]
        # Euclidean division in F_2[Z] by Z + root_bit.
        q = [0]*max(1, len(e)-1)
        for j in range(len(e)-1, 0, -1):
            if e[j]:
                q[j-1] ^= 1
                e[j] ^= 1
                e[j-1] ^= root_bit
        remainder = (remainder+(e[0] << k)) % modulus
        a = add(a, [x << k for x in trim(q)], modulus)
    assert add(mul(a, h, modulus), [remainder], modulus) == trim(
        [x % modulus for x in p])
    return a, remainder


def critical_point(h, bits):
    c = 0
    for k in range(bits):
        modulus = 1 << (k+1)
        candidates = [d for d in (c, c+(1 << k))
                      if evaluate(h, d, modulus) == 0]
        assert len(candidates) == 1
        c = candidates[0]
    return c


def check_poly(p_full, coefficient_bits, expected=None):
    # Half differentiation can lose one bit, so P is deliberately one less.
    bits = coefficient_bits-1
    modulus = 1 << bits
    assert all((i*p_full[i]) % 2 == 0 for i in range(1, len(p_full)))
    h = trim([(i*p_full[i]//2) % modulus
              for i in range(1, len(p_full))])
    p = trim([x % modulus for x in p_full])
    a, residue = local_division(p, h, bits)
    c = critical_point(h, bits)
    assert evaluate(p, c, modulus) == residue
    # Independent half-precision center test, using the stationary quadratic law.
    center_bits = (bits+1)//2
    d = critical_point(h, center_bits)
    assert evaluate(p, d, modulus) == residue
    if expected is not None:
        assert v2(residue, bits) == expected
    return {'precision': bits, 'cofactor': [str(x) for x in a],
            'constant_remainder': str(residue),
            'valuation_or_lower_bound': v2(residue, bits),
            'critical_center': str(c), 'center_bits_used_for_value': center_bits,
            'coefficientwise_identity': True,
            'independent_half_precision_value_check': True,
            'interpretation': 'nonvanishing certified' if residue else
                'zero residue only; exact vanishing not certified'}


def main(path):
    root = Path(__file__).resolve().parent
    inp = root/'inherited_coefficients.json'
    j = json.loads(inp.read_text())
    out = {'input_sha256': hashlib.sha256(inp.read_bytes()).hexdigest(),
           'arithmetic': 'Python arbitrary-precision integers modulo powers of two',
           'records': [], 'scope': 'Coefficientwise local Jacobian quotient checks'}
    for rec in j['records']:
        jet = [[int(x) for x in row] for row in rec['jet']]
        b = rec['local_coefficient_bits']
        actual = check_poly(jet[0], b, rec['expected_critical_valuation'])
        actual.update({'T': rec['T'], 'eta': '0',
                       'actual_transfer': 'The actual undepletion correction starts above these bits.'})
        assert int(actual['constant_remainder']) == (
            int(rec['depleted_critical_value_residue']) % (1 << (b-1)))
        out['records'].append(actual)
        eta = int(rec['eta_star_residue'])
        m = 1 << b
        planted = [sum(jet[k][i]*pow(eta,k,m) for k in range(len(jet))) % m
                   for i in range(len(jet[0]))]
        control = check_poly(planted, b, b-1)
        control.update({'T': rec['T'], 'eta': str(eta),
                        'scope': 'Independent analytic deformation negative control; not the actual Euler parameter.'})
        out['records'].append(control)
    # Finite rational-polynomial localization counterexample.
    # f=1+2Z+Z^2+256Z^3, h=f'/2=1+Z+384Z^2.
    example = check_poly([1,2,1,256], 80, 8)
    # Exact integer polynomial identity, not merely a modular evaluation:
    # 1152*f - 1151 - 1535*Z = (1+768*Z)*h.
    left = [1152-1151, 2304-1535, 1152, 1152*256]
    right = [1, 1+768, 384+768, 384*768]
    assert left == right
    example.update({'f': [1,2,1,256], 'half_derivative': [1,1,384],
                    'critical_polynomial_discriminant': -1535,
                    'critical_value_expression': '(1151+1535*c)/1152',
                    'critical_value_expression_integer_identity_checked': True,
                    'rational_localization_exists': False})
    out['rational_localization_counterexample'] = example
    out['status'] = 'passed'
    out['nonclaims'] = ['No new actual Euler precision.',
        'No all-index nonvanishing bound.', 'No exact-zero conclusion from a zero residue.',
        'The inherited coefficient provenance is assumed, not rebuilt here.']
    Path(path).write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({'status': out['status'], 'records': [
        {k: r[k] for k in ('T','eta','precision','valuation_or_lower_bound','interpretation')}
        for r in out['records']], 'rational_counterexample_critical_value_valuation': 8}, indent=2))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv)>1 else 'LOCAL_CERTIFICATE_CHECKS.json')
