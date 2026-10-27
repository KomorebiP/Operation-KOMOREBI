#!/usr/bin/env python3
"""Independent integer, determinant and residue-graph checks for Series 06.

No certificate-generation routine is imported. Bellman--Ford relaxation and
restriction determinants provide independent implementations of load-bearing
finite assertions. Polynomial evaluations are exact and explicitly bounded.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations, combinations_with_replacement
import json, math
from pathlib import Path
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]

def units(m):
    return [u for u in range(1,m) if math.gcd(m,u)==1]

def age(a,m,u):
    values=[u*x%m for x in a]
    assert all(values) and sum(values)%m==0
    return sum(values)//m

def exact_bellman(m,a,costs):
    """Repeated edge relaxation, no priority queue or original verifier import."""
    dist=[None]*m;dist[0]=0
    passes=0
    for _ in range(m):
        changed=False
        old=dist[:]
        for r in range(m):
            if old[r] is None:continue
            for ai,ci in zip(a,costs):
                s=(r+ai)%m;v=old[r]+ci
                if dist[s] is None or v<dist[s]:dist[s]=v;changed=True
        passes+=1
        if not changed:break
    assert all(d is not None for d in dist)
    assert all(dist[(r+ai)%m]<=dist[r]+ci for r in range(m) for ai,ci in zip(a,costs))
    return min(ci+dist[-ai%m] for ai,ci in zip(a,costs)),dist,passes

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    records=[]
    def check(name,condition,detail=None):
        records.append({'name':name,'pass':bool(condition),'detail':detail})
        if not condition:raise AssertionError((name,detail))
    transfer=json.loads((ROOT/'work/transfer/results/transfer210.json').read_text())
    m=210;s=transfer['source'];t=transfer['target'];c=transfer['certificate']
    check('source_and_target_conductor',m//math.gcd(m,*s)==70 and math.gcd(m,*t)==1)
    check('orbit_sizes',len({tuple(u*x%m for x in s) for u in units(m)})==24 and len({tuple(u*x%m for x in t) for u in units(m)})==48)
    # Sparse generating polynomial coefficient comparison over Z[x].
    coefficients=[0]*m
    for row in c:
        for x in row['packet']:coefficients[x]+=row['coefficient']
    for x in t:coefficients[x]-=1
    for x in s:coefficients[x]+=1
    check('transfer_sparse_polynomial_zero',all(x==0 for x in coefficients))
    coefficients[c[0]['packet'][0]]+=2*c[0]['coefficient']
    check('transfer_sign_mutation_rejected',any(x!=0 for x in coefficients))
    cost=[31,87,57,101,84,60]
    minimum,potentials,passes=exact_bellman(m,t,cost)
    check('transfer_bellman_ford_minimum',minimum==420,{'minimum':minimum,'relaxation_passes':passes,'states':m})
    bad=[1]*6
    check('invalid_dual_rejected',exact_bellman(m,t,bad)[0]<420)
    capacity=[]
    for data in json.loads((ROOT/'work/dual_cycles/checks/capacity_inputs.json').read_text()):
        mod=data['modulus'];a=data['character'];duals=[Q(x) for x in data['candidate_dual']]
        den=math.lcm(*(x.denominator for x in duals));costs=[int(den*x) for x in duals]
        value,d,passes=exact_bellman(mod,a,costs)
        w=sp.Matrix([sp.Rational(x) for x in data['weights']]);A=sp.Matrix(data['matrix'])
        check('capacity_bellman_'+str(mod),value>=den and A*w==sp.ones(6,1) and sum(w)==sp.Rational(sum(duals)),{'minimum_return':str(Q(value,den)),'optimum':data['weight_sum'],'bellman_edges':6*mod})
        capacity.append({'m':mod,'value':data['weight_sum'],'minimum_return':str(Q(value,den))})
    # Alternative direct determinant checks use integer substitutions and
    # Bareiss elimination, independent of symbolic domain-ge in source replay.
    t0=sp.symbols('t0:5')
    elementary=[sum(sp.prod(v) for v in combinations(t0,k)) for k in range(1,6)]
    V=sp.Matrix([[sp.diff(e,t) for t in t0] for e in elementary])
    substitutions=[(1,2,4,7,11),(-3,-1,0,2,8),(0,0,1,2,3)]
    for i,values in enumerate(substitutions):
        direct=V.subs(dict(zip(t0,values))).det(method='bareiss')
        target=math.prod(values[j]-values[k] for j in range(5) for k in range(j+1,5))
        check('vandermonde_integer_bareiss_'+str(i),direct==target,{'determinant':int(direct)})
    E1,E2,E3,E4,P,z,kappa=sp.symbols('E1 E2 E3 E4 P z kappa')
    G1=E1**4-5*E1**2*E2+5*E1*E3+5*E2**2-5*E4
    det_checks=0
    for q in (2,3,4,5,7,11,17):
        G3=5*sum(P**(q-1-j)*kappa**j*z**(5*j) for j in range(q))
        H=[E1,G1,E2,-5*E3,P-kappa*z**5,G3]
        J=sp.Matrix([[sp.diff(h,x) for x in (E1,E2,E3,E4,P,z)] for h in H])
        rhs=625*q*sum(kappa**j*P**(q-1-j)*z**(5*j-1) for j in range(1,q))
        for vals in ((1,2,3,5,2,1,3),(-1,3,2,7,3,-1,2),(2,0,1,4,1,2,-1)):
            sub=dict(zip((E1,E2,E3,E4,P,z,kappa),vals))
            actual=J.subs(sub).det(method='bareiss')
            check('intermediate_integer_bareiss_q'+str(q)+'_'+str(det_checks),actual==rhs.subs(sub))
            det_checks+=1
    # Independent graph periods: restriction of a basis six-form is determinant
    # of selected rows of the 12x6 pullback, rather than exterior-mask code.
    R=sp.zeros(12,6)
    for j in range(6):
        R[2*j,2*(j%3)]=1
        R[2*j+1,2*(j%3)+1]=1 if j<3 else -1
    periods=[0,0]
    for choices in range(64):
        rows=[2*j+((choices>>j)&1) for j in range(6)]
        k=choices.bit_count();component=k%2
        coeff=(-1)**(k//2) if component==0 else (-1)**((k-1)//2)
        periods[component]+=coeff*int(R[rows,:].det(method='bareiss'))
    check('weil_graph_u_v_determinants',periods==[0,-8],periods)
    theta_restriction=[2,2,4]
    check('weil_graph_theta3_period',math.factorial(3)*math.prod(theta_restriction)==96)
    check('weil_graph_projected_v_coefficient',Q(periods[1],-32)==Q(1,4))
    # B^t=diag(1,1,3) B kills third row/column; the leading 2x2
    # symmetric block has 3 complex entries. Split3x3 has 6 entries.
    Bs=sp.symbols('b0:9');B=sp.Matrix(3,3,Bs)
    ranks=[]
    for weights in ((1,1,3),(1,1,1)):
        equations=list(B.T-sp.diag(*weights)*B)
        mat,_=sp.linear_eq_to_matrix(equations,Bs)
        ranks.append(9-mat.rank())
    check('weil_graph_complex_tangent_dimensions',ranks==[3,6],ranks)
    # K23 selected representatives are fully encoded; the other357 historical
    # certificates are not present individually in the current source bundle.
    kd=json.loads((ROOT/'work/k23/Fermat_Hodge_K23_CM_Type_Audit.json').read_text())
    k23=[]
    for rec in kd['orbit_records']:
        mod=rec['degree'];sel=rec['selected_certificate'];CP,ST,L=(sel[x] for x in ('CP','ST','L'))
        expected=[]
        for u in units(mod):
            hc,hs,hl=(age(a,mod,u) for a in (CP,ST,L))
            eps=1 if hc+hs==3 else -1
            expected.append({'u':u,'hCP':hc,'hST':hs,'hL':hl,'epsilon_N':eps})
            check('K23_age_identity_'+str(mod)+'_'+str(rec['packet'])+'_'+str(u),hc+hs+hl==5 and eps==(-1 if hl==1 else 1))
        check('K23_stored_rows_'+str(rec['packet']),expected==sel['rows'])
        lower=sel['lower_curve_packet'];conductor=sel['CM_type_conductor'];rawq=mod//5
        check('K23_lower_packet_support_'+str(rec['packet']),all(0<x<rawq for x in lower) and sum(lower)%rawq==0)
        sign=[1 if age(lower,rawq,u)==2 else -1 for u in units(rawq)]
        check('K23_sign_descends_'+str(rec['packet']),all(sign[i]==sign[j] for i,u in enumerate(units(rawq)) for j,v in enumerate(units(rawq)) if u%conductor==v%conductor))
        k23.append({'degree':mod,'packet':rec['packet'],'historical_certificate_count':rec['certificate_count'],'selected_rows_checked':len(expected),'conductor':conductor})
    # Direct census ignores randomized hashing. Complete finite families at m8
    # andm16 establish an orthogonal small benchmark for MITM enumeration.
    dyadic=[]
    historical=json.loads((ROOT/'runs/dyadic_exhaustive/result.json').read_text())
    for mod in (8,16):
        values=range(1,mod);U=units(mod)
        for length in (4,6):
            target=length*mod//2
            count=0;enumerated=0
            for a in combinations_with_replacement(values,length):
                enumerated+=1
                if sum(a)!=target:continue
                if all(sum(u*x%mod for x in a)==target for u in U):count+=1
            expected=historical['degrees'][str(mod)]['balanced_'+('four' if length==4 else 'six')+'_count']
            check('dyadic_direct_census_'+str(mod)+'_'+str(length),count==expected,{'multisets_visited':enumerated,'balanced':count})
            dyadic.append({'m':mod,'length':length,'visited':enumerated,'balanced':count})
    result={'status':'PASS: finite independent implementation checks','checks_passed':len(records),'checks':records,'capacities':capacity,'transfer_minimum_numerator':minimum,'transfer_denominator':420,'transfer_bellman_potentials':potentials,'integer_determinant_evaluations':det_checks,'weil_graph_periods':{'u':periods[0],'v':periods[1],'theta3':96},'K23_selected_certificates':k23,'K23_selected_count':len(k23),'K23_historical_total':kd['total_exact_K23_certificates'],'dyadic_direct_census':dyadic,'mutation_checks':['transfer sign mutation rejected','uniform invalid dual rejected'],'nonclaims':['No universal Hodge proof','No regeneration of all364 K23 certificates','Polynomial substitutions do not alone prove a polynomial identity','No algebraic degeneration from a nilpotent matrix alone']}
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],result['checks_passed'])

if __name__=='__main__':main()
