from __future__ import annotations

import csv
import json
import math
import random
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

import sympy as sp
from sympy.matrices.normalforms import smith_normal_form
from sympy.polys.domains import ZZ


@dataclass
class TripleAudit:
    a: int
    b: int
    c: int
    primitive: bool
    A: int
    L: int
    kappa: int
    radical: int
    quality: float
    smith_diagonal: list[int]
    periodogram: list[int]
    gcd_A_abc: int
    gcd_L_abc: int
    gcd_A_L: int
    identities_passed: bool


def radical(n: int) -> int:
    out = 1
    for p in sp.factorint(abs(int(n))):
        out *= int(p)
    return out


def quality(a: int, b: int, c: int) -> float:
    R = radical(a * b * c)
    return math.log(c) / math.log(R)


def circulant_block(a: int, b: int, c: int) -> sp.Matrix:
    return sp.Matrix([
        [a*c, b*c, -a*b],
        [-a*b, a*c, b*c],
        [b*c, -a*b, a*c],
    ])


def dft_periodogram_exact(a: int, b: int, c: int) -> list[int]:
    # For a real length-three signal, |S_1|^2=|S_2|^2.  Compute the
    # values without floating point by using autocorrelations.
    s0, s1, s2 = a*c, b*c, -a*b
    r0 = s0*s0 + s1*s1 + s2*s2
    r1 = s0*s2 + s1*s0 + s2*s1
    return [r0 + 2*r1, r0 - r1, r0 - r1]


def point_add(P: tuple[sp.Expr, sp.Expr] | None,
              Q: tuple[sp.Expr, sp.Expr] | None,
              kappa: sp.Expr) -> tuple[sp.Expr, sp.Expr] | None:
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if sp.simplify(x1 - x2) == 0 and sp.simplify(y1 + y2) == 0:
        return None
    if sp.simplify(x1 - x2) == 0:
        slope = sp.simplify(3*x1**2/(2*y1))
    else:
        slope = sp.simplify((y2-y1)/(x2-x1))
    x3 = sp.factor(slope**2 - x1 - x2)
    y3 = sp.factor(slope*(x1-x3)-y1)
    return sp.factor(x3), sp.factor(y3)


