#!/usr/bin/env python3
"""Compare the previous attached ZIP directly with the preserved source inputs.

This is a byte-provenance check, not theorem verification. It does not modify
source files or execute code from the older archive.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--archive', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    report = {'status': 'INCOMPLETE', 'started_utc': datetime.now(timezone.utc).isoformat(),
              'previous_archive': str(args.archive.resolve())}
    try:
        report['previous_archive_sha256'] = digest(args.archive.read_bytes())
        with zipfile.ZipFile(args.archive) as z:
            candidates = [n for n in z.namelist() if n.count('/') == 1 and n.endswith('/declaration_inventory.json')]
            if len(candidates) != 1:
                raise ValueError('Expected one top-level previous declaration inventory')
            prefix = candidates[0].split('/')[0] + '/'
            inv = json.loads(z.read(candidates[0]))
            paths = [m.replace('.', '/') + '.lean' for m in inv['modules']]
            paths.append('reference/Projector_Refinement_Physics_Complete_Unified_Theory.pdf')
            records = []
            for path in paths:
                before = digest(z.read(prefix + path))
                after = digest((ROOT / path).read_bytes())
                records.append({'path': path, 'archive_sha256': before,
                                'current_sha256': after, 'equal': before == after})
            report['compared_files'] = records
            report['previous_mathematical_modules'] = len(inv['modules'])
            if any(not record['equal'] for record in records):
                raise ValueError('At least one preserved input differs from the actual prior ZIP')
            report['status'] = 'PASS'
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        report.update(status='FAIL', error=str(error))
    report['finished_utc'] = datetime.now(timezone.utc).isoformat()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], 'Previous archive byte comparison:', args.out)
    return 0 if report['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
