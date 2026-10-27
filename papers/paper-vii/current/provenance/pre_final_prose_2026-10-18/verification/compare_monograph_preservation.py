#!/usr/bin/env python3
"""Check the stated preservation contract for the 18 October proofreading.

The six approved prose clarifications intentionally change two part files.
Every complete proof body and every extracted mathematical span must remain
identical to the retrieved baseline. This is a source-preservation check, not
a proof-validity audit or a Lean compiler run. The original exact-file
comparator is retained under provenance/pre_proofread_2026-10-18/verification/.
The default operation is read-only; --report writes only the requested file.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BEFORE = ROOT / 'provenance/current_retrieved_baseline/traditional/parts'
AFTER = ROOT / 'editable/traditional/parts'
KINDS = ('theorem', 'proposition', 'lemma', 'corollary', 'definition',
         'example', 'remark', 'boundary', 'certificate', 'conjecture',
         'standardfact', 'classical', 'construction', 'statement')

# This closed list is the reviewed whole-file change contract. Merely preserving
# mathematical delimiters would not detect an unauthorized prose hypothesis edit.
APPROVED_REPLACEMENTS = {
    '02_strengthened.tex': [
        ('Then\n\\[\n\\norm{P_bU\\psi}^2',
         'Choose any total order on this finite path set. Then\n\\[\n\\norm{P_bU\\psi}^2'),
        ('for a constant depending on the packet path but not on the partition.',
         'for a constant depending on the packet path but not on the partition. The absolute-value notation for the partition denotes its mesh, the largest subinterval length.'),
        (r'Thus \(\varepsilon_{\rm KL}\) controls both state dependence of error overlaps and nonorthogonality of nominal syndrome images.',
         r'Thus \(\varepsilon_{\rm KL}\) controls the deviation of error overlaps from their scalar code form.'),
        ('then the spectral dimensions converge at that time.',
         'then the spectral dimensions defined by the heat-moment ratio converge at that time.'),
        ('The expansion must respect the limiting gauge identities and must include an estimate for the omitted terms on the declared infrared regime.',
         'Here the volume coefficient includes the sign and normalization written explicitly in the cosmological term in Part I. The expansion must respect the limiting gauge identities and must include an estimate for the omitted terms on the declared infrared regime.'),
        ('\\label{strong:fig:kato_transport}\n\\end{figure}\n\n\\subsection{Local frames and curvature}',
         '\\label{strong:fig:kato_transport}\n\\end{figure}\n\\FloatBarrier\n\n\\subsection{Local frames and curvature}'),
        (r'\includegraphics[width=.62\textwidth]{06_kato_transport.pdf}',
         r'\includegraphics[width=.58\textwidth]{06_kato_transport.pdf}')
    ],
    '03_supplement_03.tex': [
        (r'For seeds $C_1,\ldots,C_k$, generation means the concrete statement',
         r'Continue under the positive-row hypothesis above. For seeds $C_1,\ldots,C_k$, generation means the concrete statement')
    ]
}


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


def verify():
    failures, rows = [], []
    counts = collections.Counter()
    proofs = spans = 0
    filenames = sorted(p.name for p in BEFORE.glob('*.tex'))
    if len(filenames) != 9:
        failures.append('Expected nine retrieved mathematical parts')
    if filenames != sorted(p.name for p in AFTER.glob('*.tex')):
        failures.append('Part inventory changed')
    wrapper_path = ROOT / 'editable/traditional/Paper_VII_Traditional_Final.tex'
    actual = re.findall(r'\\input\{parts/([^}]+)\}', wrapper_path.read_text())
    if actual != filenames:
        failures.append('Source part input order changed')
    for name in filenames:
        before, after = BEFORE / name, AFTER / name
        if not after.is_file():
            failures.append(name + ': missing current part')
            continue
        old, new = before.read_text(), after.read_text()
        expected = old
        for original, replacement in APPROVED_REPLACEMENTS.get(name, []):
            if expected.count(original) != 1:
                failures.append(name + ': approved replacement baseline is not unique')
            else:
                expected = expected.replace(original, replacement, 1)
        approved_whole_file = expected == new
        if not approved_whole_file:
            failures.append(name + ': complete file differs from the closed list of approved edits')
        records, current = collect(old, KINDS), collect(new, KINDS)
        old_proofs, new_proofs = collect(old, ('proof',)), collect(new, ('proof',))
        old_math, new_math = mathspans(old), mathspans(new)
        same_inventory = [k for k, _ in records] == [k for k, _ in current]
        if not same_inventory:
            failures.append(name + ': ordered statement-kind inventory changed')
        if old_proofs != new_proofs:
            failures.append(name + ': complete proof body changed')
        if old_math != new_math:
            failures.append(name + ': extracted mathematical span changed')
        counts.update(k for k, _ in records)
        proofs += len(old_proofs)
        spans += len(old_math)
        rows.append({
            'baseline_path': str(before.relative_to(ROOT)),
            'current_path': str(after.relative_to(ROOT)),
            'baseline_sha256': sha(before), 'current_sha256': sha(after),
            'complete_file_byte_identical': before.read_bytes() == after.read_bytes(),
            'complete_file_equals_baseline_plus_approved_edits': approved_whole_file,
            'approved_replacement_count': len(APPROVED_REPLACEMENTS.get(name, [])),
            'ordered_record_inventory_identical': same_inventory,
            'record_environments': len(records),
            'proof_bodies': len(old_proofs),
            'all_complete_proof_bodies_identical': old_proofs == new_proofs,
            'extracted_mathematical_spans': len(old_math),
            'all_extracted_mathematical_spans_identical': old_math == new_math,
            'statement_bodies_with_prose_changes': sum(a != b for a, b in zip(records, current))
        })
    protected = sum(counts.values())
    numbered = protected - counts['statement']
    theorem_like = sum(counts[k] for k in ('theorem', 'proposition', 'lemma', 'corollary'))
    if (protected, numbered, counts['statement'], theorem_like, proofs) != (147, 142, 5, 96, 107):
        failures.append('Statement/proof inventory differs from the stated contract')
    changed = [Path(r['current_path']).name for r in rows if not r['complete_file_byte_identical']]
    if changed != ['02_strengthened.tex', '03_supplement_03.tex']:
        failures.append('Changed part inventory differs from the approved proofreading scope')
    return {
        'schema': 'komorebi.paper_vii.proofread_preservation.v1',
        'status': 'FAIL' if failures else 'PASS_FOR_STATED_SCOPE',
        'scope': 'Nine retained parts; exact full-file equality to the retrieved baseline plus the closed list of six prose clarifications and two figure-layout edits; independently checked complete proof bodies, mathematical spans and statement-kind inventory. This check does not prove the mathematics.',
        'baseline_parts': rows,
        'current_wrapper_path': str(wrapper_path.relative_to(ROOT)),
        'current_wrapper_sha256': sha(wrapper_path),
        'record_environments': protected, 'numbered_records': numbered,
        'unnumbered_statements': counts['statement'],
        'theorem_like_records': theorem_like, 'proof_bodies': proofs,
        'record_kinds': dict(counts), 'extracted_mathematical_spans': spans,
        'complete_files_byte_identical': sum(r['complete_file_byte_identical'] for r in rows),
        'changed_parts': changed, 'failures': failures,
        'interpretation': 'Counts from overlapping manuscript branches do not count independent discoveries or expand formal coverage.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = verify()
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'baseline_parts'}, indent=2))
    return bool(report['failures'])


if __name__ == '__main__':
    sys.exit(main())
