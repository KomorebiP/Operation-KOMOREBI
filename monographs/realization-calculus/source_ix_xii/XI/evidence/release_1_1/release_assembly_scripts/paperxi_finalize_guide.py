#!/usr/bin/env python3
"""Install the final verification paragraph only from accepted release evidence."""
from pathlib import Path
import hashlib, json, re

BASE = Path('/workspace/scratch/604befec1954')
RUNTIME = BASE / 'paperxi_lean'
report_path = RUNTIME / 'evidence/RELEASE_VERIFICATION.json'
report = json.loads(report_path.read_text())
review = json.loads((BASE / 'paperxi_audit/terminal_repair_review_final.json').read_text())
assert report['status'] == 'PASS'
assert review['status'] == 'passed_in_reviewed_scope'
assert not review['open_actionable_findings']
terminal = RUNTIME / 'PaperXI/ActualMonomialLocalGlobal.lean'
assert review['source_sha256'] == report['terminal_repaired_sha256'] == hashlib.sha256(terminal.read_bytes()).hexdigest()
assert review['original_kernel_declaration_comparison'] is False
scopes = report['scopes']
assert all(s['compile_status'] == s['axiom_audit_status'] == 'PASS' for s in scopes.values())
assert len(report['catalogue_private_name_resolutions']) == 4
locator = report['final_replay_result']
relative = Path(locator['path'])
assert not relative.is_absolute() and '..' not in relative.parts
replay_path = RUNTIME / relative
assert hashlib.sha256(replay_path.read_bytes()).hexdigest() == locator['sha256']
replay = json.loads(replay_path.read_text())
assert replay['status'] == 'PASS'
assert len(replay['modules']) == 425 and all(r['status'] == 'PASS' for r in replay['modules'])
rows = {r['module']: r for r in replay['modules']}
replacement = {
    '@SELECTED_OWNED@': f"{scopes['selected']['owned_constant_count']:,}",
    '@TERMINAL_OWNED@': f"{scopes['terminal']['owned_constant_count']:,}",
    '@INTERFACE_OWNED@': f"{scopes['new_interface']['owned_constant_count']:,}",
    '@SELECTED_AUX@': f"{scopes['selected']['compiler_auxiliary_count']:,}",
    '@TOWER_SECONDS@': f"{rows['PaperXI.UnramifiedFieldTower']['seconds']:,.1f}",
    '@BASECHANGE_SECONDS@': f"{rows['PaperXI.ActualUnramifiedBaseChange']['seconds']:,.1f}",
}
template = (BASE / 'paperxi_current_verification_template.tex').read_text()
for key, value in replacement.items():
    assert key in template
    template = template.replace(key, value)
assert not re.search(r'@[A-Z_]+@', template)
target = BASE / 'paperxi_release/publication/source/lean_guide/current_verification.tex'
assert 'Provisional build only' in target.read_text(), 'Final status already installed; preserve any later edits.'
target.write_text(template)
print(json.dumps({'status': 'installed_from_passed_evidence', 'path': str(target),
    'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'formal_report_sha256': hashlib.sha256(report_path.read_bytes()).hexdigest(),
    'terminal_source_sha256': report['terminal_repaired_sha256'], 'substitutions': replacement}, indent=2))
