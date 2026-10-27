#!/usr/bin/env python3
"""Exact finite checks; no claim of universal formal verification.
Boolean functions are integer truth tables, bit x is the value at x.
NOT/CNOT/Toffoli use distinct wires. All controls are positive.
"""
from __future__ import annotations
from pathlib import Path
from itertools import combinations
import argparse, json, random


def one(n): return (1 << (1 << n))-1

def variables(n):
    return [sum(((x>>i)&1)<<x for x in range(1<<n)) for i in range(n)]

def degree(f,n):
    a=[(f>>x)&1 for x in range(1<<n)]
    for i in range(n):
        for x in range(1<<n):
            if x&(1<<i): a[x]^=a[x^(1<<i)]
    return max((x.bit_count() for x,v in enumerate(a) if v),default=-1)

def monomials(n):
    return [sum((x&s==s)<<x for x in range(1<<n)) for s in range(1<<n)]

def immunity(f,n):
    """Return minimum degree of a nonzero h supported in f, and a witness."""
    if not f: return None,0
    neg=one(n)^f; mons=monomials(n)
    for d in range(n+1):
        eligible=[s for s in range(1<<n) if s.bit_count()<=d]
        basis={}
        for j,s in enumerate(eligible):
            col=mons[s]&neg; coeff=1<<j
            while col:
                p=col.bit_length()-1
                if p not in basis:
                    basis[p]=(col,coeff); break
                b,w=basis[p]; col^=b; coeff^=w
            if col==0:
                h=0
                for k,t in enumerate(eligible):
                    if coeff>>k&1: h^=mons[t]
                assert h and not (h&neg) and degree(h,n)==d
                return d,h
    raise AssertionError('point indicator must supply a witness')

def validate(ops,width):
    for g in ops:
        assert g[0] in ('N','C','T')
        assert len(g)=={'N':2,'C':3,'T':4}[g[0]]
        assert len(set(g[1:]))==len(g)-1
        assert all(0<=i<width for i in g[1:])

def step(g,v,mask):
    w=v.copy()
    if g[0]=='N': w[g[1]]^=mask
    elif g[0]=='C': w[g[2]]^=v[g[1]]
    else: w[g[3]]^=v[g[1]]&v[g[2]]
    return w

def trace(ops,v,mask):
    ans=[v.copy()]
    for g in ops: ans.append(step(g,ans[-1],mask))
    return ans

def dnf(n,f):
    gs=[]
    def gate(typ,a,b=None):
        gs.append((typ,a) if b is None else (typ,a,b))
        return n+len(gs)-1
    neg=[gate('NOT',i) for i in range(n)]
    terms=[]
    for x in range(1<<n):
        if not(f>>x&1): continue
        ls=[i if x>>i&1 else neg[i] for i in range(n)]
        t=ls[0]
        for a in ls[1:]: t=gate('AND',t,a)
        terms.append(t)
    if not terms: out=gate('AND',0,neg[0])
    else:
        out=terms[0]
        for t in terms[1:]:out=gate('OR',out,t)
    return gs,out

def compile_source(n,gs,out):
    ops=[]
    for j,g in enumerate(gs):
        t=n+j
        if g[0]=='NOT': ops.extend([('N',t),('C',g[1],t)])
        elif g[1]==g[2]:ops.append(('C',g[1],t))
        elif g[0]=='AND':ops.append(('T',g[1],g[2],t))
        else:ops.extend([('C',g[1],t),('C',g[2],t),('T',g[1],g[2],t)])
    y=n+len(gs); ans=ops+[('C',out,y)]+ops[::-1]
    validate(ans,y+1)
    return ans,y+1,y

def monomial_oracle(n):
    if n==2:return [('T',0,1,n)],n+1,n
    anc=list(range(n,2*n-2)); y=2*n-2
    p=[('T',0,1,anc[0])]
    for i in range(2,n-1):p.append(('T',anc[i-2],i,anc[i-1]))
    ops=p+[('T',anc[-1],n-1,y)]+p[::-1]
    return ops,y+1,y

def check_circuit(n,ops,width,y,f,alpha,full_degrees=True):
    validate(ops,width); mask=one(n)
    z=variables(n)+[0]*(width-n); z[y]=0
    o=z.copy();o[y]=mask
    az=trace(ops,z,mask);ao=trace(ops,o,mask)
    rz=trace(ops[::-1],z,mask);ro=trace(ops[::-1],o,mask)
    end=z.copy();end[y]=f
    assert az[-1]==end
    end[y]^=mask; assert ao[-1]==end
    tc=[0]
    for g in ops:tc.append(tc[-1]+(g[0]=='T'))
    T=tc[-1]; count=0; covector_checks=0
    lam=[0]*width;lam[y]=mask
    cached={}
    def deg(h):
        if h not in cached: cached[h]=degree(h,n)
        return cached[h]
    for j in range(len(ops)+1):
        A=az[j];B=rz[len(ops)-j]
        D=[u^v for u,v in zip(A,ao[j])]
        E=[u^v for u,v in zip(B,ro[len(ops)-j])]
        assert D==E
        H=[u^v for u,v in zip(A,B)]
        union=0; normalizer=0
        for h,d,l in zip(H,D,lam):
            assert h==(f&d)
            union|=h;normalizer^=l&d
        assert union==f and normalizer==mask
        # The covector simultaneously reconstructs the comparison.
        rebuilt=0
        for h,l in zip(H,lam):rebuilt^=h&l
        assert rebuilt==f
        if full_degrees:
            cap=max(tc[j],T-tc[j])+1
            assert all(deg(h)<=cap for h in H)
            if f:
                assert any(H)
                assert all(not h or deg(h)>=alpha for h in H)
                if abs(2*tc[j]-T)<=1:
                    assert alpha<=cap and T>=2*alpha-3
        count+=1;covector_checks+=width
        if j==len(ops):break
        g=ops[j]
        # Boolean secant matrix inverse transport; endpoints before the gate.
        if g[0]=='C':
            a,t=g[1:];lam[a]^=lam[t]
        elif g[0]=='T':
            a,b,t=g[1:]; lt=lam[t]
            lam[a]^=lt & ao[j][b]
            lam[b]^=lt & az[j][a]
    return count,covector_checks,T

