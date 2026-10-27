#!/usr/bin/env python3
"""Independent finite checks for the 1.3.0 worked derivations.

Exact rational and permutation arithmetic. This script does not execute Lean
and does not prove an infinite or arbitrary-input theorem by enumeration.
"""
from __future__ import annotations
from fractions import Fraction as F
from itertools import product, permutations
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT=Path(__file__).resolve().parents[1]
counts: dict[str,int]={}
cases: dict[str,int]={}
controls: list[dict[str,object]]=[]

def check(condition: bool, group: str) -> None:
    if not condition:
        raise AssertionError(f'Failed exact check in {group}')
    counts[group]=counts.get(group,0)+1

def case(group: str) -> None:
    cases[group]=cases.get(group,0)+1

def dot(a,b): return sum((x*y for x,y in zip(a,b)),F(0))
def matvec(a,x): return tuple(dot(row,x) for row in a)
def transpose(a): return tuple(zip(*a))
def matmul(a,b): return tuple(tuple(dot(row,col) for col in transpose(b)) for row in a)
def norm2(x): return dot(x,x)
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def perm_mul(a,b): return tuple(a[b[i]] for i in range(3))
def inv(a): return tuple(a.index(i) for i in range(3))

def rejected(name, false_claim):
    check(not false_claim,'negative_controls')
    controls.append({'name':name,'false_claim_rejected':True})

