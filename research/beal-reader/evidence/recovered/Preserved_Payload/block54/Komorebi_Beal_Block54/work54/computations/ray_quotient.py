#!/usr/bin/env python3
"""Certified integer presentation for the tame seven-primary character quotient.
Run with --primes to study a SPECIFIED support, never to infer that C has it.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
from reciprocity_checks import build, require, val7, kernel, rref


def smith(a:list[list[int]]):
    """Smith reduction, with a replayable certificate of unimodular operations."""
    a=[row[:] for row in a];ops=[]
    if not a:return [],[],[]
    m=len(a);n=len(a[0]);k=0
    def rs(i,j):a[i],a[j]=a[j],a[i];ops.append(['rs',i,j])
    def cs(i,j):
        for row in a:row[i],row[j]=row[j],row[i]
        ops.append(['cs',i,j])
    def ra(i,j,c):
        a[i]=[x+c*y for x,y in zip(a[i],a[j])];ops.append(['ra',i,j,c])
    def ca(i,j,c):
        for row in a:row[i]+=c*row[j]
        ops.append(['ca',i,j,c])
    while k<min(m,n):
        cells=[(abs(a[i][j]),i,j) for i in range(k,m) for j in range(k,n) if a[i][j]]
        if not cells:break
        _,i,j=min(cells)
        if i!=k:rs(i,k)
        if j!=k:cs(j,k)
        while True:
            changed=False
            for i in range(k+1,m):
                if a[i][k]:
                    q=a[i][k]//a[k][k];ra(i,k,-q)
                    if a[i][k]:rs(i,k)
                    changed=True;break
            if changed:continue
            for j in range(k+1,n):
                if a[k][j]:
                    q=a[k][j]//a[k][k];ca(j,k,-q)
                    if a[k][j]:cs(j,k)
                    changed=True;break
            if changed:continue
            bad=next(((i,j) for i in range(k+1,m) for j in range(k+1,n)
                      if a[i][j]%a[k][k]),None)
            if bad is None:break
            ra(k,bad[0],1)
        if a[k][k]<0:
            a[k]=[-x for x in a[k]];ops.append(['rn',k])
        k+=1
    diag=[a[i][i] for i in range(min(m,n)) if a[i][i]]
    require(all(y%x==0 for x,y in zip(diag,diag[1:])),'Smith divisibility failure')
    return diag,a,ops


def certificate_check(initial,final,ops):
    """Replay only elementary operations; does not rerun the Smith algorithm."""
    b=[r[:] for r in initial]
    for op in ops:
        kind=op[0]
        if kind=='rs':_,i,j=op;b[i],b[j]=b[j],b[i]
        elif kind=='cs':
            _,i,j=op
            for r in b:r[i],r[j]=r[j],r[i]
        elif kind=='ra':
            _,i,j,c=op;require(i!=j,'non-unimodular row addition')
            src=b[j][:]
            for t in range(len(b[i])):b[i][t]+=c*src[t]
        elif kind=='ca':
            _,i,j,c=op;require(i!=j,'non-unimodular column addition')
            for r in b:r[i]+=c*r[j]
        elif kind=='rn':_,i=op;b[i]=[-x for x in b[i]]
        else:raise ValueError('unknown certificate operation')
    require(b==final,'elementary-operation replay mismatch')
    require(all(x==0 for i,row in enumerate(b) for j,x in enumerate(row) if i!=j),
            'final matrix not diagonal')
    ds=[b[i][i] for i in range(len(b))]
    require(all(x>0 for x in ds),'nonpositive invariant')
    require(all(y%x==0 for x,y in zip(ds,ds[1:])),'non-Smith diagonal')
    return True


def quotient(qs, capacity_loss=0):
    require(capacity_loss in (0,1), 'unsupported capacity loss')
    rows,all_places,excluded,full_L=build(qs)
    kept=[i for i,p in enumerate(all_places) if p['h']>capacity_loss]
    places=[dict(all_places[i],effective_h=all_places[i]['h']-capacity_loss) for i in kept]
    L=[[full_L[j][i] % (7**places[k]['effective_h']) for k,i in enumerate(kept)] for j in range(5)]
    removed=[all_places[i]['label'] for i in range(len(all_places)) if i not in kept]
    d=len(places)
    # Columns generate relations in Z^d: cyclic orders then five global rows.
    A=[[((7**places[i]['effective_h']) if j==i else 0) for j in range(d)] +
       [L[j][i] for j in range(5)] for i in range(d)]
    if d:
        diag,final,ops=smith(A);certificate_check(A,final,ops)
    else:diag=[];final=[];ops=[]
    invariants=[x for x in diag if x!=1]
    e=max([val7(x) for x in invariants],default=0)
    return {'primes':qs,'capacity_loss':capacity_loss,'removed_capacity_zero_places':removed,'rows':rows,'places':places,'ineligible_places':excluded,
            'relation_matrix':A,'smith_matrix':final,'unimodular_operations':ops,
            'smith_diagonal':diag,'nontrivial_invariant_factors':invariants,
            'seven_exponent':e,'exponent':7**e,'certificate_replayed':True}


def toy_checks():
    count=0
    # Exhaust every single relation in C7^2, C49 x C7 and C49^2.
    # Enumerate only the cyclic relation subgroup; quotient exponent checked
    # by whether multiplying each ambient generator lies in that subgroup.
    for orders in ((7,7),(49,7),(49,49)):
        a,b=orders
        for x,y in itertools.product(range(a),range(b)):
            A=[[a,0,x],[0,b,y]]
            diag,fin,ops=smith(A);certificate_check(A,fin,ops)
            H=set();z=(0,0)
            while z not in H:
                H.add(z);z=((z[0]+x)%a,(z[1]+y)%b)
            expected_order=a*b//len(H)
            got=1
            for v in diag:got*=v
            require(got==expected_order,'toy quotient order mismatch')
            e=0
            while ((7**e%a,0) not in H or (0,7**e%b) not in H):e+=1
            require(max(diag)==7**e,'toy quotient exponent mismatch')
            count+=1
    return count


def depth_three_compatibility():
    qs=[11,13,19,29,31,43,71,491,1471]
    c=quotient(qs,1);d=len(c['places'])
    M=[[c['relation_matrix'][j][d+i]%7 for j in range(d)] for i in range(5)]
    ker=kernel(M)
    require(ker==[[3,4,6,1]],'depth3 character line changed')
    require(all(x for x in ker[0]),'nontrivial character does not force full support')
    K=[[M[j][i] for j in (0,2,3)] for i in range(d)]
    require(K==[[4,5,6],[3,5,6],[5,5,2],[2,5,2]],'Kummer restriction matrix changed')
    minor=K[:3]
    a,b,c0=minor[0];e,f,g=minor[1];h,i,j=minor[2]
    det=a*(f*j-g*i)-b*(e*j-g*h)+c0*(e*i-f*h)
    require(det%7==1 and len(rref(K)[1])==3,'Kummer compatibility determinant')
    checked=survived=0
    for u0,u1,r0,r1 in itertools.product(range(7),repeat=4):
        if (r0,r1)==(0,0):continue
        checked+=1
        ok=all((row[0]*u0+row[1]*r0+row[2])%7==0 and
               (row[0]*u1+row[1]*r1)%7==0 for row in K)
        survived+=int(ok)
    require(checked==2352 and survived==0,'normalized F49 Kummer compatibility')
    return {'support':qs,'places':[p['label'] for p in c['places']],
            'ray_rows_mod7':M,'ray_kernel_basis':ker,'kummer_matrix':K,
            'integer_three_by_three_minor':det,'minor_mod7':det%7,
            'normalized_F49_vectors_checked':checked,'surviving_vectors':survived,
            'arithmetic_result':'Under inherited hypotheses and this explicit support bound, n<=2',
            'nonclaim':'No bound on support of arbitrary C; depth1 and depth2 remain'}


def main(output,primes):
    base=[11,13,19,29,31,43,71]
    supports=[primes] if primes is not None else [base,base+[491],base+[491,1471]]
    cases=[quotient(qs,loss) for qs in supports for loss in (0,1)]
    n=toy_checks()
    if primes is None:
        require(cases[0]['nontrivial_invariant_factors']==[7,7],'base quotient changed')
    payload={'status':'PASS','cases':cases,'exhaustive_toy_presentations':n,'depth_three_compatibility':depth_three_compatibility(),
             'arithmetic':'integer Smith operations with unimodular replay; exact residue logs',
             'nonclaims':['Support is an input assumption, not a bound on C',
                         'Ray characters are not automatically actual Frey diagonals',
                         'No Lean formalization or independent mathematical reviewer']}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','toy_cases':n,'quotients':[{'primes':c['primes'],
          'loss':c['capacity_loss'],'invariants':c['nontrivial_invariant_factors'],'e':c['seven_exponent']} for c in cases]},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--primes',type=int,nargs='+');a=p.parse_args();main(a.output,a.primes)
