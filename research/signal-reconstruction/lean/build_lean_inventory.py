#!/usr/bin/env python3
"""Inventory inherited Lean text. This script does not invoke Lean or Lake."""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / 'related_formal/paper_v/formalization/lean'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mask_lean(text):
    """Blank nested comments and strings while retaining positions and newlines."""
    out = list(text)
    i = depth = 0
    string = False
    while i < len(text):
        if depth:
            if text[i:i+2] == '/-':
                out[i:i+2] = '  '; depth += 1; i += 2; continue
            if text[i:i+2] == '-/':
                out[i:i+2] = '  '; depth -= 1; i += 2; continue
            if text[i] != '\n': out[i] = ' '
            i += 1; continue
        if string:
            if text[i] == '\\':
                out[i] = ' '; i += 1
                if i < len(text) and text[i] != '\n': out[i] = ' '
                i += 1; continue
            if text[i] == '"': string = False
            if text[i] != '\n': out[i] = ' '
            i += 1; continue
        if text[i:i+2] == '/-':
            out[i:i+2] = '  '; depth = 1; i += 2; continue
        if text[i:i+2] == '--':
            j = text.find('\n', i)
            if j < 0: j = len(text)
            out[i:j] = ' ' * (j-i); i = j; continue
        if text[i] == '"': out[i] = ' '; string = True
        i += 1
    if depth or string:
        raise ValueError('Unclosed comment/string')
    return ''.join(out)


def save(name, rows):
    (HERE / (name + '.json')).write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n')
    with (HERE / (name + '.csv')).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def main():
    modules = []
    declarations = []
    root_imports = re.findall(r'^import KomorebiPaperV\.(\w+)',
                             (SOURCE / 'KomorebiPaperV.lean').read_text(), re.M)
    for path in sorted((SOURCE / 'KomorebiPaperV').glob('*.lean')):
        raw = path.read_text()
        rawlines = raw.splitlines()
        masked = mask_lean(raw)
        scopes = []
        local = []
        for line, text in enumerate(masked.splitlines(), 1):
            text = text.strip()
            match = re.match(r'namespace\s+(\S+)', text)
            if match:
                scopes.append(('namespace', match[1])); continue
            match = re.match(r'(?:noncomputable\s+)?section(?:\s+(\S+))?\s*$', text)
            if match:
                scopes.append(('section', match[1])); continue
            if re.match(r'end(?:\s|$)', text):
                if scopes: scopes.pop()
                continue
            match = re.match(r'(?:@\[[^\]]*\]\s*)?(?:(?:noncomputable|private|protected)\s+)*'
                             r'(theorem|lemma|def|abbrev|structure|inductive)\s+([\w\u2080-\u209f]+)', text)
            if not match: continue
            name = '.'.join([v for kind, v in scopes if kind == 'namespace'] + [match[2]])
            row = dict(name=name, kind=match[1], module=path.stem,
                       file=path.relative_to(ROOT).as_posix(), line=line,
                       declaration_start=rawlines[line-1].strip(), source_sha256=digest(path))
            declarations.append(row); local.append(row)
        counts = Counter(row['kind'] for row in local)
        imports = re.findall(r'^import\s+(\S+)', masked, re.M)
        modules.append(dict(module=path.stem, file=path.relative_to(ROOT).as_posix(),
                            sha256=digest(path), lines=len(rawlines), bytes=path.stat().st_size,
                            theorem_lemma_count=counts['theorem']+counts['lemma'],
                            definition_count=counts['def'], abbreviation_count=counts['abbrev'],
                            structure_count=counts['structure'], inductive_count=counts['inductive'],
                            explicit_declaration_count=len(local),
                            local_imports=';'.join(x for x in imports if x.startswith('KomorebiPaperV.')),
                            mathlib_imports=';'.join(x for x in imports if x.startswith('Mathlib.'))))
    by_name = {row['name']: row for row in declarations}
    assert len(by_name) == len(declarations), 'Duplicate explicit names'
    assert set(root_imports) == {row['module'] for row in modules}
    contract = json.loads((ROOT / 'related_formal/paper_v/verification/candidate_contract.json').read_text())
    targets = contract['theorem_targets']
    mismatches = []
    for target in targets:
        actual = by_name.get(target['declaration'])
        expected_file = (SOURCE / target['file']).relative_to(ROOT).as_posix()
        if actual is None or (actual['file'], actual['line'], actual['kind']) != (expected_file, target['line'], target['kind']):
            mismatches.append(dict(target=target, actual=actual))
    assert not mismatches, mismatches
    save('Related_Declaration_Inventory', declarations)
    save('Related_Module_Inventory', modules)
    result = dict(schema='komorebi.signal.related-lean-text-inventory.v1',
                  method='Comment/string-masked textual scan, including noncomputable declarations; no elaboration',
                  production_modules=len(modules), total_lean_files=len(list(SOURCE.rglob('*.lean'))),
                  explicit_declarations=len(declarations), kinds=dict(Counter(row['kind'] for row in declarations)),
                  contract_targets=len(targets), all_contract_source_names_files_lines_match=True,
                  root_imports_match=True,
                  evidence='Fresh static inspection of preserved Paper V v1.1.0 checkpoint',
                  fresh_signal_lean_check=False)
    (HERE / 'INVENTORY_AUDIT.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
