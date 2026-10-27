"""Freeze the accepted baseline and literal WR08/WR09/WR16 targets once."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

parent = ROOT / 'budget_v1.10.0/integration/runs/clean_budget_01'
expected = {
    'receipt.json': '42ded58f00f816a1f7895039e6521b9e510f652baf9b6e86acd1eaa47d49f376',
    'postflight.json': 'b1d47aeab1cbe838109a751edd9bba55a57593d9e9ce0e852dc0f8988983f2f2',
}
assert all(sha(parent / k) == v for k, v in expected.items())
receipt = json.loads((parent / 'receipt.json').read_text())
assert receipt['status'] == 'PASS'
for name, digest in receipt['source_snapshot_sha256'].items():
    assert sha(parent / 'source' / name) == digest, name
target_files = ['05h_regularized_repair.tex', '05k_stopping_rules.tex']
target_dir = OUT / 'targets'
target_dir.mkdir(exist_ok=True)
target_hashes = {}
for name in target_files:
    source = ROOT / 'monograph_v1.10.0/source/chapters' / name
    dest = target_dir / name
    assert not dest.exists(), 'Immutable target already exists'
    shutil.copyfile(source, dest)
    target_hashes[str(source.relative_to(ROOT))] = sha(source)
base = {
    'checkpoint': 'KS-v1.11.0-regularization-limits-start',
    'parent': 'KS-v1.10.0-WR03-WR05-complete',
    'started_utc': datetime.now(timezone.utc).isoformat(),
    'parent_archive': 'output/Komorebi_Space_Monograph_v1.10.0.zip',
    'parent_archive_sha256': sha(ROOT / 'output/Komorebi_Space_Monograph_v1.10.0.zip'),
    'formal_parent': str(parent.relative_to(ROOT)),
    'formal_parent_evidence_sha256': expected,
    'formal_parent_source_sha256': receipt['source_snapshot_sha256'],
    'target_source_sha256': target_hashes,
    'scope': 'Lean WR08 in full, then WR09 and WR16 complete named theorem clauses; no publication rewrite',
    'tracking': 'Versioned JSON/Markdown records and append-only EVENTS.jsonl; coordinator is sole journal writer',
    'owner_scopes': {
        'wr08_limits': ['formal/KomorebiSpace/RegularizationLimits.lean', 'development/basic/'],
        'wr08_strong': ['formal/KomorebiSpace/RegularizationStrongLimit.lean', 'development/strong/'],
        'noise_limits': ['formal/KomorebiSpace/RegularizationNoiseLimits.lean', 'development/noise/'],
        'limits_verifier': ['integration/', 'development/verifier/'],
        'limits_controls': ['formal/tests/', 'development/controls/'],
        'limits_math_audit': ['reviews/WR08_WR09_WR16_MATH_AUDIT.md', 'reviews/math/'],
        'root': ['records/', 'PROGRESS_LEDGER.md', 'PROGRESS_LEDGER.json', 'FORMAL_COVERAGE.json', 'README.md', 'packaging/'],
    },
}
(OUT / 'BASE_CHECKPOINT.json').write_text(json.dumps(base, indent=2) + '\n')
with (OUT / 'EVENTS.jsonl').open('x') as f:
    f.write(json.dumps({'event': 'E001', 'utc': base['started_utc'], 'kind': 'target_frozen',
                      'checkpoint': base['checkpoint'], 'base_sha256': sha(OUT / 'BASE_CHECKPOINT.json'),
                      'accepted_parent_rechecked': True, 'target_source_sha256': target_hashes}) + '\n')
print(json.dumps({'status': 'BASE_AND_TARGETS_FROZEN', 'checkpoint': base['checkpoint'],
                  'parent_source_files_checked': len(receipt['source_snapshot_sha256']),
                  'target_source_sha256': target_hashes}, indent=2))
