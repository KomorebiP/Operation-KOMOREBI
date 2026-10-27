#!/usr/bin/env python3
"""Separate arithmetic implementation; imports no primary/project arithmetic.
Direct square-root counts, discrete-log canonical curves, cyclic norm products,
and trace/norm enumeration in F7[theta]/(theta^2-theta-1).
"""
from __future__ import annotations
import argparse,hashlib,itertools,json,math
from pathlib import Path
import os
try:
    if os.environ.get("BEAL_FORCE_STDLIB"): raise ImportError
    import numpy as np
except ImportError:
    np = None


def check(ok,why):
    if not ok:raise AssertionError(why)
PRIMES=(701,911,1009,)
def distinct_factors(n):
    out=[];d=2
    while d*d<=n:
        if n%d==0:
            out.append(d)
            while n%d==0:n//=d
        d+=1
    if n>1:out.append(n)
    return out

def phi_multiply(x,y,p):
    a,b=x;c,d=y
    return ((a*c+b*d)%p,(a*d+b*c+b*d)%p)

def phi_power(x,n,p):
    ans=(1,0)
    while n:
        if n&1:ans=phi_multiply(ans,x,p)
        x=phi_multiply(x,x,p);n//=2
    return ans

FA=[[((x%7+y%7)%7)+7*((x//7+y//7)%7) for y in range(49)] for x in range(49)]
FM=[[(lambda z:z[0]+7*z[1])(phi_multiply((x%7,x//7),(y%7,y//7),7)) for y in range(49)] for x in range(49)]
NEG=[(-x%7)%7+7*((-(x//7))%7) for x in range(49)]
def fdot(xs,ys):
    v=0
    for x,y in zip(xs,ys):v=FA[v][FM[x][y]]
    return v

def to_w(x):
    a,b=x%7,x//7
    return (a+4*b)%7+7*(4*b%7)

def trim(f):
    while f and not f[-1]:f.pop()
    return f

def rem(f,g,p):
    f=trim(f[:]);g=trim(g[:]);iv=pow(g[-1],-1,p)
    while len(f)>=len(g):
        a=f[-1]*iv%p;j=len(f)-len(g)
        for k,c in enumerate(g):f[j+k]=(f[j+k]-a*c)%p
        trim(f)
    return f

def smooth(a,b,p):
    f=[5*b*b%p,12*a%p,0,10*b%p,0,0,1]
    g=[12*a%p,0,30*b%p,0,0,6]
    while g:f,g=g,rem(f,g,p)
    return len(trim(f))==1

def count_audit(primary):
    all_sets={};summary=[];gcd_checks=0
    for p in PRIMES:
        rec=next(x for x in primary['primes'] if x['q']==p)
        squares={x*x%p for x in range(p)}
        d=next(c for c in range(1,p) if (1-4*c)%p not in squares)
        # theta^2=theta-d, a field different from the primary norm-character model.
        def sq(a,b):return ((a*a-d*b*b)%p,(2*a*b+b*b)%p)
        def times(a,b,c,e):return ((a*c-d*b*e)%p,(a*e+b*c+b*e)%p)
        roots1=[0]*p;roots2=[0]*(p*p)
        for x in range(p):roots1[x*x%p]+=1
        if np is not None:
            xx,yy=np.indices((p,p),dtype=np.int64);xx=xx.ravel();yy=yy.ravel()
            aa=(xx*xx-d*yy*yy)%p;bb=(2*xx*yy+yy*yy)%p
            roots2=np.bincount(aa+p*bb,minlength=p*p)
            cc=(aa*xx-d*bb*yy)%p;ee=(aa*yy+bb*xx+bb*yy)%p
            powers=(xx,yy,cc,ee,(cc*cc-d*ee*ee)%p,(2*cc*ee+ee*ee)%p)
        else:
            powers=[]
            for x in range(p):
                for y in range(p):
                    a,b=sq(x,y);roots2[a+p*b]+=1
                    c,e=times(a,b,x,y);f,g=sq(c,e)
                    powers.append((x,y,c,e,f,g))
        base=[(x,pow(x,3,p),pow(x,6,p)) for x in range(p)]
        g=next(g for g in range(2,p) if all(pow(g,(p-1)//d,p)!=1 for d in distinct_factors(p-1)))
        logs={};v=1
        for i in range(p-1):logs[v]=i;v=v*g%p
        check(len(logs)==p-1,'Discrete-log canonicalizer incomplete')
        gcd3=math.gcd(3,p-1);gcd5=math.gcd(5,p-1)
        def canonical(a,b):
            if not b:return (pow(g,logs[a]%gcd5,p),0)
            e=logs[b];j=e%gcd3
            # Solve 3u = j-e modulo p-1; enumerate its at most3 solutions.
            modulus=(p-1)//gcd3
            u=((j-e)//gcd3*pow(3//gcd3,-1,modulus))%modulus
            return min((a*pow(g,5*(u+i*modulus),p)%p,pow(g,j,p)) for i in range(gcd3))
        seventh={pow(c,7,p) for c in range(1,p)}
        eligible={(a,b) for a in range(p) for b in range(p) if (pow(a,3,p)+pow(b,5,p))%p in seventh}
        representatives={canonical(a,b) for a,b in eligible}
        f=1 if p%5 in (1,4) else 2;Q=p**f
        ps=[x for x in range(p) if (x*x-x-1)%p==0]
        if ps:
            signs=[1 if (9-3*x)%p in squares else -1 for x in ps]
            check(len(set(signs))==1,'Conjugate twist mismatch');nu=signs[0]
        else:
            val=phi_power((9,-3),(Q-1)//2,p)
            check(val in [(1,0),(p-1,0)],'Invalid twist character');nu=1 if val==(1,0) else -1
        check((rec['f'],rec['Q'],rec['nu'])==(f,Q,nu),'Base-field/twist mismatch')
        raw={};n2_count=0;good=set();target=[Q*Q,-2*Q*(Q+1),(Q+1)**2+2*Q,-2*(Q+1),1]
        for a,b in sorted(representatives):
            n1=2+sum(roots1[(x6+10*b*x3+12*a*x+5*b*b)%p] for x,x3,x6 in base)
            t=p+1-n1;stage=(f==2 or (nu*t-2*(Q+1))%7==0)
            n2=None;pq=None;pv=None;ks=[];residual=False
            if stage:
                if np is not None:
                    x,y,x3,y3,x6,y6=powers
                    indices=(x6+10*b*x3+12*a*x+5*b*b)%p+p*((y6+10*b*y3+12*a*y)%p)
                    n2=int(2+roots2[indices].sum(dtype=np.int64))
                else:
                    n2=2+sum(roots2[(x6+10*b*x3+12*a*x+5*b*b)%p+p*((y6+10*b*y3+12*a*y)%p)] for x,y,x3,y3,x6,y6 in powers)
                n2_count+=1;num=t*t-p*p-1+n2;check(num%2==0,'Newton coefficient not integral');b2=num//2
                pq=[p*p,-p*t,b2,-t,1]
                if f==2:
                    power2=t*t-2*b2;power3=t*power2-b2*t+3*p*t
                    power4=t*power3-b2*power2+p*t*t-4*p*p
                    S=nu*power2;B=(power2*power2-power4)//2
                else:S=nu*t;B=b2
                pv=[Q*Q,-Q*S,B,-S,1];residual=all((x-y)%7==0 for x,y in zip(pv,target))
                if residual:
                    trace_numer=S-2*(Q+1)
                    norm_numer=(B-2*Q)-(Q+1)*S+(Q+1)**2
                    check(trace_numer%7==0 and norm_numer%49==0,'Defect trace/norm not integral')
                    ts=trace_numer//7%7;ns=norm_numer//49%7
                    for x in range(49):
                        u,v=x%7,x//7
                        if (2*u+v)%7==ts and (u*u+u*v-v*v)%7==ns:ks.append(x)
                    check(ks,'No coefficient-field trace root')
                    good.update(ks)
            raw[(a,b)]={'N1':n1,'N2':n2,'rational_polynomial':pq,'twisted_polynomial':pv,
             'trace_stage_pass':stage,'residual_pass':residual,'defect_roots':sorted(to_w(x) for x in ks)}
        covered=set();pairs_residual=0
        for row in rec['rows']:
            a,b=row['representative'];expected=raw[canonical(a,b)]
            for key,v in expected.items():check(row[key]==v,'Point-count row mismatch '+str((p,a,b,key)))
            if expected['residual_pass']:pairs_residual+=len(row['admissible_pairs'])
            for aa,bb in row['admissible_pairs']:
                check((aa,bb) in eligible and (aa,bb) not in covered,'Point-count coverage overlap')
                check(canonical(aa,bb)==canonical(a,b),'False curve-orbit assignment')
                check(smooth(aa,bb,p),'Singular good-locus curve');gcd_checks+=1;covered.add((aa,bb))
        check(covered==eligible,'Missing admissible equation pair')
        dig=hashlib.sha256()
        for a,b in sorted(eligible):dig.update(f'{a},{b}\n'.encode())
        check(rec['pair_set_sha256']==dig.hexdigest(),'Pair-set digest mismatch')
        check(rec['admissible_pairs']==len(eligible) and rec['residual_pairs']==pairs_residual,'Pair totals mismatch')
        check(rec['trace_defect_set']==sorted(to_w(x) for x in good),'Trace-defect set mismatch')
        check((rec['degree_one_counts'],rec['degree_two_counts'])==(len(raw),n2_count),'Count coverage totals')
        all_sets[p]=good
        summary.append({'q':p,'equation_pairs':len(eligible),'N1_counts':len(raw),'N2_counts':n2_count,
                        'residual_pairs':pairs_residual,'square_table_size':p*p,'defect_set':[to_w(x) for x in sorted(good)]})
        print('independent counts',p,'PASS',flush=True)
    return all_sets,{'primes':summary,'smoothness_checks':gcd_checks}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--counts',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();data=json.loads(a.counts.read_text())
    check(data['status']=='PASS_FINITE_COUNTS','Invalid primary input status')
    check([p['q'] for p in data['primes']]==list(PRIMES),'Wrong declared primes')
    sets,stats=count_audit(data)
    roots_by_prime={}
    for q in PRIMES:
        roots=[x for x in range(q) if (x*x-x-1)%q==0]
        check(len(roots)==2,'Test prime not split')
        for x in roots:
            check((9-3*(1-x)-(9-3*x)*x*x)%q==0,'Twist conjugation identity')
        roots_by_prime[str(q)]=roots
    out={'schema':'beal.block68.independent_counts.v1','status':'PASS_INDEPENDENT_COUNTS',
         'statistics':stats,'defect_sets_w_codes':{str(q):sorted(to_w(x) for x in sets[q]) for q in PRIMES},
         'split_phi_roots':roots_by_prime,'primary_arithmetic_imports':False,
         'basis':'theta^2=theta-d in residue count fields; theta^2=theta+1 in coefficient field',
         'scope':'Exact bounded count audit, not independent mathematical review of geometric inputs.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(out['status'])
if __name__=='__main__':main()
