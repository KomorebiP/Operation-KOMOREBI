#!/usr/bin/env python3
"""Read-only check of the final Paper VII prose preservation contract.

Every complete part must equal its preserved predecessor plus the closed,
reviewed line edits. Mathematical spans and the ordered statement, proof,
label and citation inventories are checked separately against the actual
retrieved source. Prose inside proofs may change. No Lean process is invoked.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
CURRENT = ROOT / 'verification/final_prose_2026-10-18'
BEFORE = ROOT / 'provenance/current_retrieved_baseline/traditional/parts'
PREVIOUS = ROOT / 'provenance/pre_final_prose_2026-10-18/editable/traditional/parts'
AFTER = ROOT / 'editable/traditional/parts'
KINDS = ('theorem', 'proposition', 'lemma', 'corollary', 'definition',
         'example', 'remark', 'boundary', 'certificate', 'conjecture',
         'standardfact', 'classical', 'construction', 'statement')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def collect(source, kinds):
    pattern = r'\\begin\{(' + '|'.join(kinds) + r')\}(.*?)\\end\{\1\}'
    return [(m.group(1), m.group(2)) for m in re.finditer(pattern, source, re.S)]


def mathspans(source):
    return re.findall(
        r'\$\$.*?\$\$|\$[^$]*\$|\\\[.*?\\\]|\\\(.*?\\\)|'
        r'\\begin\{(?:equation\*?|align\*?|gather\*?|multline\*?)\}'
        r'.*?\\end\{(?:equation\*?|align\*?|gather\*?|multline\*?)\}',
        source, re.S)


def apply_reviewed_edits(baseline, record):
    """Replay exact, nonoverlapping reviewed edits on preserved line ranges."""
    lines = baseline.splitlines(keepends=True)
    result, cursor = [], 0
    for edit in record['line_edits']:
        begin, end = edit['baseline_start'], edit['baseline_end']
        if not cursor <= begin <= end <= len(lines):
            raise ValueError('Invalid or overlapping reviewed edit range')
        if ''.join(lines[begin:end]) != edit['before']:
            raise ValueError('Reviewed baseline excerpt no longer matches')
        result.extend(lines[cursor:begin])
        result.append(edit['after'])
        cursor = end
    result.extend(lines[cursor:])
    return ''.join(result)


def verify():
    contract = json.loads((CURRENT / 'REVIEWED_PART_EDIT_CONTRACT.json').read_text())
    failures, rows = [], []
    counts = collections.Counter()
    filenames = sorted(p.name for p in BEFORE.glob('*.tex'))
    if len(filenames) != 9 or filenames != sorted(p.name for p in AFTER.glob('*.tex')):
        failures.append('The nine-part inventory changed')
    if sorted(contract['files']) != filenames:
        failures.append('Closed edit contract does not cover exactly the nine parts')
    wrapper_path = ROOT / 'editable/traditional/Paper_VII_Traditional_Final.tex'
    actual = re.findall(r'\\input\{parts/([^}]+)\}', wrapper_path.read_text())
    if actual != filenames:
        failures.append('The ordered part inputs changed')
    total_proofs = total_spans = unchanged_proofs = line_edit_count = 0
    for name in filenames:
        original, previous, current = BEFORE / name, PREVIOUS / name, AFTER / name
        old = original.read_bytes().decode('utf-8')
        prior = previous.read_bytes().decode('utf-8')
        new = current.read_bytes().decode('utf-8')
        record = contract['files'][name]
        identity = (sha(original) == record['retrieved_sha256'] and
                    sha(previous) == record['baseline_sha256'] and
                    sha(current) == record['reviewed_sha256'])
        try:
            exact = apply_reviewed_edits(prior, record) == new
        except ValueError:
            exact = False
        old_records, new_records = collect(old, KINDS), collect(new, KINDS)
        old_proofs, new_proofs = collect(old, ('proof',)), collect(new, ('proof',))
        old_math, new_math = mathspans(old), mathspans(new)
        structure = re.findall(r'\\(?:begin|end)\{[^}]+\}', old) == re.findall(r'\\(?:begin|end)\{[^}]+\}', new)
        anchors = re.findall(r'\\label\{[^}]+\}', old) == re.findall(r'\\label\{[^}]+\}', new)
        references = re.findall(r'\\(?:[cC]?ref|eqref|cite\w*)\*?(?:\[[^]]*\])*\{[^}]+\}', old) == re.findall(r'\\(?:[cC]?ref|eqref|cite\w*)\*?(?:\[[^]]*\])*\{[^}]+\}', new)
        statements = [kind for kind, _ in old_records] == [kind for kind, _ in new_records]
        proof_count = len(old_proofs) == len(new_proofs)
        maths = old_math == new_math
        gates = {'pinned_source_identities': identity, 'complete_file_equals_closed_reviewed_edits': exact,
                 'environment_sequence_identical': structure, 'labels_identical': anchors,
                 'references_identical': references, 'statement_inventory_identical': statements,
                 'proof_count_identical': proof_count, 'mathematical_spans_identical': maths}
        for gate, passed in gates.items():
            if not passed:
                failures.append(name + ': ' + gate)
        counts.update(kind for kind, _ in old_records)
        total_proofs += len(old_proofs)
        total_spans += len(old_math)
        same_proofs = sum(a == b for a, b in zip(old_proofs, new_proofs))
        unchanged_proofs += same_proofs
        line_edit_count += len(record['line_edits'])
        rows.append({'name': name, 'retrieved_sha256': sha(original), 'previous_sha256': sha(previous),
                     'current_sha256': sha(current), 'checks': gates,
                     'proof_bodies': len(old_proofs), 'proof_bodies_byte_identical': same_proofs,
                     'proof_bodies_with_reviewed_prose_edits': len(old_proofs) - same_proofs,
                     'extracted_mathematical_spans': len(old_math),
                     'reviewed_line_hunks': len(record['line_edits']),
                     'complete_file_byte_identical_to_retrieved': original.read_bytes() == current.read_bytes()})
    total_records = sum(counts.values())
    theorem_like = sum(counts[k] for k in ('theorem', 'proposition', 'lemma', 'corollary'))
    if (total_records, total_records - counts['statement'], counts['statement'], theorem_like, total_proofs, total_spans) != (147,142,5,96,107,1795):
        failures.append('The stated mathematical inventory changed')
    return {'schema':'komorebi.paper_vii.final_prose_preservation.v1',
            'status':'FAIL' if failures else 'PASS_FOR_STATED_SCOPE',
            'scope':'Exact full-file equality to the preserved prior edition plus closed reviewed prose and layout edits. Mathematical spans, environments, labels, citations, statement kinds and proof counts are independently compared with the retrieved source. This is not a proof-validity audit or Lean compilation.',
            'record_environments':total_records, 'numbered_records':total_records-counts['statement'],
            'unnumbered_statements':counts['statement'], 'theorem_like_records':theorem_like,
            'record_kinds':dict(counts), 'proof_bodies':total_proofs,
            'proof_bodies_byte_identical':unchanged_proofs,
            'proof_bodies_with_reviewed_prose_edits':total_proofs-unchanged_proofs,
            'extracted_mathematical_spans':total_spans,
            'complete_files_byte_identical':sum(row['complete_file_byte_identical_to_retrieved'] for row in rows),
            'reviewed_line_hunks':line_edit_count, 'baseline_parts':rows,
            'current_wrapper_path':str(wrapper_path.relative_to(ROOT)),
            'current_wrapper_sha256':sha(wrapper_path),
            'interpretation':'Counts from overlapping source branches do not count independent discoveries. All 107 complete proofs remain, with reviewed changes to explanatory prose in some proof bodies.',
            'failures':failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = verify()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k:v for k,v in report.items() if k != 'baseline_parts'}, indent=2))
    return bool(report['failures'])


if __name__ == '__main__':
    sys.exit(main())
