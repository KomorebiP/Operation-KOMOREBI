#!/usr/bin/env python3
"""Validate the staged central collection without claiming a theorem replay."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    errors: list[str] = []
    required = [
        'README.md', 'CONTRIBUTIONS.md', 'docs/START_HERE.md',
        'papers/README.md', 'formal/README.md', 'experiments/README.md',
        'packages/README.md', 'manifests/contributions.json',
        'formal/research-preview-1/REPRODUCE.md',
    ]
    for rel in required:
        if not (ROOT / rel).is_file():
            errors.append(f'Missing entry point: {rel}')
    ledger_path = ROOT / 'manifests/contributions.json'
    if ledger_path.exists():
        try:
            ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
            if not isinstance(ledger, dict) or not isinstance(ledger.get('contributions'), list):
                errors.append('Contribution ledger must contain a contributions array')
            else:
                rows = ledger['contributions']
                ids = [row.get('id') for row in rows]
                if not all(isinstance(i, str) and i for i in ids) or len(set(ids)) != len(ids):
                    errors.append('Contribution identifiers are missing or duplicated')
                for row in rows:
                    if row.get('disposition') == 'imported':
                        rel = row.get('local_path')
                        if not rel or not (ROOT / rel).exists():
                            errors.append(f"Imported contribution has no local bytes: {row.get('id')}")
        except (OSError, ValueError) as exc:
            errors.append(f'Cannot read contribution ledger: {exc}')
    preview = ROOT / 'formal/research-preview-1'
    command = [sys.executable, '-B', 'tools/check_release.py']
    proc = subprocess.run(command, cwd=preview, capture_output=True, text=True)
    try:
        preview_result = json.loads(proc.stdout)
    except ValueError:
        preview_result = {'stdout': proc.stdout, 'stderr': proc.stderr}
    if proc.returncode != 0:
        errors.append('Preserved formal preview artifact check failed')
    result = {
        'status': 'PASS' if not errors else 'FAIL',
        'scope': 'Entry-point presence and preserved formal source/artifact identity; no Lean replay, full corpus reconciliation, or publication approval.',
        'entry_points_checked': len(required),
        'preview': preview_result,
        'errors': errors,
    }
    print(json.dumps(result, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
