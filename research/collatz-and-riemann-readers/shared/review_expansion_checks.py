"""Independent bounded controls for the expanded conjecture manuscripts.

All load-bearing arithmetic controls use Python integers or Fraction. The
Hermite controls integrate polynomials against the exact normalized Gaussian
moment functional. Finite examples are not proofs of either conjecture.
"""

from fractions import Fraction as F
from decimal import Decimal, localcontext
from itertools import product
from math import comb, factorial, gcd
from pathlib import Path
import argparse
import json
import platform


def step(n):
    m = 3 * n + 1
    a = 0
    while m % 2 == 0:
        m //= 2
        a += 1
    return m, a


def packet(word):
    s = c = 0
    for a in word:
        c = 3 * c + 2**s
        s += a
    modulus = 2 ** (s + 1)
    residue = ((2**s - c) * pow(3 ** len(word), -1, modulus)) % modulus
    return s, c, modulus, residue


def mu(n):
    value = 1
    p = 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            value = -value
            if n % p == 0:
                return 0
            while n % p == 0:
                n //= p
        p += 1
    return -value if n > 1 else value


def divisors(q):
    return [b for b in range(1, q + 1) if q % b == 0]


def weight(k, n):
    r = F(1, n * n)
    return r * (1 - r) ** k


def p_add(a, b):
    return [
        (a[i] if i < len(a) else F()) + (b[i] if i < len(b) else F())
        for i in range(max(len(a), len(b)))
    ]


def p_mul(a, b):
    result = [F()] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result


def gaussian_moment(degree):
    if degree % 2:
        return F()
    k = degree // 2
    return F(factorial(2 * k), 4**k * factorial(k))


def integrate_polynomial(p):
    return sum((x * gaussian_moment(i) for i, x in enumerate(p)), F())


