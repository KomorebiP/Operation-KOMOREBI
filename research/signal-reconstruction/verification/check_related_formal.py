#!/usr/bin/env python3
"""Compare the related source contract with inherited logs; no Lean execution."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = ROOT / 'related_formal/paper_v/formalization/lean'
    evidence = ROOT / 'related_formal/paper_v/verification'
    contract_file = evidence / 'candidate_contract.json'
    audit_file = evidence / 'lean_axiom_audit.log'
    targets = json.loads(contract_file.read_text())['theorem_targets']
    problems = []
    for target in targets:
        lines = (source / target['file']).read_text().splitlines()
        name = target['declaration'].split('.')[-1]
        text = lines[target['line'] - 1] if 0 < target['line'] <= len(lines) else ''
        if not re.search(r'\btheorem\s+' + re.escape(name) + r'\b', text):
            problems.append({'declaration': target['declaration'], 'line': target['line'], 'text': text})
    log = audit_file.read_text()
    missing = [t['declaration'] for t in targets
               if "'" + t['declaration'] + "' depends on axioms:" not in log
               and "'" + t['declaration'] + "' does not depend on any axioms" not in log]
    unexpected = []
    for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", log):
        axioms = {a.strip() for a in match.group(2).split(',') if a.strip()}
        if not axioms <= {'propext', 'Classical.choice', 'Quot.sound'}:
            unexpected.append({'declaration': match.group(1), 'axioms': sorted(axioms)})
    record = {
        'status': 'PASS_STATIC_RELATED_SOURCE_CORRESPONDENCE' if not problems and not missing and not unexpected else 'FAIL',
        'scope': 'Fresh text/hash validation of inherited source and inherited logs only. No elaboration, kernel check, or new Signal formal certificate inferred.',
        'source_version': 'Paper V v1.1.0 checkpoint',
        'source_file_count': len(list(source.rglob('*.lean'))),
        'contract_target_count': len(targets), 'source_line_mismatches': problems,
        'historical_axiom_target_lines_missing': missing,
        'historical_unexpected_axioms': unexpected,
        'lean_toolchain': (source / 'lean-toolchain').read_text().strip(),
        'lake_manifest_sha256': hashlib.sha256((source / 'lake-manifest.json').read_bytes()).hexdigest(),
        'candidate_contract_sha256': hashlib.sha256(contract_file.read_bytes()).hexdigest(),
        'historical_axiom_audit_sha256': hashlib.sha256(audit_file.read_bytes()).hexdigest(),
        'log_grammar': 'Accepts both a listed axiom set and the explicit no-axioms form.',
    }
    (ROOT / 'verification/RELATED_FORMAL_STATIC_CORRESPONDENCE.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record))
    if record['status'] == 'FAIL':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
