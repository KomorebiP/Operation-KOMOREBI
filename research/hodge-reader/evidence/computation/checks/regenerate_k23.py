#!/usr/bin/env python3
"""Independently regenerate364 exact K23 finite certificates.

Input uses only seven representative packets and historical counts as comparison
targets. No archived boolean flag is trusted. All unit conjugates, pair/triple
partitions, Hodge ages, minimal sign conductors and half-plane translates are
recomputed. This constructs finite character data, not a Chow correspondence.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import argparse,json,math
import sympy as sp

ROOT=Path(__file__).resolve().parents[1]
def units(m):return [u for u in range(1,m) if math.gcd(u,m)==1]
def age(a,m,u):
    v=[u*x%m for x in a]
    assert all(v) and sum(v)%m==0
    return sum(v)//m
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    inp=json.loads((ROOT/'work/k23/Fermat_Hodge_K23_CM_Type_Audit.json').read_text())
    records=[];orbit_counts=[];distribution=Counter();total_rows=0
    x=sp.Symbol('x')
    for orbit in inp['orbit_records']:
        m=orbit['degree'];q=m//5;U=units(m);V=units(q);seen=set();count=0
        assert all(age(orbit['packet'],m,u)==3 for u in U)
        for g in U:
            A=tuple(sorted(g*t%m for t in orbit['packet']))
            nz=[t for t in A if t%5];zz=[t for t in A if t%5==0]
            assert len(nz)==5 and len(zz)==1
            e=zz[0]//5
            for P in combinations(nz,2):
                if sum(P)%5:continue
                T=list(nz)
                for t in P:T.remove(t)
                assert sum(T)%5==0
                c=sum(P)//5%q;d=sum(T)//5%q
                if not(c and d):continue
                key=(A,P,tuple(T))
                assert key not in seen;seen.add(key)
                CP=tuple(sorted((*P,m-5*c)));ST=tuple(sorted((*T,m-5*d)));L=tuple(sorted((5*c,5*d,5*e)))
                assert Counter((*A,5*c,m-5*c,5*d,m-5*d))==Counter((*CP,*ST,*L))
                lower=(c,d,e);assert sum(lower)%q==0
                rows=[]
                for u in U:
                    hc,hs,hl=(age(B,m,u) for B in (CP,ST,L))
                    assert hc in (1,2) and hs in (1,2,3) and hl in (1,2)
                    assert hc+hs+hl==5
                    eps=1 if hc+hs==3 else -1
                    assert eps==(-1 if hl==1 else 1)
                    rows.append([u,hc,hs,hl,eps])
                signs={u:(-1 if age(lower,q,u)==1 else 1) for u in V}
                conductors=[]
                for D in sp.divisors(q):
                    table={};valid=True
                    for u,sgn in signs.items():
                        r=u%D
                        if r in table and table[r]!=sgn:valid=False;break
                        table[r]=sgn
                    if valid:conductors.append(D)
                conductor=min(conductors)
                assert 1<conductor< m
                matches=[]
                for translate in units(conductor):
                    for orientation in (1,-1):
                        if all(signs[u]==orientation*(1 if (translate*u)%conductor<conductor/2 else -1) for u in V):
                            matches.append([translate,orientation])
                assert matches
                phi=sp.Poly(sp.cyclotomic_poly(q,x),x,domain=sp.QQ)
                selector=sp.Poly(sp.prod(1-x**t for t in lower),x,domain=sp.QQ)
                conjugate=sp.Poly(sp.prod(1-x**((-t)%q) for t in lower),x,domain=sp.QQ)
                assert (selector+conjugate).rem(phi).is_zero
                assert not selector.rem(phi).is_zero
                distribution[(m,conductor)]+=1;count+=1;total_rows+=len(rows)
                records.append({'degree':m,'unit_conjugate':g,'A':list(A),'P':list(P),'T':T,'CP':list(CP),'ST':list(ST),'L':list(L),'lower_curve_packet':list(lower),'CM_type_conductor':int(conductor),'half_plane_matches':matches,'rows_u_hCP_hST_hL_epsilonN':rows,'imaginary_selector_nonzero_and_conjugate_negative':True})
        assert count==orbit['certificate_count']
        orbit_counts.append({'degree':m,'packet':orbit['packet'],'regenerated_count':count})
    actual={f'm={m},d={d}':n for (m,d),n in sorted(distribution.items())}
    assert actual==inp['conductor_distribution']
    assert len(records)==inp['total_exact_K23_certificates']==364
    result={'status':'PASS: independently regenerated finite K23 certificates','regenerated_certificates':len(records),'unit_age_rows_checked':total_rows,'orbit_counts':orbit_counts,'conductor_distribution':actual,'certificates':records,'nonclaims':['No universal K23 classification from these seven representatives','No algebraic rank-one Chow map constructed','No inference that matching CM types supplies an algebraic correspondence','No verification of completeness of historical balanced census throughdegree100']}
    a.out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(records),'certificates;',total_rows,'exact age rows')
if __name__=='__main__':main()
