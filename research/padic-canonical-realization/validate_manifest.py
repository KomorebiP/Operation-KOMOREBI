#!/usr/bin/env python3
"""Project-local validation of a populated v1 computation manifest.
Checks the Mathbox v1 evidence fields, hashes, and our additional input receipts.
This local validator is not a claim that the installed plugin's full v2 validator ran.
"""
from pathlib import Path
import argparse,hashlib,json,math,re

def validate(m,root):
    e=[]
    def check(c,s):
        if not c:e.append(s)
    check(m.get('schema_version')==1,'schema version')
    for k in ('claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'):
        check(bool(m.get(k)),f'missing {k}')
    for k in ('assertion_tested','coefficient_domain','conventions','inputs','bounds','non_claims'):
        check(bool(m.get('mathematics',{}).get(k)),f'mathematics.{k}')
    check(type(m['repository'].get('dirty')) is bool,'dirty flag')
    check(type(m['run'].get('exit_status')) is int,'exit status')
    check(isinstance(m['run'].get('runtime_seconds'),(float,int)) and math.isfinite(m['run']['runtime_seconds']) and m['run']['runtime_seconds']>=0,'runtime')
    for a in m['outputs']+m.get('input_artifacts',[]):
        path=Path(a['path']);check(not path.is_absolute() and '..' not in path.parts,'unsafe path')
        if path.is_absolute() or '..' in path.parts:continue
        q=root/path;check(q.is_file(),f'missing {path}')
        if q.is_file():check(hashlib.sha256(q.read_bytes()).hexdigest()==a['sha256'],f'hash {path}')
    return e
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('manifest',type=Path);ap.add_argument('--root',type=Path,required=True);a=ap.parse_args()
    errors=validate(json.loads(a.manifest.read_text()),a.root)
    print(json.dumps({'status':'PASS' if not errors else 'FAIL','errors':errors,'scope':'project-local v1 field and input/output hash validation'},indent=2))
    raise SystemExit(bool(errors))
