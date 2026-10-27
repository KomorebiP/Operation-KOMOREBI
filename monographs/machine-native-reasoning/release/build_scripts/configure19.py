#!/usr/bin/env python3
"""Authenticate Core25 ancestry and configure prospective Core3.2 correspondence.

This is a source-map operation, not admission. Admission requires the actual two
cold gates and their comparison. Existing production Lean and original source
book files must be byte-identical to the accepted compact predecessor.
"""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = '206a735d18d4d96f8dfd32f80622f905f214233678f941dc0968c8205435ad45'
PREFIX = 'Machine_Native_Reasoning_Lean_Core25/'
NEW_MODULES = ['MachineTheory.PartitionOccupancy', 'MachineTheory.OccupancyBinary', 'MachineTheory.OccupancyExamples']

def sha(data): return hashlib.sha256(data).hexdigest()
def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--predecessor', type=Path, required=True)
    ap.add_argument('--endpoint', action='append', required=True,
                    help='Actual compiled theorem endpoint for the source map; repeat as needed.')
    args = ap.parse_args()
    data = args.predecessor.read_bytes()
    if sha(data) != EXPECTED:
        raise ValueError('Wrong accepted Core25 compact archive bytes')
    with zipfile.ZipFile(args.predecessor) as z:
        if z.testzip() is not None:
            raise ValueError('Predecessor ZIP CRC failure')
        manifest_bytes = z.read(PREFIX+'MANIFEST.json')
        manifest = json.loads(manifest_bytes)
        for row in manifest['files']:
            value = z.read(PREFIX+row['path'])
            if len(value) != row['bytes'] or sha(value) != row['sha256']:
                raise ValueError('Predecessor manifest mismatch: '+row['path'])
        all_names = {n for n in z.namelist() if not n.endswith('/')}
        declared = {PREFIX+r['path'] for r in manifest['files']}|{PREFIX+'MANIFEST.json'}
        if all_names != declared:
            raise ValueError('Predecessor manifest membership mismatch')
        preserve = [n for n in all_names if
                    (n.startswith(PREFIX+'MachineTheory/') and n.endswith('.lean')) or
                    n.startswith(PREFIX+'source/')]
        if len(preserve) != 80:
            raise ValueError('Expected 75 substantive Lean and five original source-book files')
        pins = {n[len(PREFIX):]: sha(z.read(n)) for n in sorted(preserve)}
        for rel, expected in pins.items():
            if sha((ROOT/rel).read_bytes()) != expected:
                raise ValueError('Inherited file changed: '+rel)
        history = ROOT/'evidence/history18'
        names = ['PREDECESSOR.json','MODULES.json','MachineTheory.lean','THEOREM_MAP.json',
                 'THEOREM_MAP.md','README.md','PROGRESS_LEDGER.md','CONTINUE_HERE.md',
                 'lakefile.toml','scripts/verify.py','scripts/compare_rebuild.py',
                 'checks/NEGATIVE_CONTROLS.json','release/REPORT.md',
                 'release/ADMISSION_RECORD.json','release/ACCEPTED_PROGRESS_LEDGER.md',
                 'release/NEXT_CORE32_SPEC.md']
        for name in names:
            path = history/name
            path.parent.mkdir(parents=True,exist_ok=True)
            previous = z.read(PREFIX+name)
            if path.exists() and path.read_bytes()!=previous:
                raise ValueError('Conflicting preserved history: '+name)
            path.write_bytes(previous)
        modules = json.loads(z.read(PREFIX+'MODULES.json'))
        if len(modules)!=76 or modules[-1]!='MachineTheory':
            raise ValueError('Wrong predecessor module order')
        write_json(ROOT/'MODULES.json', modules[:-1]+NEW_MODULES+modules[-1:])
        aggregate = z.read(PREFIX+'MachineTheory.lean').decode()
        (ROOT/'MachineTheory.lean').write_text(aggregate+''.join('\nimport '+m for m in NEW_MODULES)+'\n')
        predecessor = {'source_archive':args.predecessor.name, 'archive_sha256':EXPECTED,
            'archive_bytes':len(data), 'manifest_sha256':sha(manifest_bytes),
            'verified_manifest_files':len(manifest['files']),
            'scope':'Exact accepted Core25 compact source-and-receipts archive authenticated; all 75 inherited substantive Lean modules and five original source-book files are unchanged. Prior preserved evidence and historical omissions remain separate. No new recovery gap is introduced.',
            'required_unchanged':pins}
        write_json(ROOT/'PREDECESSOR.json',predecessor)
        mapping = json.loads(z.read(PREFIX+'THEOREM_MAP.json'))
        row = next(r for r in mapping if r['label']=='r:occupancy')
        if row['lean_endpoints']:
            raise ValueError('Predecessor unexpectedly mapped Core3.2 already')
        row.update(status='KERNEL_CHECKED_BLOCK19', lean_modules=NEW_MODULES,
                   lean_endpoints=args.endpoint)
        write_json(ROOT/'THEOREM_MAP.json',mapping)
        text = ['# Source-to-Lean map — cumulative Block 19','',
            'All 27 selected source statements have explicit endpoint targets. Admission is effective only after the complete current-source and independently extracted-source gates and their comparison pass. This source map alone is not a verification receipt. The unchanged source index fixes the statement identities.','']
        for row in mapping:
            text += [f"## {row['number']} — {row['title']}",
                     f"Source `{row['label']}`, original printed page {row['printed_page']}, lines {row['source_lines']}. Status: `{row['status']}`.",'']
            text += ['- `'+e+'`' for e in row['lean_endpoints']]
            text += ['']
        (ROOT/'THEOREM_MAP.md').write_text('\n'.join(text)+'\n')
    print('Prospective 27/27 map configured; 80 inherited source identities preserved. No admission asserted.')

if __name__=='__main__': main()
