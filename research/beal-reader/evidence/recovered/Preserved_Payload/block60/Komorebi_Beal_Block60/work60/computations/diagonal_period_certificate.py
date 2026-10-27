#!/usr/bin/env python3
"""Exact finite checks for Block 60. No claim of a global Beal solution.

Domains: Q(phi), phi^2=phi+1; finite residue fields; integer modular arithmetic.
The universal analytic comparison is proved separately in DIAGONAL_PERIODS.md.
"""
from __future__ import annotations
import argparse, hashlib, json, math, struct
from fractions import Fraction
from pathlib import Path


def need(test: bool, message: str) -> None:
    if not test:
        raise AssertionError(message)


class PhiRing:
    def __init__(self, p: int = 0, root: int | None = None):
        self.p, self.root = p, root
        self.one = self.make(1)
        self.zero = self.make(0)
        self.phi = self.make(0, 1)

    def make(self, a=0, b=0):
        if self.p:
            a, b = int(a) % self.p, int(b) % self.p
            return ((a + b * self.root) % self.p, 0) if self.root is not None else (a, b)
        return Fraction(a), Fraction(b)

    def add(self, x, y): return self.make(x[0] + y[0], x[1] + y[1])
    def neg(self, x): return self.make(-x[0], -x[1])
    def sub(self, x, y): return self.add(x, self.neg(y))
    def mul(self, x, y):
        a, b = x; c, d = y
        return self.make(a*c + b*d, a*d + b*c + b*d)
    def inv(self, x):
        a, b = x; norm = a*a+a*b-b*b
        if self.p:
            norm %= self.p
            need(norm != 0, 'division by zero')
            z = pow(norm, -1, self.p)
        else:
            need(norm != 0, 'division by zero')
            z = 1/norm
        return self.make((a+b)*z, -b*z)
    def div(self, x, y): return self.mul(x, self.inv(y))
    def power(self, x, n):
        if n < 0: return self.power(self.inv(x), -n)
        out = self.one
        while n:
            if n & 1: out = self.mul(out, x)
            x = self.mul(x, x); n //= 2
        return out
    def scale(self, x, n): return self.mul(self.make(n), x)
    def out(self, x):
        return list(x) if self.p else [str(x[0]), str(x[1])]
    def order(self):
        need(self.p > 0, 'finite field required')
        return self.p if self.root is not None else self.p*self.p
    def is_power(self, x, m):
        need(x != self.zero, 'zero is not a unit')
        return self.power(x, (self.order()-1)//math.gcd(m, self.order()-1)) == self.one


def period_constants(F: PhiRing):
    p, one = F.phi, F.one
    d = F.sub(F.scale(p, 2), one)
    delta = F.sub(F.make(9), F.scale(p, 3))
    a, b = F.sub(p, one), F.neg(p)
    cp_a = F.div(F.make(2), delta)
    cm_a = F.neg(F.inv(F.scale(delta, 2)))
    cp_b = F.div(F.sub(F.scale(p, 4), F.make(7)), F.make(15))
    cm_b = F.div(F.add(p, F.make(2)), F.make(15))
    vals = []
    for k, cp, cm in [(a, cp_a, cm_a), (b, cp_b, cm_b)]:
        h = F.add(F.sub(F.power(k, 2), F.scale(k, 2)), F.make(5))
        gp = F.add(F.scale(k, 2), one)
        kap = F.div(F.mul(F.mul(cp, cm), k), F.mul(h, F.power(gp, 2)))
        vals.append(kap)
    ka, kb = vals
    c = F.neg(F.power(p, -4))
    need(ka == F.neg(F.div(F.power(p, 2), F.scale(d, 675))), 'kappa a identity')
    need(kb == F.div(F.power(p, -2), F.scale(d, 675)), 'kappa b identity')
    need(F.div(kb, ka) == c, 'diagonal ratio equals cross-ratio')
    need(F.mul(ka, kb) == F.div(F.make(-1), F.make(3**6 * 5**5)), 'diagonal norm')
    need(F.mul(cp_a, cm_a) == F.neg(F.div(F.power(p, 2), F.make(45))), 'branch a derivative product')
    need(F.mul(cp_b, cm_b) == F.neg(F.div(F.power(p, -2), F.make(45))), 'branch b derivative product')
    return {'kappa_a': F.out(ka), 'kappa_b': F.out(kb), 'cross_ratio': F.out(c),
            'cp_a': F.out(cp_a), 'cm_a': F.out(cm_a), 'cp_b': F.out(cp_b), 'cm_b': F.out(cm_b)}


def polynomial_checks():
    def mul(a, b):
        c = [0]*(len(a)+len(b)-1)
        for i, x in enumerate(a):
            for j, y in enumerate(b): c[i+j] += x*y
        return c
    g, h = [-1, 1, 1], [5, -2, 1]
    f0 = mul(mul(g, g), h)
    need(f0 == [5, -12, 0, 10, 0, 0, 1], 'normalized special fiber')
    R = [-20, 36, 0, -20]
    rem = R[:]
    for i in range(len(rem)-1, 1, -1):
        z = rem[i]
        for j in range(3): rem[i-2+j] -= z*g[j]
    need(rem == [0, -4, 0, 0], 'smoothing derivative modulo g')
    scalings = 0
    for A in range(-5, 6):
        if not A: continue
        for B in range(1, 7):
            u, z = Fraction(A*A, B**3), Fraction(B**5, A**3)
            need(Fraction(A)/u**5 == z**3, 'A scaling')
            need(Fraction(B)/u**3 == z**2, 'B scaling')
            scalings += 1
    # Exponent coordinates (A,C0,3,sqrt5). Theta=C0^7/(3^3 A^3 sqrt5^5).
    theta = [-3, 7, -3, -5]
    E7, E49 = [1, 0, 1, 4], [1, -35, 1, 18]
    need([theta[i]+3*E7[i] for i in range(4)] == [0, 7, 0, 7], 'level7 multiplicative identity')
    need([theta[i]+3*E49[i] for i in range(4)] == [0, -98, 0, 49], 'level49 multiplicative identity')
    Rm = [[1, -2], [-2, -1]]
    sq = [[sum(Rm[i][k]*Rm[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    need(sq == [[5, 0], [0, 5]], 'marked Kummer matrix identity')
    # Elliptic sanity check: y^2=x^3+x^2+e has 1/j=-e/64+O(e^2).
    cp, cm, H2, smoothing = Fraction(1,4), Fraction(1,4), Fraction(1), Fraction(1)
    elliptic = -cp*cm*smoothing/(4*H2)
    need(elliptic == Fraction(-64, 16**3) == Fraction(-1,64), 'elliptic leading coefficient benchmark')
    return {'f0_coefficients':f0, 'smoothing_derivative_coefficients':R,
            'smoothing_derivative_mod_g':[0,-4], 'exact_scaling_instances':scalings,
            'theta_exponents':theta, 'E7_exponents':E7, 'E49_exponents':E49,
            'marked_matrix':Rm, 'marked_matrix_square':sq,
            'elliptic_leading_coefficient':str(elliptic)}


def primes(n):
    return [p for p in range(11, n+1) if all(p%d for d in range(2, math.isqrt(p)+1))]


def field_records(limit=2000):
    rows = []
    for p in primes(limit):
        roots = [a for a in range(p) if (a*a-a-1)%p == 0]
        for root in (roots if roots else [None]):
            F = PhiRing(p, root)
            row = {'q':p, 'phi_root':root, **period_constants(F)}
            row['phi_power_status'] = {str(m):F.is_power(F.phi,m) for m in (7,49,343)}
            rows.append(row)
    return rows


def factors(n):
    out = []
    for p in range(2, math.isqrt(n)+1):
        if n%p == 0:
            out.append(p)
            while n%p == 0: n//=p
    if n > 1: out.append(n)
    return out


def generator(q):
    fs = factors(q-1)
    return next(g for g in range(2,q) if all(pow(g,(q-1)//p,q)!=1 for p in fs))


def survivor_counts(q):
    H7 = {pow(z,7,q) for z in range(1,q)}
    H49 = {pow(z,49,q) for z in range(1,q)}
    scalar = 3*pow(5,9,q)%q
    count7, count49 = 0,0
    digest = hashlib.sha256()
    eligible_A7 = {A for A in range(1,q) if 75*A%q in H7}
    for C0 in range(1,q):
        factor = scalar*pow(pow(C0,35,q),-1,q)%q
        for A in range(1,q):
            if A in eligible_A7: count7+=1
            if A*factor%q in H49:
                need(A in eligible_A7, '49-level implies 7-level')
                count49+=1; digest.update(struct.pack('<HH',A,C0))
    need(count7 == (q-1)**2//7 and count49 == (q-1)**2//49, 'unit residue count formula')
    need(math.gcd(5,q-1)==1, 'unique fifth root at each survivor prime')
    return {'q':q,'all_unit_pairs':(q-1)**2,'full7_pairs':count7,'full49_pairs':count49,
            'full49_pairs_sha256':digest.hexdigest(),'A_per_C0_level49':(q-1)//49,
            'A_per_C0_level7':(q-1)//7}


def hensel_newton(q,A,precision=52):
    C = q**7
    target = C**7-A**3
    b0 = pow(target%q,pow(5,-1,q-1),q)
    b, k = b0,1
    stages=[1]
    while k < precision:
        j=min(2*k,precision); mod=q**j
        b=(b-(pow(b,5,mod)-target)*pow(5*pow(b,4,mod),-1,mod))%mod
        need((pow(b,5,mod)-target)%mod == 0,'Hensel equation')
        k=j;stages.append(k)
    return b0,b,stages


def witnesses():
    rows=[]
    for q in [197,883,1373,1667]:
        g=generator(q)
        A0=pow(3*pow(5,9,q),-1,q)
        F=PhiRing(q)
        need(F.power(F.phi,q+1)==F.make(-1),'inert norm of phi')
        need(F.is_power(F.phi,49),'phi49 at survivor')
        constants=period_constants(F)
        ka=tuple(constants['kappa_a']);kb=tuple(constants['kappa_b']);cc=tuple(constants['cross_ratio'])
        for label,exponent in [('positive',0),('seventh_not_fortyninth',7),('fails_seventh',1)]:
            A=A0*pow(g,exponent,q)%q
            b0,b,stages=hensel_newton(q,A)
            unit=F.power(F.make(A),-3)
            diagonal_a=F.mul(ka,unit);diagonal_b=F.mul(kb,unit)
            flags={str(M): all(F.is_power(z,M) for z in [diagonal_a,diagonal_b,cc]) for M in [7,49]}
            need(flags==({'7':True,'49':True} if exponent==0 else {'7':True,'49':False} if exponent==7 else {'7':False,'49':False}), 'witness expected power status')
            need((A**3+pow(b,5,q**52)-q**49)%(q**52)==0,'witness equation modulo q52')
            rows.append({'q':q,'kind':label,'primitive_root':g,'A_integer':A,'B_residue':b0,
                'B_mod_q52':str(b),'C_integer':str(q**7),'C_unit':1,'C_valuation':7,
                'root_precision':52,'newton_stages':stages,'equation_residue':0,
                'natural_monodromy_content':2,'full_torsion_by_period_test':flags})
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result={'schema':'komorebi.beal.block60.diagonal-period.v1',
      'arithmetic':'exact Q(phi), finite fields, integer Hensel lifts',
      'symbolic':period_constants(PhiRing()),'algebra':polynomial_checks(),
      'field_range':{'rational_primes_min':11,'rational_primes_max':2000,'all_split_places':True},
      'fields':field_records(),'unit_pair_counts':[survivor_counts(q) for q in [197,883,1373,1667]],
      'witnesses':witnesses(),
      'interpretation':{'local_period_criterion_only':True,'global_beta_constructed':False,
        'global_integer_solution_constructed':False,'new_survivor_prime_exclusion':False,
        'analytic_smoothing_comparison_is_written_not_computational':True}}
    result['coverage']={'residue_fields':len(result['fields']),
      'unit_pairs':sum(x['all_unit_pairs'] for x in result['unit_pair_counts']),
      'full49_pairs':sum(x['full49_pairs'] for x in result['unit_pair_counts']),
      'local_witnesses':len(result['witnesses']),'positive_local_witnesses':4,
      'seventh_not_fortyninth_controls':4,'fails_seventh_controls':4}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result['coverage'],sort_keys=True))
    return 0
if __name__=='__main__':raise SystemExit(main())