def main(out):
    out.mkdir(parents=True,exist_ok=True)
    report={'status':'PASS','domain':'exact F2/Boolean integers','seed':20260921}
    rows=[]; brute=0; allfun=0
    cache={}
    for n in range(1,4):
        for f in range(1<<(1<<n)):
            a,h=immunity(f,n);cache[n,f]=a
            best=None;sub=f
            while sub:
                d=degree(sub,n);best=d if best is None else min(best,d)
                sub=(sub-1)&f;brute+=1
            assert a==best
            allfun+=1
    report['one_sided_immunity']={'all_functions_through_3_inputs':allfun,'nonzero_supported_functions_exhausted':brute}
    mono=0
    for f in range(1<<16):
        monotone=all(not(f>>x&1) or all(f>>(x|1<<i)&1 for i in range(4)) for x in range(16))
        if not monotone:continue
        a,h=immunity(f,4)
        expected=min((x.bit_count() for x in range(16) if f>>x&1),default=None)
        assert a==expected
        mono+=1
    report['monotone_ideal_identity']={'all_monotone_functions_on_4_inputs':mono}
    rng=random.Random(20260921)
    circuits=cuts=cov=scalar=active=0
    for n in range(1,4):
        for f in range(1<<(1<<n)):
            gs,o=dnf(n,f);ops,w,y=compile_source(n,gs,o)
            ans=check_circuit(n,ops,w,y,f,cache[n,f]);cuts+=ans[0];cov+=ans[1];circuits+=1
            # Separate scalar evaluator: exhaust every x and both target bits.
            for x in range(1<<n):
                for bit in (0,1):
                    v=[x>>i&1 for i in range(n)]+[0]*(w-n);v[y]=bit
                    got=trace(ops,v,1)[-1];want=v.copy();want[y]^=f>>x&1
                    assert got==want;scalar+=1
            if n==3 and f%13==0:
                at=len(ops)//2; ex=[]
                for z in range(7):
                    a,b,t=rng.sample(range(w),3)
                    ex.append(('T',y,b,t) if len({y,b,t})==3 else ('T',a,b,t))
                decorated=ops[:at]+ex+ex[::-1]+ops[at:]
                ans=check_circuit(n,decorated,w,y,f,cache[n,f]);cuts+=ans[0];cov+=ans[1];circuits+=1;active+=1
    # Nontrivial output-active cubic using one borrowed bit; all values of that bit are logical inputs.
    ops=[('T',0,1,3),('T',3,2,4),('T',0,1,3),('T',3,2,4)]
    f=variables(4)[0]&variables(4)[1]&variables(4)[2]
    a,_=immunity(f,4)
    ans=check_circuit(4,ops,5,4,f,a);cuts+=ans[0];cov+=ans[1];circuits+=1
    mon=[]
    for n in range(2,11):
        ops,w,y=monomial_oracle(n);f=1<<((1<<n)-1)
        ans=check_circuit(n,ops,w,y,f,n);cuts+=ans[0];cov+=ans[1];circuits+=1
        assert ans[2]==2*n-3
        mon.append({'n':n,'Toffolis':ans[2],'proven_unrestricted_minimum':2*n-3})
    report['restored_oracles']={'circuits':circuits,'identity_loop_output_active_variants':active,'all_gate_cuts':cuts,'coordinate_covector_checks':cov,'independent_scalar_input_target_cases':scalar,'conventions':'all inputs and both target values; finite selected circuits, not exhaustive circuit search'}
    report['monomial_calibration']=mon
    # Elementary secant identity, independently over every pair of 3-wire states and every gate.
    elementary=0
    gates=[('N',i) for i in range(3)]+[('C',a,t) for a in range(3) for t in range(3) if a!=t]+[('T',a,b,t) for a in range(3) for b in range(3) for t in range(3) if len({a,b,t})==3]
    for g in gates:
        for x in range(8):
            for z in range(8):
                u=[x>>i&1 for i in range(3)];v=[z>>i&1 for i in range(3)];d=[a^b for a,b in zip(u,v)]
                mapped=d.copy()
                if g[0]=='C':mapped[g[2]]^=d[g[1]]
                elif g[0]=='T':
                    a,b,t=g[1:];mapped[t]^=(v[b]&d[a])^(u[a]&d[b])
                actual=[a^b for a,b in zip(step(g,u,1),step(g,v,1))]
                assert mapped==actual;elementary+=1
    report['local_secant']={'all_gate_endpoint_pairs_on_3_wires':elementary,'shared_multiplication_bound':'2T endpoint evaluations + 2T covector propagation = 4T; no exponential coefficient expansion'}
    (out/'cut_comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=Path(__file__).resolve().parents[1]/'results');main(p.parse_args().out)
