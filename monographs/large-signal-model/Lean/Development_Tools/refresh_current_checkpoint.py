#!/usr/bin/env python3
"""Refresh current metadata after reviewed proof/API edits, without a new parent snapshot.
Mathematical source is never edited. Execution acceptance stays pending.
"""
from pathlib import Path
import argparse, hashlib, json, re, subprocess, sys, zipfile
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
args=ap.parse_args();root=args.root.resolve()
def read(rel):return json.loads((root/rel).read_text())
def write(rel,obj):(root/rel).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(c,m):
 if not c:raise ValueError(m)
status=read('CURRENT_STATUS.json')
require(status['verification_passed'] is False and status['goal_reached'] is False,'Invalidate execution acceptance explicitly before changing checked metadata')
cfg=read('Development_Tools/accepted_claims_v019.json')
lineage=read('SOURCE_LINEAGE.json')
for module,h in cfg['accepted_source_sha256'].items():require(sha(root/'KomorebiLSM'/f'{module}.lean')==h,'Accepted source changed: '+module)
for rel,h in cfg['review_records'].items():require(sha(root/rel)==h,'Source review changed: '+rel)
for rel,h in lineage['inherited_proof_files'].items():require(sha(root/rel)==h,'Inherited mathematical source changed: '+rel)
subprocess.run([sys.executable,str(root/'scripts/build_inventory.py'),'--write'],check=True)
decls=read('DECLARATIONS.json');by_name={d['name']:d for d in decls};require(len(by_name)==len(decls),'Duplicate declaration name')
modules=re.findall(r'^import KomorebiLSM\.(\w+)$',(root/'KomorebiLSM.lean').read_text(),re.M)
require(set(modules)=={p.stem for p in (root/'KomorebiLSM').glob('*.lean')},'Root import/source omission')
parent=lineage['predecessor_archive']
with zipfile.ZipFile(root/parent['path']) as z:
 baseline=json.loads(z.read('Large_Signal_Model/Lean/RELEASE_COUNTS.json'))
nt=sum(d['kind']=='theorem' for d in decls)
example_modules=sorted({d['module'] for d in decls if d['module']=='Examples' or re.fullmatch(r'Block\d+.*Examples',d['module'])})
ne=sum(d['kind']=='theorem' and d['module'] in example_modules for d in decls)
cover=read('COVERAGE.json');changed_targets=0
for entry in cover['entries']:
 claim=cfg['claims'].get(str(entry['proposition']))
 if claim:
  require(entry['status']==claim['status']=='complete','Scope status unexpectedly changed')
  targets=[d for d in decls if d['module'] in claim['modules']]
  require(all(name in by_name for name in claim['endpoints']),'Missing reviewed endpoint')
  entry['scope']=claim['scope']
 else:targets=[by_name[d['name']] for d in entry['lean_targets']]
 new=[{**d,'source_sha256':sha(root/d['file'])} for d in targets]
 changed_targets+=sum(a!=b for a,b in zip(entry['lean_targets'],new))+abs(len(entry['lean_targets'])-len(new))
 entry['lean_targets']=new
complete=[e['proposition'] for e in cover['entries'] if e['status']=='complete']
require(complete==list(range(1,88)),'Full registered coverage changed')
write('COVERAGE.json',cover)
coverage_lines=['# Formal coverage','','87 complete mappings, 0 partial and 0 unformalized. Counts are not weighted by proof difficulty.','','| Proposition | Status | Mapped scope |','|---|---|---|']
for entry in cover['entries']:coverage_lines.append(f"| P{entry['proposition']}: {entry['title']} | {entry['status']} | {entry['scope'].replace('|','/')} |")
(root/'COVERAGE.md').write_text('\n'.join(coverage_lines)+'\n')
counts=read('RELEASE_COUNTS.json')
counts.update(proof_modules=len(modules),named_declarations=len(decls),named_theorems=nt,
 example_theorems=ne,supporting_theorems=nt-ne,new_theorems=nt-baseline['named_theorems'],
 new_example_theorems=ne-baseline['example_theorems'],negative_controls=len(list((root/'negative_controls').glob('*.lean'))),
 complete_propositions=87,partial_propositions=0,unformalized_propositions=0)
write('RELEASE_COUNTS.json',counts)
cp=read('CURRENT_CHECKPOINT.json');cp['counts']=counts;cp['new_module_hashes']=cfg['accepted_source_sha256']
if (root/'verification/current_scope/SUPPORT_SOURCE_REPAIRS.json').is_file():
 cp['post_integration_support_repairs']={'review':'verification/current_scope/SUPPORT_SOURCE_REPAIRS.json','review_sha256':sha(root/'verification/current_scope/SUPPORT_SOURCE_REPAIRS.json'),'execution':'See the canonical cumulative compiler and kernel report; raw correspondence does not certify execution.'}
cp.pop('post_integration_certificate_refactor',None)
refactors=[]
for rel in ['verification/p79_perf/RATIONAL_PROOF_REFACTOR.json','verification/p79_perf/COEFFICIENT_KERNEL_REFACTOR.json','verification/p79_perf/COEFFICIENT_KERNEL_REFACTOR_14TH.json','verification/p79_perf/COEFFICIENT_KERNEL_REFACTOR_15TH.json']:
 if (root/rel).is_file():refactors.append({'record':rel,'sha256':sha(root/rel)})
if refactors:cp['post_integration_certificate_refactors']={'records':refactors,'scope':'Exact witness data and public mathematical statements retained; proof implementations and source locations refreshed.','execution':'See canonical cumulative compiler and kernel checking.'}
cp['inherited_control_repairs']={'manifest':lineage.get('control_repair_manifest'),'counts':{'original_inherited':len(lineage['inherited_control_files']),'repaired':len(lineage.get('inherited_control_repairs',{})),'unchanged':len(lineage['inherited_control_files'])-len(lineage.get('inherited_control_repairs',{}))}}
write('CURRENT_CHECKPOINT.json',cp)
progress=read('PROGRESS.json');progress['counts']=counts;write('PROGRESS.json',progress)
old_input=read('verification/current_scope/INTEGRATION_INPUT.json');cfg['modules']=old_input['modules'];write('verification/current_scope/INTEGRATION_INPUT.json',cfg)
p=root/'scripts/check_metadata.py';s=p.read_text()
replacements=[
 (r"record\('\d+ unique named declarations'",f"record('{len(decls)} unique named declarations'"),
 (r"counts\['named_declarations'\] == \d+",f"counts['named_declarations'] == {len(decls)}"),
 (r"record\('\d+ named theorems, \d+ in example modules'",f"record('{nt} named theorems, {ne} in example modules'"),
 (r"counts\['named_theorems'\]==\d+",f"counts['named_theorems']=={nt}"),
 (r"counts\['example_theorems'\]==\d+",f"counts['example_theorems']=={ne}"),
 (r"All \d+ proof modules",f'All {len(modules)} proof modules'),
 (r"len\(set\(root_modules\)\)==\d+",f'len(set(root_modules))=={len(modules)}'),
 (r"All \d+ negative controls",f"All {counts['negative_controls']} negative controls"),
 (r"counts\['negative_controls'\]==\d+",f"counts['negative_controls']=={counts['negative_controls']}")]
for pattern,replacement in replacements:
 s,n=re.subn(pattern,lambda _:replacement,s);require(n==1,'Expected one numeric metadata contract: '+pattern)
p.write_text(s)
require(read('CURRENT_STATUS.json')==status,'Execution status was changed by refresh')
print(json.dumps({'counts':counts,'changed_target_records':changed_targets,'execution_accepted':False}))
