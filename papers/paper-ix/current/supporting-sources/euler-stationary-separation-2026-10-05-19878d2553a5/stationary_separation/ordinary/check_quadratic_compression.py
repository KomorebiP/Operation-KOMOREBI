#!/usr/bin/env python3
"""Exact degree-two preparation of fixed, previously recorded Euler controls."""
from pathlib import Path
import json, sys, hashlib

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'bernoulli_closure/separation/carry_adapted/inherited_actual.json'


def trim(p):
    while p and p[-1] == 0:
        p.pop()
    return p or [0]


def mul(p, q):
    z = [0] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            z[i+j] += a*b
    return trim(z)


def divmod2(p, w):
    p = trim([v & 1 for v in p])
    quotient = [0] * max(1, len(p)-2)
    while len(p) >= 3:
        shift = len(p)-3
        quotient[shift] = 1
        for i in range(3):
            p[shift+i] ^= w[i] & 1
        trim(p)
    return trim(quotient), p


def prepare(coeff, p):
    mod = 1 << p
    coeff = trim([int(a) % mod for a in coeff])
    scalar = coeff[2]
    inverse = pow(scalar, -1, mod)
    coeff = [a*inverse % mod for a in coeff]
    assert coeff[2] == 1
    assert coeff[1] % 2 == 0
    assert all(a % 256 == 0 for a in coeff[3:])
    w = [coeff[0] % 256, coeff[1] % 256, 1]
    u = [1]
    for k in range(8, p):
        product = mul(u, w)
        n = max(len(coeff), len(product))
        residual = [(coeff[i] if i < len(coeff) else 0) -
                    (product[i] if i < len(product) else 0) for i in range(n)]
        assert all(a % (1 << k) == 0 for a in residual)
        quotient, remainder = divmod2([a >> k for a in residual], w)
        for i, a in enumerate(remainder):
            w[i] += a << k
        u.extend([0] * max(0, len(quotient)-len(u)))
        for i, a in enumerate(quotient):
            u[i] += a << k
        # The quadratic stays monic and the cofactor stays 1 modulo 256.
        assert w[2] == 1 and w[1] % 2 == 0
        assert u[0] % 256 == 1 and all(a % 256 == 0 for a in u[1:])
    product = mul(u, w)
    n = max(len(coeff), len(product))
    assert all(((coeff[i] if i < len(coeff) else 0) -
                (product[i] if i < len(product) else 0)) % mod == 0 for i in range(n))
    return w, u, scalar


def valuation(n, cap=None):
    if n == 0:
        return cap
    n = abs(n)
    v = (n & -n).bit_length()-1
    return min(v, cap) if cap is not None else v


def evaluate(poly, x, mod):
    y = 0
    for a in reversed(poly):
        y = (y*x+a) % mod
    return y


def critical(poly, p):
    # Input is complete modulo 2^p; h=f'/2 is complete modulo 2^(p-1).
    half_derivative = [i*int(poly[i])//2 for i in range(1, len(poly))]
    assert all(i*int(poly[i]) % 2 == 0 for i in range(1, len(poly)))
    c = 0
    for k in range(p-1):
        if evaluate(half_derivative, c, 1 << (k+1)):
            c += 1 << k
    assert evaluate(half_derivative, c, 1 << (p-1)) == 0
    return c, evaluate(poly, c, 1 << p)


def main(output):
    data = json.loads(INPUT.read_text())
    rows = []
    for record in data['records']:
        previous_w = None
        previous_p = None
        for p in [16, 24, 32, 48, 64, 80, 93]:
            assert p <= record['bits']
            coeff = trim([int(a) % (1 << p) for a in record['K']])
            w, u, scalar = prepare(coeff, p)
            if previous_w is not None:
                assert all((a-b) % (1 << previous_p) == 0 for a,b in zip(w, previous_w))
            previous_w, previous_p = w, p
            a, twice_b, _ = w
            b = twice_b//2
            delta = b*b-a
            c, phi = critical(coeff, p)
            vd = valuation(delta, p)
            vp = valuation(phi, p)
            assert vd == vp == min(record['expected_phi_valuation'], p)
            # Exact finite form of delta = -w(c) + (tau*w(c)/2)^2.
            # Avoid division by two: 4delta = W'(c)^2 - 4W(c).
            modulus = 1 << p
            wc = evaluate(w, c, modulus)
            wpc = (2*c+twice_b) % modulus
            uc = evaluate(u, c, modulus)
            upc = evaluate([i*u[i] for i in range(1,len(u))], c, modulus)
            assert (wpc*uc + wc*upc) % (1 << (p-1)) == 0
            assert (4*delta - (wpc*wpc-4*wc)) % modulus == 0
            assert (scalar*uc*wc-phi) % modulus == 0
            rows.append({'T': record['T'], 'precision': p,
                         'input_degree':len(coeff)-1, 'prepared_degree':2,
                         'a':str(a), 'twice_b':str(twice_b),
                         'discriminant_over_4':str(delta),
                         'delta_integer_bits':abs(delta).bit_length(),
                         'delta_valuation_capped_at_precision':vd,
                         'actual_phi_valuation_capped_at_precision':vp,
                         'nonzero_residue_certified':vd < p})
    sharp = []
    for p in range(6,130,2):
        mod = 1 << p
        b = ((-2*pow(3,-1,mod)) % mod)//2
        a = pow(9,-1,mod)
        delta = b*b-a
        C = {0:10, 2:4, 4:7}[p % 6]
        assert delta == mod*(mod-C)//9
        assert delta != 0 and valuation(delta) == p + valuation(C)
        assert abs(delta).bit_length() == 2*p-3
        # These are approximants to the fixed rational polynomial (Z-1/3)^2.
        assert (9*a-1) % mod == 0 and (3*2*b+2) % mod == 0
        sharp.append({'precision':p,'delta_bits':abs(delta).bit_length(),
                      'delta_valuation':valuation(delta),'exact_critical_value':0})
    result = {'status':'passed', 'input_sha256':hashlib.sha256(INPUT.read_bytes()).hexdigest(),
              'actual_controls':rows,'sharp_fixed_rational_double_root_control':sharp,
              'counts':{'actual_quadratic_lifts':len(rows),'sharp_controls':len(sharp)},
              'nonclaims':['No additional multiplier digits or new T values',
                           'No exact critical-point algebraicity assumed',
                           'No universal actual stationary nonvanishing proof',
                           'Finite nonzero integer discriminants alone do not certify nonzero limits']}
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'counts':result['counts'],
                      'actual_summary':[{k:r[k] for k in ['T','precision','input_degree','delta_integer_bits','delta_valuation_capped_at_precision','nonzero_residue_certified']} for r in rows]},indent=2))

if __name__ == '__main__':
    main(sys.argv[1])
