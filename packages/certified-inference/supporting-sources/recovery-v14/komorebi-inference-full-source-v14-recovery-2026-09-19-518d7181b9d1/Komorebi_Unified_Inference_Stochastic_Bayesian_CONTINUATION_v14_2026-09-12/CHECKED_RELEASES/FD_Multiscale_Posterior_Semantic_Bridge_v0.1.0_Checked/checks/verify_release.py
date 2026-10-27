#!/usr/bin/env python3
"""Validate sealed-file hashes and theorem audit coverage without requiring Lean."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    bad=[];n=0
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        h,f=line.split(maxsplit=1);p=ROOT/f
        if not p.is_file() or sha(p)!=h:bad.append(f)
        n+=1
    if bad:raise RuntimeError('Hash mismatches: '+repr(bad))
    receipt=json.loads((ROOT/'FINAL_VERIFICATION_RECEIPT.json').read_text())
    modules=json.loads((ROOT/'MODULE_ORDER.json').read_text())
    if receipt['final_modules_passed']!=len(modules):raise RuntimeError('Module-count mismatch')
    for record in receipt['successful_final_modules']:
        source=ROOT/'Komorebi'/(record['module']+'.lean')
        if sha(source)!=record['source_sha256_before']:raise RuntimeError('Source mismatch')
        if record['exit_status']!=0:raise RuntimeError('Nonzero final module result')
    declarations=json.loads((ROOT/'DECLARATIONS.json').read_text())
    audit=json.loads((ROOT/'AXIOM_AUDIT.json').read_text())
    if set(audit['declarations'])!={x['name'] for x in declarations}:raise RuntimeError('Audit coverage mismatch')
    allowed={'propext','Classical.choice','Quot.sound'}
    if not set(audit['axiom_union'])<=allowed:raise RuntimeError('Unexpected axioms')
    manifest=json.loads((ROOT/'COMPUTATION_MANIFEST.json').read_text())
    required={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
    if required-set(manifest):raise RuntimeError('Missing manifest fields')
    if manifest['schema_version']!=1 or manifest['run']['exit_status']!=0:raise RuntimeError('Manifest state')
    for out in manifest['outputs']:
        if sha(ROOT/out['path'])!=out['sha256']:raise RuntimeError('Manifest output mismatch')
    print(f'PASS {n} file hashes; {len(modules)} module receipts; {len(declarations)} audited declarations; manifest output hashes')
if __name__=='__main__':main()
