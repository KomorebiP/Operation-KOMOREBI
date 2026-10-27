#!/usr/bin/env python3
"""Audit actual constructed bundle objects after a completed cumulative run.
Author: Komorebi P. Does not rebuild or independently recheck Mathlib.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from verify import ALLOWED_AXIOMS, MODULES, artifacts_match, parse_axiom_audits, run, sha

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--kit',type=Path,required=True)
    ap.add_argument('--run',type=Path,required=True,help='Completed cumulative run directory')
    ap.add_argument('--timeout',type=int,default=180)
    args=ap.parse_args()
    if args.timeout<1:ap.error('timeout must be positive')
    base=Path(__file__).resolve().parents[1]
    folder=args.run.resolve(); build=folder/'build'; summary=folder/'SUMMARY.json'
    prior=json.loads(summary.read_text())
    if not prior.get('pass') or not prior.get('complete'):
        raise ValueError('A completed successful cumulative run is required')
    if set(r['module'] for r in prior['modules']) != set(MODULES):
        raise ValueError('Cumulative module inventory mismatch')
    for row in prior['modules']:
        source=base/row['source']
        if sha(source)!=row['sha256'] or not artifacts_match(build,row['module'],row['build_sha256']):
            raise ValueError('Stale source or compiled interface: '+row['module'])
    inventory=base/'verification/constructed_objects_inventory.json'
    expected=set(json.loads(inventory.read_text()))
    source=base/'verification/constructed_objects_audit.lean'
    runner=base/'scripts/check_low_memory.py'
    cmd=[sys.executable,str(runner),'--kit',str(args.kit.resolve()),'--timeout',str(args.timeout),
         '--import-dir',str(build),str(source)]
    rc,log,seconds=run(cmd,args.timeout+90)
    logfile=folder/'constructed_objects.log';logfile.write_text(log)
    audits=parse_axiom_audits(log)
    unexpected={n:sorted(set(a)-ALLOWED_AXIOMS) for n,a in audits.items() if set(a)-ALLOWED_AXIOMS}
    good=rc==0 and set(audits)==expected and not unexpected
    result={'pass':good,'construction_count':len(expected),'axiom_audits':audits,
            'unexpected_axioms':unexpected,'exit_code':rc,'seconds':seconds,'command':cmd,
            'source':str(source.relative_to(base)),'source_sha256':sha(source),
            'inventory_sha256':sha(inventory),'runner_sha256':sha(runner),'log_sha256':sha(logfile),
            'cumulative_summary_sha256':sha(summary),'scope':'Six constructed objects, separate from theorem counts'}
    (folder/'CONSTRUCTED_OBJECTS_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(('PASS' if good else 'FAIL')+': '+str(len(audits))+' constructed-object axiom audits')
    if not good:print(log)
    return 0 if good else 1

if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,KeyError,ValueError) as exc:
        print('Construction audit failed: '+str(exc),file=sys.stderr);raise SystemExit(1)
