"""Exact triangular inversion and class-number check. No claim of novelty."""
from fractions import Fraction
from functools import lru_cache
from math import comb, isqrt
from pathlib import Path
import json, time
from explore import tau_triangular, sigma_primes
ROOT=Path(__file__).resolve().parent

def choose(n,k): return comb(n,k) if 0<=k<=n else 0

def m(r,j): return (-1)**(r-j)*choose(r+j,r-j)
def b(r,j): return choose(2*r,r-j)-choose(2*r,r-j-1)

@lru_cache(None)
def hurwitz_six(D):
    # Six times H(D), positive D. Includes imprimitive reduced forms.
    if D<=0 or D%4 not in (0,3): return 0
    h=0
    for a in range(1,isqrt(D//3)+1):
        for bb in range(-a,a+1):
            z=D+bb*bb
            if z%(4*a): continue
            c=z//(4*a)
            if c<a: continue
            if (abs(bb)==a or a==c) and bb<0: continue
            if a==c and bb==0: h+=3  # forms proportional to x²+y²
            elif a==bb==c: h+=2      # forms proportional to x²+xy+y²
            else: h+=6
    return h

def moments(p):
    out=[Fraction(0) for _ in range(6)]
    out[0]=Fraction(hurwitz_six(4*p),12)
    for t in range(1,isqrt(4*p-1)+1):
        H=Fraction(hurwitz_six(4*p-t*t),6)
        tt=1
        for j in range(6):
            out[j]+=tt*H
            tt*=t*t
    return out

def main():
    t=time.perf_counter()
    entries=0
    for r in range(32):
        for j in range(r+1):
            assert sum(m(r,k)*b(k,j) for k in range(j,r+1))==int(r==j)
            assert sum(b(r,k)*m(k,j) for k in range(j,r+1))==int(r==j)
            entries+=2
    for D,v in [(3,2),(4,3),(7,6),(8,6),(11,6),(12,8),(16,9)]:
        assert hurwitz_six(D)==v,(D,hurwitz_six(D),v)
    tau=tau_triangular(2411)
    _,ps=sigma_primes(499)
    ps += [2411]
    samples=[]
    for p in ps:
        s=moments(p)
        assert s[0]==p,(p,s[0])
        for r in range(1,6):
            transform=sum(m(r,j)*p**(r-j)*s[j] for j in range(r+1))
            assert transform==-1-(tau[p] if r==5 else 0),(p,r,transform)
        c=42*p**6-90*p**4-75*p**3-35*p**2-9*p-1
        assert c-s[5]==tau[p]
        if p in (2,3,5,2411):
            samples.append({'p':p,'s10':str(s[5]),'polynomial':c,'difference_tau':tau[p]})
    result={'status':'PASS','matrix_size':32,'inverse_entry_checks':entries,
            'class_number_prime_rows':len(ps),'small_prime_bound':499,
            'additional_prime':2411,'samples':samples,'seconds':time.perf_counter()-t}
    (ROOT/'trace_inverse_results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
