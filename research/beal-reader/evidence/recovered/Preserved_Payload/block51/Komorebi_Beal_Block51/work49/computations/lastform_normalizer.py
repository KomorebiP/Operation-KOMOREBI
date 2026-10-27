#!/usr/bin/env python3
"""Exact PSL2(F49)/nonsplit-normalizer branch-cycle calculation.

This constructs a finite triangle quotient and its degree1176 coset action.
It does not identify that action with an arithmetic hypergeometric cover.
"""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path

Q = 49
ADD = [[((x % 7 + y % 7) % 7) + 7*((x//7+y//7) % 7)
        for y in range(Q)] for x in range(Q)]
NEG = [((-x % 7) % 7) + 7*((- (x//7)) % 7) for x in range(Q)]
MUL = [[((x%7*(y%7)+5*(x//7)*(y//7)) % 7)
        +7*((x%7*(y//7)+(x//7)*(y%7)) % 7)
        for y in range(Q)] for x in range(Q)]
INV = [0] + [next(y for y in range(1,Q) if MUL[x][y] == 1)
             for x in range(1,Q)]


def norm(m):
    return min(m, tuple(NEG[x] for x in m))


ID = norm((1, 0, 0, 1))


def mult(m, n):
    a,b,c,d=m; e,f,g,h=n
    return norm((ADD[MUL[a][e]][MUL[b][g]], ADD[MUL[a][f]][MUL[b][h]],
                 ADD[MUL[c][e]][MUL[d][g]], ADD[MUL[c][f]][MUL[d][h]]))


def inverse(m):
    a,b,c,d=m
    return norm((d,NEG[b],NEG[c],a))


def power(m, n):
    ans=ID
    while n:
        if n & 1: ans=mult(ans,m)
        m=mult(m,m); n//=2
    return ans


def cycles(perm):
    remaining=set(range(len(perm))); lengths=[]
    while remaining:
        start=min(remaining); x=start; n=0
        while True:
            assert x in remaining
            remaining.remove(x); n+=1; x=perm[x]
            if x == start: break
        lengths.append(n)
    return {str(n): lengths.count(n) for n in sorted(set(lengths))}


def digest(obj):
    return hashlib.sha256(json.dumps(obj,separators=(',',':')).encode()).hexdigest()


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    # Complete SL2 determinant-one enumeration, then quotient by scalar +/-I.
    G=set()
    for a in range(1,Q):
        for b in range(Q):
            for c in range(Q):
                d=MUL[INV[a]][ADD[1][MUL[b][c]]]
                G.add(norm((a,b,c,d)))
    for b in range(1,Q):
        for d in range(Q):
            G.add(norm((0,b,NEG[INV[b]],d)))
    assert len(G)==58800
    ordered=sorted(G)
    squares={MUL[x][x] for x in range(1,Q)}
    delta=next(x for x in range(1,Q) if x not in squares)
    # Nonsplit norm-one torus, divided by +/-I, has order25.
    torus={norm((x,MUL[delta][y],y,x)) for x in range(Q) for y in range(Q)
           if ADD[MUL[x][x]][NEG[MUL[delta][MUL[y][y]]]]==1}
    assert len(torus)==25 and torus <= G
    i=next(x for x in range(1,Q) if MUL[x][x]==NEG[1])
    reflection=norm((i,0,0,NEG[i]))
    N=torus | {mult(reflection,t) for t in torus}
    assert len(N)==50 and N <= G
    assert all(mult(x,y) in N for x in N for y in N)
    assert all(mult(mult(reflection,t),inverse(reflection))==inverse(t) for t in torus)
    assert power(reflection,2)==ID and reflection != ID
    # Order-three element and an order-five element in the nonsplit torus.
    a=norm((0,NEG[1],1,NEG[1]))
    b0=next(t for t in sorted(torus) if t != ID and power(t,5)==ID)
    assert power(a,3)==ID and a != ID
    # Find a conjugate giving the exact projective branch-cycle triple.
    for g in ordered:
        b=mult(mult(g,b0),inverse(g))
        ab=mult(a,b)
        if ab != ID and power(ab,7)==ID:
            break
    else:
        raise AssertionError('No (3,5,7) triple found')
    c=inverse(ab)
    assert power(b,5)==ID and b != ID
    assert power(c,7)==ID and mult(mult(a,b),c)==ID
    # Exhaustive generation certificate, not an appeal to subgroup classification.
    generated={ID}; queue=deque([ID])
    while queue:
        x=queue.popleft()
        for g in (a,b):
            y=mult(x,g)
            if y not in generated:
                generated.add(y); queue.append(y)
    assert generated==G
    # Right cosets gN with left action of G.
    lookup={}; reps=[]
    for g in ordered:
        if g in lookup: continue
        j=len(reps); reps.append(g)
        coset={mult(g,n) for n in N}
        assert len(coset)==50 and not any(x in lookup for x in coset)
        for x in coset: lookup[x]=j
    assert len(lookup)==58800 and len(reps)==1176
    perms=[[lookup[mult(g,r)] for r in reps] for g in (a,b,c)]
    assert all(sorted(p)==list(range(1176)) for p in perms)
    assert all(perms[0][perms[1][perms[2][j]]]==j for j in range(1176))
    cyc=[cycles(p) for p in perms]
    assert cyc==[{'3':392},{'1':1,'5':235},{'7':168}]
    defects=[1176-sum(x.values()) for x in cyc]
    two_g_minus_two=-2*1176+sum(defects)
    assert defects==[784,940,1008] and two_g_minus_two==380
    # Coset stabilizer is N by construction; independent class-count check at5.
    centralizer=[x for x in G if mult(x,b0)==mult(b0,x)]
    conjugacy={mult(mult(g,b0),inverse(g)) for g in G}
    intersection=sorted(conjugacy & N)
    assert len(centralizer)==25 and len(intersection)==2
    assert len(centralizer)*len(intersection)//len(N)==1
    out={'status':'exact_finite_triangle_coset_action_verified',
         'field':'F7[s]/(s²−5), encoding a+7b for a+bs',
         'matrix_convention':'determinant1 matrices modulo +/-I, lexicographic representative',
         'group_order':len(G),'nonsplit_parameter':delta,'torus_order':len(torus),
         'normalizer_order':len(N),'degree':len(reps),'triangle_generators':[a,b,c],
         'generated_group_order':len(generated),'coset_cycle_counts':cyc,
         'ramification_indices':defects,'genus':1+two_g_minus_two//2,
         'order5_centralizer':len(centralizer),'order5_class_intersection_with_N':len(intersection),
         'group_sha256':digest(ordered),'normalizer_elements':sorted(N),
         'coset_representatives_sha256':digest(reps),'permutations':perms,
         'non_claims':['No identification with an arithmetic hypergeometric cover',
                       'No field-of-definition or arithmetic twist descent established',
                       'No rational or K-rational point computation',
                       'No exclusion of the surviving Hilbert form'],
         'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    args.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','group_order','normalizer_order','degree','coset_cycle_counts','genus')}))


if __name__=='__main__': main()
