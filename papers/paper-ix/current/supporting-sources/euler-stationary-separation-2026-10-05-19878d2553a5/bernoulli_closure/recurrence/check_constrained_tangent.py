#!/usr/bin/env python3
"""Actual Bernoulli tangent and independent neighboring-index contact checks."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate'
sys.path.insert(0,str(SRC))
import fast_parameter_certificate as old
b=old.base
P=320

def record(x,p):
    x%=1<<p;v=b.v2(x,p)
    return {'valuation_or_bound':v,'is_lower_bound':v==p,
            'unit_mod8':((x>>v)%8 if v+3<=p else None)}

def main(output):
    # Recurrence-compatible variation is checked independently in exact Q[v].
    aa=[F(1),F(1,3)]
    for n in range(2,25):aa.append(-sum(aa[i]*aa[n-i] for i in range(1,n))/(2*n+1))
    for scale in [F(1),F(3),F(5,9)]:
        av=[aa[n]*scale**n for n in range(25)]
        for n in range(1,25):
            assert (2*n+1)*av[n]==(scale if n==1 else -sum(av[i]*av[n-i] for i in range(1,n)))
    b.B=b.bernoullis(max(256,P));b.twoB=old.fast_twoB
    source=list(b.source(P));M=1<<P
    results=[]
    for T in [0,718787533,22831001499602523078606181325]:
        start=time.monotonic();r=(17659+(1<<18)*T)*(1<<640)-161
        costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range((r.bit_count()-1)//3+1)]
        assert min(costs)==-154 and max(q for q,v in enumerate(costs) if v==-154)==161
        Q=(P+r.bit_count()-156)//3;gam=b.gamma(r,-154,P,Q)
        assert (gam[2]>>157)%8==1
        def local(g,c):
            lo,hi=old.local_split(P,c,15,g,source)
            return[(a+bb)%M for a,bb in zip(lo,hi)]
        gg=local(gam,10202);K=[v>>178 for v in gg]
        assert all(v%(1<<178)==0 for v in gg)
        assert all(i*K[i]%2==0 for i in range(1,len(K)))
        qhalf=[i*K[i]//2 for i in range(1,len(K))]
        c=0
        for j in range(P-179):
            if b.ev(qhalf,c,1<<(j+1)):c+=1<<j
        assert c%128==20
        x=10202+(1<<15)*c
        vv=local([(q*v)%M for q,v in enumerate(gam)],10202)
        ww=local([(q*(q-1)*v)%M for q,v in enumerate(gam)],10202)
        vv0=b.ev(vv,c,M);vv1=b.ev(b.deriv(vv),c,M);ww0=b.ev(ww,c,M)
        assert vv0%(1<<154)==vv1%(1<<154)==ww0%(1<<130)==0
        kv=vv0>>154;kzv=vv1>>154;kvv=ww0>>130
        kzz=b.ev(b.deriv(b.deriv(K)),c,1<<120)
        N=100;m=1<<N
        correction=(kzv*kzv//2)*pow((kzz//2)%m,-1,m)%m
        phipp=(kvv-correction)%m
        cp=-(kzv//2)*pow((kzz//2)%m,-1,m)%m
        obs={name:record(value,N) for name,value in
             [('K_xi',kv),('K_Zxi',kzv),('K_xixi',kvv),
              ('center_xi',cp),('motion_correction',correction),('Phi_xixi',phipp)]}
        expected={'K_xi':(0,3),'K_Zxi':(16,7),'K_xixi':(29,7),
                  'center_xi':(15,1),'motion_correction':(31,1),'Phi_xixi':(29,3)}
        for name,(v,u) in expected.items():
            assert obs[name]['valuation_or_bound']==v and obs[name]['unit_mod8']==u,(name,obs[name])
        # Independent actual-r+1 packet construction, not solving identity (5).
        rp=r+1
        neighbor_costs=[3*q+(rp+q).bit_count()-rp.bit_count()
                        for q in range((rp.bit_count()-1)//3+1)]
        assert min(neighbor_costs)==-153
        assert max(q for q,v in enumerate(neighbor_costs) if v==-153)==160
        Qp=(P+rp.bit_count()-155)//3
        gp=b.gamma(rp,-153,P,Qp);neighbor=local(gp,10201)
        f=b.ev(neighbor,c,M)
        dfz=b.ev(b.deriv(neighbor),c,M)
        assert dfz%(1<<15)==0
        df=dfz>>15
        assert b.v2(f,P)==153 and b.v2(df,P-15)==152
        aval=b.ev(source,x,M);ader=b.ev(b.deriv(source),x,M)
        pp=x*(2*x-1);dp=4*x-1;u=gam[1]>>153
        gval=b.ev(gg,c,M)
        assert (gval-(1<<154)*aval-u*pp*f)%M==0
        J=140;mm=1<<J
        # Evaluate 2L to avoid dividing a nonintegral term. The two derivative
        # ratios individually have valuation -1, while their mismatch is tiny.
        twoL=(2*ader*pow(aval,-1,mm)-dp*pow((pp//2)%mm,-1,mm)
              -(df>>152)*pow((f>>153)%mm,-1,mm))%mm
        phi=b.ev(K,c,1<<(P-178))
        phiv=b.v2(phi,P-178)
        assert phiv<P-178 and b.v2(twoL,J)==phiv+26
        # Exact source-controlled expression for the same mismatch at stationarity.
        den=(gval-(1<<154)*aval)%M
        ratio=(gval>>154)*pow((den>>154)%mm,-1,mm)%mm
        predicted=2*ader*pow(aval,-1,mm)*ratio%mm
        assert twoL==predicted
        results.append({'T':str(T),'r':str(r),'terminal':161,'neighbor_terminal':160,
                        'stationary_Z_bits':P-179,'stationary_Z':str(c),
                        'normal_direction':obs,'critical_value_valuation':phiv,
                        'adjacent_log_contact_valuation':phiv+25,
                        'independent_neighbor_value':record(f>>153,140),
                        'independent_neighbor_derivative':record(df>>152,140),
                        'seconds':time.monotonic()-start})
    result={'status':'passed','base_checkpoint':'Euler-radix-audit-20261005',
            'global_bits':P,'stationary_bits':P-179,'normal_certificate_output_bits':100,
            'adjacent_log_contact_bits':140,'recurrence_scale_checks':72,'cases':results,
            'nonclaims':['No actual critical-value nonvanishing theorem',
                         'No parameter search or new multiplier digits','No Lean compilation',
                         'The normal scale family is larger than the specified Euler member']}
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in c.items() if k not in ('r','stationary_Z')} for c in results],indent=2))

if __name__=='__main__':main(sys.argv[1])
