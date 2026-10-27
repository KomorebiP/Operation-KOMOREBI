#!/usr/bin/env python3
"""Read-only integrity/evidence replay. Does not claim to recompile Lean."""
from pathlib import Path
import hashlib,json,re,sys,subprocess,os
root=Path(__file__).resolve().parent
errors=[];checks=0

def check(b,why):
 global checks
 checks+=1
 if not b:errors.append(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
entries={}
for line in (root/'CHECKSUMS.sha256').read_text().splitlines():
 h,p=line.split('  ',1);entries[p]=h
 path=Path(p)
 safe=not path.is_absolute() and '..' not in path.parts
 check(safe,'unsafe checksum path '+p)
 if safe:check((root/path).is_file() and sha(root/path)==h,'checksum '+p)
actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and '.lake' not in p.relative_to(root).parts and '__pycache__' not in p.relative_to(root).parts}
check(actual==set(entries)|{'CHECKSUMS.sha256'},'exact file inventory')
result=json.loads((root/'RESULTS.json').read_text());check(result['status']=='PASS','result status')
inv=json.loads((root/'verification/theorem_inventory.json').read_text());axioms=json.loads((root/'results/AXIOM_CLOSURES.json').read_text())
check(set(inv['names'])==set(axioms),'all theorem axiom closures accounted')
check(inv['total']==800 and inv['new']==61,'theorem inventory')
check(set().union(*(set(a) for a in axioms.values()))<={'propext','Quot.sound','Classical.choice'},'axiom policy')
for phase in result['final_phases']:
 label=phase['label'];r=json.loads((root/'results'/f'{label}.json').read_text());log=(root/'results'/f'{label}.log').read_text()
 check(r['exit']==phase['expected'],label+' exit')
 check(r['inputs_before']==r['inputs_after'] and r['inputs_unchanged'],label+' frozen input record')
 for p,h in r['inputs_after'].items():check((root/p).is_file() and sha(root/p)==h,label+' current input '+p)
 if label.startswith('final_negative_'):
  check(('declaration uses `sorry`' in log) if label.endswith('Placeholder') else ('is false' in log),label+' exact expected rejection')
check('Build completed successfully (2280 jobs).' in (root/'results/final_build.log').read_text(),'completed clean build log')
for row in json.loads((root/'PREDECESSOR_SOURCE_PRESERVATION.json').read_text())['modules']:
 check(sha(root/row['path'])==row['sha256'],'inherited source '+row['path'])
check(len(list((root/'compiled').rglob('*.olean')))==68,'compiled oleans')
check(len(list((root/'compiled').rglob('*.ilean')))==68,'compiled ileans')
audit=json.loads((root/'results/final_support_audit.json').read_text());check(audit['status']=='PASS' and audit['assertions']==20625,'finite assertion result')
manifest=json.loads((root/'COMPUTATION_MANIFEST.json').read_text())
for a in manifest.get('input_artifacts',[]):check(a['sha256']==a['sha256_after'] and sha(root/a['path'])==a['sha256'],'manifest input '+a['path'])
for a in manifest['outputs']:check(sha(root/a['path'])==a['sha256'],'manifest output '+a['path'])
print(json.dumps({'status':'PASS' if not errors else 'FAIL','checks':checks,'checksum_entries':len(entries),'errors':errors,'scope':'read-only retained-evidence and file integrity replay'},indent=2))
sys.exit(bool(errors))
