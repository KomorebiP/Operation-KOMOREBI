#!/usr/bin/env python3
"""Actual source-free tails, exterior pairing, and independent contact center."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,time
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate'
sys.path.insert(0,str(SRC))
import fast_parameter_certificate as old
b=old.base
P=384;M=1<<P;DEPTH=15;DEG=(P-1)//DEPTH;BITS=200;MOD=1<<BITS

def add(a,c,sign=1,mod=M):
    return [((a[i] if i<len(a) else 0)+sign*(c[i] if i<len(c) else 0))%mod for i in range(max(len(a),len(c)))]

def scaled(a,k,mod=M):return [k*x%mod for x in a]

def log9(bits):return sum((-1)**(n+1)*b.fmod(F(8**n,n),bits) for n in range(1,bits+1))%(1<<bits)

def rec(a,bits=BITS):
    a%=1<<bits;v=b.v2(a,bits)
    return {'valuation_or_bound':v,'is_lower_bound':v==bits,'unit_mod8':(a>>v)%8 if v+3<=bits else None}

def critical(poly,bits):
    assert poly[1]%2 and all(x%2==0 for x in poly[2:])
    z=0
    for k in range(bits):
        if b.ev(poly,z,1<<(k+1)):z+=1<<k
    return z

def main(output):
    started=time.monotonic();b.B=b.bernoullis(P);b.twoB=old.fast_twoB
    A=list(b.source(P));L=log9(BITS)
    Q=[(10202+1)*(2*10202+1),(4*10202+3)*(1<<DEPTH),2*(1<<(2*DEPTH))]
    records=[]
    for T in [0,718787533,22831001499602523078606181325]:
        r=(17659+(1<<18)*T)*(1<<640)-161
        costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range((r.bit_count()-1)//3+1)]
        assert min(costs)==-154 and max(q for q,v in enumerate(costs) if v==-154)==161
        cutoff=(P+r.bit_count()-156)//3;gam=b.gamma(r,-154,P,cutoff)
        lo,hi=old.local_split(P,10202,DEPTH,gam,A);G=add(lo,hi)
        assert all(a%(1<<178)==0 for a in G)
        K=[a>>178 for a in G];assert all(i*K[i]%2==0 for i in range(1,len(K)))
        c=critical([i*K[i]//2 for i in range(1,len(K))],P-179)
        phi=b.ev(K,c,1<<(P-178));vp=b.v2(phi,P-178)
        assert vp=={0:0,718787533:30,22831001499602523078606181325:91}[T]
        # Build both source-free tails directly, with no use of G in this step.
        U=[gam[0]]+[0]*DEG;V=U[:];pq=[1];special={0:([gam[0]],[0])}
        for q in range(1,cutoff+1):
            term=scaled(b.mul(Q,pq,M)[:DEG+1],gam[q])
            U=add(U,scaled(term,pow(pow(9,q,M),-1,M)));V=add(V,term)
            if q in (1,161):special[q]=(term,b.deriv(term))
            i=q-1
            pq=old.linmul(pq,10202-i,1<<DEPTH,DEG,M)
            pq=old.linmul(pq,2*10202-2*i-1,1<<(DEPTH+1),DEG,M)
        assert all(x%(1<<153)==0 for x in U+V)
        u=[x>>153 for x in U];v=[x>>153 for x in V]
        assert all(x%(1<<14)==0 for x in b.deriv(u)+b.deriv(v))
        du=[x>>14 for x in b.deriv(u)];dv=[x>>14 for x in b.deriv(v)] # twice physical x derivative
        geometric=add(b.mul(u,dv,MOD),b.mul(du,v,MOD),-1,MOD)
        logarithmic=scaled(b.mul(u,v,MOD),2*L,MOD)
        exterior=add(geometric,logarithmic,-1,MOD)
        assert all(x%(1<<15)==0 for x in exterior)
        J=[x>>15 for x in exterior];assert J[1]%8==7
        zeta=critical(J,BITS-15)
        assert zeta%128==c%128==20
        separation=b.v2(zeta-c,BITS-15);assert separation==13+vp
        x=10202+(1<<DEPTH)*c
        uv=b.ev(u,c,MOD);vv=b.ev(v,c,MOD);duv=b.ev(du,c,MOD);dvv=b.ev(dv,c,MOD)
        assert uv%8==vv%8==7
        two_mismatch=(2*L+duv*pow(uv,-1,MOD)-dvv*pow(vv,-1,MOD))%MOD
        source_value=(pow(9,x+1,MOD)*uv*pow(vv,-1,MOD)-1)%MOD
        qval=b.ev(Q,c,MOD);qprime=(4*x+3)%MOD
        two_C=(2*qprime*pow(qval,-1,MOD)-dvv*pow(vv,-1,MOD))%MOD
        assert two_C%8==7
        assert b.v2(source_value,BITS)==b.v2(two_mismatch,BITS)==28+vp
        assert (two_mismatch-two_C*source_value*pow(1+source_value,-1,MOD))%MOD==0
        # Independent source-elimination identity at the actual stationary center.
        gvalue=b.ev(G,c,M)
        assert (source_value-(8*qval*(gvalue>>153))*pow(vv,-1,MOD))%MOD==0
        # Exact exterior pair contributions after division by2^306 and doubling.
        jets={}
        for q,(term,der) in special.items():
            val=b.ev(term,c,M);dd=b.ev(der,c,M)
            assert val%(1<<153)==0 and dd%(1<<167)==0
            jets[q]=(val>>153,dd>>167)
        def pair(i,j):
            wi=pow(pow(9,i,MOD),-1,MOD);wj=pow(pow(9,j,MOD),-1,MOD)
            ai,di=jets[i];aj,dj=jets[j]
            return (wi-wj)*(ai*dj-di*aj)%MOD
        p0161=pair(0,161);p01=pair(0,1)
        gg=b.ev(geometric,c,MOD);ll=b.ev(logarithmic,c,MOD);ww=b.ev(exterior,c,MOD)
        assert rec(p0161)['valuation_or_bound']==4 and rec(p0161)['unit_mod8']==3
        assert rec(p01)['valuation_or_bound']==5 and rec(p01)['unit_mod8']==1
        assert b.v2(gg-p0161-p01,BITS)>=8
        assert rec(gg)['valuation_or_bound']==rec(ll)['valuation_or_bound']==4
        assert rec(gg)['unit_mod8']==rec(ll)['unit_mod8']==5
        assert b.v2(ww,BITS)==28+vp
        assert ((ww>>(28+vp))-(phi>>vp))%8==0
        zz=10202+(1<<DEPTH)*zeta
        uzz=b.ev(u,zeta,MOD);vzz=b.ev(v,zeta,MOD)
        Fz=(pow(9,zz+1,MOD)*uzz*pow(vzz,-1,MOD)-1)%MOD
        assert b.v2(Fz,BITS)==28+vp
        records.append({'T':str(T),'terminal':161,'critical_value_valuation':vp,
            'critical_Z_bits':P-179,'contact_Z_bits':BITS-15,
            'critical_Z':str(c),'contact_Z':str(zeta),
            'center_distance_valuation':separation,'twice_C':rec(two_C),
            'twice_log_mismatch':rec(two_mismatch),'source_value_at_contact_center':rec(Fz),
            'pair_0_161':rec(p0161),'pair_0_1':rec(p01),
            'geometric_term':rec(gg),'logarithmic_term':rec(ll),
            'complete_exterior':rec(ww),
            'exterior_raw_valuation':305+b.v2(ww,BITS)})
    result={'status':'passed','global_bits':P,'exterior_bits_after_normalizing_UV':BITS,
        'records':records,'seconds':time.monotonic()-started,
        'nonclaims':['No Euler counterexample','No universal critical nonvanishing','No new parameter digits','No omitted logarithmic term or derivative commutator','Only the fixed three ordinary multipliers are computed']}
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'passed','records':[{k:v for k,v in row.items() if k not in ('critical_Z','contact_Z')} for row in records]},indent=2))
if __name__=='__main__':main(sys.argv[1])
