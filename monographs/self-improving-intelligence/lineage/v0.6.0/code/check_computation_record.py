#!/usr/bin/env python3
"""Project-authored legacy-v1 computation-record checks, not an external attestation.

The field contract follows the computation-audit v1 template. This small checker
is NOT represented as an authenticated copy of the plugin's validator.
"""
from pathlib import Path
import hashlib,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=ROOT/'validation/computation_manifest.json';obj=json.loads(p.read_text());errors=[]
    required={'schema_version','claim_id','repository','command','environment','mathematics','randomness','run','outputs','checks','result','residual_risks'}
    if not required<=set(obj):errors.append('Missing top-level fields')
    if obj.get('schema_version')!=1:errors.append('Only the declared legacy v1 is accepted')
    for key in ('claim_id','result'):
        if not isinstance(obj.get(key),str) or not obj[key].strip():errors.append('Empty '+key)
    for k in ('assertion_tested','coefficient_domain','conventions','inputs','bounds','non_claims'):
        if not obj['mathematics'].get(k):errors.append('Missing mathematics.'+k)
    if not obj['environment'].get('software'):errors.append('Missing versions')
    run=obj['run']
    if not isinstance(run['runtime_seconds'],(int,float)) or not math.isfinite(run['runtime_seconds']) or run['runtime_seconds']<0:errors.append('Invalid runtime')
    if run['exit_status']!=0:errors.append('Nonzero scientific execution exit')
    if not run['started_at']:errors.append('Missing start')
    for item in obj['outputs']:
        q=ROOT/item['path']
        if not q.resolve().is_relative_to(ROOT.resolve()) or not q.is_file() or sha(q)!=item['sha256']:
            errors.append('Missing or changed output '+item['path'])
    receipt=json.loads((ROOT/'validation/execution_manifest.json').read_text())
    if receipt['status']!='PASS' or receipt['inputs_before']!=receipt['inputs_after']:errors.append('Input instability')
    for rel,h in receipt['inputs_after'].items():
        if not (ROOT/rel).is_file() or sha(ROOT/rel)!=h:errors.append('Changed input '+rel)
    totals=[]
    for file in ('finite_checks.json','discovery_checks.json','synthesis_checks.json','meta_checks.json'):
        x=json.loads((ROOT/'validation'/file).read_text());totals.append((len(x['groups']),sum(g['assertions'] for g in x['groups'])))
    if totals!=[(18,147180),(16,15604),(14,44359),(14,111024)]:errors.append('Unexpected scientific totals')
    out={'status':'PASS' if not errors else 'FAIL','errors':errors,'group_count':sum(g for g,a in totals),
         'assertions':sum(a for g,a in totals),
         'limitations':['Legacy schema does not itself require before/after hashes; the separate local receipt supplies them.',
                       'No Git revision or independent execution attestation.',
                       'Schema and hash checks do not verify general mathematical claims.']}
    (ROOT/'validation/computation_record_check.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['status'],out['group_count'],'groups',out['assertions'],'assertions; local legacy-record checks.')
    if errors:raise SystemExit('\n'.join(errors))
if __name__=='__main__':main()
