"""Bounded exact check of the shifted D Jacobi model and actual height control."""
from fractions import Fraction as F
from math import factorial
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_hankel_separation import bernoulli, val, v_int, add, mul, scale


def main():
    output = Path(sys.argv[1])
    b = bernoulli(256)
    D = [(2 - 4 ** n) * b[2 * n] for n in range(129)]
    model_records = []
    coefficient_checks = 0
    moment_checks = 0
    first_exit_checks = 0
    for r in range(7):
        def moment(p):
            return sum(t * D[r + j] for j, t in enumerate(p))
        polys = []
        norms = []
        for n in range(6):
            p = [F(0)] * n + [F(1)]
            for old, norm in zip(polys, norms):
                p = add(p, scale(old, -moment(mul(p, old)) / norm))
            norm = moment(mul(p, p))
            assert val(norm) == 4 * n + 4 * v_int(factorial(n))
            polys.append(p)
            norms.append(norm)
        diag = [moment([F(0)] + mul(p, p)) / norm for p, norm in zip(polys, norms)]
        sub = [F(0)] + [norms[n] / norms[n-1] for n in range(1, 6)]
        for n, bn in enumerate(diag):
            assert bn == 1 or val(bn - 1) >= 2
            if n:
                assert val(sub[n]) == 4 + 4 * v_int(n)
            coefficient_checks += 1
        for m in range(1, 6):
            bound = 4 * m + 4 * v_int(factorial(m))
            vector = [F(1)] + [F(0)] * (m - 1)
            errors = []
            for q in range(25):
                model = vector[0]
                exact = D[r + q] / D[r]
                err = exact - model
                assert val(model) == 0
                if q < 2 * m:
                    assert err == 0
                else:
                    assert err == 0 or val(err) >= bound
                if q == 2 * m:
                    assert val(err) == bound
                    first_exit_checks += 1
                errors.append(val(err))
                moment_checks += 1
                nxt = [F(0)] * m
                # Monic basis gives the same 0,0 matrix-power entry.
                for n, z in enumerate(vector):
                    nxt[n] += diag[n] * z
                    if n + 1 < m:
                        nxt[n+1] += z
                    if n:
                        nxt[n-1] += sub[n] * z
                vector = nxt
            model_records.append({'r': r, 'm': m, 'uniform_error_bound': bound,
                                  'error_valuations_q0_through24': errors})
    height_records = []
    for r in [16, 32, 40, 64, 128]:
        value = D[r]
        height = max(abs(value.numerator), value.denominator)
        assert val(value) == 0
        if r >= 40:
            assert height > 2 ** (2 * r)
        height_records.append({'r': r, 'dyadic_valuation': val(value),
                               'height_floor_log2': height.bit_length() - 1,
                               'undepletion_exponent_2r_minus25': 2 * r - 25,
                               'numerator_bits': abs(value.numerator).bit_length(),
                               'denominator_bits': value.denominator.bit_length()})
    payload = {'status': 'passed', 'coefficient_checks': coefficient_checks,
               'moment_checks': moment_checks, 'first_exit_checks': first_exit_checks,
               'model_records': model_records, 'height_records': height_records,
               'non_claims': ['No stationary value computed', 'No T digits',
                              'No proof of actual Euler nonintersection',
                              'Universal statements use separate proofs']}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + '\n')
    print(json.dumps({k: payload[k] for k in ['status', 'coefficient_checks',
                                            'moment_checks', 'first_exit_checks']}))


if __name__ == '__main__':
    main()
