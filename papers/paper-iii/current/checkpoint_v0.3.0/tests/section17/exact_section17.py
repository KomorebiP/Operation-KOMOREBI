#!/usr/bin/env python3
"""Independent exact-rational probes for Paper III Section 17.

Checks finite illustrations of the written proof; not a proof of all dimensions,
not a Lean replay, and not a numerical estimate disguised as a certificate.
Uses sympy for symbolic derivative controls, Fractions for tensor/norm tests.
"""
from __future__ import annotations
import argparse
import itertools
import json
import random
import sys
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

seed = 20261019
rng = random.Random(seed)
checks = Counter()
controls = {}

def check(cond: bool, label: str):
    checks[label] += 1
    if not cond:
        raise AssertionError(f"{label}: false")

def zmat(n, m): return [[Q(0) for _ in range(m)] for _ in range(n)]
def eye(n): return [[Q(int(i==j)) for j in range(n)] for i in range(n)]
def mat(A, B):
    assert len(A[0]) == len(B)
    return [[sum((A[i][k] * B[k][j] for k in range(len(B))), Q(0))
             for j in range(len(B[0]))] for i in range(len(A))]
def mv(A, x): return [sum((a*y for a,y in zip(row, x)), Q(0)) for row in A]
def msum(A, B): return [[a+b for a,b in zip(r,s)] for r,s in zip(A,B)]
def vsum(vectors, dim):
    # Freeze one-shot iterators: every output component must sum the *same*
    # tensor terms. Without this, a generator would be exhausted after i=0.
    vectors=list(vectors)
    return [sum((v[i] for v in vectors), Q(0)) for i in range(dim)]
def random_vec(dim): return [Q(rng.randrange(-5,6)) for _ in range(dim)]

def oblique_projectors(d: int):
    import sympy as s
    # A is triangular with diagonal 1, hence invertible over Q.
    A = s.eye(d)
    for i in range(d):
        for j in range(i+1,d):
            A[i,j] = rng.randint(-3,3)
    Ainv = A.inv()
    ans = []
    for i in range(d):
        E = s.zeros(d)
        E[i,i] = 1
        C = A*E*Ainv
        ans.append([[Q(int(C[a,b].p),int(C[a,b].q)) if C[a,b] else Q(0)
                     for b in range(d)] for a in range(d)])
    # Oblique systems have individually idempotent, mutually annihilating projectors
    # and their sum is identity. These checks are not assumptions in the evaluator.
    for i in range(d):
        check(mat(ans[i],ans[i]) == ans[i],"projector_idempotence")
        for j in range(d):
            if i!=j: check(mat(ans[i],ans[j]) == zmat(d,d),"projector_annihilation")
    accum = zmat(d,d)
    for P in ans: accum=msum(accum,P)
    check(accum == eye(d),"projector_completeness")
    return ans

# Tensor T[out, (in_1,..,in_r)] evaluated multilinearly on r input vectors.
def tensor_coeffs(outdim, indim, r):
    return {(o,) + t : Q(rng.randrange(-3,4))
            for o in range(outdim)
            for t in itertools.product(range(indim), repeat=r)}
def tensor_eval(T, outdim, indim, r, xs):
    assert len(xs)==r
    if r>0: assert all(len(v)==indim for v in xs)
    return [sum((T[(o,)+ind]*prod(xs[k][ind[k]] for k in range(r))
                 for ind in itertools.product(range(indim),repeat=r)),Q(0))
            for o in range(outdim)]
def prod(items):
    val=Q(1)
    for v in items: val*=v
    return val

def norm_mat_inf(A): return max(sum(map(abs,row)) for row in A)
def norm_tensor_inf(T,outdim,indim,r):
    """Exact real l-infinity multilinear operator norm.
    A multilinear map's coordinate extrema on product cubes occur at signed
    vertices (one affine coordinate at a time). This is an exhaustive finite
    certificate for these specific tensors, not a general computational proof.
    """
    sign_vectors = list(itertools.product((Q(-1),Q(1)),repeat=indim))
    return max(max(map(abs, tensor_eval(T,outdim,indim,r,xs)))
               for xs in itertools.product(sign_vectors,repeat=r))

