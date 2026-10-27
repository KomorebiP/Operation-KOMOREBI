from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import dataclass, asdict
from fractions import Fraction
from pathlib import Path
from statistics import median
from numbers import Integral
from typing import Iterable, Any

import sympy as sp


def exact_int(value: Any, name: str = "value") -> int:
    """Promote an integer scalar to arbitrary-precision Python ``int``.

    Fixed-width scalar types such as ``numpy.int64`` keep their dtype during
    multiplication and can wrap silently.  Converting at the API boundary
    ensures that all subsequent arithmetic uses Python's unbounded integers.
    """
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not bool")
    if isinstance(value, Integral) or isinstance(value, sp.Integer):
        return int(value)
    raise TypeError(f"{name} must be an integer scalar, got {type(value).__name__}")


def fraction_text(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def factor(n: int) -> dict[int, int]:
    n = exact_int(n, "n")
    return {int(p): int(e) for p, e in sp.factorint(n).items()}


def radical(n: int) -> int:
    n = exact_int(n, "n")
    r = 1
    for p in factor(n):
        r *= p
    return r


def xgcd(a: int, b: int) -> tuple[int, int, int]:
    a = exact_int(a, "a")
    b = exact_int(b, "b")
    g, s, t = sp.gcdex(sp.Integer(a), sp.Integer(b))
    # SymPy returns (s,t,g) in some versions; test identity robustly.
    vals = [int(g), int(s), int(t)]
    for perm in ((0,1,2),(1,2,0),(2,0,1),(0,2,1),(1,0,2),(2,1,0)):
        gg, ss, tt = vals[perm[0]], vals[perm[1]], vals[perm[2]]
        if ss*a + tt*b == gg and abs(gg) == math.gcd(a,b):
            if gg < 0:
                gg, ss, tt = -gg, -ss, -tt
            return gg, ss, tt
    # Python fallback
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q*r
        old_s, s = s, old_s - q*s
        old_t, t = t, old_t - q*t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    return old_r, old_s, old_t



def ceil_div(a: int, b: int) -> int:
    a = exact_int(a, "a")
    b = exact_int(b, "b")
    if b <= 0:
        raise ValueError("positive divisor required")
    return -((-a) // b)


def ceil_fraction(value: Fraction) -> int:
    return ceil_div(value.numerator, value.denominator)


def centered_residue(value: int, modulus: int) -> int:
    value = exact_int(value, "value")
    modulus = exact_int(modulus, "modulus")
    r = value % modulus
    # Choose the negative representative at the exact half for deterministic symmetry.
    if 2*r >= modulus:
        r -= modulus
    return r


@dataclass(frozen=True)
class Sector:
    name: str
    value: int
    primes: tuple[int, ...]
    radical: int
    powerful: int
    sigma: Fraction

    @classmethod
    def build(cls, name: str, value: int) -> "Sector":
        value = exact_int(value, f"sector {name} value")
        primes = tuple(sorted(factor(value))) if value > 1 else tuple()
        rad = math.prod(primes) if primes else 1
        return cls(
            name=name,
            value=value,
            primes=primes,
            radical=rad,
            powerful=value // rad,
            sigma=sum((Fraction(1,p) for p in primes), Fraction(0,1)),
        )


@dataclass(frozen=True)
class LocalMovingProfile:
    sector: Sector
    base_target: int
    residues: tuple[int, ...]
    q0: int

    @classmethod
    def build(cls, sector: Sector, base_target: int) -> "LocalMovingProfile":
        base_target = exact_int(base_target, "base_target")
        if not sector.primes:
            if base_target != 0:
                raise ValueError(f"unit sector {sector.name} cannot carry target {base_target}")
            return cls(sector, base_target, tuple(), 0)
        weights = [sector.radical // p for p in sector.primes]
        residues = tuple(centered_residue(base_target * pow(w, -1, p), p) for p, w in zip(sector.primes, weights, strict=True))
        current = sum(w*r for w,r in zip(weights,residues,strict=True))
        diff = base_target - current
        if diff % sector.radical != 0:
            raise ArithmeticError((sector,base_target,residues,current))
        return cls(sector, base_target, residues, diff // sector.radical)

    def n_interval(self, height: int) -> tuple[int, int]:
        """All global n for which this sector has a lift of sup norm <= height."""
        height = exact_int(height, "height")
        if not self.sector.primes:
            # A unit sector carries no packet coordinate.  In the one-parameter
            # aggregate family it therefore pins the common shift to zero.
            return (0, 0)
        lower_sum = 0
        upper_sum = 0
        for p, residue in zip(self.sector.primes, self.residues, strict=True):
            lower = ceil_div(-height - residue, p)
            upper = (height - residue) // p
            if lower > upper:
                return (1, 0)
            lower_sum += lower
            upper_sum += upper
        return lower_sum - self.q0, upper_sum - self.q0

    def construct(self, n_global: int, height: int) -> dict[int,int]:
        n_global = exact_int(n_global, "n_global")
        height = exact_int(height, "height")
        if not self.sector.primes:
            return {}
        q = self.q0 + n_global
        lowers=[]; uppers=[]
        for p,residue in zip(self.sector.primes,self.residues,strict=True):
            lowers.append(ceil_div(-height-residue,p))
            uppers.append((height-residue)//p)
        if sum(lowers) > q or sum(uppers) < q:
            raise ValueError("height is not feasible")
        z=lowers[:]
        remaining=q-sum(z)
        for i in range(len(z)):
            take=min(remaining,uppers[i]-z[i])
            z[i]+=take
            remaining-=take
        if remaining:
            raise AssertionError("failed to distribute local quotient")
        x={p:res+p*zi for p,res,zi in zip(self.sector.primes,self.residues,z,strict=True)}
        if max(map(abs,x.values()),default=0)>height:
            raise AssertionError("constructed lift exceeds height")
        target=self.base_target+n_global*self.sector.radical
        weights={p:self.sector.radical//p for p in self.sector.primes}
        if sum(weights[p]*x[p] for p in self.sector.primes)!=target:
            raise AssertionError("local target mismatch")
        return x

    def gauge(self, n_global: int) -> tuple[int, dict[int,int]]:
        """Exact local lift gauge for target base+n*radical."""
        n_global = exact_int(n_global, "n_global")
        if not self.sector.primes:
            return 0, {}
        # A constructive upper bound from the centered residues plus quotient distribution.
        low=0
        high=max(1, max(abs(r) for r in self.residues))
        while True:
            lo,hi=self.n_interval(high)
            if lo<=n_global<=hi:
                break
            high*=2
        while low<high:
            mid=(low+high)//2
            lo,hi=self.n_interval(mid)
            if lo<=n_global<=hi:
                high=mid
            else:
                low=mid+1
        return low,self.construct(n_global,low)


@dataclass
class CosetResult:
    k: int
    height: int
    n_global: int
    targets: tuple[int, int, int]
    local_heights: tuple[int, int, int]
    vector: list[int]
    labels: list[str]
    phase_residues: tuple[int, ...]
    active_lower_sector: str
    active_upper_sector: str
    lower_bound: float
    lower_bound_exact: str
    gap_ratio: float
    gap_ratio_exact: str
    runtime_seconds: float


@dataclass
class TripleSearchResult:
    a: int
    b: int
    c: int
    radical: int
    quality: float
    omega: int
    phi: int
    best_k: int
    n_global: int
    targets: tuple[int, int, int]
    local_heights: tuple[int, int, int]
    vector: list[int]
    labels: list[str]
    support: int
    h1: int
    stable_height: float
    stable_height_exact: str
    master_gap: float
    master_gap_exact: str
    phase_integrality_factor: float
    phase_integrality_factor_exact: str
    primitive_improvement: float
    primitive_improvement_exact: str
    initial_k_bound: int
    final_k_bound: int
    k_evaluated: int
    endpoint_template: str
    runtime_seconds: float
    pairwise_verified: bool


class MovingEscapeSearch:
    def __init__(self,a:int,b:int):
        a = exact_int(a, "a")
        b = exact_int(b, "b")
        if a<=0 or b<=0 or math.gcd(a,b)!=1:
            raise ValueError("need positive coprime a,b")
        self.a=a; self.b=b; self.c=a+b
        self.sa=Sector.build("a",a); self.sb=Sector.build("b",b); self.sc=Sector.build("c",self.c)
        self.R=self.sa.radical*self.sb.radical*self.sc.radical
        self.Q=self.sa.powerful*self.sb.powerful*self.sc.powerful
        self.labels=[f"a:{p}" for p in self.sa.primes]+[f"b:{p}" for p in self.sb.primes]+[f"c:{p}" for p in self.sc.primes]

    def stable_height(self) -> Fraction:
        sa,sb,sc=self.sa.sigma,self.sb.sigma,self.sc.sigma
        # The three Helly intervals remain valid when one sector is the unit
        # sector, in which case its reciprocal support is simply zero.
        delta=min(
            sa+sb,
            Fraction(self.c,self.b)*(sa+sc),
            Fraction(self.c,self.a)*(sb+sc),
        )
        return Fraction(self.c,self.R)/delta

    def aggregate_profiles(self,k:int) -> tuple[LocalMovingProfile,LocalMovingProfile,LocalMovingProfile]:
        k = exact_int(k, "k")
        Pa,Pb,Pc=self.sa.powerful,self.sb.powerful,self.sc.powerful
        ra,rb,rc=self.sa.radical,self.sb.radical,self.sc.radical
        if not self.sa.primes:
            ta0=0
            tb0=k*Pc
            tc0=k*Pb
        elif not self.sb.primes:
            tb0=0
            ta0=-k*Pc
            tc0=-k*Pa
        else:
            g,u,v=xgcd(ra,rb)
            if g!=1:
                raise AssertionError("primitive triple radicals must be coprime")
            # u*ra+v*rb=1.  Then rb*(-v*kPc) subtracted from ra*(u*kPc) is kPc.
            ta0=-v*k*Pc
            tb0=u*k*Pc
            numerator=Pa*ta0+Pb*tb0
            if numerator%Pc:
                raise ArithmeticError((self.a,self.b,k,ta0,tb0,numerator,Pc))
            tc0=numerator//Pc
        return (
            LocalMovingProfile.build(self.sa,ta0),
            LocalMovingProfile.build(self.sb,tb0),
            LocalMovingProfile.build(self.sc,tc0),
        )

    @staticmethod
    def intersect(profiles: tuple[LocalMovingProfile,...],height:int) -> tuple[int,int,dict[str,tuple[int,int]]]:
        intervals={p.sector.name:p.n_interval(height) for p in profiles}
        lower=max(v[0] for v in intervals.values())
        upper=min(v[1] for v in intervals.values())
        return lower,upper,intervals

    def coset(self,k:int) -> CosetResult:
        k = exact_int(k, "k")
        if k<=0: raise ValueError("k must be positive")
        start=time.perf_counter()
        profiles=self.aggregate_profiles(k)
        stable_fraction=self.stable_height()*k
        stable=float(stable_fraction)
        low=max(0,ceil_fraction(stable_fraction))
        # n=0 gives an easy upper bound if all three sectors are nonunit.  Otherwise profiles have fixed targets.
        candidate=[]
        for p in profiles:
            h,_=p.gauge(0)
            candidate.append(h)
        high=max(candidate)
        if high<low: high=low
        while True:
            lo,hi,_=self.intersect(profiles,high)
            if lo<=hi: break
            high=max(high+1,2*high)
        while low<high:
            mid=(low+high)//2
            lo,hi,_=self.intersect(profiles,mid)
            if lo<=hi: high=mid
            else: low=mid+1
        height=low
        lo,hi,intervals=self.intersect(profiles,height)
        if lo>hi: raise AssertionError("binary search failed")
        # Choose the feasible n nearest zero for reproducibility.
        n=0 if lo<=0<=hi else (lo if lo>0 else hi)
        local=[profile.gauge(n) for profile in profiles]
        local_heights=tuple(item[0] for item in local)
        vectors=[item[1] for item in local]
        vector=[vectors[0][p] for p in self.sa.primes]+[vectors[1][p] for p in self.sb.primes]+[vectors[2][p] for p in self.sc.primes]
        targets=tuple(profile.base_target+n*profile.sector.radical for profile in profiles)
        phase_residues=tuple(residue for profile in profiles for residue in profile.residues)
        if max(map(abs,vector),default=0)!=height:
            raise AssertionError("local gauges do not attain the global height")
        lam=[]; wr=[]
        for sector,nval,sign in ((self.sa,self.a,1),(self.sb,self.b,1),(self.sc,self.c,-1)):
            for p in sector.primes:
                lam.append(sign*nval//p)
                if sector.name=="a": wr.append(-(self.a*self.b)//p)
                elif sector.name=="b": wr.append((self.a*self.b)//p)
                else: wr.append(0)
        if sum(l*x for l,x in zip(lam,vector,strict=True))!=0:
            raise AssertionError("global additivity failed")
        if sum(w*x for w,x in zip(wr,vector,strict=True))!=k*self.Q:
            raise AssertionError(("global obstruction failed",k,self.Q,sum(w*x for w,x in zip(wr,vector,strict=True))))
        # Identify the pair of sectors that closes the interval at the optimum.
        lower_sector=max(intervals,key=lambda s:intervals[s][0])
        upper_sector=min(intervals,key=lambda s:intervals[s][1])
        return CosetResult(
            k=k,height=height,n_global=n,targets=targets,local_heights=local_heights,
            vector=vector,labels=self.labels,phase_residues=phase_residues,
            active_lower_sector=lower_sector,active_upper_sector=upper_sector,
            lower_bound=stable,lower_bound_exact=fraction_text(stable_fraction),
            gap_ratio=float(Fraction(height,1)/stable_fraction),
            gap_ratio_exact=fraction_text(Fraction(height,1)/stable_fraction),
            runtime_seconds=time.perf_counter()-start,
        )

    def search(self) -> TripleSearchResult:
        start=time.perf_counter()
        h1=self.coset(1)
        best=h1
        stable_fraction=self.stable_height()
        stable=float(stable_fraction)
        # H(k)>=k*stable. Once this reaches the current best, larger k cannot improve it.
        initial_k_bound=max(1,ceil_fraction(Fraction(best.height,1)/stable_fraction)-1)
        k_limit=initial_k_bound
        evaluated=1
        k=2
        while k<=k_limit:
            if k*stable_fraction<best.height:
                result=self.coset(k); evaluated+=1
                if result.height<best.height or (result.height==best.height and result.k<best.k):
                    best=result
                    k_limit=min(k_limit,max(1,ceil_fraction(Fraction(best.height,1)/stable_fraction)-1))
            k+=1
        quality=math.log(self.c)/math.log(self.R)
        if not self.sa.primes:
            endpoint="unit-a"
        elif not self.sb.primes:
            endpoint="unit-b"
        else:
            endpoint=f"{best.active_lower_sector}->{best.active_upper_sector}"
        return TripleSearchResult(
            a=self.a,b=self.b,c=self.c,radical=self.R,quality=quality,omega=len(self.labels),
            phi=best.height,best_k=best.k,n_global=best.n_global,
            targets=best.targets,local_heights=best.local_heights,
            vector=best.vector,labels=self.labels,support=sum(value!=0 for value in best.vector),
            h1=h1.height,stable_height=stable,stable_height_exact=fraction_text(stable_fraction),
            master_gap=float(Fraction(best.height,1)/stable_fraction),
            master_gap_exact=fraction_text(Fraction(best.height,1)/stable_fraction),
            phase_integrality_factor=float(Fraction(best.height,best.k)/stable_fraction),
            phase_integrality_factor_exact=fraction_text(Fraction(best.height,best.k)/stable_fraction),
            primitive_improvement=float(Fraction(h1.height,best.height)),
            primitive_improvement_exact=fraction_text(Fraction(h1.height,best.height)),
            initial_k_bound=initial_k_bound,final_k_bound=k_limit,k_evaluated=evaluated,
            endpoint_template=endpoint,
            runtime_seconds=time.perf_counter()-start,pairwise_verified=False,
        )


def top_known_triples() -> list[tuple[int,int]]:
    """Twenty historically high-quality triples from the Leiden list, encoded by factorization."""
    p=lambda *items: math.prod(base**exp for base,exp in items)
    triples=[
        (2, p((3,10),(109,1))),
        (11**2, p((3,2),(5,6),(7,3))),
        (19*1307, p((7,1),(29,2),(31,8))),
        (283, p((5,11),(13,2))),
        (1,2*3**7),
        (7**3,3**10),
        (7**2*41**2*311**3,11**16*13**2*79),
        (5**3,2**9*3**17*13**2),
        (13*19**6,2**30*5),
        (3**18*23*2269,17**3*29*31**8),
        (13**10*37**2,3**7*19**5*71**4*223),
        (2**7*23**8,19**9*857**2),
        (239,5**8*17**3),
        (5**2*7937,7**13),
        (2**2*11,3**2*13**10*17*151*4423),
        (73,2**13*7**7*941**2),
        (2**24,11**7*19*29**2),
        (11**2,3**9*13),
        (37,2**15),
        (5**14*19,2**5*3*7**13),
    ]
    for a,b in triples:
        if math.gcd(a,b)!=1:
            raise AssertionError((a,b))
    return triples


def enumerate_hits(limit:int=10000,quality_threshold:float=1.0) -> list[tuple[int,int]]:
    # Precompute radicals by a smallest-prime-factor sieve.
    spf=list(range(limit+1))
    for p in range(2,int(limit**0.5)+1):
        if spf[p]==p:
            for n in range(p*p,limit+1,p):
                if spf[n]==n: spf[n]=p
    rad=[1]*(limit+1)
    for n in range(2,limit+1):
        x=n;r=1
        while x>1:
            p=spf[x];r*=p
            while x%p==0:x//=p
        rad[n]=r
    out=[]
    for c in range(3,limit+1):
        rc=rad[c]
        for a in range(1,c//2+1):
            b=c-a
            if math.gcd(a,b)!=1: continue
            R=rad[a]*rad[b]*rc
            if math.log(c)/math.log(R)>quality_threshold:
                out.append((a,b))
    return out


def write_csv(path:Path,rows:list[TripleSearchResult]) -> None:
    data=[]
    for row in rows:
        d=asdict(row)
        for key,value in list(d.items()):
            if isinstance(value,(tuple,list)):
                d[key]=' '.join(map(str,value))
        data.append(d)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]))
        w.writeheader();w.writerows(data)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--hits-limit',type=int,default=10000)
    args=parser.parse_args()
    base=args.base.resolve();(base/'tables').mkdir(exist_ok=True);(base/'results').mkdir(exist_ok=True)
    sets={
        'existing50':[(int(r['a']),int(r['b'])) for r in csv.DictReader(open(base/'data'/'attack_iii_obstruction_metrics.csv', newline='', encoding='utf-8'))],
        'hits':enumerate_hits(args.hits_limit,1.0),
        'top20':top_known_triples(),
    }
    summary={}
    for name,pairs in sets.items():
        rows=[]
        for i,(a,b) in enumerate(pairs):
            result=MovingEscapeSearch(a,b).search();rows.append(result)
        write_csv(base/'tables'/f'{name}_moving_search.csv',rows)
        summary[name]={
            'triples':len(rows),
            'max_best_k':max(r.best_k for r in rows),
            'best_k_counts':{str(k):sum(r.best_k==k for r in rows) for k in sorted(set(r.best_k for r in rows))},
            'endpoint_templates':{t:sum(r.endpoint_template==t for r in rows) for t in sorted(set(r.endpoint_template for r in rows))},
            'max_initial_k_bound':max(r.initial_k_bound for r in rows),
            'max_final_k_bound':max(r.final_k_bound for r in rows),
            'median_k_evaluated':float(median([r.k_evaluated for r in rows])),
            'median_master_gap':float(median([r.master_gap for r in rows])),
            'max_master_gap':max(r.master_gap for r in rows),
            'median_runtime_seconds':float(median([r.runtime_seconds for r in rows])),
            'max_runtime_seconds':max(r.runtime_seconds for r in rows),
        }
    (base/'results'/'moving_search_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
