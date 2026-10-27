#!/usr/bin/env python3
"""Named discriminator: derivative/shift commutator on actual Euler packets.

No parameter search. The two ordinary multipliers were fixed in earlier runs.
The complete operator sums modulo 2^180 use q<10, with proven omitted-tail
valuation at least181. Actual G and G' are separately rebuilt on each shift.
"""
from pathlib import Path
from fractions import Fraction
from math import factorial
import argparse, hashlib, json, platform, sys, time

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate'
sys.path.insert(0,str(SRC))
import fast_parameter_certificate as old
b=old.base
P=210
OUT_BITS=180
QOP=9

def rational_kernels(N):
    ds=[Fraction(2**(2*n+1),factorial(2*n+2)) for n in range(N+1)]
    beta=[Fraction(1)]
    for n in range(1,N+1):
        beta.append(-sum(ds[i]*beta[n-i] for i in range(1,n+1)))
    return beta,[beta[n]/(1-2*n) for n in range(N+1)]

def record(n,bits=OUT_BITS):
    n%=1<<bits
    v=b.v2(n,bits)
    return {'valuation_or_bound':v,'is_lower_bound':v==bits,
            'unit_mod65536':str((n>>v)%65536) if v+16<=bits else None,
            'residue':str(n)}

def run_case(T,aa):
    started=time.monotonic()
    B=17659+(1<<18)*T
    r=B*(1<<640)-161
    costs=[3*q+(r+q).bit_count()-r.bit_count()
           for q in range((r.bit_count()-1)//3+1)]
    assert min(costs)==-154
    assert max(q for q,v in enumerate(costs) if v==-154)==161
    Q=(P+r.bit_count()-154-2)//3
    gam=b.gamma(r,-154,P,Q)
    src=list(b.source(P))
    M=1<<P
    def local(center):
        lo,hi=old.local_split(P,center,15,gam,src)
        return [(a+bb)%M for a,bb in zip(lo,hi)]
    f0=local(10202)
    assert all(a%(1<<178)==0 for a in f0)
    K=[a>>178 for a in f0]
    cbits=P-179
    assert all(i*K[i]%2==0 for i in range(1,len(K)))
    dKhalf=[i*K[i]//2 for i in range(1,len(K))]
    c=0
    for j in range(cbits):
        if b.ev(dKhalf,c,1<<(j+1)):
            c+=1<<j
    assert c%128==20
    x=10202+(1<<15)*c
    m=1<<OUT_BITS
    pq=1; dpq=0; sum_shifted=0; sum_comm=0; packets=[]
    vals=[]; ders=[]
    for q in range(QOP+1):
        fq=f0 if not q else local(10202-q)
        assert all(i*fq[i]%(1<<15)==0 for i in range(1,len(fq)))
        dfq=[i*fq[i]//(1<<15) for i in range(1,len(fq))]
        val=b.ev(fq,c,m)
        der=b.ev(dfq,c,m)
        vals.append(val);ders.append(der)
        a=aa[q]
        assert a.denominator%2==1
        aq=a.numerator*pow(a.denominator,-1,m)%m
        weight=pow(8,q,m)*aq%m
        shifted=weight*pq*der%m
        comm=weight*dpq*val%m
        sum_shifted=(sum_shifted+shifted)%m
        sum_comm=(sum_comm+comm)%m
        packets.append({'q':q,'G_at_shift':record(val),'Gprime_at_shift':record(der),
                        'shifted_derivative_term':record(shifted),
                        'commutator_term':record(comm),
                        'derivative_of_packet':record(shifted+comm)})
        factor=(x-q)*(2*x-2*q-1)
        dpq=(dpq*factor+pq*(4*x-4*q-1))%m
        pq=pq*factor%m
    assert ders[0]==0
    assert b.v2(vals[1],OUT_BITS)==153
    assert b.v2(ders[1],OUT_BITS)==152
    assert b.v2(sum_shifted,OUT_BITS)==156
    assert b.v2(sum_comm,OUT_BITS)==156
    return {'T':str(T),'r':str(r),'actual_terminal':161,'mu':-154,
            'global_packet_max':Q,'stationary_Z_bits':cbits,'stationary_Z':str(c),
            'G_at_stationary_point':record(vals[0]),
            'Tg_Gprime':record(sum_shifted),'commutator_D_Tg_G':record(sum_comm),
            'derivative_Tg_G':record(sum_shifted+sum_comm),
            'packets':packets,'seconds':time.monotonic()-started}

def main(out):
    b.B=b.bernoullis(max(256,P));b.twoB=old.fast_twoB
    beta,aa=rational_kernels(QOP)
    assert aa[1]==Fraction(1,3)
    cases=[run_case(T,aa) for T in (0,22831001499602523078606181325)]
    result={'status':'passed','named_discriminator':'strict leading valuation in the argument derivative commutator',
            'global_precision':P,'output_precision':OUT_BITS,'operator_q_max':QOP,
            'omitted_shifted_derivative_tail_valuation_lower_bound':181,
            'omitted_commutator_tail_valuation_lower_bound':183,
            'cases':cases,'python':platform.python_version(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'inherited_engine_sha256':hashlib.sha256((SRC/'fast_parameter_certificate.py').read_bytes()).hexdigest(),
            'nonclaims':['No new multiplier digits','No universal nonintersection',
                         'The stationary points need not be zeros','No Lean compilation']}
    Path(out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in c.items() if k not in ('r','packets')} for c in cases],indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    main(p.parse_args().out)
