#!/usr/bin/env python3
"""Validate the seven saved Paper XII run manifests; never rerun experiments."""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

SAVED_MANIFESTS=(
    'verification/computation/runs/fresh-20261006/appendix-exact/manifest.json',
    'verification/computation/runs/fresh-20261006/integrity/manifest.json',
    'verification/computation/runs/fresh-20261006/native-reverification-integrity/manifest.json',
    'verification/computation/runs/fresh-20261006/original-finite/manifest.json',
    'verification/computation/runs/fresh-20261006/orthogonal-primitives/manifest.json',
    'verification/computation/runs/fresh-20261006/orthogonal-primitives-safe/manifest.json',
    'verification/computation/runs/restored-integrity-20261006/integrity/manifest.json',
)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def now():
    return datetime.now(timezone.utc).isoformat()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',type=Path,required=True,help='Assembled project root containing source, downloads and verification.')
    ap.add_argument('--output',type=Path,default=Path('verification/computation/SAVED_RUN_VALIDATION.json'))
    args=ap.parse_args();root=args.root.resolve()
    if not root.is_dir():ap.error('root must be an existing project directory')
    validator=root/'verification/computation/tools/validate_manifest.py'
    report={'scope':'Saved bounded-run manifests validated against assembled input/result hashes; no mathematical experiment or Lean replay executed.',
            'started_utc':now(),'root':str(root),'expected_manifest_count':len(SAVED_MANIFESTS),
            'validator':str(validator.relative_to(root)),'validator_sha256':sha(validator) if validator.is_file() else None,
            'records':[]}
    required_inputs=set()
    for relative in SAVED_MANIFESTS:
        manifest=root/relative
        record={'manifest':relative,'status':'FAIL','manifest_sha256':sha(manifest) if manifest.is_file() else None}
        if not manifest.is_file():record['error']='Missing saved manifest'
        elif not validator.is_file():record['error']='Missing saved manifest validator'
        else:
            try:
                data=json.loads(manifest.read_text(encoding='utf-8'))
                names={x['path'] for x in data['input_artifacts']};required_inputs.update(names)
                argv=[sys.executable,str(validator),str(manifest),'--root',str(root)]
                run=subprocess.run(argv,capture_output=True,text=True,timeout=120)
                record.update(schema_version=data['schema_version'],input_artifact_count=len(data['input_artifacts']),
                              declared_result_count=len(data['declared_results']),argv=argv,
                              exit_code=run.returncode,stdout=run.stdout,stderr=run.stderr,
                              status='PASS' if run.returncode==0 else 'FAIL')
            except (OSError,ValueError,KeyError,subprocess.TimeoutExpired) as exc:
                record['error']=str(exc)
        report['records'].append(record)
    report.update(finished_utc=now(),passed_manifest_count=sum(r['status']=='PASS' for r in report['records']),
                  unique_declared_input_count=len(required_inputs),
                  required_non_source_inputs=sorted(p for p in required_inputs if not p.startswith('source/')))
    report['status']='PASS' if report['passed_manifest_count']==len(SAVED_MANIFESTS) else 'FAIL'
    output=args.output if args.output.is_absolute() else root/args.output
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(f"{report['status']}: {report['passed_manifest_count']}/{len(SAVED_MANIFESTS)} saved run manifests; {len(required_inputs)} unique declared inputs")
    print('Report:',output)
    if report['status']!='PASS':
        for r in report['records']:
            if r['status']!='PASS':print(r['manifest']+': '+r.get('error',r.get('stderr','') or r.get('stdout','')))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':sys.exit(main())
