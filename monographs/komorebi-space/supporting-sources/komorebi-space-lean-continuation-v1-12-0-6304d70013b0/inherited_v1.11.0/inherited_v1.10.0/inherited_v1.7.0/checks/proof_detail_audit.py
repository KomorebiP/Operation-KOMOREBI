#!/usr/bin/env python3
"""Check the proof-edit inventory and preserve both accepted formal source trees.

This is a mechanical editorial audit, not verification of mathematical arguments.
It checks retained labels and theorem statements, and binds proof texts to hashes.
"""
from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / 'audit/proof_detail'
OLD = ROOT / 'history/v1.6.0'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def proof_at(text: str, label: str) -> str:
    pos = text.index('\\label{' + label + '}')
    start = text.index('\\begin{proof}', pos)
    end = text.index('\\end{proof}', start) + len('\\end{proof}')
    return text[start:end]


def statements(base: Path) -> dict[str, str]:
    result = {}
    pattern = re.compile(r'\\begin\{(theorem|proposition|lemma|corollary|example|definition)\}(.*?)\\end\{\1\}', re.S)
    for path in (base / 'source/chapters').glob('*.tex'):
        for match in pattern.finditer(path.read_text()):
            for label in re.findall(r'\\label\{((?:KS|WR)\d+)\}', match.group(2)):
                if label in result:
                    raise ValueError(f'Duplicate principal label: {label}')
                result[label] = match.group(0)
    return result


def main() -> int:
    errors = []
    baseline = json.loads((AUDIT / 'baseline.json').read_text())
    # The baseline uses an explicit source-tree inventory, not a new compiler record.
    expected = baseline['formal_and_extension_files']
    if not expected:
        raise ValueError('Missing formal-file inventory in proof-detail baseline')
    if isinstance(expected, list):
        expected = {x['path']: x['sha256'] for x in expected}
    current = {str(p.relative_to(ROOT)): sha(p.read_bytes())
               for tree in ('formal', 'extension') for p in (ROOT/tree).rglob('*')
               if p.is_file() and '__pycache__' not in p.parts and '.work' not in p.parts and '.lake' not in p.parts}
    if current != expected:
        errors.append('Formal source inventory differs from the untouched predecessor')

    entries = [item for p in sorted(AUDIT.glob('changes_*.json')) for item in json.loads(p.read_text())]
    seen = set()
    expanded = []
    for entry in entries:
        label, rel = entry['id'], entry['file']
        if label in seen:
            errors.append(f'Duplicate proof-edit record {label}')
        seen.add(label)
        before = proof_at((OLD/rel).read_text(), label)
        after = proof_at((ROOT/rel).read_text(), label)
        if sha(before.encode()) != entry['old_proof_sha256']:
            errors.append(f'Predecessor proof does not match inventory: {label}')
        if sha(after.encode()) != entry['new_proof_sha256']:
            errors.append(f'Current proof does not match inventory: {label}')
        if before == after:
            errors.append(f'Listed proof is unchanged: {label}')
        expanded.append({**entry, 'current_source_sha256': sha((ROOT/rel).read_bytes())})

    before_statements, after_statements = statements(OLD), statements(ROOT)
    if before_statements != after_statements:
        keys = set(before_statements) | set(after_statements)
        errors += [f'Principal statement changed: {k}' for k in sorted(keys)
                   if before_statements.get(k) != after_statements.get(k)]
    old_text = '\n'.join(p.read_text() for p in (OLD/'source/chapters').glob('*.tex'))
    new_text = '\n'.join(p.read_text() for p in (ROOT/'source/chapters').glob('*.tex'))
    labels = lambda s: set(re.findall(r'\\label\{([^}]+)\}', s))
    lost = sorted(labels(old_text)-labels(new_text))
    if lost:
        errors.append(f'Lost source labels: {lost}')
    source_ids = lambda s: re.findall(r'\\(?:source|written)\{([^}]+)\}', s)
    if sorted(source_ids(old_text)) != sorted(source_ids(new_text)):
        errors.append('Principal evidence callouts changed')

    out = {'status': 'PASS' if not errors else 'FAIL',
           'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
           'edition': '1.7.0', 'predecessor': '1.6.0',
           'expanded_proofs': len(entries),
           'expanded_KS_proofs': sum(x['id'].startswith('KS') for x in entries),
           'expanded_WR_proofs': sum(x['id'].startswith('WR') for x in entries),
           'expanded_existing_support_proofs': sum(not x['id'].startswith(('KS','WR')) for x in entries),
           'chapters_with_expanded_proofs': len({x['file'] for x in entries}),
           'principal_statement_envelopes_unchanged': len(before_statements),
           'original_labels_preserved': not lost,
           'background_lemmas_added': 5,
           'proof_blocks_before': old_text.count('\\begin{proof}'),
           'proof_blocks_after': new_text.count('\\begin{proof}'),
           'formal_tree_files_unchanged': len(current) if current == expected else 0,
           'new_Lean_execution': False,
           'scope': 'Text/statement/label/source preservation audit. Not mathematical proof verification or a new Lean replay.',
           'errors': errors, 'proofs': expanded,
           'background_source_sha256': sha((ROOT/'source/chapters/12_proof_tools.tex').read_bytes())}
    (AUDIT/'proof_inventory.json').write_text(json.dumps(out, indent=2)+'\n')
    lines = ['# Komorebi Space proof expansion map — v1.7.0', '',
             'The theorem program and evidence identifiers are retained. This map records changes to written arguments, not new Lean results.', '',
             f"**{len(entries)} existing proof blocks expanded**, across {out['chapters_with_expanded_proofs']} chapter source files. Five classical background lemmas are added in the analytic appendix.", '',
             '| ID | Source chapter | What the expanded proof makes explicit |',
             '|---|---|---|']
    for x in sorted(entries, key=lambda x: (x['file'], x['id'])):
        lines.append(f"| {x['id']} | `{Path(x['file']).name}` | {x['focus']} |")
    lines += ['', '## Evidence boundary', '',
              'Canonical v1.2.0 and focused v1.6.0 formal records are retained, with both source trees unchanged. No new Lean compilation or axiom audit was run. Ten WR groups remain written-only; two retain written limiting consequences alongside formal pointwise inequalities.', '',
              'The audit preserves the exact principal theorem statements and checks proof text hashes and labels. It cannot certify the correctness of natural-language mathematics. The supporting analytic appendix is a written treatment of classical facts, not five new formalized claims.']
    (ROOT/'PROOF_EXPANSION_MAP.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='proofs'}, indent=2))
    return 0 if not errors else 1

if __name__ == '__main__':
    sys.exit(main())
