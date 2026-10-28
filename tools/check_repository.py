#!/usr/bin/env python3
"""Validate the staged central collection without claiming a theorem replay."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(root: Path) -> dict:
    """Return diagnostics even when a checkout or child check is incomplete."""
    errors: list[str] = []
    required = [
        'README.md', 'CONTRIBUTIONS.md', 'CONTRIBUTING.md', 'CITATION.md',
        'docs/START_HERE.md', 'docs/WORKFLOWS.md',
        'papers/README.md', 'formal/README.md', 'experiments/README.md',
        'packages/README.md', 'manifests/contributions.json',
        'formal/research-preview-1/REPRODUCE.md',
    ]
    for rel in required:
        if not (root / rel).is_file():
            errors.append(f'Missing entry point: {rel}')
    ledger_path = root / 'manifests/contributions.json'
    if ledger_path.exists():
        try:
            ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
            if (not isinstance(ledger, dict)
                    or not isinstance(ledger.get('contributions'), list)
                    or not all(isinstance(row, dict) for row in ledger['contributions'])):
                errors.append('Contribution ledger must contain an array of contribution objects')
            else:
                rows = ledger['contributions']
                ids = [row.get('id') for row in rows]
                if not all(isinstance(i, str) and i for i in ids) or len(set(ids)) != len(ids):
                    errors.append('Contribution identifiers are missing or duplicated')
                for row in rows:
                    if row.get('disposition') == 'imported':
                        rel = row.get('local_path')
                        if not isinstance(rel, str) or not rel or not (root / rel).exists():
                            errors.append(f"Imported contribution has no local bytes: {row.get('id')}")
        except (OSError, ValueError) as exc:
            errors.append(f'Cannot read contribution ledger: {exc}')
    preview = root / 'formal/research-preview-1'
    command = [sys.executable, '-B', 'tools/check_release.py']
    preview_exit_status = None
    preview_stderr = ''
    if not (preview / 'tools/check_release.py').is_file():
        reason = ('Preserved preview checker is missing: formal/research-preview-1/tools/check_release.py. '
                  'Use a complete checkout; for a sparse checkout, include the entire preserved preview directory.')
        preview_result = {'status': 'NOT_RUN', 'reason': reason}
        errors.append(reason)
    else:
        try:
            proc = subprocess.run(command, cwd=preview, capture_output=True,
                                  encoding='utf-8', errors='replace')
        except OSError as exc:
            reason = 'Cannot start the preserved preview checker: '+str(exc)
            preview_result = {'status': 'NOT_RUN', 'reason': reason}
            errors.append(reason)
        else:
            preview_exit_status, preview_stderr = proc.returncode, proc.stderr
            try:
                preview_result = json.loads(proc.stdout)
                if not isinstance(preview_result, dict):
                    raise ValueError('Expected a JSON object')
            except ValueError:
                preview_result = {'status': 'FAIL', 'stdout': proc.stdout,
                                  'errors': ['Preview checker did not return a JSON object']}
            if proc.returncode != 0 or preview_result.get('status') != 'PASS':
                errors.append('Preserved formal preview artifact check failed; inspect preview diagnostics and exit status')
    result = {
        'status': 'PASS' if not errors else 'FAIL',
        'scope': 'Entry-point presence and preserved formal source/artifact identity; no Lean replay, full corpus reconciliation, or publication approval.',
        'entry_points_checked': len(required),
        'preview': preview_result,
        'preview_exit_status': preview_exit_status,
        'errors': errors,
    }
    if preview_stderr:
        result['preview_stderr'] = preview_stderr
    return result


def main() -> int:
    result = check(ROOT)
    print(json.dumps(result, indent=2))
    return int(result['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
