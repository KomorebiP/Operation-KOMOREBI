#!/usr/bin/env python3
"""Assemble exact current correspondence input after all final source reviews.
This does not certify compiler execution and does not mutate release metadata.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, zipfile
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
ap.add_argument('--parent',type=Path,required=True)
ap.add_argument('--out',type=Path)
args=ap.parse_args();root=args.root.resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(c,m):
 if not c:raise ValueError(m)
def read(name):return json.loads((root/name).read_text())
review_names=['P66_REVIEW.json','P67_P80_REVIEW.json','P70_REVIEW.json','P79_ASSEMBLY_SCOPE.json','P79_REVIEW.json','P81_REVIEW.json','P82_P87_REVIEW.json','P87_REVIEW.json']
if (root/'verification/current_scope/SUPPORT_SOURCE_REPAIRS.json').is_file():review_names.append('SUPPORT_SOURCE_REPAIRS.json')
reviews={name:read('verification/current_scope/'+name) for name in review_names}
require(reviews['P79_REVIEW.json']['status']=='SOURCE_SCOPE_PASS_EXECUTION_PENDING','P79 source scope not final')
require(reviews['P79_REVIEW.json'].get('author_compile_passed') in (False,True),'Missing explicit P79 author execution status')
def check_hashes(obj):
 if isinstance(obj,list):
  for v in obj:check_hashes(v)
 if not isinstance(obj,dict):return
 freeze=obj.get('source_sha256')
 if isinstance(freeze,dict):
  for module,h in freeze.items():
   p=root/module if module.endswith('.lean') else root/'KomorebiLSM'/f'{module}.lean'
   require(isinstance(h,str) and p.is_file(),'Missing reviewed source: '+module)
   require(sha(p)==h,'Review source hash changed: '+module)
 for key in ('file','path'):
  if isinstance(obj.get(key),str) and isinstance(obj.get('sha256'),str):
   p=root/obj[key]
   if p.is_file():require(sha(p)==obj['sha256'],'Review file hash changed: '+obj[key])
 for v in obj.values():check_hashes(v)
for review in reviews.values():check_hashes(review)
claims={}
def add(entry):
 n=str(entry['proposition']);require(n not in claims,'Duplicate proposition review: '+n)
 claims[n]={k:entry[k] for k in ('scope','modules','endpoints')}
 claims[n]['modules']=[Path(m).stem if m.endswith('.lean') else m for m in claims[n]['modules']]
 claims[n]['status']=entry.get('status','complete')
 require(claims[n]['status']=='complete','Unfinished source correspondence: P'+n)
for name in ('P67_P80_REVIEW.json','P82_P87_REVIEW.json'):
 for entry in reviews[name]['entries']:add(entry)
p81=reviews['P81_REVIEW.json'];add({'proposition':81,**{k:p81[k] for k in ('scope','modules','endpoints')}})
add({'proposition':70,**read('verification/current_scope/P70_CFG.json')})
p79=reviews['P79_ASSEMBLY_SCOPE.json'];add({'proposition':79,**{k:p79[k] for k in ('scope','modules','endpoints')}})
add({'proposition':66,'status':'complete',
 'scope':'Full arbitrary measurable probability-space time-uniform predictable residual certificate for actual conditional means, all positive times, finite/countable prospectively registered rules with literal summable budgets, exact interval-width scaling including zero width, measurable simultaneous residual/drift event, exact equivalence relabeling, and pathwise data-selected positive times/rules. No StandardBorelSpace, independence, stationarity or supplied concentration conclusion.',
 'modules':['ConditionalBernoulli','ConditionalHoeffding','CountableConfidence','PredictableResidualGeneral','PredictableResidualAnytime','PredictableResidualAffine','PredictableResidualP66'],
 'endpoints':['Komorebi.LSM.PredictableResidualGeneral.predictable_residual_interval_certificate','Komorebi.LSM.PredictableResidualGeneral.predictable_residual_interval_finite','Komorebi.LSM.PredictableResidualGeneral.registration_transport','Komorebi.LSM.PredictableResidualGeneral.selected_interval_bound']})
with zipfile.ZipFile(args.parent) as z:
 prefix='Large_Signal_Model/Lean/'
 old_modules=re.findall(r'^import KomorebiLSM\.(\w+)$',z.read(prefix+'KomorebiLSM.lean').decode(),re.M)
 parent_coverage=json.loads(z.read(prefix+'COVERAGE.json'))
expected={str(e['proposition']) for e in parent_coverage['entries'] if e['status']!='complete'}
require(set(claims)==expected,'Claim coverage differs: missing='+str(expected-set(claims))+', extra='+str(set(claims)-expected))
spec=importlib.util.spec_from_file_location('lsm_inventory',root/'scripts/build_inventory.py')
index=importlib.util.module_from_spec(spec);spec.loader.exec_module(index)
records=[d for p in sorted((root/'KomorebiLSM').glob('*.lean')) for d in index.scan_file(p)]
by_name={d['name']:d for d in records};require(len(by_name)==len(records),'Duplicate source declaration')
all_modules={p.stem for p in (root/'KomorebiLSM').glob('*.lean')}
for n,claim in claims.items():
 require(bool(claim['endpoints']),'Empty endpoint set for P'+n)
 require(all(name in by_name for name in claim['endpoints']),'Unknown endpoint in P'+n)
 # Lean namespaces can span modules. Resolve actual source module for every endpoint.
 claim['modules']=sorted(set(claim['modules'])|{by_name[name]['module'] for name in claim['endpoints']})
 require(set(claim['modules'])<=all_modules,'Unknown mapped module for P'+n)
new_modules=sorted(all_modules-set(old_modules))
cfg={'source_scope_ready':True,'acceptance_scope':'Full registered proposition correspondence only; cumulative execution acceptance remains separate.','execution_accepted':False,
 'modules':new_modules,'accepted_source_sha256':{m:sha(root/'KomorebiLSM'/f'{m}.lean') for m in new_modules},
 'review_records':{'verification/current_scope/'+name:sha(root/'verification/current_scope'/name) for name in review_names},
 'claims':{str(n):claims[str(n)] for n in sorted(map(int,claims))}}
out=args.out or root/'Development_Tools/accepted_claims_v019.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(cfg,indent=2,ensure_ascii=False)+'\n')
print(f'Prepared {len(claims)} newly complete mappings over {len(new_modules)} new modules; cumulative execution still required: {out}')
