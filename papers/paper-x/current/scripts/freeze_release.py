#!/usr/bin/env python3
"""Seal the reviewed release tree by exact regular-file membership and SHA-256."""
from pathlib import Path
import hashlib, json, stat
ROOT = Path(__file__).resolve().parents[1]
def main():
    (ROOT/'MANIFEST.json').write_text(json.dumps({
        'role':'manifest_filename_pointer',
        'authoritative_manifest':'MANIFEST_SHA256.json',
        'verification_command':'python3 -B verify_release.py --strict',
        'scope':'The authoritative strict manifest covers exact regular-file membership, sizes and SHA-256.'
    },indent=2)+'\n')
    rows = []
    for path in sorted(ROOT.rglob('*')):
        if path.is_symlink():
            raise SystemExit('Refusing symlink: '+str(path))
        mode = path.stat().st_mode
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise SystemExit('Refusing nonregular member: '+str(path))
        if path == ROOT/'MANIFEST_SHA256.json':
            continue
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            for block in iter(lambda:stream.read(1024*1024), b''):
                digest.update(block)
        rows.append({'path':path.relative_to(ROOT).as_posix(),'bytes':path.stat().st_size,'sha256':digest.hexdigest()})
    record = {'schema':'komorebi.strict_manifest.v1','checkpoint':'P10-REBASE-001',
              'edition':'1.0.0 / 2026-10-20',
              'scope':'Exact release-file integrity only; proof and computation evidence have separate contracts.',
              'files':rows}
    (ROOT/'MANIFEST_SHA256.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'manifest_files':len(rows),'bytes':sum(row['bytes'] for row in rows)}))
if __name__ == '__main__':
    main()
