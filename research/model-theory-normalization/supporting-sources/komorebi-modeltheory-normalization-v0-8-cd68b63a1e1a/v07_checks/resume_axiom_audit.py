#!/usr/bin/env python3
"""Preserve a timed-out audit and split only its uncompleted axiom batches.

No mathematical source or compiled artifact may change. Previously completed
checks remain checks of the same bytes; the failed attempt is retained separately.
"""
from pathlib import Path
import hashlib,json
import audit_lean as audit
ROOT=Path(__file__).resolve().parents[1]
state=json.loads(audit.STATE.read_text())
audit.verify(state)
assert state['status']=='FAILED'
assert len(state['tasks'])==50 and all(t['passed'] for t in state['tasks'][:-1])
failed=state['tasks'][-1]
assert failed['name']=='axioms_05' and failed['timed_out']
preserved=ROOT/'v07_evidence/protocol_revision'
preserved.mkdir(exist_ok=True)
assert not (preserved/'COLD_STATE_attempt1.json').exists()
(preserved/'COLD_STATE_attempt1.json').write_bytes(audit.STATE.read_bytes())
(preserved/'cold_driver_attempt1.log').write_bytes((ROOT/'v07_evidence/cold_driver.log').read_bytes())
old_plan=state['plan']
plan=old_plan[:49]
new_files=[]
for item in old_plan[49:]:
    if not item.get('axioms'):
        plan.append(item); continue
    original=Path(item['argv'][-1])
    names=[line.removeprefix('#print axioms ') for line in original.read_text().splitlines() if line.startswith('#print axioms ')]
    assert names
    by_name={x['name']:x['module'] for x in state['declarations']}
    for block,start in enumerate(range(0,len(names),80)):
        group=names[start:start+80]
        name=item['name']+f'_split{block}'
        p=ROOT/'v07_checks/axioms'/f'{name}.lean'
        p.write_text(''.join('import '+m.replace('/','.')+'\n' for m in dict.fromkeys(by_name[n] for n in group))+''.join('#print axioms '+n+'\n' for n in group))
        new_files.append(p)
        plan.append({**item,'name':name,'argv':item['argv'][:-1]+[str(p)]})
state['plan']=plan
state['tasks']=state['tasks'][:-1]
state['status']='IN_PROGRESS'
state['revision_started_at']=audit.now()
revision={'reason':'One axiom group reached its 90-second wall cap after all 44 proof builds and five earlier axiom groups passed.','changed':'Only unfinished axiom grouping changes, from at most 160 names to at most 80. No accepted mathematical source or build artifacts change.','failed_attempt':failed,'preserved_state_sha256':audit.sha(preserved/'COLD_STATE_attempt1.json'),'old_task_count':len(old_plan),'new_task_count':len(plan),'already_passed':49,'max_names_per_new_group':80,'per_command_seconds':90,'scope':'Same complete declaration inventory; deliberate negative controls remain mandatory.'}
audit.dump(preserved/'REVISION.json',revision)
for p in new_files+[Path(__file__),preserved/'COLD_STATE_attempt1.json',preserved/'cold_driver_attempt1.log',preserved/'REVISION.json']:
    state['inputs'].append({'path':str(p.relative_to(ROOT)),'sha256':audit.sha(p)})
state['inputs']=sorted(state['inputs'],key=lambda x:x['path'])
state['protocol_revision']='v07_evidence/protocol_revision/REVISION.json'
audit.verify(state);audit.dump(audit.STATE,state)
print(json.dumps(revision,indent=2))
