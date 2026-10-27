#!/usr/bin/env python3
"""Run offline Python release acceptance and bind results to the tested sources.

Uses the locally bundled wheel, and records only the executing platform.
Lean acceptance is a separate workflow. Outputs must be a new directory.
Temporary installed environments are removed after their receipts are saved.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
sys.dont_write_bytecode = True
from verify_lineage import sha, verify_lineage
from release_gate import wheel_check

ROOT = Path(__file__).resolve().parents[1]

def sources() -> dict:
    paths = {p for base in ('python','scripts','tests') for p in (ROOT/base).rglob('*.py')
             if '__pycache__' not in p.parts}
    paths |= {ROOT/n for n in ('VERSION','pyproject.toml','README.md')}
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();out=a.output.resolve()
    try:out.mkdir(parents=True,exist_ok=False)
    except OSError as exc:
        print(json.dumps({'status':'FAIL','error':str(exc)}));return 2
    result={'schema':'komorebi.repair.release-acceptance.v1','status':'RUNNING',
            'started_utc':datetime.now(timezone.utc).isoformat(),
            'python':platform.python_version(),'platform':platform.platform(),
            'source_sha256':sources(),'commands':[],'checks':{}}
    def save(): (out/'acceptance.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    def check(name,ok,detail=None):
        result['checks'][name]={'pass':bool(ok),'detail':detail};save()
        if not ok:raise ValueError(name)
    def run(label,args,cwd=ROOT,timeout=240):
        env=os.environ.copy();env.update(PYTHONDONTWRITEBYTECODE='1',PYTHONPATH=str(ROOT/'python'))
        start=time.monotonic()
        q=subprocess.run([str(x) for x in args],cwd=cwd,env=env,capture_output=True,text=True,encoding='utf-8',timeout=timeout)
        txt=q.stdout+q.stderr;(out/(label+'.log')).write_text(txt,encoding='utf-8')
        result['commands'].append({'label':label,'argv':[str(x) for x in args],'returncode':q.returncode,
                                 'seconds':round(time.monotonic()-start,4),'log':label+'.log'})
        save();check(label,q.returncode==0)
        return txt
    try:
        wheel=wheel_check(ROOT);result['wheel_sha256']=wheel['sha256'];check('wheel_source_binding',True,wheel)
        txt=run('release_tests',[sys.executable,'-m','unittest','discover','-s',ROOT/'tests','-v'])
        match=re.search(r'Ran (\d+) tests',txt)
        check('release_test_count',match is not None and int(match[1])==100, None if match is None else int(match[1]))
        txt=run('engine_tests',[sys.executable,'-m','unittest','test_certificates','test_rational_menu','test_branch_menu'],cwd=ROOT/'python')
        match=re.search(r'Ran (\d+) tests',txt)
        check('engine_test_count',match is not None and int(match[1])==134,None if match is None else int(match[1]))
        run('platform_acceptance',[sys.executable,ROOT/'scripts/platform_acceptance.py','--output',out/'platform_acceptance'])
        platform_report=json.loads((out/'platform_acceptance/platform_report.json').read_text(encoding='utf-8'))
        check('installed_acceptance_status',platform_report['status']=='PASS')
        check('installed_wheel_binding',platform_report['wheel_sha256']==result['wheel_sha256'])
        check('installed_problem_count',platform_report['installed_cases']==72,platform_report['installed_cases'])
        result['installed_checks']=platform_report['installed_checks']
        result['platform_checks']=len(platform_report['checks'])
        check('installed_platform_checks',all(c['pass'] is True for c in platform_report['checks']))
        working=out/'platform_acceptance/working directory with spaces/donn\u00e9es and \u7814\u7a76/r\u00e9sultat'
        for name in ('input.json','certificate.json'):
            shutil.copyfile(working/name,out/('installed_'+name))
        shutil.rmtree(out/'platform_acceptance/isolated Python environment')
        result['isolated_environment_removed_after_receipt']=True
        lineage=verify_lineage(ROOT);check('historical_lineage',lineage['status']=='PASS',lineage)
        check('source_unchanged_during_acceptance',result['source_sha256']==sources())
        result.update(status='PASS',finished_utc=datetime.now(timezone.utc).isoformat());save()
        print(json.dumps({'status':'PASS','receipt':str(out/'acceptance.json'),
                          'scope':'Python acceptance, not kernel checking'}));return 0
    except Exception as exc:
        result.update(status='FAIL',error=str(exc),finished_utc=datetime.now(timezone.utc).isoformat());save()
        print(json.dumps({'status':'FAIL','error':str(exc),'receipt':str(out/'acceptance.json')}));return 1

if __name__=='__main__':raise SystemExit(main())
