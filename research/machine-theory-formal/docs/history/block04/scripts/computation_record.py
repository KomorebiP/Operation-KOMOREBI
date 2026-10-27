#!/usr/bin/env python3
"""Export and verify the legacy-v1 computation record against actual Lean-run receipts.
Project-authored checker, not an authenticated external audit service. The legacy
field structure follows the computation-audit skill template. Actual proof validity
comes from the recorded compiler and kernel replay, not this JSON validator.
"""
from __future__ import annotations
import argparse,hashlib,json,math,platform,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def verify(m):
 required={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
 if not required<=set(m) or m['schema_version']!=1:raise ValueError('Incomplete or unsupported legacy record')
 if not all(isinstance(m[k],str) and m[k].strip() for k in ['claim_id','command','result']):raise ValueError('Blank claim/command/result')
 for k in ['assertion_tested','coefficient_domain','conventions']:
  if not m['mathematics'][k].strip():raise ValueError('Empty mathematical contract')
 if not m['mathematics']['bounds'] or not m['mathematics']['non_claims']:raise ValueError('Missing scope')
 if not m['environment']['software'] or not isinstance(m['repository']['dirty'],bool):raise ValueError('Missing environment')
 t=m['run']['runtime_seconds']
 if not isinstance(t,(int,float)) or not math.isfinite(t) or t<0 or m['run']['exit_status']!=0:raise ValueError('Invalid completed-run fields')
 if not m['outputs'] or not m['checks']:raise ValueError('Missing evidence')
 for o in m['outputs']:
  rel=Path(o['path'])
  if rel.is_absolute() or '..' in rel.parts or not re.fullmatch('[0-9a-f]{64}',o['sha256']):raise ValueError('Unsafe output')
  if sha(ROOT/rel)!=o['sha256']:raise ValueError('Output hash mismatch: '+str(rel))
 if not all(x['passed'] for x in m['checks']):raise ValueError('A required execution check failed')
 for receipt in ['evidence/final04/report.json','evidence/fresh04/report.json']:
  r=read(ROOT/receipt)
  if r['status']!='PASS' or r['input_sha256_before']!=r['input_sha256_after']:raise ValueError('Invalid proof run')
  for rel,h in r['input_sha256_after'].items():
   if sha(ROOT/rel)!=h:raise ValueError('Input changed since proof run: '+rel)
 print('PASS: filled legacy-v1 record, output hashes and actual proof-run source bindings.')
 print('Legacy schema alone does not require input hashes or authenticate execution; the separate checked run receipts supply local input hashes. No repository revision is claimed.')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');a=ap.parse_args()
 out=ROOT/'evidence/COMPUTATION_MANIFEST_BLOCK04.json'
 if a.write:
  f=read(ROOT/'evidence/final04/report.json');g=read(ROOT/'evidence/fresh04/report.json')
  compare=read(ROOT/'evidence/FRESH_REBUILD_BLOCK04.json')
  if f['status']!='PASS' or g['status']!='PASS' or compare['status']!='PASS':raise ValueError('Proof or rebuild run did not pass')
  names=['evidence/final04/report.json','evidence/final04/axioms.json','evidence/final04/source_inventory.json','evidence/final04/dependency_artifacts.json','evidence/fresh04/report.json','evidence/fresh04/axioms.json','evidence/FRESH_REBUILD_BLOCK04.json']
  m={'schema_version':1,'claim_id':'ReviewedCore0.2:r:history-bound+r:policy-error / cumulative11of27',
    'repository':{'commit':'unavailable','dirty':True},
    'command':'python scripts/verify.py --runtime <pinned portable runtime> --out evidence/final04; fresh extracted-source replay with --out evidence/fresh04; python scripts/compare_rebuild.py with the recorded two actual runs',
    'environment':{'software':[f['lean_version'],'mathlib '+f['dependency_revisions']['mathlib'],'Python '+platform.python_version()],
                   'hardware':platform.platform()+'; CPU-only Lean checking; no separately imposed OS memory/affinity cap'},
    'mathematics':{'assertion_tested':'Kernel compilation and replay of 11 explicitly mapped conditional source results; new complete-history TV bound, sharp rare-event conditioning and uniform approximate-policy regret. Finite examples are proof terms, not sampled evidence for universal claims.',
       'coefficient_domain':'Exact real-valued finite distributions and kernels; exact rational constants in examples; Lean dependent type theory.',
       'conventions':'Column-oriented joint report/successor instruments. TV is half the finite l1 distance. Policies see action/report history only. Both conditioned event masses positive. Same loss and common finite policy catalogue.',
       'inputs':list(f['input_sha256_before']),
       'bounds':{'source_results':11,'source_total':27,'production_modules':19,'substantive_replays':18,'negative_controls':36,'per_command_wall_seconds':45,'Lean_internal_MiB':3072,'threads':1,'whole_gate_supervisor_seconds':900},
       'non_claims':['No complete-book formalization','No upstream Lean/mathlib source rebuild','No independent kernel','No physical or learned sensor validation','No empirical performance or efficient optimizer guarantee']},
    'randomness':{'used':False,'generator':'not applicable','seed':None},
    'run':{'started_at':f['started_at'],'runtime_seconds':f['total_seconds']+g['total_seconds'],'exit_status':0},
    'outputs':[{'path':p,'sha256':sha(ROOT/p)} for p in names],
    'checks':[{'name':'final/'+s['name'],'passed':s['passed']} for s in f['steps']]+[{'name':'fresh/'+s['name'],'passed':s['passed']} for s in g['steps']]+[{'name':'cold-source-comparison','passed':compare['status']=='PASS'}],
    'result':'PASS: actual cumulative Lean builds, transitive axiom audits, local same-kernel replays, specified negative controls and strict production-object cold-rebuild comparison.',
    'residual_risks':['Source-to-model adequacy is a stated mathematical premise','Pinned upstream caches are reused','Review and audit tools are project-authored','No Git revision or independent execution attestation','Legacy schema requires separate receipts for input hashes and per-command limits']}
  out.write_text(json.dumps(m,indent=2)+'\n')
 verify(read(out))
if __name__=='__main__':main()