def run() -> dict:
    # Integral intermediate choices, with exact feasibility and ambiguity.
    for k in range(-4,5):
        for m in range(-21,22):
            case('integer_branches')
            roots=[n for n in range(-12,13) if 2*n==m]
            check(bool(roots)==(m%2==0),'integer_branches')
            check(len(roots)<=1,'integer_branches')
            if roots:
                n=roots[0];x=((k,0),(k,2*n),(k,n))
                check((x[1][0],0)==x[0] and (x[2][0],2*x[2][1])==x[1],'integer_branches')
    # Coefficient domain and ambiguity. This is finite modular arithmetic,
    # not a claim of a new group-theoretic Lean instantiation.
    for p in (2,3,5,7):
        kernel=[n for n in range(p) if (2*n)%p==0]
        for m in range(p):
            roots=[n for n in range(p) if (2*n)%p==m]
            case('coefficient_domains')
            check(not roots or len(roots)==len(kernel),'coefficient_domains')
            check((len(roots)==1) if p!=2 else (len(roots)==(2 if m==0 else 0)),'coefficient_domains')
    # Binary prefix presentations and composition, independent list operations.
    for length in range(2,11):
        for word in product((0,1),repeat=length):
            case('binary_prefixes')
            diff=lambda w:tuple(w[i]^w[i+1] for i in range(len(w)-1))
            one=diff(word);two=diff(one)
            check(two==tuple(word[i]^word[i+2] for i in range(length-2)),'binary_prefixes')
            for n in range(length):
                check(diff(word[:n+1])==one[:n],'binary_prefixes')
    levels=(2,0,4,1,6,3,8,2,9,4)
    envelope=tuple(max(levels[:i+1]) for i in range(len(levels)))
    for i in range(len(levels)):
        check(envelope[i]>=levels[i],'finite_schedule')
        if i:check(envelope[i]>=envelope[i-1],'finite_schedule')
    # Block triangular transport and section-dependent repair.
    for u,r,a,b,c in product(range(-2,3),repeat=5):
        case('repair_mismatch')
        pa=(u-a*r,0)
        sx=(u+c*r,r)
        pbs=(sx[0]-b*sx[1],0)
        spa=(pa[0]+c*pa[1],pa[1])
        mismatch=((a+c-b)*r,0)
        check(sub(pbs,spa)==mismatch,'repair_mismatch')
        check(mismatch[1]==0,'repair_mismatch')
        # In charts chi_b S chi_a^{-1}(u,r).
        source=(u+a*r,r);target=(source[0]+c*r,r)
        chart=(target[0]-b*target[1],target[1])
        check(chart==(u+(a+c-b)*r,r),'repair_mismatch')
    for a,b,d,c1,c2,r in product(range(-1,2),repeat=6):
        case('mismatch_composition')
        m1=(a+c1-b)*r;m2=(b+c2-d)*r
        check((a+c1+c2-d)*r==m1+m2,'mismatch_composition')
    # Cycle differences, affine primitives, orthogonal residual repairs.
    for n in range(1,7):
        for raw in product((-1,0,1),repeat=n):
            case('cycle_residuals')
            r=tuple(map(F,raw));s=sum(r,F(0))
            repaired=tuple(t-s/n for t in r)
            check(sum(repaired,F(0))==0,'cycle_residuals')
            primitive=[F(0)]
            for t in repaired[:-1]:primitive.append(primitive[-1]+t)
            recovered=tuple(primitive[(i+1)%n]-primitive[i] for i in range(n))
            check(recovered==repaired,'cycle_residuals')
            err=sub(r,repaired)
            check(norm2(err)==s*s/n,'cycle_residuals')
            for i in range(max(0,n-1)):
                basis=tuple(F(int(j==i)-int(j==n-1)) for j in range(n))
                check(dot(err,basis)==0,'cycle_residuals')
            protected=r[:-1]+(-sum(r[:-1],F(0)),)
            check(protected[:-1]==r[:-1] and sum(protected,F(0))==0,'cycle_residuals')
            check(norm2(sub(r,protected))==s*s,'cycle_residuals')
    # Duplicated groupoid: all S3 marked objects and comparisons.
    H=tuple(permutations(range(3)));one=(0,1,2)
    objects=tuple(product(H,H))
    arrows={}
    for source in objects:
        r,phi=source
        for target in objects:
            rp,psi=target
            a0=perm_mul(inv(psi),phi)
            a1=perm_mul(perm_mul(inv(rp),a0),r)
            arrows[(source,target)]=(a0,a1)
            case('marked_S3_comparisons')
            check(perm_mul(perm_mul(a0,r),inv(a1))==rp,'marked_S3_comparisons')
            check(perm_mul(psi,a0)==phi,'marked_S3_comparisons')
            # Independently enumerate all raw gauges to check uniqueness.
            solutions=[(b0,b1) for b0 in H for b1 in H if
                       perm_mul(perm_mul(b0,r),inv(b1))==rp and perm_mul(psi,b0)==phi]
            check(solutions==[(a0,a1)],'marked_S3_comparisons')
    for x,y,z in product(objects,repeat=3):
        a=arrows[(x,y)];b=arrows[(y,z)];c=arrows[(x,z)]
        case('marked_S3_composition')
        check((perm_mul(b[0],a[0]),perm_mul(b[1],a[1]))==c,'marked_S3_composition')
    # Reflection triangle: all candidate coordinates in {-1,0,1}.
    A=((-1,1,0),(0,-1,1),(1,0,-1))
    B=((-1,1,0),(0,-1,1),(-1,0,-1))
    ones=(1,1,1);v=(1,-1,1)
    gram_a=matmul(transpose(A),A);gram_b=matmul(transpose(B),B)
    check(gram_a==tuple(tuple(3*int(i==j)-1 for j in range(3)) for i in range(3)),'triangle_gram')
    check(gram_b==tuple(tuple(int(i==j)+v[i]*v[j] for j in range(3)) for i in range(3)),'triangle_gram')
    for raw in product((-1,0,1),repeat=6):
        case('triangle_candidates')
        a=tuple(map(F,raw[:3]));b=tuple(map(F,raw[3:]));m=sum(a,F(0))/3
        nearest=(m,m,m);anchor=(a[0],)*3
        e=norm2(sub(a,nearest))+norm2(b)
        ea=norm2(sub(a,anchor))+norm2(b)
        residual=norm2(matvec(A,a))+norm2(matvec(B,b))
        check(e<=residual,'triangle_candidates')
        check(ea==e+3*(m-a[0])**2,'triangle_candidates')
        check(sum(matvec(B,b),F(0))==-2*b[0],'triangle_candidates')
    a=(F(2),F(4),F(3));b=(F(1),F(-1),F(2))
    check(norm2(matvec(A,a))+norm2(matvec(B,b))==28,'displayed_values')
    check(norm2(sub(a,(3,3,3)))+norm2(b)==8,'displayed_values')
    check(norm2(sub(a,(2,2,2)))+norm2(b)==11,'displayed_values')
    check(norm2(matvec(B,(1,1,0)))==norm2((1,1,0)),'displayed_values')
    # Sharp preserved-kernel gain, exact squared reference-uncertainty check.
    for j in range(10):
        t=F(j,10);gain=1/(1-t)
        for a,b in product(range(-4,5),repeat=2):
            case('uncertainty_certificates')
            check(gain*abs((1-t)*a)==abs(a),'uncertainty_certificates')
            distance2=t*t*b*b
            reference_bound2=t*t*(t*t*b*b+b*b)
            check(distance2<=reference_bound2,'uncertainty_certificates')
    # Explicit false claims. Never add these to the positive theorem inventory.
    rejected('odd integer middle value extends with a rounded half',2*(1//2)==1)
    rejected('unprotected average repair preserves the first three edges',
             (F(3,4),F(-1,4),F(-1,4))==(F(1),F(0),F(0)))
    rejected('coherent prefix automatically satisfies closing edge',sum((1,0,0,0))==0)
    rejected('all compatible representation changes commute with selected repair',(2,0)==(0,0))
    rejected('zero changed-model output means reference exactness',abs(-10)==0)
    rejected('reflection holonomy excludes all nonzero anchor values',(3,0)!=(3,-0))
    transposition=(1,0,2)
    rejected('fully framed distinct cocycles admit a comparison',
             perm_mul(perm_mul(one,transposition),inv(one))==one)
    rejected('rational half is an integral completion',F(1,2).denominator==1)
    # Check that the entire retained formal tree is unchanged this edition.
    baseline=json.loads((ROOT/'audit/expansion/baseline.json').read_text())
    current={str(p.relative_to(ROOT/'formal')):hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted((ROOT/'formal').rglob('*')) if p.is_file() and '.lake' not in p.parts and '__pycache__' not in p.parts}
    check(current==baseline['formal_files'],'formal_tree_integrity')
    return {'status':'PASS','publication_version':'1.3.0','executed_utc':datetime.now(timezone.utc).isoformat(),
            'assertions':sum(counts.values()),'assertions_by_group':counts,'cases_by_group':cases,
            'negative_controls':controls,'formal_baseline_unchanged':True,
            'new_lean_compilation_this_edition':False,
            'scope':'Exact finite regression and baseline byte identity. Infinite and arbitrary-input statements rely on their written proofs and identified retained Lean declarations, not on this enumeration.'}

if __name__=='__main__':
    try:
        result=run()
    except Exception as exc:
        result={'status':'FAIL','executed_utc':datetime.now(timezone.utc).isoformat(),
                'assertions_completed':sum(counts.values()),'counts':counts,'error':repr(exc)}
        (ROOT/'audit/expansion_exact.json').write_text(json.dumps(result,indent=2)+'\n')
        raise
    (ROOT/'audit/expansion_exact.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