def extended_jet(T,outdim,indim,r,P,Qproj,input_labels,h):
    return mv(Qproj,tensor_eval(T,outdim,indim,r,
                                [mv(P[input_labels[k]],h[k]) for k in range(r)]))


def arbitrary_resolution(d: int, pieces: int):
    """Complete but usually non-idempotent/overlapping linear families."""
    assert pieces >= 2
    ans=[];acc=zMat=zmat(d,d)
    for _ in range(pieces-1):
        m=[[Q(rng.randrange(-3,4)) for _ in range(d)] for _ in range(d)]
        ans.append(m);acc=msum(acc,m)
    ans.append([[eye(d)[i][j]-acc[i][j] for j in range(d)] for i in range(d)])
    tot=zmat(d,d)
    for a in ans:tot=msum(tot,a)
    check(tot==eye(d),"general_resolution_completeness")
    return ans


def check_general_resolutions():
    """Tests algebraic expansion beyond idempotent or orthogonal families."""
    saw_nonidempotent=0
    for case in range(45):
        d=2 if case%4 else 3
        q=2 if case%5 else 3
        r=case%4
        P=arbitrary_resolution(d,2+(case%2))
        S=arbitrary_resolution(q,2+((case+1)%2))
        if any(mat(z,z)!=z for z in P):saw_nonidempotent+=1
        T=tensor_coeffs(q,d,r)
        h=[random_vec(d) for _ in range(r)]
        full=tensor_eval(T,q,d,r,h)
        summands=(extended_jet(T,q,d,r,P,S[gamma],alpha,h)
                  for gamma in range(len(S))
                  for alpha in itertools.product(range(len(P)),repeat=r))
        check(full==vsum(summands,q),"nonidempotent_complete_resolution_expansion")
    check(saw_nonidempotent==45,"general_result_uses_no_idempotence")


def check_multilinear():
    for case in range(75):
        indim=2 if case%5 else 3
        outdim=2 if case%7 else 3
        r=case%4
        P=oblique_projectors(indim)
        S=oblique_projectors(outdim)
        T=tensor_coeffs(outdim,indim,r)
        h=[random_vec(indim) for _ in range(r)]
        left=tensor_eval(T,outdim,indim,r,h)
        labels=itertools.product(range(indim),repeat=r)
        terms=[]
        for gamma in range(outdim):
            for alpha in labels if gamma==0 else itertools.product(range(indim),repeat=r):
                terms.append(extended_jet(T,outdim,indim,r,P,S[gamma],alpha,h))
        right=vsum(terms,outdim)
        check(left==right,"complete_multilinear_reconstruction")
        check(vsum([mv(p,h[0]) for p in P],indim)==h[0] if r else True,
              "projected_input_identity")
        # Every block applied to actual packet vectors is in output range.
        if r:
            for gamma in range(outdim):
                alpha=tuple(rng.randrange(indim) for _ in range(r))
                v=extended_jet(T,outdim,indim,r,P,S[gamma],alpha,h)
                check(mv(S[gamma],v)==v,"jet_output_range_membership")
        # An independent reconstruct-each-slot rather than expand-in-one-sweep test.
        for gamma in range(outdim):
            check(mv(S[gamma],left)==vsum([
                extended_jet(T,outdim,indim,r,P,S[gamma],alpha,h)
                for alpha in itertools.product(range(indim),repeat=r)],outdim),
                "per_output_jet_expansion")


