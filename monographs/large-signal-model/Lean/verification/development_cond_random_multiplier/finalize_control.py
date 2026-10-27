from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=OUT/'RESULT.json';r=json.loads(p.read_text());M='ConditionalRandomMultiplier';C='ConditionalRandomUnpredictable'
assert r['source_sha256'][M]==sha(ROOT/'KomorebiLSM'/f'{M}.lean')
base=[s for s in r['stages'] if s['phase']!='negative_control']
assert len(base)==3 and all(s['returncode']==0 for s in base)
(OUT/'CONTROL_DEVELOPMENT_DIAGNOSTIC.json').write_text(json.dumps(r,indent=2)+'\n')
r['stages']=base;r['control_sha256']={C:sha(ROOT/'negative_controls'/f'{C}.lean')}
r['control_refinement_note']='Only the control was refined after the actual proof compile/audit/replay stages; unchanged proof source hash is verified.'
r['passed']=False;r['complete']=False
args=['/workspace/scratch/ea498747acd5/runtime/gated-bin/lean','-j1','-DwarningAsError=true',str(ROOT/'negative_controls'/f'{C}.lean')]
start=time.monotonic();q=subprocess.run(args,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
s=dict(phase='negative_control',command=args,returncode=q.returncode,seconds=round(time.monotonic()-start,3),stdout=q.stdout,stderr=q.stderr,expected_rejection=True)
r['stages'].append(s);p.write_text(json.dumps(r,indent=2)+'\n')
assert q.returncode!=0 and q.stdout.count('error:')==1 and '⊢ False' in q.stdout,s
assert not any(x in q.stdout for x in ['unknown constant','unknownIdentifier','failed to synthesize','type mismatch','Type mismatch','timeout','unused','noncomputable']),s
assert r['source_sha256'][M]==sha(ROOT/'KomorebiLSM'/f'{M}.lean')
assert r['control_sha256'][C]==sha(ROOT/'negative_controls'/f'{C}.lean')
r['scope_file']='verification/development_cond_random_multiplier/SCOPE.md'
r['scope_sha256']=sha(OUT/'SCOPE.md')
r['passed']=True;r['complete']=True;p.write_text(json.dumps(r,indent=2)+'\n')
print('P81_RANDOM_MULTIPLIER_PASS',sha(p),flush=True)
