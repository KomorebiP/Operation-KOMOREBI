#!/usr/bin/env python3
"""Check this TOOLING checkpoint's manifest and recorded fixture evidence.

PASS refers only to this checkpoint. It never means Paper X is release-complete.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from audit_engine import AuditError,parse_json,verify_files
from verify_control_evidence import check
ROOT=Path(__file__).resolve().parents[1]

def verify(root:Path)->dict:
    m=parse_json((root/'MANIFEST.json').read_text(encoding='utf-8'))
    if m.get('schema')!='paper_x.tooling_checkpoint_manifest.v1':raise AuditError('Unknown manifest schema')
    v=verify_files(root,m['files'],strict=True,ignored=frozenset({'MANIFEST.json'}))
    controls=check(root)
    status=parse_json((root/'evidence/RECOVERY_STATUS.json').read_text())
    if status['paper_x_production_modules_checked_this_session']!=0 or status['paper_x_release_complete'] is not False:
        raise AuditError('Checkpoint makes an unsupported production claim')
    return {'status':'PASS','scope':'tooling checkpoint integrity and preserved fixture receipts',
            'files_verified':v['files'],'compiler_fixture_cases':controls['cases'],
            'paper_x_production_modules_checked_this_session':0,
            'paper_x_release_complete':False}
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=ROOT);a=ap.parse_args()
    try:print(json.dumps(verify(a.root),indent=2))
    except Exception as e:print('FAILED:',e,file=sys.stderr);sys.exit(1)
