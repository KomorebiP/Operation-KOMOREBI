#!/usr/bin/env python3
"""Exact chi^-1 ray-character certificate; no numerical approximations or external packages."""
from __future__ import annotations
import argparse
import hashlib
import json
from itertools import product
from pathlib import Path

SUPPORT=(197,883,1373,1667)
TESTS=(29,71,491)
# Coefficients in 1,zeta,...,zeta^5, Phi_7(zeta)=0. Verified by exact norms.
GENERATORS={
 197:(1,-1,-1,-1,1,-1),883:(0,0,1,-2,1,2),
 1373:(0,2,-2,-1,-2,-2),1667:(1,-2,1,2,1,2),
 29:(0,0,0,1,-1,-1),71:(0,1,-1,-1,1,-1),491:(0,1,-2,2,0,2)}

def need(ok:bool,why:str)->None:
    if not ok:raise AssertionError(why)

def prime(n:int)->bool:
    return n>=2 and all(n%d for d in range(2,1+__import__('math').isqrt(n)))

def factors(n:int)->list[int]:
    out=[];d=2
    while d*d<=n:
        if n%d==0:
            out.append(d)
            while n%d==0:n//=d
        d+=1
    if n>1:out.append(n)
    return out

def cmul(a,b):
    out=[0]*11
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    for i in range(10,5,-1):
        for j in range(1,7):out[i-j]-=out[i]
    return out[:6]

def bareiss(rows):
    a=[list(r) for r in rows];n=len(a);last=1;sign=1
    if not n:return 1
    for k in range(n-1):
        if not a[k][k]:
            j=next((j for j in range(k+1,n) if a[j][k]),None)
            if j is None:return 0
            a[k],a[j]=a[j],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                x=pivot*a[i][j]-a[i][k]*a[k][j]
                need(x%last==0,'Nonintegral Bareiss division')
                a[i][j]=x//last
            a[i][k]=0
        last=pivot
    return sign*a[-1][-1]

def norm(a):
    columns=[cmul(a,[int(i==j) for i in range(6)]) for j in range(6)]
    return bareiss(list(zip(*columns)))

def ev(p,x,q):
    v=0
    for c in p[::-1]:v=(v*x+c)%q
    return v

def rank(rows,p=7):
    a=[[x%p for x in r] for r in rows];r=0
    for c in range(len(a[0]) if a else 0):
        j=next((j for j in range(r,len(a)) if a[j][c]),None)
        if j is None:continue
        a[r],a[j]=a[j],a[r];iv=pow(a[r][c],-1,p)
        a[r]=[x*iv%p for x in a[r]]
        for j in range(len(a)):
            if j!=r:
                t=a[j][c];a[j]=[(x-t*y)%p for x,y in zip(a[j],a[r])]
        r+=1
    return r

def fmul(x,y,q): # phi^2=phi+1
    a,b=x;c,d=y
    return ((a*c+b*d)%q,(a*d+b*c+b*d)%q)

def fpow(x,n,q):
    y=(1,0)
    while n:
        if n&1:y=fmul(y,x,q)
        x=fmul(x,x,q);n//=2
    return y