def check_norm_bounds():
    # Exact real infinity norms; oblique projectors can have norm greater than 1.
    for case in range(16):
        d=2 if case%3 else 3
        r=1 if d==3 else (case%3+1)
        P=oblique_projectors(d)
        S=oblique_projectors(d)
        T=tensor_coeffs(d,d,r)
        full=norm_tensor_inf(T,d,d,r)
        labels=itertools.product(range(d),repeat=r)
        for alpha in labels:
            for gamma in range(d):
                Qp=S[gamma]
                # The restricted map is a continuous multilinear map of the
                # same ambient dimension by inserting the given projectors.
                Tproj={}
                for o in range(d):
                    for slots in itertools.product(range(d),repeat=r):
                        unit=[]
                        for k in range(r):
                            e=[Q(int(j==slots[k])) for j in range(d)]
                            unit.append(e)
                        Tproj[(o,)+slots]=extended_jet(
                            T,d,d,r,P,Qp,alpha,unit)[o]
                block=norm_tensor_inf(Tproj,d,d,r)
                bound=norm_mat_inf(Qp)*full*prod(norm_mat_inf(P[a]) for a in alpha)
                check(block<=bound,"ambient_multilinear_norm_bound")
                if block>0:
                    check(bound>0,"nonzero_jet_has_positive_certificate")


def partitions(n):
    """All unordered partitions of 0..n-1, blocks in canonical creation order."""
    if n==0: yield tuple(); return
    def rec(i,blocks):
        if i==n:
            yield tuple(tuple(block) for block in blocks)
            return
        for j in range(len(blocks)):
            blocks[j].append(i)
            yield from rec(i+1,blocks)
            blocks[j].pop()
        blocks.append([i])
        yield from rec(i+1,blocks)
        blocks.pop()
    yield from rec(0,[])

@lru_cache(None)
def stirling(n,k):
    if n==0: return int(k==0)
    if k==0: return 0
    return k*stirling(n-1,k)+stirling(n-1,k-1)

def check_touchard():
    for n in range(1,8):
        counts=Counter(len(pi) for pi in partitions(n))
        for k,v in counts.items():
            check(v==stirling(n,k),"stirling_partition_counts")
        for m in range(0,5):
            labeled_direct=sum(m**len(pi) for pi in partitions(n))
            touchard=sum(stirling(n,k)*m**k for k in range(1,n+1))
            check(labeled_direct==touchard,"touchard_labeled_term_counts")


def sym_vec(v):
    import sympy as s
    return s.Matrix([s.Rational(u.numerator,u.denominator) for u in v])

def frac_vec(v):
    return [Q(int(v[i].p),int(v[i].q)) for i in range(v.rows)]

def check_second_chain():
    import sympy as s
    x,y = s.symbols('x y')
    u,v = s.symbols('u v')
    G=s.Matrix([x+x*y,y+x*x])
    F=s.Matrix([u*u+u*v,v*v*v+u])
    composed=s.Matrix([z.subs({u:G[0],v:G[1]},simultaneous=True) for z in F])
    Dg=G.jacobian([x,y]); Df=F.jacobian([u,v])
    Hg=[s.hessian(G[i],[x,y]) for i in range(2)]
    Hf=[s.hessian(F[i],[u,v]) for i in range(2)]
    Hfg=[s.hessian(composed[i],[x,y]) for i in range(2)]
    failures_without_middle=0
    for case in range(24):
        P=oblique_projectors(2)
        Qm=oblique_projectors(2)
        S=oblique_projectors(2)
        xx=s.Matrix([s.Rational(rng.randrange(-3,4)),s.Rational(rng.randrange(-3,4))])
        h=sym_vec(random_vec(2)); k=sym_vec(random_vec(2))
        values={x:xx[0],y:xx[1]}
        gxx=s.Matrix([v.subs(values) for v in G])
        fvals={u:gxx[0],v:gxx[1]}
        Dgv=Dg.subs(values); Dfv=Df.subs(fvals)
        Hgvals=[z.subs(values) for z in Hg]
        Hfvals=[z.subs(fvals) for z in Hf]
        Hfgvals=[z.subs(values) for z in Hfg]
        for alpha,beta,gamma in itertools.product(range(2),repeat=3):
            hh=s.Matrix(P[alpha])*h; kk=s.Matrix(P[beta])*k
            left=s.Matrix(S[gamma])*s.Matrix([(hh.T*H*kk)[0] for H in Hfgvals])
            rhs=s.zeros(2,1)
            # Partition {{1},{2}}: intermediate packets for two DG images.
            for lam,mu in itertools.product(range(2),repeat=2):
                a=s.Matrix(Qm[lam])*Dgv*hh
                b=s.Matrix(Qm[mu])*Dgv*kk
                rhs += s.Matrix(S[gamma])*s.Matrix([(a.T*H*b)[0] for H in Hfvals])
            # Partition {{1,2}}: a single D²G packet.
            D2g=s.Matrix([(hh.T*H*kk)[0] for H in Hgvals])
            for lam in range(2):
                rhs += s.Matrix(S[gamma])*Dfv*s.Matrix(Qm[lam])*D2g
            check(left==rhs,"decorated_second_chain_rule")
            # A false shortcut keeps only the lambda=0 intermediate label.
            wrong=s.Matrix(S[gamma])*Dfv*s.Matrix(Qm[0])*D2g
            a=s.Matrix(Qm[0])*Dgv*hh; b=s.Matrix(Qm[0])*Dgv*kk
            wrong+=s.Matrix(S[gamma])*s.Matrix([(a.T*H*b)[0] for H in Hfvals])
            if left!=wrong:
                failures_without_middle+=1
    check(failures_without_middle>0,"reject_missing_intermediate_packet_terms")
    controls['missing_intermediate_label_counterexamples']=failures_without_middle


