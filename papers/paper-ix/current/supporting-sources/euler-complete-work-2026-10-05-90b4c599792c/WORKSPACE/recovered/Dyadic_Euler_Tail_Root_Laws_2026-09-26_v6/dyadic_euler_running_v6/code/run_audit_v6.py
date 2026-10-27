#!/usr/bin/env python3
"""Run a declared exact audit, retaining logs and v2 provenance manifests."""
from __future__ import annotations
import argparse, hashlib, json, os, platform, resource, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True)
    p.add_argument('--result',required=True);p.add_argument('--timeout',type=int,default=40)
    p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
    command=a.command[1:] if a.command[:1]==['--'] else a.command
    if not command: raise ValueError('Missing command')
    name=a.name;output=ROOT/a.result
    if not output.resolve().is_relative_to(ROOT/'results'): raise ValueError('Result outside results/')
    if output.exists(): raise FileExistsError('Refusing to reuse a preexisting scientific output')
    inputs=sorted((ROOT/'code').glob('*.py'))
    pinned=[{'path':str(q.relative_to(ROOT)),'sha256':sha(q)} for q in inputs]
    log=ROOT/'results'/f'RUN_{name}.txt';start=time.perf_counter();stamp=datetime.now(timezone.utc).isoformat()
    limit=1536*1024**2
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
        resource.setrlimit(resource.RLIMIT_CPU,(a.timeout,a.timeout))
    env=os.environ.copy()
    for v in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):env[v]='1'
    status='completed';exit_code=-1
    with log.open('w') as stream:
        stream.write('ARGV '+json.dumps(command)+'\n');stream.flush()
        try:
            proc=subprocess.run(command,cwd=ROOT/'code',stdout=stream,stderr=subprocess.STDOUT,
                                timeout=a.timeout,env=env,preexec_fn=limits)
            exit_code=proc.returncode
            if exit_code!=0:status='failed'
        except subprocess.TimeoutExpired:
            status='timeout';exit_code=124
            stream.write('\nTIMEOUT: declared wall-clock limit exceeded. No completion claim.\n')
    runtime=time.perf_counter()-start
    for rec,q in zip(pinned,inputs):rec['sha256_after']=sha(q)
    if any(x['sha256']!=x['sha256_after'] for x in pinned) and status=='completed':status='inputs-changed'
    outputs=[{'path':str(log.relative_to(ROOT)),'sha256':sha(log),'kind':'log'}]
    if output.is_file():outputs.append({'path':a.result,'sha256':sha(output),'kind':'result'})
    elif status=='completed':status='result-missing'
    summary={}
    if output.is_file():summary=json.loads(output.read_text())
    manifest={'schema_version':2,'claim_id':f'DYADIC-V6-{name}',
      'repository':{'commit':'unavailable; archive-based working copy with pinned source hashes','dirty':True},
      'command':command,'environment':{'software':[{'name':'Python','version':sys.version},{'name':'OS','version':platform.platform()}],
        'hardware':platform.machine()+'; single-process scientific arithmetic'},
      'mathematics':{'assertion_tested':'The declared exact finite audit and its coefficientwise certificate checks.',
        'coefficient_domain':'Exact integer, rational and modular arithmetic.',
        'conventions':'Signed E_(2N), r=M+1, v2(0)=infinity; zero residue is only a lower bound.',
        'inputs':[x['path'] for x in pinned], 'bounds':{'arguments':command,'delta_interval':summary.get('delta_interval'),
           'counts':summary.get('counts',{})},
        'non_claims':['No Lean compilation.','No historical priority claim.','A timeout supplies no scientific completion.','No universal squarefreeness assertion for all Euler depths.']},
      'randomness':{'used':False,'generator':'deterministic inputs','seed':None},
      'run':{'started_at':stamp,'runtime_seconds':runtime,'exit_status':exit_code,'status':status,
        'resource_limits':{'memory_bytes':limit,'cpu_seconds':a.timeout,'max_cores':None,'max_threads':1},
        'resource_notes':'POSIX address-space and CPU-time caps; subprocess wall-clock cap; thread limits cooperative. No affinity cap.'},
      'input_artifacts':pinned,'execution_artifacts':[x['path'] for x in pinned],
      'declared_results':[a.result],'output_directory':'results','outputs':outputs,
      'checks':[{'name':k,'count':v,'status':'PASS'} for k,v in summary.get('counts',{}).items()] if status=='completed' else [],
      'result':'Completed exact audit; universal interpretation depends on the accompanying proofs.' if status=='completed' else 'Audit did not complete successfully.',
      'residual_risks':['The polynomial and analytic proofs have not been kernel checked.']}
    dest=ROOT/'results'/f'MANIFEST_{name}.json';dest.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':status,'runtime_seconds':runtime,'manifest':str(dest),'summary':{k:v for k,v in summary.items() if k in ('j','counts','delta_interval')}},indent=2))
    return 0 if status=='completed' else 1
if __name__=='__main__':raise SystemExit(main())
