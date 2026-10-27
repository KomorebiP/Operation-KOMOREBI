#!/usr/bin/env python3
"""Exact prime-ideal residue presentation for the Block54 character quotient.
Finite assertions only; not a point search or a Frey realization algorithm.
"""
from __future__ import annotations
import argparse
import itertools
import json
from math import isqrt
from pathlib import Path


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def prime(q: int) -> bool:
    return q >= 2 and all(q % d for d in range(2, isqrt(q)+1))


def val7(x: int) -> int:
    require(x != 0, "valuation of zero not used")
    r=0
    while x % 7 == 0:
        x//=7; r+=1
    return r


class Field:
    """Fq, or Fq[phi]/(phi^2-phi-1). Split phi chosen by its root."""
    def __init__(self, q: int, phi_root: int | None = None):
        require(prime(q) and q not in (2,5,7), "Unsupported/nonprime residue characteristic")
        self.q=q; self.phi_root=phi_root
        self.Q=q if phi_root is not None else q*q
        if phi_root is not None:
            require((phi_root*phi_root-phi_root-1)%q==0, "invalid split root")
        else:
            require(pow(5,(q-1)//2,q)==q-1, "quadratic quotient is not a field")
    def elm(self,a:int,b:int=0) -> tuple[int,int]:
        if self.phi_root is not None:
            return ((a+b*self.phi_root)%self.q,0)
        return (a%self.q,b%self.q)
    def mul(self,x:tuple[int,int],y:tuple[int,int])->tuple[int,int]:
        a,b=x;c,d=y
        return self.elm(a*c+b*d,a*d+b*c+b*d)
    def power(self,x:tuple[int,int],n:int)->tuple[int,int]:
        require(n>=0,'negative exponent');r=(1,0)
        while n:
            if n&1:r=self.mul(r,x)
            x=self.mul(x,x);n>>=1
        return r
    def units(self):
        for b in range(1 if self.phi_root is not None else self.q):
            for a in range(self.q):
                if (a,b)!=(0,0):yield(a,b)
    def logs(self):
        h=val7(self.Q-1);order=7**h
        require(h>0,'not eligible')
        cofactor=(self.Q-1)//order
        # This surjection is a coordinate on the 7-primary quotient, not the
        # canonical Sylow projection. A different choice rescales its column.
        for x in self.units():
            z=self.power(x,cofactor)
            if self.power(z,order//7)!=(1,0): break
        else: raise ValueError('generator not found')
        table={};t=(1,0)
        for j in range(order):
            require(t not in table,'nonprimitive generator')
            table[t]=j;t=self.mul(t,z)
        require(t==(1,0),'incorrect cyclic order')
        named={'phi':self.elm(0,1),'2':self.elm(2),'3':self.elm(3),
               'sqrt5':self.elm(-1,2),'7':self.elm(7)}
        values={name:table[self.power(v,cofactor)] for name,v in named.items()}
        return h,z,values


def places(q:int):
    require(prime(q),'composite input')
    require(q not in (2,3,5,7),'fixed prime is not a support prime')
    roots=[r for r in range(q) if (r*r-r-1)%q==0]
    if roots:return[(f'{q}:phi={r}',Field(q,r)) for r in roots]
    return[(f'{q}:inert',Field(q))]


def rref(matrix:list[list[int]],p:int=7):
    a=[[x%p for x in row] for row in matrix]
    if not a:return a,[]
    r=0;piv=[]
    for c in range(len(a[0])):
        j=next((i for i in range(r,len(a)) if a[i][c]),None)
        if j is None:continue
        a[r],a[j]=a[j],a[r]
        inv=pow(a[r][c],-1,p);a[r]=[(x*inv)%p for x in a[r]]
        for i in range(len(a)):
            if i!=r:
                k=a[i][c];a[i]=[(x-k*y)%p for x,y in zip(a[i],a[r])]
        piv.append(c);r+=1
        if r==len(a):break
    return a,piv


def kernel(matrix:list[list[int]],p:int=7):
    a,piv=rref(matrix,p);d=len(matrix[0]) if matrix else 0
    out=[]
    for f in range(d):
        if f in piv:continue
        v=[0]*d;v[f]=1
        for i,c in enumerate(piv):v[c]=-a[i][f]%p
        out.append(v)
    return out


def build(qs:list[int]):
    require(len(set(qs))==len(qs),'duplicate rational prime')
    rows=['phi','2','3','sqrt5','7'];records=[];ineligible=[]
    for q in sorted(qs):
        for label,f in places(q):
            if (f.Q-1)%7:
                ineligible.append({'label':label,'norm':f.Q});continue
            h,z,logs=f.logs()
            records.append({'label':label,'q':q,'norm':f.Q,'phi_root':f.phi_root,
                            'h':h,'generator':list(z),'logs':logs})
    matrix=[[p['logs'][x] for p in records] for x in rows]
    return rows,records,ineligible,matrix


def main(output:Path):
    rows,ps,excluded,M=build([11,13,19,29,31,43,71])
    require(len(ps)==6 and all(p['h']==1 for p in ps),'reference support changed')
    R,piv=rref(M);K=kernel(M)
    require(len(piv)==4 and len(K)==2,'reference rank changed')
    F=Field(13) # only used for a field structural check below, not coefficient F49
    support_counts={}
    vectors=[]
    for a,b in itertools.product(range(7),repeat=2):
        v=[(a*x+b*y)%7 for x,y in zip(K[0],K[1])]
        require(all(sum(x*y for x,y in zip(row,v))%7==0 for row in M),'kernel failure')
        mask=tuple(i for i,x in enumerate(v) if x)
        support_counts[mask]=support_counts.get(mask,0)+1;vectors.append(v)
    require(len({tuple(v) for v in vectors})==49,'kernel independence failed')
    circuits=[s for s in support_counts if s and not any(set(t)<set(s) for t in support_counts if t)]
    require(sorted(map(len,circuits))==[3,3,4],'minimal supports changed')
    # F49-valued vectors are independent F7 coordinates. Complete all 49^2.
    support49={}
    for v,w in itertools.product(vectors,repeat=2):
        mask=tuple(i for i,(a,b) in enumerate(zip(v,w)) if a or b)
        support49[mask]=support49.get(mask,0)+1
    require(sum(support49.values())==2401,'F49 enumeration incomplete')
    # Seven-primary quotients are not exhausted by this one finite support.
    # Retain the old two-place rational-character counterexample.
    q=1504231
    require(prime(q) and val7(q-1)==1,'old counterexample prime check')
    require(all(pow(t,(q-1)//7,q)==1 for t in (2,3,5,7)), 'old residue checks')
    # Avoid an O(q) split-root search. q=3 mod4 so square root is exact by a power.
    sq=pow(5,(q+1)//4,q);require(sq*sq%q==5,'square root failure')
    roots=sorted({(1+sq)*pow(2,-1,q)%q,(1-sq)*pow(2,-1,q)%q})
    old=[]
    for root in roots:
        f=Field(q,root);h,z,logs=f.logs();old.append({'phi_root':root,'generator':list(z),'logs':logs})
    # Same rational seventh-root generator at both places; phi has opposite logs.
    require(old[0]['generator']==old[1]['generator'],'incompatible split generators')
    require((old[0]['logs']['phi']+old[1]['logs']['phi'])%7==0,'unit cancellation failed')
    require(all(p['logs'][a]==0 for p in old for a in ('2','3','sqrt5','7')),'fixed-prime row not zero')
    # New complete normalization checks on all six residue fields.
    multiplicative_checks=0
    for rec in ps:
        f=Field(rec['q'],rec['phi_root']);h,z,logs=f.logs();d=7**h;co=(f.Q-1)//d
        tab={f.power(z,j):j for j in range(d)}
        units=list(f.units())
        # Every nonzero element and each of the five global generators.
        for x in units:
            for y in [f.elm(0,1),f.elm(2),f.elm(3),f.elm(-1,2),f.elm(7)]:
                lx=tab[f.power(x,co)];ly=tab[f.power(y,co)]
                lxy=tab[f.power(f.mul(x,y),co)]
                require((lx+ly-lxy)%d==0,'log not a homomorphism')
                multiplicative_checks+=1
    invalid=0
    for bad in ([13,13],[21],[7]):
        try:build(bad)
        except ValueError:invalid+=1
        else:raise ValueError('invalid support accepted')
    payload={'status':'PASS','arithmetic':'exact integer pairs, phi^2=phi+1; F7 row reduction',
             'support_contract':'eta ramification contained in the displayed places; NOT a universal bound on C',
             'rows':rows,'places':ps,'ineligible_places':excluded,'matrix_mod7':M,
             'rref_mod7':R,'rank':len(piv),'kernel_basis_mod7':K,
             'quotient_invariant_factors':[7,7],
             'complete_F7_kernel_vectors':49,'complete_F49_character_vectors':2401,
             'support_counts_F7':[{'indices':list(s),'count':c} for s,c in sorted(support_counts.items())],
             'support_counts_F49':[{'indices':list(s),'count':c} for s,c in sorted(support49.items())],
             'minimal_supports':[list(s) for s in sorted(circuits)],
             'log_homomorphism_checks':multiplicative_checks,'invalid_inputs_rejected':invalid,
             'surviving_two_place_counterexample':{'q':q,'places':old,'inertia_vector':[1,1],
                   'meaning':'actual abelian ray character, NOT realized as a Frey diagonal'},
             'nonclaims':['No Beal proof','No exhaustion of all supports','No independent mathematical review']}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','rank':len(piv),'kernel_basis':K,'matrix':M,
                      'labels':[x['label'] for x in ps],'supports':payload['support_counts_F49'],
                      'log_checks':multiplicative_checks},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();main(args.output)
