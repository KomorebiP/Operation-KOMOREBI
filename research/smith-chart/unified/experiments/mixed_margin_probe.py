"""Bounded exact-NRA triage, not a negative-certificate checker. Author: Komorebi P.

Optional dependency: z3-solver 5.4.1.0. Positive rational candidates are replayed
by independent exact nodal arithmetic. UNSAT reports are explicitly backend
dependent; UNKNOWN/timeouts never imply nonrealizability.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse,json,sys,time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'solver'))
from reactive_skeletons import generate,vertices,no_parallel_same_kind
from pure_type_margins import SAMPLES,gamma
from exact_phasor import C,response


def physical_response(edges,parameters,s):
    n=max([1]+[v for _,u,v in edges]+[u for _,u,v in edges])+1
    parent=list(range(n))
    def find(x):
        while parent[x]!=x:x=parent[x]
        return x
    for (_,u,v),t in zip(edges,parameters):
        if t==1:parent[find(u)]=find(v)
    if find(0)==find(1):return F(-1)
    labels={find(0):0,find(1):1};out=[]
    for (kind,u,v),t in zip(edges,parameters):
        u,v=find(u),find(v)
        if t in (0,1) or u==v:continue
        for node in (u,v):
            if node not in labels:labels[node]=len(labels)
        value=t/(1-t) if kind=='C' else (1-t)/t
        out.append((kind,labels[u],labels[v],value))
    result=response(out,C(s))['gamma'];assert not result.im
    return result.re


def run_case(z3,reactive,margin,timeout_ms,fixed=None):
    n=vertices(reactive);edges=[('R',u,v) for u,v in combinations(range(n),2)]+list(reactive)
    t=[z3.Real('t'+str(e)) for e in range(len(edges))]
    solver=z3.SolverFor('QF_NRA');solver.set(timeout=timeout_ms)
    for value in t:solver.add(value>=0,value<=1)
    if fixed is not None:
        for value,p in zip(t,fixed):solver.add(value==z3.RealVal(str(p)))
    for k,s in enumerate(SAMPLES):
        voltage=[z3.RealVal(0)]+[z3.Real('v'+str(k)+'_'+str(v)) for v in range(1,n)]
        current=[z3.Real('i'+str(k)+'_'+str(e)) for e in range(len(edges))]
        for v in voltage[1:]:solver.add(v>=0,v<=1)
        for i in current:solver.add(i>=-1,i<=1)
        for node in range(1,n):
            out=sum((i if u==node else -i if v==node else 0) for (_,u,v),i in zip(edges,current))
            solver.add(out==(1-voltage[1] if node==1 else 0))
        for (kind,u,v),p,i in zip(edges,t,current):
            phi=s if kind=='C' else 1/s if kind=='L' else F(1)
            solver.add(phi.denominator*(1-p)*i==phi.numerator*p*(voltage[u]-voltage[v]))
        residual=2*voltage[1]-1-z3.RealVal(str(gamma(s)))
        solver.add(residual<=z3.RealVal(str(margin)),residual>=-z3.RealVal(str(margin)))
    smt=solver.to_smt2().encode();start=time.monotonic();answer=solver.check()
    result={'vertices':n,'reactive':list(reactive),'model_sha256':sha256(smt).hexdigest(),
        'variables':len(t)+len(SAMPLES)*(n-1+len(edges)),
        'seconds':round(time.monotonic()-start,4),'backend_result':str(answer)}
    if answer==z3.unknown:
        result['reason']=solver.reason_unknown();result['interpretation']='RESOURCE_INCONCLUSIVE'
    elif answer==z3.unsat:
        result['interpretation']='UNSAT_REPORTED_WITHOUT_INDEPENDENT_REFUTATION_CERTIFICATE'
    else:
        model=solver.model();verified=False
        for precision in (30,80):
            values=[]
            for p in t:
                value=model.eval(p,model_completion=True)
                if z3.is_algebraic_value(value):value=value.approx(precision)
                if not z3.is_rational_value(value):break
                values.append(max(F(0),min(F(1),F(value.numerator_as_long(),value.denominator_as_long()))))
            if len(values)!=len(t):continue
            try:actual=[physical_response(edges,values,s) for s in SAMPLES]
            except (ValueError,ZeroDivisionError):continue
            error=max(abs(a-gamma(s)) for a,s in zip(actual,SAMPLES))
            if error<=margin:
                result.update(interpretation='SAT_VERIFIED_BY_EXACT_RATIONAL_PHYSICAL_REPLAY',
                    parameters=list(map(str,values)),actual_sample_gammas=list(map(str,actual)),actual_error=str(error))
                verified=True;break
        if not verified:result['interpretation']='SAT_REPORTED_BUT_NO_RATIONAL_WITNESS_VERIFIED'
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--z3-path',type=Path)
    parser.add_argument('--timeout-ms',type=int,default=100)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--selection',choices=('full','representative'),default='representative')
    parser.add_argument('--margin',default='1/1000000')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.z3_path:sys.path.insert(0,str(args.z3_path.resolve()))
    import z3
    if z3.get_version_string()!='5.4.1':raise RuntimeError('Probe requires pinned Z3 5.4.1')
    runtime_root=Path(z3.__file__).resolve().parent
    runtime_files=sorted(p for p in runtime_root.rglob('*') if p.is_file() and p.suffix in ('.py','.dll','.so','.dylib'))
    def runtime_hashes():
        return {p.relative_to(runtime_root).as_posix():sha256(p.read_bytes()).hexdigest() for p in runtime_files}
    runtime_before=runtime_hashes()
    margin=F(args.margin)
    if not 0<margin<F(401,5286560) or args.timeout_ms<=0:raise ValueError('Invalid probe contract')
    args.output.mkdir(parents=True,exist_ok=False)
    negative=run_case(z3,(),margin,5000)
    if negative['backend_result']!='unsat':raise RuntimeError('Resistor-only negative control failed')
    known=(('L',1,2,F(1)),('R',2,0,F(4,9)),('R',1,3,F(1)),
        ('L',2,4,F(8,31)),('L',3,4,F(169,186)),('C',3,4,F(186,169)),('C',4,0,F(31,8)))
    reactive=tuple((kind,u,v) for kind,u,v,value in known if kind!='R')
    rmap={tuple(sorted((u,v))):1/value for kind,u,v,value in known if kind=='R'}
    coefficients=[rmap.get((u,v),F(0)) for u,v in combinations(range(5),2)]+[
        value if kind=='C' else 1/value for kind,u,v,value in known if kind!='R']
    fixed=[a/(1+a) for a in coefficients]
    physical_edges=[('R',u,v) for u,v in combinations(range(5),2)]+list(reactive)
    assert all(physical_response(physical_edges,fixed,s)==gamma(s) for s in SAMPLES)
    positive=run_case(z3,reactive,F(0),10000,fixed)
    if positive['interpretation']!='SAT_VERIFIED_BY_EXACT_RATIONAL_PHYSICAL_REPLAY':
        raise RuntimeError('Five-reactive exact positive control failed')
    levels=generate(4)
    cases=sorted((g for q in (2,3,4) for g in levels[q]
        if len({e[0] for e in g})==2 and no_parallel_same_kind(g)),key=lambda g:(len(g),vertices(g),g))
    assert len(cases)==2130
    if args.selection=='full':selected=cases
    else:
        selected=[g for g in cases if len(g)==2]
        buckets={}
        for g in cases:
            if len(g)>2:
                key=(len(g),vertices(g),sum(kind=='C' for kind,_,_ in g))
                buckets.setdefault(key,g)
        selected+=list(buckets.values())
    if args.limit is not None:selected=selected[:args.limit]
    rows=[]
    for k,graph in enumerate(selected):
        row=run_case(z3,graph,margin,args.timeout_ms);row['index']=k;rows.append(row)
        print(json.dumps({'index':k,'budget':len(graph),'result':row['backend_result'],
            'interpretation':row['interpretation']}),flush=True)
    counts={name:sum(r['backend_result']==name for r in rows) for name in ('sat','unsat','unknown')}
    runtime_after=runtime_hashes()
    if runtime_after!=runtime_before:raise RuntimeError('Backend files changed during execution')
    record={'status':'COMPLETED','backend':'z3-solver '+z3.get_version_string(),
        'backend_files_sha256_before':runtime_before,'backend_files_sha256_after':runtime_after,
        'margin_tested':str(margin),'timeout_ms_per_case':args.timeout_ms,
        'selection':args.selection,
        'canonical_population':len(cases),'processed':len(rows),'counts':counts,
        'controls':{'negative':negative,'positive':positive},'cases':rows,
        'non_claims':['UNSAT reports are not independently checked refutation certificates',
            'UNKNOWN is not impossibility','This triage does not replace the universal written bound or prove a new mixed-RLC margin']}
    (args.output/'summary.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in record.items() if k not in ('cases','controls')},indent=2))


if __name__=='__main__':main()
