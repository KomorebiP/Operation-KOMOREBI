#!/usr/bin/env python3
"""Bind delivered formal sources to successful replay and reviewed reader sources."""
from pathlib import Path
import datetime, hashlib, json

BASE = Path('/workspace/scratch/604befec1954')
ROOT = BASE / 'paperxi_release'
RUNTIME = BASE / 'paperxi_lean'
PORTABLE = BASE / 'paperxi_lean_portable'
FORMAL = ROOT / 'formalization'
GUIDE = ROOT / 'publication/source/lean_guide'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def inventory(root):
    return {p.relative_to(root).as_posix(): sha(p)
            for p in sorted(root.rglob('*')) if p.is_file()}

formal_report_path = RUNTIME / 'evidence/RELEASE_VERIFICATION.json'
formal_report = json.loads(formal_report_path.read_text())
assert formal_report['status'] == 'PASS'
assert sha(ROOT / 'verification/lean/RELEASE_VERIFICATION.json') == sha(formal_report_path)
final_locator = formal_report['final_replay_result']
receipt_relative = Path(final_locator['path'])
assert not receipt_relative.is_absolute() and '..' not in receipt_relative.parts
assert receipt_relative.parts[0] == 'evidence'
receipt = RUNTIME / receipt_relative
assert sha(receipt) == final_locator['sha256']
run = json.loads(receipt.read_text())
assert run['status'] == 'PASS'
assert run['all_sources_unchanged'] is True
assert run['source_hashes_before'] == run['source_hashes_after']
assert len(run['source_hashes_after']) == 425
rows = {r['source_path']: r for r in run['modules']}
assert len(rows) == 425 and all(r['status'] == 'PASS' for r in rows.values())
assert set(rows) == set(run['source_hashes_after'])
selected = {k for k, r in rows.items() if r['group'] == 'selected'}
assert len(selected) == 423
assert set(rows) - selected == {
    'PaperXI/ActualMonomialLocalGlobal.lean',
    'PaperXI/SingleCandidateComparison.lean'}

portable = inventory(PORTABLE)
delivered = inventory(FORMAL)
assert portable == delivered, 'Delivered portable-project files differ from finalized staging.'
guide_files = {p.relative_to(GUIDE / 'sources').as_posix(): p
               for p in (GUIDE / 'sources/PaperXI').glob('*.lean')}
assert set(guide_files) == selected

records = []
for relative, digest in sorted(run['source_hashes_after'].items()):
    assert rows[relative]['source_sha256'] == digest
    assert sha(RUNTIME / relative) == sha(PORTABLE / relative) == sha(FORMAL / relative) == digest
    if relative in selected:
        assert sha(guide_files[relative]) == digest
    records.append({'path': relative, 'group': rows[relative]['group'],
                    'sha256': digest, 'fresh_compile_status': rows[relative]['status'],
                    'reader_selected_source_match': relative in selected})

supplement = 'PaperXI/SingleCandidateComparison.lean'
assert sha(GUIDE / 'supplements/SingleCandidateComparison.lean') == run['source_hashes_after'][supplement]
copied_receipt = ROOT / 'verification/lean' / Path(*receipt_relative.parts[1:])
assert sha(copied_receipt) == sha(receipt)

out = ROOT / 'evidence/release_1_1/FORMAL_SOURCE_BRIDGE.json'
result = {
    'schema_version': 1, 'status': 'passed',
    'script_sha256': sha(Path(__file__)),
    'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'replay_result': str(copied_receipt.relative_to(ROOT)),
    'replay_result_sha256': sha(receipt),
    'formal_report_sha256': sha(formal_report_path),
    'scope': 'All 425 source targets match the successful final replay, the working runtime, the finalized portable project and the delivered formalization. The 423 selected reader sources and separately printed comparison supplement match their corresponding targets.',
    'portable_project_file_count': len(portable),
    'delivered_portable_project_exactly_matches': True,
    'selected_modules': 423, 'separate_terminal_modules': 1,
    'separate_comparison_modules': 1,
    'records': records,
    'limit': 'This is a hash and population bridge. Compilation, axiom dependencies and mathematical repair review have separate receipts.'
}
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({k: result[k] for k in ['status', 'portable_project_file_count',
    'selected_modules', 'separate_terminal_modules', 'separate_comparison_modules']}))
