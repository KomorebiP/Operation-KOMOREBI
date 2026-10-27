#!/usr/bin/env python3
"""Compare actual completed cold proof runs. Production object identity is mandatory.
Generated audit-helper binary identity is recorded separately; identical helper source
and complete axiom records remain mandatory. This is not an independent proof kernel.
"""
from __future__ import annotations
import argparse, datetime, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def sha(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as s:
        for b in iter(lambda:s.read(4<<20),b''):h.update(b)
    return h.hexdigest()
def load(p: Path):return json.loads(p.read_text(encoding='utf-8'))
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--final',type=Path,required=True)
    ap.add_argument('--fresh',type=Path,required=True)
    ap.add_argument('--snapshot',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args(); f=load(a.final/'report.json');g=load(a.fresh/'report.json');checks={}
    for name,d in [('final',f),('fresh',g)]:
        checks[name+'_status']=d.get('status')=='PASS'
        checks[name+'_all_steps_pass']=all(s['passed'] for s in d['steps'])
        checks[name+'_no_timeout']=not any(s['timed_out'] for s in d['steps'])
        checks[name+'_stable_inputs']=d['input_sha256_before']==d['input_sha256_after']
    keys=['input_sha256_before','input_sha256_after','lean_version','dependency_revisions',
          'preserved_predecessor_files','authored_declaration_count','authored_theorem_count',
          'source_results_formalized','source_results_not_formalized','axiom_audited_declarations',
          'compiled_theorem_constants_including_generated','actual_axiom_union','negative_controls',
          'matched_upstream_artifacts','imported_module_count_including_audit_tools']
    for k in keys:checks[k]=f[k]==g[k]
    for name in ['source_inventory.json','environment_constants.json','axioms.json','dependency_artifacts.json','preservation.json']:
        checks[name]=load(a.final/name)==load(a.fresh/name)
    checks['audit_source']=(a.final/'Audit.lean').read_bytes()==(a.fresh/'Audit.lean').read_bytes()
    checks['step_outcomes']=[(s['name'],s['exit_code'],s['expected_success'],s['passed'],s['timed_out']) for s in f['steps']]==[(s['name'],s['exit_code'],s['expected_success'],s['passed'],s['timed_out']) for s in g['steps']]
    modules=load(ROOT/'MODULES.json');objects={}
    for module in modules:
        rel=module.replace('.','/')+'.olean'
        h1=sha(a.final/'objects'/rel);h2=sha(a.fresh/'objects'/rel)
        checks['production_'+module]=(h1==h2==f['local_object_sha256'][rel]==g['local_object_sha256'][rel])
        objects[module]={'final_sha256':h1,'fresh_sha256':h2,'identical':h1==h2}
    for rel,h in f['input_sha256_after'].items():checks['delivered_input_'+rel]=sha(ROOT/rel)==h
    helpers={}
    for rel in sorted(set(f['local_object_sha256'])|set(g['local_object_sha256'])):
        if rel.startswith('MachineTheory'):continue
        h1=sha(a.final/'objects'/rel);h2=sha(a.fresh/'objects'/rel)
        checks['helper_receipt_'+rel]=h1==f['local_object_sha256'][rel] and h2==g['local_object_sha256'][rel]
        helpers[rel]={'final_sha256':h1,'fresh_sha256':h2,'identical':h1==h2}
        if rel!='Audit.olean':checks['helper_identity_'+rel]=h1==h2
    import zipfile
    with zipfile.ZipFile(a.snapshot) as z:
        checks['fresh_source_no_local_objects']=not any(n.endswith(('.olean','.ilean','.c','.o')) for n in z.namelist())
    out={'schema':'komorebi.block12.fresh-rebuild.v1','status':'PASS' if all(checks.values()) else 'FAIL',
         'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'source_snapshot_sha256':sha(a.snapshot),'source_snapshot_scope':'Pinned source, documentation and runtime recovery receipts extracted into a fresh folder without local compiled objects.',
         'final_receipt_sha256':sha(a.final/'report.json'),'fresh_receipt_sha256':sha(a.fresh/'report.json'),
         'comparisons':checks,'production_objects':objects,'nonproduction_objects':helpers,
         'production_object_count':len(objects),'final_seconds':f['total_seconds'],'fresh_seconds':g['total_seconds'],
         'non_claims':['No upstream source rebuild','No independent kernel implementation','No byte-identity claim for a generated audit helper if separately marked different','No cross-platform or physical-model validation']}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],len(checks),'comparisons;',len(objects),'production objects')
    if not all(checks.values()):print('Failed:',[k for k,v in checks.items() if not v])
    return 0 if all(checks.values()) else 1
if __name__=='__main__':raise SystemExit(main())
