#!/usr/bin/env python3
"""Exact audit of dyadic Euler tail root laws. Python standard library only.

Run: python3 check_dyadic_tail.py
All rationals use Fraction. Large-row checks use the original tail formula
modulo 2**220 and the proved 4*m-1 cutoff, not floating-point arithmetic.
The proof is in PROOF.md. Finite successes do not supply the universal proof.
"""
from __future__ import annotations
from fractions import Fraction as F
from math import comb, factorial, inf
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
import sys
import time

MAX_N = 512
ROOT_BITS = 64
ROOT_EXPONENTS = tuple(range(4, 9))
BASE = Path(__file__).resolve().parent


def v2_int(x: int) -> int | float:
    x = abs(x)
    return inf if x == 0 else (x & -x).bit_length() - 1


def v2(x: F | int) -> int | float:
    x = F(x)
    return inf if not x else v2_int(x.numerator) - v2_int(x.denominator)


def mod_fraction(x: F | int, bits: int) -> int:
    x = F(x)
    if bits < 1 or x.denominator % 2 == 0:
        raise ValueError('Need positive precision and a dyadically integral rational.')
    modulus = 1 << bits
    return x.numerator * pow(x.denominator, -1, modulus) % modulus


def inverse_coefficients(limit: int) -> list[F]:
    # Reciprocal of (2t/sinh(2t))**2 in even divided-power coordinates.
    h = [F(2 ** (4*m+1), (2*m+1)*(2*m+2)) for m in range(limit+1)]
    k = [F(1)]
    for n in range(1, limit+1):
        k.append(-sum((comb(2*n, 2*j)*h[n-j]*k[j]
                       for j in range(n)), F(0)))
    return k


def bernoulli_even(limit: int) -> list[F]:
    # Independent classical Bernoulli recurrence, with B_1=-1/2.
    b = [F(1)]
    for n in range(1, limit+1):
        z = F(1) - F(2*n+1, 2)
        z += sum((comb(2*n+1, 2*j)*b[j] for j in range(1, n)), F(0))
        b.append(-z / (2*n+1))
    return b


def euler_even(limit: int) -> list[int]:
    # Independent recurrence from cosh(t)*sech(t)=1.
    e = [1]
    for n in range(1, limit+1):
        e.append(-sum(comb(2*n, 2*j)*e[j] for j in range(n)))
    return e


def source(n: int) -> F:
    if n < 0:
        raise ValueError('The rational source helper requires n>=0.')
    return F(3 ** (2*n+2)-1, 4*(2*n+1)*(2*n+2))