def run_checks():
    ordered = {}
    for word in ((1, 3), (3, 1)):
        s, c, mod, res = packet(word)
        assert (s, c, mod, res) == (
            (4, 5, 32, 19) if word == (1, 3) else (4, 11, 32, 29)
        )
        for index in range(20):
            n = res + mod * index
            m = n
            observed = []
            for _ in word:
                m, a = step(m)
                observed.append(a)
            assert tuple(observed) == word
            assert 16 * m == 9 * n + c
            assert m < n
        ordered[str(word)] = {"S": s, "C": c, "modulus": mod, "residue": res}

    budget_word = (4,1,1,1,1,2,2,1,2,1,1,2,1,1,1,2,3)
    budget_s, budget_c, _, _ = packet(budget_word)
    budget_current = 165
    budget_first_descent = None
    for index, valuation in enumerate(budget_word, 1):
        budget_current, actual = step(budget_current)
        assert actual == valuation
        if budget_current < 165 and budget_first_descent is None:
            budget_first_descent = index
    budget_g = 2**budget_s - 3**len(budget_word)
    assert (budget_s,budget_c,budget_g,budget_current) == (27,1106233681,5077565,167)
    assert budget_first_descent == 1
    assert budget_g > 0 and budget_g * 165 <= budget_c

    n = 27
    rows = []
    valuation_sum = 0
    offset = 0
    first_descent = None
    while n != 1:
        old = n
        n, a = step(n)
        offset = 3 * offset + 2**valuation_sum
        valuation_sum += a
        r = len(rows) + 1
        assert 2**valuation_sum * n == 3**r * 27 + offset
        if n < 27 and first_descent is None:
            first_descent = r
        rows.append({"r": r, "x": n, "a": a, "S": valuation_sum,
                     "shortcut_clock": valuation_sum,
                     "classical_clock": valuation_sum + r,
                     "C": offset, "previous": old})
    assert first_descent == 37
    assert rows[36]["x"] == 23 and rows[36]["S"] == 59
    assert rows[36]["classical_clock"] == 96
    assert len(rows) == 41 and valuation_sum == 70
    assert rows[-1]["classical_clock"] == 111
    classical = [27]
    while classical[-1] != 1:
        n = classical[-1]
        classical.append(3 * n + 1 if n % 2 else n // 2)
    assert len(classical) - 1 == 111 and max(classical) == 9232
    assert max([27] + [r["x"] for r in rows]) == 3077
    for r in rows:
        assert classical[r["classical_clock"]] == r["x"]
    shortcut = [27]
    while shortcut[-1] != 1:
        n = shortcut[-1]
        shortcut.append((3*n+1)//2 if n % 2 else n//2)
    assert len(shortcut)-1 == 70 and max(shortcut) == 4616
    assert next(i for i,n in enumerate(shortcut) if n < 27) == 59
    assert next(i for i,n in enumerate(classical) if n < 27) == 96
    for r in rows:
        assert shortcut[r['shortcut_clock']] == r['x']

    lifts = []
    for j in range(1, 8):
        b = 3**j
        q = (2**b + 1) // 3 ** (j + 1)
        assert 3 ** (j + 1) * q == 2**b + 1
        seed = 2 ** (j + 1) * q - 1
        increment = 2 ** (j + b + 2)
        target_increment = 2 * 3 ** (j + 1)
        for s in range(21):
            source = seed + increment * s
            current = source
            actual = []
            for r in range(j + 1):
                assert current >= source
                current, a = step(current)
                actual.append(a)
            assert actual == [1] * j + [b + 1]
            assert current == 1 + target_increment * s < source
        lifts.append({"j": j, "b": b, "seed": str(seed),
                      "source_increment": str(increment),
                      "target_increment": target_increment,
                      "first_descent": j + 1, "parameters_s": [0, 20]})
    assert lifts[1]["seed"] == "151"
    assert lifts[1]["source_increment"] == "8192"
    assert lifts[1]["target_increment"] == 54

    densities = []
    for ell in range(1, 7):
        for d in range(7):
            k, h = 5 * ell, 8 * ell + d + 1
            density = sum((F(comb(s-1, k-1), 2 ** (s+1))
                           for s in range(k, h+1)), F())
            upper = F(1, 2) * F(4, 3) ** (d+1) * F(65536, 84375) ** ell
            assert density <= upper
            densities.append({"ell": ell, "D": d, "density": str(density),
                              "upper_bound": str(upper)})
    illustrated_alpha = F(1,2)*F(4,3)**4*F(65536,84375)**9*F(16,3)
    assert illustrated_alpha < F(868,1000) < 1

    factorizations = 0
    for q in (1, 6, 30):
        ds = divisors(q)
        for n in range(1, 1001):
            b = 1
            for p in ds:
                if p > 1 and all(p % r for r in range(2, p)) and n % p == 0:
                    b *= p
            m = n // b
            if mu(n):
                assert b in ds and gcd(m, q) == 1
                assert mu(n) == mu(b) * mu(m)
            factorizations += 1

    cube_partials = []
    for q in (1, 6, 30):
        for k in (1, 2, 3, 4):
            bound = 60
            direct = sum((mu(n) * weight(k, n) for n in range(1, bound+1)), F())
            cube = sum((mu(m) * sum((mu(b) * weight(k, b*m)
                        for b in divisors(q) if b*m <= bound), F())
                        for m in range(1, bound+1) if gcd(m,q) == 1), F())
            assert direct == cube
            cube_partials.append({"Q": q, "K": k, "n_cutoff": bound,
                                  "exact_equal": True})
    displayed_cube_rows = []
    expected_rows = {
        (6,1): F(-7,27), (6,5): F(17,675), (6,7): F(857,64827),
        (6,25): F(449,421875), (6,35): F(881,1620675),
        (30,1): F(-64,225), (30,7): F(6848,540225),
        (30,11): F(17216,3294225), (30,49): F(345536,1297080225),
    }
    for (q,m), expected in expected_rows.items():
        actual = sum((mu(b)*weight(1,b*m) for b in divisors(q)), F())
        assert actual == expected
        displayed_cube_rows.append({"Q":q,"m":m,"mu":mu(m),
                                    "cube":str(actual),"contribution":str(mu(m)*actual)})
    # Independent nonzero-support controls. Non-squarefree bases contribute zero.
    assert mu(1) == 1 and mu(5) == -1 and mu(7) == -1
    assert mu(25) == mu(49) == mu(121) == 0
    assert divisors(6) == [1, 2, 3, 6]
    assert [(b, mu(b)) for b in divisors(30)] == [
        (1,1), (2,-1), (3,-1), (5,-1), (6,1), (10,1), (15,1), (30,-1)
    ]
    support_counts = []
    for q,expected in ((6,[31,35,37,41,43,47,53,55,59]),
                       (30,[31,37,41,43,47,53,59])):
        supported = [m for m in range(30,61) if gcd(m,q)==1 and mu(m)]
        assert supported == expected
        support_counts.append({'Q':q,'interval':[30,60],'supported':supported,
                               'count':len(supported)})

    # Elementary rigorous envelopes: zeta(2)<5/3 and zeta(4)<10/9.
    zeta2_upper = sum((F(1, n*n) for n in range(1,6)), F()) + F(1,5)
    zeta4_upper = F(1) + F(1,16) + F(1,24)
    assert zeta2_upper < F(5,3) and zeta4_upper < F(10,9)
    safe_kappa3 = F(3,5) - F(10,81)
    positive_tail_cases = 0
    for q in (1, 2, 6, 30, 210):
        for mscale in range(1, 6):
            k = mscale**2
            for m in range(3*mscale, 4*mscale+1):
                delta = sum((mu(b)*weight(k,b*m) for b in divisors(q)), F())
                assert delta >= safe_kappa3 / (m*m)
                positive_tail_cases += 1

    hermites = [[F(1)], [F(), F(2)]]
    for r in range(1,12):
        hermites.append(p_add([F()] + [2*x for x in hermites[r]],
                             [-2*r*x for x in hermites[r-1]]))
    gram_cases = 0
    for r in range(13):
        for s in range(13):
            value = integrate_polynomial(p_mul(hermites[r],hermites[s]))
            assert value == (2**r * factorial(r) if r == s else 0)
            gram_cases += 1

    square_cases = 0
    for sheat in (F(1,4), F(1), F(3)):
        for center in (F(-2), F(), F(3,2)):
            for z in (F(-1,3), F(), F(2,5)):
                # -(u-c)^2/(4s)+uz = -(u-c-2sz)^2/(4s)+cz+sz^2.
                left = [-center*center/(4*sheat), center/(2*sheat)+z, -1/(4*sheat)]
                shifted = center+2*sheat*z
                right = [-shifted*shifted/(4*sheat)+center*z+sheat*z*z,
                         shifted/(2*sheat), -1/(4*sheat)]
                assert left == right
                square_cases += 1

    numerical_runs = []
    for precision in (70,90):
        with localcontext() as ctx:
            ctx.prec = precision
            separation = (Decimal(1001)/1000).ln()
            overlap = (-separation*separation/8).exp()
            condition = (1+overlap)/(1-overlap)
            tails = []
            for lam in (Decimal(1),Decimal(4)):
                term = (-lam).exp()
                probabilities = [term]
                for index in range(1,180):
                    term *= lam/index
                    probabilities.append(term)
                for cutoff in (4,8,12):
                    value = sum(probabilities[cutoff+1:])
                    # For omitted indices >=180 and lambda<=4 the geometric
                    # upper bound is p180/(1-4/181), well below10^-200.
                    first_omitted = term*lam/180
                    remainder_bound = first_omitted/(1-lam/181)
                    assert remainder_bound < Decimal('1e-200')
                    tails.append({"lambda":str(lam),"R":cutoff,"tail":str(value),
                                  "series_remainder_bound":str(remainder_bound)})
            numerical_runs.append({"decimal_precision":precision,
                                   "separation":str(separation),"overlap":str(overlap),
                                   "gram_condition_number":str(condition),
                                   "I_4_given_1":str(4*Decimal(4).ln()-3),
                                   "poisson_tails":tails})
            def arctan_inverse(n,terms):
                x = 1/Decimal(n)
                power = x
                value = Decimal()
                for index in range(terms):
                    value += (-1)**index * power / (2*index+1)
                    power *= x*x
                return value,power/(2*terms+1)
            a5,error5 = arctan_inverse(5,160)
            a239,error239 = arctan_inverse(239,40)
            # Exact tangent addition check for4 atan(1/5)-atan(1/239)=pi/4.
            tan2 = 2*F(1,5)/(1-F(1,5)**2)
            tan4 = 2*tan2/(1-tan2**2)
            assert (tan4-F(1,239))/(1+tan4*F(1,239)) == 1
            pi_machin = 16*a5-4*a239
            pi_series_error = 16*error5+4*error239
            assert pi_series_error < Decimal('1e-180')
            bernoulli = [F(1)]
            for degree in range(1,27):
                bernoulli.append(-sum((F(comb(degree+1,j))*bernoulli[j]
                                       for j in range(degree)),F())/(degree+1))
            assert bernoulli[1]==F(-1,2) and bernoulli[2]==F(1,6)
            assert bernoulli[4]==F(-1,30) and bernoulli[6]==F(1,42)
            reciprocals = []
            for n in range(1,14):
                bn = abs(bernoulli[2*n])
                zeta = (Decimal(bn.numerator)/bn.denominator)*(2*pi_machin)**(2*n)/(2*factorial(2*n))
                reciprocals.append(1/zeta)
            cks = [sum((Decimal((-1)**j*comb(k,j))*reciprocals[j]
                        for j in range(k+1)),Decimal()) for k in range(13)]
            numerical_runs[-1].update({'pi_Machin':str(pi_machin),
                                      'pi_series_error_bound':str(pi_series_error),
                                      'Bernoulli_recurrence':'sum_{j=0}^{n} binom(n+1,j) B_j=0 for n>=1',
                                      'finite_c_K_values':[str(v) for v in cks]})
    for a,b in zip(numerical_runs[0]['poisson_tails'],numerical_runs[1]['poisson_tails']):
        assert abs(Decimal(a['tail'])-Decimal(b['tail'])) < Decimal('1e-68')
    assert abs(Decimal(numerical_runs[0]['gram_condition_number'])-
               Decimal(numerical_runs[1]['gram_condition_number'])) < Decimal('1e-54')
    for a,b in zip(numerical_runs[0]['finite_c_K_values'],numerical_runs[1]['finite_c_K_values']):
        assert abs(Decimal(a)-Decimal(b)) < Decimal('1e-63')

    return {"status": "passed", "python_version": platform.python_version(),
            "arithmetic": "Python integers and Fraction for exact controls; Decimal70/90 for separately labeled numerical controls",
            "ordered_words": ordered, "ordered_word_instances": 40,
            "contracting_prefix_budget": {"source":165,"word":budget_word,
                                          "S":budget_s,"C":budget_c,"G":budget_g,
                                          "endpoint":167,"earlier_actual_descent":1},
            "orbit27": {"first_actual_descent": 37, "first_descent_shortcut_clock": 59,
                         "first_descent_classical_clock": 96,
                         "odd_steps_to_1": 41, "shortcut_steps_to_1": 70,
                         "classical_steps_to_1": 111, "maximum_odd": 3077,
                         "maximum_classical": 9232, "maximum_shortcut":4616,
                         "rows": rows},
            "delayed_lifts": {"instances": 147, "families": lifts},
            "density_controls": densities,
            "illustrated_packing_alpha_D3_ell9":str(illustrated_alpha),
            "squarefree_factorization_cases": factorizations,
            "exact_cutoff_cube_controls": cube_partials,
            "displayed_cube_rows": displayed_cube_rows,
            "displayed_squarefree_support_counts": support_counts,
            "safe_rational_kappa3": str(safe_kappa3),
            "positive_tail_cases": positive_tail_cases,
            "exact_hermite_gram_entries": gram_cases,
            "gaussian_square_completion_cases": square_cases,
            "numerical_controls": numerical_runs,
            "non_claims": ["No global Collatz descent", "No RH proof or actual off-line zero",
                           "No exhaustive residue atlas", "No fresh Lean replay",
                           "Finite cutoff cube controls do not estimate the infinite signed sum"],
            "resolved_failures": []}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_suffix(".json"))
    args = parser.parse_args()
    data = run_checks()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print("PASS: exact expanded-example controls and finite Gaussian/Hermite identities.")


if __name__ == "__main__":
    main()
