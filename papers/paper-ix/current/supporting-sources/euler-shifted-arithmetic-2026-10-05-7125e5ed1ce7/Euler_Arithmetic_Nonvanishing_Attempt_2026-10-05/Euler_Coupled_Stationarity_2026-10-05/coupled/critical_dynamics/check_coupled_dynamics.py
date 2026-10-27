#!/usr/bin/env python3
"""Exact finite audit of coupled stationary motion and cancellation.

Reads certified actual-Euler epsilon jets. This is a derivative and movement
check, not an extension of the integer-parameter precision range.
"""
from pathlib import Path
from fractions import Fraction
from math import comb
import argparse, hashlib, json, time, platform

ROOT=Path(__file__).resolve().parents[2]
JETS=ROOT/'next/unit_identity/run_272/results.json'
OLD=ROOT/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate/fast_certificate_629.json'

def val(a,P=1000000):return P if not a else (abs(a)&-abs(a)).bit_length()-1
def ev(p,x,M):
    r=0
    for a in reversed(p):r=(r*x+a)%M
    return r
def der(p):return [i*p[i] for i in range(1,len(p))]
def modfrac(q,M):return q.numerator*pow(q.denominator,-1,M)%M
def derive(j,dz=0,de=0):
    out=[r[:] for r in j]
    for _ in range(dz):out=[der(r) for r in out]
    for _ in range(de):out=[[m*a for a in out[m]] for m in range(1,len(out))]
    return out
def ev2(j,e,z,M):return ev([ev(row,z,M) for row in j],e,M)

def run():
    started=time.monotonic()
    old=json.loads(OLD.read_text()); H0=list(map(int,old['H0']));H1=list(map(int,old['H1']))
    assert [a%256 for a in H0]==[215,72,107]+[0]*(len(H0)-3)
    assert [a%256 for a in H1]==[189]+[0]*(len(H1)-1)
    assert val(H0[3])==8 and val(H1[3])==42
    assert [a*pow(251,-1,256)%256 for a in (215,72,107,189)]==[213,88,81,167]

    # Independent exact rational source/Bernoulli calculation at low precision.
    Ds=[]
    for m in (31,32):
        D=Fraction(1-2*m)+Fraction(2,3)*comb(2*m,2)-Fraction(8,15)*comb(2*m,4)+Fraction(32,21)*comb(2*m,6)
        Ds.append(modfrac(D,64))
    assert Ds==[13,1]
    u=Ds[1]*pow(Ds[0]*((-323)*(-5)), -1,64)%64
    assert u==43
    # Newton source numerator modulo128 is 1+36x+32x^2+64x^3.
    n=[1,36,32,64]; A=[]
    for i in range(7):A.append(((n[i] if i<len(n) else 0)-2*(A[-1] if A else 0))%128)
    assert A==[1,34,92,8,112,32,64]
    x=10202
    log9over4=modfrac(sum((Fraction((-1)**(h+1)*8**h,4*h) for h in range(1,7)),Fraction(0)),128)
    ap=ev(der(A),x,128); q1=u*log9over4*pow(9,x,128)%128
    assert (ap,q1,(ap+q1)%128)==(50,94,16)
    records=[]
    for rec in json.loads(JETS.read_text())['records']:
        jet=[list(map(int,row)) for row in rec['jet']]
        P=rec['local_coefficient_bits'];N=P-1; M=1<<P;m=1<<N
        dz=derive(jet,dz=1);dzz=derive(jet,dz=2);dzzz=derive(jet,dz=3)
        de=derive(jet,de=1);dee=derive(jet,de=2)
        dze=derive(jet,dz=1,de=1);dzee=derive(jet,dz=1,de=2);dzze=derive(jet,dz=2,de=1)
        qjet=[[(i*row[i]//2)%m for i in range(1,len(row))] for row in jet]

        def critical(e):
            c=0
            for k in range(N):
                if ev2(qjet,e,c,1<<(k+1)):c+=1<<k
            assert ev2(qjet,e,c,m)==0
            return c

        def state(e):
            c=critical(e); hess=ev2(dzz,e,c,M);mix=ev2(dze,e,c,M)
            assert val(hess)==1 and val(mix)==19
            hi=pow(hess//2,-1,m)
            cp=-(mix//2)*hi%m
            direct=ev2(dee,e,c,M)
            motion=(mix//2)*mix*hi%m
            phipp=(direct-motion)%m
            terms=[ev2(dzee,e,c,M),2*ev2(dzze,e,c,M)*cp%M,ev2(dzzz,e,c,M)*cp*cp%M]
            numerator=sum(terms)%M
            cpp=-(numerator//2)*hi%m
            phip=ev2(de,e,c,m);phi=ev2(jet,e,c,m)
            assert c%128==20
            assert val(cp,N)==18 and (cp>>18)%8==7
            assert val(cpp,N)==40 and (cpp>>40)%8==3
            assert phip%32==17
            assert val(phipp,N)==27 and (phipp>>27)%8==1
            assert val(direct,P)==27 and val(motion,N)==37
            assert list(map(val,terms))==[41,44,45]
            return {'c':c,'phi':phi,'cp':cp,'cpp':cpp,'phip':phip,'phipp':phipp}

        st=[];eta_star=int(rec['eta_star_residue'])
        for theta in (0,1,3,eta_star):
            a=state(theta)
            for h in (1,2,4,8,1<<12):
                bb=state(theta+h);vh=val(h)
                dc=(bb['c']-a['c'])%m;dp=(bb['phi']-a['phi'])%m
                ec=(dc-h*a['cp'])%m;ep=(dp-h*a['phip'])%m
                assert val(dc,N)==18+vh and val(dp,N)==vh
                assert val(ec,N)==39+2*vh and (ec>>(39+2*vh))%8==3
                assert val(ep,N)==26+2*vh and (ep>>(26+2*vh))%8==1
                st.append({'theta':str(theta),'h':h,'center_motion_valuation':val(dc,N),
                           'critical_value_motion_valuation':val(dp,N),
                           'center_chord_error_valuation':val(ec,N),
                           'value_chord_error_valuation':val(ep,N)})
        records.append({'integer_T':rec['integer_T'],'local_coefficient_bits':P,
                        'critical_precision_bits':N,'parameter_derivative_checks':24,
                        'chord_checks':st})
    return {'status':'passed','runtime_seconds':time.monotonic()-started,
            'python':platform.python_version(),'integer_T_cases':[0,718787533],
            'source_cancellation_mod128':{'source_derivative':ap,'q1_derivative':q1,'sum':(ap+q1)%128},
            'Bernoulli_u_mod64':u,'records':records,
            'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (JETS,OLD)},
            'nonclaims':['No additional integer-parameter precision','No universal Euler nonintersection','No Lean compilation']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
    r=run();Path(a.out).write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:v for k,v in r.items() if k!='records'},indent=2))
