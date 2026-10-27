"""Structural source checks and a statement index, not a proof verifier."""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Grounded_Abstraction_v0.5.0.tex'

def main() -> None:
    text = SOURCE.read_text()
    labels = re.findall(r'\\label\{([^}]+)\}', text)
    refs = re.findall(r'\\(?:eqref|ref)\{([^}]+)\}', text)
    bib = re.findall(r'\\bibitem\{([^}]+)\}', text)
    cites = {key.strip() for group in re.findall(r'\\cite\{([^}]+)\}', text) for key in group.split(',')}
    figures = re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text)
    failures = []
    for name, entries in [('labels', labels), ('bibliography keys', bib)]:
        if len(entries) != len(set(entries)):
            failures.append(f'Duplicate {name}')
    if set(refs) - set(labels): failures.append('Missing references: ' + repr(set(refs) - set(labels)))
    if cites - set(bib): failures.append('Missing bibliography: ' + repr(cites - set(bib)))
    if set(bib) - cites: failures.append('Unused bibliography: ' + repr(set(bib) - cites))
    for name in figures:
        if not (ROOT / name).is_file(): failures.append('Missing figure: ' + name)
    envs = []
    pattern = re.compile(r'\\begin\{(theorem|proposition|corollary|proof)\}(?:\[([^\]]*)\])?(.*?)\\end\{\1\}', re.S)
    auxpath = ROOT / 'build/Grounded_Abstraction_v0.5.0.aux'
    aux = auxpath.read_text() if auxpath.exists() else ''
    numbermap = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]+)\}', aux))
    for match in pattern.finditer(text):
        kind, title, body = match.groups()
        envs.append((kind, title, body, text[:match.start()].count('\n') + 1))
    records = []
    if len(envs) % 2: failures.append('Odd statement/proof environment count')
    for index in range(0, len(envs) - 1, 2):
        stmt, proof = envs[index:index+2]
        if stmt[0] == 'proof' or proof[0] != 'proof':
            failures.append('Unpaired statement/proof')
            continue
        stmtlabels = re.findall(r'\\label\{([^}]+)\}', stmt[2])
        if len(stmtlabels) != 1: failures.append('Statement label missing or ambiguous')
        key = stmtlabels[0] if stmtlabels else ''
        records.append({'type': stmt[0], 'title': stmt[1], 'label': key,
                        'number': numbermap.get(key), 'source_start_line': stmt[3],
                        'proof_start_line': proof[3]})
    counts = Counter(r['type'] for r in records)
    result = {'status': 'PASS' if not failures else 'FAIL', 'failures': failures,
              'statements': len(records), 'statement_types': dict(counts),
              'proofs': sum(e[0] == 'proof' for e in envs),
              'definitions': len(re.findall(r'\\begin\{definition\}', text)),
              'counterexamples': len(re.findall(r'\\begin\{counterexample\}', text)),
              'figures': len(figures), 'references': len(bib), 'labels': len(labels),
              'non_claim': 'Checks document structure and links, not proof validity or novelty.'}
    (ROOT/'validation/source_audit.json').write_text(json.dumps(result, indent=2)+'\n')
    (ROOT/'STATEMENT_INDEX.json').write_text(json.dumps(records, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if failures: raise SystemExit(1)

if __name__ == '__main__': main()
