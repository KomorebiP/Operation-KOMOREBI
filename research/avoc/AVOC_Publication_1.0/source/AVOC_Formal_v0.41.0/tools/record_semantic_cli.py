#!/usr/bin/env python3
"""Record actual read-only wrapper executions; creates only new evidence files."""
import hashlib,json,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/v0.26.0/cli';OUT.mkdir(parents=True,exist_ok=True)
cases=[('campaign', (ROOT/'examples/semantic/campaign.json').read_text(),0),
 ('budget',(ROOT/'examples/semantic/budget.json').read_text(),0),
 ('depth3',(ROOT/'examples/semantic/all_functions.json').read_text(),0),
 ('zero',json.dumps({'mode':'budget','depth':2,'credit':0}),0),
 ('boolean_credit',json.dumps({'mode':'budget','depth':2,'credit':True}),2),
 ('float_credit',json.dumps({'mode':'budget','depth':2,'credit':1.0}),2),
 ('negative_depth',json.dumps({'mode':'feedback','depth':-1}),2),
 ('oversize_depth',json.dumps({'mode':'frozen','depth':3}),2),
 ('unknown_field',json.dumps({'mode':'feedback','depth':1,'trust_me':True}),2),
 ('code_injection',json.dumps({'mode':'feedback','depth':1,'references':[['python','import os']]}),2),
 ('duplicate_field','{"mode":"feedback","depth":1,"depth":2}',2),
 ('wrong_arity',json.dumps({'mode':'feedback','depth':1,'references':[['and',['literal',True]]]}),2)]
records=[]
for name,text,expected in cases:
 req=OUT/(name+'.json');req.write_text(text)
 cmd=[sys.executable,str(ROOT/'tools/run_semantic_synthesis.py'),str(req)]
 t=time.monotonic();r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,timeout=60);seconds=time.monotonic()-t
 out=OUT/(name+'_stdout.json' if not r.returncode else name+'_stdout.txt');out.write_text(r.stdout)
 err=OUT/(name+'_stderr.txt');err.write_text(r.stderr)
 assert r.returncode==expected,(name,r.returncode,r.stderr)
 if expected==0:
  result=json.loads(r.stdout);assert result['status'] in ['checked','unfunded','query_unfunded']
 records.append({'case':name,'command':cmd,'returncode':r.returncode,'expected':expected,'passed':True,'seconds':seconds,
   'request_sha256':hashlib.sha256(req.read_bytes()).hexdigest(),'output_path':str(out.relative_to(ROOT)),
   'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'stderr_sha256':hashlib.sha256(err.read_bytes()).hexdigest()})
 print(name, 'PASS', round(seconds,3),flush=True)
(OUT/'summary.json').write_text(json.dumps({'passed':True,'cases':records,'wrapper_sha256':hashlib.sha256((ROOT/'tools/run_semantic_synthesis.py').read_bytes()).hexdigest(),'recorder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2)+'\n')
