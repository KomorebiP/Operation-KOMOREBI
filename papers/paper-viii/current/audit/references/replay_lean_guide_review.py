#!/usr/bin/env python3
"""Independent, static documentation review; never invokes Lean or the guide assembler."""
import argparse
import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def uncomment(text):
    """Erase nested Lean comments while preserving source line numbers."""
    out, i, depth = [], 0, 0
    while i < len(text):
        if depth:
            if text.startswith('/-', i):
                depth += 1; out.extend('  '); i += 2
            elif text.startswith('-/', i):
                depth -= 1; out.extend('  '); i += 2
            else:
                out.append('\n' if text[i] == '\n' else ' '); i += 1
        elif text.startswith('/-', i):
            depth = 1; out.extend('  '); i += 2
        elif text.startswith('--', i):
            j = text.find('\n', i)
            if j < 0: j = len(text)
            out.extend(' ' * (j-i)); i = j
        else:
            out.append(text[i]); i += 1
    assert not depth
    return ''.join(out)


def declarations(path):
    stack, rows, audits = [], [], []
    for lineno, line in enumerate(uncomment(path.read_text()).splitlines(), 1):
        scope = re.match(r'^\s*(namespace|section)\b\s*(\S*)', line)
        if scope:
            stack.append((scope[1], scope[2])); continue
        if re.match(r'^\s*end(?:\s+\S+)?\s*$', line):
            assert stack, (path, lineno)
            stack.pop(); continue
        m = re.match(r'^\s*(?:@\[[^\n]*?\]\s*)?(?:(?:private|protected|noncomputable)\s+)*(theorem|lemma|def|abbrev|structure|inductive)\s+(\S+)', line)
        if m:
            kind, name = m.groups()
            prefix = '.'.join(x[1] for x in stack if x[0] == 'namespace')
            rows.append({'kind': kind, 'name': name, 'declaration': prefix+'.'+name if prefix else name, 'line': lineno, 'file': 'formalization/'+path.name, 'module': path.stem})
        a = re.match(r'^\s*#print\s+axioms\s+(\S+)\s*$', line)
        if a: audits.append(a[1])
    assert not stack, path
    return rows, audits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', type=Path, required=True, help='original_snapshot root')
    ap.add_argument('--guide', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    a = ap.parse_args()
    generated = a.guide/'generated'
    parsed, audits = [], []
    for path in sorted((a.source/'formalization').glob('*.lean')):
        ds, ns = declarations(path); parsed.extend(ds); audits.extend(ns)
    promised = json.loads((generated/'source_declarations.json').read_text())
    assert parsed == sorted(promised, key=lambda x: (x['file'], x['line'])), 'declaration list mismatch'
    targets = json.loads((generated/'targets.json').read_text())
    assert set(audits) == {x['declaration'] for x in targets}
    assert len(audits) == len(set(audits)) == 458
    theorem_rows = [x for x in parsed if x['kind'] in ('theorem', 'lemma')]
    assert len(theorem_rows) == 392
    assert sum(x['module']=='QuantumPacketCore' for x in theorem_rows) == 19
    assert sum(x['kind'] not in ('theorem', 'lemma') for x in targets) == 66
    sixth_inventory = json.loads((a.source/'verification/sixth_module_inventory.json').read_text())
    sixth_counts = {name: sum(x['module'] == name for x in theorem_rows) for name in sixth_inventory['modules']}
    assert len(sixth_counts) == 10 and sum(sixth_counts.values()) == 79
    assert sixth_counts == sixth_inventory['theorem_counts']

    excerpts = json.loads((generated/'excerpts.json').read_text())
    excerpt_checks = []
    for row in excerpts:
        p = a.source/row['source_file']
        exact = ('\n'.join(p.read_text().splitlines()[row['start_line']-1:row['end_line']])+'\n').encode()
        q = a.guide/'excerpts'/f"{row['tag']}.lean.txt"
        assert digest(p) == row['source_sha256']
        assert exact == q.read_bytes()
        assert hashlib.sha256(exact).hexdigest() == row['excerpt_sha256']
        excerpt_checks.append({**row, 'exact_source_bytes_match': True})
    assert len(excerpts) == 61
    assert sum(x['end_line']-x['start_line']+1 for x in excerpts) == 635
    chapter_text = '\n'.join(x.read_text() for x in sorted((a.guide/'chapters').glob('*.tex')))
    excerpt_use = Counter(re.findall(r'\\excerpt\{[^}]*\}\{([^}]+)\}', chapter_text))
    assert excerpt_use == Counter(x['tag'] for x in excerpts)
    assert 'finite and nonempty at the condition-bound endpoint' in chapter_text
    assert 'perturbed factor times the previous discrepancy' in chapter_text
    assert 'The classical CG energy-error estimate is the hypothesis' in chapter_text

    summary_path = a.source/'verification/sixth_final/SUMMARY.json'
    summary = json.loads(summary_path.read_text())
    recorded, log_sets, module_checks = {}, {}, []
    for row in summary['modules']:
        src = a.source/row['source']
        log = summary_path.parent/row['log']
        assert digest(src) == row['sha256']
        assert digest(log) == row['log_sha256']
        assert row['exit_code'] == 0 and row['pass']
        sets = {}
        for m in re.finditer(r"'([^']+)' depends on axioms:\s*\[([^\]]*)\]", log.read_text()):
            sets[m[1]] = [x.strip() for x in m[2].split(',') if x.strip()]
        # Some saved declarations use no axioms.
        for m in re.finditer(r"'([^']+)' does not depend on any axioms", log.read_text()):
            sets[m[1]] = []
        assert sets == row['axiom_audits'], (row['module'], sets, row['axiom_audits'])
        assert all(set(xs) <= set(summary['allowed_axioms']) for xs in sets.values())
        recorded.update(row['axiom_audits']); log_sets.update(sets)
        module_checks.append({'module': row['module'], 'source_sha256': digest(src), 'log_sha256': digest(log), 'axiom_records': len(sets)})
    assert set(recorded) == set(audits)
    assert recorded == json.loads((generated/'inherited_axiom_records.json').read_text())
    assert len(summary['modules']) == 40
    assert summary['theorem_declarations'] == 392 and summary['construction_audit_count'] == 66
    assert summary['complete'] and summary['pass']
    controls = []
    for row in summary['negative_controls']:
        source = a.source/row['source']
        log = summary_path.parent/row['log']
        assert digest(source) == row['sha256']
        assert digest(log) == row['log_sha256']
        assert row['exit_code'] == row['expected_exit_code'] == 1 and row['pass']
        controls.append({'name': row['name'], 'source_sha256': digest(source), 'log_sha256': digest(log), 'inherited_exit_code': row['exit_code']})
    assert len(controls) == 2
    coverage_path = a.source/'verification/coverage_ledger.json'
    coverage = json.loads(coverage_path.read_text())
    assert coverage == json.loads((generated/'coverage_ledger.json').read_text())
    assert len(coverage['records']) == 85
    checked = [x for x in coverage['records'] if x['lean_status'] == 'checked']
    classical = [x for x in coverage['records'] if x['lean_status'].startswith('external_input_')]
    assert len(checked) == 56
    assert len(classical) == 4
    assert all(set(x['lean_theorems']) <= set(audits) for x in checked)

    guide_files = sorted((a.guide/'chapters').glob('*.tex'))
    guide_files += [a.guide/'Paper_VIII_Lean_Guide_Final.tex', a.guide/'preamble.tex', a.guide/'Paper_VIII_Lean_Guide_Final.pdf']
    guide_files += sorted(generated.glob('*.json'))
    report = {
        'status': 'PASS_STATIC_DOCUMENTATION_RECONCILIATION',
        'scope': 'Independent source-byte, declaration, saved-log, and instructional correspondence checks; no fresh Lean execution and no full independent proof audit.',
        'source_modules': 40, 'theorem_declarations': len(theorem_rows),
        'paper_viii_theorems': 373, 'foundation_theorems': 19,
        'construction_audits': 66, 'audited_names': len(audits),
        'sixth_block_modules': sixth_counts, 'sixth_block_new_theorems': 79,
        'exact_excerpts': len(excerpts), 'exact_excerpt_lines': 635,
        'excerpt_usage': dict(excerpt_use), 'source_excerpts': excerpt_checks,
        'inherited_summary_sha256': digest(summary_path),
        'inherited_modules': module_checks,
        'inherited_rejected_controls': controls,
        'coverage_ledger_sha256': digest(coverage_path),
        'numbered_records': 85, 'fully_checked_ledger_records': 56,
        'separate_classical_records': 4,
        'lean_executable': shutil.which('lean'), 'lake_executable': shutil.which('lake'),
        'fresh_lean_kernel_run': False,
        'guide_hashes': {str(x.relative_to(a.guide)): digest(x) for x in guide_files},
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ['status','source_modules','theorem_declarations','construction_audits','audited_names','exact_excerpts','exact_excerpt_lines','fresh_lean_kernel_run']}))


if __name__ == '__main__':
    main()
