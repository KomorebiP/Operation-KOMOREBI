#!/usr/bin/env python3
"""Independent refinement: inverse cyclotomic basis, direct symbols, theta coefficient arithmetic."""
from __future__ import annotations
import argparse,copy,hashlib,json,math
from pathlib import Path
GENERATORS={1051:(-2,-1,2,1,0,-1)}
def check(ok,why):
    if not ok:raise AssertionError(why)
def isprime(q):return q>1 and not any(q%d==0 for d in range(2,math.isqrt(q)+1))
def prime_divisors(n):return [d for d in range(2,n+1) if n%d==0 and isprime(d)]
def primitive(q):return next(g for g in range(2,q) if not any(pow(g,(q-1)//d,q)==1 for d in prime_divisors(q-1)))
def invbasis(a):
    out=[0]*7
    for j,x in enumerate(a):out[-j%7]+=x
    return out
def cyclic_times(a,b):return [sum(a[i]*b[(j-i)%7] for i in range(7)) for j in range(7)]
def exact_norm(cs):
    a=invbasis(cs);out=[1,0,0,0,0,0,0]
    for b in range(1,7):
        conj=[0]*7
        for j,c in enumerate(a):conj[j*b%7]+=c
        out=cyclic_times(out,conj)
    check(len(set(out[1:]))==1,'Norm did not become rational')
    return out[0]-out[1]
def val(a,t,q):return sum(c*pow(t,i,q) for i,c in enumerate(a))%q
# Coefficient model theta^2=theta+1. It is not used to model the base-field radical.
def add(x,y):return (x%7+y%7)%7+7*((x//7+y//7)%7)
def times(x,y):
    a,b=x%7,x//7;c,d=y%7,y//7
    return (a*c+b*d)%7+7*((a*d+b*c+b*d)%7)
def from_w(x):return (x%7-x//7)%7+7*(2*(x//7)%7)
def to_w(x):return (x%7+4*(x//7))%7+7*(4*(x//7)%7)
def dot(xs,ys):
    z=0
    for x,y in zip(xs,ys):z=add(z,times(x,y))
    return z
def canon(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inherited',type=Path,required=True);ap.add_argument('--counts',type=Path,required=True);ap.add_argument('--certificate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    old=json.loads(a.inherited.read_text());pc=json.loads(a.counts.read_text());cert=json.loads(a.certificate.read_text())
    check(cert['status']=='PASS_FINITE_FILTER','Wrong primary-filter status')
    check(cert['counts_sha256']==hashlib.sha256(a.counts.read_bytes()).hexdigest(),'Wrong source counts hash');check(cert['inherited_sha256']==hashlib.sha256(a.inherited.read_bytes()).hexdigest(),'Wrong inherited hash')
    universe=[q for q in range(11,2001) if isprime(q) and q%7==1 and q%5 in (2,3)]
    check(cert['universe']==old['universe']==universe,'Wrong conductor universe');columns={};nsym=0
    for q in universe:
        g=primitive(q);z=pow(g,(q-1)//7,q);theta=pow(z,-1,q);direct={pow(z,e,q):e for e in range(7)};row={};sy={}
        for ell,cs in GENERATORS.items():
            vals=[val(invbasis(cs),pow(theta,b,q),q) for b in range(1,7)];check(all(vals),'Ramification/test overlap')
            exps=[direct[pow(v,(q-1)//7,q)] for v in vals];nsym+=6;row[str(ell)]=(-sum(i*v for i,v in enumerate(exps,1)))%7;sy[str(ell)]={'values':vals,'log_mod7':exps}
        columns[q]={'q':q,'generator':g,'root':z,'rows':row,'symbols':sy}
    check([columns[q] for q in universe]==cert['columns'],'Changed twisted column');tests=[];theta_pairs={}
    for rec in pc['primes']:
        ell=rec['q'];cs=GENERATORS[ell];check(exact_norm(cs)==ell,'Wrong exact cyclotomic norm')
        roots=[t for t in range(2,ell) if pow(t,7,ell)==1 and val(invbasis(cs),t,ell)==0];check(len(roots)==1,'Cyclotomic prime not identified uniquely');theta=roots[0];z=pow(theta,-1,ell)
        radical=[x for x in range(ell) if x*x%ell==5];ph=sorted({(1+x)*pow(2,-1,ell)%ell for x in radical});check(len(ph)==2,'Test prime not split')
        def direct_symbol(v):
            t=pow(v%ell,(ell-1)//7,ell);return next(k for k in range(7) if pow(theta,(-k)%7,ell)==t)
        K=[[direct_symbol(x),direct_symbol(3),direct_symbol(2*x-1)] for x in ph];pairs=set()
        for rr in rec['rows']:
            if not rr['residual_pass']:continue
            P=rr['twisted_polynomial'];Q=rec['Q'];S=-P[3];N=P[2]-2*Q
            tn=S-2*(Q+1);nn=N-(Q+1)*S+(Q+1)**2;check(tn%7==0 and nn%49==0,'Nonintegral trace correction invariants');tr=tn//7%7;nm=nn//49%7
            pair=[x for x in range(49) if (2*(x%7)+x//7)%7==tr and ((x%7)**2+(x%7)*(x//7)-(x//7)**2)%7==nm]
            check(1<=len(pair)<=2,'Incorrect coefficient root set');pairs.add(tuple(sorted(pair)))
        theta_pairs[ell]=pairs;tests.append({'q':ell,'generator':list(cs),'norm':exact_norm(cs),'root':z,'phi_roots':ph,'kummer_rows':K,'paired_trace_sets':sorted([sorted(to_w(x) for x in pair) for pair in pairs])})
    check(tests==cert['tests'],'Changed common polynomial or Kummer data')
    initial=copy.deepcopy(old['survivors']);check(len(initial)==cert['initial_count']==2,'Wrong frozen candidate boundary');survivors=initial;stages=[]
    for t in tests:
        keep=[];rej=[];q=t['q']
        for s in survivors:
            b=sum(columns[p]['rows'][str(q)]*v for p,v in zip(s['columns'],s['inertia']))%7;alpha=[from_w(x) for x in s['alpha']]
            pp=[times(dot(row,alpha),b) for row in t['kummer_rows']];good=any(set(pp)<=set(pair) for pair in theta_pairs[q]);bad=all(x==0 for x in pp)
            e={'beta':b,'products':[to_w(x) for x in pp],'good_possible':good,'bad_possible':bad,'pass':good or bad}
            if e['pass']:
                c=copy.deepcopy(s);c['values'][str(q)]=b;keep.append(c)
            else:rej.append({'candidate':s,'evaluation':e})
        stages.append({'test':q,'before':len(survivors),'after':len(keep),'retained':sorted(keep,key=canon),'rejected':rej});survivors=keep
    check(stages==cert['stages'],'Changed complete sieve transcript');check(sorted(survivors,key=canon)==cert['survivors'] and len(survivors)==cert['count'],'Changed final survivors')
    out={'schema':'beal.block67.independent_filter.v1','status':'PASS_INDEPENDENT_FILTER','primary_arithmetic_imports':False,'direct_seventh_power_symbols':nsym,'norms_checked':len(tests),'all_conductor_columns':len(universe),'initial_candidates':2,'stages':[s['after'] for s in stages],'final_survivors':len(survivors),'basis':'inverse cyclotomic basis; theta^2-theta-1 coefficient field','scope':'Refinement of exact replayed predecessor list, not a general conductor bound'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(out['status'],out['stages'])
if __name__=='__main__':main()
