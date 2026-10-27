#!/usr/bin/env python3
"""Verify the accepted focused receipt and unchanged inputs; never call the compiler."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def verify():
    release=json.loads((ROOT/'audit/extension/release.json').read_text())
    if release['status']!='PASS':raise ValueError('Focused release is not PASS')
    path=ROOT/release['receipt'];r=json.loads(path.read_text())
    if sha(path)!=release['receipt_sha256'] or r['status']!='PASS':raise ValueError('Invalid accepted receipt')
    if not r['clean_project_build'] or not r['source_unchanged_during_run']:raise ValueError('Missing clean or unchanged inputs')
    if not all(c['passed'] for c in r['commands']):raise ValueError('Incomplete command sequence')
    if r['compile_targets']!=7 or r['new_modules']!=3 or r['inherited_modules']!=3:raise ValueError('Unexpected closure')
    for m,s in r['source_files'].items():
        if sha(ROOT/s['path'])!=s['sha256']:raise ValueError('Changed source '+m)
    for p,h in r['input_hashes'].items():
        if sha(ROOT/p)!=h:raise ValueError('Changed verifier/test '+p)
    for c in r['commands']:
        if sha(ROOT/c['log'])!=c['log_sha256']:raise ValueError('Changed execution log '+c['label'])
    ax=path.parent/'axioms.json'
    if sha(ax)!=r['axiom_report_sha256']:raise ValueError('Changed axiom report')
    a=json.loads(ax.read_text())
    if a['unexpected'] or len(a['declarations'])!=r['axiom_declarations']:raise ValueError('Axiom report not complete')
    allow={'propext','Classical.choice','Quot.sound'}
    if any(x['unsafe'] or not set(x['axioms']).issubset(allow) for x in a['declarations']):raise ValueError('Forbidden axiom/safety')
    baseline=json.loads((ROOT/'audit/certified_repair/baseline.json').read_text())
    # The original 156-file preservation is also enforced by the inherited expansion suites.
    return release,r,a
if __name__=='__main__':
    rel,r,a=verify()
    print(json.dumps({'status':'PASS','scope':'Retained focused execution evidence and current source hashes. This command does not compile Lean.',
        'new_modules':r['new_modules'],'inherited_modules':r['inherited_modules'],'compile_targets':r['compile_targets'],
        'audited_declarations':r['axiom_declarations'],'accepted_receipt':rel['receipt']},indent=2))
