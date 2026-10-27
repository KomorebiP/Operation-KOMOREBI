#!/usr/bin/env python3
"""Replay actual all-row dyadic proofs, their axioms, and statement controls."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('--kit', required=True, type=Path)
p.add_argument('--baseline', required=True, type=Path)
p.add_argument('--baseline-build', required=True, type=Path)
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
src = Path(__file__).resolve().parent
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=False)
build = out / 'build'
build.mkdir()
logs = out / 'logs'
logs.mkdir()
for f in a.baseline_build.resolve().iterdir():
    if f.is_file():
        (build / f.name).symlink_to(f)
runner = a.baseline.resolve() / 'scripts/check_low_memory.py'
cases = [(x, True) for x in [
    'ChargedDworkClosure', 'DyadicFourAllRows', 'AllRowsAxioms', 'AllRowsControls'
]] + [('NegativeOldRowBound', False), ('NegativeAddressRange', False)]
results = []
for name, expected in cases:
    cmd = [sys.executable, str(runner), '--kit', str(a.kit.resolve()),
           '--threads', '1', '--timeout', '240', '--import-dir', str(build),
           '--output', str(build / (name + '.olean')), str(src / (name + '.lean'))]
    start = time.monotonic()
    run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, timeout=270)
    (logs / (name + '.log')).write_text(run.stdout)
    ok = (run.returncode == 0) if expected else (
        run.returncode != 0 and ('type mismatch' in run.stdout.lower()
        if name == 'NegativeOldRowBound' else 'decide' in run.stdout and 'false' in run.stdout))
    results.append(dict(module=name, expected_success=expected, exit_code=run.returncode,
                        passed=ok, seconds=round(time.monotonic()-start, 3)))
    print(json.dumps(results[-1]), flush=True)
    if expected and not ok:
        break
sources = {}
names = []
for f in ['ChargedDworkClosure.lean', 'DyadicFourAllRows.lean']:
    data = (src/f).read_text()
    decls = re.findall(r'^(?:@\[simp\] )?(theorem|def|abbrev) (\w+)', data, re.M)
    sources[f] = dict(sha256=hashlib.sha256((src/f).read_bytes()).hexdigest(),
                     counts={kind: sum(k == kind for k, _ in decls)
                             for kind in ['theorem', 'def', 'abbrev']})
    names += ['KomorebiPaperIX.'+f.removesuffix('.lean')+'.'+name for _, name in decls]
audit_text = (logs/'AllRowsAxioms.log').read_text() if (logs/'AllRowsAxioms.log').exists() else ''
reports = re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]", audit_text)
permitted = {'propext', 'Classical.choice', 'Quot.sound'}
audit_ok = (set(n for n, _ in reports) == set(names) and len(reports) == len(names)
            and all(set(x.strip() for x in axioms.split(',')) <= permitted
                    for _, axioms in reports))
result = dict(status='PASS' if len(results)==len(cases) and all(r['passed'] for r in results)
              and audit_ok else 'FAIL',
              sources=sources, declared_count=len(names), axiom_report_count=len(reports),
              axiom_coverage_pass=audit_ok, allowed_axioms=sorted(permitted), runs=results,
              scope='All j<4 and all natural u,k,n; actual normalized and original unnormalized N=4 coefficients.')
(out/'all_rows_audit.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
sys.exit(0 if result['status']=='PASS' else 1)
