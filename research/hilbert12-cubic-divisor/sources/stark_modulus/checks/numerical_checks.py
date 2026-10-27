#!/usr/bin/env python3
"""Independent numerical regressions, NOT interval or algebraicity certificates.

Siegel products at omega, Gauss-sum algebraic coordinates, and the original
elliptic-gamma series are evaluated separately at 70 and 110 decimal digits.
The exact proof is in PROOF.md; no recognition algorithm occurs in this file.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import json, time, platform
import mpmath as mp

start=time.perf_counter();runs=[]
for digits in (70,110):
    mp.mp.dps=digits;w=mp.exp(2j*mp.pi/3); qabs=mp.exp(-2*mp.pi*w.imag)
    np=digits;ng=7000;tol=mp.power(10,-digits+12)
    tests=[]
    def num(a): return mp.mpf(a.numerator)/a.denominator if isinstance(a,F) else mp.mpf(a)
    def logg(a,b):
        a=num(a);b=num(b);a-=mp.floor(a);b-=mp.floor(b);z=a*w+b
        out=-mp.pi*w.imag*(a*a-a+mp.mpf(1)/6)
        out+=mp.log(abs(1-mp.exp(2j*mp.pi*z)))
        for n in range(1,np+1):
            out+=mp.log(abs(1-mp.exp(2j*mp.pi*(n*w+z))))
            out+=mp.log(abs(1-mp.exp(2j*mp.pi*(n*w-z))))
        return out
    def ck(name,got,want=0):
        err=abs(got-want);rel=err/max(1,abs(want))
        tests.append({'name':name,'absolute_error':mp.nstr(err,12),'relative_error':mp.nstr(rel,12)})
        if rel>=tol:raise AssertionError((name,mp.nstr(rel),mp.nstr(tol)))
    pairs=((1,13),(4,10),(16,19))
    logs=[sum(logg(F(-a,7),F(-a,21)) for a in pair) for pair in pairs]
    ell=[-2*l for l in logs]
    ck('sum of six ray zeta derivatives',sum(ell))
    b=mp.root(7,3)*w*w;eps=2-b;reg=-mp.log(2-mp.root(7,3))
    ck('unit regulator normalization',mp.log(abs(eps)),reg/2)
    char=(1,w,w*w,w*w,w,1)
    G=sum(char[a-1]*mp.exp(6j*mp.pi*a/7) for a in range(1,7));x=G/b
    J=2+3*w
    ck('Gauss cube',x**3,J)
    aa=((1+w)*x*x-x+1,-x*x+(1+w)*x+1,-w*x*x-w*x+1)
    for k in range(3):ck(f'CM Siegel product cubic norm {k}',3*logs[k],mp.log(abs(aa[k])))
    ck('algebraic a product',aa[0]*aa[1]*aa[2],1)
    ck('hexagonal Green rotation',logg(F(-3,7),F(-1,7)),logg(F(2,7),F(3,7)))
    f=[(-1)**h*(reg/6-ell[(h-1)%3]) for h in range(6)]
    def alg(x,w):
        nu=(x+b/x-b*b)/3;v=-b*b*nu-2*nu*nu
        AW=(21*b-42)*v*v+(-15*b*b+30*b)*v-b*b-4*b+11
        BW=3*b*b*v*v+(18*b-42)*v-11*b*b+13*b+7
        W=(AW+w*BW)/3
        Y=(4*b*b+b-14)*v*v+(11*b-23)*v-b*b+3*b-3
        Z=((-2*b*b+7*b-8)*v*v+(-10*b*b+11*b+17)*v)/3+7-b-b*b
        U=(Y-(1+2*w)*Z)/2
        return W,U
    W,U=alg(x,w);Ws=[];xs,ws=x,w
    for h in range(6):
        wh,uh=alg(xs,ws);Ws.append(wh)
        ck(f'exact W log formula h={h}',mp.log(abs(wh)),-3*f[(h+5)%6])
        xs,ws=ws*b/xs,ws*ws
    for h in range(6):ck(f'Stark normalization h={h}',-mp.log(abs(Ws[(h+1)%6]))/3,f[h])
    ck('algebraic smoothing',W**5/Ws[1],U**6)
    # Independent elliptic-gamma series. No algebraic value is used inside it.
    t=-(b*b+2*b)/15;s=-(b+2)/15;p=mp.exp(2j*mp.pi*t);q=mp.exp(2j*mp.pi*s)
    pn=qn=mp.mpc(1);acc=mp.mpc(0)
    for n in range(1,ng+1):
        pn*=p;qn*=q
        if n%5:acc+=(pn*w**(n%3)-qn*w**((-n)%3))/(n*(1-pn)*(1-qn))
    loggamma=-5*acc
    target=f[0]-5*f[5]
    ck('gamma modulus vs partial zeta target',2*loggamma.real,target)
    ck('gamma modulus vs algebraic candidate',loggamma.real,mp.log(abs(U)))
    ck('cubed modulus formula',3*loggamma.real,mp.log(abs(eps**3*aa[2]*aa[1]**5)))
    # Orthogonal analytic audit: conductor21 character rho vs class number formula.
    log0=[mp.mpf(0)]*3;infl=mp.mpc(0);counts=[0]*3
    exp4={1:0,4:1,2:2};exp2={1:0,2:1,4:2}
    for a in range(1,21,3):
        for b0 in range(0,21,3):
            rj=(a+4*b0)%7;rjb=(a+2*b0)%7
            if rj==0 or rjb==0:continue
            lg=logg(F(b0,21),F(a,21))
            k=(exp4[rj*rj%7]+exp2[rjb*rjb%7])%3
            log0[k]+=lg;counts[k]+=1
            infl+=-2*w**(2*exp4[rj*rj%7]%3)*lg
    ell0=[-2*l for l in log0]
    ck('rho derivative class number formula',sum(w**k*ell0[k] for k in range(3)),3*reg)
    ck('unwanted Euler factor annihilates lambda derivative',infl)
    # Deliberately wrong normalizations must be detected.
    assert abs(target/2-2*loggamma.real)>1
    wrong_shift=-mp.log(abs(W))/3
    assert abs(wrong_shift-f[0])>mp.mpf('0.1')
    phase=mp.exp(1j*mp.mpf('0.000001'))
    ck('phase perturbation preserves modulus',abs(phase),1)
    assert abs(phase**6-1)>mp.mpf('0.000005')
    # Truncation majorants are analytic estimates, not rounding enclosures.
    rp=mp.mpf(19)/20;rq=mp.mpf(3)/5;N=ng
    tail=5/((N+1)*(1-rp**(N+1))*(1-rq**(N+1)))*(rp**(N+1)/(1-rp)+rq**(N+1)/(1-rq))
    gtail=2*qabs**np/((1-qabs)*(1-qabs**np))
    runs.append({'digits':digits,'status':'PASS','equality_checks':len(tests),'tests':tests,
                 'negative_controls':['wrong factor2','unshifted W','unit-modulus phase not sixth root'],
                 'gamma_cutoff':ng,'Siegel_product_cutoff':np,
                 'gamma_log_tail_bound_without_rounding':mp.nstr(tail,15),
                 'each_Siegel_log_tail_bound_without_rounding':mp.nstr(gtail,15),
                 'ell':[mp.nstr(z,40) for z in ell],'partial_zeta_derivatives':[mp.nstr(z,40) for z in f],
                 'gamma_log_modulus_squared':mp.nstr(2*loggamma.real,45),
                 'max_relative_error':mp.nstr(max(mp.mpf(z['relative_error']) for z in tests),12),
                 'rho_conductor21_class_counts':counts})
result={'status':'PASS','runs':runs,'python':platform.python_version(),'mpmath':mp.__version__,
        'runtime_seconds':time.perf_counter()-start,
        'interpretation':'High-precision regression only. Not a rigorous rounding enclosure or a proof of the complex phase.'}
path=Path(__file__).resolve().parent.parent/'evidence'/'numerical_results.json'
path.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','runtime_seconds':result['runtime_seconds'],
                  'runs':[{k:v for k,v in r.items() if k!='tests'} for r in runs]},indent=2))
