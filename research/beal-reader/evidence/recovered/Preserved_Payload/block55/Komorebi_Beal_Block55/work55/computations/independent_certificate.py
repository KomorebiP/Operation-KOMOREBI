#!/usr/bin/env python3
"""Independent finite certificate: sqrt(5) residue basis, seventh symbols,
integer-minor ranks, all F49 directions. Imports no primary arithmetic code.
"""
from __future__ import annotations
import argparse,itertools,json,math
from pathlib import Path

QS=[97,197,293,491,587,883,1373,1471,1567,1667]
NAMES=['phi','2','3','sqrt5','7']
def check(ok,msg):
    if not ok:raise AssertionError(msg)

def vp(a,p=7):
    check(a!=0,'zero valuation');s=0
    while a%p==0:s+=1;a//=p
    return s

def prime(n):
    return n>=2 and all(n%d for d in range(2,math.isqrt(n)+1))

class Residue:
    def __init__(self,q,sqrt_root=None):
        check(prime(q),'not prime');self.q=q;self.r=sqrt_root;self.Q=q if sqrt_root is not None else q*q
        if self.r is None:check(pow(5,(q-1)//2,q)==q-1,'not an inert field')
        else:check(self.r*self.r%q==5,'incorrect sqrt5 root')
    def elm(self,a,b=0):
        return ((a+(self.r or 0)*b)%self.q,0) if self.r is not None else (a%self.q,b%self.q)
    def mul(self,x,y):
        a,b=x;c,d=y;return self.elm(a*c+5*b*d,a*d+b*c)
    def pow(self,x,n):
        z=(1,0)
        while n:
            if n%2:z=self.mul(z,x)
            n//=2;x=self.mul(x,x)
        return z
    def symbol_column(self):
        exponent=(self.Q-1)//7
        generator=None;tested=0
        for b in range(1 if self.r is not None else self.q):
            for a in range(self.q):
                if (a,b)==(0,0):continue
                tested+=1;z=self.pow(self.elm(a,b),exponent)
                if z!=(1,0):generator=z;break
            if generator is not None:break
        check(generator is not None and self.pow(generator,7)==(1,0),'order7 generator failed')
        table={self.pow(generator,j):j for j in range(7)}
        check(len(table)==7,'symbol table not injective')
        inv2=pow(2,-1,self.q)
        elements=[self.elm(inv2,inv2),self.elm(2),self.elm(3),self.elm(0,1),self.elm(7)]
        logs=[table[self.pow(x,exponent)] for x in elements]
        # Every product of the five named values, and their inverses, is checked.
        checks=0
        for i,x in enumerate(elements):
            for j,y in enumerate(elements):
                check(table[self.pow(self.mul(x,y),exponent)]==(logs[i]+logs[j])%7,'symbol homomorphism')
                checks+=1
            inv=self.pow(x,self.Q-2)
            check(table[self.pow(inv,exponent)]==(-logs[i])%7,'symbol inverse')
            checks+=1
        return logs,generator,tested,checks

def det(a):
    """Exact integer Bareiss elimination, different from primary mod7 RREF."""
    n=len(a)
    if n==0:return 1
    a=[r[:] for r in a];sign=1;previous=1
    for k in range(n-1):
        if a[k][k]==0:
            z=next((i for i in range(k+1,n) if a[i][k]),None)
            if z is None:return 0
            a[k],a[z]=a[z],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=a[i][j]*pivot-a[i][k]*a[k][j]
                check(v%previous==0,'Bareiss divisibility')
                a[i][j]=v//previous
        for i in range(k+1,n):a[i][k]=0
        previous=pivot
    return sign*a[-1][-1]

def rank(a):
    if not a or not a[0]:return 0
    for d in range(min(len(a),len(a[0])),0,-1):
        for rr in itertools.combinations(range(len(a)),d):
            for cc in itertools.combinations(range(len(a[0])),d):
                if det([[a[i][j] for j in cc] for i in rr])%7:return d
    return 0

def subcols(M,c):return [[r[i] for i in c] for r in M]

def run(primary):
    ps=[];symbol_checks=0;generators_tested=0
    for q in QS:
        roots=[s for s in range(q) if s*s%q==5]
        local=[(None,Residue(q))] if not roots else sorted([(((1+s)*pow(2,-1,q))%q,Residue(q,s)) for s in roots],key=lambda t:t[0])
        for root,f in local:
            h=vp(f.Q-1);check(h>=2,'fixture no longer high')
            logs,g,nt,nc=f.symbol_column();symbol_checks+=nc;generators_tested+=nt
            label=f'{q}:inert' if root is None else f'{q}:phi={root}'
            old=next(p for p in primary['places'] if p['label']==label)
            oldcol=[old['logs'][name]%7 for name in NAMES]
            scale=next((c for c in range(1,7) if all((c*x-y)%7==0 for x,y in zip(oldcol,logs))),None)
            check(scale is not None and old['h']==h and old['norm']==f.Q,'independent residue mismatch')
            ps.append({'label':label,'q':q,'norm':f.Q,'h':h,'symbols':logs,'generator':list(g),'primary_column_scale':scale})
    M=[[p['symbols'][j] for p in ps] for j in range(5)]
    K=[[p['symbols'][j] for j in (0,2,3)] for p in ps]
    # Enumerate all normalized F49 directions directly. No reduction to F7 used.
    masks={};directions=0
    for a,b,c,d in itertools.product(range(7),repeat=4):
        if c==d==0:continue
        z=frozenset(i for i,l in enumerate(K) if (l[0]*a+l[1]*c+l[2])%7==0 and (l[0]*b+l[1]*d)%7==0)
        masks.setdefault(z,[]).append([a,b,c,d]);directions+=1
    compatible=[];candidate_count=0;all_circuits=0
    for size in range(1,6):
        for c in itertools.combinations(range(len(ps)),size):
            candidate_count+=1;B=subcols(M,c)
            if rank(B)!=size-1:continue
            if any(rank(subcols(M,[v for v in c if v!=removed]))!=size-1 for removed in c):continue
            all_circuits+=1
            witness=next((aa[0] for z,aa in masks.items() if set(c)<=z),None)
            if witness is not None:
                compatible.append({'indices':list(c),'q_support':sorted({ps[i]['q'] for i in c}),'kummer_rank':rank([K[i] for i in c]),'F49_alpha_witness_sqrt5_basis':witness})
    check({tuple(c['indices']) for c in compatible}=={tuple(c['indices']) for c in primary['compatible_circuits']},'compatible circuit mismatch')
    check({tuple(c['indices']):c['kummer_rank'] for c in compatible}=={tuple(c['indices']):c['kummer_rank'] for c in primary['compatible_circuits']},'Kummer rank mismatch')
    check(candidate_count==primary['candidate_subsets_of_ideals_size_at_most_5'],'candidate coverage mismatch')
    passed=0
    for cell in primary['classification']:
        qset=set(cell['prime_support']);survives=any(set(c['q_support'])<=qset for c in compatible)
        check(cell['criterion_passed']==(not survives),'1024-subset classification mismatch')
        passed+=int(not survives)
    # Replay each small maximal-zero-set minor from the main arithmetic class.
    five=primary['five_prime_class'];fm=five['matrix_mod7']
    minor_count=0
    for c in five['maximal_zero_set_minor_certificates']:
        d=det([[fm[i][j] for j in c['columns']] for i in c['rows']])
        check(d==c['determinant_integer'] and d%7==c['determinant_mod7'] and d%7!=0,'small minor certificate')
        minor_count+=1
    # Orthogonal determinant benchmarks, including singular matrices and row swaps.
    determinant_cases=0
    for entries in itertools.product(range(-2,3),repeat=4):
        a,b,c,d=entries;check(det([[a,b],[c,d]])==a*d-b*c,'2x2 determinant benchmark');determinant_cases+=1
    # Explicit rational local negative control, without importing matrix code.
    N=[[-2401,7],[-823543,2401]];F=[[148,1],[50421,344]]
    def mult(A,B):return [[sum(A[i][k]*B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    check(mult(N,N)==[[0,0],[0,0]],'negative nilpotence')
    check(mult(F,N)==[[491*x for x in row] for row in N] and mult(N,F)==N,'negative toric identities')
    check(det(F)==491 and vp(F[1][0])==5 and vp(N[1][0])==7,'negative depth')
    check(vp(F[1][1]-1)==3 and vp(N[0][0])==4 and F[0][1]%7==1,'negative class/order')
    return {'status':'PASS','arithmetic':'independent sqrt5 residue fields; seventh symbols; exact integer minor ranks',
            'imports_primary_code':False,'places':ps,'named_symbol_checks':symbol_checks,
            'generator_candidates_tested':generators_tested,'full_F49_directions':directions,
            'distinct_zero_masks':len(masks),'candidate_ideal_subsets':candidate_count,
            'all_circuits_up_to_size5':all_circuits,'compatible_circuits':compatible,
            'classified_rational_supports':1024,'criterion_pass_count':passed,'criterion_survivor_count':1024-passed,
            'small_zero_set_minor_certificates':minor_count,'determinant_benchmarks':determinant_cases,'explicit_negative_local_control':'PASS',
            'nonclaims':['Independent implementation is not an independent mathematical reviewer',
                         'No actual coefficient descent','No Frey realization of surviving patterns']}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--primary',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    result=run(json.loads(a.primary.read_text()));a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('status','full_F49_directions','candidate_ideal_subsets','classified_rational_supports','criterion_pass_count','criterion_survivor_count','named_symbol_checks','determinant_benchmarks')},indent=2))
