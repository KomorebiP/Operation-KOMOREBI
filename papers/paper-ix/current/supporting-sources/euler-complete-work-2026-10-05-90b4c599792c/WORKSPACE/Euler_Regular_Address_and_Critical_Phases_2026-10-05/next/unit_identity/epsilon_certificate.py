#!/usr/bin/env python3
"""Bounded actual-Euler audit of the independent epsilon critical manifold.

The integer Euler index is fixed. The epsilon parameter is varied independently,
so a modular singular member is not an actual singular Euler index.
"""
from pathlib import Path
import sys, json, time, hashlib, platform, argparse

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate'
sys.path.insert(0,str(SRC))
import fast_parameter_certificate as old
b=old.base

def build(T,P):
    started=time.monotonic()
    B=17659+(1<<18)*T
    r=B*(1<<640)-161
    mu=-154
    costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range((r.bit_count()-1)//3+1)]
    assert min(costs)==mu and max(q for q,w in enumerate(costs) if w==mu)==161
    assert 2*r-1>P
    b.B=b.bernoullis(max(256,P)); b.twoB=old.fast_twoB
    M=1<<P; local_bits=P-178; N=local_bits-1; mod=1<<N
    Q=(P+r.bit_count()+mu-2)//3
    gam=b.gamma(r,mu,P,Q); src=list(b.source(P))
    assert all(b.v2(a,P)>=i for i,a in enumerate(src))

    def local_from(gs):
        lo,hi=old.local_split(P,10202,15,gs,src)
        vals=[(x+y)%M for x,y in zip(lo,hi)]
        assert all(a%(1<<178)==0 for a in vals)
        return [a>>178 for a in vals]

    # Every eta power m>=2 has valuation at least 26m-27 after chart content.
    mmax=max(1,(local_bits+26)//26)
    while 26*(mmax+1)-27<local_bits:
        mmax+=1
    jet=[local_from(gam)]
    for m in range(1,mmax+1):
        gs=[g*(pow(4,q,M)-1)*pow(4,q*(m-1),M)*(1<<(24*m))%M for q,g in enumerate(gam)]
        jet.append(local_from(gs))
    assert 26*(mmax+1)-27>=local_bits
    assert jet[0][2]%2==1 and all(a%4==0 for a in jet[0][3:])
    assert jet[1][0]%2==1 and all(a%(1<<14)==0 for a in jet[1][1:])
    for m in range(2,len(jet)):
        assert all(b.v2(a,local_bits)>=min(local_bits,26*m-27) for a in jet[m])
    qjet=[]
    for fm in jet:
        assert all((i*a)%2==0 for i,a in enumerate(fm))
        qjet.append([(i*fm[i]//2)%mod for i in range(1,len(fm))])

    def ev2(js,e,z,m):
        return b.ev([b.ev(row,z,m) for row in js],e,m)

    eta=z=0
    counts=[]
    for k in range(N):
        step=1<<k; mm=2*step
        xs=[(eta+de*step,z+dz*step) for de in (0,1) for dz in (0,1)
            if ev2(jet,eta+de*step,z+dz*step,mm)==0
            and ev2(qjet,eta+de*step,z+dz*step,mm)==0]
        assert len(xs)==1
        eta,z=xs[0]; counts.append(len(xs))

    c0=0
    for k in range(N):
        if b.ev(qjet[0],c0,1<<(k+1)):c0+=1<<k
    phi0=b.ev(jet[0],c0,mod)
    assert b.v2(phi0,N)==b.v2(eta,N)

    # Orthogonal rational reassembly, rather than another power expansion.
    direct=[]
    for ee in (0,1,2,eta):
        eps=(ee<<24)%M
        gs=[g*(1-eps)*pow((1-eps*pow(4,q,M))%M,-1,M)%M for q,g in enumerate(gam)]
        f=local_from(gs)
        expected=[b.ev([row[i] for row in jet],ee,1<<local_bits) for i in range(len(f))]
        assert f==expected
        direct.append({'eta':str(ee),'all_local_coefficients_match':True})

    return {'status':'passed','integer_T':str(T),'integer_B':str(B),
            'global_precision':P,'chart_content':178,'local_coefficient_bits':local_bits,
            'joint_lift_bits':N,'computed_packet_max':Q,'eta_degree':mmax,
            'omitted_eta_power_valuation_lower_bound':26*(mmax+1)-27,
            'eta_star_residue':str(eta),'critical_Z_residue':str(z),
            'eta_star_valuation_or_bound':b.v2(eta,N),
            'depleted_critical_value_residue':str(phi0),
            'depleted_critical_value_valuation_or_bound':b.v2(phi0,N),
            'jet':[[str(a) for a in row] for row in jet],
            'direct_rational_checks':direct,'unique_joint_successors_each_bit':counts,
            'seconds':time.monotonic()-started,
            'scope':'Independent epsilon deformation at a fixed actual Euler index. '
                    'The original Bernoulli units equal the depleted units at this finite precision.',
            'nonclaims':['No singular actual Euler index','No universal Euler simplicity','No Lean compilation']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--precision',type=int,default=272)
    p.add_argument('--out',required=True);a=p.parse_args()
    records=[build(T,a.precision) for T in (0,718787533)]
    result={'python':platform.python_version(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'inherited_source_sha256':hashlib.sha256((SRC/'fast_parameter_certificate.py').read_bytes()).hexdigest(),
            'records':records}
    Path(a.out).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps([{k:v for k,v in r.items() if k not in ('jet','unique_joint_successors_each_bit')}
                      for r in records],indent=2))
