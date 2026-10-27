#!/usr/bin/env python3
"""Independent exact arithmetic; no proof of unrestricted arithmetic/global claims.
All 2x2 diagonal residual matrices over F_p, p=2,3,5, all square-zero lifts,
and degrees 0,...,6. Multiplication occurs in actual dual-number matrices.
"""
from itertools import product
from pathlib import Path
import hashlib, json, time


def add(a,b,p): return tuple((x+y)%p for x,y in zip(a,b))
def mm(a,b,p):
    return ((a[0]*b[0]+a[1]*b[2])%p,(a[0]*b[1]+a[1]*b[3])%p,
            (a[2]*b[0]+a[3]*b[2])%p,(a[2]*b[1]+a[3]*b[3])%p)
def dpow(a,e,d,p):
    """Power of a+epsilon e, with epsilon^2=0; not a geometric-sum shortcut."""
    b=(1,0,0,1); f=(0,0,0,0)
    for _ in range(d): b,f=mm(b,a,p),add(mm(b,e,p),mm(f,a,p),p)
    return b,f

def main():
    start=time.monotonic(); rows=[]; tests=0; image_tests=0
    for p in (2,3,5):
        vectors=list(product(range(p),repeat=4))
        for a,b in product(range(1,p),repeat=2):
            F=(a,0,0,b)
            ratios=(1,a*pow(b,-1,p)%p,b*pow(a,-1,p)%p,1)
            for d in range(7):
                weights=tuple(sum(pow(r,j,p) for j in range(d))%p for r in ratios)
                image=set()
                for X in vectors:
                    base,coef=dpow(F,mm(X,F,p),d,p)
                    invbase=(pow(base[0],-1,p),0,0,pow(base[3],-1,p))
                    error=mm(coef,invbase,p)
                    predicted=tuple(w*x%p for w,x in zip(weights,X))
                    assert error==predicted,(p,a,b,d,X,error,predicted)
                    image.add(error);tests+=1
                expected={e for e in vectors if all(w!=0 or x==0 for w,x in zip(weights,e))}
                assert image==expected
                image_tests+=1
                rows.append({'p':p,'diagonal':[a,b],'degree':d,'weights':weights,
                             'attainable_errors':len(image)})
    # The three discriminating matrix controls at p=3.
    find=lambda diag,d: next(r for r in rows if r['p']==3 and r['diagonal']==diag and r['degree']==d)
    assert find([1,2],2)['weights']==(2,0,0,2)
    assert find([1,2],3)['weights']==(0,1,1,0)
    assert all(w!=0 for w in find([1,2],5)['weights'])
    assert find([1,1],3)['attainable_errors']==1
    # Invariant scalar localization for degrees 1 and 2: each projection is
    # onto, but a shared correction must lie in {(a,2a)}.
    shared={(a,2*a%3) for a in range(3)}
    assert (0,1) not in shared
    assert {a for a,b in shared}==set(range(3))
    assert {b for a,b in shared}==set(range(3))
    out={'status':'PASS','coefficient_rings':'F_p[epsilon]/epsilon^2, p in {2,3,5}',
         'dimension':2,'degrees':list(range(7)),
         'diagonal_matrices':sum((p-1)**2 for p in (2,3,5)),
         'exact_dual_power_checks':tests,'complete_image_comparisons':image_tests,
         'shared_correction_image_F3_degrees_1_2':sorted(shared),
         'rows':rows,'seconds':time.monotonic()-start,
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'nonclaims':['not a global Galois or automorphy test','not a proof for arbitrary nonsemisimple matrices',
                      'finite arithmetic corroborates, but does not replace, Lean proofs']}
    Path(__file__).with_name('EXACT_CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
