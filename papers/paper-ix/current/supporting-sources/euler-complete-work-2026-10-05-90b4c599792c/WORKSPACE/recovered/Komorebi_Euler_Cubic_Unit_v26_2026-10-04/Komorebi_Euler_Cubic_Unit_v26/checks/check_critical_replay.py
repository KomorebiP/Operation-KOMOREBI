#!/usr/bin/env python3
"""Independent routes for the two retained actual-index stationary-value tests.
Higher precision, a logarithmic source, a rising-factorial scalar formula,
Horner rather than binomial localization, and Newton rather than bitwise critical lifting.
The Bernoulli modular evaluator is shared and that limitation is recorded.
This is bounded arithmetic corroboration, not a universal simplicity proof.
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, time
from fractions import Fraction
from pathlib import Path
import check_critical_value as base


def log_source(P: int) -> list[int]:
    mod=1<<P
    # log(9)/8. Every omitted index q>P has valuation at least 2q.
    lu=sum(base.fmod(Fraction((-8)**q,q+1),P) for q in range(P+1))%mod
    num=[0]*P
    for q in range(P+1):
        c=Fraction(8**q,math.factorial(q+1))
        if base.v2(c.numerator)-base.v2(c.denominator)>=P:continue
        scalar=base.fmod(c,P)*pow(lu,q+1,mod)%mod
        for i in range(min(q+1,P)):
            num[i]=(num[i]+scalar*math.comb(q,i))%mod
    return base.mul(num,[pow(-2,i,mod) for i in range(P)],mod)[:P]


def gamma_rising(r: int,mu: int,P: int,Q: int) -> list[int]:
    mod=1<<P;bb=pow(base.twoB(2*r,P),-1,mod);odd=1;v=0;out=[]
    for q in range(Q+1):
        if q:
            n=r+q;vn=base.v2(n);v+=vn
            odd=odd*(n>>vn)*(2*r+2*q-3)%mod
        exponent=4*q-mu-v
        if exponent<0:raise ValueError('nonintegral normalized packet')
        out.append(0 if exponent>=P else
                   (base.twoB(2*r+2*q,P)*bb*pow(odd,-1,mod)*(1<<exponent))%mod)
    return out


def reconstruct_alt(r: int,mu: int,P: int) -> list[int]:
    mod=1<<P;Q=(P+r.bit_count()+mu-2)//3
    g=gamma_rising(r,mu,P,Q);A=log_source(P);out=[0]*(P+2*Q);packet=[1]
    for q,scalar in enumerate(g):
        if q:
            i=q-1
            # A single quadratic factor differs from the generator's two linear products.
            packet=base.mul(packet,[i*(2*i+1),-(4*i+1),2],mod)
        if not scalar:continue
        Aq=[sum(A[n]*math.comb(n,d)*pow(-q,n-d,mod) for n in range(d,len(A)))%mod
            for d in range(len(A))]
        term=base.mul(packet,Aq,mod)
        for n,c in enumerate(term):out[n]=(out[n]+scalar*c)%mod
    return out


def newton_half_slope(F:list[int],P:int) -> tuple[int,int]:
    mod=1<<P;Q=[((i*F[i])//2)%mod for i in range(1,len(F))];D=base.deriv(Q)
    c=Q[0]%2;steps=0
    while base.ev(Q,c,mod):
        dc=base.ev(D,c,mod)
        if not dc%2:raise AssertionError('derivative not a unit')
        c=(c-base.ev(Q,c,mod)*pow(dc,-1,mod))%mod;steps+=1
        if steps>P+2:raise AssertionError('Newton failed to stabilize')
    return c,steps


def run(output:Path) -> None:
    if output.exists():raise FileExistsError(output)
    start=time.time();rows=[];checks=0
    prior=json.loads((Path(__file__).resolve().parents[1]/'evidence/v24_checks_actual.json').read_text())
    prior={r['label']:r for r in prior['actual_cases']}
    P=256;mod=1<<P
    assert log_source(P)==list(base.source(P));checks+=P
    for label,b,a in [('terminal129-first-representative',4045,7528),
                      ('terminal129-second-representative',44797,2920)]:
        r=b*(1<<515)-129
        G,mu,j=base.residual(r,P)
        alt=reconstruct_alt(r,mu,P)
        assert G==alt;checks+=len(G)
        k=15
        loc_bin=base.local(G,a,k,P)
        shifted=base.shift(alt,a,mod)
        loc_horner=[(c<<(k*n))%mod for n,c in enumerate(shifted) if k*n<P]
        assert loc_bin==loc_horner;checks+=len(loc_bin)
        content=min(base.v2(c,P) for c in loc_horner)
        assert content==147;checks+=1
        F=[c>>content for c in loc_horner];p=P-content-1
        assert F[1]%2==0 and F[2]%2==1 and all(c%4==0 for c in F[3:]);checks+=1
        cn,steps=newton_half_slope(F,p)
        cb,Q=base.lift_critical(F,p)
        assert cn==cb;checks+=1
        value=base.ev(F,cn,1<<p)
        old=prior[label]['result'];oldP=old['P']
        assert cn%(1<<oldP)==int(old['critical_center_residue']);checks+=1
        assert value%(1<<oldP)==int(old['critical_value_residue']);checks+=1
        # Check the stationary valuation identity by evaluation at many residue representatives.
        for y in range(64):
            diff=(base.ev(F,y,1<<p)-value)%(1<<p)
            assert base.v2(diff,p)==min(p,2*base.v2(base.ev(Q,y,1<<p),p));checks+=1
        rows.append({'label':label,'r':str(r),'mu':mu,'terminal':j,'global_P':P,
                     'argument_residue':a,'argument_depth':k,'content':content,
                     'normalized_coefficient_precision':P-content,'critical_precision':p,
                     'critical_center_residue':str(cn),'critical_value_residue':str(value),
                     'critical_value_valuation':base.v2(value,p),'newton_steps':steps,
                     'local_coefficients_mod_2power':[str(c) for c in F]})
    report={'status':'passed','independent_comparisons':checks,'actual_cases':rows,
            'seconds':time.time()-start,'python':platform.python_version(),
            'shared_components':['modular Bernoulli evaluator','generic polynomial convolution'],
            'independent_routes':['logarithmic source vs Newton source',
              'Pochhammer rising-factorial scalar vs paired-factorial scalar',
              'direct binomial source translation vs Horner source translation',
              'Horner local substitution vs direct binomial local substitution',
              'Newton critical lifting vs bitwise Hensel lifting'],
            'nonclaims':['No family-wide critical scalar nonvanishing',
                        'The numerical residues are not exact ordinary critical points',
                        'No new Lean proof of these numerical coefficient residues'],
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    run(ap.parse_args().output)
