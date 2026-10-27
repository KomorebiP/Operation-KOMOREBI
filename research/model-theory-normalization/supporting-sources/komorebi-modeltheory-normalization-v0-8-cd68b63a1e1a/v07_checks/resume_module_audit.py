#!/usr/bin/env python3
"""Retain the second timed-out audit; use module-mode imports for unfinished checks."""
from pathlib import Path
import json
import audit_lean as audit
ROOT=Path(__file__).resolve().parents[1]
st=json.loads(audit.STATE.read_text());audit.verify(st)
assert st['status']=='FAILED' and st['tasks'][-1]['name']=='axioms_06_split1'
assert st['tasks'][-1]['timed_out'] and all(x['passed'] for x in st['tasks'][:-1])
p=ROOT/'v07_evidence/protocol_revision';p.mkdir(exist_ok=True)
assert not (p/'COLD_STATE_attempt2.json').exists()
(p/'COLD_STATE_attempt2.json').write_bytes(audit.STATE.read_bytes())
(p/'cold_driver_attempt2.log').write_bytes((ROOT/'v07_evidence/cold_driver_resume.log').read_bytes())
failed=st['tasks'][-1];n=len(st['tasks'])-1;plan=st['plan'][:n];added=[]
for old in st['plan'][n:]:
    src=Path(old['argv'][-1]);dest=src.with_name(src.stem+'_module.lean')
    dest.write_text('module\n'+src.read_text());added.append(dest)
    plan.append({**old,'name':old['name']+'_module','argv':old['argv'][:-1]+[str(dest)]})
rev={'started_at':audit.now(),'reason':'Second axiom batch exceeded 90 seconds. A module-mode probe of the actual generated theorem passed. Remaining audit drivers now opt into Lean module imports, consistent with the accepted library files.','failed_attempt':failed,'changed':'Audit driver headers only; same declaration inventory, same #print axioms command, same compiled proof bytes, same controls.','already_passed':n,'new_task_count':len(plan),'per_command_wall_cap_seconds':90,'same_mathematical_sources':True,'scope':'This is audit protocol repair, not a weakened proof or a reduced axiom inventory.'}
audit.dump(p/'REVISION2.json',rev)
st['plan']=plan;st['tasks']=st['tasks'][:-1];st['status']='IN_PROGRESS'
st['protocol_revision2']='v07_evidence/protocol_revision/REVISION2.json'
for f in added+[Path(__file__),p/'COLD_STATE_attempt2.json',p/'cold_driver_attempt2.log',p/'REVISION2.json',ROOT/'v07_evidence/AxiomModuleProbe.lean',ROOT/'v07_evidence/AxiomModuleProbe.json']:
    st['inputs'].append({'path':str(f.relative_to(ROOT)),'sha256':audit.sha(f)})
st['inputs']=sorted(st['inputs'],key=lambda x:x['path']);audit.verify(st);audit.dump(audit.STATE,st)
print(json.dumps(rev,indent=2))
