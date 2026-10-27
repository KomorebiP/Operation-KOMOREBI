#!/usr/bin/env python3
"""Run every delivered unittest and write a nonoverwriting report directory."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
import time
import unittest
from audit_engine import AuditError,save_json,sha256,utc
ROOT=Path(__file__).resolve().parents[1]

def run(out:Path)->dict:
    if out.exists():raise AuditError('Choose a new report directory')
    out.mkdir(parents=True)
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    def ids(s):
        for x in s:
            if isinstance(x,unittest.TestSuite):yield from ids(x)
            else:yield x.id()
    tests=list(ids(suite));start=time.monotonic()
    with (out/'unittest.log').open('x',encoding='utf-8') as f:
        result=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
    r={'status':'PASS' if result.wasSuccessful() and result.testsRun==len(tests) and not result.skipped else 'FAILED',
       'scope':'verification-tool unit and receipt-mutation tests, not mathematical theorem counts',
       'recorded_utc':utc(),'tests_run':result.testsRun,'tests':tests,
       'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),
       'seconds':round(time.monotonic()-start,4),
       'log_sha256':sha256(out/'unittest.log'),
       'source_pins':{p.relative_to(ROOT).as_posix():sha256(p)
         for folder in ('scripts','tests','lean') for p in (ROOT/folder).rglob('*') if p.is_file()}}
    save_json(out/'TESTS.json',r);return r
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
    try:
        r=run(a.out);print(r['status'],r['tests_run'],'tests');sys.exit(0 if r['status']=='PASS' else 1)
    except Exception as e:print('FAILED:',e,file=sys.stderr);sys.exit(1)