def verify_symbolic() -> dict[str, str]:
    a, b, c0 = sp.symbols('a b c', nonzero=True)
    s_generic = sp.Matrix([a*c0, b*c0, -a*b])
    tau_generic = sp.Matrix([-a*b, a*c0, b*c0])
    generic_autocorr = sp.factor((s_generic.T*tau_generic)[0])
    assert sp.factor(generic_autocorr-a*b*c0*(c0-a-b)) == 0
    r0 = sp.expand(sum(v*v for v in s_generic))
    generic_periodogram_gap = sp.factor((r0+2*generic_autocorr)-(r0-generic_autocorr))
    assert sp.factor(generic_periodogram_gap-3*a*b*c0*(c0-a-b)) == 0

    a, b = sp.symbols('a b', nonzero=True)
    c = a + b
    A = sp.expand(a*a + a*b + b*b)
    L = sp.expand((a-b)*(a+2*b)*(2*a+b))
    kappa = sp.expand(4*a*b*c)

    s = sp.Matrix([a*c, b*c, -a*b])
    tau_s = sp.Matrix([-a*b, a*c, b*c])
    autocorr = sp.factor((s.T*tau_s)[0])
    assert sp.factor(autocorr - a*b*c*(c-a-b)) == 0

    C = circulant_block(a, b, c)
    assert (C*C.T-A**2*sp.eye(3)).applyfunc(sp.factor) == sp.zeros(3)
    assert sp.factor(C.det() - A**3) == 0
    assert (C.adjugate()-A*C.T).applyfunc(sp.factor) == sp.zeros(3)

    # DFT factorization in Q(sqrt(-3)).  z = a+b(1+sqrt(-3))/2.
    rt = sp.sqrt(-3)
    z = a + b*(1+rt)/2
    zbar = a + b*(1-rt)/2
    omega = (-1+rt)/2
    omega2 = (-1-rt)/2
    sh0 = sp.factor(a*c+b*c-a*b)
    sh1 = sp.factor(a*c+b*c*omega-a*b*omega2)
    sh2 = sp.factor(a*c+b*c*omega2-a*b*omega)
    assert sp.simplify(sh0-A) == 0
    assert sp.simplify(sh1-z**2) == 0
    assert sp.simplify(sh2-zbar**2) == 0

    assert sp.simplify(2*z**3 - (L + 3*rt*a*b*c)) == 0
    assert sp.factor(L**2 + 27*a*a*b*b*c*c - 4*A**3) == 0

    # Frey invariants from y^2=x^3+(b-a)x^2-abx.
    a2 = b-a
    a4 = -a*b
    b2 = 4*a2
    b4 = 2*a4
    b6 = 0
    b8 = -a4**2
    c4 = sp.factor(b2**2 - 24*b4)
    c6 = sp.factor(-b2**3 + 36*b2*b4 - 216*b6)
    delta = sp.factor(-b2**2*b8 - 8*b4**3 - 27*b6**2 + 9*b2*b4*b6)
    assert sp.expand(c4 - 16*A) == 0
    assert sp.expand(c6 - 32*L) == 0
    assert sp.expand(delta - 16*a*a*b*b*c*c) == 0
    assert sp.expand(c4**3-c6**2-1728*delta) == 0

    # Mordell points.
    Pbc = (4*b*c, 4*b*c*(a+2*b))
    Pac = (4*a*c, 4*a*c*(2*a+b))
    Pab = (-4*a*b, 4*a*b*(a-b))
    for x, y in (Pbc, Pac, Pab):
        assert sp.factor(y*y - x**3 - kappa**2) == 0

    # 3-isogeny image.
    def phi(P: tuple[sp.Expr, sp.Expr]) -> tuple[sp.Expr, sp.Expr]:
        x, y = P
        return (sp.factor((x**3+4*kappa**2)/x**2),
                sp.factor(y*(x**3-8*kappa**2)/x**3))
    image = phi(Pbc)
    assert sp.simplify(image[0]-4*A) == 0
    assert sp.simplify(image[1]+4*L) == 0
    assert sp.factor(image[1]**2-image[0]**3+27*kappa**2) == 0

    T = (sp.Integer(0), kappa)
    PT = point_add(Pbc, T, kappa)
    P2T = point_add(PT, T, kappa)
    assert PT is not None and P2T is not None
    assert sp.simplify(PT[0]-Pab[0]) == 0
    assert sp.simplify(PT[1]+Pab[1]) == 0
    assert sp.simplify(P2T[0]-Pac[0]) == 0
    assert sp.simplify(P2T[1]+Pac[1]) == 0
    T2 = point_add(T, T, kappa)
    assert T2 is not None and sp.simplify(T2[0]) == 0 and sp.simplify(T2[1]+kappa) == 0
    assert point_add(T2, T, kappa) is None

    t = sp.symbols('t')
    fiber = sp.expand((t-Pbc[0])*(t-Pac[0])*(t-Pab[0]))
    assert sp.expand(fiber - (t**3-4*A*t**2+4*kappa**2)) == 0

    psi_product = sp.factor((2*Pbc[1])*(2*(-Pab[1]))*(2*(-Pac[1])))
    assert sp.expand(psi_product - delta*c6) == 0

    return {
        'generic_autocorrelation': str(generic_autocorr),
        'generic_periodogram_gap': str(generic_periodogram_gap),
        'A': str(A),
        'L': str(sp.factor(L)),
        'c4': str(c4),
        'c6': str(c6),
        'delta': str(delta),
        'isogeny_x': str(image[0]),
        'isogeny_y': str(image[1]),
        'fiber_polynomial': str(sp.factor(fiber)),
        'torsion_product': str(psi_product),
    }


def audit_triple(a: int, b: int) -> TripleAudit:
    c = a+b
    primitive = math.gcd(a,b) == 1
    A = a*a+a*b+b*b
    L = (a-b)*(a+2*b)*(2*a+b)
    kappa = 4*a*b*c
    C = circulant_block(a,b,c)
    S = smith_normal_form(C, domain=ZZ)
    diagonal = [abs(int(S[i,i])) for i in range(3)]
    per = dft_periodogram_exact(a,b,c)

    Pbc = (4*b*c, 4*b*c*(a+2*b))
    Pac = (4*a*c, 4*a*c*(2*a+b))
    Pab = (-4*a*b, 4*a*b*(a-b))
    identities = [
        C*C.T == A*A*sp.eye(3),
        diagonal == [1,A,A*A] if primitive else True,
        per[0] == per[1] == per[2] == A*A,
        Pbc[1]**2 == Pbc[0]**3+kappa**2,
        Pac[1]**2 == Pac[0]**3+kappa**2,
        Pab[1]**2 == Pab[0]**3+kappa**2,
        L*L+27*a*a*b*b*c*c == 4*A**3,
        math.gcd(A,a*b*c) == 1 if primitive else True,
        math.gcd(abs(L),a*b*c) == 2 if primitive else True,
        math.gcd(A,abs(L)) in (1,3),
    ]
    return TripleAudit(
        a=a,b=b,c=c,primitive=primitive,A=A,L=L,kappa=kappa,
        radical=radical(a*b*c),quality=quality(a,b,c),
        smith_diagonal=diagonal,periodogram=per,
        gcd_A_abc=math.gcd(A,a*b*c),
        gcd_L_abc=math.gcd(abs(L),a*b*c),
        gcd_A_L=math.gcd(A,abs(L)),
        identities_passed=all(identities),
    )


def representation_count_bruteforce(A: int) -> int:
    # Bound follows from positive definite quadratic form.
    B = int(math.sqrt(4*A/3))+3
    count = 0
    for a in range(-B,B+1):
        for b in range(-B,B+1):
            if a*a+a*b+b*b == A:
                count += 1
    return count


