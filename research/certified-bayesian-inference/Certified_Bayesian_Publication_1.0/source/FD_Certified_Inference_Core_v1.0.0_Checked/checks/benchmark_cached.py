#!/usr/bin/env python3
"""Bounded full-cost reference benchmark. Same tolerances/backend; includes final certificate/output.
Static explicit-candidate Lean exports are generated for every distinct result.
"""
import json,sys,time,statistics,hashlib
from pathlib import Path
from fractions import Fraction as Q
from exact_certificate import Model,matrix,rational,encode,eye,zero,Candidate,export_lean as certificate_export
import cached_posterior as cp

ROOT=Path(__file__).resolve().parents[1]

def cases():
    out=[]
    for name in ['coordinate','rotated']:
        d=json.loads((ROOT/f'examples/adaptive_{name}.json').read_text());out.append((name,d))
    for name,n,k,rank,sigma in [('sparse4',4,2,1,Q(1)),('dense4',4,2,4,Q(1)),('sparse8',8,4,1,Q(1)),('dense8',8,4,8,Q(1)),('conditioned4',4,2,4,Q(1,10))]:
        H=[[Q((i+j)%3-1,3) for j in range(n)] for i in range(k)]
        if rank==1:L=[[Q(1) if i<2 else Q(0)] for i in range(n)]
        else:L=[[Q(int(i==j)) for j in range(n)] for i in range(n)]
        ps=[[[Q(int(i==j==a)) for j in range(n)] for i in range(n)] for a in range(n)]
        d=encode(dict(model=dict(H=H,L=L,N=[[0] for _ in range(k)],sigma=sigma,mean=[0]*n,observation=[Q((-1)**i,2) for i in range(k)],output_packets=ps,input_packets=[eye(k)]),initial_gain=zero(n,k),epsilon=Q(1,4),output_radius=Q(1,1000),seed=0,scan=list(range(n))))
        out.append((name,d))
    return out

def static_export(m,r,eps,namespace):
    c=Candidate.parse(r['final_candidate'],m)
    s=certificate_export(m,[c],eps,namespace)
    # Eliminate unrelated selection examples so every method has the same candidate-check contract.
    at=s.index('def selected :=');s=s[:at]+f'end Komorebi.ExactPosterior.{namespace}\n'
    return s.replace('maxHeartbeats 800000','maxHeartbeats 8000000').replace('maxRecDepth 8192','maxRecDepth 65536')

def main():
    dest=Path(sys.argv[1]);dest.mkdir(parents=True,exist_ok=True);repeats=int(sys.argv[2]) if len(sys.argv)>2 else 5
    report=[];mods=[]
    for cid,(name,d) in enumerate(cases()):
        m=Model.parse(d['model']);B=matrix(d['initial_gain'],'B');eps=rational(d['epsilon']);delta=rational(d['output_radius']);modes=['cached','recompute','full'];samples={mode:[] for mode in modes};results={}
        for repeat in range(repeats+1):
            order=modes[repeat%3:]+modes[:repeat%3]
            for mode in order:
                r=cp.solve(m,B,eps,delta,d['seed'],d['scan'],[12],max_steps=1000,mode=mode,record_trace=False)
                if r['status']=='RESOURCE_LIMIT':raise RuntimeError((name,mode,r))
                if repeat:samples[mode].append(r['timing_seconds'])
                results[mode]=r
        assert results['cached']['final_candidate']==results['recompute']['final_candidate']
        assert results['cached']['selected_packets']==results['recompute']['selected_packets']
        rows=[]
        for mode in modes:
            r=results[mode];ident=f'Benchmark{cid}{mode.title()}';path=ROOT/'Komorebi'/f'{ident}.lean'
            t=time.perf_counter();source=static_export(m,r,eps,ident);export_seconds=time.perf_counter()-t;path.write_text(source);mods.append(ident)
            rows.append(dict(mode=mode,iterations=r['iterations'],median_seconds={key:statistics.median(x[key] for x in samples[mode]) for key in samples[mode][0]},samples_seconds=samples[mode],export_seconds=export_seconds,source_bytes=len(source.encode()),work=r['work'],final_gain=r['final_candidate']['gain'],exact_score=r['exact_score'],rounded_score=r['rounded_score'],verification_precision=r['chosen_precision'],output_precision=r['parameter_output']['precision'],module=ident,source_sha256=hashlib.sha256(source.encode()).hexdigest()))
            (dest/f'{name}_{mode}.json').write_text(json.dumps(r,indent=2)+'\n')
        report.append(dict(name=name,input=d,results=rows));print(name,[(x['mode'],x['iterations'],round(x['median_seconds']['total'],4)) for x in rows],flush=True)
    (dest/'benchmark.json').write_text(json.dumps(dict(status='PASS',repetitions=repeats,warmups=1,cases=report,non_claims=['Tiny exact-rational reference cases, not BLAS/GPU comparisons.','Core timings include setup/iteration/certificate/parameter output. Export and Lean-check costs recorded separately.','Work counters cover iterative matrix kernels and selection, not preprocessing, certificate arithmetic or rational bit complexity.','Static Lean certificates check returned distributions; cached trajectory correctness is covered by universal and separate concrete-program proofs.']),indent=2)+'\n')
    (ROOT/'BENCHMARK_MODULES.json').write_text(json.dumps(mods,indent=2)+'\n')
if __name__=='__main__':main()
