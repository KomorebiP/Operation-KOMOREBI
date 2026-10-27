#!/usr/bin/env python3
"""Fail-closed current-source evidence collector for AVOC v0.39."""
from pathlib import Path
import hashlib,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]; RD=ROOT/'results/v0.39.0'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text())
errors=[]
order=read('results/v0.39.0/build_order.json'); targets=[]
for f in order:
 p=RD/f'clean_{Path(f).stem}.json';out=ROOT/'.lake/build/lib/lean'/Path(f).with_suffix('.olean')
 if not p.is_file():errors.append(f'missing build record: {f}');continue
 r=json.loads(p.read_text());checks={
 'completed':r.get('returncode')==0 and not r.get('timed_out'),
 'source':r.get('source_sha256')==sha(ROOT/f),
 'output':out.is_file() and r.get('output_sha256')==sha(out),
 'log':r.get('log_sha256')==sha(ROOT/r['log']),
 'stable':r.get('source_unchanged') and r.get('imports_unchanged')}
 for name,digest in r.get('import_outputs',{}).items():
  p=ROOT/'.lake/build/lib/lean'/Path(name.replace('.','/')).with_suffix('.olean')
  checks['import '+name]=p.is_file() and sha(p)==digest
 if not all(checks.values()):errors.append({'target':f,'checks':checks})
 targets.append({'source':f,'passed':all(checks.values()),'record_sha256':sha(RD/f'clean_{Path(f).stem}.json')})
inv=read('results/v0.39.0/declaration_inventory.json');audit=read('results/v0.39.0/axiom_audit_summary.json')
if not(audit['passed'] and audit['expected']==len(inv) and audit['reports']==len(inv)):
 errors.append('axiom inventory mismatch')
neg=read('results/v0.39.0/negative_all/summary.json')
for r in neg['records']:
 if not r.get('expected_rejection'):errors.append('negative not substantive: '+r['source'])
 if r.get('source_sha256')!=sha(ROOT/r['source']):errors.append('negative stale source: '+r['source'])
 if r.get('log_sha256')!=sha(ROOT/r['log']):errors.append('negative stale log: '+r['source'])
 for name,digest in r.get('import_outputs',{}).items():
  p=ROOT/'.lake/build/lib/lean'/Path(name.replace('.','/')).with_suffix('.olean')
  if not p.is_file() or sha(p)!=digest:errors.append('negative stale import: '+r['source'])
scan=read('results/v0.39.0/source_scan.json')
if scan['hits']:errors.append('forbidden source shortcut')
pins=read('results/v0.39.0/dependency_pins.json')
if not all(x['passed'] for x in pins):errors.append('dependency pin mismatch')
reg=read('results/v0.39.0/calibration_regression.json')
if reg.get('status')!='passed' or reg.get('lean_crosscheck',{}).get('status')!='passed' or reg.get('lean_replanning',{}).get('status')!='passed':errors.append('calibration regression not passed')
for source,digest in reg.get('source_sha256',{}).items():
 if sha(ROOT/source)!=digest:errors.append('calibration regression stale source: '+source)
if not all(x.get('status')=='passed' for x in reg.get('interface',[])):errors.append('interface check not passed')
identity=read('results/v0.39.0/inherited_source_identity.json')
if identity['byte_identical']!=180:errors.append('inherited non-audit identity mismatch')
for record in identity['records']:
 if sha(ROOT/record['source'])!=record['sha256']:errors.append('inherited module changed: '+record['source'])
inherited=read('results/v0.39.0/inherited_regression_summary.json')
# Raw execution results retain their own schema/status; require each completed subprocess.
if inherited.get('status') not in ('passed','PASS') and inherited.get('result') not in ('passed','PASS'):
 if not(inherited.get('passed') is True or inherited.get('all_passed') is True):errors.append('inherited execution summary not passed')
counts=read('results/v0.39.0/source_counts.json')
result={'version':'0.39.0','passed':not errors,'errors':errors,'targets':len(order),
 'targets_passed':sum(x['passed'] for x in targets),'named_theorem_reports':len(inv),
 'axiom_union':audit['axiom_union'],'negative_tests':neg['total'],
 'substantive_negative_rejections':neg['substantive_rejections'],
 'source_counts':counts,'build_records':targets,
 'evidence_sha256':{f:sha(RD/f) for f in ['declaration_inventory.json','axiom_audit_summary.json','negative_all/summary.json','source_scan.json','calibration_regression.json','inherited_regression_summary.json','INDEPENDENT_REVIEW.md']}}
(RD/'release_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='build_records'},indent=2))
sys.exit(0 if result['passed'] else 1)