def representation_formula(A: int) -> int:
    fac = sp.factorint(A)
    # Formula is zero if an inert prime q == 2 mod 3 occurs to an odd power.
    for q,e in fac.items():
        if q % 3 == 2 and e % 2:
            return 0
    value = 6
    for q,e in fac.items():
        if q % 3 == 1:
            value *= (e+1)
    return value


def run_random_tests(seed: int = 20260731, count: int = 250) -> list[TripleAudit]:
    rng = random.Random(seed)
    rows: list[TripleAudit] = []
    while len(rows) < count:
        a = rng.randint(1,5000)
        b = rng.randint(1,5000)
        if math.gcd(a,b) != 1:
            continue
        row = audit_triple(a,b)
        if not row.identities_passed:
            raise AssertionError(row)
        rows.append(row)
    return rows



def deterministic_trial_prime(n: int) -> tuple[bool, int, int]:
    if n < 2:
        return False, 0, 0
    limit = math.isqrt(n)
    count = 0
    last = 1
    for p in sp.primerange(2, limit+1):
        count += 1
        last = int(p)
        if n % p == 0:
            return n == p, count, last
    return True, count, last

def main() -> None:
    root = Path(__file__).resolve().parent
    (root/'results').mkdir(parents=True, exist_ok=True)
    (root/'tables').mkdir(parents=True, exist_ok=True)
    symbolic = verify_symbolic()
    random_rows = run_random_tests()

    worked_pairs = [
        (1,1),
        (1,8),
        (2,3),
        (3,125),
        (121,48_234_375),
        (2,3**10*109),
    ]
    worked = [audit_triple(a,b) for a,b in worked_pairs]
    if not all(row.identities_passed for row in worked):
        raise AssertionError('worked example failed')

    # Test the Eisenstein representation formula on a broad finite range.
    rep_checks = []
    for A in range(1,401):
        brute = representation_count_bruteforce(A)
        formula = representation_formula(A)
        if brute != formula:
            raise AssertionError(('representation formula',A,brute,formula,sp.factorint(A)))
        rep_checks.append({'A':A,'bruteforce':brute,'formula':formula})

    # Check support theorem for all worked and random triples.
    for row in random_rows+worked:
        fac = sp.factorint(row.A)
        if int(fac.get(3,0)) > 1:
            raise AssertionError(('v3(A)>1',row))
        for q in fac:
            if q != 3 and q % 3 != 1:
                raise AssertionError(('bad prime in A',q,row))

    record = worked[-1]
    record_prime, primes_tested, largest_prime_tested = deterministic_trial_prime(record.A)
    if not record_prime:
        raise AssertionError('record A is not prime')

    with (root/'tables'/'worked_examples.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=list(asdict(worked[0]).keys()))
        writer.writeheader()
        for row in worked:
            item=asdict(row)
            item['smith_diagonal']=' '.join(map(str,row.smith_diagonal))
            item['periodogram']=' '.join(map(str,row.periodogram))
            writer.writerow(item)

    with (root/'tables'/'random_audit.csv').open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=list(asdict(random_rows[0]).keys()))
        writer.writeheader()
        for row in random_rows:
            item=asdict(row)
            item['smith_diagonal']=' '.join(map(str,row.smith_diagonal))
            item['periodogram']=' '.join(map(str,row.periodogram))
            writer.writerow(item)

    with (root/'tables'/'representation_formula_checks.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=['A','bruteforce','formula'])
        writer.writeheader();writer.writerows(rep_checks)

    result = {
        'status':'verified_with_scoped_claim_boundary',
        'symbolic_identities':symbolic,
        'random_primitive_triples_checked':len(random_rows),
        'worked_examples_checked':len(worked),
        'representation_formula_values_checked':len(rep_checks),
        'all_random_checks_passed':all(r.identities_passed for r in random_rows),
        'all_worked_checks_passed':all(r.identities_passed for r in worked),
        'record':{
            'a':record.a,'b':record.b,'c':record.c,
            'A':record.A,'A_is_prime':record_prime,'A_mod_3':record.A%3,
            'trial_division_primes_tested':primes_tested,
            'largest_trial_prime':largest_prime_tested,
            'sqrt_A':math.isqrt(record.A),
            'transformed_ramanujan_scale':1/(record.A-1),
        },
        'corrections_and_boundaries':[
            'The four COS sources support the transform, filtering, periodogram, and recursive-coefficient principles. They do not state the arithmetic identities proved in the companion.',
            'The factor 1/(q-1) in the transformed atlas is a proposed Ramanujan-transfer model unless a specific averaging measure is defined. It is not an intrinsic invariant of a single abc triple.',
            'The double-atlas expansion-rigidity statement remains a proposed theorem, not a proved consequence of the verified identities.',
            'No claim in this audit is a proof of the abc conjecture.',
        ],
    }
    (root/'results'/'verification_results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
