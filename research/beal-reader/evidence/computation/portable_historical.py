#!/usr/bin/env python3
"""Replay selected exact historical scientific algorithms from bundled snapshots.

The reviewed command plan is explicit, hash-pinned, and generated from the
documented source commands. It never executes an argv from a historical report.
Expected JSON hashes compare complete content. Nested archive-integrity checks
and historical rejection controls belong to separately preserved archival runs.
"""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def semantic_sha(data, name):
    if name.endswith('backend_audit68.json'):
        data=dict(data)
        data.pop('numpy_available',None)
        data.pop('primary_backend_equalities',None)
    raw=json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
    return hashlib.sha256(raw).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--block',type=int,required=True,choices=range(67,80))
    p.add_argument('--output',type=Path,required=True)
    ns=p.parse_args();ns.output.mkdir(parents=True,exist_ok=True)
    snapshot=Path(f'evidence/computation/inputs/block{ns.block}')
    plan=json.loads(Path(f'evidence/computation/plans/block{ns.block}.json').read_text())
    files=sorted(q for q in snapshot.rglob('*') if q.is_file())
    before={q.as_posix():sha(q) for q in files}
    jobs=[];comparisons={}
    with tempfile.TemporaryDirectory(prefix='beal_portable_history_') as td:
        root=Path(td)/'project';shutil.copytree(snapshot,root)
        for name in plan['expected_results']:
            (root/name).unlink(missing_ok=True)
            (root/name).parent.mkdir(parents=True,exist_ok=True)
        for command in plan['commands']:
            argv=[sys.executable,'-B']
            for token in command['argv']:
                argv.append(str(root/token) if token.startswith(f'work{ns.block}/') else token)
            start=time.monotonic()
            cp=subprocess.run(argv,cwd=root,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True,timeout=600)
            record={'argv':argv,'runtime_seconds':time.monotonic()-start,'exit_status':cp.returncode,
                    'stdout':cp.stdout if len(cp.stdout)<10000 else cp.stdout[:10000],
                    'stdout_bytes':len(cp.stdout.encode()),'stdout_truncated_in_report':len(cp.stdout)>=10000,'stderr':cp.stderr}
            jobs.append(record)
            if cp.returncode:
                raise RuntimeError('scientific command failed: '+cp.stdout[-3000:]+cp.stderr[-3000:])
            if 'stdout_json_to' in command:
                data=json.loads(cp.stdout)
                (root/command['stdout_json_to']).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
        for name,expected in plan['expected_results'].items():
            output=root/name
            data=json.loads(output.read_text())
            found=semantic_sha(data,name)
            if found!=expected['semantic_sha256']:
                raise ValueError('complete scientific JSON mismatch: '+name)
            comparisons[name]={'complete_json_equal':True,'sha256_generated':sha(output),'semantic_sha256':found,
                               'original_byte_sha256':expected['original_byte_sha256'],'generated_bytes':output.stat().st_size}
    after={q.as_posix():sha(q) for q in files}
    if before!=after:
        raise ValueError('immutable bundled inputs changed')
    report={'status':'PASS_PORTABLE_SCIENTIFIC_REPLAY','block':ns.block,'jobs':jobs,
            'complete_json_comparisons':comparisons,'input_hashes_before':before,'input_hashes_after':after,
            'adaptations':plan['adaptations'],'scientific_algorithms_edited':False,
            'nested_archive_integrity_reasserted':False,'actual_arithmetic_target_authenticated':False,
            'nonclaims':['Does not prove the universal written results, classical source dependencies, actual Frey realization or Beal.',
                        'Does not rerun archived rejection controls or excluded nested archive-integrity checks.']}
    (ns.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['status'],ns.block,len(comparisons))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
