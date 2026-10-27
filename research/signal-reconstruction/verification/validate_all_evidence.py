#!/usr/bin/env python3
"""Validate all current and retained v2 evidence records, without rerunning science."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

def main():
    paths = set((ROOT / 'verification/runs').glob('*/*/manifest.json'))
    historical_file = ROOT / 'visual/validation/HISTORICAL_RUN_STATUS.json'
    historical = json.loads(historical_file.read_text()) if historical_file.exists() else None
    historical_root = (ROOT / historical['historical_root']).resolve() if historical else None
    if historical_root is not None and not historical_root.is_relative_to(ROOT):
        raise ValueError('Historical evidence root is outside the release')
    for path in (ROOT / 'visual/validation').rglob('*.json'):
        if historical_root is not None and path.resolve().is_relative_to(historical_root):
            continue
        value = json.loads(path.read_text())
        if isinstance(value, dict) and value.get('schema_version') == 2 and 'command' in value:
            paths.add(path)
    records = []
    for path in sorted(paths):
        relative = path.relative_to(ROOT).as_posix()
        validation_root = historical_root if historical and relative == historical['original_manifest'] else ROOT
        result = subprocess.run(
            [sys.executable, str(ROOT / 'verification/provenance_runner/validate_manifest.py'),
             str(path), '--root', str(validation_root)], capture_output=True, text=True,
        )
        records.append({'manifest': relative,
                        'manifest_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'validation_root': validation_root.relative_to(ROOT).as_posix(),
                        'classification': 'superseded_historical_snapshot' if validation_root != ROOT else 'current_or_retained_record',
                        'returncode': result.returncode, 'stdout': result.stdout.strip(),
                        'stderr': result.stderr.strip()})
    output = {'status': 'PASS' if records and all(r['returncode'] == 0 for r in records) else 'FAIL',
              'record_count': len(records), 'records': records,
              'scope': 'Schema and input/output hashes only, including the declared snapshot root for superseded visual history. Failed scientific records remain failed; superseded records remain superseded. No universal proof or Lean check inferred.',
              'historical_root_declaration_sha256': hashlib.sha256(historical_file.read_bytes()).hexdigest() if historical else None}
    (ROOT / 'verification/FINAL_EVIDENCE_VALIDATION.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({'status': output['status'], 'record_count': len(records),
                      'failed': [r for r in records if r['returncode'] != 0]}))
    if output['status'] == 'FAIL':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