def check_negative_controls():
    P=[[[Q(1),Q(-2)],[Q(0),Q(0)]],[[Q(0),Q(2)],[Q(0),Q(1)]]]
    S=[eye(2)[0:1]+[[Q(0),Q(0)]],[[Q(0),Q(0)],eye(2)[1]]]
    T={(0,0,0):Q(0),(0,0,1):Q(1),(0,1,0):Q(2),(0,1,1):Q(0),
       (1,0,0):Q(1),(1,0,1):Q(-1),(1,1,0):Q(0),(1,1,1):Q(2)}
    h=[[Q(2),Q(3)],[Q(1),Q(4)]]
    full=tensor_eval(T,2,2,2,h)
    diag=vsum([vsum([extended_jet(T,2,2,2,P,S[g],(i,i),h)
                     for i in range(2)],2) for g in range(2)],2)
    check(diag!=full,"reject_only_diagonal_packets")
    no_completion=vsum([vsum([extended_jet(T,2,2,2,P[:1],S[g],(0,0),h)],2)
                         for g in range(2)],2)
    check(no_completion!=full,"reject_missing_completeness")
    # Over F_2: three identical identity projectors each idempotent; sum is I,
    # but they are not pairwise annihilating. Coordinates (1,0,0) are legal
    # range values yet analysis(synthesis(1,0,0))=(1,1,1), not (1,0,0).
    coords=(1,0,0)
    synthesis=sum(coords)%2
    analysis=tuple(synthesis for _ in coords)
    check((3%2)==1 and analysis!=coords,
          "reject_idempotent_complete_but_nonorthogonal_coordinate_inverse")
    controls['diagonal_only_difference']=[str(x-y) for x,y in zip(full,diag)]
    controls['incomplete_difference']=[str(x-y) for x,y in zip(full,no_completion)]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    try:
        check_multilinear()
        check_general_resolutions()
        check_norm_bounds()
        check_touchard()
        check_second_chain()
        check_negative_controls()
    except Exception as e:
        print(f'FAIL {type(e).__name__}: {e}',file=sys.stderr)
        raise
    result={
      'schema':'paper-iii-section17-exact-tests/1',
      'status':'PASS',
      'test_source':'tests/section17/exact_section17.py',
      'seed':seed,'checks_by_family':dict(sorted(checks.items())),
      'total_assertions':sum(checks.values()),
      'negative_controls':controls,
      'scope':('Exact finite-dimensional rational tensor evaluations, oblique '
               'complete projector families, ambient infinity norm certificates, '
               'symbolic second-derivative chain rule, integer Stirling/Touchard '
               'counts, and deliberately false control rejection. These do not '
               'establish a general mathematical theorem or a Lean kernel replay.'),
      'symbolic_backend':'sympy',
      'rational_backend':'fractions.Fraction',
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2),encoding='utf8')
    print(json.dumps({'status':'PASS','assertions':result['total_assertions'],
                      'families':result['checks_by_family'],
                      'negative':controls},indent=2))

if __name__=='__main__': main()
