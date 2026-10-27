#!/usr/bin/env python3
"""Refresh current guide metadata without invoking Lean or editing formal source."""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import shutil
import subprocess
from data_helpers import active_text

HERE = Path(__file__).resolve().parent
PARSER = argparse.ArgumentParser(description=__doc__)
PARSER.add_argument('--source', type=Path, default=HERE.parent.parent / 'source/complete/Paper_VIII_Complete_v0.6.0_With_Visual_Appendix/original_snapshot')
ARGS = PARSER.parse_args()
SOURCE = ARGS.source.resolve()
GENERATED = HERE / 'generated'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

executables = {name: shutil.which(name) for name in ('lean', 'lake', 'elan', 'xelatex')}
source_files = sorted((SOURCE / 'formalization').glob('*.lean'))
active_findings = []
for path in source_files:
    text = active_text(path.read_text(encoding='utf-8'))
    for match in re.finditer(r'\b(?:sorry|admit|axiom)\b', text):
        active_findings.append({'file': path.name, 'line': text[:match.start()].count('\n') + 1, 'token': match.group()})
if active_findings:
    raise RuntimeError('Unresolved active formal source token: ' + str(active_findings))

reconciliation_path = GENERATED / 'documentation_reconciliation.json'
reconciliation = json.loads(reconciliation_path.read_text())
reconciliation.update(
    documentation_edition='Paper VIII monograph, 9 October 2026',
    refreshed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    executable_availability=executables,
    fresh_lean_kernel_run=False,
    fresh_gpu_benchmark_run=False,
    active_formal_source_placeholders=[],
    source_identity_method='40 active source files matched to all retained compiler summary and saved log SHA-256 identities by assemble.py',
)
dump(reconciliation_path, reconciliation)

ledger_path = GENERATED / 'coverage_ledger.json'
ledger = json.loads(ledger_path.read_text())
ledger['page_field_namespace'] = 'inherited original manuscript pages, retained for historical identity; current locations are in traditional_crosswalk.json'
ledger['current_navigation_file'] = 'traditional_crosswalk.json'
dump(ledger_path, ledger)

evidence = {
    'status': 'PASS',
    'edition_date': '2026-10-09',
    'generated_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'current_executables': executables,
    'fresh_lean_kernel_run': False,
    'fresh_gpu_performance_run': False,
    'inherited_completed_utc': reconciliation['inherited_run_completed_utc'],
    'inherited_summary_sha256': sha(SOURCE / 'verification/sixth_final/SUMMARY.json'),
    'source_inventory_sha256': sha(SOURCE / 'verification/theorem_inventory.json'),
    'source_coverage_ledger_sha256': sha(SOURCE / 'verification/coverage_ledger.json'),
    'all_active_source_sha256': {path.relative_to(SOURCE).as_posix(): sha(path) for path in source_files},
    'counts': {name: reconciliation[name] for name in (
        'source_modules', 'theorem_declarations', 'paper_viii_theorems',
        'reused_foundation_theorems', 'construction_audits', 'audited_names',
        'fully_checked_manuscript_items', 'separate_classical_inputs', 'exact_excerpts', 'excerpt_lines')},
    'proofreading_scope': 'New wrapper, evidence notes and navigation prose only. Teaching chapters and exact UTF-8 excerpt bodies preserved.',
    'mathematical_token_changes': [],
    'historical_generated_metadata': 'historical_assembly/generated/',
    'limitations': 'Compiler evidence is inherited from the source-bound September run. Static documentation checks are fresh. General SVD existence, the classical CG bound, floating-point model and simultaneous decomposition are separately supplied inputs. Three broader research targets remain open.'
}
dump(GENERATED / 'evidence_provenance.json', evidence)
print(json.dumps({'status': 'PASS', 'modules': len(source_files), 'current_executables': executables, 'fresh_lean_kernel_run': False}, indent=2))