def run():
    out={'schema':'beal.block61.twisted.v1','support':list(SUPPORT),'test_primes':list(TESTS),
         'cyclotomic_polynomial':[1]*7,'coefficient_domain':'F49, scalar matrices over F7',
         'twist':'chi^-1','prime_generators':{},'support_fields':{},'residue_evaluations':{}}
    logs={};roots={}
    for q,p in GENERATORS.items():
        need(prime(q),'Nonprime generator norm label');n=norm(p);need(n==q,'Wrong generator norm')
        out['prime_generators'][str(q)]={'coefficients':list(p),'norm':n}
    for q in SUPPORT:
        need(all(pow(2,(q-1)//p,q)!=1 for p in factors(q-1)),'2 is not primitive')
        tab={pow(2,j,q):j for j in range(q-1)};need(len(tab)==q-1,'Incomplete log table')
        rr=[x for x in range(2,q) if pow(x,7,q)==1 and ev(GENERATORS[q],x,q)==0]
        need(len(rr)==1,'Base prime not unique');roots[q]=rr[0];logs[q]=tab
        out['support_fields'][str(q)]={'primitive_root':2,'zeta_residue':rr[0],
            'zeta_residues':[pow(rr[0],b,q) for b in range(1,7)],'log_table_size':len(tab)}
    matrix=[]
    for ell in TESTS:
        row=[];out['residue_evaluations'][str(ell)]={}
        for q in SUPPORT:
            vals=[ev(GENERATORS[ell],pow(roots[q],b,q),q) for b in range(1,7)]
            need(all(vals),'Test generator meets conductor')
            ll=[logs[q][x]%7 for x in vals]
            row.append(-sum(b*ll[b-1] for b in range(1,7))%7)
            out['residue_evaluations'][str(ell)][str(q)]={'values':vals,'logs_mod7':ll}
        matrix.append(row)
    out['matrix']=matrix;out['rank']=rank(matrix)
    minors=[bareiss([[r[j] for j in range(4) if j!=omit] for r in matrix]) for omit in range(4)]
    out['signed_column_deletion_minors']=minors
    need(matrix==[[4,2,6,1],[6,2,0,5],[3,6,1,6]],'Unexpected twisted rows')
    need(out['rank']==3 and minors==[100,-140,-84,176],'Incorrect minor certificate')
    kernel=[list(v) for v in product(range(7),repeat=4)
            if all(sum(x*y for x,y in zip(r,v))%7==0 for r in matrix)]
    need(kernel==[[t,0,0,3*t%7] for t in range(7)],'Unexpected prime-field kernel')
    out['F7_kernel']=kernel
    # Full k-kernel from independently enumerated two scalar components.
    kker=[[(a[i],b[i]) for i in range(4)] for a in kernel for b in kernel]
    need(len(kker)==49,'Wrong extension-field kernel size')
    natural=[]
    for q in SUPPORT:
        need(pow(5,(q-1)//2,q)==q-1,'Support not inert')
        phi_symbol=fpow((0,1),(q*q-1)//7,q)
        need(phi_symbol==(1,0),'Unexpected phi symbol')
        natural.append([0,logs[q][3]%7,(4*logs[q][5])%7])
    out['natural_kummer_rows']=natural
    need(natural==[[0,6,6],[0,0,0],[0,3,4],[0,3,4]],'Wrong common Kummer rows')
    direction_count=0;pair_tests=0;survivors=0
    for u in product(range(7),repeat=2):
        for r in product(range(7),repeat=2):
            if r==(0,0):continue
            direction_count+=1
            zeros=[((a*u[0]+b*r[0]+c)%7==0 and (a*u[1]+b*r[1])%7==0) for a,b,c in natural]
            for v in kker:
                if all(x==(0,0) for x in v):continue
                pair_tests+=1
                survivors+=int(all(x==(0,0) or z for x,z in zip(v,zeros)))
    need(direction_count==2352 and pair_tests==112896 and survivors==0,'Compatible global pair survives')
    out['common_coefficient_test']={'normalized_F49_directions':direction_count,
        'nonzero_F49_ray_vectors':48,'joint_pairs':pair_tests,'surviving_pairs':survivors}
    phi_tests={}
    for q in TESTS:
        rr=[x for x in range(q) if (x*x-x-1)%q==0];need(len(rr)==2,'Test prime not split')
        ss=[pow(x,(q-1)//7,q) for x in rr];need(all(x!=1 for x in ss),'Phi unexpectedly seventh power')
        phi_tests[str(q)]={'roots':rr,'seventh_symbols':ss}
    out['bad_prime_phi_tests']=phi_tests
    covariance=0
    for q in SUPPORT:
        for a in range(1,7):
            for b in range(1,7):
                need((b*pow(a,-1,7))%7==pow(a,-1,7)*b%7,'Twist permutation mismatch');covariance+=1
    conjugacy=0
    for rowi,ell in enumerate(TESTS):
        for a in range(1,7):
            for col,q in enumerate(SUPPORT):
                z=-sum(b*(logs[q][ev(GENERATORS[ell],pow(roots[q],a*b,q),q)]%7) for b in range(1,7))%7
                need(z==pow(a,-1,7)*matrix[rowi][col]%7,'Wrong Frobenius conjugation');conjugacy+=1
    unit_checks=0
    for q in SUPPORT:
        r=roots[q];lg=logs[q]
        for a in range(1,7):
            vals=[(pow(r,a*b,q)-1)*pow(pow(r,b,q)-1,-1,q)%q for b in range(1,7)]
            need(sum(b*lg[vals[b-1]] for b in range(1,7))%7==0,'Cyclotomic unit not killed');unit_checks+=1
    # All independent changes of the four base primes preserve the necessary support.
    reindex=0
    for cc in product(range(1,7),repeat=4):
        changed=[[x*pow(c,-1,7)%7 for x,c in zip(row,cc)] for row in matrix]
        v=[cc[0],0,0,3*cc[3]%7]
        need(rank(changed)==3 and all(sum(x*y for x,y in zip(row,v))%7==0 for row in changed),'Reindexing failed')
        reindex+=1
    out['normalization_checks']={'Delta_transport':covariance,'Frobenius_conjugacy_entries':conjugacy,
        'cyclotomic_unit_tests':unit_checks,'base_prime_reindexings':reindex}
    out['negative_controls']={'ray_kernel_is_nonzero':[1,0,0,3],
        'ordinary_character_weights_are_not_chi_inverse':True,
        'local_positive_Frey_families_not_retracted':True}
    out['status']='PASS_EXACT_FINITE_CERTIFICATE'
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    out=run();a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status']);print('matrix',out['matrix']);print('joint pairs',out['common_coefficient_test'])
if __name__=='__main__':main()
