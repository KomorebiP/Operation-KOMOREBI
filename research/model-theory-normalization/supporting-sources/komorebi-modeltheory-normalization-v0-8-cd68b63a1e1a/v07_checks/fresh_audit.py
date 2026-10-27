#!/usr/bin/env python3
"""Start a fresh cold audit with module-mode, bounded-size axiom drivers.

Run in a copy and move aside the distributed COLD_STATE.json first. This changes
only the audit plan before any proof process is run, never the proof sources.
"""
from pathlib import Path
import argparse,json
import audit_lean as audit

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',required=True,type=Path);args=p.parse_args()
    audit.init(args.runtime.resolve())
    st=json.loads(audit.STATE.read_text());assert not st['tasks'];audit.verify(st)
    plan=[];extra=[]
    for item in st['plan']:
        if item.get('axioms'):
            old=Path(item['argv'][-1]);lines=old.read_text().splitlines()
            names=[line for line in lines if line.startswith('#print axioms ')]
            imports=[line for line in lines if line.startswith('import ')]
            for k,start in enumerate(range(0,len(names),80)):
                target=old.with_name('Fresh_'+old.stem+f'_{k}.lean')
                target.write_text('module\n'+'\n'.join(imports+names[start:start+80])+'\n')
                extra.append(target)
                plan.append({**item,'name':item['name']+f'_fresh{k}','argv':item['argv'][:-1]+[str(target)]})
        elif item['name'].startswith('control_'):
            old=Path(item['argv'][-1]);target=old.with_name('Fresh_'+old.name)
            target.write_text('module\n'+old.read_text());extra.append(target)
            plan.append({**item,'name':item['name']+'_fresh','argv':item['argv'][:-1]+[str(target)]})
        else:plan.append(item)
    st['plan']=plan
    for f in extra+[Path(__file__)]:
        st['inputs'].append({'path':str(f.relative_to(audit.ROOT)),'sha256':audit.sha(f)})
    st['inputs']=sorted(st['inputs'],key=lambda x:x['path']);audit.verify(st);audit.dump(audit.STATE,st)
    while len(json.loads(audit.STATE.read_text())['tasks'])<len(plan):audit.batch(1)
    audit.finish()
if __name__=='__main__':main()
