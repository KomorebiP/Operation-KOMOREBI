#!/usr/bin/env python3
"""Compare protected manuscript bodies against the exact retrieved baseline."""
from pathlib import Path
import argparse
import collections
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
BASELINE = ROOT / 'provenance/current_retrieved_baseline/traditional.tex'
CURRENT = ROOT / 'editable/traditional/Paper_VI_Traditional_Final.tex'
KINDS = ('theorem', 'proposition', 'lemma', 'corollary', 'definition',
         'example', 'remark', 'boundary', 'certificate', 'conjecture',
         'standardfact', 'classical')

def collect(text, kinds):
    pattern = r'\\begin\{(' + '|'.join(kinds) + r')\}(.*?)\\end\{\1\}'
    return [(m.group(1), m.group(2)) for m in re.finditer(pattern, text, re.S)]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, help='Optional report outside the sealed package.')
    args = parser.parse_args()
    if args.report and args.report.resolve().is_relative_to(ROOT):
        parser.error('report must be outside the sealed package')
    before = BASELINE.read_bytes().decode("utf-8")
    after = CURRENT.read_bytes().decode("utf-8")
    old_records, new_records = collect(before, KINDS), collect(after, KINDS)
    old_proofs, new_proofs = collect(before, ('proof',)), collect(after, ('proof',))
    failures = []
    for name, old, new in [('numbered record', old_records, new_records),
                           ('proof', old_proofs, new_proofs)]:
        if len(old) != len(new):
            failures.append({'scope': name, 'baseline_count': len(old),
                             'current_count': len(new)})
        for ordinal, (a, b) in enumerate(zip(old, new), start=1):
            if a != b:
                failures.append({'scope': name, 'ordinal': ordinal,
                                 'kind': a[0], 'problem': 'protected body differs'})
    if len(old_records) != 184 or len(old_proofs) != 140:
        failures.append({'problem': 'baseline inventory differs from the recorded contract'})
    report = {
        'status': 'FAIL' if failures else 'PASS',
        'scope': 'Exact ordered byte-text identity of protected LaTeX bodies. No mathematical validity audit.',
        'baseline_path': str(BASELINE.relative_to(ROOT)),
        'baseline_sha256': sha(BASELINE),
        'current_path': str(CURRENT.relative_to(ROOT)),
        'current_sha256': sha(CURRENT),
        'numbered_records': len(old_records),
        'proof_bodies': len(old_proofs),
        'record_kinds': dict(collections.Counter(k for k, body in old_records)),
        'theorem_like_records': sum(k in ('theorem', 'proposition', 'lemma', 'corollary')
                                    for k, body in old_records),
        'failures': failures,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return bool(failures)

if __name__ == '__main__':
    sys.exit(main())
