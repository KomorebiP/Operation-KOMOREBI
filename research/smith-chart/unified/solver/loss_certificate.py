"""Exact damping-dependent uncertainty disks for paired-loss RLC graphs.

Author: Komorebi P. This checks hypotheses of the separately proved finite
branch-to-port contraction. It does not substitute for hardware measurements.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse,json,re
from exact_phasor import C,solve

FORMAT='komorebi-paired-loss-reflection-disk-v1'

def rational(x):
    if type(x) is int:
        if x.bit_length()>1024:raise ValueError('Integer acceptance limit: 1024 bits')
        return F(x)
    if type(x) is not str or len(x)>256 or not re.fullmatch(r'[+-]?\d+(?:/\d+)?',x):
        raise ValueError('Use bounded integers or rational strings, not floats or booleans')
    try:return F(x)
    except (ValueError,ZeroDivisionError) as exc:raise ValueError('Invalid rational') from exc

def parse(problem):
    if not isinstance(problem,dict) or set(problem)!={'branches','frequency_band','relative_tolerance','reference_R','samples'}:
        raise ValueError('Problem fields differ from the declared format')
    delta,reference=rational(problem['relative_tolerance']),rational(problem['reference_R'])
    if not 0<delta<1 or reference<=0:raise ValueError('Positive reference and 0<delta<1 required')
    band=problem['frequency_band']
    if not isinstance(band,list) or len(band)!=2:raise ValueError('Band requires two endpoints')
    low,high=map(rational,band)
    if not 0<low<=high:raise ValueError('Positive ordered band required')
    raw=problem['branches']
    if not isinstance(raw,list) or not 1<=len(raw)<=24:raise ValueError('Branch acceptance limit: 1..24')
    branches=[]
    for e in raw:
        if not isinstance(e,dict):raise ValueError('Each branch must be an object')
        kind=e.get('kind');required={'kind','nodes','value'}|({'series_R'} if kind in ('L','C') else set())
        if kind not in ('R','L','C') or set(e)!=required:raise ValueError('Branch kind or fields invalid')
        nodes=e['nodes']
        if not isinstance(nodes,list) or len(nodes)!=2 or any(type(v) is not int or not 0<=v<=15 for v in nodes):
            raise ValueError('Integer node labels 0..15 required; ports are 0 and 1')
        value=rational(e['value']);loss=rational(e['series_R']) if kind!='R' else value
        if value<=0 or loss<=0:raise ValueError('Every reactive branch needs its own strictly positive series loss')
        branches.append((kind,*nodes,value,loss))
    samples=problem['samples']
    if not isinstance(samples,list) or len(samples)>32:raise ValueError('Sample acceptance limit: 32')
    samples=list(map(rational,samples))
    if any(not low<=w<=high for w in samples):raise ValueError('Samples must lie inside the band')
    return branches,(low,high),delta,reference,samples

def impedances(branches,omega,reference=F(1)):
    rows=[]
    for kind,u,v,value,loss in branches:
        x=omega*value if kind=='L' else -1/(omega*value) if kind=='C' else F(0)
        rows.append((u,v,C(loss/reference,x/reference)))
    return rows

def response_impedances(edges):
    """Compound-edge nodal solve, separate from the expanded physical graph."""
    reached={1}
    while True:
        extra=reached|{v for u,v,z in edges if u in reached}|{u for u,v,z in edges if v in reached}
        if extra==reached:break
        reached=extra
    if 0 not in reached:return {'gamma':C(1),'currents':[C() for _ in edges]}
    nodes=sorted(reached-{0});indices={n:k for k,n in enumerate(nodes)}
    A=[[C() for _ in nodes] for _ in nodes];b=[C() for _ in nodes]
    for u,v,z in edges:
        y=1/z
        if u not in reached:continue
        for p,q in ((u,v),(v,u)):
            if p in indices:
                A[indices[p]][indices[p]]+=y
                if q in indices:A[indices[p]][indices[q]]-=y
    A[indices[1]][indices[1]]+=1;b[indices[1]]=C(1)
    values=solve(A,b);voltage={0:C(),**{n:values[k] for n,k in indices.items()}}
    currents=[(voltage.get(u,C())-voltage.get(v,C()))/z for u,v,z in edges]
    return {'gamma':2*voltage[1]-1,'currents':currents}

def expand(branches,reference=F(1)):
    fresh=max([1]+[v for _,u,v,_,_ in branches]+[u for _,u,v,_,_ in branches])+1
    edges=[];indices=[]
    for kind,u,v,value,loss in branches:
        if kind=='R':
            indices.append((len(edges),));edges.append(('R',u,v,value/reference))
        else:
            indices.append((len(edges),len(edges)+1))
            edges.append(('R',u,fresh,loss/reference))
            edges.append((kind,fresh,v,value/reference if kind=='L' else value*reference))
            fresh+=1
    return edges,indices

def complex_record(z):return {'re':str(z.re),'im':str(z.im)}

def budget(delta,kappa):
    return delta*delta*((1-delta)**2+kappa*kappa)/(4*(1-delta)**3)

def certificate(problem):
    branches,(low,high),delta,reference,samples=parse(problem)
    kappas=[high*value/loss if kind=='L' else 1/(low*value*loss) if kind=='C' else F(0)
            for kind,u,v,value,loss in branches]
    kappa=max(kappas);B=budget(delta,kappa);disks=[]
    for omega in samples:
        g=response_impedances(impedances(branches,omega,reference))['gamma'];r=g.normsq()
        if r>1:raise RuntimeError('Positive-loss graph violates port passivity')
        A=1+B*(1-r)
        disks.append({'omega':str(omega),'nominal_gamma':complex_record(g),
          'center':complex_record(g/A),'radius_squared':str(B*(1+B)*(1-r)**2/(A*A))})
    return {'format':FORMAT,'problem':problem,'nominal_band_quality_bound':str(kappa),
      'branch_mismatch_squared_budget':str(B),'uniform_gamma_difference_squared_bound':str(min(F(4),B)),
      'sample_disks':disks,'scope':'Fixed graph; dedicated positive series loss for every L/C; independent multiplicative R/L/C changes; specified positive band. Ideal lumped model, not measured hardware.',
      'mathematical_basis':'Finite branch-to-port power/Cauchy-Schwarz contraction and exact disk completion; written proof and selected formal statements have separate records.'}

def verify(record):
    if not isinstance(record,dict) or record.get('format')!=FORMAT:raise ValueError('Wrong certificate format')
    if 'problem' not in record:raise ValueError('Missing certificate problem')
    rebuilt=certificate(record['problem'])
    if record!=rebuilt:raise ValueError('Certificate differs from exact graph, band, budget or disk reconstruction')
    return {'status':'PASS','branch_mismatch_squared_budget':rebuilt['branch_mismatch_squared_budget'],
      'nominal_band_quality_bound':rebuilt['nominal_band_quality_bound'],'sample_disks':len(rebuilt['sample_disks']),
      'coverage':'Continuous component box and whole declared band by the written theorem; samples are nominal disk evaluations only.'}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('problem',type=Path);parser.add_argument('--output',type=Path)
    parser.add_argument('--verify',action='store_true',help='Reconstruct and check a previously emitted record')
    args=parser.parse_args()
    if args.problem.stat().st_size>131072:raise ValueError('Problem file acceptance limit: 128 KiB')
    raw=json.loads(args.problem.read_bytes())
    record=verify(raw) if args.verify else certificate(raw)
    if not args.verify:verify(record)
    text=json.dumps(record,indent=2)+'\n'
    if args.output:args.output.write_text(text,encoding='utf-8')
    else:print(text)
