#!/usr/bin/env python3
"""Block58 exact good/bad Frobenius closure. Standard library, Python >=3.10.
Only q=41,59 and the declared twelve conductor places are certified.
The geometric identifications are explicit inherited hypotheses.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
from inherited_frobenius_counts import tables,count1,count2,polynomial,twisted,character
from inherited_reciprocity_checks import places,rref,kernel

QS=[41,59]
U=[97,197,293,491,587,883,1373,1471,1567,1667]
ELEMENTS=[('phi',(0,1)),('2',(2,0)),('3',(3,0)),('sqrt5',(-1,2)),('7',(7,0)),
 ('pi11',(3,1)),('bar_pi11',(4,-1)),('pi19',(4,1)),('bar_pi19',(5,-1)),
 ('pi31',(5,2)),('bar_pi31',(7,-2)),('pi41',(6,1)),('bar_pi41',(7,-1)),
 ('pi59',(7,2)),('bar_pi59',(9,-2))]
OLD_A=[3,0,0,5,2,5,0,0,0,0,1,0]
OLD_B=[5,0,2,0,0,0,0,0,2,5,1,0]

def check(ok,msg):
    if not ok: raise ValueError(msg)

def det(a):
    if not a:return 1
    b=[list(r) for r in a];n=len(b);prev=1;sign=1
    check(all(len(r)==n for r in b),'Nonsquare matrix')
    for k in range(n-1):
        p=next((i for i in range(k,n) if b[i][k]),None)
        if p is None:return 0
        if p!=k:b[p],b[k]=b[k],b[p];sign=-sign
        pivot=b[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                num=pivot*b[i][j]-b[i][k]*b[k][j]
                check(num%prev==0,'Inexact determinant division');b[i][j]=num//prev
            b[i][k]=0
        prev=pivot
    return sign*b[-1][-1]

def finite_frobenius(q):
    check(q in QS and all(q%d for d in range(2,math.isqrt(q)+1)),'Undeclared or composite prime')
    f=1 if q%5 in (1,4) else 2;check(f==1,'This certificate uses split primes')
    nu=(1 if q%5==1 else -1)*character(-3,q)
    tab=tables(q);seventh={pow(c,7,q) for c in range(1,q)}
    good={(a,b) for a in range(q) for b in range(q) if (pow(a,3,q)+pow(b,5,q))%q in seventh}
    pows=[(pow(u,5,q),pow(u,3,q)) for u in range(1,q)]
    unseen=set(good);rows=[]
    target=[q*q,-2*q*(q+1),(q+1)**2+2*q,-2*(q+1),1]
    while unseen:
        a,b=min(unseen);orbit={(a*u5%q,b*u3%q) for u5,u3 in pows}
        members=sorted(orbit & good)
        check(set(members)<=unseen,'Orbit not a partition');unseen.difference_update(members)
        n1=count1(a,b,q,tab);n2=count2(a,b,q,tab)
        P=polynomial(q,n1,n2);T=twisted(q,P,nu,1)
        match={str(m):all((c-d)%m==0 for c,d in zip(T,target)) for m in (7,49,343)}
        check(sum(T)>0,'Nonpositive order')
        rows.append({'representative':[a,b],'admissible_pairs':[list(z) for z in members],
          'N1':n1,'N2':n2,'Pq_ascending':P,'twisted_polynomial':T,'matches':match})
    counts={str(m):sum(len(r['admissible_pairs']) for r in rows if r['matches'][str(m)]) for m in (7,49,343)}
    check(counts==({'7':120,'49':0,'343':0} if q==41 else {'7':116,'49':0,'343':0}),'Unexpected modulus loci')
    trace_surv=sorted({-r['twisted_polynomial'][3] for r in rows if r['matches']['7']})
    check(trace_surv==([0,7,14] if q==41 else [-6,1]),'Unexpected residual traces')
    check(all((t-2*(q+1))%49 for t in trace_surv),'Depth-two trace survivor')
    return {'q':q,'f':f,'nu':nu,'pairs':len(good),'degree_one_counts':len(rows),'degree_two_counts':len(rows),
      'target_polynomial_ascending':target,'matches_by_pairs':counts,'residual_twisted_traces':trace_surv,
      'required_trace_mod49':2*(q+1)%49,'rows':rows}

def reciprocity():
    records=[]
    for q in U:
        for lab,F in places(q):
            h,z,_=F.logs();check(h>=2,'Conductor place not high')
            co=(F.Q-1)//7**h;table={F.power(z,j):j for j in range(7**h)}
            logs=[table[F.power(F.elm(*ab),co)]%7 for name,ab in ELEMENTS]
            records.append({'label':lab,'q':q,'phi_root':F.phi_root,'norm':F.Q,'h':h,'logs_mod7':logs})
    check(len(records)==12,'Conductor place count')
    M=[[r['logs_mod7'][i] for r in records] for i in range(len(ELEMENTS))]
    check(len(rref(M[:11])[1])==10,'Predecessor row rank changed')
    for v in (OLD_A,OLD_B):check(all(sum(a*b for a,b in zip(row,v))%7==0 for row in M[:11]),'Old null vector invalid')
    evals=[[sum(a*b for a,b in zip(M[i],v))%7 for v in (OLD_A,OLD_B)] for i in (11,13)]
    check(evals==[[3,4],[0,4]] and det(evals)%7==5,'Two new rows do not kill the old kernel')
    pivrows=rref([list(row) for row in zip(*M)])[1]
    check(len(pivrows)==12 and not kernel(M),'New full-column rank failed')
    minor=[M[i] for i in pivrows];D=det(minor);check(D%7!=0,'Rank determinant vanished')
    return {'universe':U,'row_elements':[{'name':n,'phi_coefficients':list(ab)} for n,ab in ELEMENTS],
       'places':records,'matrix_mod7':M,'old_rank':10,'old_kernel_basis':[OLD_A,OLD_B],
       'new_rows_on_old_kernel':evals,'two_by_two_determinant':det(evals),'rank':12,'kernel_dimension':0,
       'rank_minor':{'row_indices':pivrows,'integer_determinant':D,'determinant_mod7':D%7},
       'norms_new_generators':{name:a*a+a*b-b*b for name,(a,b) in ELEMENTS[11:]},
       'does_not_use_kummer_filter':True}

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',required=True,type=Path);a=ap.parse_args()
    out={'schema':'komorebi.beal.block58.primary.v1','status':'PASS_DECLARED_FINITE_ASSERTIONS',
       'finite_frobenius':[finite_frobenius(q) for q in QS],'reciprocity':reciprocity(),
       'nonclaims':['No upstream geometry verification','No universal high-prime bound','No Beal proof']}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':out['status'],'pairs':sum(x['pairs'] for x in out['finite_frobenius']),
       'point_count_orbits':sum(x['degree_two_counts'] for x in out['finite_frobenius']),
       'new_reciprocity_rank':out['reciprocity']['rank'],'rank_minor':out['reciprocity']['rank_minor']}))
if __name__=='__main__':main()