def source_mod(z: int, bits: int) -> int:
    """Analytic A(z) mod 2**bits, including its removable point z=-1."""
    modulus = 1 << bits
    if z == -1:
        # A(-1)=-log(9)/8. The omitted logarithm terms have order >=bits.
        value = sum((mod_fraction(F((-1)**(k+1)*8**(k-1), k), bits)
                     for k in range(1, bits+4)), 0)
        return -value % modulus
    exponent = z+1
    denominator = 8*exponent*(2*z+1)
    loss = int(v2_int(denominator))
    numerator = (pow(9, exponent, 1 << (bits+loss))-1) % (1 << (bits+loss))
    assert numerator % (1 << loss) == 0
    return ((numerator >> loss) * pow(denominator // (1 << loss), -1, modulus)) % modulus


def root_function_mod(x: int, bits: int, a: int, beta: list[F]) -> int:
    """G_a(x) mod 2**bits. Omitted j>=2 have Gauss order >=3j-3."""
    if a < 4:
        raise ValueError('The simple-root family requires a>=4.')
    r = (1 << a)-1
    last = (bits+3)//3
    if r+last >= len(beta):
        raise ValueError('Insufficient inverse coefficients for requested precision.')
    modulus = 1 << bits
    p = 1
    answer = 0
    for j in range(last+1):
        if j:
            p = p*(x-j+1)*(2*x-(2*j-1)) % modulus
        gamma = F((1 << (a-4))*8**j)*beta[r+j]/beta[r]
        assert v2(gamma) >= 0
        answer = (answer + mod_fraction(gamma, bits)*p*source_mod(x-j, bits)) % modulus
    return answer


def root_lift(a: int, bits: int, beta: list[F]) -> tuple[int, list[dict]]:
    alpha = 0
    history = []
    for b in range(1, bits+1):
        if root_function_mod(alpha, b, a, beta):
            alpha += 1 << (b-1)
        assert root_function_mod(alpha, b, a, beta) == 0
        assert root_function_mod(alpha ^ (1 << (b-1)), b, a, beta) != 0
        history.append({'bits': b, 'alpha': alpha,
                        'rho': (alpha+(1 << a)-1) % (1 << b)})
    return alpha, history


def original_tail_mod(n: int, depth: int, bits: int, kappa: list[F]) -> int:
    """Original, unfactored tail. Terms with 4*m-1>=bits vanish."""
    modulus = 1 << bits
    last = min(n, bits//4)
    if last >= len(kappa):
        raise ValueError('Insufficient coefficients.')
    answer = 0
    for m in range(depth+1, last+1):
        answer = (answer + mod_fraction(kappa[m], bits)*(comb(2*n, 2*m) % modulus)
                  * source_mod(n-m, bits)) % modulus
    return answer


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    started = datetime.now(timezone.utc).isoformat()
    clock = time.perf_counter()
    kappa = inverse_coefficients(MAX_N)
    bernoulli = bernoulli_even(MAX_N)
    euler = euler_even(MAX_N)
    sources = [source(n) for n in range(MAX_N+1)]
    beta = [kappa[m]/(4**m*factorial(2*m)) for m in range(MAX_N+1)]
    for m in range(1, MAX_N+1):
        assert kappa[m] == -2**(4*m)*(2*m-1)*bernoulli[m]
        assert v2(kappa[m]) == 4*m-1
        assert v2(beta[m]) == m.bit_count()-1
    for n, value in enumerate(sources):
        assert v2(value) == 0
        assert source_mod(n, 32) == mod_fraction(value, 32)
    # Independent rational checks on negative analytic-source inputs.
    for z in range(-32, -1):
        rational_source = (F(9)**(z+1)-1) / (8*(z+1)*(2*z+1))
        assert source_mod(z, 32) == mod_fraction(rational_source, 32)

    roots = {}
    lifts = {}
    for a in ROOT_EXPONENTS:
        roots[a], lifts[a] = root_lift(a, ROOT_BITS, beta)
        assert v2_int(roots[a]) == a-4
    alpha128, lift128 = root_lift(4, 128, beta)
    rho128 = (alpha128+15) % (1 << 128)
    r_to_a = {(1 << a)-1: a for a in ROOT_EXPONENTS}

    counts = dict(full_reconstruction=0, nonempty_rational_tails=0,
                  tied_minimum_tails=0, root_law=0, low_popcount_law=0,
                  original_modular_vs_rational=0, factored_modular_vs_rational=0,
                  empty_tails=0)
    max_minima = 0
    selected = []
    n16_certificate = {}
    for n in range(MAX_N+1):
        ts = [kappa[m]*comb(2*n, 2*m)*sources[n-m] for m in range(n+1)]
        assert sum(ts, F(0)) == euler[n]
        counts['full_reconstruction'] += 1
        assert F(euler[n])-sum(ts, F(0)) == 0
        counts['empty_tails'] += 1
        acc = F(0)
        minimum = inf
        multiplicity = 0
        for m in range(n, 0, -1):
            acc += ts[m]
            weight = 4*m-1+m.bit_count()+(n-m).bit_count()-n.bit_count()
            assert v2(ts[m]) == weight
            if weight < minimum:
                minimum, multiplicity = weight, 1
            elif weight == minimum:
                multiplicity += 1
            actual = v2(acc)
            assert actual >= minimum
            if multiplicity % 2:
                assert actual == minimum
            else:
                assert actual > minimum
            counts['nonempty_rational_tails'] += 1
            counts['tied_minimum_tails'] += int(multiplicity > 1)
            max_minima = max(max_minima, multiplicity)
            if m.bit_count() <= 4 and m != 15:
                assert actual == weight
                counts['low_popcount_law'] += 1
            if m in r_to_a:
                a = r_to_a[m]
                rho = (roots[a]+m) % (1 << ROOT_BITS)
                difference = (n-rho) % (1 << ROOT_BITS)
                assert difference != 0  # the root precision resolves this test
                predicted = weight+4-a+int(v2_int(difference))
                assert actual == predicted
                counts['root_law'] += 1
                normalized = (1 << (a-4))*acc/(kappa[m]*comb(2*n, 2*m))
                assert mod_fraction(normalized, 32) == root_function_mod(n-m, 32, a, beta)
                counts['factored_modular_vs_rational'] += 1
            if m == 15:
                assert mod_fraction(acc, 90) == original_tail_mod(n, 14, 90, kappa)
                counts['original_modular_vs_rational'] += 1
                if n in (16,18,20,24,32,48,80,112,176,432):
                    selected.append(dict(N=n,M=14,minimum_weight=int(minimum),
                                         tail_valuation=int(actual),extra=int(actual-minimum)))
            if n == 16 and m == 15:
                n16_certificate = dict(tail=str(acc), valuation=int(actual),
                    tail_divided_by_2_to_68=str(acc/2**68),
                    normalized_term_residues_mod_64=[mod_fraction(ts[j]/2**63,6) for j in (15,16)])

    # Three tied minimum weights far outside a small integer scan.
    huge = 1 << 68
    offsets = []
    relative_weights = []
    for d in range(18):
        m = huge-d
        w = 4*m-1+m.bit_count()+d.bit_count()-huge.bit_count()
        relative_weights.append([d, w-(4*huge-1)])
        assert w >= 4*huge-1
        if w == 4*huge-1:
            offsets.append(d)
    assert offsets == [0,16,17]

    large_rows = []
    for n in (9392,2083857584,4183939833681749168):
        leading = 59+int(v2_int(comb(n,15)))
        difference = (n-rho128) % (1 << 128)
        assert difference
        extra = int(v2_int(difference))
        residue = original_tail_mod(n,14,220,kappa)
        assert residue and v2_int(residue) == leading+extra < 220
        large_rows.append(dict(N=n,M=14,leading_weight=leading,extra=extra,
                     exact_tail_valuation=leading+extra,modulus_exponent=220,
                     normalized_residue_mod_16=(residue >> (leading+extra)) % 16))

    result = {
        'status':'PASS', 'arithmetic':'exact rational and integer modular arithmetic',
        'max_half_index':MAX_N, 'counts':counts,
        'maximum_minimum_multiplicity_in_bounded_scan':max_minima,
        'root_family':{'a_values':list(ROOT_EXPONENTS),'precision_bits':ROOT_BITS,
            'rho_residues':{str(a):(roots[a]+(1 << a)-1) % (1 << ROOT_BITS) for a in roots}},
        'rho_4_mod_2_to_128':rho128,'rho_4_lifts':lift128,
        'selected_rational_tails':selected,'N16_certificate':n16_certificate,
        'large_row_original_kernel_checks':large_rows,
        'three_minima_counterexample':{'N':huge,'M':huge-18,
            'minimum_weight':4*huge-1,'minimum_offsets_N_minus_m':offsets,
            'relative_weights_by_offset':relative_weights,
            'scope':'exact weights only; the enormous Euler number was not computed'},
        'non_claims':['No Lean compilation in this run.',
            'No historical-priority claim.',
            'Finite tests alone do not prove the universal statements in PROOF.md.',
            'The simple-root theorem does not classify every truncation depth.']}
    output = BASE/'RESULTS.json'
    output.write_text(json.dumps(result,indent=2)+'\n')
    elapsed = time.perf_counter()-clock
    manifest = {
        'schema_version':1,'claim_id':'dyadic-euler-tail-binary-edge-root-laws',
        'repository':{'commit':'not applicable: standalone newly created audit','dirty':False},
        'command':'python3 check_dyadic_tail.py',
        'environment':{'software':[sys.version,platform.platform()],
                       'hardware':f'{platform.machine()}, {os.cpu_count()} logical CPUs reported'},
        'mathematics':{'assertion_tested':'Exact reconstruction, coefficient weights, root laws, and counterexample in RESULTS.json',
            'coefficient_domain':'Q via fractions.Fraction; Z/(2^k) via arbitrary-precision integers',
            'conventions':'E_0=1,E_2=-1,E_4=5; N indexes E_(2N); v2(0)=infinity; depth M retains m=0..M',
            'inputs':['Displayed exact source and inverse definitions; no external numerical data'],
            'bounds':{'max_half_index':MAX_N,'root_a_values':list(ROOT_EXPONENTS),
                      'root_bits':64,'a4_extra_root_bits':128,'large_row_modulus_bits':220},
            'non_claims':result['non_claims']},
        'randomness':{'used':False,'generator':'none','seed':None},
        'run':{'started_at':started,'runtime_seconds':elapsed,'exit_status':0},
        'outputs':[{'path':'RESULTS.json','sha256':sha256(output)}],
        'checks':['Independent Bernoulli recurrence versus inverse-series recurrence',
                  'Euler recurrence versus complete dyadic reconstruction',
                  'All nonempty tails in the stated finite range',
                  'Factored root evaluator versus rational tails',
                  'Original unfactored modular kernel versus rational tails and large-row predictions',
                  'All 18 exact weights in the three-minimum counterexample'],
        'result':'All assertions passed.',
        'residual_risks':['Universal proof is prose, not machine-checked.',
                          'Standalone provenance has no pre-existing repository commit.',
                          'Manifest fields and hashes are checked locally; bundled skill validator was not run.'],
        'input_hashes':{'check_dyadic_tail.py':sha256(Path(__file__)),
                        'PROOF.md':sha256(BASE/'PROOF.md')}}
    for entry in manifest['outputs']:
        assert sha256(BASE/entry['path']) == entry['sha256']
    assert all(manifest[field] for field in ('claim_id','command','environment','mathematics','checks','result'))
    (BASE/'MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':'PASS','counts':counts,'runtime_seconds':elapsed,
                      'large_row_checks':large_rows},indent=2))


if __name__ == '__main__':
    main()
