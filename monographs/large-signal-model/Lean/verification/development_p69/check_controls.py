#!/usr/bin/env python3
"""Rebind refined controls; retain unchanged, actual proof-check stages."""
from pathlib import Path
import hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=OUT/'RESULT.json';r=json.loads(p.read_text())
assert r['source_sha256']=={m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in r['source_sha256']}
assert r['dependencies']=={m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in r['dependencies']}
base=[s for s in r['stages'] if not s['phase'].startswith('negative_control:')]
assert len(base)==7 and all(s['returncode']==0 for s in base)
(OUT/'CONTROL_SNAPSHOT_DIAGNOSTIC.json').write_text(json.dumps(r,indent=2)+'\n')
r['stages']=base;r['control_sha256']={m:sha(ROOT/'negative_controls'/f'{m}.lean') for m in r['control_sha256']}
r['control_snapshot_note']='Controls were refined during the first check run; final controls are rechecked here. Unchanged proof sources retain their actual fresh compile, full-name audit and replay stages.'
r['passed']=False;r['complete']=False
save=lambda:p.write_text(json.dumps(r,indent=2)+'\n')
save()
for m in r['control_sha256']:
 args=['/workspace/scratch/ea498747acd5/runtime/gated-bin/lean','-j1','-DwarningAsError=true',str(ROOT/'negative_controls'/f'{m}.lean')]
 start=time.monotonic();q=subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 s=dict(phase='negative_control:'+m,command=args,returncode=q.returncode,stdout=q.stdout,stderr=q.stderr,seconds=round(time.monotonic()-start,3),expected_rejection=True)
 r['stages'].append(s);save();print(m,q.returncode,flush=True)
 assert q.returncode!=0 and 'False' in q.stdout,s
 assert not any(t in q.stdout for t in ['unknown constant','unknown module','failed to synthesize','type mismatch','Type mismatch','timeout','unused']),s
assert r['source_sha256']=={m:sha(ROOT/'KomorebiLSM'/f'{m}.lean') for m in r['source_sha256']}
assert r['control_sha256']=={m:sha(ROOT/'negative_controls'/f'{m}.lean') for m in r['control_sha256']}
r['passed']=True;r['complete']=True;save();print('P69_INDIVIDUAL_PASS',flush=True)
