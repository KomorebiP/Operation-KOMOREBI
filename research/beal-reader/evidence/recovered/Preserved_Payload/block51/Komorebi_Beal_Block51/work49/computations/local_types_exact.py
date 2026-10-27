"""Exact checks supporting local_types.md; no p-adic geometry is implemented."""
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import json

# Exact quadratic algebra Q[r]/(r^2+r-1), encoded by (constant, r coefficient).
def add(a, b): return (a[0]+b[0], a[1]+b[1])
def neg(a): return (-a[0], -a[1])
def mul(a, b):
    return (a[0]*b[0]+a[1]*b[1], a[0]*b[1]+a[1]*b[0]-a[1]*b[1])
def scale(a, c): return (a[0]*c, a[1]*c)
def power(a, n):
    z = (Q(1), Q(0))
    for _ in range(n): z=mul(z,a)
    return z
def pmul(a,b):
    c=[Q(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): c[i+j]+=x*y
    return c
def hull(points):
    out=[]
    for p in points:
        while len(out)>=2:
            a,b=out[-2:]
            cross=(b[0]-a[0])*(p[1]-b[1])-(b[1]-a[1])*(p[0]-b[0])
            if cross>0: break
            out.pop()
        out.append(p)
    return out

def main():
    r=(Q(0),Q(1)); one=(Q(1),Q(0))
    g=[-1,1,1]; h=[5,-2,1]
    f0=[5,-12,0,10,0,0,1]
    assert pmul(pmul(g,g),h)==f0
    shifted=[]
    for j in range(7):
        a=(Q(0),Q(0))
        for k in range(j,7): a=add(a,scale(power(r,k-j),f0[k]*comb(k,j)))
        shifted.append(a)
    expected=[(0,0),(0,0),(30,-15),(-10,40),(15,-15),(0,6),(1,0)]
    assert shifted==expected
    # r^3+1=2r, so the three-adic constant perturbation is 20 r eps+5eps^2.
    assert add(power(r,3),one)==scale(r,2)
    # h(r)=6-3r, and the conjugate radicand is 9+3r.
    d=(Q(6),Q(-3)); dc=(Q(9),Q(3)); phi=add(one,r)
    assert mul(d,power(phi,2))==dc
    assert mul(d,dc)==(Q(45),Q(0))
    # D h(r) is a square for both twins: D^2 and (D phi)^2.
    assert mul(d,dc)==power(mul(d,phi),2)
    rows=[]
    for c in range(1,101):
        v3=[7*c,7*c+1,1,0,1,1,0]
        v5=[14*c,14*c,3,2,2,0,0]
        h3=hull(list(enumerate(v3)))
        h5=hull(list(enumerate(v5)))
        assert h3==[(0,7*c),(2,1),(3,0),(6,0)]
        assert h5==[(0,14*c),(2,3),(5,0),(6,0)]
        d3=Q(7*c-1,2); d5=Q(14*c-3,2)
        n3=2*(d3-1); n5=2*(d5-1)
        assert n3==7*c-3 and n5==14*c-5
        # Orthogonal discriminant check: two triples / five-cluster.
        assert 4*d3+8==6+14*c
        assert 4*d5+16==10+28*c
        assert n3%7==4 and n5%7==2
        rows.append({"c":c,"v3_vertices":h3,"v5K_vertices":h5,
                     "n3":int(n3),"n5":int(n5)})
    out={"status":"passed","domain":"Q[r]/(r^2+r-1), exact fractions",
         "algebra_checks":["limiting factorization","translated coefficients",
                           "three-adic constant perturbation","radicand square classes"],
         "finite_checks":{"c_min":1,"c_max":100,"rows":rows},
         "non_claims":["No p-adic geometry implemented", "No universal conclusion from finite c loop",
                       "No independent recomputation of source theorems"]}
    dest=Path("work49/verification/local_types_run/result.json")
    dest.write_text(json.dumps(out,indent=2)+"\n")
    print("PASS: exact symbolic identities and c=1..100 Newton polygon/discriminant checks")

if __name__=="__main__": main()
