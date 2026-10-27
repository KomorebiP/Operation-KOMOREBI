#!/usr/bin/env python3
"""Compare every actual proof object and interface from two clean production runs."""
from pathlib import Path
import argparse
import hashlib
import json

def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('build_a', type=Path)
    p.add_argument('build_b', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    ar = json.loads((a.build_a/'BUILD_REPORT.json').read_text())
    br = json.loads((a.build_b/'BUILD_REPORT.json').read_text())
    am = {r['module']: r for r in ar['results']}
    bm = {r['module']: r for r in br['results']}
    inputs_match = (set(am)==set(bm) and all(am[m]['source_sha256']==bm[m]['source_sha256'] for m in am))
    complete = all(r['status']=='PASS' and r['complete'] and r['passed_modules']==r['expected_modules']
                   and r['production_objects_seeded']==0 for r in [ar, br])
    rows = []
    ap = {p.relative_to(a.build_a) for p in (a.build_a/'objects').rglob('*') if p.is_file()}
    bp = {p.relative_to(a.build_b) for p in (a.build_b/'objects').rglob('*') if p.is_file()}
    for rel in sorted(ap|bp):
            left, right = a.build_a/rel, a.build_b/rel
            lh = sha(left) if left.is_file() else None
            rh = sha(right) if right.is_file() else None
            rows.append({'path': rel.as_posix(),
                         'A_sha256': lh, 'B_sha256': rh,
                         'A_bytes': left.stat().st_size if left.is_file() else None,
                         'B_bytes': right.stat().st_size if right.is_file() else None,
                         'identical': lh is not None and lh==rh})
    same = all(r['identical'] for r in rows)
    report = {'status': 'PASS' if complete and inputs_match and same else 'FAIL',
              'scope': 'Two fresh source compilations against the same pinned external compiled dependencies; no cold Mathlib rebuild.',
              'build_A': str(a.build_a.resolve()), 'build_B': str(a.build_b.resolve()),
              'both_clean_complete_runs': complete, 'same_modules_and_source_hashes': inputs_match,
              'module_count': len(am), 'object_and_interface_pairs': len(rows),
              'same_generated_file_set': ap==bp,
              'identical_pairs': sum(r['identical'] for r in rows), 'all_pairs_byte_identical': same,
              'A_report_sha256': sha(a.build_a/'BUILD_REPORT.json'),
              'B_report_sha256': sha(a.build_b/'BUILD_REPORT.json'), 'pairs': rows}
    a.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k!='pairs'}))
    return 0 if report['status']=='PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
